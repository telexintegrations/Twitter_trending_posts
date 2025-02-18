import os
import sys
from typing import List
import json


from pydantic import BaseModel
from fastapi import BackgroundTasks
import httpx
import asyncio

from twikit import Client
from twikit.trend import PlaceTrends
from twikit.utils import Result
from twikit.tweet import Tweet

from models.model import Setting, MonitorPayload

client = Client('en-US')
recent_tweets = []


if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    file = os.path.exists('cookies.json')
    if file:
        print('file exists')
        client.load_cookies('cookies.json')
    else:
        response = await client.login(
		auth_info_1=USERNAME,
		auth_info_2=EMAIL,
		password=PASSWORD,
		enable_ui_metrics=True,
		)
        client.save_cookies('cookies.json')

async def fetch_trending_tweets_in_nigeria() -> PlaceTrends:
    """ Fetch trending tweets """
    nigeria = 23424908
    trends = await client.get_place_trends(nigeria)

    return trends['trends'][:10]

async def get_tweets() -> Result[Tweet]:
    """ Search for tweets """
    print("fetching tweets")
    trends = await fetch_trending_tweets_in_nigeria()
    for i in trends:
        tweets = await client.search_tweet(i.name, 'Latest', count=5)
        category = {}
        aggregated_tweets = [f"• {tweet.text}" for tweet in tweets]
        category.update({i.name: aggregated_tweets})
        recent_tweets.append(category)

async def monitor_task(payload: MonitorPayload):
    print("logging")
    status = ""
    try:
        await main()
        await get_tweets()
        status = "success"
    except Exception:
        """ Retry """
        await main()
        await get_tweets()
        status = "success"

    formatted_tweets = []
    for category in recent_tweets:
        for trend, tweets in category.items():
            tweet_text = f"{trend}\n" + "\n".join(tweets) + "\n"
            formatted_tweets.append({
                "trend": trend,
                "tweet_text": tweet_text
            })

    data = {
        "message": json.dumps(formatted_tweets, ensure_ascii=False),
        "username": "Twitter Monitor",
        "event_name": "Trending tweets check",
        "status": status
        }
    async with httpx.AsyncClient() as client:
        await client.post(payload.return_url, json=data, headers={"Content-Type": "application/json"})

