# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 06:19:49 2020

@author: perrin27
"""

import pandas as pd

#from datetime import date

from os.path import dirname, join

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, DatetimeTickFormatter
from bokeh.plotting import figure, show
from bokeh.models.glyphs import VBar

x = [1, 2, 3, 4]
y = [1, 2, 3, 4]
source = ColumnDataSource(data={'x': x, 'y': y})

data = pd.read_excel(join(dirname(__file__), 'data/feuille de saisie METEO mois par mois.xls'), None, header = (0,1)) # header dans les deux premières lignes de chaque onglet

plot = figure(plot_width = 800, plot_height=300, x_axis_type='datetime')
    
glyph = VBar(x='x', bottom=0, top='y', width=1 ,line_alpha=0.1, fill_color="#6599ed")
    
plot.add_glyph(source, glyph)

plot.yaxis.axis_label = "mm d'eau"
plot.axis.axis_label_text_font_style = "bold"
plot.background_fill_color = "beige"
plot.background_fill_alpha = 0.5
plot.xaxis.formatter = DatetimeTickFormatter(months = ['%b %Y'])
plot.xaxis.visible = False
plot.grid.grid_line_alpha = 0.5

    



curdoc().add_root(plot)
curdoc().title = "Météo Bouchaux"
show(plot)