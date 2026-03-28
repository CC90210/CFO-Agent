---
name: ATLAS Growth Timeline
description: Capability evolution from v1.0 to current — milestones, skills acquired, next frontier
tags: [growth, evolution, milestones, timeline]
---

# ATLAS Growth Timeline

> Tracks capability evolution. Updated on major milestones.

## Version History

### V1.0 — Foundation (Sessions 1-5, ~2026-03-16)
- Basic trading strategies (RSI, EMA crossover, Bollinger)
- CCXT integration for Kraken
- Backtest engine with regime-aware filtering
- Risk manager with hardcoded kill switches
- 10 AI agents (4 analysts + debate + risk + portfolio + Darwinian)
- Basic Telegram bot

### V1.5 — Strategy Expansion (Sessions 6-12)
- 12 strategies registered (added VWAP, multi-TF momentum, London breakout, opening range, smart money, Ichimoku, order flow, Z-score, volume profile)
- OANDA integration (gold/forex)
- Trailing stop system (Chandelier, Parabolic SAR, ATR-trail, composite)
- Trade protocol framework (10-step decision)
- Correlation tracker
- Live exit loop fixed (real Kraken sell orders)
- 140 tests passing

### V2.0 — CFO Expansion (Sessions 13-22)
- 4 finance modules (tax.py, advisor.py, wealth_tracker.py, budget.py)
- 18-document tax knowledge base (~16,500 lines)
- 3 domain skills (accounting-advisor, tax-optimization, financial-planning)
- Brain/ directory (CAPABILITIES.md, STATE.md)
- Regime hysteresis (min_hold_bars=6, 51% false transition reduction)
- Portfolio tightening (+110% improvement)
- OANDA thread safety (Semaphore(2))
- Daemon freeze fix (single-instance enforcement)
- Position sizing overhaul for micro accounts
- **Tax filing: 2025 taxes filed successfully**
- Crown Dependencies + UK passport strategy added
- Income-scaling playbook (Tier 0 to Tier 6)
- Foreign reporting guide (T1135, T1134, transfer pricing)
- TOSI defense guide
- VDP guide
- HST registration guide
- Installment payment guide

## Capability Frontier

### Current Limits
- Trading: micro account ($136) limits strategy effectiveness
- Tax: no CRA My Account access (CC must log in)
- Brokers: Alpaca not configured (no US equities)
- International: Crown Dependencies strategy is theoretical (CC hasn't relocated)

### Next Level (V2.5 targets)
- Wire trade_protocol.py into engine.py
- Wire correlation_tracker.py into risk_manager.py
- Multi-day paper trading validation
- FHSA opened and contributing
- CRA My Account access for CC
- Alpaca paper trading configured
- Quarterly tax review automation

### Long-Term (V3.0 vision)
- Full autonomous trading across crypto + metals + equities
- Automated tax-loss harvesting (Q4 flag and execute)
- Real-time income tier monitoring with strategy adjustments
- International entity setup when income triggers
- Automated quarterly installment calculations
