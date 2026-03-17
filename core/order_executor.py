"""
core/order_executor.py
-----------------------
Order Execution Engine for Atlas Trading Agent.

Supports two modes:
  PAPER — simulates fills locally with realistic slippage; no real money at risk.
  LIVE  — routes orders through CCXT to the configured exchange.

The executor is deliberately mode-explicit: callers pass ``mode`` on every
call so there is never any ambiguity about which path is taken.  The LIVE path
is additionally guarded by the ExchangeSettings ``confirm_live`` flag — if that
flag is False, live orders are rejected at the settings layer before reaching
the exchange.

Retry logic
-----------
Every order attempt retries up to MAX_RETRIES times with exponential back-off
(1 s, 2 s, 4 s) before giving up and raising.

Slippage model (PAPER)
----------------------
Slippage is sampled uniformly from [0.05%, 0.15%] and always moves against the
trader (i.e. worse fill for both buys and sells).
"""

from __future__ import annotations

import asyncio
import logging
import random
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import ccxt
import ccxt.async_support as ccxt_async

from config.settings import settings
from strategies.base import Direction, ExitReason, Position, TradeResult

logger = logging.getLogger("atlas.executor")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MAX_RETRIES: int = 3
_RETRY_BASE_DELAY_S: float = 1.0
_SLIPPAGE_MIN_PCT: float = 0.0005   # 0.05 %
_SLIPPAGE_MAX_PCT: float = 0.0015   # 0.15 %
_DEFAULT_MAKER_FEE: float = 0.001   # 0.10 %
_DEFAULT_TAKER_FEE: float = 0.001   # 0.10 %


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ExecutionMode(str, Enum):
    PAPER = "PAPER"
    LIVE = "LIVE"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class OrderRequest:
    """Everything the executor needs to place or simulate an order."""

    symbol: str
    side: str           # "buy" or "sell"
    order_type: OrderType
    quantity: float
    price: float | None = None        # required for limit/stop/tp orders
    stop_price: float | None = None   # trigger price for stop orders
    trailing_offset: float | None = None  # % or price offset for trailing stop
    client_order_id: str = field(default_factory=lambda: f"atlas_{int(datetime.now(UTC).timestamp() * 1000)}")


@dataclass
class ExecutionRecord:
    """Full record of an executed (or simulated) order."""

    order_id: str
    symbol: str
    side: str
    order_type: OrderType
    requested_quantity: float
    filled_quantity: float
    requested_price: float | None
    fill_price: float
    fee: float          # in quote currency
    mode: ExecutionMode
    timestamp: datetime
    success: bool
    error: str = ""
    raw_response: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# OrderExecutor
# ---------------------------------------------------------------------------


