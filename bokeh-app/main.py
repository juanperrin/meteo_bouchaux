# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 06:19:49 2020

@author: perrin27
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import date
from tkinter import *
from os.path import dirname, join

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, DataRange1d, RadioButtonGroup, Select, DatetimeTickFormatter, LinearAxis, DateRangeSlider
from bokeh.palettes import Blues4
from bokeh.plotting import figure, show, output_file, output_notebook
from bokeh.models.tools import HoverTool
from bokeh.models.glyphs import VBar, Line

# output to static HTML file
#output_file("meteo.html")
output_notebook()


""" préparation des data """


#lire les données à partir du fichier Méteo initial et retourner un OrderedDict
#data = pd.read_excel((r'C:\Users\perrin27\Desktop\projet-METEO\bokeh\bouchaux\data\feuille de saisie METEO mois par mois.xls'), None, header = (0,1))
data = pd.read_excel(join(dirname(__file__), 'data/feuille de saisie METEO mois par mois.xls'), None, header = (0,1)) # header dans les deux premières lignes de chaque onglet

# on fait une liste de tous les onglets du fichier initial
liste_mois = list(data.keys())
#on crée les dataframes vides, avec le nom des colonnes
data_all = pd.DataFrame(columns=['dates','nom_jour','hauteur_pluie','commentaire_pluie','temps_matin','temps_midi','temps_soir','temp_mini','temp_maxi'])
stat_mois = pd.DataFrame(columns=['mois', 'hauteur_pluie_max', 'cumul_pluie'])

# on rempli ces dataframes avec les donnees brutes et des statistiques sur les donnée brutes
for mois in liste_mois: # on boucle pour tous les mois du classeur
    
    tab = data.get(mois) # selection de l'onglet à partir de son nom (= key du DataFrame)
    annee = tab.iloc[0,0].year #on lit la date de la première cellule en haut à gauche de l'onglet
    mois = tab.iloc[0,0].month
    jour = tab.iloc[0,0].day
    annee_mois_jour = date(annee, mois, jour)
    # on ne prend que les 9 premières colonnes de chaque, mais on garde pour le moment toutes les lignes
    tab_2 = tab.iloc[:,0:9]

    # renommer les colonnes
    tab_2.columns = ['dates','nom_jour','hauteur_pluie','commentaire_pluie','temps_matin','temps_midi','temps_soir','temp_mini','temp_maxi']
    # on ne garde que le tableau rectangulaire, qui correspond aux lignes de la colonne 'dates' qui ne sont pas des NaT
    tab_clean = tab_2[tab_2['dates'].notnull()]
    
    tab_clean.loc[:, 'hauteur_pluie'] = pd.to_numeric(tab_clean.loc[:, 'hauteur_pluie'], errors='coerce')
    tab_clean.loc[:, 'temp_mini'] = pd.to_numeric(tab_clean.loc[:, 'temp_mini'], errors='coerce')
    tab_clean.loc[:, 'temp_maxi'] = pd.to_numeric(tab_clean.loc[:, 'temp_maxi'], errors='coerce')
    
    # on calcule des statistiques sur les donnees
    hauteur_pluie_max = tab_clean['hauteur_pluie'].max() # maximum de pluie journalière
    pluie_cumul = tab_clean['hauteur_pluie'].sum() # calcul du cumul de pluie pour le mois
    # on remplit le dataframe stat_mois avec les donnees statistiques mensuelles
    stat_mois = stat_mois.append(pd.Series([annee_mois_jour, hauteur_pluie_max, pluie_cumul], index=['mois','hauteur_pluie_max','cumul_pluie']), ignore_index=True)

    
#    tab_clean.insert(3, "pluie_cumulee", pluie_cumul, True) # on insert la colonne de cumul de pluis dans le tableau à la position 3
    
    data_all = data_all.append(tab_clean)
    
# statistiques sur le tableau de stats mensuelles
mois_plus_pluvieux = stat_mois['mois'][stat_mois['cumul_pluie'].idxmax()]  # trouvele mois où le cumul de pluie est le plus grand
cumul_pluie_max = stat_mois['cumul_pluie'].max() # valeur du cumul de pluie le plus grand

