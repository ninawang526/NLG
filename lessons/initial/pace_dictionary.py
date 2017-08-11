# pace-specific words
pace_dictionary = {
"ADJ_HIGH" : "fast",
"ADJ_LOW" : "slow",



"CONNECTOR_WORDS" : {"sequence": ".",
"elaboration": ", especially ",
"description": ", which "},

"NONE_MSG" : "Please speak for at least 5 seconds to receive feedback!",
"MORE_MSG" : "Speak for at least 30 seconds to receive more specific feedback!",

############### PACE PARAGRAPH ###################
"AVG_TREND_MSG" : ["your pace was pretty %s in this recording",
"you spoke at a pace of %d WPM -- quite %s -- for most of this recording",
"you spoke at a pretty %s pace in this recording"],

"AVG_NORMAL_MSG" : ["your pace was nice and balanced for most of this recording",
"you spoke at a nice, balanced %s WPM for most of this recording"],


# "especially..."
"ELABORATION_MSG" : "in the %s, where you spoke at %d WPM",


# "which..."
"DESCRIPTION_MSG" : {"high": [
"is good for projecting energy and excitement, but may be less effective in showing authority",
"is perfect for a smaller audience or occasion, but can be much less effective for a larger one",
"projects a lot of enthusiasm and passion, but makes it harder to bring out key contrasts",
"projects a lot of enthusiasm, but makes it much harder to give any one word real emphasis or weight",
"conveys a lot of energy and passion, but can make it hard for the audience to keep up with what you're saying",
"conveys a lot of enthusiasm, but can make it difficult for your central ideas and messages to stand out"
],
"normal":[
"provides really good variety of energy and emphasis throughout your speech",
"allows you to put emphasis on key points while conveying energy in the right places",
"provides a lot of flexibility for conveying different tones and moods",
"provides really good variety of energy and emphasis. Just make sure that you're giving your central idea the right weight and authority",
"conveys a good mix of both energy and emphasis, but just keep in mind that you can really step up intensity and tension by slowing down at key moments",
"conveys a good mix of both energy and emphasis, but just keep in mind that you can bring out contrasts more strongly by slowing down at key moments"
],
"low":[
"is very slow and deliberate: perfect for projecting authority, but perhaps less effective in showing optimism or passion",
"projects a lot of authority, but can be less effective in projecting confidence and optimism",
"is perfect for bringing the audience along and communicating your thoughts clearly, but could sound too measured for more lighthearted speeches",
"plays with tension and surprise -- you have the freedom to go in many different directions of tone and message",
"conveys a strong use of silence and pauses, but but too much could make you sound contrived",
"conveys a strong use of silence, but too much could make you sound like you've lost your way"
]},


# all the suggestions
"SUGGESTION_START" : {
"high":["it's important to start off with a slower pace so that you can ease into the speech and engage the audience right away"],
"low":["opening your speech slowly and deliberately is perfect for engaging the audience from the start and giving everyone enough time to follow your train of thought"]
},

"SUGGESTION_MIDDLE_INTRO" : "keep in mind that the middle of your speech is where you express the bulk of your ideas; your pace here ",


"SUGGESTION_MIDDLE" : {
"high":["conveyed a lot of energy and excitement, whereas a slower pace may be more effective in showing authority",
"conveyed a lot of optimism and confidence, where as a slower pace may be better in showing thoughtfulness and authority",
"projects a lot of lightheartedness and optimism. If you were addressing a more solemn occasion, a slower pace would definitely be better here.",
"is great for conveying optimism and passion. If you wanted to give your ideas more gravity, a slower pace would be better here"
],
"low":["conveyed a lot of thoughtfulness and authority. If you want to show more enthusiasm and passion, a faster pace might work better",
"conveyed a lot of thoughtfulness and gravity. If you want to show more optimism and confidence, a faster pace might be more appropriate",
"is perfect for giving weight to your points and communicating them clearly, but may be too measured for more lighthearted speeches"]
},

"SUGGESTION_END" : {
"high":["make sure to finish up at a slower pace; this will really bring your speech to a confident, purposeful close"],
"low": ["finishing slowly and deliberately is perfect for bringing your speech to a confident, purposeful close"]
},


"SUGGESTION_START_END" : {
"high":["using a slower, more deliberate pace in these parts will help you engage the audience from the start and finish on a strong note in the end",
"using a slower, more deliberate pace in these parts will convey more authority, allowing you to set a powerful tone at the start and drive your points home at the end"
],
"low":["speaking slowly and deliberately in these parts is perfect for engaging the audience from the start and finishing on a strong note in the end",
"speaking slowly and deliberately in these parts conveys great thoughtfulness, which is perfect for setting a powerful tone at the start and driving your points home at the end"
]},

"SUGGESTION_EVERYWHERE" : {
"high":[
"a slower pace will let your words breathe and give the audience time to absorb what you're saying",
"remember that if you speak too fast, audience members won't be able to keep up",
"remember that a speech is a conversation with an audience, and if you speak too fast, audience members won't be able to keep up",
"keep in mind that when you speak too fast, people in a larger audience have a harder time gathering their own thoughts",
"the faster you talk, the less you control your own words; a slower pace will let your words breathe and give the audience time to absorb what you're saying",
"a slower pace with purposeful pauses will allow you to respond to the audience's mood",
"a slower pace will allow you to \"hear\" the audience listening to you, and you can respond better to the overall mood",
"remember that the faster you talk, the less you hear. a slower pace will allow you to better respond to the audience's mood",
"make sure that you're talking in a pace that helps your audience move with you from one idea to the next",
"you'll give your words authority as well as energy by slowing down in places that matter",
"make sure to slow down and give your audience the space to hear your words and be persuaded by them",
"remember that this pace might be too fast for larger audiences, as it will take a longer time for your words to reach the back of the room",
"remember that when you speak quickly, it's much harder to give any one word real emphasis or weight",
"if you use a slower pace, you'll be able to convey a much better sense of control and thoughtfulness"
],
"low":[
#"keep in mind that this pace is great for a large audience, but it might come across as too measured for a smaller audience",
"always keep in mind the purpose of what you're saying; a faster pace will be much better suited for conveying passion and enthusiasm",
"keep in mind that a faster pace will energize your audience and help them stay engaged in what you're saying",
"think about the purpose of what you're saying; a faster pace might be more appropriate if you're trying to convey excitement and enthusiasm"
]},

"SUGGESTION_NORMAL_EVERYWHERE" : [
"you should also think generally about the intensity of your words -- are you adding emphasis exactly where you want to?",
"you should also think about how your pace fits in with what you're saying. If you were to sum up your tone in just one word, what would it be? Do you feel that your pace properly express this?",
"you should also think generally about ways you can step up the quality of your speech even more. For example, by posing simple questions along the way, you can really help the audience follow your argument"
],


"AUDIENCE_MSG" : [
["overall, your pace in this recording was likely much too fast for any audience -- a wall of words. Speaking too quickly makes it \
difficult to have a \"conversation\" with the audience, and you're much more likely to \
make mistakes"
],

["overall, your pace in this recording was likely too fast for any audience over 30 people. \
It leaves the audience very little time to think and catch up, and you risk leaving people behind",
"overall, your pace in this recording was likely too fast for any audience over 30 people. \
It may sound over-rehearsed -- there's no real \"conversation\" happening with the audience.",
"your overall pace in this recording was likely too fast for any audience over 30 people. \
At a pace like this, it's hard to project authority or create meaningful tension. You may make mistakes \
or miss out something important"
],

["overall, your pace in this recording was brisk but not running out of control. \
You're giving yourself options -- you can even choose to throw in some faster short passages for emphasis",
"overall, your pace in this recording was a bit fast but not out of control. \
Think about slowing down for any audience over 30 people, and adding changes of intensity to create a sense \
of conversation"
],

["overall, this was a good presentation pace for most audiences. You showed respect \
by helping everyone in the audience follow your arguments. You used silence and pauses \
to add emphasis and exploit contrasts",
"overall, this was a good presentation pace for most audiences. You're using silence/pauses \
to add emphasis and exploit contrasts. You're keeping control of your thoughts and words, and \
you're giving yourself options to respond to the audience"
],

["overall, this was a strong, measured presentation pace for all audiences. You kept \
control of your thoughts and words, and gave the audience plenty of time to absorb \
what you said"],

["overall, this was a slow, measured, \"presidential\" presentation pace for all audiences, \
especially very large audiences or for a speech delivered in open air. You showed respect \
by helping everyone in the audience follow your arguments. You projected authority and dignity"
]]
}