class OrderExecutor:
    """
    Unified order execution engine.

    Parameters
    ----------
    mode          : ExecutionMode.PAPER or ExecutionMode.LIVE
    maker_fee_pct : maker fee fraction (default 0.001)
    taker_fee_pct : taker fee fraction (default 0.001)

    In PAPER mode the exchange object is never touched.
    In LIVE mode an async CCXT exchange client is initialised on first use
    (lazy init to avoid blocking startup).
    """

    def __init__(
        self,
        mode: ExecutionMode | None = None,
        maker_fee_pct: float = _DEFAULT_MAKER_FEE,
        taker_fee_pct: float = _DEFAULT_TAKER_FEE,
    ) -> None:
        if mode is None:
            mode = ExecutionMode.PAPER if settings.is_paper else ExecutionMode.LIVE

        if mode == ExecutionMode.LIVE and not settings.is_live:
            raise RuntimeError(
                "Attempted to create LIVE OrderExecutor but settings.is_live is False. "
                "Set PAPER_TRADE=false AND CONFIRM_LIVE=true in your .env to enable live trading."
            )

        self.mode = mode
        self.maker_fee_pct = maker_fee_pct
        self.taker_fee_pct = taker_fee_pct

        # Paper trading state
        self._paper_positions: dict[str, Position] = {}
        self._paper_balance: dict[str, float] = {"USDT": 10_000.0}

        # CCXT exchange (lazy — only created for LIVE)
        self._exchange: ccxt_async.Exchange | None = None

        logger.info("OrderExecutor initialised in %s mode", mode.value)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        """
        Establish the exchange connection.  Must be called before any LIVE
        order.  Safe to call in PAPER mode (no-op).
        """
        if self.mode != ExecutionMode.LIVE:
            return

        exchange_id = settings.exchange.default_exchange
        exchange_cls = getattr(ccxt_async, exchange_id, None)
        if exchange_cls is None:
            raise ValueError(f"Unknown CCXT exchange: '{exchange_id}'")

        init_params: dict[str, str] = {}
        if settings.exchange.exchange_api_key:
            init_params["apiKey"] = settings.exchange.exchange_api_key
        if settings.exchange.exchange_secret:
            init_params["secret"] = settings.exchange.exchange_secret
        if settings.exchange.exchange_passphrase:
            init_params["password"] = settings.exchange.exchange_passphrase

        self._exchange = exchange_cls(init_params)
        await self._exchange.load_markets()
        logger.info("Connected to %s (LIVE)", exchange_id)

    async def close(self) -> None:
        """Close the async exchange session gracefully."""
        if self._exchange is not None:
            await self._exchange.close()
            self._exchange = None

    # ------------------------------------------------------------------
    # Core execution methods
    # ------------------------------------------------------------------

    async def execute_trade(
        self,
        signal_symbol: str,
        signal_direction: Direction,
        size: float,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        strategy_name: str,
        order_type: OrderType = OrderType.MARKET,
        limit_price: float | None = None,
    ) -> tuple[ExecutionRecord, Position | None]:
        """
        Open a new position.

        Returns (ExecutionRecord, Position).  Position is None on failure.
        In PAPER mode the fill is immediate at entry_price ± slippage.
        In LIVE mode a real order is placed via CCXT.

        Parameters
        ----------
        signal_symbol    : e.g. "BTC/USDT"
        signal_direction : Direction.LONG or Direction.SHORT
        size             : quantity in base asset units
        entry_price      : expected fill price (used for paper; limit reference for live)
        stop_loss        : stop-loss price — used to attach a SL order after fill
        take_profit      : take-profit price — used to attach a TP order after fill
        strategy_name    : source strategy (for logging / audit trail)
        order_type       : default MARKET
        limit_price      : required when order_type == LIMIT
        """
        ccxt_side = "buy" if signal_direction == Direction.LONG else "sell"
        request = OrderRequest(
            symbol=signal_symbol,
            side=ccxt_side,
            order_type=order_type,
            quantity=size,
            price=limit_price if order_type == OrderType.LIMIT else None,
        )

        record = await self._dispatch(request, reference_price=entry_price)

        if not record.success:
            logger.error("Trade execution failed for %s: %s", signal_symbol, record.error)
            return record, None

        # Build the Position object
        position = Position(
            symbol=signal_symbol,
            side=signal_direction,
            entry_price=record.fill_price,
            size=record.filled_quantity,
            stop_loss=stop_loss,
            take_profit=take_profit,
            entry_time=record.timestamp,
            strategy=strategy_name,
            metadata={"order_id": record.order_id, "entry_fee": record.fee},
        )

        if self.mode == ExecutionMode.PAPER:
            self._paper_positions[signal_symbol] = position
        else:
            # Attach SL and TP orders immediately after fill
            await self.place_stop_loss(position, stop_loss)
            await self.place_take_profit(position, take_profit)

        logger.info(
            "Trade OPENED: %s %s @ %.4f size=%.6f fee=%.4f [%s]",
            signal_direction.value,
            signal_symbol,
            record.fill_price,
            record.filled_quantity,
            record.fee,
            self.mode.value,
        )
        return record, position

    async def place_stop_loss(self, position: Position, stop_price: float) -> ExecutionRecord | None:
        """
        Attach a stop-loss order for an open position.
        No-op in PAPER mode (stop monitoring handled by RiskManager).
        """
        if self.mode == ExecutionMode.PAPER:
            logger.debug("PAPER: SL recorded at %.4f for %s", stop_price, position.symbol)
            return None

        # LIVE: place stop-market order on the exchange
        close_side = "sell" if position.side == Direction.LONG else "buy"
        request = OrderRequest(
            symbol=position.symbol,
            side=close_side,
            order_type=OrderType.STOP_LOSS,
            quantity=position.size,
            stop_price=stop_price,
        )
        return await self._dispatch(request, reference_price=stop_price)

    async def place_take_profit(self, position: Position, tp_price: float) -> ExecutionRecord | None:
        """
        Attach a take-profit order for an open position.
        No-op in PAPER mode (TP monitoring handled by RiskManager).
        """
        if self.mode == ExecutionMode.PAPER:
            logger.debug("PAPER: TP recorded at %.4f for %s", tp_price, position.symbol)
            return None

        close_side = "sell" if position.side == Direction.LONG else "buy"
        request = OrderRequest(
            symbol=position.symbol,
            side=close_side,
            order_type=OrderType.TAKE_PROFIT,
            quantity=position.size,
            price=tp_price,
            stop_price=tp_price,
        )
        return await self._dispatch(request, reference_price=tp_price)

    async def close_position(
        self,
        position: Position,
        current_price: float,
        reason: ExitReason,
    ) -> TradeResult:
        """
        Close an open position at market.

        Parameters
        ----------
        position      : the position to close
        current_price : latest price (used for paper fill and PnL calculation)
        reason        : the exit reason for the trade record

        Returns
        -------
        TradeResult
        """
        close_side = "sell" if position.side == Direction.LONG else "buy"
        request = OrderRequest(
            symbol=position.symbol,
            side=close_side,
            order_type=OrderType.MARKET,
            quantity=position.size,
        )
        record = await self._dispatch(request, reference_price=current_price)

        fill = record.fill_price if record.success else current_price
        if position.side == Direction.LONG:
            raw_pnl = (fill - position.entry_price) * position.size
        else:
            raw_pnl = (position.entry_price - fill) * position.size

        entry_fee = position.metadata.get("entry_fee", 0.0)
        net_pnl = raw_pnl - entry_fee - record.fee
        cost_basis = position.entry_price * position.size
        pnl_pct = (net_pnl / cost_basis * 100.0) if cost_basis > 0 else 0.0
        duration = (record.timestamp - position.entry_time).total_seconds()

        if self.mode == ExecutionMode.PAPER:
            self._paper_positions.pop(position.symbol, None)

        result = TradeResult(
            pnl=net_pnl,
            pnl_pct=pnl_pct,
            duration_seconds=duration,
            entry_price=position.entry_price,
            exit_price=fill,
            exit_reason=reason,
            symbol=position.symbol,
            strategy=position.strategy,
            metadata={"close_order_id": record.order_id, "exit_fee": record.fee},
        )
        logger.info(
            "Trade CLOSED: %s @ %.4f | PnL=%.2f (%.2f%%) reason=%s [%s]",
            position.symbol,
            fill,
            net_pnl,
            pnl_pct,
            reason.value,
            self.mode.value,
        )
        return result

    # ------------------------------------------------------------------
    # Account queries
    # ------------------------------------------------------------------

    async def get_open_positions(self) -> list[Position]:
        """Return all currently open positions."""
        if self.mode == ExecutionMode.PAPER:
            return list(self._paper_positions.values())

        if self._exchange is None:
            raise RuntimeError("Call connect() before get_open_positions()")

        raw = await self._exchange.fetch_positions()
        positions: list[Position] = []
        for p in raw:
            if p.get("contracts", 0) == 0:
                continue
            side = Direction.LONG if p["side"] == "long" else Direction.SHORT
            positions.append(
                Position(
                    symbol=p["symbol"],
                    side=side,
                    entry_price=float(p.get("entryPrice") or 0),
                    size=float(p.get("contracts") or 0),
                    stop_loss=float(p.get("stopLossPrice") or 0),
                    take_profit=float(p.get("takeProfitPrice") or 0),
                    entry_time=datetime.now(UTC),
                    strategy="live_sync",
                    metadata=p,
                )
            )
        return positions

    async def get_balance(self) -> dict[str, float]:
        """
        Return a dict mapping currency → free balance.

        In PAPER mode returns the simulated balance.
        In LIVE mode fetches from the exchange.
        """
        if self.mode == ExecutionMode.PAPER:
            return dict(self._paper_balance)

        if self._exchange is None:
            raise RuntimeError("Call connect() before get_balance()")

        raw = await self._exchange.fetch_balance()
        return {k: v["free"] for k, v in raw.items() if isinstance(v, dict) and "free" in v}

    # ------------------------------------------------------------------
    # Internal dispatch + retry
    # ------------------------------------------------------------------

    async def _dispatch(self, request: OrderRequest, reference_price: float) -> ExecutionRecord:
        """Route the order to paper or live execution with retry logic."""
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                if self.mode == ExecutionMode.PAPER:
                    return self._paper_fill(request, reference_price)
                return await self._live_order(request)
            except (ccxt.NetworkError, ccxt.RequestTimeout) as exc:
                if attempt >= MAX_RETRIES:
                    logger.error(
                        "Order failed after %d attempts: %s — %s",
                        MAX_RETRIES,
                        request.symbol,
                        exc,
                    )
                    return ExecutionRecord(
                        order_id="",
                        symbol=request.symbol,
                        side=request.side,
                        order_type=request.order_type,
                        requested_quantity=request.quantity,
                        filled_quantity=0.0,
                        requested_price=request.price,
                        fill_price=0.0,
                        fee=0.0,
                        mode=self.mode,
                        timestamp=datetime.now(UTC),
                        success=False,
                        error=str(exc),
                    )
                delay = _RETRY_BASE_DELAY_S * (2 ** (attempt - 1))
                logger.warning("Order attempt %d/%d failed, retrying in %.1fs", attempt, MAX_RETRIES, delay)
                await asyncio.sleep(delay)
            except Exception as exc:  # non-retriable
                logger.error("Non-retriable order error for %s: %s", request.symbol, exc)
                return ExecutionRecord(
                    order_id="",
                    symbol=request.symbol,
                    side=request.side,
                    order_type=request.order_type,
                    requested_quantity=request.quantity,
                    filled_quantity=0.0,
                    requested_price=request.price,
                    fill_price=0.0,
                    fee=0.0,
                    mode=self.mode,
                    timestamp=datetime.now(UTC),
                    success=False,
                    error=str(exc),
                )

        # Unreachable but satisfies type checker
        raise RuntimeError("Exceeded MAX_RETRIES without returning")

    def _paper_fill(self, request: OrderRequest, reference_price: float) -> ExecutionRecord:
        """Simulate a fill at reference_price ± slippage."""
        slippage = random.uniform(_SLIPPAGE_MIN_PCT, _SLIPPAGE_MAX_PCT)
        if request.side == "buy":
            fill_price = reference_price * (1.0 + slippage)
        else:
            fill_price = reference_price * (1.0 - slippage)

        fee = fill_price * request.quantity * self.taker_fee_pct

        # Update simulated balance (simple USDT tracking)
        notional = fill_price * request.quantity + fee
        if request.side == "buy":
            self._paper_balance["USDT"] = self._paper_balance.get("USDT", 0.0) - notional
        else:
            self._paper_balance["USDT"] = self._paper_balance.get("USDT", 0.0) + (notional - 2 * fee)

        record = ExecutionRecord(
            order_id=f"paper_{request.client_order_id}",
            symbol=request.symbol,
            side=request.side,
            order_type=request.order_type,
            requested_quantity=request.quantity,
            filled_quantity=request.quantity,
            requested_price=request.price,
            fill_price=fill_price,
            fee=fee,
            mode=ExecutionMode.PAPER,
            timestamp=datetime.now(UTC),
            success=True,
        )
        logger.debug(
            "PAPER fill: %s %s qty=%.6f @ %.4f (slip=%.4f%%) fee=%.4f",
            request.side.upper(),
            request.symbol,
            request.quantity,
            fill_price,
            slippage * 100,
            fee,
        )
        return record

    async def _live_order(self, request: OrderRequest) -> ExecutionRecord:
        """Place a real order via CCXT and normalise the response."""
        if self._exchange is None:
            raise RuntimeError("Call connect() before placing live orders")

        params: dict[str, Any] = {"newClientOrderId": request.client_order_id}
        if request.stop_price is not None:
            params["stopPrice"] = request.stop_price
        if request.trailing_offset is not None:
            params["trailingPercent"] = request.trailing_offset

        order = await self._exchange.create_order(
            symbol=request.symbol,
            type=request.order_type.value,
            side=request.side,
            amount=request.quantity,
            price=request.price,
            params=params,
        )

        fill_price = float(order.get("average") or order.get("price") or 0.0)
        filled_qty = float(order.get("filled") or 0.0)
        fee_info = order.get("fee") or {}
        fee = float(fee_info.get("cost") or filled_qty * fill_price * self.taker_fee_pct)

        return ExecutionRecord(
            order_id=str(order.get("id", "")),
            symbol=request.symbol,
            side=request.side,
            order_type=request.order_type,
            requested_quantity=request.quantity,
            filled_quantity=filled_qty,
            requested_price=request.price,
            fill_price=fill_price,
            fee=fee,
            mode=ExecutionMode.LIVE,
            timestamp=datetime.now(UTC),
            success=order.get("status") in ("closed", "filled"),
            raw_response=order,
        )
