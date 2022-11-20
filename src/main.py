import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.patches as patches
import matplotlib as mpl
import pandas as pd
import numpy as np
from skyfield.api import utc
from constants import *
from moon_tracker import MoonTracker

# Class used for handling visualizations
class ArtemisVis:
    # Sets up matplotlib. Takes the number of time data points for scaling the distance/velocity plots and the max/min
    # values for each axis of the map plot
    def __init__(self, date_count, max_x, min_x, max_y, min_y):
        # Removes matplotlib's toolbar
        mpl.rcParams["toolbar"] = "None"

        # Set up figure
        self.fig = plt.figure(figsize = (9, 5))
        self.fig.suptitle("Artemis I")
        self.fig.subplots_adjust(top = 0.90, bottom = 0.1, left = 0.1, right = 0.90)

        # Since plot is set to not block, must close program when user closed window since program is kept
        # going by an input() call at the end
        self.fig.canvas.mpl_connect("close_event", self.__exit_program)

        # Set up GridSpec used to arrange subplots
        self.gs = GridSpec(3, 3, figure = self.fig)
        self.gs.update(wspace = .3, hspace = .3)

        self.moon_tracker = MoonTracker()

        self.date_count = date_count
        self.map_max_x = max_x
        self.map_min_x = min_x
        self.map_max_y = max_y
        self.map_min_y = min_y

        # Color settings
        mpl.rcParams["text.color"] = FG_COLOR
        mpl.rcParams["axes.labelcolor"] = FG_COLOR
        mpl.rcParams["xtick.labelcolor"] = FG_COLOR
        mpl.rcParams["ytick.labelcolor"] = FG_COLOR
        mpl.rcParams["axes.edgecolor"] = FG_COLOR
        mpl.rcParams["axes.facecolor"] = BG_COLOR
        self.fig.set_facecolor(BG_COLOR)

    # Used to end program when matplotlib window closed
    def __exit_program(self, _):
        exit(0)

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
        self.distance_plot.set_xlim([0, self.date_count])
        self.distance_plot.set_ylim([0, MAX_DISTANCE])
        self.distance_plot.set_xticks([], [])
        self.distance_plot.set_xlabel("time")
        self.distance_plot.set_ylabel("distance (km)")

        # Plots velocity over time
        self.vel_plot = self.fig.add_subplot(self.gs.new_subplotspec((0, 2)))
        self.vel_plot.set_xlim([0, self.date_count])
        self.vel_plot.set_ylim([0, MAX_VELOCITY])
        self.vel_plot.set_xticks([], [])
        self.vel_plot.set_xlabel("time")
        self.vel_plot.set_ylabel("velocity (km/s)")

        # Shows Orion in space relative to Earth and Moon
        self.map_plot = self.fig.add_subplot(self.gs.new_subplotspec((1, 0), colspan = 3, rowspan = 2))
        self.map_plot.axis("equal")
        self.map_plot.set_xlim([self.map_min_x, self.map_max_x])
        self.map_plot.set_ylim([self.map_min_y, self.map_max_y])
        self.map_plot.set_xlabel("distance (1000 km)")
        self.map_plot.set_ylabel("distance (km)")

    # Draws the Earth and Moon, to scale, on the map plot
    def plot_earth_and_moon(self):
        theta = np.linspace(0, 2 * np.pi, BODY_RESOLUTION)
        
        # Calculate cartesian coords of Earth-sized circle and plot
        earth_x = EARTH_RADIUS * np.cos(theta)
        earth_y = EARTH_RADIUS * np.sin(theta)
        self.map_plot.fill_between(earth_x, earth_y, color = EARTH_COLOR)

        # Calculate initial cartesian coords of Moon-sized circle and plot
        self.moon_x = MOON_RADIUS * np.cos(theta)
        self.moon_y = MOON_RADIUS * np.sin(theta)

    # Creates background and artist objects required for animation
    def setup_animation(self):
        self.background = self.fig.canvas.copy_from_bbox(self.fig.bbox)

        # Plot initial points to get artist objects
        (self.distance_artist,) = self.distance_plot.plot(time_data[0], distance[0], color = TELEMETRY_PLOT_COLORS, animated = True)
        (self.vel_artist,) = self.vel_plot.plot(time_data[0], vel[0], color = TELEMETRY_PLOT_COLORS, animated = True)
        (self.trace_artist,) = self.map_plot.plot(pos_x[0], pos_y[0], color = ORION_TRACE_COLOR, animated = True)
        self.moon_artist = self.map_plot.add_patch(patches.Circle((0, 0), radius = 0, color = MOON_COLOR))
        self.moon_eraser_artist = self.map_plot.add_patch(patches.Circle((0, 0), radius = 0, color = SPACE_COLOR))

        self.fig.draw_artist(self.distance_artist)
        self.fig.draw_artist(self.vel_artist)
        self.fig.draw_artist(self.trace_artist)
        self.fig.draw_artist(self.moon_artist)
        self.fig.draw_artist(self.moon_eraser_artist)

    # Animates plots using blitting. Takes time data, x positions, y positions, distances, and velocities
    def animate(self, time_data, pos_x, pos_y, distance, vel, moon_pos_x, moon_pos_y):
        # Animate through all time values
        for i in range(len(time_data)):
            self.fig.canvas.blit(self.fig.bbox)
            self.fig.canvas.flush_events()
            
            self.fig.canvas.restore_region(self.background)
            
            # Update data points individually rather than re-plotting for better efficiency
            self.distance_artist.set_xdata(range(0, i))
            self.distance_artist.set_ydata(distance[0:i])

            self.vel_artist.set_xdata(range(0, i))
            self.vel_artist.set_ydata(vel[0:i])

            self.trace_artist.set_xdata(pos_x[0:i])
            self.trace_artist.set_ydata(pos_y[0:i])

            # Remove previous frame's patch so that more don't keep getting on top of old ones
            self.map_plot.patches.pop()

            # Erase old moon by drawing a black circle on top of its previous position
            if i > 0:
                self.moon_eraser_artist = self.map_plot.add_patch(patches.Circle((moon_pos_x[i - 1], moon_pos_y[i - 1]), radius = MOON_RADIUS + MOON_ERASER_INCREASE, color = SPACE_COLOR))
            
            self.moon_artist = self.map_plot.add_patch(patches.Circle((moon_pos_x[i], moon_pos_y[i]), radius = MOON_RADIUS, color = MOON_COLOR))

            self.fig.draw_artist(self.distance_artist)
            self.fig.draw_artist(self.vel_artist)
            self.fig.draw_artist(self.trace_artist)
            self.fig.draw_artist(self.moon_eraser_artist)
            self.fig.draw_artist(self.moon_artist)

    # Shows matplotlib window
    def show(self):
        plt.show(block = False)

