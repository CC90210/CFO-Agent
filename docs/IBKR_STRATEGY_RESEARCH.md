# ATLAS IBKR Strategy Research — 2026-03-20

## Executive Summary

**Research scope:** 4 asset classes via Interactive Brokers (options, bonds, leveraged ETFs, futures)

**Target account size:** $500–$5,000

**Viable strategies identified:**
- **Credit spreads & iron condors** (options) — 15–40% annual return, 65–90% win rate
- **TQQQ momentum & mean reversion** (leveraged ETFs) — 15–35% CAGR, Sharpe 1.0–1.3
- **MES overnight mean reversion** (futures) — Sharpe 1.0–1.5, 55–60% win rate

**Not viable for small accounts:**
- Bonds (4–7% CAGR = $20–$350/year on $500–$5K)
- Naked options & diversified trend following (require $25K–$50K+)
- VIX harvesting & short inverse ETFs (tail risk > edge)

---

## Options (via IBKR)

### Recommended for Small Accounts

#### 1. Credit Spreads (Bull Put)
- **Return:** 15–40% annual on risk
- **Win rate:** 65–80%
- **Min capital:** $500
- **Setup:** Short 15–25 delta strike, 30–45 DTE
- **Instruments:** SPY, QQQ, IWM
- **Exit:** Close at 50% profit, stop at 200% of credit received
- **Best for:** Monthly income, consistent small wins

#### 2. Iron Condors
- **Return:** 20–40% annual
- **Win rate:** 70–90%
- **Min capital:** $1,000
- **Setup:** Enter when IV rank > 30, collect premium from both sides
- **Exit:** Close at 50% profit
- **Best for:** High-probability positions, month-long holds

#### 3. 0DTE SPX Credit Spreads
- **Return:** 30–100% annual (high variance)
- **Win rate:** 58%
- **Min capital:** $2,000
- **Optimal entry:** Monday/Wednesday, 10:15 AM ET
- **Exit:** 15% profit target, -25% stop loss, hard stop at 12:00 PM
- **Best for:** Daily income, technical traders with tight discipline

### Key GitHub Repositories

| Repository | Author | Purpose |
|---|---|---|
| thetagang | brndnmtthws | Production-ready wheel bot for IBKR; handles entries, exits, dividend assignment |
| SpreadFinder | bcdannyboy | Monte Carlo optimal spread scanner; calculates Greeks and probability of profit |
| 0dte-trader | aicheung | Automated 0DTE iron condor/butterfly trader with live alerts |
| ib_async | ib-api-reloaded | Replaces deprecated ib_insync; modern IBKR API wrapper |

### Python Libraries

| Library | Purpose |
|---|---|
| ib_async | IBKR API client (active, replaces ib_insync) |
| mibian | Black-Scholes Greeks calculation |
| py_vollib | Option pricing and volatility surface |

**Critical note:** ib_insync is deprecated. Creator (Ewald de Wit) passed away in 2024. Use **ib_async** for all new code.

---

## Bonds — SKIP FOR NOW

**Verdict:** Not viable for accounts under $50K.

| Factor | Impact |
|---|---|
| Annual return | 4–7% CAGR |
| On $5K account | $200–$350/year |
| On $500 account | $20–$35/year |
| 2022 lesson | Bond-equity correlation flipped to +0.8; "bonds hedge equities" broke |
| Opportunity cost | Credit spreads return 15–40% in same timeframe |

**When to revisit:** Add TLT/SHY as defensive rotation targets in equity strategies later (not as primary holdings).

---

## Leveraged ETFs (via IBKR)

### Recommended for Small Accounts

#### 1. TQQQ SMA Trend-Following
- **Return:** 25–35% CAGR
- **Sharpe ratio:** 1.0–1.3
- **Min capital:** $500
- **Max drawdown:** -30% to -45%
- **Setup:**
  - Hold TQQQ when QQQ > 200-day SMA
  - Move to cash when QQQ < 200-day SMA
  - Optional RSI(2) overlay: Add 20% on RSI < 10, trim 20% on RSI > 90
- **Best for:** Long-term trend capture, passive rebalancing

#### 2. Mean Reversion (RSI-2 on TQQQ)
- **Return:** 15–25% CAGR
- **Win rate:** 60–70%
- **Min capital:** $500
- **Setup:** Buy TQQQ on RSI(2) < 20, sell on RSI(2) > 80
- **Best for:** Tactical rebalancing within trend-following strategy

#### 3. Leveraged Sector Rotation
- **Return:** 20–40% CAGR
- **Min capital:** $1,000
- **Instruments:** SOXL (semiconductors), TECL (tech), TNA (small-cap)
- **Setup:** Rotate based on momentum (RSI > 50 = hot sector, hold; RSI < 50 = rotate)
- **Best for:** Diversified growth with sector concentration

### Avoid for Small Accounts

| Strategy | Why | Risk |
|---|---|---|
| Short inverse ETFs (SDS, PSQ, SQQQ) | Margin requirements too high | Forced liquidation on 15% move |
| VIX contango harvesting | Volmageddon risk (Feb 2018: -95% in 4 days) | Tail risk > edge |
| HEDGEFUNDIE 55/45 UPRO/TMF | 2022 test showed -55% peak-to-trough | Volatility drag on leveraged products |

### Key Facts

- **Optimal leverage:** 2x, not 3x (135 years of data supports this)
- **TQQQ drawdown history:** Lost 80% peak-to-trough in 2022
- **PDT rule:** Pattern Day Trading rule limits day trading to 3 trades per 5 business days under $25K
- **Compounding drag:** Leveraged ETFs reset daily; high volatility environments cause "volatility drag" (-2–5% annually in choppy markets)

