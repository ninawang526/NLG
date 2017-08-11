############################################################################
# This file contains the code for the 2nd half of the data processing: taking
# especially high/low blocks in a user's speech, and putting them in
# time context: beginning, middle, end / first half, second half
############################################################################

import numpy as np

# Determines whether more meaningful to split speech by thirds or halves
def putInTimeContext(groups, category, duration):
    if category == "normal":
        results = {"split":"everywhere"}
        return results

    speech_by_thirds = locateInTime(groups, category, "thirds", duration)
    thirds_std = speech_by_thirds["std"]

    speech_by_halves = locateInTime(groups, category, "halves", duration)
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
        trend = summary["0"]["trend"]
        for i in summary:
            if summary[str(i)]["trend"] != trend:
                results["split"] = split
                results["summary"] = summary
            else:
                results["split"] = "everywhere"
    else:
        results["split"] = split
        results["summary"] = summary

    return results


# Given a category to look for (high, low, or normal), scan the speech for that
# category.
def locateInTime(groups, category, split, duration):
    if category == "normal":
        return []
    else:
        summary = flagCategory(groups, category, split, duration)

    return summary


# Given a speech divided in time blocks, sees if any part is particularly high/low. Returns
# standard deviation (measurement of how well the split divides up the data) and
# where high/low blocks are.
def flagCategory(groups, category, split, duration):
    time_ranges = getTimeRanges(duration, split)

    percentages = []
    leftover_time = 0
    leftover_index = None
    group_index = 0

    # traverse blocks of time
    for i in range(len(time_ranges)-1):
        rangeStart = time_ranges[i]
        rangeEnd = time_ranges[i+1]
        rangeDuration = rangeEnd - rangeStart
        indices = [] # list of indices seen in this time range.

        if leftover_time < rangeDuration:
            groupDuration = leftover_time
            leftover_time = 0
            if leftover_index is not None:
                indices.append({"index":leftover_index,"duration":groupDuration})
        else:
            percentages.append({"trend":category,"percentage":1., "index":leftover_index})
            leftover_time = leftover_time - rangeDuration
            continue

        # traverse special groups
        while group_index < len(groups):
            groupStart = groups[group_index]["start"]
            groupEnd = groups[group_index]["end"]
            duration = groupEnd - groupStart
            trend = groups[group_index]["trend"]

            # if out of time range entirely.
            if groupStart > rangeEnd:
                break

            # if goes beyond time boundary
            elif groupEnd > rangeEnd:
                if (trend == category):
                    leftover_time = groupEnd - rangeEnd
                    leftover_index = group_index
                    groupDuration = groupDuration + (rangeEnd - groupStart)
                    indices.append({"index":group_index,"duration":(rangeEnd - groupStart)})
                else:
                    leftover_time = 0
                    leftover_index = 0
                group_index = group_index + 1
                break
            else:
                if (trend == category):
                    groupDuration = groupDuration + duration
                    indices.append({"index":group_index,"duration":duration})
                leftover_time = 0
                leftover_index = 0

            group_index = group_index + 1

        try:
            percentage = groupDuration / float(rangeDuration)
        except ZeroDivisionError as e:
            percentage = 0

        sig_index = findMostSigIndex(indices)
        percentages.append({"trend":category,"percentage":percentage, "index":sig_index})

    times_summary = {}
    for i in range(len(percentages)):
        if percentages[i]["percentage"] > .4:
            times_summary[str(i)] = {"trend":percentages[i]["trend"], "percentage":percentages[i]["percentage"],
                                    "index":percentages[i]["index"]}

    summary = {"std": np.std(np.array([x["percentage"] for x in percentages])), "times_summary": times_summary}
    return summary


def findMostSigIndex(indices):
    if len(indices) == 0:
        return None

    maxDuration = indices[0]["duration"]
    maxIndex = indices[0]["index"]
    for item in indices:
        if item["duration"] > maxDuration:
            maxDuration = item["duration"]
            maxIndex = item["index"]
    return maxIndex


# Returns time intervals based on if the speech is split into thirds or halves
def getTimeRanges(duration, split):
    if split == "thirds":
        interval = duration / 3.
        time_ranges = [0, interval, (2*interval), (3*interval)]
    else:
        interval = duration / 2.
        time_ranges = [0, interval, (2*interval)]

    return time_ranges


# make data fit certain patterns to make for easier lexicalization:
def clean(location_summary):
    cleaned = {}

    match_index = findTwoThirdsMatch(location_summary)
    if (match_index is not None):
        # first, switch to "halves" if it makes more sense.
        middle = location_summary["1"]
        match = location_summary[match_index]
        if match["percentage"] > .7: #change to .5?
            cleaned["split"] = "halves"
            if match_index == "2":
                match_index = "1"
            other_index = 1-int(match_index)
            try:
                other = location_summary[other_index]
                cleaned["summary"] = {match_index:match, other_index:other}
            except KeyError as e:
                cleaned["summary"] = {match_index:match}

            return cleaned

        # otherwise, keep the more significant one and discard the other.
        else:
            cleaned["split"] = "thirds"
            middle_score = middle["percentage"]
            match_score = match["percentage"]
            other_index = 2-int(match_index)

            cleaned["summary"] = {}
            try:
                other = location_summary[other_index]
                cleaned["summary"][other_index] = other
            except KeyError as e:
                pass

            if middle_score > match_score:
                cleaned["summary"]["1"] = middle
            else:
                cleaned["summary"][match_index] = match

            return cleaned

    # if no changes
    cleaned = {"split":"thirds", "summary":location_summary}
    return cleaned


# look for if 2 adjacent timeblocks share the same index
def findTwoThirdsMatch(summary):
    try:
        middle = summary["1"]
    except KeyError as e:
        return None

    try:
        start = summary["0"]
    except KeyError as e:
        start = {"trend":None}

    try:
        end = summary["2"]
    except KeyError as e:
        end = {"trend":None}

    if start["trend"] == middle["trend"]:
        return "0"
    elif end["trend"] == middle["trend"]:
        return "2"
    else:
        return None
