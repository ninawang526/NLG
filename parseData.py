from database_init import db
import json
import numpy as np
import matplotlib.pyplot as plt
from metricData import getPaceData


def parseData(name, session_id):
    data = {}

    statement = "SELECT wpm_variation, total_time " \
                "FROM public.sessions " \
                "WHERE session_id = \'" + session_id + "\'"
    db_results = db.engine.execute(statement)
    for item in db_results:
        wpms = json.loads(item[0])

    session_length = wpms[str(len(wpms)-1)]["range"]["1"]

    # if session length < 15 seconds, they get lite feedback
    if session_length >= 15:
        data["version"] = "full"
    else:
        print session_length
        raise Exception("short")
        data["version"] = "lite"

    data["name"] = name
    data["pace-data"] = getPaceData(session_id)

    return data


if __name__ == '__main__':
    #session_id = "-Kfsn6SJ90E4xx1ZDAf9"
    #user_id = "EaMibpsK4uPHFCB4EiGZ0Rpqf5D3"

    #session_id = "-Kf_3BtznHUlYNHRnrnj"
    #user_id = "jXBraUQxenNEcJsBOlqSrbc97xh2"

    session_id = "-Kf_2PJrnHUlYNHRnrnj"

    #session_id = "-KfgFyu4U1ZI7m5YeiZb"

    #session_id = "-KfbR79qTRv7k4GAu4lt"
    #user_id = "8OZ5Gp9cF4aDPDqstL2ySjpf8mJ2"

    #session_id = "-KfDgUY4-TVEcUGQmzeP"
    #user_id = "zMza7lNNvlY9gJYa9Oos8LW46Pg2"

    data = parseData("[name]", session_id)
