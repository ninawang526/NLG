from database_init import db
import json
#pylab inline
import numpy as np
import matplotlib.pyplot as plt
from google.cloud import storage
import os
import google.auth
import IPython

##### when calculating, variation must be across sentences. doesn't make sense to say wpm didn't vary within one sentence bc
## obviously it didn't...it was calculated as an avg

# authenticate
projectID  = "oraiapp-3da7c"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "app.json"
credentials, project = google.auth.default()
if credentials.requires_scopes:
    credentials = credentials.with_scopes(['https://www.googleapis.com/auth/devstorage.read_write'])
storage_client = storage.Client(credentials=credentials,project=projectID)
storageBucket = storage_client.get_bucket('oraiapp-3da7c.appspot.com')


#session_id = "-Kfsn6SJ90E4xx1ZDAf9"
#user_id = "EaMibpsK4uPHFCB4EiGZ0Rpqf5D3"

#session_id = "-Kf_3BtznHUlYNHRnrnj"
#user_id = "jXBraUQxenNEcJsBOlqSrbc97xh2"


#session_id = "-KfbR79qTRv7k4GAu4lt"
#user_id = "8OZ5Gp9cF4aDPDqstL2ySjpf8mJ2"

session_id = "-KfDgUY4-TVEcUGQmzeP"
user_id = "zMza7lNNvlY9gJYa9Oos8LW46Pg2"

statement = "SELECT wpm_variation, transcript_string, total_time " \
                "FROM public.sessions " \
                "WHERE session_id = \'" + session_id + "\'" \
                " AND user_id = \'" + user_id + "\'"

data = db.engine.execute(statement)

wpms = {}
for item in data:
    wpm = json.loads(item[0])
    print item[1]
    print "total time: ", item[2]


#get audio
#blob = storageBucket.get_blob(user_id + '/audio/' + session_id + '.wav')
#with open("audio.wav", 'wb') as file_obj:
#    blob.download_to_file(file_obj)

#audio = IPython.display.Audio(filename='audio.wav')
#display(audio)



wpmsList = []
wpms = []
times = []
for i in range(len(wpm)):
    wpmsList.append({"wpm": wpm[str(i)]["wpm"], "start":wpm[str(i)]["range"]["0"], "end":wpm[str(i)]["range"]["1"]})
    wpms.append(wpm[str(i)]["wpm"])
    times.append(wpm[str(i)]["range"]["0"])


plt.plot(times, wpms)

overall_wpm = sum(wpms)/len(wpms)
plt.axhline(overall_wpm, color='r', linestyle='dashed', linewidth=2)

print "avg: ", overall_wpm
overall_std = np.std(np.array(wpms))
print "stddev: ", overall_std

stds = []
# wpmsList split into ~50 second blocks, calculate std on those.
# if shorter speech, split into fewer parts; want ~3 points in each group
duration = wpmsList[len(wpmsList)-1]["end"]
if duration < 80:
    INTERVAL = times[len(times)-1] / 2.5
else:
    INTERVAL = times[len(times)-1] / 5.

print "interval: ", INTERVAL
seconds = 0
block = []
for item in wpmsList:
    time =  item["end"] - item["start"]
    if seconds+time >= INTERVAL:
        if abs(INTERVAL-seconds) < abs(INTERVAL-(seconds+time)) and seconds > 0:
            stds.append(block)
            block = []
            block.append(item)
            seconds = time
        else:
            block.append(item)
            stds.append(block)
            block = []
            seconds = 0
    else:
        block.append(item)
        seconds = seconds + time

if len(block) > 0:
    if len(block) == 1:
        stds[len(stds)-1].extend(block)
    else:
        stds.append(block)

times = []
times.append(0)
times.append(duration / 2.)
#times.append(2 * (duration / 3.))
times.append(duration)
print times

for item in times:
    plt.axvline(item, color='g', linestyle='dashed', linewidth=2)

trend = []
for group in stds:
    print group
    wpms = []
    start = group[0]["start"]
    for i in range(len(group)):
        wpms.append(group[i]["wpm"])
        if i == (len(group)-1):
            end = group[i]["end"]
            plt.axvline(end, color='r', linestyle='dashed', linewidth=2)


    std = np.std(np.array(wpms))
    print std
    if std > 30:
        plt.axvspan(start, end, alpha=0.2, color='red')
        variation = "high"
    elif std < 5 and std > 0: #CHANGE TO 5.
        plt.axvspan(start, end, alpha=0.2, color='yellow')
        variation = "low"
    else:
        variation = "normal"
    trend.append({"variation":variation, "std": std, "start":start, "end":end})

variation = trend[0]["variation"]
start = trend[0]["start"]
std = trend[0]["std"]
count = 0
groups = []
for i in range(len(trend)):
    if trend[i]["variation"] == variation:
        end = trend[i]["end"]
        std = trend[i]["std"]
        count = count + 1
    else:
        groups.append({"start":start, "end":end, "variation":{"type":variation,"std":std}})
        variation = trend[i]["variation"]
        start = trend[i]["start"]
        end = trend[i]["end"]
        std = trend[i]["std"]
        count = 0

    if i == len(trend)-1:
        groups.append({"start":start, "end":end, "variation":{"type":variation,"std":std}})

def checkLocations(category, trend):
    # everywhere, or especially one place?
    if category == "low" or category == "high":
        #check especially: check percentages? what percentage of x range is low (50%)
        trendIndex = 0
        leftover = 0
        for i in range(len(times)-1):
            rangeStart = times[i]
            rangeEnd = times[i+1]
            rangeDuration = rangeEnd - rangeStart
            trendDuration = leftover

            while trendIndex < len(trend):
                #print 'hi'
                trendStart = trend[trendIndex]["start"]
                trendEnd = trend[trendIndex]["end"]
                duration = trendEnd - trendStart

                if (trend[trendIndex]["variation"] == category):
                    trendIndex = trendIndex + 1
                    if trendEnd > rangeEnd:
                        leftover = trendEnd - rangeEnd
                        trendDuration = trendDuration + (rangeEnd - trendStart)
                        break
                    else:
                        trendDuration = trendDuration + duration

            print trendDuration, rangeDuration
            print "percentage:" , (trendDuration / float(rangeDuration))

# check for beginning/end situation
# if inconclusive, check for most significant
# check if just overall bad/overall good
# flag patterns: +/-/+; +/-; +++
i = 0
variation = "normal"
while variation == "normal":
    variation = groups[i]["variation"]
    i = i + 1
    if i == len(groups):
        break

if overall_std < 15: #CHANGE TO 10
    checkLocations("low", trend)
elif overall_std > 30:
    checkLocations("high", trend)
else:
    pass
    checkLocations("normal", trend)


axes = plt.gca()
plt.show()
