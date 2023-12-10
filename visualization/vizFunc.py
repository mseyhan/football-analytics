# basics
import numpy as np
import pandas as pd
import math
import json
from scipy.stats import t
from scipy import stats
import time

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
with open('../config.json', 'r') as config_file:
    config = json.load(config_file)

# database path
db_path = config.get('statsbomb_db_path')

def get_config_cmap(cmap_name,n=int()):
    try:
        cmap = LinearSegmentedColormap.from_list(config["cmaps"][cmap_name]["name"],
                                                 config["cmaps"][cmap_name]["colors"],
                                                 n)
    except:
        print("No colormap was found in config.json")
    return cmap

# stored keys as json to integers for mapping
def keystoint(x):
    return {int(k): v for k, v in x.items()}

# get formation mapping, keys stored as integers
formation_dict = json.loads(json.dumps(config['formation_dict']['EN']), object_hook=keystoint) # set an object hook to get integers

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
        self.playerNameFont = FontManager(url=config["fonts"]["rubik"])
        self.captionFont = FontManager(url=config["fonts"]["bebas_neue"])
        self.nameTagFont = FontManager(url=config["fonts"]["roboto_regular"])
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


def get_selected_matches():
    # RUN ONLY WHEN WORKING A DIFFERENT PLAYER/SEASON
    # connect to the sqlite database
    conn = sqlite3.connect(db_path)

    with open('data/selected_matches.sql') as inserts:
        q1 = inserts.read()

    # retrieve all matchdata
    seasonId = 27 # only for reporting, change in .sql file
    competitionId = 2
    query = q1
    print(query)
    # use the connection and query to create a dataframe
    matches = pd.read_sql_query(query, conn)

    # close the connection
    conn.close()

    # RUN ONLY WHEN WORKING A DIFFERENT PLAYER/SEASON
    print(matches.head())
    match_list = matches.match_id.unique().tolist()
    return matches, match_list

def parse_insert_events_stg():
    print('Retrieve match list...')
    match_list = get_selected_matches()[0]
    print('match_list retrieved.')
    # create an sqlalchemy engine to connect to the SQLite database
    engine = create_engine(f'sqlite:///{db_path}')
    # instantiate a parser object
    parser = Sbopen()
    # RUN ONLY WHEN WORKING A DIFFERENT PLAYER-SEASON
    start_time = time.time()
    event_df_list = []
    print('GENERATE df_event ---------------------')
    for i, match in enumerate(match_list):
        print(f"{i} - ENTERED :",match)
        event_df_list.append(parser.event(match)[0])
        print("event appended\n---------------------")
    print("appending complete")

    df_event = pd.concat(event_df_list)
    print("Concatenation done")
    # in order not to do the same data retrieval over and over, using the to_sql function to write the dataframe to the sqlite database
    df_event.to_sql('event_stg', engine, if_exists='replace', index=False)
    end_time = time.time()
    duration = end_time - start_time
    print(f"It took {duration}")
    return df_event