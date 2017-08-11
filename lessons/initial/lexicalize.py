import random
import copy
from pause_dictionary import pause_dictionary
from pace_dictionary import pace_dictionary

# traverse the tree and lexicalize each node
def lexicalize(root, topic):
    global feedback
    feedback = []

    global dictionary

    if topic == "pace":
        dictionary = pace_dictionary
    elif topic == "pause":
        dictionary = pause_dictionary
    else:
        raise Exception("unrecognized topic: %s" %(topic))

    lex(root)
    return toString(feedback)


# in-order traversal of document tree, lexicalizing messages one by one
def lex(root):
    if root.message is not None:
        msg = lexMessage(root)
        if msg is not None:
            feedback.append(lexMessage(root))
        else:
            feedback.append(root.message.name)

    if root.children is None:
        return

    for i in range(len(root.children)):
        lex(root.children[i])
        if i < (len(root.children)-1):
            if root.message is None:
                feedback.append(lexConnector(root))


def toString(feedbackArray):
    punctuation = ["!", ".", "?"]
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
                finalCharList.append(charList[i].upper())
            else:
                finalCharList.append(charList[i])

    return "".join(finalCharList)


def lexConnector(root):
    connector = root.connector
    return dictionary["CONNECTOR_WORDS"][connector]


def lexMessage(root):
    connector = root.parent.connector
    message = root.message
    name = message.name

    if name == "AvgMsg":
        return lexAvg(root)

    elif name == "DescriptionMsg":
        return lexDescription(root)

    elif name == "ElaborationMsg":
        return lexElaboration(root)

    elif name == "ContextMsg":
        return lexContext(root)

    elif name == "AudienceMsg":
        return lexAudience(root)

    elif name == "NoneMsg":
        return dictionary["NONE_MSG"]

    elif name == "MoreMsg":
        return dictionary["MORE_MSG"]

    else:
        return None


# short description of overall trend
def lexAvg(root):
    args = root.message.arguments
    trend = args["trend"]
    value = int(args["value"])
    split = args["split"]

    if trend == "high":
        adj = dictionary["ADJ_HIGH"]
    else:
        adj = dictionary["ADJ_LOW"]

    if split == "everywhere" and trend == "normal":
        choice = random.choice(dictionary["AVG_NORMAL_MSG"])
        try:
            return choice %(value)
        except TypeError:
            return choice
    else:
        choice = random.choice(dictionary["AVG_TREND_MSG"])
        try:
            return choice %(value, adj)
        except TypeError:
            return choice %(adj)


# meaning of overall trend
def lexDescription(root):
    args = root.message.arguments
    trend = args["trend"]

    return random.choice(dictionary["DESCRIPTION_MSG"][trend])


# "especially this area"
def lexElaboration(root):
    args = root.message.arguments
    schema = args["schema"]
    val = args["value"]

    if schema == "start-end":
        place = "beginning and ending"
    elif schema == "start":
        place = "beginning"
    elif schema == "first" or schema == "second":
        place = schema + " half"
    else:
        place = schema

    try:
        return dictionary["ELABORATION_MSG"] %(place, val)
    except TypeError:
        return dictionary["ELABORATION_MSG"] %(place)


def lexContext(root):
    args = root.message.arguments

    schema = args["schema"]
    trend = args["trend"]
    value = int(args["value"])

    if schema == "everywhere":
        if trend == "normal":
            return random.choice(dictionary["SUGGESTION_NORMAL_EVERYWHERE"])
        else:
            return random.choice(dictionary["SUGGESTION_EVERYWHERE"][trend])
    elif schema == "start" or schema == "first":
        return random.choice(dictionary["SUGGESTION_START"][trend])
    elif schema == "end" or schema == "second":
        return random.choice(dictionary["SUGGESTION_END"][trend])
    elif schema == "start-end":
        return random.choice(dictionary["SUGGESTION_START_END"][trend])
    elif schema == "middle":
        return dictionary["SUGGESTION_MIDDLE_INTRO"] + random.choice(dictionary["DESCRIPTION_MSG"][trend])
    else:
        raise Exception("unrecognized schema: %s", schema)


def lexAudience(root):
    args = root.message.arguments
    pace_value = args["pace"]

    if pace_value > 165:
        index = 0
    elif pace_value > 155:
        index = 1
    elif pace_value > 130:
        index = 2
    elif pace_value > 125:
        index = 3
    elif pace_value > 115:
        index = 4
    else:
        index = 5

    return random.choice(dictionary["AUDIENCE_MSG"][index])







#
