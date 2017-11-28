#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 16:57:45 2017
PANDAS
@author: robmaj12
"""

#import simulation
#from importlib import reload
import pandas as pd
from bokeh.charts import Area, show, output_notebook
import bokeh.models.glyphs
import bokeh.models.sources
from bokeh.plotting import figure, output_file, show
from bokeh.models.ranges import Range1d
import numpy
#reload(simulation)
#simulation.main()
output_file("line_bar.html")

df = pd.DataFrame()
df['time_period']=  [1,   2,  3,  4,  5,  6,  7,  8,  9, 10]
df['online']=       [80, 83, 80, 90, 75, 74, 77, 70, 75, 70]
df['maintenance']=  [10,  5,  3, 10, 15, 12, 12,  5, 10, 20]
df['offline']=      [10, 12, 17,  0, 10, 14, 11, 25, 15, 10]
df['asset_demand']= [100, 100, 100, 100, 100,  100, 100, 100, 100, 100]
df['asset_in_use']= [80, 83, 80, 90, 75, 74, 77, 70, 75, 70]

p = Area(df, x='time_period', y=['online', 'maintenance','offline'], title="Area Chart",
         xscale='time_period', stack=True,
         xlabel='Time (10 day period)', ylabel='Number of Assets',
         # We need to disable the automatic legend and add the correct one later
         legend=False)

# Create a data source
ds = bokeh.models.sources.ColumnDataSource(dict(x=df['time_period'], y=df['asset_demand']))

# Define the line glyph
line = bokeh.models.glyphs.Line(x='x', y='y', line_width=4, line_color='red')
#line = bokeh.models.glyphs.Line(x=df['time_period'], y=df['asset_demand'], line_width=4, line_color='blue')
ds1 = bokeh.models.sources.ColumnDataSource(dict(x=df['time_period'], y=df['asset_in_use']))
line1 = bokeh.models.glyphs.Line(x='x', y='y', line_width=4, line_color='blue')
# Add the data source and glyph to the plot
p.add_glyph(ds,line)
p.add_glyph(ds1, line1)

# Manually update the legend
legends = p._builders[0]._legends
legends.append( ('x',[p.renderers[-1]] ) )
# Activate the legend
# Add it to the chart
#p.add_legend(legends)
#output_notebook()
show(p)