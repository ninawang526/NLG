from database_init import db, Sessions, Users
import google.auth
import dateutil.parser
#from google.cloud import storage
import os
import pyrebase
import pytz
from datetime import datetime
import gzip
import json
os.system("mkdir errors")
# Firebase configurations
projectID  = "oraiapp-3da7c"
fbase_config = {"apiKey": "",
  "authDomain": "https://accounts.google.com/o/oauth2/auth",
  "databaseURL": "https://oraiapp-3da7c.firebaseio.com",
  "storageBucket": "",
  "serviceAccount": "app.json"
  }
# Initializes firebase using an ORM wrapper (pyrebase)
initialize_firebase = pyrebase.initialize_app(fbase_config)
# Fetches files from Firebase using autheticatiion details
firebase = initialize_firebase.database()

# Get time now as America/New York datetime object converted to a string
# Optionally subtract a number of days from today

def getDateEST(days_to_subtract=0):
    tz = pytz.timezone('America/New_York')
    if days_to_subtract == 0:
        return (datetime.now(tz)).strftime("%Y-%m-%d")
    return dateutil.parser.parse((datetime.now(tz)- timedelta(days=days_to_subtract)).strftime("%Y-%m-%d"))

def stringToDateConverter(date_inp):

    date = dateutil.parser.parse(date_inp)
    return date.replace(tzinfo=None)

database_dump_file_name = "/tmp/my-secure-file"

def downloadFile(filename=None):
    """
    Download a database dump from firebase
    """
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "app.json"
    credentials, project = google.auth.default()
    if credentials.requires_scopes:
      credentials = credentials.with_scopes(['https://www.googleapis.com/auth/devstorage.read_write'])
    storage_client = storage.Client(credentials=credentials,project=projectID)
    # bucket_name = 'my-new-bucket'
    from google.cloud.storage import Blob

    # client = storage.Client(project='my-project')
    bucket = storage_client.get_bucket('oraiapp-3da7c-backups')
    blob = None
    blobs = bucket.list_blobs(prefix=getDateEST())
    paths = [(x.path,x) for x in blobs if "data" in x.path ]
    paths.sort(reverse=True)
    blob = paths[0][1]

    with open(database_dump_file_name, 'wb') as file_obj:
        blob.download_to_file(file_obj)
    print ("Downloaded")

downloadFile()



def unzipAndSelectFirebaseData(dataset):
    all_data = {}
#
    with gzip.open(dataset,mode="rt") as data_file:
        all_data = json.load(data_file)


    return (all_data["sessions"],all_data["users"])

