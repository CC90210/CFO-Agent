"""
research/__init__.py
--------------------
Atlas Research module — CC's on-demand stock picker, market analyst, and macro watcher.

Sub-modules
-----------
news_ingest     Multi-source news aggregation (RSS, Google News, NewsAPI, SEC EDGAR)
macro_watch     Geopolitical flashpoints, sector rotation signals, macro context
fundamentals    Company fundamentals + technicals via yfinance / Alpha Vantage / FMP
stock_picker    StockPickerAgent — Claude-powered deep research with entry/exit/thesis
"""

from research.news_ingest import NewsItem, Filing, fetch_rss, fetch_google_news, fetch_newsapi, fetch_sec_filings
from research.macro_watch import geopolitical_flashpoints, sector_map, rotation_signal
from research.fundamentals import Fundamentals, get_fundamentals, get_price_history, technicals

# stock_picker is imported lazily to avoid the Python runpy re-import warning
# when `python -m research.stock_picker` is invoked. Import explicitly if needed:
#   from research.stock_picker import Pick, DeepDive, StockPickerAgent

__all__ = [
    # news_ingest
    "NewsItem",
    "Filing",
    "fetch_rss",
    "fetch_google_news",
    "fetch_newsapi",
    "fetch_sec_filings",
    # macro_watch
    "geopolitical_flashpoints",
    "sector_map",
    "rotation_signal",
    # fundamentals
    "Fundamentals",
    "get_fundamentals",
    "get_price_history",
    "technicals",
]