""" Fin de préparation des data """

startdate = date(2016, 1, 1)
enddate = date.today()
largeur_plot = 1200

""" MODULE "GLOBAL"   """
""" 1-- plot HAUTEUR_PLUIE """
def make_plot_pluie(source, title):
    plot = figure(plot_width = largeur_plot, plot_height=300, x_axis_type='datetime', x_range=(date(2019, 1, 1), date(2020, 1, 1)))
    plot.title.text = title
    glyph = VBar(x='x', bottom=0, top='y',
                 width=largeur_bar,
                 line_alpha=0.1,
                 fill_color="#6599ed")
    
    plot.add_glyph(source, glyph)
    
#    plot.xaxis.axis_label = 'Date'
    plot.yaxis.axis_label = "mm d'eau"
    plot.axis.axis_label_text_font_style = "bold"
    plot.background_fill_color = "beige"
    plot.background_fill_alpha = 0.5
    plot.xaxis.formatter = DatetimeTickFormatter(months = ['%b %Y'])
    plot.xaxis.visible = False
    plot.grid.grid_line_alpha = 0.5
    #--------hovertool------------
    hover = HoverTool()
    hover.tooltips=[
    ('Date', '@x{%d-%m-%Y}'),
    ('Hauteur pluie', '@y mm')
        ]
    hover.formatters={'x': 'datetime'}
    plot.add_tools(hover)
    #------------------------------
    return plot

def update_range(attr, old, new):
    plot.x_range.start = new[0]
    plot.x_range.end = new[1]
    plot2.x_range.start = new[0]
    plot2.x_range.end = new[1]
    
    
source = ColumnDataSource(data={'x': data_all['dates'], 'y': data_all['hauteur_pluie']})

largeur_bar = 24*3600*1000*0.9 #ce chiffre est très grand car la résolution des barres est de 1 milliseconde !
plot_titre_pluie = "Météo aux Bouchaux - hauteur d'eau en mm"

plot = make_plot_pluie(source, plot_titre_pluie)




""" 2-- plot TEMPERATURE """

def make_plot_temp(source, title):
    plot2 = figure(plot_width=largeur_plot, plot_height=300, x_axis_type='datetime', x_range=(date(2019, 1, 1), date(2020, 1, 1)))
#    plot2.title.text = title
    glyph = Line(x='x', y='y1',
                 line_width=1,
                 line_alpha=0.9,
                 line_color="#393b79")
                 
    glyph2 = Line(x='x', y='y2',
                 line_width=1,
                 line_alpha=0.9,
                 line_color="#d62728")
                 
    plot2.add_glyph(source_temp, glyph)
    plot2.add_glyph(source_temp, glyph2)
    
    plot2.xaxis.axis_label = 'Date'
    plot2.yaxis.axis_label = "°C"
    plot2.axis.axis_label_text_font_style = "bold"
    plot2.background_fill_color = "beige"
    plot2.background_fill_alpha = 0.5
    plot2.xaxis.formatter = DatetimeTickFormatter(months = ['%b %Y'])
    plot2.grid.grid_line_alpha = 0.5
    return plot2

source_temp = ColumnDataSource(data={'x': data_all['dates'], 'y1': data_all['temp_mini'], 'y2': data_all['temp_maxi']})

plot_titre_temp = "Météo aux Bouchaux - température en °C"
plot2 = make_plot_temp(source_temp, plot_titre_temp)





"""  DateRangeSlider widget  """

Date_slider = DateRangeSlider(title="période: ", start=startdate, end=enddate,
                                 value=(date(2019, 1, 1), date(2020, 1, 1)), step=1,
                                 width = largeur_plot - 77) 

Date_slider.on_change('value', update_range)



controls = Date_slider
curdoc().add_root(column(plot, plot2, controls))
curdoc().title = "Météo Bouchaux"

#show(plot)

""" FIN MODULE GLOBAL """


""" MODULE MOIS par MOIS """





""" FIN MODULE MOIS par MOIS """




""" MODULE STATS """

""" FIN MODULE STATS """