def sessionsPopulator(sessions):
    title_missing = open("errors/"+"No_title.txt",'w')

    api_missing = open("errors/"+"No_API.txt",'w')

    E_recomissing = open("errors/"+"No_Energy_reco.txt",'w')

    E_val_missing = open("errors/"+"No_Energy_value.txt",'w')

    Vocval_missing = open("errors/"+"No_vocal_variation.txt",'w')

    filler_loc_missing = open("errors/"+"No_filler_locations.txt",'w')

    filler_summary_missing = open("errors/"+"No_filler_summary,txt",'w')

    starttimes_missing = open("errors/"+"No_start_times.txt",'w')

    endtimes_missing = open("errors/"+"No_end_times,txt",'w')

    wpm_missing = open("errors/"+"No_WPM.txt","w")

    transcript_missing = open("errors/"+"No_wpm_transcript.txt","w")

    sessions_without_time = open("errors/"+"sessions_without_time.txt","w")

    no_total_time = open("errors/"+"no_total_time.txt","w")

    no_UID = open("errors/"+"no_uid.txt","w")



    for sid,session in sessions.items():

        try:
            if session["Final"] == False:

                continue
        except KeyError as e:
            continue

        session_data = {}

        try:
            session_data["Title"] = str(session["meta"]['title'])
        except KeyError as e:
            title_missing.write(sid+"\n")
            session_data["Title"] = "None"

        try:
            session_data["API"] = str(session["Apiversion"])
        except KeyError as e:
            api_missing.write(sid+"\n")
            session_data["API"] = ""

        try:
            session_data["E_Recommendation"] = str(session["Energy"]["Recommendation"])
        except KeyError as e:
            E_recomissing.write(sid +"\n")
            session_data["E_Recommedation"] = ""
        try:
            session_data["E_value"] = json.dumps(session['Energy']["Values"])
        except KeyError as e:
            E_val_missing.write(str(sid+"\n"))
            session_data["E_value"] = json.dumps({})

        session_data["vocal_variation"] = int(session["Energy"]["VocalVariation"])

        session_data["Error"] = str(session["Error"])


        session_data["Filler_reco"] = str(session["Fillers"]["Recommendation"])

        try:
            locations = []
            if len(session['Fillers']["Locations"]) > 0:
                for location in session['Fillers']["Locations"]:
                    locations.append(int(session['Fillers']["Locations"][location]))
            session_data["Filler_location"] = locations
        except KeyError as e:
            filler_loc_missing.write(sid +"\n")
            session_data["Filler_location"] = []

        try:
            session_data["Filler_summary"] = json.dumps(session['Fillers']["Summary"])
        except KeyError as e:
            filler_summary_missing.write(sid+"\n")
            session_data["Filler_summary"] = json.dumps({})

        session_data["Pauses"] = json.dumps(session['Pauses'])


        try:
            times = []
            if len(session["StartTimes"]) > 0:
                for time in session["StartTimes"]:
                    times.append(int(time))
            session_data["start_times"] = times
        except KeyError as e:
           starttimes_missing.write(sid+"\n")
           session_data["start_times"] = list([])


        try:
            times = []
            if len(session["EndTimes"]) > 0:
                for time in session["EndTimes"]:
                    times.append(int(time))
            session_data["end_times"] = times
        except KeyError as e:
           endtimes_missing.write(sid+"\n")
           session_data["end_times"] = list([])

        try:
            session_data["WPM_average"] = float(session["WPM"]["Average"])
        except KeyError as e:
            session_data["WPM_average"] = 0.0

        try:
            session_data["WPM_variation"] = json.dumps(session["WPM"]["WPM"])
        except KeyError as e:
            session_data["WPM_variation"] = json.dumps({})
            wpm_missing.write(sid+"\n")

        try:
            session_data["WPM_recommendation"] = str(session["WPM"]["Recommendation"])
        except KeyError as e:
            session_data["WPM_recommendation"] = ""
            wpm_missing.write(sid+"\n")


        try:
            words = []
            for word in session["Words"]:
                words.append(session["Words"][word])
            session_data["transcript_array"] = list(words)
            session_data["transcript_string"] = str(" ".join(words))
        except KeyError as e:
            session_data["transcript_array"] = ['']
            session_data["transcript_string"] = ""
            transcript_missing.write(sid+"\n")


        try:
            session_data["date"] = datetime.fromtimestamp(int(session["Timestamp"])).date()
        except KeyError as e:
            try:
                session_data["date"] = stringToDateConverter(session["meta"]["time"]).date()
            except KeyError as e:
                session_data["date"] = stringToDateConverter("1997-05-11T15:00:00.000Z").date()
            except ValueError as e:
                session_data["date"] = stringToDateConverter("1997-05-11T15:00:00.000Z").date()
        except ValueError as e:
            session_data["date"] = stringToDateConverter("1997-05-11T15:00:00.000Z").date()




        try:
            for word in session["EndTimes"]:
                None
            session_data["total_time"] = float(session["EndTimes"][word])
        except KeyError as e:
            no_total_time.write(sid+"\n")
            session_data["total_time"] = 0.0

        try:
            session_data["user_id"] = str(session["UID"])
        except KeyError as e:
            no_UID.write(sid+"\n")
            session_data["user_id"] = ""

        try:
            session_data["prompt-id"] = str(session["Prompt"])
        except KeyError as e:
            session_data["prompt-id"] = ""


