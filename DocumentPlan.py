from NLGMessage import *
from NLGLeaf import *


# document consists of: pace paragraph, energy paragraph, and closing paragraph.
def getDocumentPlan(data):
    pace_data = data["pace-data"]

    pace_paragraph = NLGLeaf("paragraph", "root", "paragraph")
    if pace_data["trend"] == "normal":
        pace_paragraph.addChild(getNormalMessages(pace_data))
    else:
        pace_paragraph.addChild(getTrendMessages(pace_data))

    closing_paragraph = NLGLeaf("paragraph", "root", "paragraph")
    closing_paragraph.addChild(getClosingMessages(data))

    document = NLGLeaf("document", "root", "sequence")
    document.addChild(pace_paragraph)
    document.addChild(closing_paragraph)
    document.printTree()
    return document


# consists of a description & a suggestion
def getTrendMessages(data):
    root = NLGLeaf("pace", "root", "sequence")

    split = data["location_summary"]["split"]
    if split == "everywhere":
        desc = getEverywhereDesc(data)
    else:
        desc = getTrendDesc(data)

    schema_info = getSchemaInfo(data)
    sugg = getSuggestion(data, schema_info)

    root.addChild(desc)
    root.addChild(sugg)

    return root


# get the opening description line
def getTrendDesc(data):
    schema_info = getSchemaInfo(data)
    assert(len(schema_info) == 1)

    args = {"trend":data["trend"], "value":data["average"], "split":data["location_summary"]["split"]}
    AvgMsg = NLGMessage('AvgMsg', 'pace', args)
    # "ElaborationMsg = "especially...""
    ElaborationMsg = NLGMessage('ElaborationMsg', 'pace', schema_info[0])

    root = NLGLeaf("pace", "nucleus", "elaboration")
    root.addChild(NLGLeaf('pace', "nucleus", "message", AvgMsg))
    root.addChild(NLGLeaf('pace', "satellite", "message", ElaborationMsg))

    return root


# get the opening description line
def getEverywhereDesc(data):
    args = {"trend":data["trend"], "value":data["average"], "split":data["location_summary"]["split"]}
    AvgMsg = NLGMessage('AvgMsg', 'pace', args)

    args = {"trend":data["trend"]}
    # "DescriptionMsg = "which is...""
    DescriptionMsg = NLGMessage('DescriptionMsg', 'pace', args)

    root = NLGLeaf("pace", "nucleus", "description")
    root.addChild(NLGLeaf('pace', "nucleus", "message", AvgMsg))
    root.addChild(NLGLeaf('pace', "satellite", "message", DescriptionMsg))

    return root


# returns schema (start-end, start, end, middle), value, and trend
def getSchemaInfo(data):
    split = data["location_summary"]["split"]

    try:
        locations = data["location_summary"]["summary"]
    except KeyError as e:
        return [{"schema":"everywhere", "value":data["average"], "trend": data["trend"]}]

    # identify schema (start-end, start, end, middle)
    if split == "thirds":
        r = 3
    else:
        r = 2

    schemas = []
    for i in range(r):
        try:
            schema = findSchema(split, i)
            schemas.append({"schema":schema, "value":locations[str(i)]["value"], "trend": locations[str(i)]["trend"]})
        except KeyError as e:
            continue

    # see if there's a start-end schema
    if split == "thirds":
        start = None
        end = None

        for item in schemas:
            if item["schema"] == "start":
                start = item
            if item["schema"] == "end":
                end = item

        if start is not None and end is not None:
            if start["trend"] == end["trend"]:
                schemas.remove(end)
                start["schema"] = "start-end"

                if start["trend"] == "low":
                    start["value"] = min(start["value"], end["value"])
                else:
                    start["value"] = max(start["value"], end["value"])

    return schemas


# matches index to corresponding schema (start-end, start, end, middle)
def findSchema(split, index):
    index = int(index)
    schema = ""

    halves = ["first","second"]
    thirds = ["start","middle","end"]

    if split == "halves":
        return halves[index]
    elif split == "thirds":
        return thirds[index]
    else:
        raise Exception("unrecognized split: %s", split)


