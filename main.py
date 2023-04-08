import json, requests, datetime, time

import sys

# TODO 9 apr: 
# learned: cant fake timestamps anymore bc of how ui rendering works

# dev hack to import the local
sys.path = ['/home/user/atprototools'] + sys.path
from atprototools import *
# import atprototools as atpt


TWEETS_JS_PATH = "./data/tweets.js"

ATP_HOST = "https://bsky.social"
ATP_AUTH_TOKEN = ""


f = open(TWEETS_JS_PATH)
c = f.read().replace("window.YTD.tweets.part0 = ", "")
tweets = json.loads(c)

# def login():
#     data = {"identifier":USERNAME, "password":PASSWORD}
#     resp = requests.post(
#         ATP_HOST + "/xrpc/com.atproto.server.createSession",
#         json=data
#     )

#     global ATP_AUTH_TOKEN
#     ATP_AUTH_TOKEN = resp.json().get('accessJwt')
#     if ATP_AUTH_TOKEN == None:
#         raise ValueError("no access token")

def poast(poastcontent, timestamp):
    poastcontent = poastcontent
    timestamp = datetime.datetime.now(datetime.timezone.utc) # - datetime.timedelta(1)
    timestamp = timestamp.isoformat().replace('+00:00', 'Z')
    headers = {"Authorization": "Bearer " + ATP_AUTH_TOKEN}
    # can u post as other DIDs? that would be interesting
    # this is the bskies DID
    # no, you get a 401 auth required if you try posting w/ another's DID
    data = {
        "collection":"app.bsky.feed.post",
        "$type": "app.bsky.feed.post",
        "repo":"did:plc:2yk6xmkpavh4x3eicoa4bjjq",
        "record":{
            "$type": "app.bsky.feed.post",
            "createdAt":timestamp,
            "text":poastcontent,
            }
        }
    resp = requests.post(
        ATP_HOST + "/xrpc/com.atproto.repo.createRecord",
        json=data,
        headers = headers
    )
    return resp


# resp = poast("testpoast")
# print(resp)
# print(resp.content)
# import pdb; pdb.set_trace()

def upload_old_tweets():
    print(str(len(tweets)) + "tweets to skootify")
    for index, tweet in enumerate(tweets):
        tweet = tweet.get("tweet")
        skoot_text = tweet.get("full_text")

        if tweet.get("retweeted") == True: continue
        if skoot_text[0] == "@": continue
        if skoot_text[0:4] == "RT @": continue
        
        date_string = tweet.get("created_at")
        date_format = "%a %b %d %H:%M:%S %z %Y"
        parsed_date = datetime.datetime.strptime(date_string, date_format)
        assert(str(type(parsed_date)) == "<class 'datetime.datetime'>")
        poast(skoot_text, parsed_date)
        print("{} of {} at {} skooted {}".format(index, len(tweets), parsed_date, skoot_text))
        time.sleep(.1)

# def get_latest_skoot():
#     headers = {"Authorization": "Bearer " + ATP_AUTH_TOKEN}
#     resp = requests.get(
#         ATP_HOST + "/xrpc/app.bsky.feed.getAuthorFeed?actor=ik.bsky.social&limit=1",
#         headers = headers
#     )
#     return resp

def get_skoot_text_from_feed(skoot):
    return skoot.get('feed')[0].get('post').get('record').get('text')

# def delete_skoot(did,rkey):
#     data = {"collection":"app.bsky.feed.post","repo":"did:plc:{}".format(did),"rkey":"{}".format(rkey)}
#     headers = {"Authorization": "Bearer " + ATP_AUTH_TOKEN}
#     resp = requests.post(
#         ATP_HOST + "/xrpc/com.atproto.repo.deleteRecord",
#         json = data,
#         headers=headers
#     )
#     return resp

def wipe_profile():
    acct = "ik.bsky.social"
    did = "2yk6xmkpavh4x3eicoa4bjjq"
    testpost_question_mark = get_latest_skoot(acct)
    text = testpost_question_mark.json().get('feed')[0].get('post').get('record').get('text')

    while (text != "testpoast"):
        skoot = get_latest_skoot(acct).json()
        text = get_skoot_text_from_feed(skoot)
        if (text == "testpoast"): continue
        rkey = skoot.get('feed')[0].get('post').get('uri').split('/')[-1]
        print("attempting to delete {}".format(text))
        resp = delete_skoot(did, rkey)
        print(resp)
        # import pdb; pdb.set_trace()
 
def main():
    # login()
    login(USERNAME, PASSWORD)
    wipe_profile()
    # upload_old_tweets()
    # wipe_profile()

main()
