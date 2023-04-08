import json, datetime, time, os

import atprototools as atpt
# import sys; sys.path = ['/home/user/atprototools'] + sys.path # dev hack to import the local

TWEETS_JS_PATH = "./data/tweets.js"

USERNAME = os.environ.get("BSKY_USERNAME")
PASSWORD = os.environ.get("PASSWORD")


f = open(TWEETS_JS_PATH)
c = f.read().replace("window.YTD.tweets.part0 = ", "")
tweets = json.loads(c)

def upload_old_tweets():
    print(str(len(tweets)) + "tweets to skootify")
    for index, tweet in enumerate(tweets):
        tweet = tweet.get("tweet")
        skoot_text = tweet.get("full_text")

        if tweet.get("retweeted") == True: continue
        if skoot_text[0:4] == "RT @": continue
        if skoot_text[0] == "@": continue # don't skoot mentions or replies
        
        date_string = tweet.get("created_at")
        date_format = "%a %b %d %H:%M:%S %z %Y"
        parsed_date = datetime.datetime.strptime(date_string, date_format)
        assert(str(type(parsed_date)) == "<class 'datetime.datetime'>")
        atpt.post_skoot(skoot_text, parsed_date)
        print("{} of {} at {} skooted {}".format(index, len(tweets), parsed_date, skoot_text))
        time.sleep(.1)

def get_skoot_text_from_feed(skoot):
    return skoot.get('feed')[0].get('post').get('record').get('text')

def wipe_profile():
    testpost_question_mark = atpt.get_latest_skoot(USERNAME)
    text = testpost_question_mark.json().get('feed')[0].get('post').get('record').get('text')

    while (text != "testpoast"):
        skoot = atpt.get_latest_skoot(USERNAME).json()
        text = get_skoot_text_from_feed(skoot)
        if (text == "testpoast"): continue
        rkey = skoot.get('feed')[0].get('post').get('uri').split('/')[-1]
        print("attempting to delete {}".format(text))
        resp = atpt.delete_skoot(atpt.DID, rkey)
        print(resp)
        # import pdb; pdb.set_trace()
 
def main():
    atpt.login(USERNAME, PASSWORD)
    # wipe_profile()
    upload_old_tweets()

main()
