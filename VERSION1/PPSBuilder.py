from TextPlanner import *
from MessageBuilder import *
import random
import requests
import json

# head, features, subject, predicate (comes after the verb), object, modifier
def PPSTemplate(head, features, subject, predicate, obj, modifier, conj1=None, conj2=None, conj3=None):
    PPS = {"head":head, "features":features, "subject":subject, "predicate":predicate,
            "object":obj, "modifier":modifier, "conj1":conj1, "conj2":conj2, "conj3":conj3}
    return PPS

def lexicalize(word, data=None):
    if word == "today":
        rand = random.randint(0,2)
        if rand == 0:
            return "today"
        elif rand == 1:
            return "today's date"
        else:
            return "the date"
    elif word == "number-of-flights":
        if data == 0:
            features = {"number": "plural"}
            modifier = "no"
        elif data == 1:
            features = {"number": "singular"}
            modifier = "one"
        else:
            features = {"number": "plural"}
            modifier = "several"
        return PPSTemplate("flight", features, None, None, None, modifier)
# today is June 28
# today's date is June 28
# the date is June 28
def buildDatePPS(message):
    head = "is"
    subj = lexicalize("today")
    obj = message.arguments["date"]
    return PPSTemplate(head, None, subj, None, obj, None)

# there are several flights from EWR to LAX
# a couple of flights are flying from EWR to LAX
def buildFlightDetailsPPS(message):
    head = "be"
    features = {"tense": "present"}
    subj = lexicalize("number-of-flights", message.arguments["count"])
    pObj = PPSTemplate("from", None, None, None, None, None,
                message.arguments["source"]["airport"],
                message.arguments["destination"]["airport"])
    predicate = PPSTemplate("fly", {"tense":"present"}, None, None, pObj, None)
    return PPSTemplate(head, features, subj, predicate, None, None)

def buildNextFlightPPS(message):
    return

def generateMessagePlans():
    textPlan = buildTextPlan()
    PPSArray = {'DatePPS':'', 'FlightDetailsPPS':'', 'NextFlightPPS': ''}

    messages = getAllMessages()
    for message in messages:
        name = message.messageType
        if name == 'DateMsg':
            PPSArray['DatePPS'] = buildDatePPS(message)
            #print "DateMsg:", PPSArray['DatePPS']

        elif name == 'FlightDetailsMsg':
            PPSArray['FlightDetailsPPS'] = buildFlightDetailsPPS(message)
            #print json.dumps(PPSArray['FlightDetailsPPS'])

        #elif name == 'NextFlightMsg':
        #    PPSArray['NextFlightPPS'] = buildNextFlightPPS(message)
        #    print "NextFlightPPS:", PPSArray["NextFlightPPS"]

    # one PPS for every message
    formulateSentence(PPSArray)
    # gather together phrases.
def combine(d1, d2):

    return

def formulateSentence(PPSArray):
    PPS = PPSArray['DatePPS']
    d1 = {"sentence":
        {
            "subject": PPS["subject"],
            "verb": PPS["head"],
            "object": PPS["object"],
         }
      }

    PPS = PPSArray['FlightDetailsPPS']
    d2 = {"sentence":
        {
            "subject": "there",
            "object": {
                        "type":"noun_phrase",
                        "head":"flight",
                        "features":PPS["subject"]["features"],
                        "pre-modifiers":[PPS["subject"]["modifier"]]
                        },
            "verb": "is",
            "complements": [
                {
                    "type": "preposition_phrase",
                    "noun": PPS["predicate"]["object"]["conj1"],
                    "preposition": "from"
                },
                {
                    "type": "preposition_phrase",
                    "noun": PPS["predicate"]["object"]["conj2"],
                    "preposition": "to"
                }
            ],
            "features":
            {
               "tense":"future",
               "perfect": "false",
            }
         }
      }

    test = {"sentence":
        {
            "subject": "John",
            "verb": {
                "type":"verb_phrase",
                "head":"eat"
            },
            "object": "cake",
            "features":{"form":"imperative"}
         }
      }


    #data = combine(d1, d2)
    #data = json.dumps(data)
    test = json.dumps(test)

    headers = {"Content-Type":"application/json"}
    r = requests.post('http://localhost:8000/generateSentence', data=test, headers=headers)
    print r.text


def main():
    generateMessagePlans()
    #generate DocumentPlan

if __name__ == '__main__':
    main()