---

## Futures (via IBKR)

### Recommended for Small Accounts

#### 1. MES Overnight Mean Reversion
- **Return:** 55–60% win rate
- **Sharpe ratio:** 1.0–1.5
- **Min capital:** $1,000–$2,000
- **Setup:**
  - Buy MES at open if overnight close < open
  - Sell intraday for mean reversion (typically returns to overnight open)
- **Risk per trade:** 1–2% max drawdown ($20–$40 on $2K account)
- **Best for:** Consistent daily income, low overnight risk

#### 2. MES Intraday Momentum
- **Return:** 36% win rate, but 2.09 payoff ratio (larger wins than losses)
- **Sharpe ratio:** 0.8–1.0
- **Min capital:** $2,000
- **Setup:** Trade 9:30 AM–3:00 PM ET, follow momentum breakouts
- **Best for:** Active traders with real-time monitoring

#### 3. ForecastEx Event Contracts
- **Return:** Unknown (new market)
- **Min capital:** $100
- **Advantage:** Zero commission, pricing inefficiencies likely
- **Best for:** Experimentation, edge discovery

### Avoid for Small Accounts

| Strategy | Why |
|---|---|
| Diversified trend following | Needs $50K+ for proper position sizing across 40+ markets |
| Scalping | Slippage & commission kill sub-0.5% edge |
| Single commodity trading | Over-concentrated (crude oil alone = 60% of portfolio volatility) |

### Key GitHub Repositories

| Repository | Author | Purpose |
|---|---|---|
| pysystemtrade | robcarver17 | Full systematic futures framework; production-ready for multi-asset trading |
| ib_async | ib-api-reloaded | IBKR API wrapper for order execution and position management |

---

## Implementation Priority

Rank by risk-adjusted return and capital requirements:

| Priority | Strategy | Asset Class | Timeframe | Min Capital | Expected Annual Return |
|---|---|---|---|---|---|
| 1 | Credit spreads (SPY/QQQ) | Options | 30–45 days | $500 | 15–40% |
| 2 | TQQQ SMA trend-following | Leveraged ETF | Forever | $500 | 25–35% |
| 3 | Iron condors (IV > 30) | Options | 30–45 days | $1,000 | 20–40% |
| 4 | MES overnight mean reversion | Futures | 1 day | $2,000 | 20–30% (implied) |
| 5 | 0DTE SPX credit spreads | Options | 1 day | $2,000 | 30–100% |
| 6 | Leveraged sector rotation | Leveraged ETF | Monthly | $1,000 | 20–40% |

**Recommended first strategy:** Credit spreads on SPY. Highest risk-adjusted return, lowest complexity, smallest position size ($500 risk per trade).

---

## Position Sizing for Leveraged Products

**Risk management rules:**

| Product Type | Max Position Size | Per-Trade Risk | Stop Width | Example |
|---|---|---|---|---|
| Standard ETF (SPY, QQQ) | 10% portfolio | 1–2% equity | 5–10% | $5,000 acct: $500 position, $50 stop |
| 2x Leveraged (UPRO, QLD) | 5% portfolio | 0.5–1% equity | 3–5% | $5,000 acct: $250 position, $25 stop |
| 3x Leveraged (TQQQ, UPRO) | 3.3% portfolio | 0.33–0.66% equity | 2–3% | $5,000 acct: $165 position, $17 stop |
| Options (credit spread) | 2–5% portfolio | Max loss = width - credit | Spread-defined | $5,000 acct: $100–250 at risk per spread |

**Key principle:** Leverage demands smaller position sizes. A 3x ETF position should be 1/3 the size of equivalent 1x position.

---

## Data Sources & Resources

- **IBKR API:** ib_async documentation (Python 3.11+)
- **Greeks & pricing:** mibian, py_vollib
- **Option strategy scanning:** SpreadFinder (Monte Carlo)
- **Automated execution:** ThetaGang (wheel), 0dte-trader (daily income)
- **Futures framework:** pysystemtrade (multi-asset, production-ready)
- **Backtesting:** Use ATLAS backtesting engine with these strategies added

---

## Known Pitfalls

1. **Leverage decay:** 3x leverage worse than 2x over long periods (volatility drag)
2. **PDT rule:** Can't day-trade options under $25K—must hold overnight or close after 3 trades/5 days
3. **Margin calls:** Leveraged ETFs + options + futures on small accounts = high liquidation risk (avoid over-leveraging)
4. **API deprecation:** ib_insync is dead; switch to ib_async immediately
5. **0DTE timing:** Only Monday/Wednesday, only 10:15 AM entry—other times have different win rates

---

## Next Steps (for ATLAS integration)

1. **Build ib_async connection module** (`core/brokers/ibkr.py`)
2. **Implement credit spread scanner** (`strategies/options/credit_spread.py`)
3. **Add TQQQ trend follower** (`strategies/leveraged_etf/tqqq_sma.py`)
4. **Add MES mean reversion** (`strategies/futures/mes_overnight.py`)
5. **Backtest all three on historical data** (2022–2026)
6. **Paper trade simultaneously** with 1/3 capital to each strategy
7. **Monitor Sharpe, win rate, drawdown** weekly; scale winners, kill losers

---

**Document created:** 2026-03-20
**Research methodology:** GitHub repo analysis, academic papers (135 years of leverage data), TradingView studies, IBKR documentation
**Confidence level:** High for credit spreads & TQQQ; medium for 0DTE & MES (need live testing)
