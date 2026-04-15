# Atlas Research Module

On-demand equity research, stock picking, and macro analysis engine.
Built for CC's ATLAS CFO agent. Free-tier APIs only at launch, with a clear upgrade path.

## Architecture

```
research/
├── __init__.py          # Module exports
├── news_ingest.py       # RSS, Google News, NewsAPI, SEC EDGAR
├── macro_watch.py       # Geopolitical flashpoints, sector rotation, macro context
├── fundamentals.py      # yfinance / Alpha Vantage / FMP fundamentals + technicals
├── stock_picker.py      # StockPickerAgent (Claude-powered) + CLI
├── prompts/
│   └── stock_pick.md    # Full Claude prompt template (edit to tune behavior)
└── README.md

data/
├── cache/               # Auto-cached API responses (news: 1hr, fundamentals: 24hr)
└── picks/               # Saved pick files (markdown) + tracking log
```

## Quick Start

```bash
# Get 3 picks for a theme
python -m research.stock_picker "AI infrastructure plays for next 6 months"

# Get 5 picks for a different theme
python -m research.stock_picker "defense stocks ahead of NATO summit" -n 5

# Deep dive on a specific stock
python -m research.stock_picker --deep-dive NVDA

# Save picks to data/picks/
python -m research.stock_picker "uranium nuclear energy plays" --save

# Get raw JSON output (for piping to other tools)
python -m research.stock_picker "biotech GLP-1 plays" --json
```

## Python API

```python
from research.stock_picker import StockPickerAgent

agent = StockPickerAgent()

# Get 3 picks
picks = agent.pick("AI infrastructure plays for 6 months", n=3)
for pick in picks:
    print(f"{pick.ticker}: {pick.conviction}/10 conviction, {pick.upside_pct:.1f}% upside")
    agent.save_pick(pick)

# Deep dive
dd = agent.deep_dive("NVDA")
print(dd.final_verdict)
print(dd.to_markdown())

# Macro context only
from research.macro_watch import macro_context_summary
from research.news_ingest import fetch_google_news
news = fetch_google_news("Middle East oil supply", days=7)
print(macro_context_summary(news))

# Fundamentals only
from research.fundamentals import get_fundamentals, get_price_history, technicals
fund = get_fundamentals("NVDA")
print(fund.valuation_summary())
df = get_price_history("NVDA", period="2y")
tech = technicals(df)
print(tech)
```

## Data Sources

### Free (No Key Required)

| Source | What it provides | Rate Limit | Cached |
|--------|-----------------|------------|--------|
| yfinance | Fundamentals, price history, insider data | ~2000/day (soft) | 24hr / 1hr |
| Google News RSS | News search for any query | Soft (no documented limit) | 1hr |
| SEC EDGAR JSON API | 8-K, 10-K, 10-Q filings | 10 req/sec | 1hr |
| Curated RSS feeds | 15 business/finance feeds | None | 1hr |

### Free With Key (Set in `.env`)

| Variable | Source | Free Tier | Best For |
|----------|--------|-----------|----------|
| `ALPHA_VANTAGE_KEY` | alphavantage.co | 25 req/day | P/E, analyst targets, EPS |
| `FINNHUB_KEY` | finnhub.io | 60 req/min | Earnings calendar, insider trades |
| `NEWSAPI_KEY` | newsapi.org | 100 req/day | Structured news search |
| `FMP_KEY` | financialmodelingprep.com | 250 req/day | 10-yr financials, DCF ratios |

## Paid Upgrade Path

When CC is ready to invest in research infrastructure, here are the recommended upgrades ranked by ROI:

### Tier 1: Immediate ROI ($43/mo)

| Service | Cost | What it unlocks | ROI case |
|---------|------|-----------------|----------|
| **Financial Modeling Prep Premium** | $14/mo | 10-yr historical financials, DCF models, ratios, 750 req/day (vs 250), comparable analysis | 1 avoided bad trade > $14/mo |
| **Polygon.io Starter** | $29/mo | Real-time US equity quotes, options flow, tick data, 100% uptime SLA | Needed once CC wants to time entries precisely |

### Tier 2: News Edge ($27/mo)

| Service | Cost | What it unlocks | ROI case |
|---------|------|-----------------|----------|
| **Benzinga Pro Basic** | $27/mo | Real-time news squawk, analyst ratings wire, institutional-grade alerts | Edge on earnings pre-announcement news |

### Tier 3: Quant Edge ($34/mo)

| Service | Cost | What it unlocks | ROI case |
|---------|------|-----------------|----------|
| **Seeking Alpha Premium** | $19/mo | Earnings estimates, quant ratings, author analysis | SA quant ratings have strong backtested alpha |
| **TIKR Terminal** | $15/mo | Bloomberg-lite: 20-yr financials, segment data, screen | Deep comps for serious due diligence |

### Recommended Starter Bundle

If CC has one pick per month that works, **FMP Premium + Polygon Starter ($43/mo)** pays for itself.

**Priority order:**
1. FMP Premium ($14) — deepens fundamental analysis immediately
2. Polygon Starter ($29) — unlocks real-time data and options flow
3. Benzinga Pro ($27) — only if CC wants to be faster on news catalysts
4. SA Premium ($19) + TIKR ($15) — for serious stock-level deep dives

Total cost at full build-out: ~$104/mo. One successful trade per quarter covers it.

## How the Claude Prompt Works

The prompt in `prompts/stock_pick.md` instructs Claude to:
1. Think like a senior portfolio manager, not a retail analyst
2. Enforce CC's risk profile (aggressive, Canadian tax context, TFSA-first)
3. Apply anti-bullshit rules: no meme stocks, no uncritical bull cases, demand downside math
4. Require conviction >= 6/10 (rejects weak picks automatically)
5. Return strict JSON for clean parsing

To tune Claude's behavior, edit `prompts/stock_pick.md` directly. The file is hot-loaded on each run.

## Caching

All API responses are cached in `data/cache/`. Cache files are named by MD5 hash of the request parameters.

| Data type | TTL |
|-----------|-----|
| News (RSS / Google News / NewsAPI) | 1 hour |
| SEC filings | 1 hour |
| Fundamentals (yfinance / AV / FMP) | 24 hours |
| Price history | 1 hour |
| CIK lookups (EDGAR) | 24 hours |

To force a refresh, delete the relevant `data/cache/fund_*.json` or `news_*.json` files.

## Adding New Sectors / Tickers

Edit `_SECTOR_DEFAULTS` in `stock_picker.py` to add new keyword → ticker list mappings.
The agent uses these as candidates when no explicit tickers are passed.

## Geopolitical Flashpoints

Active flashpoints are defined in `macro_watch.py` in `_FLASHPOINTS`. Each flashpoint has:
- `escalation_triggers`: keywords that signal the situation is heating up in news
- `sector_impacts`: which sectors move and in which direction if this escalates
- `related_tickers`: direct-impact stocks to watch

To add a new flashpoint, add a `Flashpoint` object to `_FLASHPOINTS`.
