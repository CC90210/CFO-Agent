"""
data/watchlists.py
-------------------
Pre-configured asset watchlists for Atlas Trading Agent.

Provides named lists of symbols that can be fed into scanners, screeners,
and the orchestrator's symbol-selection logic.

Symbol format follows CCXT convention:
  Crypto   : "BTC/USDT"
  Stocks   : "AAPL"  (used with yfinance / Yahoo Finance)
  Forex    : "EUR/USD"
  Commodities : "XAU/USD"

CoinGecko IDs are also provided for the crypto lists since FundamentalsAnalyst
and NewsFetcher's CoinGecko methods require them.

Usage
-----
    from data.watchlists import get_watchlist, COINGECKO_ID_MAP

    symbols = get_watchlist("CRYPTO_MAJORS")
    # → ["BTC/USDT", "ETH/USDT", "SOL/USDT", ...]

    cg_id = COINGECKO_ID_MAP.get("BTC")
    # → "bitcoin"
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Watchlists
# ---------------------------------------------------------------------------

# Top crypto assets by market cap
CRYPTO_MAJORS: list[str] = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "BNB/USDT",
    "XRP/USDT",
    "ADA/USDT",
    "AVAX/USDT",
    "DOT/USDT",
    "LINK/USDT",
    "MATIC/USDT",
]

# DeFi blue-chips
CRYPTO_DEFI: list[str] = [
    "UNI/USDT",
    "AAVE/USDT",
    "MKR/USDT",
    "CRV/USDT",
    "COMP/USDT",
]

# Large-cap crypto altcoins
CRYPTO_ALTS: list[str] = [
    "DOGE/USDT",
    "LTC/USDT",
    "ATOM/USDT",
    "APT/USDT",
    "ARB/USDT",
    "OP/USDT",
    "INJ/USDT",
    "TIA/USDT",
    "SEI/USDT",
    "SUI/USDT",
]

# S&P 500 top constituents + major ETFs
STOCKS_SP500_TOP: list[str] = [
    "SPY",    # S&P 500 ETF
    "QQQ",    # Nasdaq-100 ETF
    "AAPL",
    "MSFT",
    "NVDA",
    "GOOGL",
    "AMZN",
    "META",
    "TSLA",
    "BRK-B",
]

# Additional tech growth stocks
STOCKS_TECH: list[str] = [
    "AMD",
    "INTC",
    "ASML",
    "CRM",
    "ORCL",
    "NFLX",
    "ADBE",
    "UBER",
    "SHOP",
    "SNOW",
]

# Major forex pairs
FOREX_MAJORS: list[str] = [
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "AUD/USD",
    "USD/CAD",
    "USD/CHF",
    "NZD/USD",
]

# Commodities (using common trading symbols)
COMMODITIES: list[str] = [
    "XAU/USD",  # Gold
    "XAG/USD",  # Silver
    "CL",       # Crude Oil (WTI)
    "NG",       # Natural Gas
    "WEAT",     # Wheat ETF
]

# ---------------------------------------------------------------------------
# Registry for named lookups
# ---------------------------------------------------------------------------

_WATCHLISTS: dict[str, list[str]] = {
    "CRYPTO_MAJORS": CRYPTO_MAJORS,
    "CRYPTO_DEFI": CRYPTO_DEFI,
    "CRYPTO_ALTS": CRYPTO_ALTS,
    "STOCKS_SP500_TOP": STOCKS_SP500_TOP,
    "STOCKS_TECH": STOCKS_TECH,
    "FOREX_MAJORS": FOREX_MAJORS,
    "COMMODITIES": COMMODITIES,
}

# ---------------------------------------------------------------------------
# CoinGecko ID map (base symbol → coingecko coin id)
# Used by FundamentalsAnalyst and NewsFetcher.fetch_coingecko_market_data()
# ---------------------------------------------------------------------------

COINGECKO_ID_MAP: dict[str, str] = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "AVAX": "avalanche-2",
    "DOT": "polkadot",
    "LINK": "chainlink",
    "MATIC": "matic-network",
    "UNI": "uniswap",
    "AAVE": "aave",
    "MKR": "maker",
    "CRV": "curve-dao-token",
    "COMP": "compound-governance-token",
    "DOGE": "dogecoin",
    "LTC": "litecoin",
    "ATOM": "cosmos",
    "APT": "aptos",
    "ARB": "arbitrum",
    "OP": "optimism",
    "INJ": "injective-protocol",
    "TIA": "celestia",
    "SEI": "sei-network",
    "SUI": "sui",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_watchlist(name: str) -> list[str]:
    """
    Return a named watchlist of trading symbols.

    Parameters
    ----------
    name : watchlist name — one of:
           CRYPTO_MAJORS, CRYPTO_DEFI, CRYPTO_ALTS,
           STOCKS_SP500_TOP, STOCKS_TECH,
           FOREX_MAJORS, COMMODITIES

    Returns
    -------
    list of symbol strings; raises KeyError for unknown names

    Raises
    ------
    KeyError : if the watchlist name is not registered
    """
    if name not in _WATCHLISTS:
        available = ", ".join(sorted(_WATCHLISTS.keys()))
        raise KeyError(
            f"Unknown watchlist '{name}'. Available: {available}"
        )
    return list(_WATCHLISTS[name])  # return a copy so callers can't mutate


def list_watchlists() -> list[str]:
    """Return the names of all available watchlists."""
    return sorted(_WATCHLISTS.keys())


def get_coingecko_id(symbol: str) -> str | None:
    """
    Look up the CoinGecko coin ID for a base trading symbol.

    Parameters
    ----------
    symbol : base symbol or full pair, e.g. "BTC" or "BTC/USDT"

    Returns
    -------
    CoinGecko ID string, or None if not found
    """
    base = symbol.split("/")[0].split("-")[0].upper()
    return COINGECKO_ID_MAP.get(base)
