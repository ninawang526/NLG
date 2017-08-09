import json
import os
import numpy as np
from nltk.metrics.distance import edit_distance
from matplotlib import pyplot as plt
from dtw import dtw
from timeContext import putInTimeContext, clean

# Tailor this according to how the input file is structured.
def getWordList(filename):
    with open(filename) as f:
        data = json.loads(f.read())

    results = data["results"]
    if len(results) > 0:
        try:
            STARTPAD = results[0]["alternatives"][0]["timestamps"][0][1]
        except (KeyError, IndexError) as e:
            STARTPAD = 0

    wordList = []
    for entry in results:
        if entry["final"] is True:
            try:
                timestamps = entry["alternatives"][0]["timestamps"]
                for word in timestamps:
                    if word[0] != "%HESITATION":
                        wordList.append({"word":word[0], "time":word[1]-STARTPAD})
            except (KeyError, IndexError) as e:
                continue

    return wordList


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
            #print wl[i]["word"],
            wc = wc + 1
            i = i + 1
        else:
            break

    #print "\n"
    try:
        return (wc / float((end-start)/60))
    except ZeroDivisionError:
        return 0


# Given a list of intervals, compare speech1 stats to speech2 stats, returns
# intervals with a delta value associated with each one
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

    print "start index: %d, end index: %d" %(startIndex, endIndex)

    # map the word1 to the corresponding word2
    w2start = wl2[path2[startIndex]]
    w2end = wl2[path2[endIndex]]
    #print 'w2:', w2start["time"], w2end["time"]

    w1start = wl1[path1[startIndex]]
    w1end = wl1[path1[endIndex]]
    #print 'w1:', w1start["time"], w1end["time"]

    val1 = getWPM(w1start["time"], w1end["time"], wl1)
    val2 = getWPM(w2start["time"], w2end["time"], wl2)

    # remember that trend refers to difference in time from word2 to word1;
    # an increasing difference in time means that word2 is getting further
    # from word1 in the positive direction, aka word2 is being spoken slower.
    #if interval["trend"] == "increasing":
    #    change = "slower"
    #else:
    #    change = "faster"

    #print "val1: %f, val2: %f" %(val1, val2)
    return val1, val2


def fillWPMs(location_summary, wl1, wl2, sig, path):
    split = location_summary["split"]

    summary = {}
    times = location_summary["summary"]
    for spot in times:
        index = times[spot]["index"]
        info = sig[index]
        start = info["start"]
        end = info["end"]

        val1, val2 = compareChanges(start, end)
        summary[spot] = {"trend":info["trend"], "val1":val1, "val2":val2}

    results = {"split":split, "summary":summary}
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
            else:
                print "failed; start = %f, end = %f, val1 = %f, val2 = %f" %(start, end, val1, val2)

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


# Takes two word lists as input, returns areas of change from first version of speech to second.
# Word lists must be in this format: [{word:"hello", time:3}, ...]
def getSpeechChangeData(wordlist1, wordlist2):
    results = {}

    global wl1
    wl1 = wordlist1

    global wl2
    wl2 = wordlist2

    if len(wl1)==0 or len(wl2)==0:
        return results

    # map corresponding words from speech2 to speech1
    global path
    path = getDtwPath(wl1, wl2)
    np.savetxt('path', path, fmt='%d')

    #path = np.loadtxt("path", dtype=int)
    plotSpeeches(wl1, wl2, path)

    start1 = wl1[0]["time"]
    end1 = wl1[len(wl1)-1]["time"]

    val1, val2 = compareChanges(start1, end1)
    results["val1"] = val1
    results["val2"] = val2
    print val1, val2

    if abs(val1 - val2) < 5:
        results["overall"] = "same"
    elif val1 < val2:
        results["overall"] = "decreasing"
    else:
        results["overall"] = "increasing"

    start2 = wl2[0]["time"]
    end2 = wl2[len(wl2)-1]["time"]
    results["pace"] = getWPM(start2, end2, wl2)


    # calculate time differences of corresponding words of speech2 to speech1
    x, y = getDiffArray(wl1, wl2, path)
    sig = findSignificantChanges(x, y, wl1, wl2)
    print sig

    location_summary = putInTimeContext(sig, results["overall"], end1)

    if location_summary["split"] == "thirds":
        summary = clean(location_summary["summary"])
    else:
        summary = location_summary

    if location_summary["split"] != "everywhere":
        results["location_summary"] = fillWPMs(summary, wl1, wl2, sig, path)
    else:
        results["location_summary"] = summary

    f = open("lessons_data", "w")
    f.write(json.dumps(results, indent=2))
    f.flush()
    f.close()

    plt.show()

    return results


if __name__ == '__main__':
    f1 = "sample1.json"
    f2 = "sample5.json"

    wl1 = getWordList(f1)
    wl2 = getWordList(f2)

    getSpeechChangeData(wl1, wl2)


#curl -X POST -u "a2c092e7-c9d5-4dd3-9e3e-7d9d810a250e":"xfBGkNCkAA8h" --header "Content-Type: audio/wav" --data-binary "@audio5.wav" "https://stream.watsonplatform.net/speech-to-text/api/v1/recognize?timestamps=true" > sample5.json
