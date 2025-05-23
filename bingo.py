from flask import Flask, render_template, jsonify, redirect, url_for, request
import asyncio
import aiohttp
from urllib.parse import unquote
import json
import random
import openai
import os
from groq import Groq

app = Flask(__name__)
client = Groq(api_key = os.environ.get("GROQ_API_KEY"))

def generate_fake_title_groq():
    response = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Generate a realistic-sounding Wikipedia article title about a fictional event, person, or place. Do not put any events that take place in the future, and avoid too detailed description."
            "The title should closely resemble real Wikipedia article titles in tone and style. Avoid sounding fantastical or obviously fake. Limit 10 words, ideally less. Output only your title, nothing else."
        }
    ],
    model="gemma2-9b-it",
    )
    return response.choices[0].message.content


async def get_wikipedia_page():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://en.wikipedia.org/wiki/Special:Random", allow_redirects=True) as response:
            title = unquote(str(response.url).split("/")[-1].replace("_", " "))
            return {"title": title}

async def get_random_wikipedia_pages(n):
    tasks = [get_wikipedia_page() for _ in range(n)]
    return await asyncio.gather(*tasks)

def get_pages_sync(n_total=25, num_fakes=5):
    num_real = n_total - num_fakes
    real_titles = asyncio.run(get_random_wikipedia_pages(num_real))

    real_wrapped = [{"title": item["title"], "is_fake": False} for item in real_titles]

    fake_titles = [{"title": generate_fake_title_groq(), "is_fake": True} for _ in range(num_fakes)]

    all_titles = real_wrapped + fake_titles
    random.shuffle(all_titles)
    return all_titles


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/board')
def board():
    pages = get_pages_sync(25)
    return render_template('board.html', pages=pages)

@app.route('/new-board')
def new_board():
    pages = get_pages_sync(25)
    return jsonify(pages)

if __name__ == '__main__':
    app.run(debug=True)
