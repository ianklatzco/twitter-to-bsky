import json, datetime, time, os, html, re

import atprototools
# import sys; sys.path = ['/home/user/atprototools'] + sys.path # dev hack to import the local

TWEETS_JS_PATH = "./data/tweets.js"
DATA_PATH = "./data"

USERNAME = os.environ.get("BSKY_USERNAME")
PASSWORD = os.environ.get("PASSWORD")

print("Opening tweets json...")
f = open(TWEETS_JS_PATH, encoding="utf8")
c = f.read().replace("window.YTD.tweets.part0 = ", "")
twitter_data_date_format = "%a %b %d %H:%M:%S %z %Y"
tweets = sorted(json.loads(c), key=lambda x: datetime.datetime.strptime(x['tweet']['created_at'], twitter_data_date_format))

def upload_old_tweets():
    global atsession
    print(str(len(tweets)) + "tweets to blootify")
    for index, tweet in enumerate(tweets):
        tweet = tweet.get("tweet")
        tweet_media_path = None
        bloot_text = html.unescape(tweet.get("full_text"))
        date_string = tweet.get("created_at")
        parsed_date = datetime.datetime.strptime(date_string, twitter_data_date_format)
        assert(str(type(parsed_date)) == "<class 'datetime.datetime'>")

        print("{:05}/{:05} {} from {} is:\n\t{}".format(index+1, len(tweets), tweet.get("id"), parsed_date, bloot_text))

        if tweet.get("retweeted") == True:
            print("\t⏭️ Retweeting doesn't make sense, skipping")
            continue
        if bloot_text[0:4] == "RT @":
            print("\t⏭️ Retweeting doesn't make sense, skipping")
            continue
        if bloot_text[0] == "@":
            print("\t⏭️ Mentions or replies don't make sense, skipping")
            continue
        if tweet.get("entities").get("media") != None:
            if len(tweet.get("entities").get("media")) == 1:
                print("\t🖼️ Contains media")
                media_metadata = tweet.get("entities").get("media")[0]
                bloot_text = re.sub((" ?" + re.escape(media_metadata.get("url"))), "", bloot_text)
                print("\t\tUpdated text = {}".format(bloot_text))
                tweet_media_path = "{0}/tweets_media/{1}-{2}".format(DATA_PATH, tweet.get("id"), str(media_metadata.get("media_url")).split("/")[-1])
                print("\t\tImage path to upload = {}".format(tweet_media_path))
            else:
                print("⏭️ Multiple photos not implemented (ToDo), skipping")
                continue
        if tweet.get("entities").get("urls") != None and len(tweet.get("entities").get("urls")) > 0:
            print("\t🔗 Contains {} url(s)".format(len(tweet.get("entities").get("urls"))))
            urls = tweet.get("entities").get("urls")
            for url_index, url in enumerate(urls):
                if "x.com" in str(url.get("expanded_url")):
                    old_id = str(url.get("expanded_url").split("/")[-1])
                    old_tweet = [x for x in tweets if x['tweet']['id'] == old_id]
                    if old_tweet:
                        print("\t\t📯 {}/{} Contains own tweet url".format(url_index+1, len(tweet.get("entities").get("urls"))))
                        bloot_text = bloot_text.replace(url.get("url"), "\n\nRT {0}: {1}".format(USERNAME, old_tweet[0].get('tweet').get('full_text')))
                    else:
                        print("\t\t📯 {}/{} Contains foreign tweet url".format(url_index+1, len(tweet.get("entities").get("urls"))))
                        bloot_text = bloot_text.replace(url.get("url"), url.get("expanded_url"))
                else:
                    print("\t\t🔗 {}/{} Contains url".format(url_index+1, len(tweet.get("entities").get("urls"))))
                    bloot_text = bloot_text.replace(url.get("url"), url.get("expanded_url"))
            print("\tUpdated text = {}".format(bloot_text))
        
        atsession.postBloot(postcontent=bloot_text, image_path=tweet_media_path, timestamp=parsed_date)
        print("\t\t📤✅ blooted")
        time.sleep(.05)

def get_bloot_text_from_feed(bloot):
    return bloot.get('feed')[0].get('post').get('record').get('text')

def wipe_profile():
    global atsession
    print("Getting latest bloot...")
    latest_post = atsession.getLatestBloot(accountname=USERNAME)
    did_transformed = atsession.DID.split(":")[-1]
    print("DID = {}...".format(did_transformed[:4]))

    while ( latest_post.ok and latest_post.json().get('feed') != None and len(latest_post.json().get('feed')) == 1):
        id = latest_post.json().get('feed')[0].get('post').get('uri').split('/')[-1]
        text = get_bloot_text_from_feed(latest_post.json())
        print("attempting to delete {} with text {}".format(id, text)) 
        resp = atsession.deleteBloot(did=did_transformed, rkey=id)
        print(resp)

        print("Getting latest bloot...")
        latest_post = atsession.getLatestBloot(accountname=USERNAME)

    print("No more bloots to delete")


def warning():
    response = ""
    print("\nWARNING: Unless you have very few followers,")
    print("""\n*** this tool will SPAM THE TIMELINES of everyone who follows you when you upload your old tweets. ***""")
    print("""\n*** this tool will SPAM THE TIMELINES of everyone who follows you when you upload your old tweets. ***""")
    print("""\n*** this tool will SPAM THE TIMELINES of everyone who follows you when you upload your old tweets. ***\n""")
    print("It is recommended that you do not run this tool unless your account is brand new.\n")
    print("Please type [I UNDERSTAND] this will spam others' timelines.")
    response = input("Type [I UNDERSTAND]: ")
    if response != "I UNDERSTAND":
        print("Exiting....")
        import sys; sys.exit()
 

warning()
print("Logging in...")
atsession = atprototools.Session(username=USERNAME, password=PASSWORD)
#wipe_profile()
upload_old_tweets()
