#####################################################################
# if you want to measure a new topic, here is where you would put the code.
# basically, you just need to make a "topic list": [{"value","start","end"},...]
# then, in getInitialData(), update function with your new topic
#####################################################################

from database_init import db
import json
from dataCalculations import getData


def getWPM(start, end, wl):
    i = 0
    wc = 0

    while i < len(wl):
        if wl[i]["time"] < start:
            i = i + 1
        else:
            break

    while i < len(wl):
        if wl[i]["time"] <= end:
            wc = wc + 1
            i = i + 1
        else:
            break

    try:
        return (wc / float((end-start)/60))
    except ZeroDivisionError:
        return 0


# Gets WPM results from database and throws them into a list
def getWpmsList(session_id):
    statement = "SELECT wpm_variation, total_time " \
                "FROM public.sessions " \
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


def getPausesList(wl):
    # split speech into roughly 10-second chunks
    chunk_size = 10
    pause_groups = []
    wl_index = 0
    while wl_index < len(wl)-1:
        current_time = 0
        subgroup = []
        while current_time < chunk_size and wl_index < len(wl)-1:
            subgroup.append(wl[wl_index])
            duration = wl[wl_index+1]["start"] - wl[wl_index]["start"]
            current_time = current_time + duration
            wl_index = wl_index + 1
        pause_groups.append(subgroup)

    # calculate total pause length for each 10-second chunk
    pause_list = []
    for i in range(len(pause_groups)):
        chunk = pause_groups[i]

        pause_sum = 0
        for word in range(len(chunk)-1):
            pause = chunk[word+1]["start"]-chunk[word]["end"]
            if pause > .5:
                pause_sum = pause_sum + pause

        start = chunk[0]["start"]
        if i < len(pause_groups)-1:
            trailing_pause = pause_groups[i+1][0]["start"] - pause_groups[i][len(chunk)-1]["end"]
            if trailing_pause > .5:
                pause_sum = pause_sum + trailing_pause
            end = pause_groups[i+1][0]["start"]
        else:
            end = chunk[len(chunk)-1]["end"]

        pause_list.append({"start":start,"end":end,"value":pause_sum})

    return pause_list



# depending on length of speech, returns if feedback will be full, lite, or none.
def getVersion(elapsed_time, speaking_time):
    if elapsed_time < 5 or speaking_time < 3:
        version = "none"
    elif elapsed_time < 30:
        version = "lite"
    else:
        version = "full"

    return version



# things included: value, pace, location_summary, and reference to speech text.
def getInitialData(session_id, wl, topic):
    statement = "SELECT total_time " \
                "FROM public.sessions " \
                "WHERE session_id = \'" + session_id + "\'"
    db_results = db.engine.execute(statement)
    for item in db_results:
        speaking_time = item[0]

    try:
        elapsed_time = wl[len(wl)-1]["end"]
    except:
        elapsed_time = 0

    results = {}
    results["elapsed_time"] = elapsed_time
    results["speaking_time"] = speaking_time
    results["version"] = getVersion(elapsed_time, speaking_time)

    if results["version"] == "none" or len(wl)==0:
        return results

    start = wl[0]["time"]
    end = wl[len(wl)-1]["time"]


    if topic == "pace":
        wpms_list = getWpmsList(session_id)
        # std refers to the group standard dev: how much do groups have to vary
        # so that the change from group to group is considered significant
        results.update(getData(wpms_list, results["version"], high=160, low=130, std=5))
        results["pace-value"] = results["average"]

    elif topic == "pause":
        pauses_list = getPausesList(wl)
        results.update(getData(pauses_list, results["version"], high=3, low=2, std=.2))
        results["pace-value"] = getWPM(start, end, wl)

    else:
        raise Exception("unrecognized topic: %s" %(topic))

    return results













        #
