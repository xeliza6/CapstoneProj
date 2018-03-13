#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 11:10:39 2018

@author: robmaj12
"""
import pandas as pd
import plotly as py
import plotly.graph_objs as go
import read_temp

sim_state_history = {}
def read_file(system_state_record):
    for unit_id, state_data in system_state_record.items(): 
        df = pd.DataFrame( columns=['asset_ID','Unit_From','Unit_To','clock','score'])
        i = 0
        for state in state_data:
            df.loc[i] = state
            i += 1
        
        sim_state_history[unit_id] = df  

data_file = read_temp.read_global_data()
df1 = pd.DataFrame()
df1['online'] =      data_file[0] 
#df1['maintenance'] = data_file[1]
#df1['offline'] =     data_file[2]
df1['asset_demand'] = data_file[3]
df1['time_period'] = data_file[4]

#for i in range(len(df1['time_period'])):
#    df1['maintenance'] = data_file[0][i]+data_file[1][i]
#    df1['offline'] = data_file[0][i]+data_file[1][i]+data_file[2][i]


online = go.Scatter(x=df1['time_period'],y=df1['online'],fill='tonexty',name='Online')
maint = go.Scatter(x=df1['time_period'],y=df1['maintenance'], fill ='tonexty',name='Maintenance')
offline = go.Scatter(x=df1['time_period'],y=df1['offline'],fill='tonexty',name='Offline')
demand = go.Scatter(x=df1['time_period'],y=df1['asset_demand'], fill ='tonexty',name='Demand')
data= [demand,offline,maint,online]
layout = go.Layout(dict(title = 'Total Asset System Usage'),
    showlegend=True,
    xaxis=dict(
        type='linear', title= 'Time in Days',
    ),
    yaxis=dict(
        type='linear',title='Number of Assets',
        dtick=10
    )
)
fig = go.Figure(data=data,layout=layout)

py.offline.plot(fig, filename ='systemUse')
