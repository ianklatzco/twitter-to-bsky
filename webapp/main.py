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
    assert get_bsky_username("bsky:@klatz.co foo bar") == "klatz.co"
    # assert get_bsky_username("bsky: @klatz.co") == "klatz.co"
    # assert get_bsky_username("bsky: klatz.co") == "klatz.co"
    # assert get_bsky_username("bsky:klatz.co") == "klatz.co"
    # assert get_bsky_username("🦋 @klatz.co") == "klatz.co"
    # assert get_bsky_username("🦋@klatz.co") == "klatz.co"
    # assert get_bsky_username("🦋klatz.co") == "klatz.co"

def get_bsky_username(instr) -> str:
    # print("checking bsky username for {}".format(instr))
    # TODO look for DIDs too i guess
    # text = "bsky: foo bsky:foo"

    sumlist = []

    # pattern = r"bsky:\s*[A-Za-z]"
    pattern = r"🦋.*"
    # pattern = r"bsky:\s*.*"
    matches = re.findall(pattern, instr)

    # pattern = r"🦋.*"
    # matches + re.findall(pattern, instr)

    if matches != []:
        print("matches: ")
        print(matches)
    if matches == []: return

    build = matches[0].replace("bsky","")
    build = matches[0].replace("🦋","")
    print(build)

    if build[0] ==":": build = build.replace(":","")
    if build[0] ==" ": build = build.replace(" ","")
    if build[0] =="@": build = build.replace("@","")

    build = build.split()[0]

    print(build)
    return build


# -> List[users]
def process_json(input_json=None):
    sample = '''[[{"id":"33333","name":"foouserdisplayname","username":"ian5v","created_at":"2015-01-24T20:50:17Z","description":"bsky:klatz.co","entities":{},"location":"usa","pinned_tweet_id":"33333","profile_image_url":"foo","protected":false,"url":"lol"},{"id":"3333","text":"pinned tweet text content","entities":{}}]]'''
    if input_json==None: input_json = sample

    eee = json.loads(input_json)
    returnlist = []
    for person_youre_following in eee:
        bsky_username = None
        # if person_youre_following[0].get("username") != "ian5v":
        #     continue
        # import sys; sys.exit()
    
        # print(json.dumps(person_youre_following[0]))

        # 1. check the handle to see if they just registered twitterhandle.bsky.social
        # 2. 

        bio_full_json = person_youre_following[0]
        pinned = person_youre_following[1]

        displayname = bio_full_json.get('name')
        username = bio_full_json.get('username')
        description = bio_full_json.get('description')
        entities = bio_full_json.get("entities")

        if not description: continue 
        if not entities: continue
        if not entities.get('description'): continue

        if "🦋" not in description: continue

        print(username)

        # handles that are valid website (probably all of them) will get url shortened
        # entities -> description -> urls
        # entities -> url -> urls

        desc_urls = entities.get('description').get('urls')
        if not desc_urls: continue 

    
        # only one link in desc
        if len(desc_urls) == 1:
            bsky_username = entities.get('description').get('urls')[0].get('expanded_url')

        # TODO
        # 2+ links in desc
        if len(desc_urls) >= 2:
            # bsky_username = entities.get('description').get('urls')[0].get('expanded_url')
            pass
            # bfly_index = description.index("🦋")
            # bfly_index + 1 or + 2 where the url/handle starts

        if bsky_username == None: continue


        bsky_username = bsky_username.replace("http://",'').replace("https://","")
        print(bsky_username)

        # bsky_username = get_bsky_username(description) # from bio

        print('got here')
        session = atprototools.Session(os.environ.get("BSKY_USERNAME"), os.environ.get("BSKY_PASSWORD"))
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
        # print(data)
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
            rows.append( f'''
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
                """ + "\n".join(rows) + "</table>"
        ,content_type="text/html")
    else:
        # testdata = open("testdata.json", encoding='utf-8').read()
        testdata = open("phil-following.json", encoding='utf-8').read()
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

# test_get_bsky_username()
main()