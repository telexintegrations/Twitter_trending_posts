import asyncio
import json
import os
import sys

import httpx
from decouple import config
from twikit import Client
from twikit.errors import TooManyRequests
from twikit.trend import PlaceTrends
from twikit.tweet import Tweet
from twikit.utils import Result

from core.config import logger
from models.model import MonitorPayload

client = Client("en-US")

USERNAME = config("TWITTER_USERNAME")
EMAIL = config("TWITTER_EMAIL")
PASSWORD = config("TWITTER_PASSWORD")


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

recent_tweets = []


async def main():
    file = os.path.exists("cookies.json")
    if file:
        print("file exists")
        client.load_cookies("cookies.json")
    else:
        await client.login(
            auth_info_1=USERNAME,
            auth_info_2=EMAIL,
            password=PASSWORD,
            enable_ui_metrics=True,
        )
        client.save_cookies("cookies.json")


async def fetch_trending_tweets_in_nigeria() -> PlaceTrends:
    """Fetch trending tweets"""
    nigeria = 23424908
    trends = await client.get_place_trends(nigeria)

    return trends["trends"][:10]


async def get_tweets() -> Result[Tweet]:
    """Search for tweets"""
    trends = await fetch_trending_tweets_in_nigeria()
    for i in trends:
        tweets = await client.search_tweet(i.name, "Latest", count=5)
        category = {}
        aggregated_tweets = [f"• {tweet.text}" for tweet in tweets]
        category.update({i.name: aggregated_tweets})
        recent_tweets.append(category)


async def monitor_task(payload: MonitorPayload):
    print("feting data")
    status = ""
    max_retries = 3
    retries = 0
    while retries < max_retries:
        try:
            await main()
            await get_tweets()
            status = "success"
            break
        except TooManyRequests:
            """ Retry """
            await asyncio.sleep(900)  # sleep for 15 minutes
            retries += 1
            if retries >= max_retries:
                status = "failed"
                break
            await main()
            await get_tweets()
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            retries += 1
            if retries >= max_retries:
                status = "failed"
                break

    formatted_tweets = []
    for category in recent_tweets:
        for trend, tweets in category.items():
            tweet_text = f"{trend}\n" + "\n".join(tweets) + "\n"
            formatted_tweets.append({"trend": trend, "tweet_text": tweet_text})
    data = {
        "message": json.dumps(formatted_tweets, ensure_ascii=False),
        "username": "Twitter Monitor",
        "event_name": "Trending tweets check",
        "status": status,
    }
    async with httpx.AsyncClient() as client:
        await client.post(
            payload.return_url, json=data, headers={"Content-Type": "application/json"}
        )
