

'''
    forgive me for this cursed code
    for i was sick and cold and lacking for bread
    i promise i'll refactor things nicely
    if only you might send me a pr and help me tidy?
    💙
'''


from functools import reduce
import sys
from aiohttp import web
import csv
from io import StringIO, BytesIO
import json
import re
import atprototools
import requests
import datetime
import os
from parse_json import parse_json
from string import ascii_letters, digits
from typing import List

ATP_HOST = "https://bsky.social"
DISCORD_WEBHOOK_URL = "https://disc"+"ord.com/api/webhooks/109577989" + \
    "9303788686/VqsbHiWNLfQcETLYjuAsFFZ-7DMaJ3GznYQMZWJ3"+"EUw9qxsbGxB71KyZbypejzQUwUcC"

"""put twitter username in website
 yanks all the following usernames + bios
 queries bsky for matching names
 returns and displays them in webui so you can click them in new tabs to follow
 (bonus) hide the ones you've clicked"""

# do we need descriptions here?
# we don't need to store the REST ID if we're not trying to keep a mapping


class TwitterProfile():
    def __init__(self, username: str, displayname: str):
        self.username: str = username
        self.displayname: str = displayname

    def __repr__(self) -> str:
        return str(self.username) + "," + str(self.displayname)

# will put more stuff later??


class BskyProfile():
    def __init__(self, handle: str):
        self.username: str = handle

    def __repr__(self) -> str:
        return str(self.username)


class User():
    def __init__(self, twitter: TwitterProfile, bsky: BskyProfile):
        self.twitter = twitter
        self.bsky = bsky

    def __repr__(self):
        return str(self.twitter) + "," + str(self.bsky)


guestbook: List[User] = [
    User(TwitterProfile('arcalinea', 'Jay Graber'),
         BskyProfile('jay.bsky.team')),
    User(TwitterProfile('coderobe', 'Mara 🕊️'),
         BskyProfile('codero.be')),
    User(TwitterProfile('ian5v', 'Ian Klatzco'),
         BskyProfile('klatz.co')),
    User(TwitterProfile('lucyluwang', 'Lucy Lu Wang'),
         BskyProfile('lucylw.bsky.social')),
    User(TwitterProfile('willscott', 'willscott'),
         BskyProfile('wills.co.tt')),
    User(TwitterProfile('s3krit', 's3krit'),
         BskyProfile('punk.place')),
    User(TwitterProfile('blisstweeting', 'Phil'),
         BskyProfile('blisstweeting.ingroup.social')),
    User(TwitterProfile('RobertHaisfield', 'Rob Haisfield'),
         BskyProfile('robhaisfield.com')),
    User(TwitterProfile('mr_ligi', 'ligi ☮️🌍🚲🌳🍵🎶🌶🔥🖖'),
         BskyProfile('ligi.de')),
    User(TwitterProfile('stephengraves', 'stephengraves.eth'),
         BskyProfile('stephengraves.bsky.social')),
    User(TwitterProfile('H_H_H_H_H_H_H_7', '𝙝⁷ | 하세 🏳️‍⚧️'),
         BskyProfile('heartade.bsky.social')),
    User(TwitterProfile('markusmoetz', 'makke'),
         BskyProfile('markus.bsky.social')),
    User(TwitterProfile('connerdelights', 'Andrew Conner'),
         BskyProfile('andrewconner.com')),
]


def test_get_bsky_username():
    sample_text = "Hello! This is supposed to be a twitter profile text. " + \
        "It also mentions bsky without being a username and " + \
        "even has a link to bsky.app on the profile. " + \
        "The user happens to like 🦋 as well and has a link to " +\
        "gist.github.com on their profile."
    sample_usernames = ["heartade.bsky.social", "klatz.co"]
    sample_tags = ["bsky:@", "bsky: @", "bsky:", "bsky: ", "bsky@", "bsky @", "bsky ",
                   "🦋:@", "🦋: @", "🦋:", "🦋: ", "🦋@", "🦋 @", "🦋 ", "🦋"]
    for sample_username in sample_usernames:
        for sample_tag in sample_tags:
            test_text = "{} {}{} {}".format(
                sample_text, sample_tag, sample_username, sample_text)
            print("testing: {}".format(test_text))
            assert get_bsky_username(test_text) == sample_username


