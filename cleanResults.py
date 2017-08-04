

# make data fit certain patterns to make for easier lexicalization:
def clean(trend, location_summary):
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

            print "CLEANED: turned into halves"
            return cleaned

        # otherwise, keep the more significant one and discard the other.
        else:
            cleaned["split"] = "thirds"
            middle_score = middle["percentage"] * middle["value"]
            match_score = match["percentage"] * match["value"]
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

    #print "HI:", start, middle, end
    if start["trend"] == middle["trend"]:
        return "0"
    elif end["trend"] == middle["trend"]:
        return "2"
    else:
        return None
