from artemis_vis import *
from moon_tracker import MoonTracker
import pandas as pd
import numpy as np
from skyfield.api import utc
from constants import *

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
time_data = orion_df["time"].to_list()
pos_x = orion_df["pos_x"].to_list()
pos_y = orion_df["pos_y"].to_list()
distance = orion_df["distance"].to_list()
vel = orion_df["vel"].to_list()

moon_tracker = MoonTracker()

print("Setting up Artemis visualizer...")
artemis = ArtemisVis(len(time_data), MAX_X, MIN_X, MAX_Y, MIN_Y)

print("Setting up plots...")
artemis.setup_plots()

moon_pos_x = []
moon_pos_y = []

print("Gathering Moon positions...")

for dt in time_data:
    current_time = dt.to_pydatetime().replace(tzinfo=utc)
    moon_position = moon_tracker.get_xy(current_time)

    moon_pos_x.append(moon_position[0])
    moon_pos_y.append(moon_position[1])

artemis.show()

artemis.animate(time_data, pos_x, pos_y, distance, vel, moon_pos_x, moon_pos_y)

# Blocking function call to stop window from closing after animation
input("")
