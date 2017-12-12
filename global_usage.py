#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 16:57:45 2017
File to set up the Asset usage graph
@author: robmaj12
"""

import pandas as pd
import numpy as np
import bokeh.models.sources
from bokeh.charts import Area, Scatter, output_file, show
from bokeh.models import Range1d,BasicTickFormatter,ColumnDataSource
from bokeh.models.tickers import FixedTicker
from bokeh.models.glyphs import Line
from bokeh.io import gridplot
import read_temp
output_file("Overall.html")
data_file = read_temp.read_global_data()
#data_file = read_global_data()
#set up data frame for asset usage plot
online_assets = []
maintenance_assets = []
eol_assets = []
total_asset_demand = []
#try to make real data frame
#data_file = open("data.txt")
df1 = pd.DataFrame()
df1['online'] =      data_file[0]
df1['maintenance'] = data_file[1]
df1['offline'] =         data_file[2]
df1['total_asset_demand'] = data_file[3]
df1['time_period1'] = data_file[4]


#data_file.close()
##make play data frame
#df = pd.DataFrame()
#df['time_period']=  [0,1,   2,  3,  4,  5,  6,  7,  8,  9, 10]
#df['online_assets']=       [100,80, 83, 80, 90, 75, 74, 77, 70, 75, 70]
#df['maintenance_assets']=  [0,10,  5,  3, 10, 15, 12, 12,  5, 10, 20]
#df['offline']=      [0,10, 12, 17,  0, 10, 14, 11, 25, 15, 10]
#df['asset_demand']= [100,100, 100, 100, 100, 100,  100, 100, 100, 100, 100]
#df['asset_in_use']= [100,80, 83, 80, 90, 75, 74, 77, 70, 75, 70]
#create stacked area graph
p = Area(df1,x='time_period1', y=['online', 'maintenance','offline'],
          stack=True, color=['green','red','blue'],
         xlabel='Time by Days', ylabel='Number of Assets',
         # We need to disable the automatic legend and add the correct one later
         legend="bottom_left", plot_height=300)
#sets graph width to size of html page
p.sizing_mode = 'scale_width'
#control the yaxis range
p.y_range = Range1d(0, 100)
#control xaxis range
p.x_range.start = 0 
p.x_range.end = max(df1['time_period1'])
#control the values at each tick mark
#p.xaxis.ticker = FixedTicker(ticks=[0, 50000, 100000,150000,200000,250000,300000,350000,400000,450000,500000,550000])
#p.xaxis[0].formatter = PrintfTickFormatter(format=f)
#p.xaxis.formatter = BasicTickFormatter(use_scientific=False)

# set title options
p.title.text = "Asset Usage"
p.title.align = "center"
p.title.text_color = "black"
p.title.text_font_size = "25px"


    
# Create a data source for the asset demand
#ds = bokeh.models.sources.ColumnDataSource(dict(x=df['time_period'], y=df['asset_demand']))

# Define the line glyph
#line = bokeh.models.glyphs.Line(x=df['time_period'], y=df['asset_demand'], line_width=4, line_color='red')
#demand_line = bokeh.models.glyphs.Line(x='x', y='y', line_width=4, line_color='red')
# Create a data source for the asset in use
#ds1 = bokeh.models.sources.ColumnDataSource(dict(x=df['time_period1'], y=df['total_asset_demand']))
# Define the line glyph
#line = bokeh.models.glyphs.Line(x=df['time_period'], y=df['asset_in_use'], line_width=4, line_color='blue')
#in_use_line = bokeh.models.glyphs.Line(x='x', y='y', line_width=4, line_color='blue')
# Add the data source and line glyphs to the plot
#p.add_glyph(ds,demand_line)
#p.add_glyph(ds1, in_use_line)
#h = gridplot([[p],[scaPlot]])

#output_notebook()
show(p)