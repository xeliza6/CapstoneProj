#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 16:57:45 2017

@author: robmaj12
"""

import pandas as pd
import bokeh.models.sources
import bokeh.models.glyphs
from bokeh.charts import Area, output_file, show
from bokeh.models import Range1d
output_file("Overall.html")


online_assets = []
maintenance_assets = []
eol_assets = []
total_asset_demand = []
#try to make real data frame
data_file = open("data.txt")
df1 = pd.DataFrame()
df1['online_assets'] =      [int(i) for i in data_file.readline()[1:-2].split(',')]
df1['maintenance_assets'] = [int(i) for i in data_file.readline()[1:-2].split(',')]
df1['eol_assets'] =         [int(i) for i in data_file.readline()[1:-2].split(',')]
df1['total_asset_demand'] = [int(i) for i in data_file.readline()[1:-2].split(',')]
df1['time_period1'] = [i * 30 for i in list(range(len(df1['online_assets'])))]


data_file.close()
#make play data fram
df = pd.DataFrame()
df['time_period']=  [0,1,   2,  3,  4,  5,  6,  7,  8,  9, 10]
df['online_assets']=       [100,80, 83, 80, 90, 75, 74, 77, 70, 75, 70]
df['maintenance_assets']=  [0,10,  5,  3, 10, 15, 12, 12,  5, 10, 20]
df['offline']=      [0,10, 12, 17,  0, 10, 14, 11, 25, 15, 10]
df['asset_demand']= [100,100, 100, 100, 100, 100,  100, 100, 100, 100, 100]
df['asset_in_use']= [100,80, 83, 80, 90, 75, 74, 77, 70, 75, 70]
#create stacked area graph
p = Area(df,x='time_period', y=['online_assets', 'maintenance_assets','offline'],
          stack=True,
         xlabel='Time by days', ylabel='Number of Assets',
         # We need to disable the automatic legend and add the correct one later
         legend=False)
p.x_range = Range1d(0, 10)
p.y_range = Range1d(0, 100)
#p.x_range = Range1d(0, max(range(len(df1['online_assets']))))

# set title options
p.title.text = "Asset Usage over time"
p.title.align = "center"
p.title.text_color = "black"
p.title.text_font_size = "25px"

    
# Create a data source for the asset demand
ds = bokeh.models.sources.ColumnDataSource(dict(x=df['time_period'], y=df['asset_demand']))

# Define the line glyph
#line = bokeh.models.glyphs.Line(x=df['time_period'], y=df['asset_demand'], line_width=4, line_color='red')
demand_line = bokeh.models.glyphs.Line(x='x', y='y', line_width=4, line_color='red')
# Create a data source for the asset in use
ds1 = bokeh.models.sources.ColumnDataSource(dict(x=df['time_period'], y=df['asset_in_use']))
# Define the line glyph
#line = bokeh.models.glyphs.Line(x=df['time_period'], y=df['asset_in_use'], line_width=4, line_color='blue')
in_use_line = bokeh.models.glyphs.Line(x='x', y='y', line_width=4, line_color='blue')
# Add the data source and line glyphs to the plot
p.add_glyph(ds,demand_line)
p.add_glyph(ds1, in_use_line)


#output_notebook()
show(p)
