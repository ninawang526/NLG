import numpy as np
import math
from PRACTICE_CONSTANTS import *


# find average change of those values, and stddev of values
def getDeltaAndStddev(array):
    data = {"avg-delta":"","stddev":""}

    deltas = [] # represent change from prev session
    for i in range(len(array)-1):
        deltas.append(array[i] - array[i+1])

    data["avg-delta"] = float(sum(deltas)) / float(len(deltas))
    data["stddev"] = np.std(np.array(array))

    return data


# absolute difference of usage to ideal_min/max
def magnitude(usage, ideal_min, ideal_max):
    if usage > ideal_max:
        return usage - ideal_max
    elif usage < ideal_min:
        return ideal_min - usage
    else:
        return 0


def determineLevel(usage, area):
    if area == "filler":
        bounds = [0.4, 1.3, 2.0]
    elif area == "energy":
        bounds = [0, 1, 3]
    elif area == "pace":
        bounds = [0, 3, 8]
    else:
        raise Exception("unrecognized area: %s" %(area))

    if usage <= bounds[0]:
        return 4
    elif usage < bounds[1]:
        return 3
    elif usage < bounds[2]:
        return 2
    else:
        return 1


# somewhat arbitrary values?
def determineOverallLevel(data):
    levels = []

    filler_usage = magnitude(data["filler-data"]["avg"], 0, IDEAL_FILLERS_MAX)
    levels.append(determineLevel(filler_usage, "filler"))

    energy_delta = magnitude(data["energy-data"]["avg"], IDEAL_VOCAL_VARIATIONS_MIN, IDEAL_VOCAL_VARIATIONS_MAX)
    levels.append(determineLevel(energy_delta, "energy"))

    pace_delta = magnitude(data["pace-data"]["avg"], IDEAL_WPM_MIN, IDEAL_WPM_MAX)
    levels.append(determineLevel(pace_delta, "pace"))

    return sum(levels) / len(levels)


# simple formula: current + stddev
def determineGoal(area, data):
    goal = None
    direction = None
    session_length = None

    if area == "energy":
        current = data["energy-data"]["usage"]
        try:
            user_stddev = data["energy-data"]["stddev"]
            stddev = max(user_stddev, energy_default_std)
        except KeyError as e:
            stddev = energy_default_std

        # if already good, just aim to speak 30 seconds longer.
        if current <= IDEAL_VOCAL_VARIATIONS_MAX and current >= IDEAL_VOCAL_VARIATIONS_MIN:
            goal = current
            direction = "constant"
            session_length = int((data["session-length"] + 30) / 10) * 10

        elif current < IDEAL_VOCAL_VARIATIONS_MIN:
            goal = int(round(current + stddev))
            if goal > IDEAL_VOCAL_VARIATIONS_MAX:
                goal = IDEAL_VOCAL_VARIATIONS
            direction = "positive"

        elif current > IDEAL_VOCAL_VARIATIONS_MAX:
            goal = int(round(current - stddev))
            if goal < IDEAL_VOCAL_VARIATIONS_MIN:
                goal = IDEAL_VOCAL_VARIATIONS
            direction = "negative"


    elif area == "pace":
        current = data["pace-data"]["usage"]
        try:
            user_stddev = data["pace-data"]["stddev"]
            stddev = max(user_stddev, pace_default_std)
        except KeyError as e:
            stddev = pace_default_std

        # if already good, just aim to speak 30 seconds longer.
        if current <= IDEAL_WPM_MAX and current >= IDEAL_WPM_MIN:
            goal = current
            direction = "constant"
            session_length = int((data["session-length"] + 30) / 10) * 10

        elif current < IDEAL_WPM_MIN:
            goal = int(round(current + stddev))
            if goal > IDEAL_WPM_MAX:
                goal = IDEAL_WPM
            direction = "positive"

        elif current > IDEAL_WPM_MAX:
            goal = int(round(current - stddev))
            if goal < IDEAL_WPM_MIN:
                goal = IDEAL_WPM
            direction = "negative"


    elif area == "filler":
        current = data["filler-data"]["usage"]
        try:
            user_stddev = data["filler-data"]["stddev"]
            stddev = max(user_stddev, filler_default_std)
        except KeyError as e:
            stddev = filler_default_std

        # if already good, aim to speak 30 seconds longer.
        if current < IDEAL_FILLERS_MAX:
            goal = current
            session_length = int((data["session-length"] + 30) / 10) * 10
            direction = "constant"
        else:
            session_length = int((data["session-length"]) / 10) * 10
            goal_per_minute = math.floor(current - stddev)
            if goal_per_minute <= 0:
                goal = 0
            else:
                goal = int(math.floor(goal_per_minute * (session_length / 60)))
            direction = "negative"

    result = {}
    result["goal"] = goal
    result["direction"] = direction
    result["session-length"] = session_length

    return result
