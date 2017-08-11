import random
import copy
from pace_dictionary import pace_dictionary
from energy_dictionary import energy_dictionary

# traverse the tree and lexicalize each node
def lexicalize(root):
    global feedback
    feedback = []

    global stack_of_messages
    stack_of_messages = []

    global dictionary
    topic = root.topic
    if topic == "energy":
        dictionary = energy_dictionary
    else:
        dictionary = pace_dictionary

    lex(root)

    return toString(feedback)


# in-order traversal of document tree, lexicalizing messages one by one
def lex(root):
    if root.message is not None:
        msg = lexMessage(root)
        if msg is not None:
            feedback.append(lexMessage(root))
        stack_of_messages.append(root.message)

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
    word = random.choice(dictionary["CONNECTOR_WORDS"][connector])

    # special case
    for child in root.children:
        if child.connector == "message":
            if child.message.name == "AdditionalMsg":
                word = ". As for the speech as a whole, "

    return word


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

    elif name == "SuggestionMsg":
        return lexSuggestion(root)

    elif name == "MiddleSuggestionMsg":
        return lexMiddleSuggestion(root)

    elif name == "AdditionalMsg":
        return lexAdditional(root)

    elif name == "BalanceMsg":
        return lexBalance(root)

    elif name == "OverallMsg":
        return lexOverall(root)

    #elif name == "NextRecordingMsg":
    #    return lexNext(root)

    elif name == "NoneMsg":
        return dictionary["NONE_MSG"]

    elif name == "MoreMsg":
        return dictionary["MORE_MSG"]


# short description of overall trend
def lexAvg(root):
    args = root.message.arguments
    trend = args["trend"]
    value = int(args["value"])
    split = args["split"]

    if trend != "normal":
        adj = dictionary["SPEC_WORDS"][trend]["adj"]

    if split == "everywhere":
        if trend == "normal":
            choice = random.choice(dictionary["AVG_EVERYWHERE_MSG"])
            try:
                return choice %(value)
            except:
                return choice
        else:
            choice = random.choice(dictionary["AVG_TREND_MSG"])
            try:
                return choice %(value, adj)
            except TypeError:
                return choice %(adj)
    else:
        if trend == "normal":
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


# meaning of overall trend
def lexElaboration(root):
    args = root.message.arguments

    schema = args["schema"]
    trend = args["trend"]
    value = int(args["value"])

    try:
        last_message = stack_of_messages[len(stack_of_messages)-1]
    except IndexError as e:
        last_message = None

    d = dictionary["SPEC_WORDS"][trend]
    adj = d["adj"]
    verb = d["verb"]

    if schema == "start" or schema == "first":
        verb_c = d["verb_c"]["front"]
    else:
        verb_c = d["verb_c"]["back"]

    if schema == "start-end":
        place = "beginning and ending"
    elif schema == "start":
        place = "beginning"
    elif schema == "first" or schema == "second":
        place = schema + " half"
    else:
        place = schema


    choice = dictionary["ELABORATION_MSG"][root.parent.connector]
    if root.parent.connector == "contrast":
        choice = choice[schema]
        head = ""
        if root.type == "nucleus":
            head = "you "
        elif last_message is not None:
            if last_message.name == "AvgMsg":
                head = "you "

        try:
            return head + choice %(adj, value)
        except:
            return head + choice %(adj)

    elif root.parent.connector == "sequence":
        try:
            return choice %(adj, value, place)
        except:
            return choice %(adj, place)
    elif root.parent.connector == "addition":
        try:
            return choice %(verb_c, value, place)
        except:
            return choice
    else:
        try:
            return choice %(place, verb, value)
        except:
            return choice %(place)


def lexSuggestion(root):
    args = root.message.arguments

    schema = args["schema"]
    trend = args["trend"]
    value = int(args["value"])

    add = ""
    if root.parent.connector == "contrast" and root.type == "satellite":
        add = "also "

    if schema == "everywhere":
        if trend == "normal":
            return random.choice(dictionary["SUGGESTION_NORMAL_EVERYWHERE"])
        else:
            return random.choice(dictionary["SUGGESTION_EVERYWHERE"][trend])
    elif schema == "start" or schema == "first":
        try:
            return (random.choice(dictionary["SUGGESTION_START"][trend]) %(add))
        except:
            return random.choice(dictionary["SUGGESTION_START"][trend])
    elif schema == "end" or schema == "second":
        try:
            return (random.choice(dictionary["SUGGESTION_END"][trend]) %(add))
        except:
            return random.choice(dictionary["SUGGESTION_END"][trend])
    elif schema == "start-end":
        return random.choice(dictionary["SUGGESTION_START_END"][trend])
    elif schema == "middle":
        return dictionary["SUGGESTION_MIDDLE_INTRO_2"] + random.choice(dictionary["DESCRIPTION_MSG"][trend])
    else:
        raise Exception("unrecognized schema: %s", schema)


def lexMiddleSuggestion(root):
    args = root.message.arguments

    trend = args["trend"]
    value = int(args["value"])

    try:
        adj = dictionary["SPEC_WORDS"][trend]["adj"]
        return (dictionary["SUGGESTION_MIDDLE_INTRO_1"] %(adj)) + random.choice(dictionary["SUGGESTION_MIDDLE"][trend])
    except:
        return (dictionary["SUGGESTION_MIDDLE_INTRO_1"] %(value)) + random.choice(dictionary["SUGGESTION_MIDDLE"][trend])


def lexAdditional(root):
    args = root.message.arguments
    trend = args["trend"]
    return random.choice(dictionary["SUGGESTION_EVERYWHERE"][trend])


def lexBalance(root):
    return dictionary["BALANCE_INTRO"] %(random.choice(dictionary["BALANCE_MSG"]))


def lexOverall(root):
    args = root.message.arguments
    pace_value = args["pace-value"]

    if pace_value > 160:
        index = 0
    elif pace_value > 150:
        index = 1
    elif pace_value > 140:
        index = 2
    elif pace_value > 125:
        index = 3
    elif pace_value > 115:
        index = 4
    else:
        index = 5

    return random.choice(dictionary["OVERALL_MSG"][index])


def lexNext(root):
    args = root.message.arguments
    area = args["area"]
    value = args["value"]

    if value > 140:
        index = "high"
    else:
        index = "low"

    return dictionary["NEXT_RECORDING_INTRO"] + dictionary["NEXT_RECORDING_SUGG"][index]








#
