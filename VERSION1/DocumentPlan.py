from NLGMessage import *
from NLGLeaf import *

# build local tree, making sure to end on a positive message.
def getP1TreeStructure(topic, description, comparison, improve):
    if description.tone == "negative" and comparison.tone == "negative":
        node1 = NLGLeaf(topic, "nucleus", "message", comparison)
        node2 = NLGLeaf(topic, "satellite", "message", improve)
        connector = "causal"

    elif description.tone == "positive" and comparison.tone == "negative":
        node1 = NLGLeaf(topic, "nucleus", "message", comparison)
        node2 = NLGLeaf(topic, "satellite", "message", description)
        connector = "contrast"

    else:
        node1 = NLGLeaf(topic, "nucleus", "message", description)
        node2 = NLGLeaf(topic, "satellite", "message", comparison)
        if description.tone == "positive":
            connector = "elaboration"
        else:
            connector = "contrast"

    tree = NLGLeaf(topic, "nucleus", connector)
    tree.addChild(node1)
    tree.addChild(node2)
    return tree


def getIntroMessage():
    args = {"session-level":data["session-level"], "name":data["name"]}
    IntroMsg = NLGMessage('IntroMsg', 'intro', 'other', args)

    return NLGLeaf("other", "nucleus", "message", IntroMsg)


#(self, topic, type, connector, message=None):
def getFillerMessages():
    args = {"level": data["filler-data"]["session-level"], "usage": data["filler-data"]["usage"]}
    FillerDescriptionMsg = NLGMessage('FillerDescriptionMsg','filler', 'description', args)

    if data["version"] == "lite":
        return NLGLeaf("filler", "nucleus", "message", FillerDescriptionMsg)

    elif data["version"] == "full":
        args = {"current": data["filler-data"]["usage"], "average": data["filler-data"]["avg"]}
        FillerCompareMsg = NLGMessage('FillerCompareMsg','filler', 'comparison', args)
        FillerImproveMsg = NLGMessage('FillerImproveMsg', 'filler', 'improve')

        return getP1TreeStructure("filler", FillerDescriptionMsg, FillerCompareMsg, FillerImproveMsg)


def getEnergyMessages():
    args = {"level": data["energy-data"]["session-level"], "usage": data["energy-data"]["usage"]}
    EnergyDescriptionMsg = NLGMessage('EnergyDescriptionMsg','energy', 'description', args)

    if data["version"] == "lite":
        return NLGLeaf("energy", "nucleus", "message", EnergyDescriptionMsg)

    elif data["version"] == "full":
        args = {"current": data["energy-data"]["usage"], "average": data["energy-data"]["avg"]}
        EnergyCompareMsg = NLGMessage('EnergyCompareMsg','energy', 'comparison', args)
        EnergyImproveMsg = NLGMessage('EnergyImproveMsg', 'energy', 'improve')

        return getP1TreeStructure("energy", EnergyDescriptionMsg, EnergyCompareMsg, EnergyImproveMsg)


def getPaceMessages():
    args = {"level": data["pace-data"]["session-level"], "usage": data["pace-data"]["usage"]}
    PaceDescriptionMsg = NLGMessage('PaceDescriptionMsg','pace', 'description', args)

    if data["version"] == "lite":
        return NLGLeaf("pace", "nucleus", "message", PaceDescriptionMsg)

    elif data["version"] == "full":
        args = {"current": data["pace-data"]["usage"], "average": data["pace-data"]["avg"]}
        PaceCompareMsg = NLGMessage('PaceCompareMsg','pace', 'comparison', args)
        PaceImproveMsg = NLGMessage('PaceImproveMsg', 'pace', 'improve')

        return getP1TreeStructure("pace", PaceDescriptionMsg, PaceCompareMsg, PaceImproveMsg)


#(self, topic, type, connector, message=None):
def getP2TreeStructure(topic, nucleus, satellite):
    node1 = NLGLeaf(topic, "nucleus", "message", nucleus)
    node2 = NLGLeaf(topic, "satellite", "message", satellite)

    root = NLGLeaf(topic, "nucleus", "elaboration")
    root.addChild(node1)
    root.addChild(node2)

    return root


def getTrendMessage():
    percent_change = data["trend-data"]["overall-change-per-session"]
    if percent_change > 5:
        trend = "positive"
    elif percent_change < -5:
        trend = "negative"
    else:
        trend = "constant"

    if trend != "positive":
        return

    args = {"trend":trend}
    SummaryPhraseMsg = NLGMessage('SummaryPhraseMsg', 'trend', 'other', args)

    args = {"change": data["trend-data"]["overall-change-per-session"], "direction": trend}
    ProgressMsg = NLGMessage('ProgressMsg', 'trend', 'other', args)

    tree = getP2TreeStructure("trend", SummaryPhraseMsg, ProgressMsg)
    return tree


def getSuggestionMessage():
    SummaryPhraseMsg = NLGMessage('SummaryPhraseMsg', 'suggestion', 'other')
    args = {"level": data["overall-level"]}
    SuggestionMsg = NLGMessage('SuggestionMsg', 'suggestion', 'other', args)

    tree = getP2TreeStructure("suggestion", SummaryPhraseMsg, SuggestionMsg)
    return tree


def getNextSessionMessage():
    # area, direction, goal, session-length
    args = data["trend-data"]["next-session"]
    NextSessionMessage = NLGMessage('NextSessionMessage', 'next-session', 'other', args)
    return(NLGLeaf("next-session", "nucleus", "message", NextSessionMessage))


# put leaves on root, ordered by their positivityScore
def addLeaves(root, leafList):
    sortedList = sorted(leafList, key=byPositivityScore, reverse=True)
    for item in sortedList:
        root.addChild(item)

    return root


def byPositivityScore(element):
    return element.positivityScore


def getDocumentPlan(type, user_data):
    global data
    data = user_data

    if type == "practice":
        # build paragraph 1
        branch = NLGLeaf("paragraph", "nucleus", "sequence")
        leafList = []
        branch.addChild(getIntroMessage())
        leafList.append(getFillerMessages())
        leafList.append(getPaceMessages())
        leafList.append(getEnergyMessages())

        paragraph1 = addLeaves(branch, leafList)

        # build paragraph2
        leafList = []
        branch = NLGLeaf("paragraph", "satellite", "sequence")

        if data["version"] == "full":
            trendMessage = getTrendMessage()
            if trendMessage is not None:
                leafList.append(trendMessage)
            leafList.append(getSuggestionMessage())

        leafList.append(getNextSessionMessage())

        paragraph2 = addLeaves(branch, leafList)

        # build document
        document = NLGLeaf("document", "root", "sequence")
        document.addChild(paragraph1)
        document.addChild(paragraph2)

    elif type == "lesson":
        return

    return document

if __name__ == '__main__':
    getDocumentPlan("practice")
