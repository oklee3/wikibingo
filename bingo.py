from flask import Flask, render_template, jsonify, redirect, url_for, request
import asyncio
import aiohttp
from urllib.parse import unquote
import json
import random
import openai
import os
from groq import Groq
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
client = Groq(api_key = os.environ.get("GROQ_API_KEY"))

def generate_fake_title_groq():
    response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "Generate one fake but realistic Wikipedia article title. It should sound plausible and fit naturally among real articles. Randomly choose if it's about a person, place, event, or concept. Keep it short and don't include any description — just the title. Never do something using the word 'of'"
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
