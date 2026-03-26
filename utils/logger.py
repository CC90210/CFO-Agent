"""
utils/logger.py
---------------
Structured logging setup for Atlas Trading Agent.

Log hierarchy
-------------
  atlas              — root logger (controls overall level)
  atlas.trade        — every trade event (open, close, fill, PnL)
  atlas.agent        — every agent decision and reasoning step
  atlas.risk         — every risk check result and kill-switch event
  atlas.performance  — daily P&L summaries and performance metrics

Output
------
  Console handler  — human-readable, colourised (when tty), INFO+
  File handler     — JSON-lines format, configurable level, rotating

File rotation
-------------
  Max 10 MB per file, 30 backup files retained (≈ 30 days of typical usage).
  JSON format makes it trivial to grep/jq and ingest into analytics pipelines.

Usage
-----
  from utils.logger import setup_logging, get_trade_logger

  setup_logging()  # call once at startup

  trade_log = get_trade_logger()
  trade_log.info("opened", extra={"symbol": "BTC/USDT", "price": 64200.0})
"""

from __future__ import annotations

import json
import logging
import logging.handlers
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config.settings import settings

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_MAX_BYTES: int = 10 * 1024 * 1024   # 10 MB
_BACKUP_COUNT: int = 30
_CONSOLE_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_LOGGER_NAMES = {
    "trade": "atlas.trade",
    "agent": "atlas.agent",
    "risk": "atlas.risk",
    "performance": "atlas.performance",
}


# ---------------------------------------------------------------------------
# JSON-lines formatter
# ---------------------------------------------------------------------------


class _AutoFlushHandler(logging.handlers.RotatingFileHandler):
    """RotatingFileHandler that flushes after every emit (fixes Windows buffering)."""

    def emit(self, record: logging.LogRecord) -> None:
        super().emit(record)
        self.flush()


