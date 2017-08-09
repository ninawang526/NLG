import random
import copy
from dictionary import *

# traverse the tree and lexicalize each node
def lexicalize(root, goal):
    global feedback
    feedback = []

    global stack_of_messages
    stack_of_messages = []

    global speech_goal
    speech_goal = goal

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
    return CONNECTOR_WORDS[connector]


def lexMessage(root):
    connector = root.parent.connector
    message = root.message
    name = message.name

    if name == "SameMsg":
        return SAME_MSG

    elif name == "AvgMsg":
        return lexAvg(root)

    elif name == "ElaborationMsg":
        return lexElaboration(root)

    elif name == "ContextMsg":
        return lexContext(root)

    elif name == "SuggestionMsg":
        return lexSuggestion(root)

    elif name == "AudienceMsg":
        return lexAudience(root)

    elif name == "NoneMsg":
        return NONE_MSG

    elif name == "MoreMsg":
        return MORE_MSG

    else:
        return None


# short description of overall trend
def lexAvg(root):
    args = root.message.arguments
    trend = args["trend"]
    split = args["split"]
    val1 = args["val1"]
    val2 = args["val2"]

    if trend == "increasing":
        adj = "slower"
    else:
        adj = "faster"

    diff = abs(val2-val1)
    if diff < 10:
        modifier = "a bit"
    elif diff < 15:
        modifier = "quite a bit"
    else:
        modifier = "much"

    add = ""
    if speech_goal != trend: # and generic = False
        add = "actually "

    if split == "everywhere":
        return AVG_EVERYWHERE_MSG %(val2, add, modifier, adj, val1)

    else:
        return AVG_TREND_MSG %(add, modifier, adj)


# "especially this area"
def lexElaboration(root):
    args = root.message.arguments
    schema = args["schema"]
    val1 = args["val1"]
    val2 = args["val2"]

    if schema == "start-end":
        place = "beginning and ending"
    elif schema == "start":
        place = "beginning"
    elif schema == "first" or schema == "second":
        place = schema + " half"
    else:
        place = schema

    return ELABORATION_MSG %(place, val1, val2)


def lexContext(root):
    args = root.message.arguments
    schema = args["schema"]
    change = args["trend"]

    if schema == "everywhere" or schema == "middle":
        return random.choice(CONTEXT_GENERIC)
    elif schema == "start" or schema == "first":
        return random.choice(CONTEXT_START)
    elif schema == "end" or schema == "second":
        return random.choice(CONTEXT_END)
    elif schema == "start-end":
        return random.choice(CONTEXT_START_END)
    else:
        raise Exception("unrecognized schema: %s", schema)


def lexSuggestion(root):
    return random.choice(SUGGESTION_MSG)


def lexAudience(root):
    args = root.message.arguments
    pace_value = args["pace"]

    if pace_value > 165:
        index = 0
    elif pace_value > 155:
        index = 1
    elif pace_value > 140:
        index = 2
    elif pace_value > 125:
        index = 3
    elif pace_value > 115:
        index = 4
    else:
        index = 5

    return random.choice(AUDIENCE_MSG[index])







#
