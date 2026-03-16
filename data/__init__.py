"""
data package — market data and news/sentiment fetching.
"""

from data.fetcher import MarketDataFetcher
from data.news_fetcher import NewsFetcher, NewsItem

__all__ = [
    "MarketDataFetcher",
    "NewsFetcher",
    "NewsItem",
]
