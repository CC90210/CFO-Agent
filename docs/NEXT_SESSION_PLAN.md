# ATLAS — Next Session Plan (March 20, 2026)

> Wake up. Execute. Profit.

## Priority 1: Deploy to Free VPS (30 min)

### Option A: Oracle Cloud Free Tier (BEST — 4 ARM cores, 24GB RAM, FREE FOREVER)
1. Sign up at cloud.oracle.com (requires credit card for verification, never charged)
2. Create an ARM Ampere A1 instance (4 OCPU, 24GB RAM — within Always Free tier)
3. Choose Ubuntu 22.04 minimal image
4. SSH in, install Docker:
   ```bash
   sudo apt update && sudo apt install -y docker.io docker-compose-plugin
   sudo usermod -aG docker $USER
   ```
5. Clone the repo:
   ```bash
   git clone https://github.com/YOUR_USERNAME/trading-agent.git
   cd trading-agent
   cp .env.example .env
   # Fill in API keys
   nano .env
   ```
6. Deploy:
   ```bash
   docker compose up -d --build
   docker compose logs -f
   ```
7. Verify paper trading is running, Telegram alerts working

### Option B: Google Cloud Free Tier (e2-micro, 1GB RAM — backup option)
- Tighter on resources but functional for paper trading
- Sign up at cloud.google.com, create e2-micro VM

### Option C: AWS Free Tier (t2.micro, 1GB RAM — 12 months free)
- Similar to GCP, good backup

## Priority 2: Run Quick Validation (15 min)

Run these commands on the VPS after deployment:
```bash
# Verify all tests pass
docker compose exec atlas-trader python -m pytest tests/ -v

# Quick sanity check — analyze BTC
docker compose exec atlas-trader python analyze.py BTC/USDT

# Start paper trading
docker compose exec atlas-trader python paper_trade.py
```

## Priority 3: Monitor First Trades (Ongoing)

- Watch Telegram for alerts
- Check logs: `docker compose logs -f --tail 100`
- After 1 hour: verify trades are being logged to database
- After 4 hours: check P&L in logs

## Priority 4: Implement Meta-Labeling (Next Coding Session)

This is the #1 enhancement from our research. Steps:
1. `pip install lightgbm mlfinlab scikit-learn`
2. Create `strategies/ml/meta_labeler.py`
3. Train on historical backtest results (use trade database)
4. Wire into engine.py between signal generation and execution
5. Backtest the improvement

## Priority 5: Add Funding Rate Arbitrage Strategy

Delta-neutral strategy collecting funding payments:
1. Create `strategies/defi/funding_rate_arb.py`
2. Monitor funding rates via CCXT (every 8h on Binance)
3. When rate > 0.03%: long spot + short perp
4. When rate normalizes: close both legs
5. Expected: 21%+ APY with near-zero directional risk

## Priority 6: Add Pairs Trading Strategy

Market-neutral statistical arbitrage:
1. Create `strategies/technical/pairs_trading.py`
2. Use Engle-Granger cointegration test on crypto pairs
3. Trade spread when Z-score > 2.0, exit at Z < 0.5
4. Start with BTC/ETH pair (highest liquidity, proven cointegration)

---

## Quick Reference

| Command | What It Does |
|---------|-------------|
| `docker compose up -d` | Start Atlas in background |
| `docker compose logs -f` | Watch live logs |
| `docker compose down` | Stop Atlas |
| `docker compose exec atlas-trader python -m pytest tests/ -v` | Run tests |
| `docker compose exec atlas-trader python analyze.py BTC/USDT` | Analyze a symbol |
| `docker compose exec atlas-trader python paper_trade.py` | Start paper trading |

## System Status (As of Tonight)

- **Tests:** 200/200 passing
- **Health Score:** 9.2/10
- **Strategies:** 12 registered (10 active, 2 disabled)
- **Docker:** Ready to deploy
- **YAML Params:** All matched to constructors
- **Execution Protocol:** Written at docs/EXECUTION_PROTOCOL.md
- **Research:** Saved at docs/STRATEGY_RESEARCH.md

---

*"Atlas doesn't sleep. Deploy it, and it trades while you do."*
