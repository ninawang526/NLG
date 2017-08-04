import math
from calculations import *


def getTrendData(data):
    trendData = {}

    # calculating "overall-change-per-session": (change-per-session / stddev) * 100
    if data["version"] == "full":
        energy_change = data["energy-data"]["change-per-session"]
        energy_std = data["energy-data"]["stddev"]
        pace_change = data["pace-data"]["change-per-session"]
        pace_std = data["pace-data"]["stddev"]
        filler_change = data["filler-data"]["change-per-session"]
        filler_std = data["filler-data"]["stddev"]

        percent_change = 0
        if filler_std != 0:
            percent_change = (float(filler_change) / filler_std) * 100
        # flip the sign; decrease in fillers is a positive change
        filler_trend = 0 - percent_change

        # the more negative the better (decreasing distance to IDEAL_VOCAL_VARIATIONS)
        percent_change = 0
        if energy_std != 0:
            percent_change = (float(energy_change) / energy_std) * 100
        energy_trend = 0 - percent_change

        percent_change = 0
        if pace_std != 0:
            percent_change = (float(pace_change) / pace_std) * 100
        pace_trend = 0 - percent_change

        trendData["overall-change-per-session"] = float(filler_trend + energy_trend + pace_trend) / 3.0

    # calculating focus of next session; determined by weakest field this session
    levels = {}
    levels["filler"] = data["filler-data"]["session-level"]
    levels["energy"] = data["energy-data"]["session-level"]
    levels["pace"] = data["pace-data"]["session-level"]

    area_of_improvement = min(levels, key=levels.get)

    improvementData = determineGoal(area_of_improvement, data)
    improvementData["area"] = area_of_improvement
    trendData["next-session"] = improvementData

    return trendData
