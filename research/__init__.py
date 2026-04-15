"""
research/__init__.py
--------------------
Atlas Research module — CC's on-demand stock picker, market analyst, and macro watcher.

Sub-modules
-----------
news_ingest             Multi-source news aggregation (RSS, Google News, NewsAPI, SEC EDGAR)
macro_watch             Geopolitical flashpoints, sector rotation signals, macro context
fundamentals            Company fundamentals + technicals via yfinance / Alpha Vantage / FMP
stock_picker            StockPickerAgent — Claude-powered deep research with entry/exit/thesis
insider_tracking        SEC Form 4 insider transaction signals (EDGAR, free, no key)
institutional_tracking  SEC Form 13F smart-money holdings (EDGAR, free, no key)
earnings_calendar       Earnings dates, EPS surprise history, PEAD signal scoring
options_flow            Short interest, unusual options activity, IV rank, squeeze scoring
psychology              Behavioral finance: Fear & Greed, VIX regime, AAII, put/call ratio
historical_patterns     Seasonality, presidential cycle, market regime, historical analogs
"""

from research.news_ingest import NewsItem, Filing, fetch_rss, fetch_google_news, fetch_newsapi, fetch_sec_filings
from research.macro_watch import geopolitical_flashpoints, sector_map, rotation_signal
from research.fundamentals import Fundamentals, get_fundamentals, get_price_history, technicals
from research.insider_tracking import (
    InsiderTransaction,
    ticker_to_cik,
    recent_insider_activity,
    insider_score,
)
from research.institutional_tracking import (
    Holding,
    tracked_funds,
    get_fund_holdings,
    what_are_smart_money_buying,
    who_owns,
)
from research.earnings_calendar import (
    EarningsEvent,
    TickerNotFound as EarningsTickerNotFound,
    upcoming_earnings,
    earnings_history,
    surprise_score,
    days_to_next_earnings,
)
from research.options_flow import (
    OptionsSnapshot,
    TickerNotFound as OptionsTickerNotFound,
    get_options_snapshot,
    unusual_activity,
    squeeze_score,
    iv_rank,
)
from research.psychology import (
    behavioral_snapshot,
    fear_greed_index,
    vix_signal,
    aaii_sentiment,
    naaim_exposure,
    put_call_ratio_cboe,
    margin_debt_signal,
)
from research.historical_patterns import (
    cycle_context,
    market_regime,
    seasonality,
    presidential_cycle_phase,
    historical_analogs,
)

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
    # insider_tracking
    "InsiderTransaction",
    "ticker_to_cik",
    "recent_insider_activity",
    "insider_score",
    # institutional_tracking
    "Holding",
    "tracked_funds",
    "get_fund_holdings",
    "what_are_smart_money_buying",
    "who_owns",
    # earnings_calendar
    "EarningsEvent",
    "EarningsTickerNotFound",
    "upcoming_earnings",
    "earnings_history",
    "surprise_score",
    "days_to_next_earnings",
    # options_flow
    "OptionsSnapshot",
    "OptionsTickerNotFound",
    "get_options_snapshot",
    "unusual_activity",
    "squeeze_score",
    "iv_rank",
    # psychology
    "behavioral_snapshot",
    "fear_greed_index",
    "vix_signal",
    "aaii_sentiment",
    "naaim_exposure",
    "put_call_ratio_cboe",
    "margin_debt_signal",
    # historical_patterns
    "cycle_context",
    "market_regime",
    "seasonality",
    "presidential_cycle_phase",
    "historical_analogs",
]
