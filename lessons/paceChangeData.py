############################################################################
# This code uses the DTW algorithm to locate areas where the user changed
# pace from speech1->speech2.
############################################################################


import json
import os
import numpy as np
from nltk.metrics.distance import edit_distance
from matplotlib import pyplot as plt
from dtw import dtw
from timeContext import putInTimeContext, clean
from database_init import db


# Takes two word lists as input, returns areas of change from first version of speech to second.
def getPaceChangeData(wordlist1, wordlist2, total_time):
    results = {}

    results["version"] = version(total_time)
    if results["version"] == "none":
        return results

    global wl1, wl2
    wl1 = wordlist1
    wl2 = wordlist2

    # map corresponding words from speech2 to speech1
    global path
    path = getDtwPath(wl1, wl2)
    np.savetxt('path', path, fmt='%d')

    plotSpeeches(wl1, wl2, path)

    # compare on basis of speech 1
    start1 = wl1[0]["time"]
    end1 = wl1[len(wl1)-1]["time"]
    val1, val2 = compareChanges(start1, end1)
    results["val1"] = val1
    results["val2"] = val2
    results["overall"] = getOverall(val1, val2)

    start2 = wl2[0]["time"]
    end2 = wl2[len(wl2)-1]["time"]
    results["pace"] = getWPM(start2, end2, wl2)

    results["location_summary"] = getLocationSummary(results["overall"], end1)

    #flushResults(data)
    plt.show()

    return results


def flushResults(data):
    f = open("lessons_data", "w")
    f.write(json.dumps(results, indent=2))
    f.flush()
    f.close()


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


# Given a list of intervals, compare speech1 stats to speech2 stats, returns
# intervals with a delta value associated with each one.

# remember that trend refers to difference in time from word2 to word1;
# an increasing difference in time means that word2 is getting further
# from word1 in the positive direction, aka word2 is being spoken slower.
def compareChanges(start, end):
    results = []

    path1 = path[0]
    path2 = path[1]

    # traverse path to find the word1s at the time intervals
    i = 0
    startIndex = 0
    endIndex = 0

    while i < len(path1):
        if wl1[path1[i]]["time"] >= start:
            startIndex = i
            break
        i = i + 1

    while i < len(path1):
        if wl1[path1[i]]["time"] >= end:
            endIndex = i
            break
        i = i + 1

    # map the word1 to the corresponding word2
    w2start = wl2[path2[startIndex]]
    w2end = wl2[path2[endIndex]]

    w1start = wl1[path1[startIndex]]
    w1end = wl1[path1[endIndex]]

    val1 = getWPM(w1start["time"], w1end["time"], wl1)
    val2 = getWPM(w2start["time"], w2end["time"], wl2)

    return val1, val2


def fillWPMs(location_summary, wl1, wl2, sig, path):
    summary = {}
    times = location_summary["summary"]
    for spot in times:
        index = times[spot]["index"]
        info = sig[index]
        start = info["start"]
        end = info["end"]

        val1, val2 = compareChanges(start, end)
        summary[spot] = {"trend":info["trend"], "val1":val1, "val2":val2}

    results = {"split":location_summary["split"], "summary":summary}
    return results


# Given x and y data, returns a best-fit polynomial.
def findPolynomial(x, y):
    p = np.polyfit(x, y, 7)
    polynomial = np.poly1d(p)
    return polynomial


# Given a list of intervals, returns start-end times of significant ones.
def findSignificant(intervals, polynomial, duration):
    SLOPE_CUTOFF = .15
    TIME_CUTOFF = .25 * duration

    significant = []
    for item in intervals:
        start = item["start"]
        end = item["end"]

        dx = end-start
        dy = polynomial(end)-polynomial(start)
        slope = dy / float(dx)

        if dx > TIME_CUTOFF and abs(slope) > SLOPE_CUTOFF:
            # double check to eliminate any errors.
            val1, val2 = compareChanges(start, end)
            if (val1 > val2 and slope > 0) or (val1 < val2 and slope < 0):
                significant.append(item)

    return significant


# Given a polynomial, returns start-end times of all increasing/decreasing chunks
def findAllSlopePatterns(graph):
    patterns = []
    pos = False
    start = 0
    end = 0

    for i in range(len(graph)):
        if graph[i]["val"] > 0:
            if pos == False:
                if i>0:
                    patterns.append({"start":start,"end":end, "trend":"decreasing"})
                pos = True
                start = graph[i]["time"]
                end = graph[i]["time"]
            else:
                end = graph[i]["time"]

            if i == (len(graph)-1):
                patterns.append({"start":start,"end":end, "trend":"increasing"})

        else:
            if pos == True:
                if i>0:
                    patterns.append({"start":start,"end":end, "trend":"increasing"})
                pos = False
                start = graph[i]["time"]
                end = graph[i]["time"]
            else:
                end = graph[i]["time"]

            if i == (len(graph)-1):
                patterns.append({"start":start,"end":end, "trend":"decreasing"})

    return patterns


