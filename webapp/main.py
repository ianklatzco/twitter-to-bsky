from aiohttp import web
import csv
from io import StringIO,BytesIO
import json
import re
import atprototools
import requests
import datetime
import os
from string import ascii_letters, digits

ATP_HOST = "https://bsky.social"
DISCORD_WEBHOOK_URL = "https://disc"+"ord.com/api/webhooks/109577989"+"9303788686/VqsbHiWNLfQcETLYjuAsFFZ-7DMaJ3GznYQMZWJ3"+"EUw9qxsbGxB71KyZbypejzQUwUcC"

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
        return str(self.twitter) + "," + str(self.bsky)

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
            print(username) # twitter username
            bfly_index = description.index("🦋") + 1
            entities = entities.get('description').get('urls')
            for ent in entities:
                start = ent.get('start')
                if start == bfly_index:
                    bsky_username = ent.get('display_url')
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
    if request.method == 'GET':
        resp = requests.post(DISCORD_WEBHOOK_URL, json={'content':'somebody opened the link!'}, headers={'Content-Type': 'application/json'})
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
                        <li>get the JSON export of the people you follow from 
                            <a href="https://unflwrs.syfaro.com/">https://unflwrs.syfaro.com/</a>
                        </li>
                        <li>unzip following.json somewhere</li>
                        <li>upload following.json</li>
                    </ol>
                    <form action="/upload" method="post" enctype="multipart/form-data">
                        <input type="file" name="file">
                        <input type="submit" value="get your twitter friends' bsky handles">
                    </form>

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

async def handle_upload(request):
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

    rows = []
    for user in list_of_user_profiles_on_bsky:
        bsky_handle = user.bsky.get('handle')
        rows.append( f'''
            <tr>
                <td> {user.twitter[0].get('username')}</td>
                <td> <a target="_blank" href="https://staging.bsky.app/profile/{bsky_handle}">🦋{bsky_handle}</a> </td>
            </tr>
            '''
        )
    rows2 = []
    rows2.append( f'''
        <tr>
            <td> coderobe</td>
            <td> <a target="_blank" href="https://staging.bsky.app/profile/codero.be">🦋codero.be</a> </td>
        </tr>
        '''
    )
    rows2.append( f'''
        <tr>
            <td> ian5v</td>
            <td> <a target="_blank" href="https://staging.bsky.app/profile/klatz.co">🦋klatz.co</a> </td>
        </tr>
        '''
    )
    rows2.append( f'''
        <tr>
            <td>lucyluwang</td>
            <td> <a target="_blank" href="https://staging.bsky.app/profile/lucylw.bsky.social">🦋lucylw.bsky.social</a> </td>
        </tr>
        '''
    )
    rows2.append( f'''
        <tr>
            <td>willscott</td>
            <td> <a target="_blank" href="https://staging.bsky.app/profile/wills.co.tt">🦋wills.co.tt</a> </td>
        </tr>
        '''
    )
    rows2.append( f'''
        <tr>
            <td> s3krit</td>
            <td> <a target="_blank" href="https://staging.bsky.app/profile/punk.place">🦋punk.place</a> </td>
        </tr>
        '''
    )
    rows2.append( f'''
        <tr>
            <td> blisstweeting</td>
            <td> <a target="_blank" href="https://staging.bsky.app/profile/blisstweeting.ingroup.social">🦋blisstweeting.ingroup.social</a> </td>
        </tr>
        '''
    )
    rows2.append( f'''
        <tr>
            <td>RobertHaisfield</td>
            <td> <a target="_blank" href="https://staging.bsky.app/profile/robhaisfield.com">🦋robhaisfield.com</a> </td>
        </tr>
        '''
    )
    rows2.append( f'''
        <tr>
            <td>mr_ligi</td>
            <td> <a target="_blank" href="https://staging.bsky.app/profile/ligi.de">🦋ligi.de</a> </td>
        </tr>
        '''
    )
    rows2.append( f'''
        <tr>
            <td>stephengraves</td>
            <td> <a target="_blank" href="https://staging.bsky.app/profile/stephengraves.bsky.social">🦋stephengraves.bsky.social</a> </td>
        </tr>
        '''
    )


    # Data received: {list_of_user_profiles_on_bsky}
    return web.Response(text=f"""
    <h4> your friends! (there might not be any.... sorry.....) </h4>
        <table>
            <tr>
                <th>twitter</th>
                <th>bsky</th>
            </tr>
            """ + "\n".join(rows) + "</table><hr>" +
            """<br> 
            <h4>guestbook!</h4>
            <table>
            <tr>
                <th>twitter</th>
                <th>bsky</th>
            </tr>
            """ + "\n".join(rows2) + "</table>" +

            '''
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
            ''' + 

            "<br> <h3> this is a work in progress! please tell me about any bugs by replying to the thread <a target='_blank' href='https://staging.bsky.app/profile/klatz.co/post/3jt6mh7imkv2z'>here!</a>"
            "<br><br><a href='/'>go back</a>" 
    ,content_type="text/html")

async def handle_testsetup(request):
    if request.method == 'POST':
        data = await request.post()
        uu = User()
        uu.twitter = data.get('twitterhandle')
        uu.bsky = data.get('blueskyhandle')
        for c in uu.twitter:
            if c not in (ascii_letters + digits + "." + "@"):
                return web.Response(text="ascii letters + numbers only pls")
        for c in uu.bsky:
            if c not in (ascii_letters + digits + "." + "@"):
                return web.Response(text="ascii letters + numbers only pls")
        # username = data.get('twitterhandle').replace("@","")
        # do a selenium
        resp = requests.post(DISCORD_WEBHOOK_URL, json={'content':uu.twitter + ',' + uu.bsky}, headers={'Content-Type': 'application/json'})


        rows = []
        list_of_user_profiles_on_bsky = [uu]
        for user in list_of_user_profiles_on_bsky:
            bsky_handle = user.bsky
            rows.append( f'''
                <tr>
                    <td> {user.twitter}</td>
                    <td> <a target="_blank" href="https://staging.bsky.app/profile/{bsky_handle}">🦋{bsky_handle}</a> </td>
                </tr>
                '''
            )
        rows.append( f'''
            <tr>
                <td>arcalinea</td>
                <td> <a target="_blank" href="https://staging.bsky.app/profile/jay.bsky.social">🦋jay.bsky.social</a> </td>
            </tr>
            '''
        )
        rows.append( f'''
            <tr>
                <td> ian5v</td>
                <td> <a target="_blank" href="https://staging.bsky.app/profile/klatz.co">🦋klatz.co</a> </td>
            </tr>
            '''
        )
        rows.append( f'''
            <tr>
                <td>mr_ligi</td>
                <td> <a target="_blank" href="https://staging.bsky.app/profile/ligi.de">🦋ligi.de</a> </td>
            </tr>
            '''
        )
        rows.append( f'''
            <tr>
                <td>stephengraves</td>
                <td> <a target="_blank" href="https://staging.bsky.app/profile/stephengraves.bsky.social">🦋stephengraves.bsky.social</a> </td>
            </tr>
            '''
        )


        # Data received: {list_of_user_profiles_on_bsky}
        return web.Response(text=f"""
            <h3>guestbook</h3>
            <table>
                <tr>
                    <th>twitter</th>
                    <th>bsky</th>
                </tr>
                """ + "\n".join(rows) + "</table>" +
                "<a href='/'>go back</a>"

        ,content_type="text/html")

        return web.Response(text=f"""
        yay! <a href="/">go back</a>
        """
        ,content_type="text/html")

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
main()