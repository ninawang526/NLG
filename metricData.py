from database_init import db
import json
import numpy as np
import matplotlib.pyplot as plt
from cleanResults import clean

HIGH_WPM = 160
LOW_WPM = 140


def getPaceData(session_id):
    wpms_list = getWpmsFromDatabase(session_id)

    results = {}
    results["average"] = getAvgAndStd(wpms_list, "avg")
    results["std"] = getAvgAndStd(wpms_list, "std")
    results["trend"] = getTrend(results["average"])
    results["location_summary"] = getLocationSummary(wpms_list, results["trend"])

    graph(wpms_list, results["average"], results["location_summary"]["split"])
    flushResults(results)

    return results


# Gets WPM results from database and throws them into a list
def getWpmsFromDatabase(session_id):
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


def flushResults(results):
    f = open("nlg2_data", "w")
    f.write(json.dumps(results, indent=2))
    f.flush()
    f.close()


# Calculates average WPM (scaled by duration of sentence), and standard deviation
def getAvgAndStd(wpms_list, choice):
    wpm_sum = 0
    time_sum = 0
    for item in wpms_list:
        duration = item["end"] - item["start"]
        time_sum = time_sum + duration
        wpm_sum = wpm_sum + (item["value"] * duration)

    if choice == "avg":
        return (wpm_sum / time_sum)
    elif choice == "std":
        return (np.std(np.array([x["value"] for x in wpms_list])))


# Tells if the overall speech is high WPM, low WPM, or normal WPM
def getTrend(average):
    if average > HIGH_WPM:
        return "high"
    elif average < LOW_WPM:
        return "low"
    else:
        return "normal"


# Identifies high/low blocks and puts them into time context (start, middle, end)
def getLocationSummary(wpms_list, trend):
    groups = identifySpecialBlocks(wpms_list)

    std_of_groups = np.std(np.array([x["value"] for x in groups]))

    if std_of_groups < 5:
        location_summary = {"split":"everywhere"}
    else:
        location_summary = putInTimeContext(groups, trend)
        # clean results so that they fit into known patterns
        if location_summary["split"] == "thirds":
            location_summary = clean(trend, location_summary["summary"])

    return location_summary


# Identifies high/low blocks by splitting speech into even-sized chunks and
# seeing if above/below avg
def identifySpecialBlocks(objects_list):
    objects_by_block = splitIntoBlocks(objects_list)

    # examine each individual block
    trends = []
    for group in objects_by_block:
        object_sum = 0
        total_time = 0
        start = group[0]["start"]
        for i in range(len(group)):
            duration = group[i]["end"] - group[i]["start"]
            total_time = total_time + duration
            object_sum = object_sum + (group[i]["value"] * duration)
            if i == (len(group)-1):
                end = group[i]["end"]
                plt.axvline(end, color='black', linewidth=2)

        avg = object_sum / total_time
        trends.append({"trend":getTrend(avg), "value": avg, "start":start, "end":end})

        #JUST GRAPHING.
        vals = [x["value"] for x in objects_list]
        overall_avg = sum(vals) / float(len(vals))
        if avg > HIGH_WPM and (overall_avg > HIGH_WPM or overall_avg > LOW_WPM): # CHANGE TO 130
            plt.axvspan(start, end, alpha=0.2, color='red')
        elif avg < LOW_WPM and (overall_avg < LOW_WPM or overall_avg < HIGH_WPM):
            plt.axvspan(start, end, alpha=0.2, color='yellow')

    # group like blocks together
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
            value = value_sum / total_time
            groups.append({"start":start, "end":end, "trend":trend, "value":value})
            plt.plot([start, end], [value, value], lw=2,color="black", solid_capstyle="butt")

            trend = trends[i]["trend"]
            start = trends[i]["start"]
            end = trends[i]["end"]
            value_sum = (trends[i]["value"] * (end-start))
            total_time = end - start

        if i == len(trends)-1:
            value = value_sum / total_time
            groups.append({"start":start, "end":end, "trend":trend, "value":value})
            plt.plot([start, end], [value, value], lw=2,color="black", solid_capstyle="butt")

    return groups