# dict_keys(['Apiversion', 'Energy', 'Error', 'Fillers', 'Final', 'Pauses',
#  'Projection', 'TranscriptClarity', 'UID', 'WPM', 'EndTimes', 'StartTimes',
#  'Words', 'meta', 'public'])


        single_Session = Sessions(session_id = sid, title = session_data["Title"], total_time = session_data["total_time"],
                                user_id = session_data["user_id"], session_date = session_data["date"],
                                api_version = session_data["API"], energy_recommendation = session_data["E_Recommendation"],
                                energy_values = session_data["E_value"], vocal_variation = session_data["vocal_variation"],
                                error = session_data["Error"], fillers_recommendation = session_data["Filler_reco"],
                                fillers_location = session_data["Filler_location"], fillers_summary = session_data["Filler_summary"],
                                pauses = session_data["Pauses"], start_times = session_data["start_times"],
                                end_times = session_data["end_times"], wpm_average = session_data["WPM_average"],
                                wpm_recommendation = session_data["WPM_recommendation"], wpm_variation = session_data["WPM_variation"],
                                transcript_array = session_data["transcript_array"], transcript_string = session_data["transcript_string"],
                                prompt_id = session_data["prompt-id"])



        db.session.add(single_Session)
        db.session.commit()
    print("Session Populating finished")


def usersPopulator(users):

    noname = open("errors/"+"noname.txt","w")

    noCreatedAt = open("errors/"+"noCreatedAt.txt","w")

    noLast = open("errors/"+"noLastSignIn.txt","w")

    notz = open("errors/"+"notimezonez.txt","w")

    nogen = open("errors/"+"nogender.txt","w")

    noemail = open("errors/"+"noemail.txt","w")

    noage = open("errors/"+"noage.txt","w")

    noprovider = open("errors/"+"noprovider.txt","w")

    noprofession = open("errors/"+"noprofession.txt","w")

    for uniqueid, data in users.items():
        user_data = {}


        try:
            user_data["name"] = data["userInfo"]["name"]
        except KeyError as e:
            noname.write(uniqueid+"\n")
            user_data["name"] = ""

        try:
            user_data["created_at"] = stringToDateConverter(data["fbaseMeta"]["metadata"]["createdAt"]).date()
        except KeyError as e:
            user_data["created_at"] = stringToDateConverter("1997-05-11T15:00:00.000Z").date()



        try:
            dates = []

            if len(data["performance"]["sessions"]) > 1:
                for session in data["performance"]["sessions"].keys():
                    try:
                        dates.append(stringToDateConverter(data['performance']['sessions'][session]['meta']['time']).date())
                    except ValueError as e:
                        continue
                if len(dates) > 0:
                    user_data["last_sign_in"] = max(dates)
                else:
                    user_data["last_sign_in"] =  stringToDateConverter(data["fbaseMeta"]["metadata"]["lastSignedInAt"]).date()
            else:
                user_data["last_sign_in"] =  stringToDateConverter(data["fbaseMeta"]["metadata"]["lastSignedInAt"]).date()
        except KeyError as e:
                user_data["last_sign_in"] =  stringToDateConverter(data["fbaseMeta"]["metadata"]["lastSignedInAt"]).date()


        try:
            user_data["timezone"] = data["userInfo"]["timeZone"]
        except KeyError as e:
            notz.write(uniqueid+"\n")
            user_data["timezone"] = ""

        try:
            user_data["email"] = data["userInfo"]["email"]
        except KeyError as e:
            noemail.write(uniqueid+"\n")
            user_data["email"] = ""

        try:
            user_data["gender"] = data["userInfo"]["gender"]
        except KeyError as e:
            nogen.write(uniqueid+"\n")
            user_data["gender"] = ""

        try:
            user_data["provider"] = data["fbaseMeta"]["providerData"]["0"]["providerId"]
        except KeyError as e:
            noprovider.write(uniqueid+"\n")
            user_data["provider"] = ""

        try:
            user_data["age"] = data["userInfo"]["age"]
        except KeyError as e:
            noage.write(uniqueid+"\n")
            user_data["age"] = 0

        try:
            user_data["profession"] = data["userInfo"]["profession"]
        except KeyError as e:
            noprofession.write(uniqueid+"\n")
            user_data["profession"] = ""


        user = Users(uid = uniqueid, name = user_data["name"], created_at = user_data["created_at"],
                    last_sign_in = user_data["last_sign_in"], email = user_data["email"],
                    provider = user_data["provider"], timezone = user_data["timezone"],
                    gender = user_data["gender"], age = user_data["age"], profession = user_data["profession"])


        db.session.add(user)
        db.session.commit()
    print("Users finished populating")

data = unzipAndSelectFirebaseData(database_dump_file_name)

sessionsPopulator(data[0])
usersPopulator(data[1])
