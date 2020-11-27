import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import urllib
from fred_api import fred_api
import time
import requests
import json 
from scipy import stats

api = fred_api
endpoint = r'https://api.stlouisfed.org/fred/releases?&api_key={}&file_type=json'.format(api)
    
content = requests.get(url = endpoint)

data = content.json()


liabilities_endpoint = r'https://api.stlouisfed.org/fred/series/observations?series_id=NCBCEL&api_key={}&file_type=json'.format(api)
    
content = requests.get(url = liabilities_endpoint)

data = content.json()
#data = dict(data)
date = []
value = []
for i in data['observations']:
    date.append(i['date'])
    value.append(i['value'])
    
d = {'date':date, 'liabilities_value':value}
liabilities = pd.DataFrame(d)

networth_endoint = r'https://api.stlouisfed.org/fred/series/observations?series_id=TNWMVBSNNCB&api_key={}&file_type=json'.format(api)
    
content = requests.get(url = networth_endoint)

data = content.json()

nw_date = []
nw_value = []
for i in data['observations']:
    nw_date.append(i['date'])
    nw_value.append(i['value'])
    
#make dict then dataframe

nw_d = {'date':nw_date, 'networth_value':nw_value}
networth = pd.DataFrame(nw_d)

ms_index = liabilities.merge(networth, left_on='date', right_on='date', how = 'inner')
condition_liabilities = [ms_index['liabilities_value'] == "."]
condition_networth = [ms_index['networth_value'] == '.']
replace = [0]
ms_index['liabilities_value'] = np.select(condition_liabilities, replace, default=ms_index['liabilities_value'])
ms_index['networth_value'] = np.select(condition_networth, replace, default = ms_index['networth_value'])

ms_index['liabilities_value'] = ms_index['liabilities_value'].astype(float)
ms_index['networth_value'] = ms_index['networth_value'].astype(float)
ms_index['ms_index_ratio'] = round(((ms_index['liabilities_value']*1000000)/(ms_index['networth_value']*1000000)), 2)

g_mean = stats.gmean(ms_index.iloc[24:,]['ms_index_ratio'], axis = 0)
ms_index['ratio_normal'] = (ms_index['ms_index_ratio'] / g_mean)

fig_dims = (20, 8)
fig, ax = plt.subplots(figsize=fig_dims)
plt.xticks(
    rotation=90, 
    horizontalalignment='right',
    fontweight='light',
    fontsize='small'  
)
g = sns.pointplot(x = 'date', y = 'ratio_normal', data = ms_index.iloc[24:,])
ax1 = g.axes

ax1.axhline(g_mean, ls='--', c ='r')

plt.show()

