#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 11:10:39 2018

@author: robmaj12
"""
import pandas as pd
import plotly as py
import plotly.graph_objs as go
import matplotlib.pyplot as plt

import oo_simulation

system_state_record, transfer_record = oo_simulation.main()

#Make dataframe to conatin the system_state_record
df = pd.DataFrame(columns=['time', 'online', 'maintenance','offline', 'asset_demand', 'shortage'])
i = 0
while i < len(system_state_record['global']):
    df.loc[i] = system_state_record['global'][i]
    i = i+1
    
#j = 0
#while j < len(df['time']):
#    df['maintenance'].loc[j] = df['online'][j]+df['maintenance'][j]
#    df['offline'].loc[j] = df['online'][j]+df['offline'][j]
#    j = j + 1
    

##set up lines to plot    
#online = go.Scatter(x=df['time'],y=df['online'],fill='lines',name='Online')
#maint = go.Scatter(x=df['time'],y=df['maintenance'], fill ='lines',name='Maintenance')
#offline = go.Scatter(x=df['time'],y=df['offline'],fill='lines',name='Offline')
#demand = go.Scatter(x=df['time'],y=df['asset_demand'], fill ='tonexty',name='Demand')
#shortage =go.Scatter(x=df['time'],y=df['shortage'],fill = 'lines',name='Shortage')
##orgainze the data and create a a layout
#data= [shortage,offline,maint,online]
#layout = go.Layout(dict(title = 'Total Asset System Usage'),
#    showlegend=True,
#    xaxis=dict(
#        type='linear', title= 'Time in Days',
#    ),
#    yaxis=dict(
#        type='linear',title='Number of Assets',
#        dtick=10
#    )
#)
#    #create figure and plot
#fig = go.Figure(data=data,layout=layout)
#
#py.offline.plot(fig, filename ='systemUse.html')
online= list(df['online'])
maintenance= list(df['maintenance'])
offline= list(df['offline'])
demand = list(df['asset_demand'])
shortage = list(df['shortage'])
time= list(df['time'])
plt.style.use('fivethirtyeight')
plt.title('System Usage Plot')
plt.xlabel('Time in Days',fontsize=12)
plt.ylabel('Number of Assets',fontsize=12)
plt.stackplot(time,online, maintenance, offline,shortage, labels=['Online','Maintenance','Offline','Demand Shortage'])
plt.legend(loc='upper right')
