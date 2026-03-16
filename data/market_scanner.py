"""
data/market_scanner.py
-----------------------
Market-wide intelligence scanner for Atlas Trading Agent.

Provides:
  - Top gainers and losers across exchanges (via CCXT)
  - Volume anomaly detection (spikes > 2x 20-day average)
  - Correlation matrix between watched assets
  - Market breadth indicators (% above 50 EMA, advance/decline ratio)

All methods are async and cached. Heavy computations (correlation, breadth)
use pandas and are offloaded to a thread executor to keep the event loop free.

No API keys required — uses CCXT for exchange data.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("atlas.scanner")


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class Mover:
    """A top-gaining or top-losing asset on an exchange."""

    symbol: str
    price: float
    change_pct: float   # percentage change in the last 24h (positive = gainer)
    volume: float       # 24h quote volume
    volume_ratio: float  # current 24h volume / 20-day average daily volume

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "price": self.price,
            "change_pct": self.change_pct,
            "volume": self.volume,
            "volume_ratio": self.volume_ratio,
        }


@dataclass
class VolumeAnomaly:
    """An asset exhibiting unusual trading volume relative to its history."""

    symbol: str
    current_volume: float   # current 24h volume
    avg_volume: float       # 20-day average daily volume
    ratio: float            # current_volume / avg_volume (e.g. 3.5 = 350% of avg)
    price_change_pct: float  # 24h price change while the spike was detected

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "current_volume": self.current_volume,
            "avg_volume": self.avg_volume,
            "ratio": self.ratio,
            "price_change_pct": self.price_change_pct,
        }


@dataclass
class MarketBreadth:
    """Aggregate health of a market — how many assets are trending up."""

    exchange: str
    total_assets: int
    assets_above_50ema: int
    pct_above_50ema: float      # 0.0 – 1.0
    advance_count: int          # assets up 24h
    decline_count: int          # assets down 24h
    unchanged_count: int
    advance_decline_ratio: float  # advance_count / max(decline_count, 1)
    sentiment: str              # "BULLISH" | "BEARISH" | "NEUTRAL"

    def to_dict(self) -> dict[str, Any]:
        return {
            "exchange": self.exchange,
            "total_assets": self.total_assets,
            "assets_above_50ema": self.assets_above_50ema,
            "pct_above_50ema": self.pct_above_50ema,
            "advance_count": self.advance_count,
            "decline_count": self.decline_count,
            "unchanged_count": self.unchanged_count,
            "advance_decline_ratio": self.advance_decline_ratio,
            "sentiment": self.sentiment,
        }


# ---------------------------------------------------------------------------
# Simple in-memory cache (mirrors pattern from news_fetcher)
# ---------------------------------------------------------------------------


class _Cache:
    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: float) -> None:
        self._store[key] = (value, time.monotonic() + ttl)


_TICKERS_CACHE_TTL = 300.0    # 5 minutes — exchange ticker snapshots
_OHLCV_CACHE_TTL = 600.0      # 10 minutes — historical OHLCV
_BREADTH_CACHE_TTL = 900.0    # 15 minutes — market breadth is expensive
_CORRELATION_CACHE_TTL = 1800.0  # 30 minutes

# Volume anomaly threshold
_VOLUME_ANOMALY_RATIO = 2.0  # flag when current volume > 2x average


class MarketScanner:
    """
    Market-wide intelligence scanner.

    Parameters
    ----------
    exchange_id : CCXT exchange identifier, e.g. "binance", "kraken", "coinbase"
    quote_currency : filter markets by quote asset, e.g. "USDT", "USD"

    Usage
    -----
    scanner = MarketScanner("binance", "USDT")
    movers   = await scanner.scan_top_movers("binance", limit=20)
    anomalies = await scanner.detect_volume_anomalies(["BTC/USDT", "ETH/USDT"])
    corr     = await scanner.calculate_correlation_matrix(["BTC/USDT", "ETH/USDT"])
    breadth  = await scanner.get_market_breadth("binance")
    """

    def __init__(
        self,
        exchange_id: str = "binance",
        quote_currency: str = "USDT",
    ) -> None:
        self._exchange_id = exchange_id
        self._quote_currency = quote_currency
        self._cache = _Cache()
        self._exchange: Any = None  # lazy-initialised CCXT exchange

    def _get_exchange(self, exchange_id: str) -> Any:
        """Lazy-initialise a CCXT exchange instance."""
        try:
            import ccxt  # type: ignore[import-untyped]
        except ImportError:
            raise ImportError("ccxt not installed — run: pip install ccxt")

        exchange_class = getattr(ccxt, exchange_id.lower(), None)
        if exchange_class is None:
            raise ValueError(f"Unknown CCXT exchange: {exchange_id}")
        return exchange_class({"enableRateLimit": True})

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def scan_top_movers(
        self,
        exchange: str | None = None,
        limit: int = 20,
    ) -> list[Mover]:
        """
        Scan for the top gainers and losers (by 24h % change) on an exchange.

        Parameters
        ----------
        exchange : CCXT exchange ID; defaults to the instance's exchange_id
        limit    : number of movers to return (split equally between
                   gainers and losers — e.g. limit=20 → top 10 + bottom 10)

        Returns
        -------
        list of Mover sorted by change_pct descending (gainers first, losers last)
        """
        exchange_id = exchange or self._exchange_id
        cache_key = f"top_movers:{exchange_id}:{limit}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached  # type: ignore[return-value]

        tickers = await self._fetch_tickers(exchange_id)
        if not tickers:
            return []

        movers: list[Mover] = []
        for symbol, ticker in tickers.items():
            # Only include USDT (or configured quote) pairs for consistency
            if not symbol.endswith(f"/{self._quote_currency}"):
                continue
            change_pct = ticker.get("percentage") or 0.0
            price = ticker.get("last") or 0.0
            volume = ticker.get("quoteVolume") or 0.0
            movers.append(
                Mover(
                    symbol=symbol,
                    price=price,
                    change_pct=change_pct,
                    volume=volume,
                    volume_ratio=1.0,  # ratio computed in detect_volume_anomalies
                )
            )

        # Sort descending by % change
        movers.sort(key=lambda m: m.change_pct, reverse=True)

        half = limit // 2
        top_gainers = movers[:half]
        top_losers = movers[-half:][::-1]  # re-sort losers worst-first
        result = top_gainers + top_losers

        self._cache.set(cache_key, result, _TICKERS_CACHE_TTL)
        logger.debug("Scanned %d movers on %s", len(result), exchange_id)
        return result

    async def detect_volume_anomalies(
        self,
        symbols: list[str],
        lookback: int = 20,
    ) -> list[VolumeAnomaly]:
        """
        Detect assets where current 24h volume significantly exceeds their
        historical average (threshold: >2x 20-day average).

        Parameters
        ----------
        symbols  : list of trading symbols, e.g. ["BTC/USDT", "ETH/USDT"]
        lookback : number of days to compute the average volume over

        Returns
        -------
        list of VolumeAnomaly sorted by ratio descending (most extreme first)
        """
        cache_key = f"vol_anomalies:{','.join(sorted(symbols))}:{lookback}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached  # type: ignore[return-value]

        tickers = await self._fetch_tickers(self._exchange_id)
        anomalies: list[VolumeAnomaly] = []

        for symbol in symbols:
            # Fetch 24h rolling volume from live ticker
            ticker = tickers.get(symbol, {})
            current_volume = ticker.get("quoteVolume") or 0.0
            price_change = ticker.get("percentage") or 0.0

            # Fetch historical OHLCV to compute average daily volume
            historical = await self._fetch_ohlcv(symbol, timeframe="1d", limit=lookback + 1)
            if not historical:
                continue

            # Exclude the most recent candle (incomplete day)
            past_volumes = [float(candle[5]) for candle in historical[:-1] if candle[5]]
            if not past_volumes:
                continue

            avg_volume = sum(past_volumes) / len(past_volumes)
            if avg_volume <= 0:
                continue

            ratio = current_volume / avg_volume
            if ratio >= _VOLUME_ANOMALY_RATIO:
                anomalies.append(
                    VolumeAnomaly(
                        symbol=symbol,
                        current_volume=current_volume,
                        avg_volume=avg_volume,
                        ratio=round(ratio, 2),
                        price_change_pct=price_change,
                    )
                )

        anomalies.sort(key=lambda a: a.ratio, reverse=True)
        self._cache.set(cache_key, anomalies, _OHLCV_CACHE_TTL)
        logger.debug("Found %d volume anomalies in %d symbols", len(anomalies), len(symbols))
        return anomalies

    async def calculate_correlation_matrix(
        self,
        symbols: list[str],
        timeframe: str = "1d",
        limit: int = 90,
    ) -> "Any":  # returns pd.DataFrame
        """
        Compute a Pearson correlation matrix of daily close returns for the
        given symbols over the specified lookback period.

        Parameters
        ----------
        symbols   : list of trading symbols, e.g. ["BTC/USDT", "ETH/USDT"]
        timeframe : CCXT timeframe string, e.g. "1d", "4h"
        limit     : number of candles to use (90 days by default)

        Returns
        -------
        pd.DataFrame with symbols as both index and columns, values in [-1, 1].
        Returns an empty DataFrame on failure.
        """
        import pandas as pd  # type: ignore[import-untyped]

        cache_key = f"corr:{','.join(sorted(symbols))}:{timeframe}:{limit}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached  # type: ignore[return-value]

        close_series: dict[str, list[float]] = {}

        fetch_tasks = [
            self._fetch_ohlcv(symbol, timeframe=timeframe, limit=limit + 1)
            for symbol in symbols
        ]
        results = await asyncio.gather(*fetch_tasks, return_exceptions=True)

        for symbol, ohlcv in zip(symbols, results):
            if isinstance(ohlcv, Exception) or not ohlcv:
                logger.warning("Skipping %s for correlation matrix (fetch failed)", symbol)
                continue
            closes = [float(candle[4]) for candle in ohlcv if candle[4]]
            if len(closes) > 1:
                close_series[symbol] = closes

        if len(close_series) < 2:
            logger.warning("Not enough series to compute correlation matrix")
            return pd.DataFrame()

        def _compute_correlation() -> "Any":
            price_df = pd.DataFrame(close_series)
            # Align on shortest series
            min_len = price_df.apply(lambda col: col.dropna().shape[0]).min()
            price_df = price_df.tail(min_len)
            returns_df = price_df.pct_change().dropna()
            return returns_df.corr()

        corr_df = await asyncio.get_event_loop().run_in_executor(None, _compute_correlation)
        self._cache.set(cache_key, corr_df, _CORRELATION_CACHE_TTL)
        logger.debug("Correlation matrix computed for %d symbols", len(close_series))
        return corr_df

    async def get_market_breadth(self, exchange: str | None = None) -> MarketBreadth:
        """
        Compute market breadth indicators:
          - Percentage of assets trading above their 50-period EMA
          - Advance/decline ratio over the past 24h

        Parameters
        ----------
        exchange : CCXT exchange ID; defaults to the instance's exchange_id

        Returns
        -------
        MarketBreadth dataclass; sentiment is "BULLISH" if >60% above 50 EMA,
        "BEARISH" if <40%, "NEUTRAL" otherwise.
        """
        exchange_id = exchange or self._exchange_id
        cache_key = f"breadth:{exchange_id}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached  # type: ignore[return-value]

        tickers = await self._fetch_tickers(exchange_id)

        # Filter to quote-currency pairs only
        relevant = {
            sym: tick for sym, tick in tickers.items()
            if sym.endswith(f"/{self._quote_currency}")
        }

        advance_count = 0
        decline_count = 0
        unchanged_count = 0
        above_50ema = 0
        total = len(relevant)

        if total == 0:
            return MarketBreadth(
                exchange=exchange_id,
                total_assets=0,
                assets_above_50ema=0,
                pct_above_50ema=0.0,
                advance_count=0,
                decline_count=0,
                unchanged_count=0,
                advance_decline_ratio=1.0,
                sentiment="NEUTRAL",
            )

        # 50 EMA check: fetch daily closes for a sample of liquid markets
        # (computing for ALL markets would be too slow / API-heavy)
        liquid_symbols = sorted(
            relevant.keys(),
            key=lambda s: relevant[s].get("quoteVolume") or 0,
            reverse=True,
        )[:50]  # top 50 by volume

        ema_tasks = [
            self._check_above_50ema(sym) for sym in liquid_symbols
        ]
        ema_results = await asyncio.gather(*ema_tasks, return_exceptions=True)
        valid_ema = [r for r in ema_results if isinstance(r, bool)]
        above_50ema = sum(1 for r in valid_ema if r)
        pct_above_50ema = above_50ema / len(valid_ema) if valid_ema else 0.0

        # Advance / decline from 24h ticker data
        for ticker in relevant.values():
            change = ticker.get("percentage") or 0.0
            if change > 0.1:
                advance_count += 1
            elif change < -0.1:
                decline_count += 1
            else:
                unchanged_count += 1

        ad_ratio = advance_count / max(decline_count, 1)

        if pct_above_50ema > 0.6 and ad_ratio > 1.5:
            sentiment = "BULLISH"
        elif pct_above_50ema < 0.4 and ad_ratio < 0.67:
            sentiment = "BEARISH"
        else:
            sentiment = "NEUTRAL"

        breadth = MarketBreadth(
            exchange=exchange_id,
            total_assets=total,
            assets_above_50ema=above_50ema,
            pct_above_50ema=round(pct_above_50ema, 3),
            advance_count=advance_count,
            decline_count=decline_count,
            unchanged_count=unchanged_count,
            advance_decline_ratio=round(ad_ratio, 2),
            sentiment=sentiment,
        )

        self._cache.set(cache_key, breadth, _BREADTH_CACHE_TTL)
        logger.debug(
            "Market breadth on %s: %s (%.1f%% above 50EMA, A/D=%.2f)",
            exchange_id, sentiment, pct_above_50ema * 100, ad_ratio,
        )
        return breadth

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _fetch_tickers(self, exchange_id: str) -> dict[str, Any]:
        """Fetch all live tickers from a CCXT exchange (cached 5 minutes)."""
        cache_key = f"tickers:{exchange_id}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached  # type: ignore[return-value]

        def _blocking_fetch_tickers() -> dict[str, Any]:
            ex = self._get_exchange(exchange_id)
            return ex.fetch_tickers()  # type: ignore[no-any-return]

        try:
            tickers: dict[str, Any] = await asyncio.get_event_loop().run_in_executor(
                None, _blocking_fetch_tickers
            )
        except Exception as exc:
            logger.error("Failed to fetch tickers from %s: %s", exchange_id, exc)
            return {}

        self._cache.set(cache_key, tickers, _TICKERS_CACHE_TTL)
        return tickers

    async def _fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1d",
        limit: int = 21,
    ) -> list[list[Any]]:
        """Fetch OHLCV candles from CCXT (cached 10 minutes)."""
        cache_key = f"ohlcv:{self._exchange_id}:{symbol}:{timeframe}:{limit}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached  # type: ignore[return-value]

        def _blocking_fetch_ohlcv() -> list[list[Any]]:
            ex = self._get_exchange(self._exchange_id)
            return ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)  # type: ignore[no-any-return]

        try:
            ohlcv: list[list[Any]] = await asyncio.get_event_loop().run_in_executor(
                None, _blocking_fetch_ohlcv
            )
        except Exception as exc:
            logger.debug("OHLCV fetch failed for %s: %s", symbol, exc)
            return []

        self._cache.set(cache_key, ohlcv, _OHLCV_CACHE_TTL)
        return ohlcv

    async def _check_above_50ema(self, symbol: str) -> bool:
        """Return True if the current price is above the 50-period daily EMA."""
        import pandas as pd

        ohlcv = await self._fetch_ohlcv(symbol, timeframe="1d", limit=60)
        if len(ohlcv) < 50:
            return False

        def _compute_ema() -> bool:
            closes = pd.Series([float(c[4]) for c in ohlcv])
            ema50 = closes.ewm(span=50, adjust=False).mean().iloc[-1]
            return float(closes.iloc[-1]) > float(ema50)

        try:
            result: bool = await asyncio.get_event_loop().run_in_executor(None, _compute_ema)
            return result
        except Exception:
            return False
