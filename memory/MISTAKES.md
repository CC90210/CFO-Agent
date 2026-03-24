# ATLAS Mistakes Log

## 2026-03-20 — CCXTAdapter 10s Timeout + Unguarded Fallback Caused Zero Trades

**What happened:** Paper trading ran but generated zero trades. Every symbol tick was silently dying because CCXTAdapter.fetch_ohlcv timed out in 10 seconds (too short for multi-symbol concurrent fetches), then the engine fallback called `self._exchange.fetch_ohlcv()` with NO `asyncio.wait_for` wrapper — meaning it could hang indefinitely and had no retry.

**Root cause:**
1. `_DEFAULT_TIMEOUT_S = 10.0` in broker_adapter.py — too short under network load or rate limiting
2. Engine `_fetch_ohlcv` fallback path had no timeout wrapper and no retry
3. No INFO-level logging when signals were suppressed (regime, conviction, should_enter) — all at DEBUG, so logs showed nothing actionable

**Fix applied:**
- Raised `_DEFAULT_TIMEOUT_S` to 30.0 in `core/broker_adapter.py`
- Added 3-attempt exponential backoff retry (2s, 4s) to `CCXTAdapter.fetch_ohlcv`
- Wrapped engine fallback CCXT call in `asyncio.wait_for(timeout=30)` with 3-attempt retry
- Promoted key "no signal" branches from DEBUG to INFO: regime suppression, `should_enter=False`, `analyze=None`, `direction=FLAT`, conviction below threshold, OHLCV unavailable

**Prevention:** Any network call in an async trading loop MUST have: (1) explicit `asyncio.wait_for` timeout, (2) at minimum 2 retries with backoff, (3) INFO-level fallback logging so ops can see why ticks are silent. Never leave a fallback path without its own timeout.

---

## 2026-03-17 — Ichimoku 4/5 Condition Disaster

**What happened:** Changed Ichimoku from 5/5 required conditions to 4/5. Backtest showed 501 trades and -91% return.

**Root cause:** Ichimoku is a complete system where each condition filters different types of noise. Removing any one condition allows massively more false positives. The TK cross alone fires on every minor pullback — the other 4 conditions are what make it selective.

**Prevention:** NEVER relax Ichimoku below 5/5 conditions. If trade frequency is too low, accept it — that's the system working correctly.

---

## 2026-03-17 — Uniform Trailing Stops Killed Trend Profits

**What happened:** Applied Chandelier exit at 3x ATR uniformly to all strategies. Multi-timeframe went from +7.81% to -1.29%, volume profile from +6.46% to -1.01%.

**Root cause:** Trend-following strategies need to ride winners through normal pullbacks. 3x ATR is too tight — it exits during healthy retracements, then re-enters at worse prices. This caused trade count to jump from 7 to 25 (whipsaw).

**Prevention:** Always configure trailing stops PER STRATEGY TYPE:
- Trend-following: 4-5x ATR or disabled (use strategy's own should_exit)
- Mean-reversion: 1.5-2x ATR
- Breakout: 2-3x ATR, activate only after 1.5x ATR profit
