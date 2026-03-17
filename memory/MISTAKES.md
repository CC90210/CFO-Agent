# ATLAS Mistakes Log

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
