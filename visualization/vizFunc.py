# basics
import numpy as np
import pandas as pd
import math
import json

# viz
import matplotlib.pyplot as plt
import seaborn as sns

# mplsoccer
from mplsoccer.pitch import Pitch
from mplsoccer import Sbopen
from mplsoccer import Pitch, VerticalPitch, FontManager

# shapes
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
# colors
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import Normalize

# cosmetics
from adjustText import adjust_text
from highlight_text import ax_text,fig_text
import matplotlib.patches as patches
#etl
from sqlalchemy import create_engine
import sqlite3

whites4background = ['#F8FAFC','#F7FAFC','#F9FAFC','#F1F5F9',
                     '#F9FAFB','#FAFAFA','#FAFAF9','#F6F6F8',
                     '#F5F5F4','#F7F7F9','#F8F8F8','#F2F2F2']

palette = ["#989898","#ffc100","#ff0057","#ff0057","#1a1a1a","#0d7177"]

# Load configuration from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

def get_config_cmap(cmap_name,n=int()):
    try:
        cmap = LinearSegmentedColormap.from_list(config["cmaps"][cmap_name]["name"],
                                                 config["cmaps"][cmap_name]["colors"],
                                                 n)
    except:
        print("No colormap was found in config.json")
    return cmap

def show_color_maps(cmaps):
    fig, axes = plt.subplots(figsize=(12, 5), nrows=8, ncols=2, constrained_layout=True)
    gradient = np.linspace(0, 1, 256)
    gradient = np.repeat(np.expand_dims(gradient, axis=0), repeats=10, axis=0)
    fm = FontManager()
    for i, cmap in enumerate(cmaps):
        axes[i, 0].axis('off')
        axes[i, 1].axis('off')
        axes[i, 0].imshow(gradient, cmap=cmap)
        axes[i, 1].text(0, 0.5, cmap.name, va='center', fontsize=20, fontproperties=fm.prop)

class footyviz:
    def __init__(self, data, pitch):
        # two eminent components, data and pitch
        self.data = data
        self.pitch = pitch
        self.pitchLengthX = 120 # predefined pitch length, changeable
        self.pitchWidthY = 80 # predefined pitch width, changeable
        self.figSizeX = 10 # predefined figure size x, changeable
        self.figSizeY = 7.727 # predefined figure size y, changeable
        self.zorder = 3 # starting zorder, will change in every addition
        self.backgroundColor = pitch.pitch_color
        self.scattyDotColor = 'grey'
        self.title_font = {'size':'20', 'color':'black', 'weight':'bold'}
        self.font_url = 'https://github.com/google/fonts/blob/main/ofl/bebasneue/BebasNeue-Regular.ttf?raw=true'
        self.seasonNameList = [value for value in self.data.season_name.unique() if not (isinstance(value, float) and np.isnan(value))]
        self.playerName = None
        # create a colormap
        self.colors = [(0, self.backgroundColor), (0.5, "yellow"), (1, "red")]
        self.colormap = LinearSegmentedColormap.from_list("custom_colormap", self.colors, N=100)
    def navigate(self, **filters):
        query_string = ' & '.join([f'({col} == {repr(val)})' for col, val in filters.items()])
    
        self.data = self.data.query(query_string)
        #return self.data
    def navigate_temp(self,**filters):
        query_string = ' & '.join([f'({col} == {repr(val)})' for col, val in filters.items()])
        return self.data.query(query_string)
    def heatmap(self,title):
        #self.backgroundColor = background_hex
        self.fig, self.ax = self.pitch.draw(figsize=(self.figSizeX, self.figSizeY),constrained_layout=False,tight_layout=True)
        kde = self.pitch.kdeplot(x=self.data.x,y=self.data.y,fill=True,ax=self.ax,shade_lowest=False,n_levels=1000,cmap= self.colormap)
        # Set the limits of the axes
        self.fig.set_facecolor(self.backgroundColor)
        self.ax.set_xlim(-0.5, self.pitchLengthX+0.5)
        self.ax.set_ylim(-0.27, self.pitchWidthY+0.1)
        self.ax.set_aspect('equal')
        self.ax.set_title(title, **self.title_font, loc='center')
        plt.gca().invert_yaxis()
        # Adding a fancy title

    def scatty(self):
        sns.scatterplot(x='x', y='y', data=self.data, ec=None,alpha=1, color = self.scattyDotColor,zorder=3, legend=False)


