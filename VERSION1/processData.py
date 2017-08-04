import json
import numpy as np
import math
import random

from database_init import db
from metricData import *
from trendData import *


############### TO DO ###################
# catch rounding imperfections: a wpm of 5 shouldn't be "better than avg of 5 wpm"

def parseData(name, session_id, user_id):
    data = {}

    statement = "SELECT total_time FROM public.sessions " \
                "WHERE session_id = \'" + session_id + "\'"
    results = db.engine.execute(statement)
    for item in results:
        if item[0] != None:
            data["session-length"] = item[0]
        else:
            raise Exception("session length is None")

    # if user has completed < 3 sessions, they get lite feedback
    statement = "SELECT count(session_id) FROM public.sessions " \
                "WHERE user_id = \'" + user_id + "\'"
    results = db.engine.execute(statement)
    for item in results:
        session_count = item[0]
        if session_count >= 3:
            data["version"] = "full"
        else:
            data["version"] = "lite"

    data["name"] = name

    data["filler-data"] = getFillerData(session_id, user_id)
    data["energy-data"] = getEnergyData(session_id, user_id)
    data["pace-data"] = getPaceData(session_id, user_id)

    data["trend-data"] = getTrendData(data)

    filler_level = data["filler-data"]["session-level"]
    energy_level = data["energy-data"]["session-level"]
    pace_level = data["pace-data"]["session-level"]
    data["session-level"] = (filler_level + energy_level + pace_level) / 3

    if data["version"] == "full":
        data["overall-level"] = determineOverallLevel(data)

    return data

if __name__ == '__main__':
    data = parseData("-KfZeYPfnHUlYNHRnrnj", "HEFVpmnkcVTLf8uhyb7DM2KnML13",)
