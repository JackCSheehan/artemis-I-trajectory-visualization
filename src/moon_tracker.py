from skyfield.api import load

# Class to handle tracking Moon's position
class MoonTracker:
    def __init__(self):
        bodies = load("de421.bsp")

        # Get Moon vector sum from Skyfield to plot its position
        self.moon_vs = bodies["moon"]

        # Earth vector sum is needed to indicate where we are observing Moon from
        self.earth_vs = bodies["earth"]

        # Get timescale used for getting Moon's position at various times
        self.timescale = load.timescale()

    # Returns x and y coordinates of Moon at the given datetime relative to Earth as tuple
    def get_xy(self, observation_datetime):
        astrometric = self.moon_vs.at(self.timescale.from_datetime(observation_datetime)).observe(self.earth_vs)
        moon_position = astrometric.apparent().position.km

        return (-moon_position[0], -moon_position[1])