orion_df = pd.read_csv("../data/orion.txt", names = [
    "time",
    "pos_x",
    "pos_y",
    "pos_z",
    "vel_x",
    "vel_y",
    "vel_z"
], header = None, sep = "\s+", parse_dates = ["time"])

# Add calculated columns for distance and velocity
orion_df["distance"] = np.sqrt(np.power(orion_df["pos_x"], 2) + np.power(orion_df["pos_y"], 2) + np.power(orion_df["pos_z"], 2))
orion_df["vel"] = np.sqrt(np.power(orion_df["vel_x"], 2) + np.power(orion_df["vel_y"], 2) + np.power(orion_df["vel_z"], 2))

# Extract specific data columns from Orion dataframe
time_data = orion_df["time"].to_list()[::20]
pos_x = orion_df["pos_x"].to_list()[::20]
pos_y = orion_df["pos_y"].to_list()[::20]
distance = orion_df["distance"].to_list()[::20]
vel = orion_df["vel"].to_list()[::20]

moon_tracker = MoonTracker()

artemis = ArtemisVis(len(time_data), MAX_X, MIN_X, MAX_Y, MIN_Y)
artemis.setup_plots()
artemis.plot_earth_and_moon()

moon_pos_x = []
moon_pos_y = []

for dt in time_data:
    current_time = dt.to_pydatetime().replace(tzinfo=utc)
    moon_position = moon_tracker.get_xy(current_time)

    #moon_pos_x.append(artemis.moon_x + moon_position[0])
    #moon_pos_y.append(artemis.moon_y + moon_position[1])
    moon_pos_x.append(moon_position[0])
    moon_pos_y.append(moon_position[1])

artemis.setup_animation()
artemis.show()

artemis.animate(time_data, pos_x, pos_y, distance, vel, moon_pos_x, moon_pos_y)

# Blocking function call to stop window from closing after animation
input("")
