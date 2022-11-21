import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.patches as patches
import matplotlib as mpl
from matplotlib.ticker import FormatStrFormatter
from constants import *
from utils import *

# Global matplotlib settings

# Removes matplotlib's toolbar
mpl.rcParams["toolbar"] = "None"

# Color settings
mpl.rcParams["text.color"] = FG_COLOR
mpl.rcParams["axes.labelcolor"] = FG_COLOR
mpl.rcParams["xtick.labelcolor"] = FG_COLOR
mpl.rcParams["ytick.labelcolor"] = FG_COLOR
mpl.rcParams["axes.edgecolor"] = FG_COLOR
mpl.rcParams["axes.facecolor"] = BG_COLOR

# Class used for handling matplotlib plotting and animations
class ArtemisVis:
    # Sets up matplotlib. Takes the number of time data points for scaling the distance/velocity plots and the max/min
    # values for each axis of the map plot
    def __init__(self, date_count, max_x, min_x, max_y, min_y):
        # Set up figure
        self.fig = plt.figure("Artemis I", figsize = (9, 5))
        self.fig.set_facecolor(BG_COLOR)
        self.fig.subplots_adjust(top = 0.95, bottom = 0.1, left = 0.11, right = 0.98)

        # Since plot is set to not block, must close program when user closed window since program is kept
        # going by an input() call at the end
        self.fig.canvas.mpl_connect("close_event", self.__exit_program)

        # Set up GridSpec used to arrange subplots
        self.gs = GridSpec(3, 3, figure = self.fig)
        self.gs.update(wspace = .3, hspace = .45)

        self.date_count = date_count
        self.map_max_x = max_x
        self.map_min_x = min_x
        self.map_max_y = max_y
        self.map_min_y = min_y

    # Used to end program when matplotlib window closed
    def __exit_program(self, _):
        exit(0)

    # Sets up the four plot areas
    def setup_plots(self):
        # Info plot shows live-updating text
        self.info_plot = self.fig.add_subplot(self.gs.new_subplotspec((0, 0)))
        self.info_plot.axis("off")

        # Plots distance over time
        self.distance_plot = self.fig.add_subplot(self.gs.new_subplotspec((0, 1)))
        self.distance_plot.set_title("Distance From Earth (km)")
        self.distance_plot.set_xlim([0, self.date_count])
        self.distance_plot.set_ylim([0, MAX_DISTANCE])
        self.distance_plot.set_xticks([], [])
        self.distance_plot.set_xlabel("time")
        self.distance_plot.set_ylabel("distance (km)")

        # Plots velocity over time
        self.vel_plot = self.fig.add_subplot(self.gs.new_subplotspec((0, 2)))
        self.vel_plot.set_title("Velocity (km/s)")
        self.vel_plot.set_xlim([0, self.date_count])
        self.vel_plot.set_ylim([0, MAX_VELOCITY])
        self.vel_plot.set_xticks([], [])
        self.vel_plot.set_xlabel("time")
        self.vel_plot.set_ylabel("velocity (km/s)")

        # Shows Orion trajectory
        self.map_plot = self.fig.add_subplot(self.gs.new_subplotspec((1, 0), colspan = 3, rowspan = 2))
        self.map_plot.set_title("Orion's Trajectory")
        self.map_plot.axis("equal")
        self.map_plot.set_xlim([self.map_min_x, self.map_max_x])
        self.map_plot.set_ylim([self.map_min_y, self.map_max_y])
        self.map_plot.set_xlabel("distance (1000 km)")
        self.map_plot.set_ylabel("distance (km)")

        # Prevents abbreviation of large numbers on x axis
        self.fig.gca().xaxis.set_major_formatter(FormatStrFormatter("%d"))

        # Draw Earth
        self.map_plot.add_patch(patches.Circle((0, 0), radius = EARTH_RADIUS, color = EARTH_COLOR))

    # Animates plots using blitting. Takes time data, Orion x/y positions, distances, velocities, and moon x/y positions
    def animate(self, time_data, pos_x, pos_y, distance, vel, moon_pos_x, moon_pos_y):
        background = self.fig.canvas.copy_from_bbox(self.fig.bbox)

        # Plot initial points to get artist objects
        (distance_artist,) = self.distance_plot.plot([-1], [-1], color = TELEMETRY_PLOT_COLORS, animated = True)
        (vel_artist,) = self.vel_plot.plot([-1], [-1], color = TELEMETRY_PLOT_COLORS, animated = True)
        (trace_artist,) = self.map_plot.plot([0], [0], color = ORION_TRACE_COLOR, animated = True)
        
        time_text = self.info_plot.text(0, 0.7, "")
        distance_text_artist = self.info_plot.text(0, .5, "")
        vel_text_artist = self.info_plot.text(0, .3, "")

        # Animate through all time values
        for i in range(len(time_data)):
            self.fig.canvas.blit(self.fig.bbox)
            self.fig.canvas.flush_events()
            self.fig.canvas.restore_region(background)
            
            distance_artist.set_xdata(range(0, i))
            distance_artist.set_ydata(distance[0:i])
            self.fig.draw_artist(distance_artist)

            vel_artist.set_xdata(range(0, i))
            vel_artist.set_ydata(vel[0:i])
            self.fig.draw_artist(vel_artist)

            trace_artist.set_xdata(pos_x[0:i])
            trace_artist.set_ydata(pos_y[0:i])
            self.fig.draw_artist(trace_artist)

            # Erase old moon by drawing a black circle on top of its previous position
            if i > 0:
                moon_eraser_artist = self.map_plot.add_patch(patches.Circle((moon_pos_x[i - 1], moon_pos_y[i - 1]), radius = MOON_RADIUS + MOON_ERASER_INCREASE, color = SPACE_COLOR))
                self.fig.draw_artist(moon_eraser_artist)

            moon_artist = self.map_plot.add_patch(patches.Circle((moon_pos_x[i], moon_pos_y[i]), radius = MOON_RADIUS, color = MOON_COLOR))
            self.fig.draw_artist(moon_artist)

            # Erase previous contents of the info box
            info_box_eraser = self.info_plot.add_patch(patches.Rectangle((0, 0), 1, 1, color = BG_COLOR))
            self.fig.draw_artist(info_box_eraser)

            # Animate text values
            time_text.set_text(format_time(time_data[i]))
            self.fig.draw_artist(time_text)

            distance_text_artist.set_text(f"Distance: {distance[i]:,.2f} km")
            self.fig.draw_artist(distance_text_artist)

            vel_text_artist.set_text(f"Velocity: {vel[i]:,.2f} km/s")
            self.fig.draw_artist(vel_text_artist)
            
    # Shows matplotlib window
    def show(self):
        plt.show(block = False)
