import random
import copy
from dictionary import *
from processData import *

# traverse the tree and lexicalize each node
def lexicalize(root, feedback_version):
    global feedback
    feedback = []

    global stackOfMessages
    stackOfMessages = []

    global version
    version = feedback_version

    global connector_words
    connector_words = copy.deepcopy(CONNECTOR_WORDS)

    global compare_msg
    compare_msg = copy.deepcopy(COMPARE_MSG)

    global description_msg
    description_msg = copy.deepcopy(DESCRIPTION_MSG)

    global metric_praise
    metric_praise = copy.deepcopy(METRIC_PRAISE)

    global metric_improve_msg
    metric_improve_msg = copy.deepcopy(METRIC_IMPROVE_MSG)

    lex(root)
    feedbackString = toString(feedback)
    return feedbackString


# in-order traversal
def lex(root):
    if root.message is not None:
        feedback.append(lexMessage(root))
        stackOfMessages.append(root.message)

    if root.children is None:
        return

    for i in range(len(root.children)):
        if i == (len(root.children)-1):
            if root.topic == "paragraph" and root.type == "nucleus":
                feedback.append(lexEndingWord())
            lex(root.children[i])
        else:
            lex(root.children[i])
            if root.message is None:
                if version == "lite":
                    feedback.append(",")
                else:
                    feedback.append(lexConnector(root))


def toString(feedbackArray):
    punctuation = ["!", ".", "?", ","]
    string = "".join(feedbackArray)
    charList = list(string)

    finalCharList = []
    for i in range(len(charList)):
        if i == len(charList)-1 and string[i] not in punctuation:
            finalCharList.append(string[i])
            finalCharList.append(".")

        elif i == 0 and string[i].isalpha():
            finalCharList.append(string[i].upper())

        else:
            if charList[i-1] in punctuation and charList[i] in punctuation:
                continue
            elif charList[i-1] in punctuation and charList[i] != " " and not charList[i].isdigit():
                finalCharList.append(" ")
                #if charList[i-1] == ",":
                #    finalCharList.append(charList[i].lower())
                #else:
                finalCharList.append(charList[i].upper())
            else:
                finalCharList.append(charList[i])

    return "".join(finalCharList)


# refill local[index] with reference[index]
def refillDictionary(local, reference, index=None):
    if index is not None:
        local[index] = copy.deepcopy(reference[index])
    else:
        local = copy.deepcopy(reference)


def lexConnector(root):
    connector = root.connector

    if connector == "sequence":
        return "."

    if len(connector_words[connector]) == 0:
        refillDictionary(connector_words, CONNECTOR_WORDS, index=connector)

    if root.topic == "trend" and connector == "elaboration":
        word = "--"
    elif root.topic == "suggestion" and connector == "elaboration":
        word = ", "
    else:
        word = random.choice(connector_words[connector])
    connector_words[connector].remove(word)
    return word


def lexEndingWord():
    return random.choice(["lastly, ", "finally, "])


def lexMessage(root):
    connector = root.parent.connector
    message = root.message
    name = message.name
    topic = message.topic
    args = message.arguments

    if name == "IntroMsg":
        level = args["session-level"] - 1
        name = args["name"]
        return random.choice(INTRO_MSG[level]) %(name)

    elif topic == "pace":
        return lexPace(root)

    elif topic == "energy":
        return lexEnergy(root)

    elif topic == "filler":
        return lexFiller(root)

    elif topic == "trend":
        return lexTrend(root)

    elif topic == "suggestion":
        return lexSuggestion(root)

    elif topic == "next-session":
        if version == "lite":
            return LITE_MSG + lexNextSession(root)
        return lexNextSession(root)

    else:
        raise Exception("unrecognized message topic: %s" %(message.topic))


