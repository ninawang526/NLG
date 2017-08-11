############################################################################
# This file sets up the structure and order of the document. A document is a tree
# consisting of a bunch of NLGLeafs, which contain info about the topic,
# ordering, transitions, etc. The leaves are NLGMessages, which are the actual
# messages, and they contain info needed to turn the message into a sentence.
############################################################################


from NLGMessage import *
from NLGLeaf import *


# document consists of: metric paragraph and audience paragraph.
def getDocumentPlan(data, version, topic):
    document = NLGLeaf("document", "root", "sequence")

    metric_paragraph = NLGLeaf("paragraph", "root", "paragraph")

    if version == "none":
        NoneMsg = NLGMessage('NoneMsg', topic)
        metric_paragraph.addChild(NLGLeaf(topic, "nucleus", "message", NoneMsg))
        document.addChild(metric_paragraph)
        return document

    metric_paragraph.addChild(getTrendMessages(data, topic))
    document.addChild(metric_paragraph)

    audience_paragraph = NLGLeaf("paragraph", "root", "paragraph")
    audience_paragraph.addChild(getAudienceMessages(data))
    document.addChild(audience_paragraph)

    if version == "lite":
        additional_paragraph = NLGLeaf("paragraph", "root", "paragraph")
        MoreMsg = NLGMessage('MoreMsg', topic)
        additional_paragraph.addChild(NLGLeaf(topic, "nucleus", "message", MoreMsg))
        document.addChild(additional_paragraph)

    #document.printTree()
    return document


# consists of a description & a context msg
def getTrendMessages(data, topic):
    root = NLGLeaf(topic, "root", "sequence")

    split = data["location_summary"]["split"]
    if split == "everywhere":
        desc = getEverywhereDesc(data, topic)
    else:
        desc = getTrendDesc(data, topic)

    schema_info = getSchemaInfo(data)

    context = getContextMessage(data, schema_info, topic)

    root.addChild(desc)
    root.addChild(context)

    return root


# get the opening description line
def getEverywhereDesc(data, topic):
    if topic == "pace":
        root = NLGLeaf("pace", "nucleus", "description")
    else:
        root = NLGLeaf("pace", "nucleus", "sequence")

    args = {"trend":data["trend"], "value":data["average"], "split":data["location_summary"]["split"]}
    AvgMsg = NLGMessage('AvgMsg', topic, args)
    root.addChild(NLGLeaf(topic, "nucleus", "message", AvgMsg))

    args = {"trend":data["trend"]}
    # "DescriptionMsg = "which is...""
    DescriptionMsg = NLGMessage('DescriptionMsg', topic, args)
    root.addChild(NLGLeaf(topic, "satellite", "message", DescriptionMsg))

    return root


# get the opening description line
def getTrendDesc(data, topic):
    schema_info = getSchemaInfo(data)
    assert(len(schema_info) == 1)

    args = {"trend":data["trend"], "split":data["location_summary"]["split"],"value":data["average"]}
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
            schemas.append({"schema":schema, "value":locations[str(i)]["val"], "trend": locations[str(i)]["trend"]})
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
    assert(len(schema_info)==1)

    msg = NLGMessage('ContextMsg', topic, schema_info[0])
    root = NLGLeaf(topic, "nucleus", "message", msg)

    return root



def getAudienceMessages(data):
    root = NLGLeaf("pace", "root", "sequence")

    args = {"pace":data["pace-value"]}
    msg = NLGMessage('AudienceMsg', "pace", args)
    root.addChild(NLGLeaf('pace', "nucleus", "message", msg))

    return root






#
