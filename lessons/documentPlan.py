from NLGMessage import *
from NLGLeaf import *


# document consists of: pace paragraph, energy paragraph, and closing paragraph.
def getDocumentPlan(data, goal, version, topic="pace"):
    document = NLGLeaf("document", "root", "sequence")

    metric_paragraph = NLGLeaf("paragraph", "root", "paragraph")

    if version == "none":
        NoneMsg = NLGMessage('NoneMsg', topic)
        metric_paragraph.addChild(NLGLeaf(topic, "nucleus", "message", NoneMsg))
        document.addChild(metric_paragraph)
        return document

    if data["overall"] == "same":
        metric_paragraph.addChild(getSameMessages(topic))
    else:
        metric_paragraph.addChild(getTrendMessages(data, goal, topic))
    document.addChild(metric_paragraph)

    audience_paragraph = NLGLeaf("paragraph", "root", "paragraph")
    audience_paragraph.addChild(getAudienceMessages(data))
    document.addChild(audience_paragraph)

    if version == "lite":
        additional_paragraph = NLGLeaf("paragraph", "root", "paragraph")
        MoreMsg = NLGMessage('MoreMsg', topic)
        additional_paragraph.addChild(NLGLeaf(topic, "nucleus", "message", MoreMsg))
        document.addChild(additional_paragraph)

    document.printTree()
    return document


# Consists of a description & suggestion
def getSameMessages(topic):
    root = NLGLeaf(topic, "root", "sequence")

    desc = NLGMessage('SameMsg', topic)
    sugg = NLGMessage('SuggestionMsg', topic)

    root.addChild(NLGLeaf(topic, "nucleus", "message", desc))
    root.addChild(NLGLeaf(topic, "satellite", "message", sugg))

    return root


# consists of a description & a context msg or suggestion msg
def getTrendMessages(data, goal, topic):
    root = NLGLeaf(topic, "root", "sequence")

    split = data["location_summary"]["split"]
    if split == "everywhere":
        desc = getEverywhereDesc(data, topic)
    else:
        desc = getTrendDesc(data, topic)

    schema_info = getSchemaInfo(data)

    if data["overall"] != goal:
        sugg = NLGMessage('SuggestionMsg', topic)
        msg2 = NLGLeaf(topic, "nucleus", "message", sugg)
    else:
        msg2 = getContextMessage(data, schema_info, topic)

    root.addChild(desc)
    root.addChild(msg2)

    return root


# get the opening description line
def getEverywhereDesc(data, topic):
    args = {"trend":data["overall"], "val1":data["val1"], "val2":data["val2"], "split":"everywhere"}
    EverywhereMsg = NLGMessage('AvgMsg', topic, args)

    root = NLGLeaf(topic, "nucleus", "sequence")
    root.addChild(NLGLeaf(topic, "nucleus", "message", EverywhereMsg))

    return root


# get the opening description line
def getTrendDesc(data, topic):
    schema_info = getSchemaInfo(data)
    assert(len(schema_info) == 1)

    args = {"trend":data["overall"], "split":data["location_summary"]["split"],"val1":data["val1"],"val2":data["val2"]}
    AvgMsg = NLGMessage('AvgMsg', topic, args)
    # "ElaborationMsg = "especially...""
    ElaborationMsg = NLGMessage('ElaborationMsg', topic, schema_info[0])

    root = NLGLeaf(topic, "nucleus", "elaboration")
    root.addChild(NLGLeaf(topic, "nucleus", "message", AvgMsg))
    root.addChild(NLGLeaf(topic, "satellite", "message", ElaborationMsg))

    return root


# returns schema (start-end, start, end, middle), value, and trend
def getSchemaInfo(data):
    split = data["location_summary"]["split"]
    if split == "everywhere":
        return [{"schema":"everywhere", "val1":data["val1"], "val2":data["val2"], "trend": data["overall"]}]

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
            schemas.append({"schema":schema, "val1":locations[str(i)]["val1"], "val2":locations[str(i)]["val2"], "trend": locations[str(i)]["trend"]})
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

        # just keep start's?
        if start is not None and end is not None:
            if start["trend"] == end["trend"]:
                schemas.remove(end)
                start["schema"] = "start-end"
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


# get context msg based on schema
def getContextMessage(data, schema_info, topic):
    print schema_info
    assert(len(schema_info)==1)

    msg = NLGMessage('ContextMsg', topic, schema_info[0])
    root = NLGLeaf(topic, "nucleus", "message", msg)

    return root



def getAudienceMessages(data):
    root = NLGLeaf("pace", "root", "sequence")

    args = {"pace":data["pace"]}
    msg = NLGMessage('AudienceMsg', "pace", args)
    root.addChild(NLGLeaf('pace', "nucleus", "message", msg))

    return root






#
