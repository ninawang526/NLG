from DocumentPlan import *
from processData import *
from lexicalize import *


def getParagraphs(root):
    if root.topic == 'paragraph':
        paragraphs.append(root)

    if root.children is None:
        return

    for item in root.children:
        getParagraphs(item)


def generateFeedback(name, session_id, user_id, session_type, filler=True, energy=True, pace=True):
    data = parseData(name, session_id, user_id)

    f = open("nlg_data", "w")
    f.write(json.dumps(data, indent=2))
    f.write("\n\n")

    docPlan = getDocumentPlan(session_type, data)

    msgs = docPlan.getOrderedMessages()
    for m in msgs:
        item = m.message
        s = item.name + " " + item.topic + " " + json.dumps(item.arguments) + " " + str(m.positivityScore) + '\n'
        f.write(s)
    f.close()

    #global paragraphs
    #paragraphs = []

    #getParagraphs(docPlan)


    #for paragraph in paragraphs:
    #    string = lexicalize(paragraph, data["version"])
    #    print string
    #    print ""


if __name__ == '__main__':
    #normal
    #generateFeedback("[name]","-KfZeYPfnHUlYNHRnrnj", "HEFVpmnkcVTLf8uhyb7DM2KnML13", "practice")
    #few sessions
    #generateFeedback("[name]", "-KfbaPIATRv7k4GAu4lt", "4WNrrUCwF8PSnpWS2C2gTGeLH7L2", "practice")
    #normal
    #generateFeedback("[name]","-Kf_0yCWnHUlYNHRnrnj", "RKqVhoOjJMhJ5Kt0gpP44OqFcoJ2", "practice")
    #generateFeedback("[name]","-Kf_4YImnHUlYNHRnrnj", "jXBraUQxenNEcJsBOlqSrbc97xh2", "practice")
    #generateFeedback("[name]","-Kfc07nnVJRQMtoVEf5R", "EIgD2E3pSjMEgnUG9pokigkkPHq1", "practice")
    generateFeedback("[name]","-Kfiqt5690E4xx1ZDAf9", "SC2jlMrbPORIg7qdgYAI44C3Gy03", "practice")
    #generateFeedback("[name]","-KfYGwXLnHUlYNHRnrnj", "NF26l69ZNoSk7paYRoVV17aCYZE2", "practice")
