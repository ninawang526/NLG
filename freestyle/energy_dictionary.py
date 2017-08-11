
energy_dictionary = {

################### energy-specific words ###################
"SPEC_WORDS": {"high": {
"adj": "nice and energetic",
"verb": "reached",
"verb_c": {"front":"raised it to", "back":"raised it to"}},

"low": {
"adj": "quite monotone",
"verb": "spoke with",
"verb_c": {"front":"started slowly at", "back":"slowed to"}}
},
#############################################################

"CONNECTOR_WORDS": {"sequence": ["."],
"description": [", which "],
"contrast":[", but "],
"elaboration": [", particularly "],
"addition": [", and "]},


"NONE_MSG": "Please speak for at least 5 seconds to receive feedback!",
"MORE_MSG": "Speak for at least 30 seconds to receive more specific feedback!",

############### ENERGY PARAGRAPH ###################

"AVG_TREND_MSG": ["you were %s overall in this recording",
"you were generally %s in this recording"],

"AVG_NORMAL_MSG": ["your tone was generally pretty balanced in this recording"],

"AVG_EVERYWHERE_MSG": ["your tone was pretty balanced overall in this recording"],


# "especially..." / "but..."
"ELABORATION_MSG": {"elaboration":"in the %s",
"contrast":{
"start":"were %s in the beginning",
"first":"were %s in the first half",
"end":"were %s at the end",
"second":"were %s in the second half",
"start-end": "were %s in the beginning and end",
"middle":"were %s in the middle",
},
"sequence": "you were %s in the %s",
"addition":""},


# "which..."
"DESCRIPTION_MSG": {"high": [
"really gives strong emphasis to your ideas; there's enough contrast to highlight the core points of your speech",
"really keeps the audience interested in what you're saying",
"really conveys that you are passionate and enthusiastic about what you're saying"
],
"normal":[
"fits for a lot of speeches, but just keep in mind that contrast is the heart of public speaking -- you really want to vary your tone to keep the audience interested",
"conveys a good mix of enthusiasm and seriousness, but just keep in mind that you can really step up audience engagement by adding more variation to your tone",
"is good for a lot of speeches, but just keep in mind that you can really bring life to your speech by varying your tone"
],
"low":[
"can make you sound boring or uninterested in your own ideas",
"can easily make an audience fall asleep, no matter how good your ideas are",
"can really take away from your ideas and your message"
]},


# all the suggestions
"SUGGESTION_START": {
"low":["you should %sstart off with more energy so that people are interested in what you're saying from the start"],
"high":["opening your speech energetically was really great for captivating people and getting them engaged in what you're saying"]
},

"SUGGESTION_MIDDLE_INTRO_1": "you were %s in the middle, which ",

"SUGGESTION_MIDDLE_INTRO_2": "this ",


"SUGGESTION_MIDDLE": {"high": [
"really gives strong emphasis to your ideas; there's enough contrast to highlight the core points of your speech",
"really keeps the audience interested in what you're saying",
"really makes you sound passionate and enthusiastic about your ideas"
],
"low":[
"can make you sound boring or uninterested in your own ideas",
"can easily make a good speech sound boring -- contrast is the key to public speaking, and the right variation of tone has the power to bring your words to life",
"can make even the best speech sound bland. The right variation of tone will really animate your speech and hold the audience captive in the music of your words"
]},

"SUGGESTION_END": {
"low":["make sure to finish up with more energy; this will really give your speech one last bit of power and importance",
"you really want to finish on a strong note. Closing off your speech with a boost of energy and excitement will allow your ideas to make one last strong impression",
"you really want to finish off strong. Giving the end of your speech one last boost of energy will really impress the audience and have the speech stick in their minds"],
"high": ["this boost of energy at the end is perfect for closing your speech with strength, passion, and confidence",
"this is a really strong finish. A boost of energy at the end does a lot to leave the audience with one last good impression"]
},


"SUGGESTION_START_END": {
"low":["speaking more energetically here will set a tone of enthusiasm to the speech right away and allow you to really make a lasting impression at the end",
"speaking more energetically here will set a captivate the audience from the very beginning and drive your points home at the end"
],
"high":["the boosts of energy here really captivate from the start and make a strong impression in the end",
"speaking energetically in these spots really breathes life into your speech from the start and gives one last emphasis to your core ideas at the end"
]},

"SUGGESTION_EVERYWHERE": {
"high":[
"it tells to the audience that what you're saying is really exciting -- this is something worth listening to",
"this is an engaging speech; there is passion and enthusiasm in it, and your energy brings your words to life",
"this is an engaging speech; there is life in your ideas, and you're putting music into your words"
],
"low":[
"you don't want to sound boring; varying your tone more will convince the audience that you're passionate about what you're saying",
"you don't want to make a good speech sound bland. Variations in tone tell the audience that this is exciting -- this is something they should be listening to",
"don't make a good speech sound dull. Infusing passion and enthusiasm into your speech will capture the audience and bring your words to life",
"don't ruin a good speech by making it sound boring. Varying your tone deliberately will breathe life into your speech and hold the audience captive in the music of your words"
]},

"SUGGESTION_NORMAL_EVERYWHERE": [""],


"BALANCE_INTRO": "just make sure you're staying balanced, and that your tone matches what you're trying to convey%s",

"BALANCE_MSG": [""],



############### CLOSING PARAGRAPH ###################

"LITE_MSG": "just speak a little longer to receive more detailed feedback!"

}


#
