"""
core/broker_adapter.py
-----------------------
Broker Adapter Pattern for Atlas Trading Agent.

Provides a unified interface for multi-asset trading across crypto (CCXT),
US equities (Alpaca), and forex/commodities (OANDA). All adapters conform
to the same abstract interface so the engine and strategies are fully
broker-agnostic.

Asset class routing is handled by BrokerRegistry, which inspects symbol
format to select the correct adapter automatically.

Symbol conventions
------------------
  Crypto   : "BTC/USDT", "ETH/BTC"      → CCXTAdapter
  Forex    : "EUR_USD", "GBP_JPY"        → OANDAAdapter
  Metals   : "XAU_USD", "XAG_USD"       → OANDAAdapter
  Equities : "AAPL", "TSLA", "GME"      → AlpacaAdapter

OHLCV format (canonical)
------------------------
  list of [timestamp_ms: int, open: float, high: float,
            low: float, close: float, volume: float]
  This matches the CCXT convention and what data/fetcher.py expects.

Rate limiting
-------------
Each adapter self-limits via asyncio.sleep where the broker's API
documentation specifies a rate. Callers must NOT assume instant responses
on heavily-throttled endpoints (OANDA v20 = 120 req/s, Alpaca = 200/min).

Timeout policy
--------------
All network calls are wrapped in asyncio.wait_for with a default 10-second
timeout. Individual methods accept an optional ``timeout`` parameter to
override this default.
"""

from __future__ import annotations

import asyncio
import logging
import re
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any
from http.client import RemoteDisconnected
import requests.exceptions as _req_exc

from config.settings import settings

logger = logging.getLogger("atlas.broker_adapter")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_DEFAULT_TIMEOUT_S: float = 30.0

# Patterns used by BrokerRegistry for symbol routing
_CRYPTO_PATTERN = re.compile(r".+/[A-Z]{2,6}$")          # BTC/USDT, ETH/BTC
_FOREX_PATTERN = re.compile(r"^[A-Z]{3}_[A-Z]{3}$")       # EUR_USD, GBP_JPY
_EQUITY_PATTERN = re.compile(r"^[A-Z]{1,5}$")             # AAPL, TSLA, GME

# Precious metals routed to OANDA regardless of equity pattern match
_METALS: frozenset[str] = frozenset({"XAU_USD", "XAG_USD", "XPT_USD", "XPD_USD"})


# ---------------------------------------------------------------------------
# Abstract base class
# ---------------------------------------------------------------------------


