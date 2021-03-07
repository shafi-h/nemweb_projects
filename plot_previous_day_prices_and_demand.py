## This script produces a quick visualisation of the previous day's spot electricity prices and demand in the NEM
## The data is sourced from the latest Public_Prices file published by AEMO on http://nemweb.com.au/Reports/Current/Public_Prices/


import csv
import pandas as pd
import requests
from bs4 import BeautifulSoup
import zipfile
import io
import matplotlib.pyplot as plt


## Define links

site = 'http://nemweb.com.au'
link = 'http://nemweb.com.au/Reports/Current/Public_Prices/'


## Get links from the Nemweb Public_Prices page

page = requests.get(link)
data = page.text
soup = BeautifulSoup(data, 'html.parser')
links = soup.find_all('a')


## Get latest link

latest_link = site + links[-1].get('href')
print('Link to previous day\'s prices: ',latest_link)


## Process latest file

response = requests.get(latest_link)
zf = zipfile.ZipFile(io.BytesIO(response.content))
file_name = zf.namelist()[0] # This is the file that we want the data from
foofile = zf.open(file_name)

data = []
for line in foofile.readlines():
    row = line.decode('utf-8')
    data.append(row)

csv_reader = csv.reader(data)


## Parse the data and put into a list to be loaded into a dataframe

prices = []

for row in csv_reader:
    if row[0:2] == ['D','TREGION']:
        version = int(row[3])
        settlementdate = row[4]
        regionid = row[6]
        rrp = float(row[7])
        total_demand = float(row[10])
        row_data = [version, settlementdate, regionid, rrp, total_demand]
        prices.append(row_data)
        

## Create dataframes

df = pd.DataFrame(prices, columns = ['Version','SettlementDate','RegionID','RRP','TotalDemand'])
df['SettlementDate'] = pd.to_datetime(df['SettlementDate'])
df['Ranking'] = df.groupby(['SettlementDate','RegionID'], as_index=False)['Version'].rank(method='dense', ascending=False)  ## Rank the data to get the latest version
df = df.loc[df['Ranking']==1,:]
df = df.sort_values(by='SettlementDate', ascending=True)
df_vic = df.loc[df['RegionID']=='VIC1', :]
df_nsw = df.loc[df['RegionID']=='NSW1', :]
df_sa = df.loc[df['RegionID']=='SA1', :]
df_qld = df.loc[df['RegionID']=='QLD1', :]


## Plot spot prices in each state

plt.plot(df_vic['SettlementDate'], df_vic['RRP'], label = 'VIC')
plt.plot(df_nsw['SettlementDate'], df_nsw['RRP'], label = 'NSW')
plt.plot(df_sa['SettlementDate'], df_sa['RRP'], label = 'SA')
plt.plot(df_qld['SettlementDate'], df_qld['RRP'], label = 'QLD')

plt.xlabel('Datetime')
plt.ylabel('Price ($)')
plt.title('NEM spot prices')
plt.legend()
plt.show()


## Plot demand in each state

plt.plot(df_vic['SettlementDate'], df_vic['TotalDemand'], label = 'VIC')
plt.plot(df_nsw['SettlementDate'], df_nsw['TotalDemand'], label = 'NSW')
plt.plot(df_sa['SettlementDate'], df_sa['TotalDemand'], label = 'SA')
plt.plot(df_qld['SettlementDate'], df_qld['TotalDemand'], label = 'QLD')

plt.xlabel('Datetime')
plt.ylabel('Demand (MWh)')
plt.title('NEM Demand')
plt.legend()
plt.show()
