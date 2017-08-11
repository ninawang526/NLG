
from DocumentPlan import *
from parseData import parseData
from lexicalize import lexicalize
import json
import random
import sys

def generateFeedback(session_id, filler=True, energy=True, pace=True):
    print session_id

    data = parseData(session_id)
    #flushResults(data)

    docPlan = getDocumentPlan(data, data["version"])

    global paragraphs
    paragraphs = []
    getParagraphs(docPlan)

    for paragraph in paragraphs:
        string = lexicalize(paragraph)
        print string
        print ""


def getParagraphs(root):
    if root.connector == 'paragraph':
        paragraphs.append(root)

    if root.children is None:
        return

    for item in root.children:
        getParagraphs(item)


def flushResults(results):
    f = open("nlg2_data", "w")
    f.write(json.dumps(results, indent=2))
    f.flush()
    f.close()


if __name__ == '__main__':
    statement = "SELECT session_id " \
                "FROM public.sessions " \
                "LIMIT 1000"
    sessionInfo = db.engine.execute(statement)
    ids = []
    for item in sessionInfo:
        ids.append(item[0])

    rand = random.choice(ids)
    print rand
    generateFeedback(rand)
    #generateFeedback("-KoIJxRnhDpAsFlVUtQT")





#
