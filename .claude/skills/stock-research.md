---
description: "Stock research, picks, deep dives, insider/institutional tracking, earnings, options flow, sentiment, macro analysis. Use for any stock market or investment question."
---
# Atlas Stock Research Skill

> **NOTE:** Atlas does NOT execute trades or run algo-trading. All trading automation was archived on 2026-04-14 (see `archive/trading-automation/`). Atlas researches and recommends — CC executes manually on Wealthsimple/Kraken.

## When to activate
Any question about: stocks, picks, buy, sell, hold, market, research, deepdive, insider, institutional, earnings, options, sentiment, macro, sector rotation, what to invest in, portfolio.

## Quick Commands
```bash
python main.py picks "AI infra 6-12 mo"  # Stock picks with entry/exit/why
python main.py deepdive NVDA              # Bull/bear/base analysis on single ticker
```

## Research Pipeline (10 layers)
Atlas runs these data layers before making any recommendation:

1. **Macro** — `research/macro_watch.py` — geopolitical flashpoints, sector rotation
2. **News** — `research/news_ingest.py` — RSS, Google News, NewsAPI, SEC EDGAR
3. **Fundamentals** — `research/fundamentals.py` — P/E, margins, growth, 50/200 SMA, RSI, MACD
4. **Insider** — `research/insider_tracking.py` — SEC Form 4, cluster buying detection
5. **Institutional** — `research/institutional_tracking.py` — 13F filings, Buffett/Soros/Druckenmiller tracking
6. **Earnings** — `research/earnings_calendar.py` — EPS surprise history, PEAD signals
7. **Options** — `research/options_flow.py` — short interest, IV rank, squeeze scoring
8. **Sentiment** — `research/psychology.py` — Fear & Greed, VIX, AAII, put/call ratio
9. **Historical** — `research/historical_patterns.py` — seasonality, presidential cycle, analog matching
10. **Synthesis** — `research/stock_picker.py` — Claude Opus assembles all layers into execution-ready pick

## Skill Playbooks
- `skills/trade-protocol/SKILL.md` — 10-step trade decision framework
- `skills/position-sizing/SKILL.md` — Kelly criterion, micro account rules
- `skills/portfolio-rebalancing/SKILL.md` — tax-aware rebalancing

## Account Routing (where to place trades)
- Growth → TFSA (tax-free compound)
- US dividend/qualified → RRSP (treaty withholding waived)
- Short-term speculative → personal non-registered (losses offset gains)
- FHSA → first-home-allocated equities

## Saved Picks
Check `data/picks/*.md` for previously generated research.

## Rules
- Never claim certainty on a stock pick
- Never recommend a pick Atlas hasn't researched
- Always provide entry price, exit target, stop-loss, conviction (0-10), risks
- Reject conviction < 6
- No memes. No day-trading. No algo signals.
- Horizon bias: 3-18 months
- Position sizing must respect the Montreal $10K floor