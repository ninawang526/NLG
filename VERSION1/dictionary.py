
CONNECTOR_WORDS = {"elaboration": ["--", ", ", ", which is ", "; ", "; that's "],
"contrast":[", but ", ", although ", ", however "],
"causal": [", so ", ", so just "]}

############### FIRST PARAGRAPH ###################

INTRO_MSG = [["you need a little more practice, %s"],
["not bad, %s!", "alright %s!"],
["pretty good, %s!", "nicely done %s!"],
["brilliantly said, %s!", "wonderful job, %s!", "impressive, %s!"]]


DESCRIPTION_MSG = [[{"str":"a bit too %s","type":"reg"}, {"str":"pretty %s here","type":"reg"}],
[{"str":"on the %s side","type":"comp"}, {"str":"quite %s","type":"reg"}],
[{"str":"a little %s than it should have been","type":"comp"}, {"str":"a bit %s","type":"reg"}, {"str":"a little %s","type":"reg"}],
[{"str":"a perfect %g %s","type":"reg"}, {"str":"an excellent %g %s","type":"reg"}]]


COMPARE_MSG = [[{"str":"a bit %s this time than your average of %g %s","type":"comp"}, {"str":"slightly %s than your average of %g %s","type":"comp"}],
[{"str":"%s than your average of %g %s","type":"comp"}],
[{"str":"%s %s this time than your average of %g %s","type":"comp"}, {"str":"a lot %s than your average of %g %s","type":"comp"}],
# BIG FILLER CHANGES DON'T USE THE LINE ABOVE, THEY USE THE LINE BELOW!
[{"str":"a big improvement from your average of %g %s","type":"reg"}]]


FILLER_DESCRIPTION = [[{"str":"you spoke a bit too many %sin this recording","type":""}, {"str":"you used quite a few %sin this recording","type":""}],
[{"str":"you used a couple %sin this recording","type":""}],
[{"str":"you hardly spoke any %sin this recording","type":""}, {"str":"you barely used any %sin this recording","type":""}, {"str":"you only used a few %sin this recording","type":""}],
[{"str":"you didn't use any %sin this recording","type":""}, {"str":"you spoke zero %sin this recording","type":""}]]


OK_MSG = "%s still in good range"
#{"str":"","type":""}

METRIC_PRAISE = ["right within TED talk range!",
"exactly where it should be",
"right on par with TED speakers!"]

FILLER_PRAISE = ["very impressive!", "not easy!"]

METRIC_IMPROVE_MSG = ["make sure to %s your %s a little more",
"be more aware of %s in your next recording",
"try to %s your %s next time",
"be more careful to %s your %s"]


############### SECOND PARAGRAPH ###################

TREND_SUMMARY_MSG = ["your hard work is paying off",
"your hard work has been really paying off",
"these practice recordings have really helped"]

TREND_DETAILS_MSG = "you're improving by about %g percent with each recording!"

SUGGESTION_DESCRIPTION_MSG = ["at your current level", "at your level", "at this level"]

SUGGESTIONS_BY_LEVEL = [
["you should watch some TED talks and carefully observe how they capture the audience. Also, practice makes perfect, so a sure-fire way to improve is to complete at least one speech lesson a day"],
["try to put more thought into your speeches beforehand; plan out what you're going to say before you start speaking"],
["your next step should be to make speech practice a daily habit: watch for filler usage, pace, and energy in your everyday conversations"],
["you should keep in mind that controlling filler usage, pace, and energy is vital for a good speech, but a great speech will have personality as well. Challenge yourself to add a little improvisation or humor to your speeches",
"you should challenge yourself to speak longer during recordings",
"you should start thinking about more advanced public speaking techniques as well. Start out with body language--make sure your gestures, posturing, and movements are all done with purpose"]]

NEXT_SESSION_HEAD = "for now, let's focus on %s: "

NEXT_SESSION_MSG = {
"pace": [{"desc":["your pace this time was slow and very deliberate, but speeding up a bit will make you sound more confident and optimistic.", "your pace this time was slow and very deliberate, but to make sure that your audience stays focused, you can speed up just a little bit."],
            "sugg": "for your next recording, try to aim for at least %g WPM"},
        {"desc":["your pace this time was a nice balance of speed and emphasis, which gives you many options for conveying different tones and moods."],
            "sugg": "for your next recording, try to keep this pace up while speaking for an extra minute"},
        {"desc":["your pace this time was the faster side, which conveys a lot of energy but makes it harder to project authority.","your pace this time tends to be quite fast, which makes it harder to bring out key contrasts in your speech.", "you spoke quite quickly this time, which can make it hard for the audience to keep up."],
            "sugg": "for your next recording, try to bring it down to a more balanced %g WPM"}],

"energy": [{"desc":["your energy this time was pretty low, which can make your speech sound boring.", "you were on the more monotone side this time, which can make you sound uninterested or tired."],
            "sugg": "so for your next recording, try to shoot for at least %g %s"},
        {"desc":["in this recording, you did a great job varying your tone and voice throughout your speeches"],
            "sugg": ", so for your next recording, try to keep this up while speaking for an extra minute!"},
        {"desc":["you spoke with a lot of vocal variations in this recording, which conveys a lot of excitement but can make it hard for the audience to follow along.", "you spoke with a lot of energy in this recording, which conveys enthusiasm but can distract from the contents of your speech."],
            "sugg": "for your next recording, try to tone it down to %g %s!"}],

"filler": [{"desc":["you used a few more fillers than you should this time, which can make you sound like you lack confidence."],
            "sugg": "for your next recording, try to take a pause in between ideas, giving yourself time to gather your thoughts without filling the silence with an \"um\" or \"uh\""},
        {"desc":["you did a great job at keeping filler usage low in this recording"],
            "sugg": ", so for your next recording, try to keep this up while speaking for an extra minute!"}],

"time":[{"desc":"you've been doing well across all the measurements"},
        {"sugg":"so try to speak for a total of %s seconds while keeping up the good work!"}]
}

LITE_MSG = "just complete a few more recordings to receive more detailed feedback!"







#
