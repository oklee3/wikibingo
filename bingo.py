from flask import Flask, render_template, jsonify
import asyncio
import aiohttp
from urllib.parse import unquote

app = Flask(__name__)

async def get_wikipedia_page():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://en.wikipedia.org/wiki/Special:Random", allow_redirects=True) as response:
            return unquote(str(response.url).split("/")[-1].replace("_", " "))

async def get_random_wikipedia_pages(n):
    tasks = [get_wikipedia_page() for _ in range(n)]
    return await asyncio.gather(*tasks)

def get_pages_sync(n):
    return asyncio.run(get_random_wikipedia_pages(n))

@app.route('/')
def index():
    titles = get_pages_sync(25)
    return render_template('home.html', titles=titles)

@app.route('/new-board')
def new_board():
    titles = get_pages_sync(25)
    return jsonify(titles)

if __name__ == '__main__':
    app.run(debug=True)
