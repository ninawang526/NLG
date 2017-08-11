############################################################################
# This file contains the code for the 2nd half of the data processing: taking
# especially high/low blocks in a user's speech, and putting them in
# time context: beginning, middle, end / first half, second half
############################################################################

import numpy as np

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
    # more criteria for if groups are everywhere
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
# category. If speech is overall high/low wpm, just look for only higher/lower
# places. Else, look for both highs and lows.
def locateInTime(groups, category, split):
    if category == "low" or category == "high":
        summary = flagCategory(groups, category, split)

    elif category == "normal":
        summary_high = flagCategory(groups, "high", split)
        summary_low = flagCategory(groups, "low", split)

        std = max(summary_high["std"], summary_low["std"])

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
            elif high_percentage is not None and low_percentage is not None:
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
            leftover_time = 0
            leftover_value = 0
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
