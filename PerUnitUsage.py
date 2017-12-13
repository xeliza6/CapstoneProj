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
from bokeh.models import Range1d,ColumnDataSource
from bokeh.io import gridplot
from bokeh.models.glyphs import Line
import read_temp
output_file("Overall.html")

units=["A",'B','C','D','E','F','G','H','I','J']
df_plots_array = []

for unit in units:
    unit_data_file = read_temp.read_unit_data(unit)

    ##Create  data frame
    dfA = pd.DataFrame()
    dfA['online'] =      unit_data_file[0]
    dfA['maintenance'] = unit_data_file[1]
    dfA['offline'] =         unit_data_file[2]
    dfA['asset_demand'] = unit_data_file[3]
    dfA['time_period1'] = unit_data_file[5]
    
    
    #create stacked area graph
    pA = Area(dfA,x='time_period1', y=['online', 'maintenance','offline'],
              stack=True, color=['green','red','blue'],
             xlabel='Time by Days', ylabel='Number of Assets',
             # We need to disable the automatic legend and add the correct one later
             legend=False, plot_height=300,plot_width = 1100)
    #sets graph width to size of html page
    pA.sizing_mode = 'scale_width'
    #control the yaxis range
    pA.y_range = Range1d(0, max(dfA['online']))
    #control xaxis range
    pA.x_range.start = 0 
    pA.x_range.end = max(dfA['time_period1'])
    
    # set title options
    pA.title.text = "Unit "+unit+" Asset Usage"
    pA.title.align = "center"
    pA.title.text_color = "black"
    pA.title.text_font_size = "25px"
    # Create a data source for the asset demand
    dsA = bokeh.models.sources.ColumnDataSource(dict(x=dfA['time_period1'], y=dfA['asset_demand']))
    
    # Define the line glyph
    lineA = bokeh.models.glyphs.Line(x='x', y='y', line_width=4, line_color='black')
    pA.add_glyph(dsA,lineA)
    df_plots_array.append([pA])


h = gridplot(df_plots_array)
h.legend.
#output_notebook()
show(h)