# Splits up wpm_list into even-sized blocks of time
def splitIntoBlocks(object_list):
    # determine what size blocks to split into
    duration = object_list[len(object_list)-1]["end"]
    if duration < 80:
        time_interval = duration / 2.5
    else:
        time_interval = duration / 5.

    objects_by_block = []
    block = []
    seconds = 0
    for item in object_list:
        duration = item["end"] - item["start"]
        if (seconds+duration) >= time_interval:
            # decides whether to attach duration to this block or the next one.
            if abs(time_interval-seconds) < abs(time_interval-(seconds+duration)) and seconds > 0:
                objects_by_block.append(block)
                block = []
                block.append(item)
                seconds = duration
            else:
                block.append(item)
                objects_by_block.append(block)
                block = []
                seconds = 0
        else:
            block.append(item)
            seconds = seconds + duration

    # handles yet-unincluded blocks.
    if len(block) > 0:
        if len(block) == 1:
            try:
                objects_by_block[len(objects_by_block)-1].extend(block)
            except IndexError:
                objects_by_block.append(block)
        else:
            objects_by_block.append(block)

    return objects_by_block


# Determines whether more meaningful to split speech by thirds or halves
def putInTimeContext(groups, category):
    duration = groups[len(groups)-1]["end"]

    speech_by_thirds = locateInTime(groups, category, "thirds")
    thirds_std = speech_by_thirds["std"]

    speech_by_halves = locateInTime(groups, category, "halves")
    halves_std = speech_by_halves["std"]

    if halves_std > thirds_std:
        split = "halves"
        summary = speech_by_halves["times_summary"]
    else:
        split = "thirds"
        summary = speech_by_thirds["times_summary"]

    results = {}
    if len(summary) == 0:
        results["split"] = "everywhere"
    elif (split == "halves" and len(summary) == 2) or (split == "thirds" and len(summary) == 3):
        results["split"] = "everywhere"
        # for normal, must check if every trend is the same.
        if category == "normal":
            trend = summary["0"]["trend"]
            for i in summary:
                if summary[str(i)]["trend"] != trend:
                    results["split"] = split
                    results["summary"] = summary
    else:
        results["split"] = split
        results["summary"] = summary

    return results


# Given a category to look for (high, low, or normal), scan the speech for that
# category.
def locateInTime(groups, category, split):
    if category == "low" or category == "high":
        summary = flagCategory(groups, category, split)

    elif category == "normal":
        summary_high = flagCategory(groups, "high", split)
        summary_low = flagCategory(groups, "low", split)

        std = (summary_high["std"] + summary_low["std"]) / 2.

        summary = {"std":std, "times_summary":{}}

        if split == "halves":
            r = 2
        else:
            r = 3

        for i in range(r):
            high_percentage = None
            low_percentage = None
            high_val = None
            low_val = None
            try:
                high_percentage = summary_high["times_summary"][str(i)]["percentage"]
                high_val = summary_high["times_summary"][str(i)]["value"]
            except KeyError as e:
                pass
            try:
                low_percentage = summary_low["times_summary"][str(i)]["percentage"]
                low_val = summary_low["times_summary"][str(i)]["value"]
            except KeyError as e:
                pass

            if high_percentage is None and low_percentage is not None:
                summary["times_summary"][str(i)] = {"trend":"low", "percentage":low_percentage, "value":low_val}
            elif low_percentage is None and high_percentage is not None:
                summary["times_summary"][str(i)] = {"trend":"high", "percentage":high_percentage, "value":high_val}
            elif high_percentage is not None and low is not None:
                if low_percentage > high_percentage:
                    summary["times_summary"][str(i)] = {"trend":"low", "percentage":low_percentage, "value":low_val}
                else:
                    summary["times_summary"][str(i)] = {"trend":"high", "percentage":high_percentage, "value":high_val}

    else:
        raise Exception("unrecognized category: %s" %(category))

    return summary