class _JsonLinesFormatter(logging.Formatter):
    """
    Emit each log record as a single-line JSON object.

    Standard fields: timestamp, level, logger, message
    Extra fields: any key added via ``extra={}`` in the log call
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        # Merge any extra fields the caller provided
        skip = {
            "msg", "args", "levelname", "levelno", "name", "pathname",
            "filename", "module", "lineno", "funcName", "created", "msecs",
            "relativeCreated", "thread", "threadName", "processName",
            "process", "message", "exc_info", "exc_text", "stack_info",
        }
        for key, val in record.__dict__.items():
            if key not in skip:
                try:
                    json.dumps(val)  # only include JSON-serialisable extras
                    payload[key] = val
                except (TypeError, ValueError):
                    payload[key] = str(val)

        return json.dumps(payload, default=str, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Colourised console formatter (optional, degrades gracefully on non-tty)
# ---------------------------------------------------------------------------

_LEVEL_COLOURS = {
    "DEBUG": "\033[36m",     # cyan
    "INFO": "\033[32m",      # green
    "WARNING": "\033[33m",   # yellow
    "ERROR": "\033[31m",     # red
    "CRITICAL": "\033[1;31m",  # bold red
}
_RESET = "\033[0m"


class _ColourisedFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)
        if sys.stderr.isatty():  # type: ignore[misc]
            colour = _LEVEL_COLOURS.get(record.levelname, "")
            return f"{colour}{formatted}{_RESET}"
        return formatted


# ---------------------------------------------------------------------------
# Public setup function
# ---------------------------------------------------------------------------


_configured: bool = False


def setup_logging(force: bool = False) -> None:
    """
    Configure the Atlas logger hierarchy.

    Should be called once at application startup.
    Subsequent calls are no-ops unless ``force=True``.

    Parameters
    ----------
    force : re-configure even if already set up (useful in tests)
    """
    global _configured
    if _configured and not force:
        return

    log_dir: Path = settings.logging.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)
    root_level = getattr(logging, settings.logging.log_level, logging.INFO)

    root = logging.getLogger("atlas")
    root.setLevel(logging.DEBUG)  # root at DEBUG; handlers filter to configured level
    root.propagate = False

    # ── Console handler ──────────────────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(root_level)
    console_handler.setFormatter(
        _ColourisedFormatter(fmt=_CONSOLE_FORMAT, datefmt=_DATE_FORMAT)
    )
    root.addHandler(console_handler)

    # ── Master file handler (ALL atlas.* logs → atlas_master.log) ─────────
    master_log_path = log_dir / "atlas_master.log"
    master_fh = _AutoFlushHandler(
        master_log_path,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    master_fh.setLevel(logging.INFO)
    master_fh.setFormatter(logging.Formatter(
        fmt=_CONSOLE_FORMAT, datefmt=_DATE_FORMAT,
    ))
    root.addHandler(master_fh)

    # ── File handlers (one per domain logger) ────────────────────────────────
    for domain, logger_name in _LOGGER_NAMES.items():
        log_path = log_dir / f"{domain}.jsonl"
        file_handler = _AutoFlushHandler(
            log_path,
            maxBytes=_MAX_BYTES,
            backupCount=_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)  # capture everything in files
        file_handler.setFormatter(_JsonLinesFormatter())

        domain_logger = logging.getLogger(logger_name)
        domain_logger.setLevel(logging.DEBUG)
        domain_logger.addHandler(file_handler)
        # Do NOT propagate — file records go to the domain file only
        # (they will still appear on console via the parent root handler)

    # ── Engine file handler (atlas.engine → engine.jsonl) ───────────────────
    engine_log_path = log_dir / "engine.jsonl"
    engine_fh = _AutoFlushHandler(
        engine_log_path,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    engine_fh.setLevel(logging.DEBUG)
    engine_fh.setFormatter(_JsonLinesFormatter())
    engine_logger = logging.getLogger("atlas.engine")
    engine_logger.setLevel(logging.DEBUG)
    engine_logger.addHandler(engine_fh)

    _configured = True
    logging.getLogger("atlas").info(
        "Logging initialised — level=%s dir=%s", settings.logging.log_level, log_dir
    )


# ---------------------------------------------------------------------------
# Convenience accessors
# ---------------------------------------------------------------------------


def get_trade_logger() -> logging.Logger:
    """Return the trade-event logger (``atlas.trade``)."""
    return logging.getLogger(_LOGGER_NAMES["trade"])


def get_agent_logger() -> logging.Logger:
    """Return the agent-decision logger (``atlas.agent``)."""
    return logging.getLogger(_LOGGER_NAMES["agent"])


def get_risk_logger() -> logging.Logger:
    """Return the risk-management logger (``atlas.risk``)."""
    return logging.getLogger(_LOGGER_NAMES["risk"])


def get_performance_logger() -> logging.Logger:
    """Return the performance/P&L logger (``atlas.performance``)."""
    return logging.getLogger(_LOGGER_NAMES["performance"])


def log_trade_opened(
    symbol: str,
    direction: str,
    entry_price: float,
    size: float,
    stop_loss: float,
    take_profit: float,
    conviction: float,
    strategy: str,
) -> None:
    """Structured helper to log a trade opening event."""
    get_trade_logger().info(
        "TRADE_OPEN",
        extra={
            "event": "trade_open",
            "symbol": symbol,
            "direction": direction,
            "entry_price": entry_price,
            "size": size,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "conviction": conviction,
            "strategy": strategy,
        },
    )


def log_trade_closed(
    symbol: str,
    direction: str,
    entry_price: float,
    exit_price: float,
    size: float,
    pnl: float,
    pnl_pct: float,
    exit_reason: str,
    strategy: str,
) -> None:
    """Structured helper to log a trade closing event."""
    get_trade_logger().info(
        "TRADE_CLOSE",
        extra={
            "event": "trade_close",
            "symbol": symbol,
            "direction": direction,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "size": size,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "exit_reason": exit_reason,
            "strategy": strategy,
        },
    )


def log_agent_decision(
    agent_name: str,
    symbol: str,
    decision: str,
    conviction: float,
    reasoning: str,
) -> None:
    """Structured helper to log an agent decision."""
    get_agent_logger().info(
        "AGENT_DECISION",
        extra={
            "event": "agent_decision",
            "agent": agent_name,
            "symbol": symbol,
            "decision": decision,
            "conviction": conviction,
            "reasoning": reasoning,
        },
    )


def log_daily_summary(
    date: str,
    starting_equity: float,
    ending_equity: float,
    pnl: float,
    pnl_pct: float,
    trades_opened: int,
    trades_closed: int,
    max_drawdown_pct: float,
) -> None:
    """Structured helper to log a daily P&L summary."""
    get_performance_logger().info(
        "DAILY_SUMMARY",
        extra={
            "event": "daily_summary",
            "date": date,
            "starting_equity": starting_equity,
            "ending_equity": ending_equity,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "trades_opened": trades_opened,
            "trades_closed": trades_closed,
            "max_drawdown_pct": max_drawdown_pct,
        },
    )
