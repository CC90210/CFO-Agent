"""
data/fetcher.py
---------------
Market Data Fetcher for Atlas Trading Agent.

Fetches OHLCV, ticker, and order-book data from any CCXT-supported exchange.
All data is normalised to a standard DataFrame format with columns:
    timestamp (UTC, DatetimeTZDtype), open, high, low, close, volume

Caching
-------
Raw OHLCV responses are cached keyed by (symbol, timeframe).  A cache entry is
considered fresh for the duration of one candle period.  For example, a 1h
candle is re-fetched at most once per hour.  The cache lives only in memory;
it is not persisted to disk.

Rate limiting
-------------
A per-call asyncio.sleep is applied based on the exchange's self-reported
rateLimit attribute (milliseconds per request).  This is a simple token-bucket
approximation; production systems should add a proper leaky-bucket or use
CCXT's built-in enableRateLimit=True.

Websocket streaming
-------------------
stream_price() opens a long-lived websocket via CCXT's watch_ticker and
delivers price updates to the provided async callback.  The stream continues
until the caller cancels the enclosing Task.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Callable, Coroutine

import ccxt
import ccxt.async_support as ccxt_async
import pandas as pd

from config.settings import settings

logger = logging.getLogger("atlas.fetcher")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_OHLCV_COLUMNS: list[str] = ["timestamp", "open", "high", "low", "close", "volume"]
_DEFAULT_TIMEFRAMES: list[str] = ["15m", "1h", "4h", "1d"]
_DEFAULT_OHLCV_LIMIT: int = 500
_CACHE_BUFFER_FACTOR: float = 0.9  # treat cache as stale after 90% of bar duration
_TIMEFRAME_SECONDS: dict[str, int] = {
    "1m": 60,
    "3m": 180,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "2h": 7200,
    "4h": 14400,
    "6h": 21600,
    "12h": 43200,
    "1d": 86400,
    "1w": 604800,
}

# ---------------------------------------------------------------------------
# Cache entry
# ---------------------------------------------------------------------------


class _CacheEntry:
    __slots__ = ("df", "fetched_at", "ttl")

    def __init__(self, df: pd.DataFrame, ttl: float) -> None:
        self.df = df
        self.fetched_at = time.monotonic()
        self.ttl = ttl

    def is_fresh(self) -> bool:
        return (time.monotonic() - self.fetched_at) < self.ttl


# ---------------------------------------------------------------------------
# MarketDataFetcher
# ---------------------------------------------------------------------------


class MarketDataFetcher:
    """
    Async wrapper around a CCXT exchange for all market data needs.

    Parameters
    ----------
    exchange_id : CCXT exchange identifier (e.g. 'binance').
                  Defaults to settings.exchange.default_exchange.
    sandbox     : use the exchange's testnet/sandbox environment.

    Usage
    -----
    async with MarketDataFetcher() as fetcher:
        df = await fetcher.fetch_ohlcv("BTC/USDT", "1h", limit=200)
        ticker = await fetcher.fetch_ticker("BTC/USDT")
    """

    def __init__(
        self,
        exchange_id: str | None = None,
        sandbox: bool = False,
    ) -> None:
        eid = exchange_id or settings.exchange.default_exchange
        exchange_cls = getattr(ccxt_async, eid, None)
        if exchange_cls is None:
            raise ValueError(f"Unknown CCXT exchange: '{eid}'")

        init_params: dict[str, Any] = {"enableRateLimit": True}
        if settings.exchange.exchange_api_key:
            init_params["apiKey"] = settings.exchange.exchange_api_key
        if settings.exchange.exchange_secret:
            init_params["secret"] = settings.exchange.exchange_secret

        self._exchange: ccxt_async.Exchange = exchange_cls(init_params)
        if sandbox:
            self._exchange.set_sandbox_mode(True)

        self._ohlcv_cache: dict[str, _CacheEntry] = {}
        self._ticker_cache: dict[str, _CacheEntry] = {}
        self._markets_loaded: bool = False

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "MarketDataFetcher":
        await self._ensure_markets()
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self._exchange.close()

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = _DEFAULT_OHLCV_LIMIT,
        since: int | None = None,
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data and return a normalised DataFrame.

        Parameters
        ----------
        symbol    : e.g. "BTC/USDT"
        timeframe : CCXT timeframe string, e.g. "1h", "4h", "1d"
        limit     : number of candles to fetch (most recent)
        since     : optional UNIX timestamp in milliseconds for start time

        Returns
        -------
        pd.DataFrame with columns: timestamp, open, high, low, close, volume
            timestamp is UTC-aware DatetimeTZDtype index.
        """
        cache_key = f"{symbol}:{timeframe}:{limit}"
        ttl = _TIMEFRAME_SECONDS.get(timeframe, 3600) * _CACHE_BUFFER_FACTOR

        cached = self._ohlcv_cache.get(cache_key)
        if cached is not None and cached.is_fresh() and since is None:
            logger.debug("OHLCV cache hit: %s", cache_key)
            return cached.df.copy()

        await self._ensure_markets()
        await self._rate_limit()

        try:
            raw: list[list[Any]] = await self._exchange.fetch_ohlcv(
                symbol, timeframe=timeframe, limit=limit, since=since
            )
        except ccxt.BadSymbol as exc:
            raise ValueError(f"Symbol not available on exchange: {symbol}") from exc
        except ccxt.BaseError as exc:
            logger.error("OHLCV fetch failed for %s/%s: %s", symbol, timeframe, exc)
            raise

        df = self._normalise_ohlcv(raw)
        if since is None:
            self._ohlcv_cache[cache_key] = _CacheEntry(df, ttl)
        logger.debug("Fetched %d candles for %s/%s", len(df), symbol, timeframe)
        return df

    async def fetch_ticker(self, symbol: str) -> dict[str, Any]:
        """
        Return current price, bid, ask, and 24 h volume for a symbol.

        Returns
        -------
        dict with keys: symbol, last, bid, ask, volume, timestamp
        """
        cache_key = f"ticker:{symbol}"
        ttl = 10.0  # refresh every 10 seconds for live price accuracy

        cached = self._ticker_cache.get(cache_key)
        if cached is not None and cached.is_fresh():
            return dict(cached.df.iloc[0])  # stored as 1-row DataFrame

        await self._ensure_markets()
        await self._rate_limit()

        try:
            raw = await self._exchange.fetch_ticker(symbol)
        except ccxt.BaseError as exc:
            logger.error("Ticker fetch failed for %s: %s", symbol, exc)
            raise

        result: dict[str, Any] = {
            "symbol": raw.get("symbol", symbol),
            "last": float(raw.get("last") or 0.0),
            "bid": float(raw.get("bid") or 0.0),
            "ask": float(raw.get("ask") or 0.0),
            "volume": float(raw.get("baseVolume") or raw.get("volume") or 0.0),
            "quote_volume": float(raw.get("quoteVolume") or 0.0),
            "timestamp": pd.Timestamp(raw["timestamp"], unit="ms", tz="UTC")
            if raw.get("timestamp")
            else pd.Timestamp.utcnow(),
        }
        # Cache as a 1-row DataFrame (reuses the same cache infrastructure)
        self._ticker_cache[cache_key] = _CacheEntry(pd.DataFrame([result]), ttl)
        return result

    async def fetch_order_book(
        self,
        symbol: str,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Fetch the current order book.

        Returns
        -------
        dict with:
            bids: list of [price, amount] descending by price
            asks: list of [price, amount] ascending by price
            spread: ask[0] - bid[0]
            mid_price: (ask[0] + bid[0]) / 2
        """
        await self._ensure_markets()
        await self._rate_limit()

        try:
            raw = await self._exchange.fetch_order_book(symbol, limit=limit)
        except ccxt.BaseError as exc:
            logger.error("Order book fetch failed for %s: %s", symbol, exc)
            raise

        bids: list[list[float]] = raw.get("bids", [])
        asks: list[list[float]] = raw.get("asks", [])

        best_bid = bids[0][0] if bids else 0.0
        best_ask = asks[0][0] if asks else 0.0

        return {
            "symbol": symbol,
            "bids": bids,
            "asks": asks,
            "spread": best_ask - best_bid,
            "mid_price": (best_bid + best_ask) / 2.0 if best_bid and best_ask else 0.0,
            "timestamp": pd.Timestamp.utcnow(),
        }

    async def fetch_multiple_timeframes(
        self,
        symbol: str,
        timeframes: list[str] | None = None,
        limit: int = _DEFAULT_OHLCV_LIMIT,
    ) -> dict[str, pd.DataFrame]:
        """
        Concurrently fetch OHLCV for multiple timeframes.

        Parameters
        ----------
        symbol     : e.g. "BTC/USDT"
        timeframes : list of CCXT timeframe strings; defaults to ['15m','1h','4h','1d']
        limit      : candles per timeframe

        Returns
        -------
        dict mapping timeframe → DataFrame
        """
        tfs = timeframes or _DEFAULT_TIMEFRAMES
        tasks = [self.fetch_ohlcv(symbol, tf, limit) for tf in tfs]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        output: dict[str, pd.DataFrame] = {}
        for tf, result in zip(tfs, results):
            if isinstance(result, Exception):
                logger.warning("Failed to fetch %s/%s: %s", symbol, tf, result)
            else:
                output[tf] = result
        return output

    async def stream_price(
        self,
        symbol: str,
        callback: Callable[[dict[str, Any]], Coroutine[Any, Any, None]],
    ) -> None:
        """
        Stream real-time price updates via websocket and deliver each
        ticker update to the async callback.

        This coroutine runs indefinitely.  Cancel the enclosing Task to stop.

        Parameters
        ----------
        symbol   : e.g. "BTC/USDT"
        callback : async function called with each ticker dict
        """
        if not hasattr(self._exchange, "watch_ticker"):
            raise NotImplementedError(
                f"{self._exchange.id} does not support websocket watch_ticker. "
                "Use fetch_ticker() polling instead."
            )

        await self._ensure_markets()
        logger.info("Starting price stream for %s on %s", symbol, self._exchange.id)

        while True:
            try:
                ticker = await self._exchange.watch_ticker(symbol)  # type: ignore[attr-defined]
                payload: dict[str, Any] = {
                    "symbol": symbol,
                    "last": float(ticker.get("last") or 0.0),
                    "bid": float(ticker.get("bid") or 0.0),
                    "ask": float(ticker.get("ask") or 0.0),
                    "volume": float(ticker.get("baseVolume") or 0.0),
                    "timestamp": pd.Timestamp.utcnow(),
                }
                await callback(payload)
            except asyncio.CancelledError:
                logger.info("Price stream cancelled for %s", symbol)
                break
            except ccxt.BaseError as exc:
                logger.warning("Stream error for %s: %s — reconnecting in 5s", symbol, exc)
                await asyncio.sleep(5)

    async def download_historical(
        self,
        symbol: str,
        timeframe: str,
        start: pd.Timestamp,
        end: pd.Timestamp | None = None,
    ) -> pd.DataFrame:
        """
        Download full historical OHLCV data between start and end,
        paginating through as many requests as needed.

        Intended for backtesting data preparation.

        Parameters
        ----------
        symbol    : e.g. "BTC/USDT"
        timeframe : e.g. "1h"
        start     : UTC start time (inclusive)
        end       : UTC end time (inclusive); defaults to now

        Returns
        -------
        pd.DataFrame — complete history, deduplicated and sorted
        """
        end_ts = end or pd.Timestamp.utcnow()
        since_ms = int(start.timestamp() * 1000)
        end_ms = int(end_ts.timestamp() * 1000)
        all_candles: list[list[Any]] = []

        await self._ensure_markets()
        logger.info(
            "Downloading historical %s/%s from %s to %s",
            symbol,
            timeframe,
            start.isoformat(),
            end_ts.isoformat(),
        )

        while since_ms < end_ms:
            await self._rate_limit()
            try:
                batch: list[list[Any]] = await self._exchange.fetch_ohlcv(
                    symbol, timeframe=timeframe, since=since_ms, limit=1000
                )
            except ccxt.BaseError as exc:
                logger.error("Historical download error: %s", exc)
                break

            if not batch:
                break

            all_candles.extend(batch)
            since_ms = batch[-1][0] + 1  # next batch starts after last candle
            logger.debug("Downloaded %d candles (total so far: %d)", len(batch), len(all_candles))

            if len(batch) < 1000:
                break

        if not all_candles:
            return pd.DataFrame(columns=_OHLCV_COLUMNS)

        df = self._normalise_ohlcv(all_candles)
        df = df[df["timestamp"] <= end_ts].drop_duplicates(subset=["timestamp"]).sort_values("timestamp")
        logger.info("Historical download complete: %d candles for %s/%s", len(df), symbol, timeframe)
        return df

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _ensure_markets(self) -> None:
        if not self._markets_loaded:
            await self._exchange.load_markets()
            self._markets_loaded = True

    async def _rate_limit(self) -> None:
        """Simple rate-limit sleep based on the exchange's rateLimit property."""
        rate_limit_ms = getattr(self._exchange, "rateLimit", 100)
        await asyncio.sleep(rate_limit_ms / 1000.0)

    @staticmethod
    def _normalise_ohlcv(raw: list[list[Any]]) -> pd.DataFrame:
        """
        Convert a raw CCXT OHLCV list to a normalised DataFrame.

        Input format: [[timestamp_ms, open, high, low, close, volume], ...]
        Output: DataFrame with UTC-aware datetime index.
        """
        df = pd.DataFrame(raw, columns=_OHLCV_COLUMNS)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df = df.sort_values("timestamp").drop_duplicates(subset=["timestamp"])
        for col in ("open", "high", "low", "close", "volume"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["open", "high", "low", "close"])
        df = df.set_index("timestamp")
        return df
