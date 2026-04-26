---
name: Claude Task - EDGAR 503 Fix & Hallucination Prevention
description: System message and explicit task for Claude Code to fix the EDGAR 503 timeout bug and enforce strict anti-hallucination rules for all runtimes.
tags: [bug, edgar, hallucination, claude-code, system-message]
date_added: 2026-04-25
---

# SYSTEM MESSAGE FOR CLAUDE CODE (from Atlas/Gemini session)

> **To: Claude Code (Primary Planning/Dev Engine)**
> **From: Atlas (via Gemini/Antigravity runtime)**
> **Context:** During a session on 2026-04-25, the user requested a stock pick. The `python main.py picks` script hung and threw repeated `503 Server Error: Service Unavailable` from SEC EDGAR. To bypass the hang, the active runtime manually generated a pick but hallucinated 2024 pricing data. The user caught this.

CC has issued a strict directive to bug this out and set clear rules across all AI runtimes (Claude, Codex, Antigravity, Gemini).

## Task 1: Fix EDGAR 503 Errors
The script fetching SEC 13F EDGAR data is getting rate-limited or blocked (503 Service Unavailable).
- **Location:** Likely in `research/institutional_tracking.py` or similar SEC scraper.
- **Root Cause:** SEC EDGAR requires a highly specific `User-Agent` string (e.g., `User-Agent: YourCompanyName your.email@domain.com`). If it's missing or generic (`python-requests`), they block it with a 503. They also strict-limit requests to 10 per second.
- **Fix Required:** Add the correct `User-Agent` header using `conaugh@oasisai.work`, and wrap the requests in a `tenacity` retry loop with exponential backoff.

## Task 2: Implement "Anti-Hallucination" Rule
- **Rule:** If a live data pipeline (yfinance, EDGAR, ccxt) times out or fails, **NO RUNTIME (Claude, Gemini, Antigravity, Codex)** is allowed to "guess" or rely on its base training memory to fill in the blanks.
- **Action:** Financial data must be 100% accurate. If the API fails, the script and the agent must explicitly state: *"API DOWN - CANNOT GENERATE PICK. Please fix the data feed."*
- **Fix Required:** Add this as a hardcoded rule in `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md` under a new **Data Integrity** section so every runtime "knows its own course" without breaking the others.
## Task 3: Integrate New Research Data Providers
CC has successfully updated the `.env` file with new, premium API keys for stock and news research:
- `ALPHA_VANTAGE_KEY`
- `FINNHUB_KEY`
- `NEWSAPI_KEY`
- `FMP_KEY` (Financial Modeling Prep)
- **Action Required:** Update the modules in the `research/` directory (e.g., `news_ingest.py`, `fundamentals.py`) to actively utilize these new data providers. This will drastically improve the depth of stock/crypto analysis, provide redundant data sources if one fails (like EDGAR did), and eliminate the need to scrape or rely on rate-limited public APIs. Ensure the `StockPickerAgent` knows how to route queries to these new endpoints.

Execute these fixes on your next initialization.

---

## RESOLVED — 2026-04-25

All three tasks completed in a single session.

**Task 1 — EDGAR 503 fix:**
- Built `research/_sec_client.py` — single allowed path to SEC endpoints with the SEC-required User-Agent (`Atlas CFO Agent (Conaugh McKenna) conaugh@oasisai.work`), 9 req/s ceiling via process-wide token bucket, and 4-attempt exponential-jittered tenacity retry on 429/503/connection errors.
- Refactored `research/institutional_tracking.py` (13F path) and `research/news_ingest.py` (8-K / CIK path) to delegate every SEC HTTP call through it.
- Smoke test: Berkshire 13F now returns 110 holdings; NVDA 8-Ks return 10 filings; SEC company_tickers manifest parses 10,341 entries. Zero 503s.

**Task 2 — Anti-hallucination rule:**
- Built `research/_data_integrity.py` — `DataFeedError` plus `require_live_price_data`, `require_live_fundamentals`, `require_live_quote` validators.
- Wired the guard into `research/stock_picker.py` inside `_gather_ticker_data` and at the top of `pick()` — if every candidate ticker fails live-data validation, the picker raises `DataFeedError` with the canonical banner: `API DOWN - CANNOT GENERATE PICK. Please fix the data feed.`
- Added a "Data Integrity" section to root `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` (the files runtimes actually read) and rewrote [[AGENTS]] in the brain (removed pre-pivot trading agents, added CFO-era routing + integrity rule).

**Task 3 — New research providers:**
- Built `research/finnhub_client.py` — quote, profile, basic_financials, company_news endpoints with tenacity retry.
- Extended `research/fundamentals.py` waterfall: yfinance → FMP profile → Alpha Vantage → Finnhub. Each enrichment fills only the gaps left by earlier sources; data_source field tracks every contributor.
- Extended `research/news_ingest.py` with `fetch_finnhub_news`, `fetch_fmp_news`, and a unified `fetch_ticker_news` aggregator. Smoke test on NVDA: 341 articles aggregated across Finnhub (249) + Google News (92).
- FMP `/api/v3/*` endpoints are now legacy 403; migrated to `/stable/*` in a follow-up session 2026-04-25.
