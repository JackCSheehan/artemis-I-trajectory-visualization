import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.animation as animation
import matplotlib as mpl
import pandas as pd
import numpy as np
from constants import *

# Class used for handling visualizations
class ArtemisVis:
    # Sets up Matplotlib
    def __init__(self):
        mpl.rcParams["toolbar"] = "None"

        self.fig = plt.figure(figsize = (9, 5))
        self.fig.suptitle("Artemis I")
        self.fig.subplots_adjust(top = 0.90, bottom = 0.1, left = 0.1, right = 0.90)

        self.gs = GridSpec(2, 3, figure = self.fig)
        self.gs.update(wspace = .3, hspace = .3)

        # Color settings
        mpl.rcParams["text.color"] = "white"
        mpl.rcParams["axes.labelcolor"] = "white"
        mpl.rcParams["xtick.labelcolor"] = "white"
        mpl.rcParams["ytick.labelcolor"] = "white"
        mpl.rcParams["axes.edgecolor"] = "white"
        mpl.rcParams["axes.facecolor"] = "black"
        self.fig.set_facecolor("black")

    # Sets up the four plot areas
    def setup_plots(self):
        # Info plot shows live-updating text
        self.info_plot = self.fig.add_subplot(self.gs.new_subplotspec((0, 0)))
        self.info_plot.axis("off")
        self.info_plot.text(0, .7, "Time: Nov 17 14:45 UTC")
        self.info_plot.text(0, .5, "Distance: 1000 km")
        self.info_plot.text(0, .3, "Velocity: 1000 km/s")

        # Plots distance over time
        self.distance_plot = self.fig.add_subplot(self.gs.new_subplotspec((0, 1)))
        self.distance_plot.set_xlabel("time")
        self.distance_plot.set_ylabel("distance (km)")

        # Plots velocity over time
        self.vel_plot = self.fig.add_subplot(self.gs.new_subplotspec((0, 2)))
        self.vel_plot.set_xlabel("time")
        self.vel_plot.set_ylabel("velocity (km/s)")

        # Shows Orion in space relative to Earth and Moon
        self.map_plot = self.fig.add_subplot(self.gs.new_subplotspec((1, 0), colspan = 3))
        self.map_plot.set_xlabel("distance (km)")
        self.map_plot.set_ylabel("distance (km)")
        self.map_plot.axis("equal")

    # Draws the Earth and Moon, to scale, on the map plot
    def plot_earth_and_moon(self):
        theta = np.linspace(0, 2 * np.pi, 15)
        
        # Calculate cartesian coords of Earth-sized circle and plot
        earth_x = EARTH_RADIUS * np.cos(theta)
        earth_y = EARTH_RADIUS * np.sin(theta)
        self.map_plot.fill_between(earth_x, earth_y, color = EARTH_COLOR)

        # Calculate cartesian coords of Moon-sized circle and plot
        moon_x = MOON_RADIUS * np.cos(theta) + 384400
        moon_y = MOON_RADIUS * np.sin(theta)

        self.map_plot.fill_between(moon_x, moon_y, color = MOON_COLOR)

    def show(self):
        plt.show()

artemis = ArtemisVis()
artemis.setup_plots()
artemis.plot_earth_and_moon()

orion_df = pd.read_csv("../data/orion.txt", names = [
    "time",
    "pos_x",
    "pos_y",
    "pos_z",
    "vel_x",
    "vel_y",
    "vel_z"
], header = None, sep = "\s+")

# Extract specific data columns from Orion dataframe
time_data = []
pos_x = orion_df["pos_x"].to_list()[::20]
pos_y = orion_df["pos_y"].to_list()[::20]
distance = []
vel = []

def animate(i):
    artemis.map_plot.plot(pos_x[0:i], pos_y[0:i], color = "red")

    # Since plot is not cleared, the previously plotted values can be removed from the list as it is
    # no longer needed
    try:
        pos_x.pop(0)
        pos_y.pop(0)
    except:
        return

ani = animation.FuncAnimation(artemis.fig, animate, interval = 0)

artemis.show()



