#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 11:10:39 2018

@author: robmaj12
"""
import pandas as pd
import matplotlib.pyplot as plt

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
plt.style.use('fivethirtyeight')
plt.title('System Usage Plot')
plt.xlabel('Time in Days',fontsize=12)
plt.ylabel('Number of Assets',fontsize=12)
plt.stackplot(time,online, maintenance, offline, labels=['Online','Maintenance','Offline'])
plt.legend(loc='lower left')
