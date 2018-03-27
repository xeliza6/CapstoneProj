#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 16:39:12 2018

@author: robmaj12
"""

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
#run the simulation
system_state_record, transfer_record = oo_simulation.main()
units=['A','B','C','D','E','F','G','H','I','J']
#fig, axs = plt.subplots(10,1,sharex=True)
#fig.subplots_adjust(hspace=0)

index = 1
#Make dataframe to conatin the system_state_record
for unit in units:
    plt.figure(index)
    df = pd.DataFrame(columns=['time', 'online', 'maintenance','offline', 'asset_demand', 'shortage'])
    i = 0
    while i < len(system_state_record[unit]):
        df.loc[i] = system_state_record[unit][i]
        i = i+1
    

    online= list(df['online'])
    maintenance= list(df['maintenance'])
    offline= list(df['offline'])
    demand = list(df['asset_demand'])
    shortage = list(df['shortage'])
    time= list(df['time'])
    plt.style.use('fivethirtyeight')
    plt.title('Unit '+unit+' Usage Plot')
    plt.xlabel('Time in Days',fontsize=12)
    plt.ylabel('Number of Assets',fontsize=12)
    plt.plot(time,demand,label='Demand',linewidth=1,color='#8b8b8b')
    plt.stackplot(time,online, maintenance, offline, labels=['Online','Maintenance','Offline'],colors=['#6d904f','#e5ae38','#fc4f30'])
    index=index+1
    plt.legend(loc='lower left')
    fontP = FontProperties()
    fontP.set_size('small')
    plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left", borderaxespad=1.2,
               frameon=False,prop=fontP, ncol=4)
plt.show()
