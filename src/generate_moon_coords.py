"""
Script used to pre-compute moon coordinates since generating the coordinates at run time takes too long
"""
from skyfield.api import utc
import pandas as pd
from skyfield.api import load
from constants import *

if __name__ == "__main__":
    orion_df = pd.read_csv(
        "../data/orion.txt",
        sep = "\s+",
        parse_dates = ["time"])
    time_data = orion_df["time"].to_list()

    # Set up Skyfield
    bodies = load("de421.bsp")

    moon_vs = bodies["moon"]
    earth_vs = bodies["earth"]

    timescale = load.timescale()

    moon_pos_x = []
    moon_pos_y = []

    # Get moon coordinates
    for dt in time_data:
        current_time = dt.to_pydatetime().replace(tzinfo=utc)

        # Gets Moon's position when viewed from Earth
        astrometric = moon_vs.at(timescale.from_datetime(current_time)).observe(earth_vs)
        moon_position = astrometric.apparent().position.km

        # Coordinate's signs come back as inverted from what they should be when viewing the positions from
        # above Earth's equatorial plane. As such, the moon positions must have their signs inverted
        moon_pos_x.append(-moon_position[0])
        moon_pos_y.append(-moon_position[1])

    # Save moon coordinates to separate file for reading later
    moon_df = pd.DataFrame({
        "moon_x": moon_pos_x,
        "moon_y": moon_pos_y,
    })

    moon_df.to_csv("../data/moon.csv")
