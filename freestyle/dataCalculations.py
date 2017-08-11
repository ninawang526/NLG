############################################################################
# This file contains the code for the 1st half of the data processing:
# identifying especially high/low blocks in a user's speech
############################################################################

from database_init import db
import json
import numpy as np
import matplotlib.pyplot as plt
from cleanResults import clean
from timeContext import putInTimeContext


# Takes feedback version, list of data, boundaries for what are considered high and
# low values, and boundary for standard deviation to highlight significant changes.
# Returns average value, stddev, overall trend (high/low/normal), and location summary
# of where special areas are in the speech.
def getData(version, data_list, high, low, std):
    if version == "none" or data_list == 0:
        return {}

    global HIGH, LOW, STD
    HIGH = high
    LOW = low
    STD = std

    results = {}
    results["average"], results["std"] = getAvgAndStd(data_list)
    results["trend"] = getTrend(results["average"])

    if version == "lite":
        results["location_summary"] = {"split":"everywhere"}
    else:
        results["location_summary"] = getLocationSummary(data_list, results["trend"])

    graph(data_list, results["average"], results["location_summary"]["split"])
    return results


# Calculates average (scaled by duration), and standard deviation
def getAvgAndStd(data_list):
    data_sum = 0
    time_sum = 0
    for item in data_list:
        duration = item["end"] - item["start"]
        time_sum = time_sum + duration
        data_sum = data_sum + (item["value"] * duration)

    try:
        avg = (data_sum / float(time_sum))
    except ZeroDivisionError:
        avg = 0

    std = (np.std(np.array([x["value"] for x in data_list])))

    return avg, std


# Tells if the overall speech is high, low, or normal
def getTrend(average):
    if average > HIGH:
        return "high"
    elif average < LOW:
        return "low"
    else:
        return "normal"


# Identifies high/low blocks and puts them into time context (start, middle, end)
def getLocationSummary(data_list, trend):
    groups = identifySpecialBlocks(data_list)

    total_duration = data_list[len(data_list)-1]["end"]

    if isEverywhere(groups, total_duration, trend):
        location_summary = {"split":"everywhere"}

    else:
        # clean results so that they fit into known patterns
        location_summary = putInTimeContext(groups, trend)
        if location_summary["split"] == "thirds":
            location_summary = clean(trend, location_summary["summary"])

    return location_summary


# Identifies high/low blocks by splitting speech into even-sized chunks and
# seeing if any are above/below avg
def identifySpecialBlocks(data_list):
    trends = splitIntoBlocks(data_list)

    #JUST GRAPHING.
    graphTrends(trends, data_list)

    # group adjacent trends together
    if len(trends) == 0:
        return trends

    trend = trends[0]["trend"]
    start = trends[0]["start"]
    value_sum = 0
    total_time = 0
    groups = []
    for i in range(len(trends)):
        if trends[i]["trend"] == trend:
            end = trends[i]["end"]
            value_sum = value_sum + (trends[i]["value"] * (end-start))
            total_time = total_time + (end-start)
        else:
            try:
                value = value_sum / float(total_time)
            except ZeroDivisionError:
                value = 0

            groups.append({"start":start, "end":end, "trend":trend, "value":value})
            plt.plot([start, end], [value, value], lw=2,color="black", solid_capstyle="butt")

            trend = trends[i]["trend"]
            start = trends[i]["start"]
            end = trends[i]["end"]
            value_sum = float(trends[i]["value"]) * (end-start)
            total_time = end - start

        if i == len(trends)-1:
            try:
                value = value_sum / float(total_time)
            except ZeroDivisionError:
                value = 0

            groups.append({"start":start, "end":end, "trend":trend, "value":value})
            plt.plot([start, end], [value, value], lw=2,color="black", solid_capstyle="butt")

    return groups


# Splits up data_list into even-sized blocks of time
def splitIntoBlocks(data_list):
    # determine what size blocks to split into
    duration = data_list[len(data_list)-1]["end"]
    if duration < 80:
        time_interval = duration / 2.5
    else:
        time_interval = duration / 5.

    objects_by_block = []
    block = []
    seconds = 0
    for item in data_list:
        duration = item["end"] - item["start"]
        if (seconds+duration) >= time_interval:
            # decides whether to attach duration to this block or the next one.
            if abs(time_interval-seconds) < abs(time_interval-(seconds+duration)) and seconds > 0:
                objects_by_block.append(summarizeBlock(block))
                block = []
                block.append(item)
                seconds = duration
            else:
                block.append(item)
                objects_by_block.append(summarizeBlock(block))
                block = []
                seconds = 0
        else:
            block.append(item)
            seconds = seconds + duration

    if len(block) > 0:
        objects_by_block.append(summarizeBlock(block))

    return objects_by_block


# given a list of values, summarize them into one entry.
def summarizeBlock(block):
    assert (len(block)>0)

    object_sum = 0
    total_time = 0
    start = block[0]["start"]
    for i in range(len(block)):
        duration = block[i]["end"] - block[i]["start"]
        total_time = total_time + duration
        object_sum = object_sum + (block[i]["value"] * duration)
        if i == (len(block)-1):
            end = block[i]["end"]
            plt.axvline(end, color='black', linewidth=2)

    try:
        avg = object_sum / float(total_time)
    except ZeroDivisionError:
        avg = 0

    return {"trend":getTrend(avg), "value": avg, "start":start, "end":end}



# checks if the special blocks are everywhere and not in specific places
def isEverywhere(groups, total_duration, trend):
    trend_duration = 0
    for item in groups:
        t = item["trend"]
        if t == trend:
            trend_duration = trend_duration + (item["end"] - item["start"])

    # criteria one: if special groups take up > 85% of total duration
    if trend_duration > (.85 * (total_duration)):
        return True

    # criteria two: if the stddev of groups is low
    std_of_groups = np.std(np.array([x["value"] for x in groups]))
    if std_of_groups < STD:
        return True

    return False


def graph(wpms_list, average, split):
    for item in wpms_list:
        end = item["end"]
        start = item["start"]
        value = item["value"]

        plt.plot([start, end], [value, value], lw=10, color="orange", solid_capstyle="butt")

    #plt.axhline(HIGH, color='red', linestyle="dashed", linewidth=2)
    plt.axhline(average, color='red', linewidth=2)

    duration = wpms_list[len(wpms_list)-1]["end"]
    if split == "thirds":
        interval = duration / 3.
        time_ranges = [0, interval, (2*interval), (3*interval)]
    elif split == "halves":
        interval = duration / 2.
        time_ranges = [0, interval, (2*interval)]
    else:
        time_ranges = []


    for item in time_ranges:
        plt.axvline(item, color='g', linestyle="dashed",linewidth=2)

    plt.show()


def graphTrends(trends, data_list):
    for group in trends:
        avg = group["value"]
        start = group["start"]
        end = group["end"]
        vals = [x["value"] for x in data_list]
        overall_avg = sum(vals) / float(len(vals))
        if avg > HIGH and (overall_avg > HIGH or overall_avg > LOW): # CHANGE TO 130
            plt.axvspan(start, end, alpha=0.2, color='red')
        elif avg < LOW and (overall_avg < LOW or overall_avg < HIGH):
            plt.axvspan(start, end, alpha=0.2, color='yellow')
        plt.plot([start, end], [avg, avg], lw=2,color="black",linestyle="dotted", solid_capstyle="butt")
