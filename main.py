from DocumentPlan import *
from parseData import parseData
from lexicalize import lexicalize
import json


def getParagraphs(root):
    if root.topic == 'paragraph':
        paragraphs.append(root)

    if root.children is None:
        return

    for item in root.children:
        getParagraphs(item)


def generateFeedback(name, session_id, filler=True, energy=True, pace=True):
    data = parseData(name, session_id)

    #data = {}
    #f = open("nlg2_data", "r")
    #results = f.read()
    #data["pace-data"] = json.loads(results)
    #data["version"] = "full"

    docPlan = getDocumentPlan(data)

    global paragraphs
    paragraphs = []
    getParagraphs(docPlan)

    for paragraph in paragraphs:
        string = lexicalize(paragraph, data["version"])
        print string
        print ""


if __name__ == '__main__':
    #normal
    #generateFeedback("[name]","-KfZeYPfnHUlYNHRnrnj")
    #few sessions
    #generateFeedback("[name]", "-KfbaPIATRv7k4GAu4lt", "4WNrrUCwF8PSnpWS2C2gTGeLH7L2", "practice")
    #normal
    #generateFeedback("[name]","-Kf_0yCWnHUlYNHRnrnj")
    #generateFeedback("[name]","-Kf_4YImnHUlYNHRnrnj")
    #generateFeedback("[name]","-Kfc07nnVJRQMtoVEf5R")
    #generateFeedback("[name]","-Kfiqt5690E4xx1ZDAf9")
    #generateFeedback("[name]","-KfYGwXLnHUlYNHRnrnj")

    #generateFeedback("[name]","-Kf_3BtznHUlYNHRnrnj")
    #generateFeedback("[name]","-Kf_2PJrnHUlYNHRnrnj")
    #generateFeedback("[name]","-KfbiFX6VJRQMtoVEf5R")
    #generateFeedback("[name]","-Kf_-DaZnHUlYNHRnrnj")
    generateFeedback("[name]","-KfDaJnwz4u6i1tfwjGm")