def get_bsky_username(instr) -> str:
    # print("checking bsky username for {}".format(instr))
    # TODO look for DIDs too i guess
    # text = "bsky: foo bsky:foo"

    pattern = r"🦋[\s:@]*[^\s]+|bsky[\s:@]+[^\s]+"
    matches = re.findall(pattern, instr)

    if matches != []:
        print("matches: ")
        print(matches)
    if matches == []:
        return

    possible_handles = []
    for match in matches:
        # replace emoji with bsky: because it's easier to parse
        tmpstr: str = match.replace("🦋", "bsky:")
        # remove first occurence of bsky
        tmpstr = tmpstr.replace("bsky", "", 1)
        tokens = tmpstr.split()
        tokens = reduce(lambda x, y: x+y, map(lambda x: x.split(":"), tokens))
        tokens = reduce(lambda x, y: x+y, map(lambda x: x.split("@"), tokens))

        possible_handles += filter(lambda x: x.count(".")
                                   >= 1 and x[-1] != ".", tokens)

    print(possible_handles)
    return possible_handles[0]


# -> List[User]
def process_json(input_json: str) -> List[User]:
    candidates = parse_json(input_json)
    returnlist: List[User] = []
    for candidate in candidates:
        for candidate_handle in candidate.bsky_handle_candidate:
            returnlist.append(
                User(
                    TwitterProfile(candidate.name, candidate.screen_name),
                    BskyProfile(candidate_handle)
                )
            )
    return returnlist

async def handle(request):
    if request.method == 'GET':
        resp = requests.post(DISCORD_WEBHOOK_URL, json={
                             'content': 'somebody opened the link!'}, headers={'Content-Type': 'application/json'})
        # testdata = open("testdata.json", encoding='utf-8').read()

        return web.Response(text=f"""
            <html>
                <body>
                    <br><br><br><br>
                    <br><br><br><br>
                    <br><br><br><br>
                    <br><br><br><br>
                    <h3>(wip) website 2 follow ur twitter friends on bsky🦋</h3>

                    <ol>
                        <li>put 🦋your.bsky.handle in your twitter bio</li>
                        <li>get the JSON export of the people you follow using 
                            <a href="https://github.com/Heartade/get-bird-follows">get-bird-follows userscript</a>
                        </li>
                        <li>upload (your_twitter_handle).json</li>
                    </ol>
                    <form action="/upload" method="post" enctype="multipart/form-data">
                        <input type="file" name="file" accept=".json">
                        <input type="submit" value="get your twitter friends' bsky handles">
                    </form>

                    <!-- var e = document.querySelector("body > form > input[type=file]:nth-child(1)") -->
                    <!-- e.files[0] -->
                    <!-- on submit click, pop alert box if != following.json -->

                    <br><br><br><br>
                    <br><br><br><br>
                    <br><br><br><br>
                    <br><br><br><br>
                    this website does not store any of your data! you can check the <a href='https://github.com/ianklatzco/twitter-to-bsky'>source code</a> to make sure c:

                    <br><br><br><br>
                    
                    <!--
                    <h3>i want 2 test that my twitter bio is set up so my friends can find me</h3>
                    -->

                </body>
            </html>
        """,
                            content_type="text/html"
                            )


def generate_rows_of_users(list_of_user_profiles_on_bsky: List[User]) -> str:
    return "\n".join(
        map(lambda user: f'''
        <tr>
            <td>{user.twitter.displayname}</td>
            <td><a target="_blank" href="https://twitter.com/{user.twitter.username}">@{user.twitter.username}</td>
            <td><a target="_blank" href="https://staging.bsky.app/profile/{user.bsky.username}">🦋{user.bsky.username}</a></td>
        </tr>
    ''', list_of_user_profiles_on_bsky)
    )


