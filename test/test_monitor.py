from unittest.mock import AsyncMock, patch

import pytest

from models.model import MonitorPayload
from monitoring.monitor import (
    client,
    fetch_trending_tweets_in_nigeria,
    get_tweets,
    main,
    monitor_task,
    recent_tweets,
)


@pytest.mark.asyncio
async def test_main_with_existing_cookies():
    with (
        patch("os.path.exists", return_value=True),
        patch.object(client, "load_cookies") as mock_load_cookies,
    ):
        await main()
        mock_load_cookies.assert_called_once_with("cookies.json")


@pytest.mark.asyncio
async def test_main_without_existing_cookies():
    with (
        patch("os.path.exists", return_value=False),
        patch.object(client, "login", return_value=AsyncMock()),
        patch.object(client, "save_cookies") as mock_save_cookies,
    ):
        await main()
        mock_save_cookies.assert_called_once_with("cookies.json")


@pytest.mark.asyncio
async def test_fetch_trending_tweets_in_nigeria():
    mock_trends = {
        "trends": [{"name": "Trend1"}, {"name": "Trend2"}, {"name": "Trend3"}]
    }
    with patch.object(
        client, "get_place_trends", new_callable=AsyncMock
    ) as mock_get_place_trends:
        mock_get_place_trends.return_value = mock_trends
        trends = await fetch_trending_tweets_in_nigeria()
        assert len(trends) == 3


@pytest.mark.asyncio
async def test_get_tweets():
    class MockTrend:
        def __init__(self, name):
            self.name = name

    mock_trends = [MockTrend("Trend1"), MockTrend("Trend2")]
    mock_tweets = [AsyncMock(text="Tweet1"), AsyncMock(text="Tweet2")]
    with (
        patch(
            "monitoring.monitor.fetch_trending_tweets_in_nigeria",
            return_value=mock_trends,
        ),
        patch.object(
            client, "search_tweet", return_value=AsyncMock(return_value=mock_tweets)
        ),
    ):
        await get_tweets()
        assert len(recent_tweets) == 2
        assert "Trend1" in recent_tweets[0]
        assert "Trend2" in recent_tweets[1]


@pytest.mark.asyncio
async def test_monitor_task():
    payload = MonitorPayload(
        return_url="http://example.com", channel_id="test_channel", settings=[]
    )
    with (
        patch("monitoring.monitor.main", return_value=AsyncMock()),
        patch("monitoring.monitor.get_tweets", return_value=AsyncMock()),
        patch(
            "httpx.AsyncClient.post", return_value=AsyncMock(status_code=200)
        ) as mock_post,
    ):
        await monitor_task(payload)
        mock_post.assert_called_once_with(
            payload.return_url,
            json={
                "message": '[{"trend": "Trend1", "tweet_text": "Trend1\\n\\n"}, {"trend": "Trend2", "tweet_text": "Trend2\\n\\n"}]',
                "username": "Twitter Monitor",
                "event_name": "Trending tweets check",
                "status": "success",
            },
            headers={"Content-Type": "application/json"},
        )
