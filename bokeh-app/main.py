# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 06:19:49 2020

@author: perrin27
"""

import pandas as pd
import datetime
#from datetime import date

from os.path import dirname, join

from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, DateRangeSlider
from bokeh.plotting import figure
from bokeh.models.tools import HoverTool
from bokeh.models.glyphs import VBar


data = pd.read_excel(join(dirname(__file__), 'data/feuille de saisie METEO mois par mois.xls'), None, header = (0,1)) # header dans les deux premières lignes de chaque onglet

liste_mois = list(data.keys())

data_all = pd.DataFrame(columns=['dates','nom_jour','hauteur_pluie','commentaire_pluie','temps_matin','temps_midi','temps_soir','temp_mini','temp_maxi'])
stat_mois = pd.DataFrame(columns=['mois', 'hauteur_pluie_max', 'cumul_pluie'])


for mois in liste_mois: 
    
    tab = data.get(mois)
    tab_2 = tab.iloc[:,0:9]
    tab_2.columns = ['dates','nom_jour','hauteur_pluie','commentaire_pluie','temps_matin','temps_midi','temps_soir','temp_mini','temp_maxi']
    tab_clean = tab_2[tab_2['dates'].notnull()]
    tab_clean.loc[:, 'h_pluie'] = pd.to_numeric(tab_clean.loc[:, 'hauteur_pluie'], errors='coerce')
    tab_clean.loc[:, 't_mini'] = pd.to_numeric(tab_clean.loc[:, 'temp_mini'], errors='coerce')
    tab_clean.loc[:, 't_maxi'] = pd.to_numeric(tab_clean.loc[:, 'temp_maxi'], errors='coerce')
    data_all = data_all.append(tab_clean)
    


startdate = datetime.date(2016, 1, 1)
enddate = datetime.date.today()
largeur_plot = 1200



def make_plot_pluie(source, title):
    plot = figure(plot_width = largeur_plot, plot_height=300, x_axis_type='datetime', x_range=(datetime.date(2019, 1, 1), datetime.date(2020, 1, 1)))
    plot.title.text = title
    glyph = VBar(x='x', bottom=0, top='y',
                 width=largeur_bar,
                 line_alpha=0.1,
                 fill_color="#6599ed")
    
    plot.add_glyph(source, glyph)

    plot.yaxis.axis_label = "mm d'eau"
    plot.axis.axis_label_text_font_style = "bold"
    plot.background_fill_color = "beige"
    plot.background_fill_alpha = 0.5
    plot.xaxis.formatter = DatetimeTickFormatter(months = ['%b %Y'])
    plot.xaxis.visible = False
    plot.grid.grid_line_alpha = 0.5

    hover = HoverTool()
    hover.tooltips=[
    ('Date', '@x{%d-%m-%Y}'),
    ('Hauteur pluie', '@y mm')
        ]
    hover.formatters={'x': 'datetime'}
    plot.add_tools(hover)

    return plot

def update_range(attr, old, new):
    plot.x_range.start = new[0]
    plot.x_range.end = new[1]
    
source = ColumnDataSource(data={'x': data_all['dates'], 'y': data_all['h_pluie']})

largeur_bar = 24*3600*1000*0.9
plot_titre_pluie = "Météo aux Bouchaux - jour par jour - hauteur d'eau en mm et température en °C"

plot = make_plot_pluie(source, plot_titre_pluie)

Date_slider = DateRangeSlider(title="période: ", start=startdate, end=enddate,
                                 value=(datetime.date(2019, 1, 1), datetime.date(2020, 1, 1)), step=1,
                                 width = largeur_plot - 77) 
Date_slider.on_change('value', update_range)

controls = Date_slider
curdoc().add_root(column(plot, controls))
curdoc().title = "Météo Bouchaux"