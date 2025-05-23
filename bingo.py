from flask import Flask, render_template, jsonify, redirect, url_for, request
import asyncio
import aiohttp
from urllib.parse import unquote
import json
import random
import openai
import os
from groq import Groq
from anthropic import Anthropic
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
anthropic_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

TITLE_PROVIDER = os.environ.get("TITLE_PROVIDER", "groq")  # Default to groq if not specified

def generate_fake_titles_groq(num_titles=5):
    response = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Generate 5 different fictional Wikipedia article titles. Each title should be realistic for an actual Wikipedia entry. Make sure the titles are diverse and a similar distribution to wikipedia topics in terms of content, language, and time period. Output only the titles, one per line, with no additional text or formatting. Make sure the article isn't real."
            }
        ],
        model="gemma2-9b-it",
    )
    titles = response.choices[0].message.content.strip().split('\n')
    # Clean up any potential formatting and ensure we have exactly num_titles
    titles = [t.strip().strip('"').strip("'").strip('-').strip() for t in titles if t.strip()]
    return titles[:num_titles]

def generate_fake_titles_anthropic(num_titles=5):
    response = anthropic_client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=200,
        messages=[
            {
                "role": "user",
                "content": "Generate 5 different fictional Wikipedia article titles. Each title should be realistic for an actual Wikipedia entry. Make sure the titles are diverse and a similar distribution to wikipedia topics in terms of content, language, and time period. Output only the titles, one per line, with no additional text or formatting. Use web search to verify the article isn't real."
            }
        ],
        tools=[
        {
            "name": "web_search",
            "type": "web_search_20250305"
        }
        ]
    )
    titles = response.content[0].text.strip().split('\n')
    # Clean up any potential formatting and ensure we have exactly num_titles
    titles = [t.strip().strip('"').strip("'").strip('-').strip() for t in titles if t.strip()]
    return titles[:num_titles]

def generate_fake_titles(num_titles=5):
    if TITLE_PROVIDER.lower() == "anthropic":
        return generate_fake_titles_anthropic(num_titles)
    else:
        return generate_fake_titles_groq(num_titles)

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

    fake_titles = [{"title": title, "is_fake": True} for title in generate_fake_titles(num_fakes)]

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
