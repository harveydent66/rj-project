from tracemalloc import start
from wsgiref import headers
import numpy as np
import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup
from datetime import date
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

matplotlib.style.use('ggplot')

# Init
start_url = 'http://www.bcd-bbn.com/controlers/authenticate.php'
post_params = {'username': 'marwanko', 'password': 'Marwanek1959'}

response = requests.post(start_url, data=post_params)
soup = BeautifulSoup(response.text, 'html.parser')

# Scraping
table = soup.find('table')

headers = []
for i in table.find_all('th')[0: -4]:
    title = i.text
    title = ''.join(title.split())
    headers.append(title)

mydata = pd.DataFrame(columns=headers)

for j in table.find_all('tr')[1:-1]:
    row_data = j.find_all('td')
    row = [i.text for i in row_data]
    row = [r.replace(',', '') for r in row]
    length = len(mydata)
    mydata.loc[length] = row

mydata = mydata.set_index('Date')
mydata = mydata.apply(pd.to_numeric)
mydata = mydata.round(2)
mydata = mydata[['DownloadMB', 'UploadMB', 'TotalMB']]

data_cap = (10**6) * 1.25
total_consumption = mydata.sum()['TotalMB']
remaining = (data_cap - total_consumption)
total_consumption_pct = (total_consumption / data_cap)
remaining_pct = 100 - (total_consumption_pct * 100)
downloads = mydata.sum()['DownloadMB']
uploads = mydata.sum()['UploadMB']
dl_pct = (downloads / data_cap) * 100
ul_pct = (uploads / data_cap) * 100

total_consumption_pct2 = str(round(total_consumption_pct * 100, 2)) + ' %'
remaining_pct2 = str(round(remaining_pct, 2)) + ' %'
dl_pct2 = str(round(dl_pct, 2)) + ' %'
ul_pct2 = str(round(ul_pct, 2)) + ' %'

mydata.loc['Total'] = mydata.sum() 

st.set_page_config(
     page_title="Internet Usage",
     page_icon="📡",
     layout="wide",
     initial_sidebar_state="expanded"
 )

empty, datefield, empty2, empty3, empty4 = st.columns(5)
with datefield:
    st.metric('Date: ', str(date.today().strftime("%d/%m/%Y")))

blank, col1, col2, col3, col4 = st.columns(5)
col1.metric('Total Downloads %', dl_pct2)
col1.metric('Downloads', (f'{round((downloads/1000), 2):,}' + ' GB'))
col2.metric('Total Uploads %', ul_pct2)
col2.metric('Uploads', f'{round((uploads/1000), 2):,}' + ' GB')
col3.metric('Total Usage %', total_consumption_pct2)
col3.metric('Total Usage', f'{round((total_consumption/1000), 2):,}' + ' GB')
col4.metric('Total Remaining %', remaining_pct2)
col4.metric('Remaining', f'{round((remaining/1000), 2):,}' + ' GB')


colA, colB, colC = st.columns([1, 7, 1])
with colB:
    showTable = st.checkbox('Show Table', value=True)
    if showTable:
        st.table(mydata)
        if total_consumption_pct <= 1:
            st.progress(total_consumption_pct)
        else:
            st.markdown(
            """
            <style>
                .stProgress > div > div > div > div {
                    background-color: red;
                }
            </style>""",
        unsafe_allow_html=True,
    )
            st.progress(total_consumption_pct - 1)


chart_data = mydata[:-1]

chartData = pd.DataFrame(columns=['Uploads', 'Downloads'])
chartData['Downloads'] = mydata.DownloadMB[:-1]
chartData['Uploads'] = mydata.UploadMB[:-1]
chartData.set_index(mydata.index[:-1], inplace=True)


colD, colE, colF = st.columns([1, 7, 1])
with colE:
    showGraph = st.checkbox('Show Graph', value=True)
    if showGraph:
        st.bar_chart(chartData, height=700)

# Plotting
# fig, ax = plt.subplots(figsize=(20,7))

# ax.bar(chart_data.index, chart_data.DownloadMB, label='Downloads')
# ax.bar(chart_data.index, chart_data.UploadMB, label='Uploads')
# ax.plot(chart_data.index, chart_data.TotalMB, label='Total', c='black')

# ax.legend()

# ax.set_ylabel('Usage in MBs')
# ax.set_xlabel('Date')

# st.pyplot(fig)