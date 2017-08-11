############################################################################
# This file sets up the structure and order of the document. A document is a tree
# consisting of a bunch of NLGLeafs, which contain info about the topic,
# ordering, transitions, etc. The leaves are NLGMessages, which are the actual
# messages, and they contain info needed to turn the message into a sentence.
############################################################################

from NLGMessage import *
from NLGLeaf import *

# builds entire document. document consists of: pace paragraph, energy paragraph,
# and closing paragraph.
def getDocumentPlan(data, version):
    document = NLGLeaf("document", "root", "sequence")

    # energy paragraph
    energy_paragraph = NLGLeaf("energy", "root", "paragraph")

    if version == "none":
        NoneMsg = NLGMessage('NoneMsg', 'energy')
        energy_paragraph.addChild(NLGLeaf('energy', "nucleus", "message", NoneMsg))
        document.addChild(energy_paragraph)
        return document

    energy_data = data["energy-data"]
    if energy_data["trend"] == "normal":
        energy_paragraph.addChild(getNormalMessages(energy_data, "energy"))
    else:
        energy_paragraph.addChild(getTrendMessages(energy_data, "energy"))
    document.addChild(energy_paragraph)

    # pace paragraph
    pace_paragraph = NLGLeaf('pace', "root", "paragraph")
    pace_data = data["pace-data"]
    if pace_data["trend"] == "normal":
        pace_paragraph.addChild(getNormalMessages(pace_data, 'pace'))
    else:
        pace_paragraph.addChild(getTrendMessages(pace_data, 'pace'))
    document.addChild(pace_paragraph)

    # closing paragraph
    closing_paragraph = NLGLeaf("pace", "root", "paragraph")
    closing_paragraph.addChild(getClosingMessages(data))
    document.addChild(closing_paragraph)

    if version == "lite":
        additional_paragraph = NLGLeaf("energy", "root", "paragraph")
        MoreMsg = NLGMessage('MoreMsg', "energy")
        additional_paragraph.addChild(NLGLeaf("energy", "nucleus", "message", MoreMsg))
        document.addChild(additional_paragraph)

    #document.printTree()
    return document


# consists of a description & a suggestion
def getTrendMessages(data, topic):
    root = NLGLeaf(topic, "root", "sequence")

    split = data["location_summary"]["split"]
    if split == "everywhere":
        desc = getEverywhereDesc(data, topic)
    else:
        desc = getTrendDesc(data, topic)

    schema_info = getSchemaInfo(data)
    sugg = getSuggestion(data, schema_info, topic)

    root.addChild(desc)
    root.addChild(sugg)

    return root


# get the opening description line
def getTrendDesc(data, topic):
    schema_info = getSchemaInfo(data)
    assert(len(schema_info) == 1)

    args = {"trend":data["trend"], "value":data["average"], "split":data["location_summary"]["split"]}
    AvgMsg = NLGMessage('AvgMsg', topic, args)
    # "ElaborationMsg = "especially...""
    ElaborationMsg = NLGMessage('ElaborationMsg', topic, schema_info[0])

    root = NLGLeaf(topic, "nucleus", "elaboration")
    root.addChild(NLGLeaf(topic, "nucleus", "message", AvgMsg))
    root.addChild(NLGLeaf(topic, "satellite", "message", ElaborationMsg))

    return root


# get the opening description line
def getEverywhereDesc(data, topic):
    args = {"trend":data["trend"], "value":data["average"], "split":data["location_summary"]["split"]}
    AvgMsg = NLGMessage('AvgMsg', topic, args)

    # "DescriptionMsg = "which is..."
    args = {"trend":data["trend"]}
    DescriptionMsg = NLGMessage('DescriptionMsg', topic, args)


    root = NLGLeaf(topic, "nucleus", "description")
    root.addChild(NLGLeaf(topic, "nucleus", "message", AvgMsg))
    root.addChild(NLGLeaf(topic, "satellite", "message", DescriptionMsg))

    return root


