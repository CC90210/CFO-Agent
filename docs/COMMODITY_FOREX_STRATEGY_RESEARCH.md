# ATLAS — Commodity & Forex Strategy Research (2026-03-25)

> Comprehensive research: top 10 quantitatively-validated strategies for gold, silver, oil, and forex majors.
> Ranked by profitability and implementability for a $150–$500 account via OANDA.

---

## Executive Summary

| Rank | Strategy | Asset Class | Expected Sharpe | Annual Return | Complexity | Data Needs | Small Account? |
|------|----------|-------------|-----------------|---------------|------------|------------|----------------|
| 1 | Time Series Momentum (TSMOM) | Gold, Silver, Oil, Forex | 1.0–1.5 | 15–25% | Medium | OHLCV 1h/4h | YES |
| 2 | Gold Pullback Window (State Machine) | XAU/USD | 0.89 | ~9% annualized | Medium | OHLCV 1h | YES |
| 3 | London Session Breakout | EUR/USD, GBP/USD, XAU/USD | 0.7–1.2 | 15–30% | Low | OHLCV 15m/1h | YES |
| 4 | Carry + Momentum Hybrid | AUD/USD, USD/JPY, NZD/JPY | 0.6–1.0 | 8–15% + swap | Low-Medium | OHLCV 4h + rates | YES |
| 5 | Gold Seasonal + Trend Filter | XAU/USD, XAG/USD | 0.7–0.9 | 10–15% | Low | OHLCV daily | YES |
| 6 | Cross-Asset Regime (Gold/DXY/VIX) | XAU/USD, multi-asset | 0.8–1.2 | 12–20% | High | Multi-feed | YES (simplified) |
| 7 | Oil Calendar Spread Z-Score | WTI Crude (CFD) | 0.6–1.0 | 10–18% | High | Futures curve | MARGINAL |
| 8 | COT Positioning Fade | Gold, Silver, Oil | 0.5–0.8 | 8–12% | Medium | COT weekly | YES |
| 9 | Initial Balance Breakout (Gold) | XAU/USD | 0.8–1.1 | 20–40% | Low | OHLCV 15m | YES |
| 10 | Gold/Silver Ratio Mean Reversion | XAU/XAG spread | 0.5–0.7 | 8–12% | Low | OHLCV daily | YES |

---

## Strategy #1: Time Series Momentum (TSMOM)

**Source:** Moskowitz, Ooi & Pedersen (2012), Journal of Financial Economics. The foundational academic paper documenting momentum across 58 futures contracts over 25+ years.

**Core Finding:** A diversified portfolio of TSMOM strategies across asset classes delivers Sharpe > 1.20 with little exposure to standard risk factors. Performs best during extreme market conditions (crisis alpha).

### Implementation for ATLAS

**Signal:** For each instrument, compute the excess return over the past `L` months (lookback). If positive, go long. If negative, go short.

**Parameters (validated by academic research):**
- Lookback period: 12 months (252 trading days) — strongest single signal
- Blended signal: average of 1-month, 3-month, 12-month lookbacks — more robust
- Rebalance: monthly or weekly
- Position sizing: inverse volatility weighting (target 10% annualized vol per position)
- Stop loss: 2x ATR(20) from entry
- Take profit: trail at 3x ATR after 1.5x ATR profit

**Applicable instruments:**
- XAU/USD (gold) — strong trending behavior, macro-driven
- XAG/USD (silver) — higher vol, stronger momentum effect
- Oil (WTI/Brent CFD via OANDA) — inventory-driven trends
- EUR/USD, GBP/USD, USD/JPY, AUD/USD — rate-differential trends

**Sharpe ratio:** 1.0–1.5 (diversified across assets)
**Implementation complexity:** Medium — requires multi-asset lookback calculation
**Data requirements:** Daily OHLCV, 12+ months history
**Small account suitability:** HIGH — fractional position sizing via OANDA CFDs. $150 minimum with 20:1 leverage.

**Why it's #1:** Most academically validated strategy in existence. Works across ALL asset classes we're targeting. Already partially implemented in ATLAS via multi-timeframe momentum and Donchian breakout.

---

## Strategy #2: Gold Pullback Window (4-Phase State Machine)

