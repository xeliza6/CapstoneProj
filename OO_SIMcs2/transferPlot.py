#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 20:14:44 2018

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
import numpy as np
import oo_simulation
from matplotlib.font_manager import FontProperties
system_state_record, transfer_record = oo_simulation.main()
units=['A','B','C','D','E','F','G','H','I','J']
maxT = len(transfer_record)-1
maxTime = transfer_record[maxT][3]
months = maxTime/30
counts = [0] * int(months)
#For loop for sum up the counts by month
b = 30
spot = 0
count = 0
for i in range(1,len(transfer_record)):
   time = transfer_record[i][3]
   if (time <= b):
       count = count + 1
   else:
       counts[spot] = count
       b = b + 30
       spot  = spot + 1
       count  = 1
   #Set up dataframe    
df = pd.DataFrame(columns=['time', 'transfers'])
time = np.arange(len(counts))
df['time']= time
df['transfers']= counts
time = list(df['time'])
transfers = list(df['transfers'])
#fig,ax = plt.subplots()
#plt.plot(time,transfers,label='Transfers',linewidth=1.5,color='#e5ae38')

fig = plt.figure(1)
ax = fig.add_subplot(111)
plt.style.use('fivethirtyeight')
plt.title('System Transfers by Month')
plt.xlabel('Time in Months',fontsize=12)
plt.ylabel('Number of Assets Transfered',fontsize=12)
ax.bar(time,transfers,label='Transfers',align='center',color='#e5ae38',alpha=0.5)
plt.xticks(np.arange(min(time), max(time)+5, 1.0))
plt.yticks(np.arange(min(transfers), max(transfers)+10, 10.0))
#mplcursors.cursor(hover=True)
fontP = FontProperties()
fontP.set_size('small')
plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
           borderaxespad=1.2, frameon=False,prop=fontP, ncol=1)

plt.show()