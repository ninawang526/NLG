import json
from database_init import db
from calculations import *
from PRACTICE_CONSTANTS import *

################# populates filler, energy, & pace data #################

# Gets session usage (wpm), average usage. The change per session, stddev,
# and level are all measured by **difference from IDEAL_WPM_MIN/MAX**,
# so as to provide a range. Disregards "orai_sample" and sessions
# shorter than 3 seconds. If < 3 sessions overall, only fill in session usage.
def getPaceData(session_id, user_id):
    paceData = {}

    statement = "SELECT session_id, wpm_average, wpm_variation " \
                "FROM public.sessions " \
                "WHERE user_id = \'" + user_id + "\'" \
                "ORDER BY session_date DESC"
    data = db.engine.execute(statement)

    pastUsages = []
    for item in data:
        sessionId = item[0]
        if sessionId == 'orai_sample':
            continue

        wpm = item[1]

        if sessionId == session_id:
            paceData["usage"] = wpm
        else:
            pastUsages.append(wpm)

        wpmVariations = json.loads(item[2])

    if len(pastUsages) >= 3:
        paceData["avg"] = sum(pastUsages) / float(len(pastUsages))

        # absolute MAGNITUDE difference from ideal wpm
        magnitudes = [magnitude(x, IDEAL_WPM_MIN, IDEAL_WPM_MAX) for x in pastUsages]
        ds = getDeltaAndStddev(magnitudes)
        paceData["change-per-session"] = ds["avg-delta"]
        paceData["stddev"] = ds["stddev"]

    # determining levels
    usage = magnitude(paceData["usage"], IDEAL_WPM_MIN, IDEAL_WPM_MAX)
    paceData["session-level"] = determineLevel(usage, "pace")

    if len(pastUsages) >= 3:
        pastUsages.append(paceData["usage"])
        allDataAvg = sum(pastUsages) / float(len(pastUsages))
        usage = magnitude(allDataAvg, IDEAL_WPM_MIN, IDEAL_WPM_MAX)
        paceData["overall-level"] = determineLevel(usage, "pace")


    # determining variations
    wpmslist = []
    for i in range(len(wpmVariations)):
        wpmslist.append(wpmVariations[str(i)]["wpm"])

    stddev = []




    return paceData



# Gets session usage (vocal vars per minute), average usage. Change per session,
# stddev, and level are all measured by **difference from IDEAL_VOCAL_VARIATIONS_MIN/MAX**,
# so as to provide a range. Disregards "orai_sample" and sessions
# shorter than 3 seconds. If < 3 sessions overall, only fill in session usage.
def getEnergyData(session_id, user_id):
    energyData = {}

    statement = "SELECT session_id, vocal_variation, total_time " \
                "FROM public.sessions " \
                "WHERE user_id = \'" + user_id + "\'" \
                "ORDER BY session_date DESC"
    data = db.engine.execute(statement)

    pastUsages = []
    for item in data:
        sessionId = item[0]
        if sessionId == 'orai_sample':
            continue

        seconds = item[2]
        minutes = float(seconds / 60)
        if minutes == 0:
            vvpm = 0
        else:
            vvpm = item[1] / minutes

        if sessionId == session_id:
            energyData["usage"] = vvpm
        elif seconds > 3:
            pastUsages.append(vvpm)

    if len(pastUsages) >= 3:
        energyData["avg"] = sum(pastUsages) / float(len(pastUsages))

        # absolute MAGNITUDE distance from ideal vvpm
        magnitudes = [magnitude(x, IDEAL_VOCAL_VARIATIONS_MIN, IDEAL_VOCAL_VARIATIONS_MAX) for x in pastUsages]
        ds = getDeltaAndStddev(magnitudes)
        energyData["change-per-session"] = ds["avg-delta"]
        energyData["stddev"] = ds["stddev"]

    # determining level
    usage = magnitude(energyData["usage"], IDEAL_VOCAL_VARIATIONS_MIN, IDEAL_VOCAL_VARIATIONS_MAX)
    energyData["session-level"] = determineLevel(usage, "energy")

    if len(pastUsages) >= 3:
        pastUsages.append(energyData["usage"])
        allDataAvg = sum(pastUsages) / float(len(pastUsages))
        usage = magnitude(allDataAvg, IDEAL_VOCAL_VARIATIONS_MIN, IDEAL_VOCAL_VARIATIONS_MAX)
        energyData["overall-level"] = determineLevel(usage, "energy")

    return energyData


# Gets session usage (fillers per minute), average usage, change per session,
# stddev, and session/overall level. Disregards "orai_sample" and sessions
# shorter than 3 seconds. If < 3 sessions overall, only fill in session usage.
def getFillerData(session_id, user_id):
    fillerData = {}

    statement = "SELECT session_id, fillers_summary, total_time " \
                "FROM public.sessions " \
                "WHERE user_id = \'" + user_id + "\'" \
                "ORDER BY session_date DESC"
    data = db.engine.execute(statement)

    pastUsages = []
    for item in data:
        sessionId = item[0]
        if sessionId == 'orai_sample':
            continue

        fillerWords = json.loads(item[1])
        count = 0
        for index, value in fillerWords.iteritems():
            count = count + value["Value"]

        seconds = item[2]
        minutes = float(seconds / 60)
        if minutes == 0:
            usage = 0
        else:
            usage = count / minutes

        if sessionId == session_id:
            fillerData["usage"] = usage
        elif seconds > 3:
            pastUsages.append(usage)

    if len(pastUsages) >= 3:
        fillerData["avg"] = sum(pastUsages) / float(len(pastUsages))
        ds = getDeltaAndStddev(pastUsages)
        fillerData["change-per-session"] = ds["avg-delta"]
        fillerData["stddev"] = ds["stddev"]

    # determining levels
    fillerData["session-level"] = determineLevel(fillerData["usage"], "filler")

    if len(pastUsages) >= 3:
        pastUsages.append(fillerData["usage"])
        allDataAvg = sum(pastUsages) / float(len(pastUsages))
        fillerData["overall-level"] = determineLevel(allDataAvg, "filler")

    return fillerData