**Source:** [ilahuerta-IA/backtrader-pullback-window-xauusd](https://github.com/ilahuerta-IA/backtrader-pullback-window-xauusd) — backtested 2020–2025.

**Backtested Performance:**
- Sharpe ratio: 0.89
- Profit factor: 1.64
- Win rate: 55.43%
- Max drawdown: 5.81%
- Total return: +44.75% over 5 years (~8.9% annualized)

### 4-Phase State Machine

1. **SCANNING:** Wait for volatility expansion channel breakout (Keltner or Bollinger)
2. **PULLBACK_WAIT:** After breakout detected, wait for price to pull back to the EMA(20) zone
3. **ENTRY:** Enter on the first bullish bar that closes above EMA(20) after pullback
4. **MANAGING:** Trail stop using 2x ATR, lock profits at 1.5R

**Parameters:**
- Volatility channel: EMA(20) +/- 2.0x ATR(14) (Keltner)
- Pullback zone: price must touch EMA(20) +/- 0.5x ATR
- Entry confirmation: bullish engulfing or close above EMA(20)
- Stop loss: 2.0x ATR below entry
- Take profit: 4.0x ATR (2:1 R:R)
- Trailing stop: activate at 1.5x ATR profit, trail at 2.0x ATR

**Why it's #2:** Low drawdown (5.81%) makes it ideal for small accounts. The state machine approach prevents chasing breakouts — it waits for the pullback, which dramatically reduces false entries. Already aligns with our existing `gold_trend_follower.py` architecture.

---

## Strategy #3: London Session Breakout (Enhanced)

**Source:** QuantifiedStrategies.com backtests + institutional forex research. Profit factor > 1.5 across multi-year tests.

### Rules

**Range definition:** High/low of Asian session (00:00–08:00 UTC)

**Entry (Long):**
1. Price breaks above Asian session high after 08:00 UTC
2. Breakout candle closes above the high (not just a wick)
3. ATR(14) expanding vs 5-bar SMA of ATR (real breakout, not drift)
4. RSI(14) between 40–70 (momentum confirmed, not overbought)

**Entry (Short):** Mirror of above below Asian session low, RSI 30–60.

**Exit:**
- Stop loss: opposite side of Asian range (or 1.0x range width below entry)
- Take profit: 1.5x range width (conservative) or 2.0x (aggressive)
- Time stop: close at 16:00 UTC (end of London session) — no overnight holds
- Gold-specific: widen to SL 1.5x range, TP 2.5x range (gold trends harder)

**Best pairs:** GBP/USD (primary — cleanest breakouts), EUR/USD, XAU/USD
**Best timeframe:** 15m candles for entry, 1h for confirmation

**Parameters:**
- Asian range window: 00:00–08:00 UTC
- Entry window: 08:00–11:00 UTC (first 3 hours only)
- Min range size: 0.3x ATR(14) — filter out tiny ranges
- Max range size: 2.0x ATR(14) — filter out already-expanded days

**Sharpe ratio:** 0.7–1.2 depending on pair
**Implementation complexity:** LOW — already have `london_breakout.py` and `forex_session_momentum.py`
**Data requirements:** Intraday OHLCV (15m or 1h)
**Small account suitability:** HIGH — 1 trade per day, tight risk, quick exits

---

## Strategy #4: Carry + Momentum Hybrid (Forex)

**Source:** Academic carry trade literature + ATLAS existing `forex_carry_momentum.py`

### Core Edge

Two structural tailwinds stacked:
1. **Carry:** earn swap/overnight interest by being long high-yield vs short low-yield
2. **Momentum:** only hold when trend confirms carry direction

**Current Interest Rate Hierarchy (March 2026):**
- High yield: AUD (~4.1%), NZD (~3.75%), USD (~4.5%)
- Low yield: JPY (~0.5%), CHF (~1.25%), EUR (~2.5%)

**Best carry pairs:**
- AUD/JPY — highest positive swap when long
- NZD/JPY — second highest
- USD/JPY — long USD earns carry (but JPY strengthening in 2026)
- AUD/USD — complex, rate differential narrowing

**For OANDA implementation (via AUD_USD, USD_JPY):**

**Entry (Long carry pair):**
1. Price > SMA(200) — macro uptrend
2. Price > SMA(50) — medium-term confirmation
3. ADX(14) > 20 — trending, not ranging
4. MACD histogram > 0 — positive momentum
5. RSI(14) 40–70 — not overbought

**Exit:**
- Stop loss: 2.5x ATR(14)
- Take profit: 2.0x risk (5.0x ATR)
- Trail after 1.5x ATR profit

**CRITICAL WARNING for 2026:** The yen carry trade is unwinding. BOJ is hiking rates while Fed is cutting. USD/JPY long carry trades are increasingly dangerous. AUD/JPY also bearish. Implement with tight risk controls and regime filter — disable carry in RISK_OFF regime.

**Sharpe ratio:** 0.6–1.0 (with trend filter; pure carry is ~0.3–0.5)
**Implementation complexity:** LOW-MEDIUM — already built as `forex_carry_momentum.py`
**Small account suitability:** HIGH — OANDA supports micro lots (0.001), swap income compounds

---

## Strategy #5: Gold Seasonal + Trend Filter

**Source:** 50-year seasonal analysis (Seasonax, Barchart, Quantified Strategies)

### Seasonal Patterns (Backtested 50+ Years)

| Month | Avg Return | Win Rate | Signal |
|-------|-----------|----------|--------|
| January | +1.90% | 80% | STRONG BUY |
| February | +0.80% | 60% | Mild bullish |
| March | -0.30% | 45% | Avoid |
| April | +0.50% | 55% | Neutral |
| May | -0.10% | 48% | Avoid |
| June | -0.40% | 42% | Avoid |
| July | +0.60% | 58% | Entry window |
| August | +1.20% | 65% | BUY (start of strong period) |
| September | +1.00% | 62% | BUY |
| October | -0.20% | 45% | Avoid |
| November | +0.70% | 58% | Bullish |
| December | +0.50% | 55% | Bullish |

**Strong period:** July 6 → February 21 — average gain 7–11%, success rate > 65%
**Weak period:** March → June — average flat or negative

**Turn-of-month effect:** Gold rises ~0.70% in the 2 trading days around month-end/month-start. Annualized, this accounts for 2/3 of gold's total return.

### Implementation

**Strategy:** Only take LONG gold trades during Aug–Feb. Stay flat March–July.

**Combine with trend filter to avoid catching falling knives:**
1. Seasonal window = Aug 1 through Feb 28
2. Price > EMA(50) — medium-term uptrend
3. Enter on RSI(14) < 40 pullback within seasonal window
4. Stop: 2.0x ATR(14)
5. Target: 3.0x ATR or hold until end of seasonal window

**Sharpe ratio:** 0.7–0.9
**Implementation complexity:** LOW — calendar filter + existing indicators
**Data requirements:** Daily OHLCV
**Small account suitability:** HIGH — long holding periods, few trades, low transaction costs

---

## Strategy #6: Cross-Asset Regime Trading (Gold/DXY/VIX)

**Source:** World Gold Council research, ACY analysis, Bloomberg correlation studies

### Core Relationships

| Correlation | Coefficient | Trading Implication |
|-------------|------------|---------------------|
| Gold vs DXY | -0.45 to -0.72 | When USD weakens, go long gold |
| Gold vs US 10Y Real Yield | -0.80 | When real yields fall, gold rallies |
| Gold vs VIX | +0.30 to +0.50 | Gold rises in fear episodes |
| Oil (WTI) vs USD/CAD | -0.60 to -0.75 | Oil up → CAD strengthens → USD/CAD falls |
| AUD/USD vs Risk Appetite | +0.65 | AUD is a risk-on currency |

### Four Regime States

1. **RISK-ON (bull):** Long AUD/USD, short gold, long oil. USD weak.
2. **RISK-OFF (fear):** Long gold, long JPY (short USD/JPY), short oil.
3. **INFLATION:** Long gold, long oil, short bonds. USD mixed.
4. **DEFLATION:** Long USD/JPY, long bonds, short gold, short oil.

### Implementation (Simplified for Small Account)

**Regime detection inputs:**
- VIX level (via OANDA CFD or data feed): > 25 = risk-off, < 15 = risk-on
- DXY trend: falling DXY → bullish gold, bearish USD/JPY
- US 10Y yield direction: falling → bullish gold
- Oil trend: rising → bullish CAD (short USD/CAD)

**Trade rules:**
- When regime = RISK_OFF and DXY falling: LONG XAU/USD, size 1.5x normal
- When regime = RISK_ON and DXY rising: SHORT XAU/USD or FLAT
- When oil trending up (TSMOM signal positive): SHORT USD/CAD
- When VIX spikes > 30 AND gold + DXY both rising: EXTREME FEAR — max long gold

**Sharpe ratio:** 0.8–1.2 (regime-conditional improves base strategies by 30–50%)
**Implementation complexity:** HIGH — requires multiple data feeds
**Data requirements:** OHLCV + VIX + DXY + yields
**Small account suitability:** YES if simplified to DXY correlation only

---

## Strategy #7: Oil Calendar Spread Z-Score

**Source:** QuantStrategy.io, CME Group research on contango/backwardation

### Core Concept

Trade the spread between front-month and deferred oil futures. When spread is extreme (Z-score > 2), mean-revert it.

**Parameters:**
- Spread = Front-month price - Deferred-month price
- Z-score lookback: 60 trading days
- Entry: Z-score > +2.0 (extreme contango) → SHORT spread
- Entry: Z-score < -2.0 (extreme backwardation) → LONG spread
- Exit: Z-score reverts to 0 (or < +0.5 / > -0.5)
- Confirm with RSI on spread: RSI > 70 (overbought contango) or RSI < 30 (oversold)

**For OANDA/small account adaptation:**
- OANDA doesn't offer futures curve directly
- Proxy: trade WTI CFD directionally based on contango/backwardation regime
- Backwardation (current supply shortage) → long bias
- Contango (oversupply) → short bias or flat
- Use EIA inventory data (Wednesday 10:30 ET) as catalyst

**EIA inventory report strategy:**
- Inventory surprise < -2M barrels → LONG oil (supply tighter than expected)
- Inventory surprise > +2M barrels → SHORT oil
- Confirm with 4h RSI < 30 (for longs) or RSI > 70 (for shorts)
- Stop: 1.5x ATR, Target: 2.0x ATR
- Hold max 48 hours

**Sharpe ratio:** 0.6–1.0
**Implementation complexity:** HIGH — requires external data (EIA API, futures curve)
**Data requirements:** EIA weekly inventory, futures curve data
**Small account suitability:** MARGINAL — oil CFDs have wider spreads, higher margin requirements

---

## Strategy #8: COT Positioning Fade

**Source:** CFTC Commitment of Traders reports, published every Friday for Tuesday's positions.

### Core Concept

Non-commercials (hedge funds, CTAs) are trend-followers who pile into extreme positions at trend ends. When their net positioning reaches extremes, fade them.

**Parameters:**
- Data: CFTC COT report — net non-commercial positions for gold, silver, oil
- Z-score lookback: 52 weeks (1 year of weekly COT data)
- Entry: Net long Z-score > +2.0 → SHORT signal (too crowded long)
- Entry: Net long Z-score < -2.0 → LONG signal (too crowded short)
- Combine with price trend: only fade when price also shows reversal signal (RSI divergence, breakdown from trendline)
- Hold: 2–6 weeks (COT is a slow signal)

**Gold-specific COT rules:**
- When commercial hedgers are net short at extreme levels → bearish (smart money hedging)
- When commercial hedgers reduce shorts sharply → bullish (smart money accumulating)
- Non-commercial net long at 3-year high → prepare for reversal

**Exit:**
- COT Z-score normalizes (returns to +/-0.5)
- Price hits 3x ATR(20) weekly target
- Stop: 2x ATR(20) weekly

**Sharpe ratio:** 0.5–0.8
**Implementation complexity:** MEDIUM — need COT data feed (free from CFTC, updated weekly)
**Data requirements:** Weekly COT reports + daily OHLCV
**Small account suitability:** HIGH — very few trades (4–8 per year per instrument), low transaction costs

---

## Strategy #9: Initial Balance Breakout (Gold Intraday)

**Source:** TradeTheSwig.com backtests — +411% return Jan 2025–Jan 2026 on gold futures.

### Core Concept

The "Initial Balance" (IB) is the range of the first 60 minutes of a trading session. Gold frequently breaks out of this range and trends for the rest of the session.

**Parameters:**
- IB window: first 60 minutes of London session (08:00–09:00 UTC)
- Entry: price breaks above IB high (long) or below IB low (short)
- Target: 50% of IB range beyond the breakout level
- Stop: 60% of IB range on the opposite side
- R:R: approximately 0.83:1 — compensated by > 55% win rate
- Time stop: close at 16:00 UTC regardless of P&L
- Max 1 trade per day

**Filters:**
- Skip if IB range < 0.2x ATR(14) — too narrow, likely false breakout
- Skip if IB range > 1.5x ATR(14) — already expanded, move already happened
- Prefer London open direction aligned with overnight trend

**Backtested performance:**
- Win rate: ~55%
- Average trade: $200–$370 per gold futures contract
- Suitable for 15m timeframe entries

**Sharpe ratio:** 0.8–1.1
**Implementation complexity:** LOW — time window + range calculation
**Data requirements:** 15m OHLCV, session timestamps
**Small account suitability:** HIGH — 1 trade/day, defined risk, quick exit

---

## Strategy #10: Gold/Silver Ratio Mean Reversion

**Source:** Historical precious metals ratio analysis. The XAU/XAG ratio has mean-reverted around 60–80 for decades.

### Core Concept

The gold/silver ratio (currently ~100 as of March 2026) tends to cycle between extremes. When the ratio is historically high (>85), silver is cheap relative to gold — long silver, short gold. When low (<65), the reverse.

**Parameters:**
- Ratio calculation: XAU_USD price / XAG_USD price
- Z-score lookback: 252 trading days (1 year)
- Entry (long silver/short gold): Ratio Z-score > +1.5 (ratio elevated)
- Entry (long gold/short silver): Ratio Z-score < -1.5 (ratio compressed)
- Exit: Z-score normalizes to +/-0.5
- Position sizing: dollar-neutral (equal notional on each leg)

**OANDA implementation:**
- Can trade this as a pairs trade: long XAG_USD + short XAU_USD (or vice versa)
- Or simply use ratio as directional bias: if ratio > 85, overweight silver in directional trades
- With $150–$500, likely better as a bias filter rather than full pairs trade

**Historical stats:**
- Ratio range: 15 (1980) to 125 (2020 COVID)
- Current: ~100 — historically elevated, suggesting silver undervaluation
- Mean reversion half-life: ~6–12 months

**Sharpe ratio:** 0.5–0.7
**Implementation complexity:** LOW — simple ratio calculation
**Data requirements:** Daily prices for XAU_USD and XAG_USD
**Small account suitability:** HIGH as directional bias; MARGINAL as hedged pairs trade (needs both legs)

---

## Cross-Asset Correlation Matrix (Trading Rules)

| Signal | Action | Confidence |
|--------|--------|------------|
| DXY falling + gold breakout | LONG XAU/USD aggressively | HIGH |
| DXY rising + gold breaking down | SHORT XAU/USD or FLAT | HIGH |
| Oil rising + USD/CAD falling | SHORT USD/CAD (long CAD) | MEDIUM |
| VIX > 25 + DXY flat/falling | LONG XAU/USD (safe haven) | HIGH |
| VIX > 30 + DXY AND gold both rising | MAX LONG gold (extreme fear) | VERY HIGH |
| BOJ rate hike + USD/JPY breaking down | SHORT USD/JPY (carry unwind) | HIGH |
| Gold/Silver ratio > 90 | Prefer silver over gold for longs | MEDIUM |
| EIA inventory surprise < -2M bbl | LONG WTI oil | MEDIUM |

---

## Implementation Priority for ATLAS

### Phase 1 — Immediate (Already Have Infrastructure)

1. **London Session Breakout (enhanced)** — upgrade existing `london_breakout.py` and `forex_session_momentum.py` with Asian range definition, time stops, and gold-specific wider targets
2. **Time Series Momentum** — implement as new strategy or enhance `multi_timeframe.py` with 1/3/12 month lookback blend
3. **Gold Seasonal Filter** — add calendar-based conviction modifier to `gold_trend_follower.py`

### Phase 2 — Short-term (Need Minor Extensions)

4. **Initial Balance Breakout** — new strategy, simple to implement, 1 trade/day on gold
5. **Gold/Silver Ratio Bias** — add as conviction modifier to existing gold/silver strategies
6. **Cross-Asset Regime Signals** — extend `regime_detector.py` with DXY correlation

### Phase 3 — Medium-term (Need Data Infrastructure)

7. **COT Positioning** — needs CFTC data parser (free, weekly)
8. **Carry + Momentum Enhancement** — already have `forex_carry_momentum.py`, needs swap rate data
9. **Oil Calendar Spread** — needs futures curve data or EIA API integration
10. **Full Cross-Asset Regime** — needs VIX + DXY + yield data feeds

---

## Key Findings & Recommendations

### What Works Best for Gold/Silver
- **Trend following dominates.** Gold trends on macro shifts (rates, USD, geopolitics) that persist for months. Mean reversion is secondary.
- **London session is the money session.** Highest gold liquidity 08:00–16:00 UTC. Best breakouts in first 3 hours.
- **Wide stops are mandatory.** Gold's ATR is 2–3x typical forex pairs. Tight stops get wiped. Use 2.0–2.5x ATR minimum.
- **Seasonal overlay adds 2–3% annually.** Not enough alone, but stacked on trend = free edge.

### What Works Best for Forex Majors
- **Carry + trend is the institutional standard.** Pure carry crashes in risk-off. Trend filter prevents holding through unwinds.
- **Session breakouts are real edge** but degrade without time stops. Close at session end.
- **EUR/USD and GBP/USD are momentum pairs in 2026** (USD weakening). Trend-following preferred over mean reversion.
- **USD/JPY is dangerous in 2026** — BOJ hiking, carry unwind risk. Only trade with explicit carry confirmation.

### What Works Best for Oil
- **Inventory surprises are the cleanest catalyst.** EIA Wednesday report drives 48-hour moves.
- **Mean reversion is weak on oil.** It trends on supply/demand fundamentals, not revert.
- **Contango/backwardation regime is slow but reliable.** Backwardation = bullish bias, contango = bearish.

### For a $150–$500 Account
- **Use OANDA micro lots** (0.001 lot = $0.10/pip on forex, ~$0.01/tick on gold)
- **Max 2–3 positions simultaneously** to keep risk per trade at 1–1.5%
- **Prioritize gold and GBP/USD** — highest Sharpe strategies on these instruments
- **Avoid oil initially** — wider spreads eat into small account returns
- **Compound aggressively** — at 15–25% annual, $500 → $625–$750 in year 1

---

## Sources

- [Moskowitz, Ooi & Pedersen — Time Series Momentum (JFE 2012)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2089463)
- [Gold Pullback Window Strategy — GitHub](https://github.com/ilahuerta-IA/backtrader-pullback-window-xauusd)
- [QuantifiedStrategies — Gold Trading Strategies 2026](https://www.quantifiedstrategies.com/gold-trading-strategies/)
- [QuantifiedStrategies — London Breakout Strategy](https://www.quantifiedstrategies.com/london-breakout-strategy/)
- [QuantifiedStrategies — COT Trading Strategies](https://www.quantifiedstrategies.com/commitments-of-traders/)
- [QuantifiedStrategies — MACD & RSI for Commodities](https://www.quantifiedstrategies.com/macd-and-rsi-trading-strategy-for-commodities/)
- [Unger Academy — Gold Trend-Following 2025](https://ungeracademy.com/blog/trend-following-strategies-gold-future-2025)
- [Initial Balance Breakout — TradeTheSwig](https://tradethatswing.com/one-trade-a-day-gold-strategy-411-in-last-year-fully-automatable/)
- [World Gold Council — Why Gold in 2026](https://www.gold.org/goldhub/research/why-gold-2026-cross-asset-perspective)
- [SSGA — Gold 2026 Outlook](https://www.ssga.com/us/en/intermediary/insights/gold-2026-outlook-can-the-structural-bull-cycle-continue-to-5000)
- [ACY — Gold Strategy Using VIX, Yields, DXY](https://acy.com/en/market-news/education/gold-strategy-using-vix-yields-dxy-2025-l-s-162409/)
- [FXNX — XAUUSD Correlation Secrets](https://fxnx.com/en/blog/xauusd-correlation-secrets-trading-gold-via-dxy-yields)
- [Seasonax — Gold Seasonal Patterns](https://www.seasonax.com/seasonal-gold-price-trends-and-investment-strategy/)
- [QuantStrategy.io — Calendar Spread Strategies](https://quantstrategy.io/blog/calendar-spread-strategies-in-futures-exploiting-contango/)
- [CME Group — Energy Calendar Spread Options](https://www.cmegroup.com/articles/whitepapers/trading-energy-calendar-spread-options.html)
- [FOREX.com — Carry Trade Strategy](https://www.forex.com/en-us/trading-guides/currency-carry-trades-explained/)
- [TioMarkets — Carry Trade 2026 Guide](https://tiomarkets.com/article/carry-trade-strategy-in-forex-a-complete-guide)
- [Robert Carver — Systematic Trading (Blog)](https://qoppac.blogspot.com/)
- [QuantEvolve — Multi-Agent Strategy Discovery (arXiv)](https://arxiv.org/html/2510.18569v1)
- [TradersPost — VWAP for Gold Trading](https://blog.traderspost.io/article/using-vwap-for-gold-trading-strategies)
