from functools import reduce
import sys
from aiohttp import web
import csv
from io import StringIO
import json
import re
import atprototools
import requests
import datetime
import os

ATP_HOST = "https://bsky.social"

"""put twitter username in website
 yanks all the following usernames + bios
 queries bsky for matching names
 returns and displays them in webui so you can click them in new tabs to follow
 (bonus) hide the ones you've clicked"""


class User():
    def __init__(self):
        self.twitter = ""
        self.bsky = ""

    def __repr__(self):
        return str(self.twitter) + str(self.bsky)


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


# -> List[users]
def process_json(input_json=None):
    sample = '''[[{"id":"33333","name":"foouserdisplayname","username":"ian5v","created_at":"2015-01-24T20:50:17Z","description":"bsky:klatz.co","entities":{},"location":"usa","pinned_tweet_id":"33333","profile_image_url":"foo","protected":false,"url":"lol"},{"id":"3333","text":"pinned tweet text content","entities":{}}]]'''
    if input_json == None:
        input_json = sample

    eee = json.loads(input_json)
    returnlist = []
    for person_youre_following in eee:

        # 1. check the handle to see if they just registered twitterhandle.bsky.social
        # 2.

        # two items in a list, first is the bio and second is the pinned tweet
        # TODO check bio
        bio_full_json = person_youre_following[0]
        pinned = person_youre_following[1]
        displayname = bio_full_json.get('name')
        username = bio_full_json.get('username')
        description = bio_full_json.get('description')

        if ("bsky" in description):
            # print(description.split())
            pass

        if ("bsky" in displayname):
            pass
            # print(displayname)

        bsky_username = get_bsky_username(description)  # from bio
        if bsky_username == None:
            continue

        session = atprototools.Session(os.environ.get(
            "BSKY_USERNAME"), os.environ.get("BSKY_PASSWORD"))
        bsky_did = session.resolveHandle(bsky_username).json().get('did')
        profile_json = session.getProfile(bsky_did).json()

        # RESUME now i have the json containing profile content; parse it and render the bsky profile in html (just a link to the profile is fine to start)

        user = User()
        user.twitter = person_youre_following
        user.bsky = profile_json
        returnlist.append(user)

        # TODO check pinned tweet
        # import pdb; pdb.set_trace()
    return returnlist


async def handle(request):
    if request.method == 'POST':
        data = await request.post()
        print(data)
        twitter_username = data.get("name")
        ccc = data.get('text')
        list_of_user_profiles_on_bsky = process_json(ccc)
        # print(ccc)
        # print(type(ccc))
        # fff = StringIO(ccc)
        # print(fff)
        # print(type(fff))
        # reader = csv.reader(ccc.split('\n'), delimiter=",")
        # print(type(reader))
        # import pdb; pdb.set_trace()
        # for row in reader:
        #     print(row)

        # generate some html

        '''
            <tr> twitter</tr>
            <tr> bsky</tr>
        '''

        rows = []
        for user in list_of_user_profiles_on_bsky:
            bsky_handle = user.bsky.get('handle')
            rows.append(f'''
                <tr>
                    <td>{user.twitter[0].get('username')}</td>
                    <td> <a target="_blank" href="https://staging.bsky.app/profile/{bsky_handle}">{bsky_handle}</a> </td>
                </tr>
                '''
                        )

        # Data received: {list_of_user_profiles_on_bsky}
        return web.Response(text=f"""
            <table>
                <tr>
                    <th>twitter</th>
                    <th>bsky</th>
                </tr>
                """ + "\n".join(rows) + "</table>", content_type="text/html")
    else:
        testdata = open("testdata.json", encoding='utf-8').read()
        return web.Response(text=f"""
            <html>
                <body>

                    <ol>
                        <li>get the JSON export of the people you follow from 
                            <a href="https://unflwrs.syfaro.com/">https://unflwrs.syfaro.com/</a>
                        </li>
                        <li>paste following.json into the box below</li>
                    </ol>
                    <form method="post">
                        <label for="name">Paste the json from unflwrs:</label><br>
                        <textarea rows="5" cols="60" name="text" placeholder="">

                        {testdata}

                        </textarea> <br>
                        <input type="submit" value="get your twitter friends' bsky handles">
                    </form> 
                </body>
            </html>
        """,
                            content_type="text/html"
                            )


def main():
    app = web.Application()
    app.add_routes([web.get('/', handle),
                    web.post('/', handle)])
    web.run_app(app)


# process_json()
# test_get_bsky_username()
if __name__ == "__main__":
    args = sys.argv[1:]
    if args[0] == "--test":
        test_get_bsky_username()
    else:
        main()
