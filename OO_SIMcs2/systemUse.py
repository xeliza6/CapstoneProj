#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 11:10:39 2018

@author: robmaj12
"""
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


import oo_simulation

system_state_record, transfer_record = oo_simulation.main()

#Make dataframe to conatin the system_state_record
df = pd.DataFrame(columns=['time', 'online', 'maintenance','offline', 'asset_demand', 'shortage'])
i = 0
while i < len(system_state_record['global']):
    df.loc[i] = system_state_record['global'][i]
    i = i+1
    
online= list(df['online'])
maintenance= list(df['maintenance'])
offline= list(df['offline'])
demand = list(df['asset_demand'])
shortage = list(df['shortage'])
time= list(df['time'])
fig = plt.figure(1)
ax = fig.add_subplot(111)
plt.style.use('fivethirtyeight')
plt.title('System Usage Plot')
plt.xlabel('Time in Days',fontsize=12)
plt.ylabel('Number of Assets',fontsize=12)
ax.plot(time,demand,label='Demand',linewidth=1.5,color='#30a2da')
ax.stackplot(time,online, maintenance, offline,
              labels=['Online','Maintenance','Offline'], colors=['#6d904f','#e5ae38','#fc4f30'])
handles, labels = ax.get_legend_handles_labels()

fontP = FontProperties()
fontP.set_size('small')
plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left", borderaxespad=1.2, frameon=False,prop=fontP, ncol=4)
plt.show()