# returns schema (start-end, start, end, middle), value, and trend
def getSchemaInfo(data):
    split = data["location_summary"]["split"]

    if split == "everywhere":
        return [{"schema":"everywhere", "value":data["average"], "trend": data["trend"]}]

    locations = data["location_summary"]["summary"]
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
def getSuggestion(data, schema_info, topic):
    low_list = ["start", "start-end", "end"]
    half_list = ["first", "second"]

    if len(schema_info) == 1:
        # special case
        if topic == "pace" and ((data["trend"] == "low" and schema_info[0]["schema"] in low_list) or \
        (data["trend"] == "low" and schema_info[0]["schema"] in half_list)):
            msg1 = NLGMessage('SuggestionMsg', topic, schema_info[0])
            node1 = NLGLeaf(topic, "nucleus", "message", msg1)

            msg2 = NLGMessage('AdditionalMsg', topic, schema_info[0])
            node2 = NLGLeaf(topic, "satellite", "message", msg2)

            root = NLGLeaf(topic, "nucleus", "contrast")
            root.addChild(node1)
            root.addChild(node2)
        else:
            msg = NLGMessage('SuggestionMsg', topic, schema_info[0])
            root = NLGLeaf(topic, "nucleus", "message", msg)

    elif len(schema_info) == 2:
        if data["location_summary"]["split"] == "halves":
            msg = NLGMessage('BalanceMsg', topic)
            root = NLGLeaf(topic, "nucleus", "message", msg)

        else:
            msg1 = NLGMessage('SuggestionMsg', topic, schema_info[0])
            msg2 = NLGMessage('SuggestionMsg', topic, schema_info[1])

            if schema_info[1]["trend"] == "low" and schema_info[1]["schema"] in low_list:
                node1 = NLGLeaf(topic, "nucleus", "message", msg2)
                node2 = NLGLeaf(topic, "satellite", "message", msg1)
            else:
                node1 = NLGLeaf(topic, "nucleus", "message", msg1)
                node2 = NLGLeaf(topic, "satellite", "message", msg2)

            root = NLGLeaf(topic, "satellite", "contrast")
            root.addChild(node1)
            root.addChild(node2)

    else:
        raise Exception("unknown # of schemas: %d", len(schema_info))

    return root


def getNormalMessages(data, topic):
    split = data["location_summary"]["split"]
    schema_info = getSchemaInfo(data)

    if split == "everywhere":
        desc = getEverywhereDesc(data, topic)
    else:
        for item in schema_info:
            if item["schema"] == "middle" and len(schema_info) > 1:
                return getNormalMiddleMsg(data, schema_info, topic)

        desc = getNormalDesc(data, schema_info, topic)

    sugg = getSuggestion(data, schema_info, topic)

    root = NLGLeaf(topic, "root", "sequence")
    root.addChild(desc)
    root.addChild(sugg)

    return root


def getNormalDesc(data, schema_info, topic):
    low_list = ["start", "start-end", "end", "first", "second"]

    if len(schema_info) == 1:
        args = {"trend":data["trend"], "value":data["average"], "split":data["location_summary"]["split"]}
        msg1 = NLGMessage('AvgMsg', topic, args)
        msg2 = NLGMessage('ElaborationMsg', topic, schema_info[0])

        if topic == "pace" and schema_info[0]["trend"] == "low" and schema_info[0]["schema"] in low_list:
            root = NLGLeaf(topic, "nucleus", "addition")
        else:
            root = NLGLeaf(topic, "nucleus", "contrast")

    elif len(schema_info) == 2:
        msg1 = NLGMessage('ElaborationMsg', topic, schema_info[0])
        msg2 = NLGMessage('ElaborationMsg', topic, schema_info[1])
        root = NLGLeaf(topic, "nucleus", "contrast")

    else:
        raise Exception("unrecognized schema length: %d", len(schema_info))


    root.addChild(NLGLeaf(topic, "nucleus", "message", msg1))
    root.addChild(NLGLeaf(topic, "satellite", "message", msg2))

    return root


# if there's a middle schema + other schema, talk about other first, then middle
def getNormalMiddleMsg(data, schema_info, topic):
    root = NLGLeaf(topic, "root", "sequence")
    assert(len(schema_info)==2)

    for item in schema_info:
        if item["schema"] == "middle":
            middle_schema = item
        else:
            other_schema = item

    assert(middle_schema is not None)

    root_other = NLGLeaf(topic, "nucleus", "sequence")
    msg1 = NLGMessage('ElaborationMsg', topic, other_schema)
    msg2 = NLGMessage('SuggestionMsg', topic, other_schema)
    root_other.addChild(NLGLeaf(topic, "nucleus", "message", msg1))
    root_other.addChild(NLGLeaf(topic, "satellite", "message", msg2))

    msg1 = NLGMessage('MiddleSuggestionMsg', topic, middle_schema)
    root_middle = NLGLeaf(topic, "nucleus", "message", msg1)

    root = NLGLeaf(topic, "nucleus", "sequence")
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
