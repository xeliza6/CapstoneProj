#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 20:50:32 2017

@author: robmaj12
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 16:57:45 2017
File to set up the Asset usage graph
@author: robmaj12
"""

import pandas as pd
from bokeh.charts import Area, output_file, show
from bokeh.models import Range1d
from bokeh.io import gridplot
import read_temp
output_file("Overall.html")
data_file_A = read_temp.read_unit_data("A")


dfA = pd.DataFrame()
dfA['online'] =      data_file_A[0]
dfA['maintenance'] = data_file_A[1]
dfA['offline'] =         data_file_A[2]
dfA['asset_demand'] = data_file_A[3]
dfA['time_period1'] = data_file_A[5]


#create stacked area graph
pA = Area(dfA,x='time_period1', y=['online', 'maintenance','offline'],
          stack=True, color=['green','red','blue'],
         xlabel='Time by Days', ylabel='Number of Assets',
         # We need to disable the automatic legend and add the correct one later
         legend="top_right", plot_height=300)
#sets graph width to size of html page
pA.sizing_mode = 'scale_width'
#control the yaxis range
pA.y_range = Range1d(0, max(dfA['online']))
#control xaxis range
pA.x_range.start = 0 
pA.x_range.end = max(dfA['time_period1'])

# set title options
pA.title.text = "Unit A Asset Usage"
pA.title.align = "center"
pA.title.text_color = "black"
pA.title.text_font_size = "25px"


#create B data
data_file_B = read_temp.read_unit_data("B")
dfB = pd.DataFrame()
dfB['online'] =      data_file_B[0]
dfB['maintenance'] = data_file_B[1]
dfB['offline'] =         data_file_B[2]
dfB['asset_demand'] = data_file_B[3]
dfB['time_period1'] = data_file_B[5]
#create stacked area graph
pB = Area(dfB,x='time_period1', y=['online', 'maintenance','offline'],
          stack=True, color=['green','red','blue'],
         xlabel='Time by Days', ylabel='Number of Assets',
         # We need to disable the automatic legend and add the correct one later
         legend="top_right", plot_height=300)
#sets graph width to size of html page
pB.sizing_mode = 'scale_width'
#control the yaxis range
pB.y_range = Range1d(0, max(dfB['online']))
#control xaxis range
pB.x_range.start = 0 
pB.x_range.end = max(dfB['time_period1'])

# set title options
pB.title.text = "Unit B Asset Usage"
pB.title.align = "center"
pB.title.text_color = "black"
pB.title.text_font_size = "25px"


#create C data
data_file_C = read_temp.read_unit_data("C")
dfC = pd.DataFrame()
dfC['online'] =      data_file_C[0]
dfC['maintenance'] = data_file_C[1]
dfC['offline'] =     data_file_C[2]
dfC['time_period1'] = data_file_C[5]
#create stacked area graph
pC = Area(dfC,x='time_period1', y=['online', 'maintenance','offline'],
          stack=True, color=['green','red','blue'],
         xlabel='Time by Days', ylabel='Number of Assets',
         # We need to disable the automatic legend and add the correct one later
         legend="top_right", plot_height=300)
#sets graph width to size of html page
pC.sizing_mode = 'scale_width'
#control the yaxis range
pC.y_range = Range1d(0, max(dfC['online']))
#control xaxis range
pC.x_range.start = 0 
pC.x_range.end = max(dfC['time_period1'])

# set title options
pC.title.text = "Unit C Asset Usage"
pC.title.align = "center"
pC.title.text_color = "black"
pC.title.text_font_size = "25px"


#create D data
data_file_D = read_temp.read_unit_data("D")
dfD = pd.DataFrame()
dfD['online'] =      data_file_D[0]
dfD['maintenance'] = data_file_D[1]
dfD['offline'] =     data_file_D[2]
dfD['time_period1'] = data_file_D[5]
#create stacked area graph
pD = Area(dfD,x='time_period1', y=['online', 'maintenance','offline'],
          stack=True, color=['green','red','blue'],
         xlabel='Time by Days', ylabel='Number of Assets',
         # We need to disable the automatic legend and add the correct one later
         legend="top_right", plot_height=300)
#sets graph width to size of html page
pD.sizing_mode = 'scale_width'
#control the yaxis range
#pD.y_range = Range1d(0, max(dfD['online']))
pD.y_range.start = 0
#control xaxis range
pD.x_range.start = 0 
pD.x_range.end = max(dfD['time_period1'])

# set title options
pD.title.text = "Unit D Asset Usage"
pD.title.align = "center"
pD.title.text_color = "black"
pD.title.text_font_size = "25px"

##create E data
#data_file_D = read_temp.read_unit_data("E")
#dfE = pd.DataFrame()
#dfE['online'] =      data_file_D[0]
#dfE['maintenance'] = data_file_D[1]
#dfE['offline'] =     data_file_D[2]
#dfE['time_period1'] = data_file_D[5]
##create stacked area graph
#pD = Area(dfE,x='time_period1', y=['online', 'maintenance','offline'],
#          stack=True, color=['green','red','blue'],
#         xlabel='Time by Days', ylabel='Number of Assets',
#         # We need to disable the automatic legend and add the correct one later
#         legend="top_right", plot_height=300)
##sets graph width to size of html page
#pD.sizing_mode = 'scale_width'
##control the yaxis range
#pD.y_range.start = 0
##control xaxis range
#pD.x_range.start = 0 
#pD.x_range.end = max(dfE['time_period1'])
#
## set title options
#pD.title.text = "Unit D Asset Usage"
#pD.title.align = "center"
#pD.title.text_color = "black"
#pD.title.text_font_size = "25px"



h = gridplot([[pA],[pB],[pC],[pD]])

#output_notebook()
show(h)