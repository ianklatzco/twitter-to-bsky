from aiohttp import web
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

"""put twitter username in website
 it chromedrivers your twitter account
 yanks all the following usernames + bios
 queries bsky for matching names
 returns and displays them in webui so you can click them in new tabs to follow
 (bonus) hide the ones you've clicked"""

async def handle(request):
    if request.method == 'POST':
        data = await request.post()
        print(data)
        return web.Response(text=f"Data received: {data}")
    else:
        return web.Response(text="""
            <html>
                <body>
                    <form method="post">
                        <label for="name">Name:</label><br>
                        <input type="text" id="name" name="name" value="klatz.co"><br>
                        <input type="submit" value="Submit">
                    </form> 
                </body>
            </html>
        """,
        content_type="text/html"
        )

app = web.Application()
app.add_routes([web.get('/', handle),
                web.post('/', handle)])

# content type text/html

web.run_app(app)