# maps function to best-fitting polynomial, then takes derivative to find areas
# of significant change.
def findSignificantChanges(x, y, wl1, wl2):
    polynomial = findPolynomial(x,y)
    deriv = polynomial.deriv() # function

    derivs = [{"time":time,"val":deriv(time)} for time in x]

    plotEquations(x, y, polynomial, deriv)

    allSlopePatterns = findAllSlopePatterns(derivs)

    # contexualize using speech one, so user can understand changes from 1->2
    duration = wl1[len(wl1)-1]["time"]
    significants = findSignificant(allSlopePatterns, polynomial, duration)

    return significants


# plots equations on graph
def plotEquations(x, y, poly, deriv):
    d = [deriv(val) for val in x]
    fitted = [poly(val) for val in x]

    ax1 = fig.add_subplot(3,1,2)
    ax1.plot(x,y)
    ax1.axhline(0,color="red",ls="dotted")
    ax1.plot(x,fitted,color="green")

    ax2 = fig.add_subplot(3,1,3)
    ax2.axhline(0,color="red",ls="dotted")
    ax2.plot(x, d,color="blue")


# plots speech match graph
def plotSpeeches(wl1, wl2, path):
    path1 = path[0]
    path2 = path[1]

    global fig
    fig = plt.figure(figsize=(6, 6))

    ax = fig.add_subplot(3,1,1)

    for i in range(0, len(path2), 5):
        start1 = wl1[path1[i]]["time"]
        start2 = wl2[path2[i]]["time"]
        ax.plot([start1, start2], [1, -1], lw=1, fillstyle="bottom",color="orange", solid_capstyle="butt")


def getDtwPath(wl1, wl2):
    transcript1 = " ".join([x["word"] for x in wl1])
    transcript2 = " ".join([x["word"] for x in wl2])

    x = transcript1.split()
    y = transcript2.split()

    dist, cost, acc, path = dtw(x, y, edit_distance)
    return path


def getDiffArray(wl1, wl2, path):
    speech1path = path[0]
    speech2path = path[1]

    diffs = []
    times = []

    f = open("timediff","w")
    # contextualize using speech1path
    for i in range(len(speech1path)): #range(len(speech2path)):
        word1 = wl1[speech1path[i]]
        word2 = wl2[speech2path[i]]
        f.write("%s %s %f \n" %(word1["word"], word2["word"], word2["time"]-word1["time"]))

        diff = word2["time"]-word1["time"]

        diffs.append(diff)
        times.append(word1["time"])

    f.flush()
    f.close()

    return times, diffs


def getLocationSummary(overall_trend, duration):
    # calculate time differences of corresponding words of speech2 to speech1
    x, y = getDiffArray(wl1, wl2, path)
    sig = findSignificantChanges(x, y, wl1, wl2)

    location_summary = putInTimeContext(sig, overall_trend, duration)

    if location_summary["split"] == "everywhere":
        return location_summary
    elif location_summary["split"] == "thirds":
        location_summary = clean(location_summary["summary"])

    location_summary = fillWPMs(location_summary, wl1, wl2, sig, path)
    return location_summary


def getOverall(val1, val2):
    if abs(val1-val2) < 5:
        return "same"
    elif val1 < val2:
        return "increasing"
    else:
        return "decreasing"


# for now, fetch from database
def version(session_id):
    statement = "SELECT total_time " \
                "FROM public.sessions " \
                "WHERE session_id = \'" + session_id + "\'"
    db_results = db.engine.execute(statement)
    for item in db_results:
        total_time = item[0]

    if total_time < 3:
        version = "none"
    else:
        version = "full"

    return version


if __name__ == '__main__':
    f1 = "sample1.json"
    f2 = "sample5.json"

    wl1 = getWordList(f1)
    wl2 = getWordList(f2)

    getSpeechChangeData(wl1, wl2)


#curl -X POST -u "a2c092e7-c9d5-4dd3-9e3e-7d9d810a250e":"xfBGkNCkAA8h" --header "Content-Type: audio/wav" --data-binary "@audio5.wav" "https://stream.watsonplatform.net/speech-to-text/api/v1/recognize?timestamps=true" > sample5.json
