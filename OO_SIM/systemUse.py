#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 11:10:39 2018

@author: robmaj12
"""
import pandas as pd
import plotly as py
import plotly.graph_objs as go
import oo_simulation

system_state_record, transfer_record = oo_simulation.main()

#Make dataframe to conatin the system_state_record
df = pd.DataFrame(columns=['time', 'online', 'maintenance','offline', 'asset_demand', 'shortage'])
i = 0
while i < len(system_state_record['global']):
    df.loc[i] = system_state_record['global'][i]
    i = i+1
#set up lines to plot    
online = go.Scatter(x=df['time'],y=df['online'],fill='tonexty',name='Online')
maint = go.Scatter(x=df['time'],y=df['maintenance'], fill ='tonexty',name='Maintenance')
offline = go.Scatter(x=df['time'],y=df['offline'],fill='tonexty',name='Offline')
demand = go.Scatter(x=df['time'],y=df['asset_demand'], fill ='tonexty',name='Demand')
#orgainze the data and create a a layout
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
    #create figure and plot
fig = go.Figure(data=data,layout=layout)

py.offline.plot(fig, filename ='systemUse.html')