def lexPace(root):
    message = root.message
    name = message.name
    topic = message.topic
    args = message.arguments

    head = "your pace was "
    prevMessage = stackOfMessages[len(stackOfMessages)-1]
    if prevMessage.topic == "pace":
        head = "it was "
    if root.parent.connector == "elaboration" and root.type == "satellite":
        head = ""

    if name == "PaceDescriptionMsg":
        level = args["level"]
        usage = int(round(args["usage"]))

        if prevMessage.name == "PaceCompareMsg":
            return OK_MSG %(head)

        ##changes!!!
        #delta = magnitude(usage, IDEAL_WPM_MIN, IDEAL_WPM_MAX)
        adj_reg = ""
        adj_comp = ""
        if usage < IDEAL_WPM_MIN:
            adj_reg = "slow"
            adj_comp = "slower"
        elif usage > IDEAL_WPM_MAX:
            adj_reg = "fast"
            adj_comp = "faster"

        try:
            body = random.choice(description_msg[level-1])
            description_msg[level-1].remove(body)
            if body["type"] == "comp":
                adj = adj_comp
            else:
                adj = adj_reg
        except IndexError as error:
            refillDictionary(description_msg, DESCRIPTION_MSG, index=level-1)

        if level < 4:
            return head + body["str"] %(adj)
        else:
            return head + body["str"] %(usage, "WPM")

    elif name == "PaceCompareMsg":
        current = args["current"]
        avg = args["average"]

        current_diff = abs(current - IDEAL_WPM)
        avg_diff = abs(avg - IDEAL_WPM)
        if current_diff > avg_diff:
            adj_reg = "controlled"
            adj_comp = "less controlled"
        elif current_diff <= avg_diff:
            adj_reg = "controlled"
            adj_comp = "more controlled"

        degree_of_change = findDegreeOfChange(current, avg)

        if degree_of_change < 2 and prevMessage.tone == "positive" and root.type == "satellite":
            if len(metric_praise) == 0:
                refillDictionary(metric_praise, METRIC_PRAISE)
            body = random.choice(metric_praise)
            metric_praise.remove(body)
            return body

        else:
            if len(compare_msg[degree_of_change]) == 0:
                refillDictionary(compare_msg, COMPARE_MSG, index=degree_of_change)

            body = random.choice(compare_msg[degree_of_change])
            compare_msg[degree_of_change].remove(body)

            if body["type"] == "comp":
                adj = adj_comp
            else:
                adj = adj_reg

        modifier = "much"
        avg = int(round(avg))

        if degree_of_change < 3:
            try:
                return head + body["str"] %(adj, avg, "WPM")
            except TypeError:
                return head + body["str"] %("much", adj, avg, "WPM")
        else:
            return head + body["str"] %(avg, "WPM")

    elif name == "PaceImproveMsg":
        if len(metric_improve_msg) == 0:
            refillDictionary(metric_improve_msg, METRIC_IMPROVE_MSG)
        body = random.choice(metric_improve_msg)
        metric_improve_msg.remove(body)
        try:
            return body %("steady", "speed")
        except TypeError:
            return body %("speed")


def lexEnergy(root):
    message = root.message
    name = message.name
    topic = message.topic
    args = message.arguments

    head = "your energy was "
    prevMessage = stackOfMessages[len(stackOfMessages)-1]
    if prevMessage.topic == "energy":
        head = "it was "
    if root.parent.connector == "elaboration" and root.type == "satellite":
        head = ""

    if name == "EnergyDescriptionMsg":
        level = args["level"]
        usage = int(round(args["usage"]))

        if prevMessage.name == "EnergyCompareMsg":
            return OK_MSG %(head)

        #delta = magnitude(usage, IDEAL_VOCAL_VARIATIONS_MIN, IDEAL_VOCAL_VARIATIONS_MAX)
        adj_reg = ""
        adj_comp = ""
        if usage < IDEAL_VOCAL_VARIATIONS_MIN:
            adj_reg = "high"
            adj_comp = "higher"
        elif usage > IDEAL_VOCAL_VARIATIONS_MAX:
            adj_reg = "low"
            adj_comp = "lower"

        if len(description_msg[level-1]) == 0:
            refillDictionary(description_msg, DESCRIPTION_MSG, index=level-1)

        body = random.choice(description_msg[level-1])
        description_msg[level-1].remove(body)

        if body["type"] == "comp":
            adj = adj_comp
        else:
            adj = adj_reg

        if level < 4:
            return head + body["str"] %(adj)
        else:
            return head + body["str"] %(usage, "WPM")

    elif name == "EnergyCompareMsg":
        current = args["current"]
        avg = args["average"]

        current_diff = abs(current - IDEAL_VOCAL_VARIATIONS)
        avg_diff = abs(avg - IDEAL_VOCAL_VARIATIONS)
        if current_diff > avg_diff:
            adj = "more unbalanced"
        elif current_diff <= avg_diff:
            adj = "more balanced"

        degree_of_change = findDegreeOfChange(current, avg)

        if degree_of_change < 2 and prevMessage.tone == "positive" and root.type == "satellite":
            if len(metric_praise) == 0:
                refillDictionary(metric_praise, METRIC_PRAISE)

            body = random.choice(metric_praise)
            metric_praise.remove(body)
            return body

        else:
            if len(compare_msg[degree_of_change]) == 0:
                refillDictionary(compare_msg, COMPARE_MSG, index=degree_of_change)

            body = random.choice(compare_msg[degree_of_change])
            compare_msg[degree_of_change].remove(body)

        avg = int(round(avg))
        unit = "vocal variations"
        if avg == 1:
            unit = "vocal variation"
        if degree_of_change < 3:
            try:
                return head + body["str"] %(adj, avg, unit)
            except TypeError:
                return head + body["str"] %("much", adj, avg, unit)
        else:
            return head + body["str"] %(avg, unit)

    elif name == "EnergyImproveMsg":
        if len(metric_improve_msg) == 0:
            refillDictionary(metric_improve_msg, METRIC_IMPROVE_MSG)
        body = random.choice(metric_improve_msg)
        metric_improve_msg.remove(body)

        try:
            return body %("watch", "voice")
        except TypeError:
            return body %("variations")


