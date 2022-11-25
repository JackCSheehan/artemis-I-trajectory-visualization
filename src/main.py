from artemis_vis import *
import pandas as pd
import numpy as np
from skyfield.api import utc
from constants import *

if __name__ == "__main__":
    # Read Orion data from CSV provided by NASA
    orion_df = pd.read_csv(
        "../data/orion.txt",
        sep = "\s+",
        parse_dates = ["time"]
    )

    # Remove every DIVIDE_BY row for performance reasons
    orion_df = orion_df.iloc[0::DIVIDE_BY]

    # Add calculated columns for distance and velocity
    orion_df["distance"] = np.sqrt(
        np.power(orion_df["pos_x"], 2) +
        np.power(orion_df["pos_y"], 2) +
        np.power(orion_df["pos_z"], 2)
    )

    orion_df["vel"] = np.sqrt(
        np.power(orion_df["vel_x"], 2) +
        np.power(orion_df["vel_y"], 2) +
        np.power(orion_df["vel_z"], 2)
    )

    # Extract specific data columns from Orion dataframe
    time_data = orion_df["time"].to_list()
    pos_x = orion_df["pos_x"].to_list()
    pos_y = orion_df["pos_y"].to_list()
    distance = orion_df["distance"].to_list()
    vel = orion_df["vel"].to_list()

    # Load pre-computed Moon coordinates
    moon_df = pd.read_csv("../data/moon.csv")
    moon_df = moon_df.iloc[0::DIVIDE_BY]

    moon_pos_x = moon_df["moon_x"].to_list()
    moon_pos_y = moon_df["moon_y"].to_list()

    artemis = ArtemisVis(len(time_data))
    artemis.show()

    artemis.animate(time_data, pos_x, pos_y, distance, vel, moon_pos_x, moon_pos_y)