def generate_table_of_users(list_of_user_profiles_on_bsky: List[User]) -> str:
    return f'''
    <table>
        <tr>
            <th>name</th>
            <th>twitter</th>
            <th>bsky</th>
        </tr>
        {generate_rows_of_users(list_of_user_profiles_on_bsky)}
    </table>
    '''


async def handle_upload(request):
    global guestbook
    reader = await request.multipart()
    field = await reader.next()
    filename = field.filename
    size = 0
    f = BytesIO()
    while True:
        chunk = await field.read_chunk()  # Read the next chunk of data
        if not chunk:
            break
        size += len(chunk)
        f.write(chunk)
    f.seek(0)
    ccc = f.read()
    f.close()
    ccc = ccc.decode('utf8')
    list_of_user_profiles_on_bsky = process_json(ccc)
    # return web.Response(text=f'{filename} uploaded successfully')

    # Data received: {list_of_user_profiles_on_bsky}
    return web.Response(text=f"""
    <h4> your friends! (there might not be any.... sorry.....) </h4>
    {generate_table_of_users(list_of_user_profiles_on_bsky)}
    <hr><br> 
    <h4>guestbook!</h4>
    {generate_table_of_users(guestbook)}
    <h3>i want to be added to the guestbook!</h3>
    <ol>
        <li>set your twitter bio to include 🦋yourusername.bsky.social</li>
        <li>put your twitter handle here</li>
        <li>click the button</li>
        <li>ian manually adds you when he wakes up</li>
    </ol>
    <form action="/testsetup" method="post">
        <!--
        <label for="checkbox-id">i want to be added to the guestbook</label>
        <input type="checkbox" id="checkbox-id" value="checkbox_value">
        -->
        <input type="text" name="twitterhandle" placeholder="your twitter" >
        <input type="text" name="blueskyhandle" placeholder="your bluesky" >
        <input type="submit" value="add me to the guestbook (so people can find me from this website)">
        <!--
        <input type="submit" value="check if this dinky lil' website can read ur twitter">
        -->
    </form>
    <br>
    <h3> this is a work in progress! please tell me about any bugs by replying to the thread <a target='_blank' href='https://staging.bsky.app/profile/klatz.co/post/3jt6mh7imkv2z'>here!</a>
    <br><br>
    <a href='/'>go back</a>
    """, content_type="text/html")


async def handle_testsetup(request):
    global guestbook
    if request.method == 'POST':
        data = await request.post()
        twitter_handle = data.get('twitterhandle')
        bsky_handle = data.get('blueskyhandle')
        uu = User(
            TwitterProfile(twitter_handle, ""),
            BskyProfile(bsky_handle)
        )
        
        for c in uu.twitter.username:
            if c not in (ascii_letters + digits + "_-.@"):
                return web.Response(text="only ascii alphabets, digits, _, -, ., and @ are allowed.")
        for c in uu.bsky.username:
            if c not in (ascii_letters + digits + "_-.@"):
                return web.Response(text="only ascii alphabets, digits, _, -, ., and @ are allowed.")
        # username = data.get('twitterhandle').replace("@","")
        # do a selenium
        resp = requests.post(DISCORD_WEBHOOK_URL, json={
                             'content': uu.twitter.username + ',' + uu.bsky.username}, headers={'Content-Type': 'application/json'})

        # do we store this somewhere
        guestbook = [uu] + guestbook

        # Data received: {list_of_user_profiles_on_bsky}
        return web.Response(text=f"""
            <h3>guestbook</h3>
            {generate_table_of_users(guestbook)}
            <a href='/'>go back</a>
            """, content_type="text/html")


def main():
    app = web.Application()
    app.add_routes([
        web.get('/', handle),
        web.post('/', handle),
        web.post('/upload', handle_upload),
        web.post('/testsetup', handle_testsetup)
    ])
    web.run_app(app)


# test_get_bsky_username()
if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 0:
        if args[0] == "--test-get-bsky-username":
            test_get_bsky_username()
    else:
        main()