def lexFiller(root):
    message = root.message
    name = message.name
    topic = message.topic
    args = message.arguments

    if name == "FillerDescriptionMsg":
        level = args["level"]
        usage = round(args["usage"],1)

        subj = "filler words "
        prevMessage = stackOfMessages[len(stackOfMessages)-1]
        if prevMessage.topic == "filler":
            subj = ""
            if prevMessage.name == "FillerCompareMsg":
                return OK_MSG %("you were")

        if level == 4 and usage != 0:
            level = 3
        body = random.choice(FILLER_DESCRIPTION[level-1])
        return body["str"] %(subj)

    elif name == "FillerCompareMsg":
        current = args["current"]
        avg = round(args["average"],1)

        if current > avg:
            adj = "more filler words"
        else:
            adj = "fewer filler words"

        subj = "filler words "
        prevMessage = stackOfMessages[len(stackOfMessages)-1]
        if prevMessage.topic == "filler":
            subj = ""

        degree_of_change = findDegreeOfChange(current, avg)
        if degree_of_change == 2 and root.type == "satellite":
            degree_of_change = 3

        if degree_of_change < 1 and message.tone == "positive":
            return random.choice(FILLER_PRAISE)

        else:
            if len(compare_msg[degree_of_change]) == 0:
                refillDictionary(compare_msg, COMPARE_MSG, index=degree_of_change)

            body = random.choice(compare_msg[degree_of_change])
            compare_msg[degree_of_change].remove(body)

        unit = "per minute"
        head = "you used "
        if root.type == "nucleus" and root.parent.connector == "contrast":
            head == "you did use"

        if degree_of_change < 3:
            try:
                return head + body["str"] %(adj, avg, unit)
            except TypeError:
                return head + body["str"] %("many", adj, avg, unit)
        else:
            if root.type == "satellite" and root.parent.connector == "contrast":
                return "it was " + body["str"] %(avg, unit)
            else:
                return body["str"] %(avg, unit)

    elif name == "FillerImproveMsg":
        if len(metric_improve_msg) == 0:
            refillDictionary(metric_improve_msg, METRIC_IMPROVE_MSG)
        body = random.choice(metric_improve_msg)
        metric_improve_msg.remove(body)

        try:
            return body %("usage")
        except TypeError:
            return body %("reduce", "usage")


############### SECOND PARAGRAPH ###################


def lexTrend(root):
    message = root.message
    name = message.name
    args = message.arguments

    if name == "SummaryPhraseMsg":
        return (random.choice(TREND_SUMMARY_MSG))

    elif name == "ProgressMsg":
        change = int(round(args["change"]))
        return (TREND_DETAILS_MSG %(change))


def lexSuggestion(root):
    message = root.message
    name = message.name
    args = message.arguments

    if name == "SummaryPhraseMsg":
        return (random.choice(SUGGESTION_DESCRIPTION_MSG))

    elif name == "SuggestionMsg":
        level = args["level"]
        return (random.choice(SUGGESTIONS_BY_LEVEL[level-1]))


def lexNextSession(root):
    message = root.message
    name = message.name
    args = message.arguments

    area = args["area"]
    minutes = args["session-length"]
    direction = args["direction"]
    goal = args["goal"]

    if area == "filler":
        if direction == "negative":
            index = 0
        else:
            index = 1
    else:
        if direction == "positive":
            index = 0
        elif direction == "constant":
            index = 1
        else:
            index = 2

    unit = ""
    if area == "energy":
        unit = "vocal variations"
        if goal == 1:
            unit = "vocal variation"
    elif area == "pace":
        unit = "WPM"

    next_session_msg = NEXT_SESSION_MSG[area][index]
    if area == "filler":
        return NEXT_SESSION_HEAD %("fillers") + random.choice(next_session_msg["desc"]) + next_session_msg["sugg"]
    else:
        try:
            return NEXT_SESSION_HEAD %(area) + random.choice(next_session_msg["desc"]) + next_session_msg["sugg"] %(goal, unit)
        except TypeError:
            return NEXT_SESSION_HEAD %(area) + random.choice(next_session_msg["desc"]) + next_session_msg["sugg"] %(goal)
        except TypeError:
            return NEXT_SESSION_HEAD %(area) + random.choice(next_session_msg["desc"]) + next_session_msg["sugg"]

# warning: somewhat arbitrary values
def findDegreeOfChange(current, avg):
    if avg == 0:
        return 0
    percent_difference = (abs(current - avg) / float(avg)) * 100
    if percent_difference < 10:
        return 0
    elif percent_difference < 40:
        return 1
    else:
        return 2



if __name__ == '__main__':
    pass
