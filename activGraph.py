#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 15:33:12 2017

@author: robmaj12
"""
import pandas as pd
import numpy as np
from bokeh.models import ColumnDataSource, DataRange1d
from bokeh.models.glyphs import Line
from bokeh.models import Legend
from bokeh.charts import Scatter, output_file, show
from bokeh.models import Range1d
df = pd.DataFrame()
df1 = pd.DataFrame()
df['time_period']=  [0,1,   2,  3,  4,  5,  6,  7,  8,  9, 10]
df['transfers']=  [0,0,   -1,  2,  2,  -3,  5,  -1,  -3,  2, 4]
#make scatter plot
p = Scatter(df, x='time_period', y='transfers',
            xlabel="Time in Months", ylabel="Number of Transfers")
#set up line at y = 0
N = 10
x = np.linspace(0, 10, N)
y = x*0
#make a data source
source = ColumnDataSource(dict(x=x, y=y))

glyph = Line(x="x", y="y", line_color="black", line_width=2, line_alpha=1)
p.add_glyph(source, glyph)
#set x and y ranges
p.x_range = Range1d(0, 10)
p.y_range = Range1d(-10, 10)


# set title options
p.title.text = "Activity Graph for One Unit"
p.title.align = "center"
p.title.text_color = "black"
p.title.text_font_size = "25px"


#p.add_layout(legend, 'right')
#p.add_glyph(line)
output_file("scatter.html")
#display the activty graph
show(p)