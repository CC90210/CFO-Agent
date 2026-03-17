# ATLAS Strategy Deep Analysis (2026-03-17)

> Deep-dive analysis of all strategies with specific weaknesses and fixes identified.
> Use this as the blueprint for the next tuning session.

## Common Flaw Across ALL Strategies

**Take-profit targets are too ambitious.** All use 2-3x ATR or 3:1+ R:R. In reality, mean reversion hits 50-70% of target before reversing, and trend-following targets are too far to reach on momentum alone.

**Fix:** Implement **scale-out exits** instead of single TP:
- 30% at 1x ATR (covers commissions + quick win)
- 30% at 2x ATR (medium target)
- 40% trail with ATR trailing stop

This increases TP hit rate from ~40-50% to ~70-80%.

---

## Per-Strategy Findings

### 1. RSI Mean Reversion
**Problem:** 1.5x ATR stop is too tight. Mean reversion often extends beyond stop before reverting. Bollinger midline as TP is too conservative (it's entry, not exit).
**Fix:**
- Stop loss: 2.5-3.0x ATR (allow breathing room)
- Take profit: BB opposite band instead of midline, or scale out
- ADX filter: relax to < 30 or 35 (currently 25 is too restrictive)
- Add trailing stop once 1x ATR in profit

### 2. EMA Crossover
**Problem:** Entry is LATE — by the time fast EMA crosses slow + MACD confirms, the initial impulse is done. 3:1 R:R is unrealistic from a lagging entry.
**Fix:**
- Wait for 1-2 bar retest of crossover line (filter false crosses)
- Lower TP to 2:1 R:R
- Add SMA 200 filter (only LONG above SMA 200)
- Exit logic: ATR trailing stop instead of opposite crossover
- ADX threshold: > 20 instead of 25 (catch trends earlier)

### 3. Ichimoku Trend
**Problem:** Massive lag from 5 conditions + Chikou + cloud displacement. By the time all 5 align, 30-40% of the trend is gone. Cloud exit is too tight.
**CRITICAL: DO NOT relax to 4/5 conditions — this was tested and caused -91% with 501 trades.**
**Fix:**
- Add trailing stop once cloud support established
- Scale position by conviction (stronger setups get larger size)
- Consider 1H timeframe for more precise entries
- Cloud exit: require price to penetrate 50% into cloud (already implemented)

### 4. Multi-Timeframe
**Problem:** MTF pullback detection too strict (0.5% band). LTF MACD may be using resampled data. Confluence min of 2/3 is too low.
**Fix:**
- Expand pullback band to EMA ±2%
- Verify LTF MACD uses raw 15m data
- Require LTF agreement for entry
- Exit: require 2 consecutive HTF closes below EMA(50)
- Increase TP to 4:1 for high-confluence setups

### 5. Bollinger Squeeze
**Problem:** Squeeze detection is backward-looking (entering AFTER expansion starts). Volume surge on breakout = exhaustion, not confirmation. 22% win rate, 0.14 PF.
**Fix:**
- Detect when BB width reaches 20-period low (not 126-bar)
- Require 2 consecutive closes OUTSIDE BB (filter false breaks) — ALREADY IMPLEMENTED
- Consider flipping volume logic: normal/below-average volume on breakout = accumulation
- Widen stops to 1.5x ATR below entry
- Works better on 15m-1H (faster squeezes)

### 6. Smart Money
**Problem:** 0% win rate, 6 trades. Very low trade count makes it hard to evaluate.
**Fix:** Needs more data. OB tolerance at 0.8% and FVG at 0.3 ATR are tuned. May need longer backtest period.

---

## Priority Implementation Order

1. **Scale-out exits for ALL strategies** — highest impact, single change
2. **RSI: widen stops to 2.5x ATR, TP to BB opposite band** — already partially done
3. **EMA: add SMA 200 filter + lower TP to 2:1** — quick win
4. **Multi-TF: expand pullback band + verify LTF data** — bug fix
5. **Bollinger: redefine squeeze as 20-period low** — structural fix
