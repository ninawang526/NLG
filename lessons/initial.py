import json
from dtw import dtw
from nltk.metrics.distance import edit_distance

# Tailor this according to how the input file is structured.
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
                        wordList.append({"word":word[0], "time":word[1]-STARTPAD})
            except (KeyError, IndexError) as e:
                continue

    return wordList

def getDtwPath(wl1, wl2):
    transcript1 = " ".join([x["word"] for x in wl1])
    transcript2 = " ".join([x["word"] for x in wl2])

    x = transcript1.split()
    y = transcript2.split()

    dist, cost, acc, path = dtw(x, y, edit_distance)
    return path

f1 = "sample1.json"
f2 = "sample3.json"

global w1
w1 = getWordList(f1)
global w2
w2 = getWordList(f2)

global path
path = getDtwPath(w1, w2)

global speech1path
speech1path = path[0]
global speech2path
speech2path = path[1]
assert (len(speech2path)==len(speech1path))