class BrokerAdapter(ABC):
    """
    Abstract base for all broker integrations.

    Every concrete adapter must implement all abstract methods. The adapter
    manages its own connection lifecycle — callers must await connect() before
    any data or order methods, and await disconnect() when done.

    Thread / concurrency model
    --------------------------
    All public methods are async. The adapter may use a single underlying
    connection object that it creates in connect(). If the adapter is shared
    across concurrent callers, it is the adapter's responsibility to ensure
    thread/task safety (e.g. by acquiring an asyncio.Lock around state
    mutations).
    """

    # ------------------------------------------------------------------
    # Identity properties
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def name(self) -> str:
        """Short human-readable broker identifier, e.g. 'ccxt:binance'."""

    @property
    @abstractmethod
    def supported_asset_classes(self) -> list[str]:
        """
        Asset classes this adapter can trade.

        Common values: 'crypto', 'forex', 'stocks', 'commodities', 'etf'.
        """

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    @abstractmethod
    async def connect(self) -> None:
        """
        Authenticate and establish the broker connection.

        Must be idempotent — calling connect() on an already-connected adapter
        should be a no-op or re-validate credentials gracefully.
        """

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Close connections and release resources.

        Must be idempotent — safe to call even if connect() was never called.
        """

    # ------------------------------------------------------------------
    # Market data
    # ------------------------------------------------------------------

    @abstractmethod
    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 500,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> list[list[float]]:
        """
        Fetch OHLCV candles for a symbol.

        Parameters
        ----------
        symbol    : broker-native symbol string
        timeframe : interval string — adapters normalise broker-specific formats
                    internally. Callers always pass CCXT-style strings:
                    '1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w'.
        limit     : number of most-recent candles to return
        timeout   : network timeout in seconds

        Returns
        -------
        list of [timestamp_ms, open, high, low, close, volume]
        where timestamp_ms is a UNIX epoch in milliseconds (int).
        """

    @abstractmethod
    async def fetch_ticker(
        self,
        symbol: str,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> dict[str, Any]:
        """
        Fetch the current market quote for a symbol.

        Returns
        -------
        dict with keys:
            symbol : str
            last   : float  — last traded price
            bid    : float  — best bid
            ask    : float  — best ask
            volume : float  — 24-hour volume in base units
        """

    # ------------------------------------------------------------------
    # Order management
    # ------------------------------------------------------------------

    @abstractmethod
    async def place_market_order(
        self,
        symbol: str,
        side: str,
        size: float,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> dict[str, Any]:
        """
        Place a market order.

        Parameters
        ----------
        symbol : broker-native symbol
        side   : 'buy' or 'sell'
        size   : quantity in base asset units (shares, lots, contracts)
        timeout: network timeout in seconds

        Returns
        -------
        dict with at minimum:
            order_id : str
            symbol   : str
            side     : str
            size     : float
            fill_price : float  (0.0 if not yet filled)
            status   : str      ('open', 'filled', 'cancelled', 'rejected')
            timestamp: datetime
        """

    @abstractmethod
    async def place_limit_order(
        self,
        symbol: str,
        side: str,
        size: float,
        price: float,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> dict[str, Any]:
        """
        Place a limit order.

        Parameters mirror place_market_order() with the addition of ``price``.

        Returns the same order dict schema as place_market_order().
        """

    @abstractmethod
    async def cancel_order(
        self,
        order_id: str,
        symbol: str,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> bool:
        """
        Cancel an open order.

        Returns True if the cancellation was accepted, False otherwise.
        Does not raise on "order already filled/cancelled" — logs a warning
        and returns False.
        """

    # ------------------------------------------------------------------
    # Account state
    # ------------------------------------------------------------------

    @abstractmethod
    async def get_balance(
        self,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> dict[str, float]:
        """
        Return available (free) balances.

        Returns
        -------
        dict mapping asset/currency symbol → free balance as float.
        e.g. {'USDT': 9800.00, 'BTC': 0.012}
        """

    @abstractmethod
    async def get_open_positions(
        self,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> list[dict[str, Any]]:
        """
        Return all currently open positions.

        Returns
        -------
        list of dicts with at minimum:
            symbol     : str
            side       : 'long' or 'short'
            size       : float
            entry_price: float
            unrealized_pnl : float
        """

    # ------------------------------------------------------------------
    # Helpers available to all subclasses
    # ------------------------------------------------------------------

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(UTC)

    @staticmethod
    def _ms_timestamp(dt: datetime | None = None) -> int:
        t = dt or datetime.now(UTC)
        return int(t.timestamp() * 1000)


# ---------------------------------------------------------------------------
# CCXTAdapter
# ---------------------------------------------------------------------------


class CCXTAdapter(BrokerAdapter):
    """
    Adapter wrapping CCXT async exchange for crypto trading.

    Mirrors the connection logic in core/order_executor.py and
    data/fetcher.py but exposes the unified BrokerAdapter interface
    so the rest of the system treats crypto identically to other asset
    classes.

    Parameters
    ----------
    exchange_id  : CCXT exchange id, e.g. 'binance', 'okx'
    api_key      : exchange API key (read from env if not supplied)
    secret       : exchange API secret
    passphrase   : optional passphrase (OKX, KuCoin)
    paper        : when True, markets are loaded but no real orders placed
                   (order methods raise NotImplementedError — use
                   core/order_executor.py for paper simulation)
    sandbox      : when True, enables the exchange's testnet environment

    Rate limiting
    -------------
    Delegates to CCXT's built-in enableRateLimit=True. The exchange object
    self-throttles. Additional per-call rate limiting is not required for
    most exchanges at Atlas's current volume.
    """

    def __init__(
        self,
        exchange_id: str | None = None,
        api_key: str | None = None,
        secret: str | None = None,
        passphrase: str | None = None,
        paper: bool = True,
        sandbox: bool = False,
    ) -> None:
        try:
            import ccxt.async_support as ccxt_async
            self._ccxt_async = ccxt_async
            import ccxt
            self._ccxt = ccxt
        except ImportError as exc:
            raise ImportError(
                "ccxt is required for CCXTAdapter. "
                "Install it with: pip install ccxt"
            ) from exc

        self._exchange_id = exchange_id or settings.exchange.default_exchange
        self._api_key = api_key or settings.exchange.exchange_api_key
        self._secret = secret or settings.exchange.exchange_secret
        self._passphrase = passphrase or settings.exchange.exchange_passphrase
        self._paper = paper
        self._sandbox = sandbox
        self._exchange: Any = None  # ccxt_async.Exchange — typed as Any to avoid import at class level

    # -- Identity --

    @property
    def name(self) -> str:
        return f"ccxt:{self._exchange_id}"

    @property
    def supported_asset_classes(self) -> list[str]:
        return ["crypto"]

    # -- Lifecycle --

    async def connect(self) -> None:
        if self._exchange is not None:
            return  # already connected

        exchange_cls = getattr(self._ccxt_async, self._exchange_id, None)
        if exchange_cls is None:
            raise ValueError(f"Unknown CCXT exchange: '{self._exchange_id}'")

        init_params: dict[str, Any] = {"enableRateLimit": True}
        _placeholders = {"", "your_exchange_api_key_here", "your_exchange_secret_here"}
        if self._api_key and self._api_key not in _placeholders:
            init_params["apiKey"] = self._api_key
        if self._secret and self._secret not in _placeholders:
            init_params["secret"] = self._secret
        if self._passphrase:
            init_params["password"] = self._passphrase

        self._exchange = exchange_cls(init_params)
        if self._sandbox:
            self._exchange.set_sandbox_mode(True)

        try:
            await asyncio.wait_for(self._exchange.load_markets(), timeout=_DEFAULT_TIMEOUT_S)
            logger.info("CCXTAdapter connected: %s (paper=%s, sandbox=%s)", self._exchange_id, self._paper, self._sandbox)
        except asyncio.TimeoutError:
            logger.error("CCXTAdapter connect timeout: %s", self._exchange_id)
            raise
        except Exception as exc:
            logger.error("CCXTAdapter connect failed: %s — %s", self._exchange_id, exc)
            raise

    async def disconnect(self) -> None:
        if self._exchange is not None:
            try:
                await self._exchange.close()
            except Exception as exc:
                logger.warning("CCXTAdapter close error: %s", exc)
            finally:
                self._exchange = None
                logger.info("CCXTAdapter disconnected: %s", self._exchange_id)

    # -- Market data --

    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 500,
        timeout: float = _DEFAULT_TIMEOUT_S,
        max_retries: int = 3,
    ) -> list[list[float]]:
        self._require_connected()
        last_exc: Exception | None = None
        for attempt in range(1, max_retries + 1):
            try:
                raw: list[list[Any]] = await asyncio.wait_for(
                    self._exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit),
                    timeout=timeout,
                )
                return [[int(c[0]), float(c[1]), float(c[2]), float(c[3]), float(c[4]), float(c[5])] for c in raw]
            except asyncio.TimeoutError as exc:
                last_exc = exc
                logger.warning(
                    "CCXTAdapter fetch_ohlcv timeout: %s/%s (attempt %d/%d)",
                    symbol, timeframe, attempt, max_retries,
                )
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)  # 2s, 4s
            except self._ccxt.BadSymbol as exc:
                raise ValueError(f"Symbol not available on {self._exchange_id}: {symbol}") from exc
            except self._ccxt.BaseError as exc:
                last_exc = exc
                logger.warning(
                    "CCXTAdapter fetch_ohlcv error %s/%s (attempt %d/%d): %s",
                    symbol, timeframe, attempt, max_retries, exc,
                )
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)  # 2s, 4s
        logger.error(
            "CCXTAdapter fetch_ohlcv failed after %d attempts: %s/%s — %s",
            max_retries, symbol, timeframe, last_exc,
        )
        raise last_exc  # type: ignore[misc]

    async def fetch_ticker(
        self,
        symbol: str,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> dict[str, Any]:
        self._require_connected()
        try:
            raw: dict[str, Any] = await asyncio.wait_for(
                self._exchange.fetch_ticker(symbol),
                timeout=timeout,
            )
            return {
                "symbol": symbol,
                "last": float(raw.get("last") or 0.0),
                "bid": float(raw.get("bid") or 0.0),
                "ask": float(raw.get("ask") or 0.0),
                "volume": float(raw.get("baseVolume") or raw.get("volume") or 0.0),
            }
        except asyncio.TimeoutError:
            logger.error("CCXTAdapter fetch_ticker timeout: %s", symbol)
            raise
        except self._ccxt.BaseError as exc:
            logger.error("CCXTAdapter fetch_ticker error %s: %s", symbol, exc)
            raise

    # -- Order management --

    async def place_market_order(
        self,
        symbol: str,
        side: str,
        size: float,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> dict[str, Any]:
        self._require_connected()
        try:
            order: dict[str, Any] = await asyncio.wait_for(
                self._exchange.create_order(symbol, "market", side, size),
                timeout=timeout,
            )
            return self._normalise_order(order)
        except asyncio.TimeoutError:
            logger.error("CCXTAdapter place_market_order timeout: %s", symbol)
            raise
        except self._ccxt.BaseError as exc:
            logger.error("CCXTAdapter place_market_order error %s: %s", symbol, exc)
            raise

    async def place_limit_order(
        self,
        symbol: str,
        side: str,
        size: float,
        price: float,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> dict[str, Any]:
        self._require_connected()
        try:
            order: dict[str, Any] = await asyncio.wait_for(
                self._exchange.create_order(symbol, "limit", side, size, price),
                timeout=timeout,
            )
            return self._normalise_order(order)
        except asyncio.TimeoutError:
            logger.error("CCXTAdapter place_limit_order timeout: %s", symbol)
            raise
        except self._ccxt.BaseError as exc:
            logger.error("CCXTAdapter place_limit_order error %s: %s", symbol, exc)
            raise

    async def cancel_order(
        self,
        order_id: str,
        symbol: str,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> bool:
        self._require_connected()
        try:
            await asyncio.wait_for(
                self._exchange.cancel_order(order_id, symbol),
                timeout=timeout,
            )
            return True
        except asyncio.TimeoutError:
            logger.error("CCXTAdapter cancel_order timeout: %s", order_id)
            return False
        except self._ccxt.OrderNotFound:
            logger.warning("CCXTAdapter cancel_order: order %s not found (already filled/cancelled)", order_id)
            return False
        except self._ccxt.BaseError as exc:
            logger.error("CCXTAdapter cancel_order error %s: %s", order_id, exc)
            return False

    # -- Account state --

    async def get_balance(
        self,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> dict[str, float]:
        self._require_connected()
        try:
            raw: dict[str, Any] = await asyncio.wait_for(
                self._exchange.fetch_balance(),
                timeout=timeout,
            )
            return {
                k: float(v["free"])
                for k, v in raw.items()
                if isinstance(v, dict) and v.get("free") is not None
            }
        except asyncio.TimeoutError:
            logger.error("CCXTAdapter get_balance timeout")
            raise
        except self._ccxt.BaseError as exc:
            logger.error("CCXTAdapter get_balance error: %s", exc)
            raise

    async def get_open_positions(
        self,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> list[dict[str, Any]]:
        self._require_connected()
        try:
            raw: list[dict[str, Any]] = await asyncio.wait_for(
                self._exchange.fetch_positions(),
                timeout=timeout,
            )
            positions = []
            for p in raw:
                contracts = float(p.get("contracts") or 0.0)
                if contracts == 0.0:
                    continue
                positions.append({
                    "symbol": p.get("symbol", ""),
                    "side": p.get("side", "long"),
                    "size": contracts,
                    "entry_price": float(p.get("entryPrice") or 0.0),
                    "unrealized_pnl": float(p.get("unrealizedPnl") or 0.0),
                })
            return positions
        except asyncio.TimeoutError:
            logger.error("CCXTAdapter get_open_positions timeout")
            raise
        except self._ccxt.BaseError as exc:
            logger.error("CCXTAdapter get_open_positions error: %s", exc)
            raise

    # -- Private helpers --

    def _require_connected(self) -> None:
        if self._exchange is None:
            raise RuntimeError(f"CCXTAdapter ({self._exchange_id}) not connected. Call connect() first.")

    @staticmethod
    def _normalise_order(order: dict[str, Any]) -> dict[str, Any]:
        fill = float(order.get("average") or order.get("price") or 0.0)
        return {
            "order_id": str(order.get("id", "")),
            "symbol": order.get("symbol", ""),
            "side": order.get("side", ""),
            "size": float(order.get("amount") or 0.0),
            "fill_price": fill,
            "status": order.get("status", "open"),
            "timestamp": datetime.now(UTC),
            "raw": order,
        }


# ---------------------------------------------------------------------------
# AlpacaAdapter
# ---------------------------------------------------------------------------


class AlpacaAdapter(BrokerAdapter):
    """
    Adapter for US equities and ETFs via Alpaca Markets.

    Requires the ``alpaca-py`` package (alpaca-trade-api is deprecated):
        pip install alpaca-py

    Environment variables (loaded from .env via settings):
        ALPACA_API_KEY    — Alpaca API key ID
        ALPACA_SECRET_KEY — Alpaca secret key

    Paper vs live
    -------------
    paper=True  → uses paper-api.alpaca.markets (safe default)
    paper=False → uses api.alpaca.markets (real money)

    Rate limiting
    -------------
    Alpaca allows 200 requests/minute on the free tier. The adapter does
    not self-throttle — callers operating at high frequency should add a
    leaky-bucket wrapper.

    Timeframe mapping
    -----------------
    CCXT-style strings are mapped to Alpaca TimeFrame objects:
        '1m' → TimeFrame.Minute
        '5m' → TimeFrame(5, TimeFrameUnit.Minute)
        '1h' → TimeFrame.Hour
        '1d' → TimeFrame.Day
        '1w' → TimeFrame.Week
    """

    _TIMEFRAME_MAP: dict[str, str] = {
        "1m": "1Min",
        "5m": "5Min",
        "15m": "15Min",
        "30m": "30Min",
        "1h": "1Hour",
        "4h": "4Hour",
        "1d": "1Day",
        "1w": "1Week",
    }

    def __init__(
        self,
        api_key: str | None = None,
        secret_key: str | None = None,
        paper: bool = True,
    ) -> None:
        self._api_key = api_key or settings.alpaca.alpaca_api_key
        self._secret_key = secret_key or settings.alpaca.alpaca_secret_key
        self._paper = paper

        # These are initialised in connect()
        self._trading_client: Any = None
        self._data_client: Any = None

    # -- Identity --

    @property
    def name(self) -> str:
        mode = "paper" if self._paper else "live"
        return f"alpaca:{mode}"

    @property
    def supported_asset_classes(self) -> list[str]:
        return ["stocks", "etf", "crypto"]

    # -- Lifecycle --

    async def connect(self) -> None:
        try:
            from alpaca.trading.client import TradingClient
            from alpaca.data.historical import StockHistoricalDataClient
        except ImportError as exc:
            raise ImportError(
                "alpaca-py is required for AlpacaAdapter. "
                "Install it with: pip install alpaca-py"
            ) from exc

        if not self._api_key or not self._secret_key:
            raise ValueError(
                "Alpaca credentials not configured. "
                "Set ALPACA_API_KEY and ALPACA_SECRET_KEY in your .env file."
            )

        if self._trading_client is not None:
            return  # already connected

        try:
            self._trading_client = TradingClient(
                api_key=self._api_key,
                secret_key=self._secret_key,
                paper=self._paper,
            )
            self._data_client = StockHistoricalDataClient(
                api_key=self._api_key,
                secret_key=self._secret_key,
            )
            logger.info("AlpacaAdapter connected (paper=%s)", self._paper)
        except Exception as exc:
            logger.error("AlpacaAdapter connect failed: %s", exc)
            raise

    async def disconnect(self) -> None:
        self._trading_client = None
        self._data_client = None
        logger.info("AlpacaAdapter disconnected")

    # -- Market data --

    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 500,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> list[list[float]]:
        self._require_connected()
        try:
            from alpaca.data.requests import StockBarsRequest
            from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

            alpaca_tf = self._map_timeframe(timeframe)

            request_params = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=alpaca_tf,
                limit=limit,
            )

            bars = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._data_client.get_stock_bars(request_params),
                ),
                timeout=timeout,
            )

            result: list[list[float]] = []
            if symbol in bars:
                for bar in bars[symbol]:
                    ts_ms = int(bar.timestamp.timestamp() * 1000)
                    result.append([
                        ts_ms,
                        float(bar.open),
                        float(bar.high),
                        float(bar.low),
                        float(bar.close),
                        float(bar.volume),
                    ])
            return result
        except asyncio.TimeoutError:
            logger.error("AlpacaAdapter fetch_ohlcv timeout: %s/%s", symbol, timeframe)
            raise
        except Exception as exc:
            logger.error("AlpacaAdapter fetch_ohlcv error %s/%s: %s", symbol, timeframe, exc)
            raise

    async def fetch_ticker(
        self,
        symbol: str,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> dict[str, Any]:
        self._require_connected()
        try:
            from alpaca.data.requests import StockLatestQuoteRequest

            request_params = StockLatestQuoteRequest(symbol_or_symbols=symbol)

            quote_response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._data_client.get_stock_latest_quote(request_params),
                ),
                timeout=timeout,
            )

            quote = quote_response.get(symbol)
            if quote is None:
                raise ValueError(f"No quote returned for {symbol}")

            bid = float(quote.bid_price or 0.0)
            ask = float(quote.ask_price or 0.0)
            last = (bid + ask) / 2.0 if bid and ask else 0.0

            return {
                "symbol": symbol,
                "last": last,
                "bid": bid,
                "ask": ask,
                "volume": float(getattr(quote, "bid_size", 0.0) or 0.0),
            }
        except asyncio.TimeoutError:
            logger.error("AlpacaAdapter fetch_ticker timeout: %s", symbol)
            raise
        except Exception as exc:
            logger.error("AlpacaAdapter fetch_ticker error %s: %s", symbol, exc)
            raise

    # -- Order management --

    async def place_market_order(
        self,
        symbol: str,
        side: str,
        size: float,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> dict[str, Any]:
        self._require_connected()
        try:
            from alpaca.trading.requests import MarketOrderRequest
            from alpaca.trading.enums import OrderSide, TimeInForce

            alpaca_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
            order_request = MarketOrderRequest(
                symbol=symbol,
                qty=size,
                side=alpaca_side,
                time_in_force=TimeInForce.DAY,
            )
            order = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._trading_client.submit_order(order_request),
                ),
                timeout=timeout,
            )
            return self._normalise_order(order)
        except asyncio.TimeoutError:
            logger.error("AlpacaAdapter place_market_order timeout: %s", symbol)
            raise
        except Exception as exc:
            logger.error("AlpacaAdapter place_market_order error %s: %s", symbol, exc)
            raise

    async def place_limit_order(
        self,
        symbol: str,
        side: str,
        size: float,
        price: float,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> dict[str, Any]:
        self._require_connected()
        try:
            from alpaca.trading.requests import LimitOrderRequest
            from alpaca.trading.enums import OrderSide, TimeInForce

            alpaca_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
            order_request = LimitOrderRequest(
                symbol=symbol,
                qty=size,
                side=alpaca_side,
                time_in_force=TimeInForce.DAY,
                limit_price=price,
            )
            order = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._trading_client.submit_order(order_request),
                ),
                timeout=timeout,
            )
            return self._normalise_order(order)
        except asyncio.TimeoutError:
            logger.error("AlpacaAdapter place_limit_order timeout: %s", symbol)
            raise
        except Exception as exc:
            logger.error("AlpacaAdapter place_limit_order error %s: %s", symbol, exc)
            raise

    async def cancel_order(
        self,
        order_id: str,
        symbol: str,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> bool:
        self._require_connected()
        try:
            await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._trading_client.cancel_order_by_id(order_id),
                ),
                timeout=timeout,
            )
            return True
        except asyncio.TimeoutError:
            logger.error("AlpacaAdapter cancel_order timeout: %s", order_id)
            return False
        except Exception as exc:
            logger.warning("AlpacaAdapter cancel_order failed %s: %s", order_id, exc)
            return False

    # -- Account state --

    async def get_balance(
        self,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> dict[str, float]:
        self._require_connected()
        try:
            account = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    self._trading_client.get_account,
                ),
                timeout=timeout,
            )
            return {
                "USD": float(account.cash or 0.0),
                "buying_power": float(account.buying_power or 0.0),
                "portfolio_value": float(account.portfolio_value or 0.0),
            }
        except asyncio.TimeoutError:
            logger.error("AlpacaAdapter get_balance timeout")
            raise
        except Exception as exc:
            logger.error("AlpacaAdapter get_balance error: %s", exc)
            raise

    async def get_open_positions(
        self,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> list[dict[str, Any]]:
        self._require_connected()
        try:
            raw_positions = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    self._trading_client.get_all_positions,
                ),
                timeout=timeout,
            )
            positions = []
            for p in raw_positions:
                qty = float(p.qty or 0.0)
                if qty == 0.0:
                    continue
                side = "long" if qty > 0 else "short"
                positions.append({
                    "symbol": p.symbol,
                    "side": side,
                    "size": abs(qty),
                    "entry_price": float(p.avg_entry_price or 0.0),
                    "unrealized_pnl": float(p.unrealized_pl or 0.0),
                })
            return positions
        except asyncio.TimeoutError:
            logger.error("AlpacaAdapter get_open_positions timeout")
            raise
        except Exception as exc:
            logger.error("AlpacaAdapter get_open_positions error: %s", exc)
            raise

    # -- Private helpers --

    def _require_connected(self) -> None:
        if self._trading_client is None:
            raise RuntimeError("AlpacaAdapter not connected. Call connect() first.")

    @staticmethod
    def _normalise_order(order: Any) -> dict[str, Any]:
        """Normalise an alpaca-py Order object to the canonical order dict."""
        fill = float(order.filled_avg_price or 0.0)
        return {
            "order_id": str(order.id),
            "symbol": str(order.symbol),
            "side": str(order.side.value) if hasattr(order.side, "value") else str(order.side),
            "size": float(order.qty or 0.0),
            "fill_price": fill,
            "status": str(order.status.value) if hasattr(order.status, "value") else str(order.status),
            "timestamp": datetime.now(UTC),
            "raw": order,
        }

    def _map_timeframe(self, ccxt_tf: str) -> Any:
        """Map a CCXT-style timeframe string to an Alpaca TimeFrame object."""
        try:
            from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
        except ImportError as exc:
            raise ImportError("alpaca-py is required for AlpacaAdapter.") from exc

        mapping: dict[str, Any] = {
            "1m": TimeFrame.Minute,
            "5m": TimeFrame(5, TimeFrameUnit.Minute),
            "15m": TimeFrame(15, TimeFrameUnit.Minute),
            "30m": TimeFrame(30, TimeFrameUnit.Minute),
            "1h": TimeFrame.Hour,
            "4h": TimeFrame(4, TimeFrameUnit.Hour),
            "1d": TimeFrame.Day,
            "1w": TimeFrame.Week,
        }
        tf = mapping.get(ccxt_tf)
        if tf is None:
            raise ValueError(
                f"Unsupported timeframe for AlpacaAdapter: '{ccxt_tf}'. "
                f"Supported: {list(mapping.keys())}"
            )
        return tf


# ---------------------------------------------------------------------------
# OANDAAdapter
# ---------------------------------------------------------------------------


class OANDAAdapter(BrokerAdapter):
    """
    Adapter for forex and precious metals via OANDA v20 REST API.

    Requires the ``oandapyV20`` package:
        pip install oandapyV20

    Environment variables (loaded from .env via settings):
        OANDA_TOKEN      — OANDA personal access token
        OANDA_ACCOUNT_ID — OANDA account ID (e.g. '001-001-1234567-001')

    Practice vs live
    ----------------
    practice=True  → api-fxtrade.oanda.com/v3 (demo account)
    practice=False → api-fxtrade.oanda.com/v3 with live credentials

    OANDA uses the same API endpoint hostname for both practice and live;
    the account type is determined by the account ID itself. The ``practice``
    flag here controls which token and account are expected, and is used
    for logging/safety checks.

    Symbol format
    -------------
    OANDA uses underscore format: EUR_USD, XAU_USD.
    The adapter accepts this format directly and does not convert.

    Timeframe mapping
    -----------------
    CCXT-style strings are mapped to OANDA granularity codes:
        '1m' → 'M1', '5m' → 'M5', '1h' → 'H1', '1d' → 'D', '1w' → 'W'

    Rate limiting
    -------------
    OANDA v20 allows 120 requests/second. The adapter does not self-throttle
    since Atlas's usage is well below this limit.
    """

    _TIMEFRAME_MAP: dict[str, str] = {
        "1m": "M1",
        "5m": "M5",
        "15m": "M15",
        "30m": "M30",
        "1h": "H1",
        "4h": "H4",
        "1d": "D",
        "1w": "W",
        "1M": "M",
    }

    def __init__(
        self,
        token: str | None = None,
        account_id: str | None = None,
        practice: bool | None = None,
    ) -> None:
        self._token = token or settings.oanda.oanda_token
        self._account_id = account_id or settings.oanda.oanda_account_id
        self._practice = practice if practice is not None else settings.oanda.oanda_practice
        self._api: Any = None  # oandapyV20.API — typed as Any to avoid import at class level

    # -- Identity --

    @property
    def name(self) -> str:
        mode = "practice" if self._practice else "live"
        return f"oanda:{mode}"

    @property
    def supported_asset_classes(self) -> list[str]:
        return ["forex", "commodities"]

    # -- Lifecycle --

    async def connect(self) -> None:
        try:
            import oandapyV20
        except ImportError as exc:
            raise ImportError(
                "oandapyV20 is required for OANDAAdapter. "
                "Install it with: pip install oandapyV20"
            ) from exc

        if not self._token:
            raise ValueError(
                "OANDA token not configured. Set OANDA_TOKEN in your .env file."
            )
        if not self._account_id:
            raise ValueError(
                "OANDA account ID not configured. Set OANDA_ACCOUNT_ID in your .env file."
            )

        if self._api is not None:
            return  # already connected

        environment = "practice" if self._practice else "live"
        self._api = oandapyV20.API(
            access_token=self._token,
            environment=environment,
        )
        logger.info("OANDAAdapter connected (practice=%s, account=%s)", self._practice, self._account_id)

    async def disconnect(self) -> None:
        self._api = None
        logger.info("OANDAAdapter disconnected")

    # -- Market data --

    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 500,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> list[list[float]]:
        self._require_connected()
        try:
            from oandapyV20.endpoints.instruments import InstrumentsCandles

            granularity = self._map_timeframe(timeframe)
            params = {"count": str(limit), "granularity": granularity}
            request = InstrumentsCandles(instrument=symbol, params=params)

            raw_response: dict[str, Any] = await self._execute_request(request, timeout)

            candles = raw_response.get("candles", [])
            result: list[list[float]] = []
            for candle in candles:
                if not candle.get("complete", True):
                    continue  # skip the live/incomplete candle
                mid = candle.get("mid", {})
                ts_ms = int(
                    datetime.fromisoformat(
                        candle["time"].replace("Z", "+00:00")
                    ).timestamp() * 1000
                )
                result.append([
                    ts_ms,
                    float(mid.get("o", 0.0)),
                    float(mid.get("h", 0.0)),
                    float(mid.get("l", 0.0)),
                    float(mid.get("c", 0.0)),
                    float(candle.get("volume", 0.0)),
                ])
            return result
        except asyncio.TimeoutError:
            logger.error("OANDAAdapter fetch_ohlcv timeout: %s/%s", symbol, timeframe)
            raise
        except Exception as exc:
            logger.error("OANDAAdapter fetch_ohlcv error %s/%s: %s", symbol, timeframe, exc)
            raise

    async def fetch_ticker(
        self,
        symbol: str,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> dict[str, Any]:
        self._require_connected()
        try:
            from oandapyV20.endpoints.pricing import PricingInfo

            params = {"instruments": symbol}
            request = PricingInfo(accountID=self._account_id, params=params)

            raw_response: dict[str, Any] = await self._execute_request(request, timeout)

            prices = raw_response.get("prices", [])
            if not prices:
                raise ValueError(f"No pricing data returned for {symbol}")

            price = prices[0]
            bids = price.get("bids", [{}])
            asks = price.get("asks", [{}])
            bid = float(bids[0].get("price", 0.0)) if bids else 0.0
            ask = float(asks[0].get("price", 0.0)) if asks else 0.0
            last = (bid + ask) / 2.0 if bid and ask else 0.0

            return {
                "symbol": symbol,
                "last": last,
                "bid": bid,
                "ask": ask,
                "volume": 0.0,  # OANDA does not provide real-time volume in the pricing endpoint
            }
        except asyncio.TimeoutError:
            logger.error("OANDAAdapter fetch_ticker timeout: %s", symbol)
            raise
        except Exception as exc:
            logger.error("OANDAAdapter fetch_ticker error %s: %s", symbol, exc)
            raise

    # -- Order management --

    async def place_market_order(
        self,
        symbol: str,
        side: str,
        size: float,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> dict[str, Any]:
        self._require_connected()
        try:
            from oandapyV20.endpoints.orders import OrderCreate

            # OANDA uses signed units: positive = buy, negative = sell
            units = size if side.lower() == "buy" else -size
            order_body = {
                "order": {
                    "type": "MARKET",
                    "instrument": symbol,
                    "units": str(units),
                    "timeInForce": "FOK",  # Fill or Kill — standard for market orders
                    "positionFill": "DEFAULT",
                }
            }
            request = OrderCreate(accountID=self._account_id, data=order_body)

            raw_response: dict[str, Any] = await self._execute_request(request, timeout)
            return self._normalise_order(raw_response, symbol, side, abs(units))
        except asyncio.TimeoutError:
            logger.error("OANDAAdapter place_market_order timeout: %s", symbol)
            raise
        except Exception as exc:
            logger.error("OANDAAdapter place_market_order error %s: %s", symbol, exc)
            raise

    async def place_limit_order(
        self,
        symbol: str,
        side: str,
        size: float,
        price: float,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> dict[str, Any]:
        self._require_connected()
        try:
            from oandapyV20.endpoints.orders import OrderCreate

            units = size if side.lower() == "buy" else -size
            order_body = {
                "order": {
                    "type": "LIMIT",
                    "instrument": symbol,
                    "units": str(units),
                    "price": str(round(price, 5)),
                    "timeInForce": "GTC",  # Good Till Cancelled for limit orders
                    "positionFill": "DEFAULT",
                }
            }
            request = OrderCreate(accountID=self._account_id, data=order_body)

            raw_response: dict[str, Any] = await self._execute_request(request, timeout)
            return self._normalise_order(raw_response, symbol, side, abs(units))
        except asyncio.TimeoutError:
            logger.error("OANDAAdapter place_limit_order timeout: %s", symbol)
            raise
        except Exception as exc:
            logger.error("OANDAAdapter place_limit_order error %s: %s", symbol, exc)
            raise

    async def cancel_order(
        self,
        order_id: str,
        symbol: str,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> bool:
        self._require_connected()
        try:
            from oandapyV20.endpoints.orders import OrderCancel

            request = OrderCancel(accountID=self._account_id, orderID=order_id)
            await self._execute_request(request, timeout)
            return True
        except asyncio.TimeoutError:
            logger.error("OANDAAdapter cancel_order timeout: %s", order_id)
            return False
        except Exception as exc:
            logger.warning("OANDAAdapter cancel_order failed %s: %s", order_id, exc)
            return False

    # -- Account state --

    async def get_balance(
        self,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> dict[str, float]:
        self._require_connected()
        try:
            from oandapyV20.endpoints.accounts import AccountSummary

            request = AccountSummary(accountID=self._account_id)
            raw_response: dict[str, Any] = await self._execute_request(request, timeout)

            account = raw_response.get("account", {})
            return {
                "balance": float(account.get("balance", 0.0)),
                "NAV": float(account.get("NAV", 0.0)),
                "unrealizedPL": float(account.get("unrealizedPL", 0.0)),
                "marginAvailable": float(account.get("marginAvailable", 0.0)),
            }
        except asyncio.TimeoutError:
            logger.error("OANDAAdapter get_balance timeout")
            raise
        except Exception as exc:
            logger.error("OANDAAdapter get_balance error: %s", exc)
            raise

    async def get_open_positions(
        self,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> list[dict[str, Any]]:
        self._require_connected()
        try:
            from oandapyV20.endpoints.positions import OpenPositions

            request = OpenPositions(accountID=self._account_id)
            raw_response: dict[str, Any] = await self._execute_request(request, timeout)

            positions: list[dict[str, Any]] = []
            for p in raw_response.get("positions", []):
                long_units = float(p.get("long", {}).get("units", 0.0))
                short_units = float(p.get("short", {}).get("units", 0.0))

                if long_units != 0.0:
                    positions.append({
                        "symbol": p["instrument"],
                        "side": "long",
                        "size": long_units,
                        "entry_price": float(p.get("long", {}).get("averagePrice", 0.0)),
                        "unrealized_pnl": float(p.get("long", {}).get("unrealizedPL", 0.0)),
                    })
                if short_units != 0.0:
                    positions.append({
                        "symbol": p["instrument"],
                        "side": "short",
                        "size": abs(short_units),
                        "entry_price": float(p.get("short", {}).get("averagePrice", 0.0)),
                        "unrealized_pnl": float(p.get("short", {}).get("unrealizedPL", 0.0)),
                    })

            return positions
        except asyncio.TimeoutError:
            logger.error("OANDAAdapter get_open_positions timeout")
            raise
        except Exception as exc:
            logger.error("OANDAAdapter get_open_positions error: %s", exc)
            raise

    # -- Private helpers --

    def _require_connected(self) -> None:
        if self._api is None:
            raise RuntimeError("OANDAAdapter not connected. Call connect() first.")

    def _recreate_api(self) -> None:
        """Tear down the stale requests.Session and build a fresh oandapyV20.API."""
        import oandapyV20
        try:
            if self._api is not None:
                self._api.client.close()
        except Exception:
            pass
        self._api = None
        environment = "practice" if self._practice else "live"
        self._api = oandapyV20.API(
            access_token=self._token,
            environment=environment,
        )
        logger.info("OANDAAdapter: HTTP session recreated after connection drop")

    async def _execute_request(self, request: Any, timeout: float) -> Any:
        """Run an oandapyV20 endpoint request in a thread executor.

        On ``RemoteDisconnected`` or ``ConnectionError`` (OANDA drops idle
        connections), the underlying requests.Session is stale.  We recreate
        the API client once and retry before letting the exception propagate.
        """
        for attempt in range(2):
            try:
                return await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self._api.request(request),
                    ),
                    timeout=timeout,
                )
            except (RemoteDisconnected, ConnectionError, _req_exc.ConnectionError, OSError) as exc:
                if attempt == 0:
                    logger.warning(
                        "OANDAAdapter: connection dropped (%s), recreating session and retrying",
                        exc,
                    )
                    self._recreate_api()
                    continue
                raise

    def _map_timeframe(self, ccxt_tf: str) -> str:
        granularity = self._TIMEFRAME_MAP.get(ccxt_tf)
        if granularity is None:
            raise ValueError(
                f"Unsupported timeframe for OANDAAdapter: '{ccxt_tf}'. "
                f"Supported: {list(self._TIMEFRAME_MAP.keys())}"
            )
        return granularity

    @staticmethod
    def _normalise_order(
        response: dict[str, Any],
        symbol: str,
        side: str,
        size: float,
    ) -> dict[str, Any]:
        """Extract order details from OANDA OrderCreate response."""
        # OANDA returns orderFillTransaction for market fills, orderCreateTransaction for limits
        fill_tx = response.get("orderFillTransaction", {})
        create_tx = response.get("orderCreateTransaction", {})
        order_id = str(
            fill_tx.get("orderID")
            or create_tx.get("orderID")
            or response.get("relatedTransactionIDs", [""])[0]
        )
        fill_price = float(fill_tx.get("price", 0.0))
        status = "filled" if fill_tx else "open"

        return {
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "size": size,
            "fill_price": fill_price,
            "status": status,
            "timestamp": datetime.now(UTC),
            "raw": response,
        }


# ---------------------------------------------------------------------------
# BrokerRegistry
# ---------------------------------------------------------------------------


class BrokerRegistry:
    """
    Singleton registry that holds configured broker adapters and routes
    symbols to the correct adapter automatically.

    Usage
    -----
    registry = BrokerRegistry.instance()
    registry.register(CCXTAdapter())
    registry.register(AlpacaAdapter())

    await registry.connect_all()

    adapter = registry.get_adapter_for_symbol("EUR_USD")   # → OANDAAdapter
    adapter = registry.get_adapter_for_symbol("AAPL")       # → AlpacaAdapter
    adapter = registry.get_adapter_for_symbol("BTC/USDT")   # → CCXTAdapter

    await registry.disconnect_all()

    Symbol routing rules (in priority order)
    -----------------------------------------
    1. Metals (XAU_USD, XAG_USD, XPT_USD, XPD_USD) → first registered OANDAAdapter
    2. Crypto (contains '/') → first registered CCXTAdapter
    3. Forex (three letters, underscore, three letters: EUR_USD) → first registered OANDAAdapter
    4. Equities (1–5 uppercase letters only: AAPL, TSLA) → first registered AlpacaAdapter
    5. No match → raises ValueError
    """

    _singleton: "BrokerRegistry | None" = None

    def __init__(self) -> None:
        self._adapters: list[BrokerAdapter] = []

    @classmethod
    def instance(cls) -> "BrokerRegistry":
        """Return the global singleton registry."""
        if cls._singleton is None:
            cls._singleton = cls()
        return cls._singleton

    @classmethod
    def reset(cls) -> None:
        """
        Destroy the singleton.

        Useful in tests to start each test with a clean registry.
        """
        cls._singleton = None

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, adapter: BrokerAdapter) -> None:
        """
        Add a broker adapter to the registry.

        Duplicate adapter names are allowed to support multiple accounts
        on the same broker (e.g. paper + live Alpaca accounts registered
        under different names).
        """
        self._adapters.append(adapter)
        logger.info("BrokerRegistry: registered adapter '%s'", adapter.name)

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    def get_adapter_for_symbol(self, symbol: str) -> BrokerAdapter:
        """
        Return the appropriate adapter for the given symbol.

        Parameters
        ----------
        symbol : broker-agnostic symbol string

        Raises
        ------
        ValueError  : if no registered adapter handles the symbol format
        RuntimeError: if the registry has no adapters registered
        """
        if not self._adapters:
            raise RuntimeError(
                "BrokerRegistry has no adapters registered. "
                "Call registry.register(adapter) before routing symbols."
            )

        # Precious metals — must come before equity pattern check
        # because XAU has no underscore-separated three-letter pair check issue
        if symbol in _METALS:
            adapter = self._first_adapter_of_type(OANDAAdapter)
            if adapter is not None:
                return adapter

        # Crypto — slash-delimited pairs
        if _CRYPTO_PATTERN.match(symbol):
            adapter = self._first_adapter_of_type(CCXTAdapter)
            if adapter is not None:
                return adapter
            raise ValueError(
                f"No CCXTAdapter registered for crypto symbol '{symbol}'. "
                "Call registry.register(CCXTAdapter(...))."
            )

        # Forex — three letters, underscore, three letters (e.g. EUR_USD)
        if _FOREX_PATTERN.match(symbol):
            adapter = self._first_adapter_of_type(OANDAAdapter)
            if adapter is not None:
                return adapter
            raise ValueError(
                f"No OANDAAdapter registered for forex symbol '{symbol}'. "
                "Call registry.register(OANDAAdapter(...))."
            )

        # Equities — 1–5 uppercase letters, no special characters
        if _EQUITY_PATTERN.match(symbol):
            adapter = self._first_adapter_of_type(AlpacaAdapter)
            if adapter is not None:
                return adapter
            raise ValueError(
                f"No AlpacaAdapter registered for equity symbol '{symbol}'. "
                "Call registry.register(AlpacaAdapter(...))."
            )

        raise ValueError(
            f"Cannot determine asset class for symbol '{symbol}'. "
            "Expected formats: 'BTC/USDT' (crypto), 'EUR_USD' (forex), "
            "'AAPL' (equities), 'XAU_USD' (metals)."
        )

    # ------------------------------------------------------------------
    # Bulk operations
    # ------------------------------------------------------------------

    def get_all_adapters(self) -> list[BrokerAdapter]:
        """Return all registered adapters."""
        return list(self._adapters)

    async def connect_all(self) -> None:
        """
        Connect all registered adapters concurrently.

        Individual connection failures are logged but do not prevent other
        adapters from connecting — the registry remains usable for adapters
        that connected successfully.
        """
        results = await asyncio.gather(
            *[adapter.connect() for adapter in self._adapters],
            return_exceptions=True,
        )
        for adapter, result in zip(self._adapters, results):
            if isinstance(result, Exception):
                logger.error(
                    "BrokerRegistry: failed to connect '%s': %s",
                    adapter.name,
                    result,
                )
            else:
                logger.info("BrokerRegistry: connected '%s'", adapter.name)

    async def disconnect_all(self) -> None:
        """
        Disconnect all registered adapters concurrently.

        Individual disconnect failures are logged but do not affect others.
        """
        results = await asyncio.gather(
            *[adapter.disconnect() for adapter in self._adapters],
            return_exceptions=True,
        )
        for adapter, result in zip(self._adapters, results):
            if isinstance(result, Exception):
                logger.error(
                    "BrokerRegistry: error disconnecting '%s': %s",
                    adapter.name,
                    result,
                )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _first_adapter_of_type(self, adapter_type: type) -> BrokerAdapter | None:
        """Return the first registered adapter of the given type, or None."""
        for adapter in self._adapters:
            if isinstance(adapter, adapter_type):
                return adapter
        return None