# get suggestion msg based on schema
def getSuggestion(data, schema_info):
    low_list = ["start", "start-end", "end"]
    half_list = ["first", "second"]

    if len(schema_info) == 1:
        # special case
        if (data["trend"] == "low" and schema_info[0]["schema"] in low_list) or \
        (data["trend"] != "normal" and schema_info[0]["schema"] in half_list):
            msg1 = NLGMessage('SuggestionMsg', 'pace', schema_info[0])
            node1 = NLGLeaf('pace', "nucleus", "message", msg1)

            msg2 = NLGMessage('AdditionalMsg', 'pace', schema_info[0])
            node2 = NLGLeaf('pace', "satellite", "message", msg2)

            root = NLGLeaf("pace", "nucleus", "contrast")
            root.addChild(node1)
            root.addChild(node2)
        else:
            msg = NLGMessage('SuggestionMsg', 'pace', schema_info[0])
            root = NLGLeaf('pace', "nucleus", "message", msg)

    elif len(schema_info) == 2:
        if data["location_summary"]["split"] == "halves":
            msg = NLGMessage('BalanceMsg', 'pace')
            root = NLGLeaf('pace', "nucleus", "message", msg)

        else:
            msg1 = NLGMessage('SuggestionMsg', 'pace', schema_info[0])
            msg2 = NLGMessage('SuggestionMsg', 'pace', schema_info[1])

            if schema_info[1]["trend"] == "low" and schema_info[1]["schema"] in low_list:
                node1 = NLGLeaf('pace', "nucleus", "message", msg2)
                node2 = NLGLeaf('pace', "satellite", "message", msg1)
            else:
                node1 = NLGLeaf('pace', "nucleus", "message", msg1)
                node2 = NLGLeaf('pace', "satellite", "message", msg2)

            root = NLGLeaf("pace", "satellite", "contrast")
            root.addChild(node1)
            root.addChild(node2)

    else:
        raise Exception("unknown # of schemas: %d", len(schema_info))

    return root


def getNormalMessages(data):
    split = data["location_summary"]["split"]
    schema_info = getSchemaInfo(data)

    if split == "everywhere":
        desc = getEverywhereDesc(data)
    else:
        for item in schema_info:
            if item["schema"] == "middle" and len(schema_info) > 1:
                return getNormalMiddleMsg(data, schema_info)

        desc = getNormalDesc(data, schema_info)

    sugg = getSuggestion(data, schema_info)

    root = NLGLeaf("pace", "root", "sequence")
    root.addChild(desc)
    root.addChild(sugg)

    return root


def getNormalDesc(data, schema_info):
    low_list = ["start", "start-end", "end", "first", "second"]

    if len(schema_info) == 1:
        args = {"trend":data["trend"], "value":data["average"], "split":data["location_summary"]["split"]}
        msg1 = NLGMessage('AvgMsg', 'pace', args)
        msg2 = NLGMessage('ElaborationMsg', 'pace', schema_info[0])

        if schema_info[0]["trend"] == "low" and schema_info[0]["schema"] in low_list:
            root = NLGLeaf("pace", "nucleus", "addition")
        else:
            root = NLGLeaf("pace", "nucleus", "contrast")

    elif len(schema_info) == 2:
        msg1 = NLGMessage('ElaborationMsg', 'pace', schema_info[0])
        msg2 = NLGMessage('ElaborationMsg', 'pace', schema_info[1])
        root = NLGLeaf("pace", "nucleus", "contrast")

    else:
        raise Exception("unrecognized schema length: %d", len(schema_info))


    root.addChild(NLGLeaf('pace', "nucleus", "message", msg1))
    root.addChild(NLGLeaf('pace', "satellite", "message", msg2))

    return root


# if there's a middle schema + other schema, talk about other first, then middle
def getNormalMiddleMsg(data, schema_info):
    root = NLGLeaf("pace", "root", "sequence")
    assert(len(schema_info)==2)

    for item in schema_info:
        if item["schema"] == "middle":
            middle_schema = item
        else:
            other_schema = item

    assert(middle_schema is not None)

    root_other = NLGLeaf("pace", "nucleus", "sequence")
    msg1 = NLGMessage('ElaborationMsg', 'pace', other_schema)
    msg2 = NLGMessage('SuggestionMsg', 'pace', other_schema)
    root_other.addChild(NLGLeaf('pace', "nucleus", "message", msg1))
    root_other.addChild(NLGLeaf('pace', "satellite", "message", msg2))

    msg1 = NLGMessage('MiddleSuggestionMsg', 'pace', middle_schema)
    root_middle = NLGLeaf('pace', "nucleus", "message", msg1)

    root = NLGLeaf("pace", "nucleus", "sequence")
    root.addChild(root_other)
    root.addChild(root_middle)

    return root


def getClosingMessages(data):

    root = NLGLeaf("overall", "root", "sequence")

    args = {"pace-trend":data["pace-data"]["trend"], "pace-value":data["pace-data"]["average"]}
    overall_msg = NLGMessage('OverallMsg', 'overall', args)
    root.addChild(NLGLeaf('overall', "nucleus", "message", overall_msg))

    # hard coded rn
    args = {"area":"pace", "value":data["pace-data"]["average"]}
    next_recording_msg = NLGMessage('NextRecordingMsg', 'overall', args)
    root.addChild(NLGLeaf('overall', "satellite", "message", next_recording_msg))

    return root









#