# Given a speech divided in time blocks, sees if any part is particularly high/low. Returns
# standard deviation (measurement of how well the split divides up the data) and
# where high/low blocks are.
def flagCategory(groups, category, split):
    duration = groups[len(groups)-1]["end"]
    time_ranges = getTimeRanges(duration, split)

    percentages = []
    groups_index = 0
    leftover_time = 0
    leftover_value = 0

    for i in range(len(time_ranges)-1):
        rangeStart = time_ranges[i]
        rangeEnd = time_ranges[i+1]
        rangeDuration = rangeEnd - rangeStart

        if leftover_time < rangeDuration:
            groupDuration = leftover_time
            groupSum = (leftover_value * leftover_time)
        else:
            percentages.append({"trend":category,"percentage":1., "value": leftover_value})
            leftover_time = leftover_time - rangeDuration
            continue

        while groups_index < len(groups):
            groupStart = groups[groups_index]["start"]
            groupEnd = groups[groups_index]["end"]
            duration = groupEnd - groupStart
            trend = groups[groups_index]["trend"]
            value = groups[groups_index]["value"]

            # if goes beyond time boundary
            if groupEnd > rangeEnd:
                if (trend == category):
                    leftover_time = groupEnd - rangeEnd
                    leftover_value = value
                    groupDuration = groupDuration + (rangeEnd - groupStart)
                    groupSum = groupSum + (value * (rangeEnd - groupStart))
                    #print "value", value
                    #print "groupSum = %f + (%f * %f)" %(groupSum, value, (rangeEnd - groupStart))
                else:
                    leftover_time = 0
                    leftover_value = 0
                groups_index = groups_index + 1
                break
            else:
                if (trend == category):
                    groupDuration = groupDuration + duration
                    groupSum = groupSum + (value * duration)
                    #print "groupSum = %f + (%f * %f)" %(groupSum, value, duration)
                leftover_time = 0
                leftover_value = 0

            groups_index = groups_index + 1

        try:
            group_value = groupSum / float(groupDuration)
        except ZeroDivisionError as e:
            group_value = 0
        try:
            percentage = groupDuration / float(rangeDuration)
        except ZeroDivisionError as e:
            percentage = 0

        percentages.append({"trend":category,"percentage":percentage, "value":group_value})

    times_summary = {}
    for i in range(len(percentages)):
        if percentages[i]["percentage"] > .4:
            times_summary[str(i)] = {"trend":percentages[i]["trend"], "percentage":percentages[i]["percentage"], "value":percentages[i]["value"]}

    summary = {"std": np.std(np.array([x["percentage"] for x in percentages])), "times_summary": times_summary}
    return summary


# Returns time intervals based on if the speech is split into thirds or halves
def getTimeRanges(duration, split):
    if split == "thirds":
        interval = duration / 3.
        time_ranges = [0, interval, (2*interval), (3*interval)]
    elif split == "halves":
        interval = duration / 2.
        time_ranges = [0, interval, (2*interval)]
    else:
        raise Exception("Speech must be broken in halves or thirds.")

    return time_ranges


def graph(wpms_list, average, split):
    for item in wpms_list:
        end = item["end"]
        start = item["start"]
        value = item["value"]

        plt.plot([start, end], [value, value], lw=10, color="orange", solid_capstyle="butt")

    #plt.axhline(HIGH_WPM, color='red', linestyle="dashed", linewidth=2)
    plt.axhline(average, color='red', linewidth=2)

    duration = wpms_list[len(wpms_list)-1]["end"]
    if split == "thirds":
        interval = duration / 3.
        time_ranges = [0, interval, (2*interval), (3*interval)]
    elif split == "halves":
        interval = duration / 2.
        time_ranges = [0, interval, (2*interval)]

    for item in time_ranges:
        plt.axvline(item, color='g', linestyle="dashed",linewidth=2)

    plt.show()
