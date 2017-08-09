from speechChangeData import getSpeechChangeData, getWordList
from documentPlan import getDocumentPlan
from lexicalize import lexicalize
import json

# Use this for pace calculations

def getParagraphs(root):
    if root.topic == 'paragraph':
        paragraphs.append(root)

    if root.children is None:
        return

    for item in root.children:
        getParagraphs(item)


# Must pass a function that calculates the differences between two speeches
def getLessonsFeedback(goal, diffFunction=None, repeat=False):
    f1 = "sample5.json"
    f2 = "sample2.json"

    wl1 = getWordList(f1)
    wl2 = getWordList(f2)

    #calculate speech difference score.
    speechChangeData = getSpeechChangeData(wl1, wl2)

    #f = open("lessons_data", "r")
    #speechChangeData = json.loads(f.read())
    #f.close()

    docPlan = getDocumentPlan(speechChangeData, goal, "full")

    global paragraphs
    paragraphs = []

    getParagraphs(docPlan)

    for paragraph in paragraphs:
        string = lexicalize(paragraph, goal)
        print string
        print ""


if __name__ == '__main__':
    getLessonsFeedback("increasing")
