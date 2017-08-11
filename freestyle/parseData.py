############################################################################
# This file begins the data processing
############################################################################

from database_init import db
import json
import numpy as np
import matplotlib.pyplot as plt
from dataCalculations import getData, plt


# Fetches all the data needed to form a document plan.
def parseData(session_id):
    statement = "SELECT total_time " \
                "FROM public.sessions " \
                "WHERE session_id = \'" + session_id + "\'"
    db_results = db.engine.execute(statement)
    for item in db_results:
        speaking_time = item[0]

    wpms_list = getWpmsList(session_id)
    energy_list = getEnergyList(session_id)
    try:
        elapsed_time = energy_list[len(energy_list)-1]["end"]
    except:
        elapsed_time = 0

    data = {}
    data["elapsed_time"] = elapsed_time
    data["speaking_time"] = speaking_time
    data["version"] = getVersion(elapsed_time, speaking_time)
    data["energy-data"] = getData(data["version"], energy_list, high=.2, low=-.2, std=0)
    data["pace-data"] = getData(data["version"], wpms_list, high=160, low=140, std=5)

    return data


# Gets WPM results from database and throws them into a list: {"value","start","end"}
def getWpmsList(session_id):
    statement = "SELECT wpm_variation FROM public.sessions " \
                "WHERE session_id = \'" + session_id + "\'"
    data = db.engine.execute(statement)
    for item in data:
        wpms_dict = json.loads(item[0])

    wpms_list = []
    for i in range(len(wpms_dict)):
        start = wpms_dict[str(i)]["range"]["0"]
        end = wpms_dict[str(i)]["range"]["1"]
        wpm = wpms_dict[str(i)]["wpm"]
        wpms_list.append({"value":wpm, "start":start, "end":end})

    return wpms_list


# format: {"value","start","end"}
def getEnergyList(session_id):
    statement = "SELECT energy_values FROM public.sessions " \
                "WHERE session_id = \'" + session_id + "\'"
    data = db.engine.execute(statement)
    for item in data:
        energy_dict = json.loads(item[0])

    energy_list = []
    for i in range(len(energy_dict)):
        if i == 0:
            start = 0
        else:
            start = translateTime(energy_dict[str(i-1)]["Label"])

        end = translateTime(energy_dict[str(i)]["Label"])
        rating = energy_dict[str(i)]["Rating"]
        energy_list.append({"value":rating, "start":start, "end":end})

    return energy_list


# turn mm:ss time format into number of seconds
def translateTime(s):
    array = s.split(":")
    mins = int(array[0])
    secs = int(array[1])
    return (mins*60)+secs


# depending on length of speech, returns if feedback will be full, lite, or none.
def getVersion(elapsed_time, speaking_time):
    if elapsed_time < 5 or speaking_time < 3:
        version = "none"
    elif elapsed_time < 30:
        version = "lite"
    else:
        version = "full"

    return version


if __name__ == '__main__':
    session_id = "-Kf_2PJrnHUlYNHRnrnj"
    data = parseData(session_id)
