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

def test_get_bsky_username():
    assert get_bsky_username("bsky:@klatz.co foo bar") == "klatz.co"
    # assert get_bsky_username("bsky: @klatz.co") == "klatz.co"
    # assert get_bsky_username("bsky: klatz.co") == "klatz.co"
    # assert get_bsky_username("bsky:klatz.co") == "klatz.co"
    # assert get_bsky_username("🦋 @klatz.co") == "klatz.co"
    # assert get_bsky_username("🦋@klatz.co") == "klatz.co"
    # assert get_bsky_username("🦋klatz.co") == "klatz.co"

def get_bsky_username(instr) -> str:
    # TODO look for DIDs too i guess
    # text = "bsky: foo bsky:foo"

    # pattern = r"bsky:\s*[A-Za-z]"
    pattern = r"bsky:\s*.*"

    matches = re.findall(pattern, instr)
    build = matches[0].replace("bsky","")

    if build[0] ==":": build = build.replace(":","")
    if build[0] ==" ": build = build.replace(" ","")

    build = build.split()[0]

    print(build)
    return build




def process_json(input_json=None):
    sample = '''[[{"id":"33333","name":"foouserdisplayname","username":"ian5v","created_at":"2015-01-24T20:50:17Z","description":"bsky:klatz.co","entities":{},"location":"usa","pinned_tweet_id":"33333","profile_image_url":"foo","protected":false,"url":"lol"},{"id":"3333","text":"pinned tweet text content","entities":{}}]]'''
    if input_json==None: input_json = sample

    eee = json.loads(input_json)
    for person_youre_following in eee:
        # two items in a list, first is the bio and second is the pinned tweet
        # TODO check bio
        bio = person_youre_following[0]
        pinned = person_youre_following[1]
        displayname = bio.get('name')
        username = bio.get('username')
        description = bio.get('description')

        if ( "bsky" in description ) :
            # print(description.split())
            pass

        if ( "bsky" in displayname ) :
            pass
            # print(displayname)

        bsky_username = get_bsky_username() # from bio

        session = atprototools.Session(os.environ.get("BSKY_USERNAME"), os.environ.get("BSKY_PASSWORD"))
        bsky_did = session.resolveHandle(bsky_username).json()
        profile_json = session.getProfile(bsky_did).json()

        # RESUME now i have the json containing profile content; parse it and render the bsky profile in html (just a link to the profile is fine to start)

        # TODO check pinned tweet
        # import pdb; pdb.set_trace()




async def handle(request):
    if request.method == 'POST':
        data = await request.post()
        print(data)
        twitter_username = data.get("name")
        ccc = data.get('text')
        # print(ccc)
        # print(type(ccc))
        # fff = StringIO(ccc)
        # print(fff)
        # print(type(fff))
        # reader = csv.reader(ccc.split('\n'), delimiter=",")
        # print(type(reader))
        # import pdb; pdb.set_trace()
        for row in reader:
            print(row)
        return web.Response(text=f"Data received: {data}")
    else:
        return web.Response(text="""
            <html>
                <body>
                    <a href="https://unflwrs.syfaro.com/">https://unflwrs.syfaro.com/</a>
                    <form method="post">
                        <label for="name">Paste the json from unflwrs:</label><br>
                        <textarea rows="5" cols="60" name="text" placeholder="">

                        [[{"id":"33333","name":"foouserdisplayname","username":"ian5v","created_at":"2015-01-24T20:50:17Z","description":"bsky:klatz.co","entities":{},"location":"usa","pinned_tweet_id":"33333","profile_image_url":"foo","protected":false,"url":"lol"},{"id":"3333","text":"pinned tweet text content","entities":{}}]]

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

process_json()
test_get_bsky_username()