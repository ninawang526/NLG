#####################################################################
# There are 2 types of feedback: initial and repeat. Initial is for the first time
# a user says a particular speech. Repeat is for a later repeat of the same speech,
# which gets compared to a previous one.
# You also have to specify the metric to measure. Initial can measure anything,
# but currently repeat can only measure pace.

# ****!!! For repeat, for now I am only passing saved files of text. In the future
# pass 2 word lists: {"word","start","end"}

# flow of code:
# initial: main -> initialData -> [dataCalculations -> timeContext] -> [documentPlan -> lexicalize]
# repeat: main -> paceChangeData -> [dataCalculations] -> [documentPlan -> lexicalize]

#####################################################################
# Instructions to Add New Measurement (initial):

# 1) go to initialData.py and follow instructions to write a function there
# 2) create a new file called [metric]_dictionary.py in the intial folder
#    and fill that in according to the template of other dictionaries.
#####################################################################

from initialData import getInitialData
from paceChangeData import getPaceChangeData
import json
from database_init import db
import random

# "goal" is for repeat feedback; refers to how the user should have changed from speech1->speech2
def generateFeedback(session_id, wordlist1, wordlist2=None, topic="pace", goal="increasing", repeat=False):
    if repeat == False:
        data = getInitialData(session_id, wordlist1, topic)
        from initial.documentPlan import getDocumentPlan
        from initial.lexicalize import lexicalize
        docPlan = getDocumentPlan(data, data["version"], topic)

    else:
        assert (wordlist2 is not None)
        topic = "pace"
        if topic == "pace":
            data = getPaceChangeData(wordlist1,  wordlist2, session_id)
            from repeat.documentPlan import getDocumentPlan
            from repeat.lexicalize import lexicalize
            docPlan = getDocumentPlan(data, "increasing", data["version"])

    #flushResults(data)

    global paragraphs
    paragraphs = []

    getParagraphs(docPlan)

    for paragraph in paragraphs:
        try:
            string = lexicalize(paragraph, goal=goal)
        except TypeError:
            string = lexicalize(paragraph, topic=topic)
        print string
        print ""


# Tailor this according to how the input file is structured.
# Word lists must be in this format: [{word:"hello", start:3, end:5}, ...]
def getWordList(filename):
    with open(filename) as f:
        data = json.loads(f.read())

    results = data["results"]
    if len(results) > 0:
        try:
            STARTPAD = results[0]["alternatives"][0]["timestamps"][0][1]
        except (KeyError, IndexError) as e:
            STARTPAD = 0

    wordList = []
    for entry in results:
        if entry["final"] is True:
            try:
                timestamps = entry["alternatives"][0]["timestamps"]
                for word in timestamps:
                    if word[0] != "%HESITATION":
                        wordList.append({"word":word[0], "time":word[1]-STARTPAD, "start":word[1]-STARTPAD, "end":word[2]-STARTPAD})
            except (KeyError, IndexError) as e:
                continue

    return wordList


def getParagraphs(root):
    if root.topic == 'paragraph':
        paragraphs.append(root)

    if root.children is None:
        return

    for item in root.children:
        getParagraphs(item)


def flushResults(data):
    f = open("initial_data","w")
    f.write(json.dumps(data, indent=2))
    f.flush()
    f.close()


if __name__ == '__main__':
    f1 = "sample2.json"
    f2 = "sample3.json"

    wl1 = getWordList(f1)
    wl2 = getWordList(f2)

    statement = "SELECT session_id, user_id " \
            "FROM public.sessions " \
            "LIMIT 1000"
    sessionInfo = db.engine.execute(statement)
    ids = []
    for item in sessionInfo:
        ids.append({"session":item[0],"user":item[1]})

    rand = random.choice(ids)
    print rand["session"]

    #session_id = "-KnANjythDpAsFlVUtQT"
    session_id = rand["session"]
    generateFeedback(session_id=session_id, wordlist1=wl1, topic="pause", repeat=False)
