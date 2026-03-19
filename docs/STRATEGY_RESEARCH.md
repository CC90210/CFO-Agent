# ATLAS Strategy Research — March 2026

> Deep research compilation: top GitHub repos, profitable strategies, ML techniques, and deployment best practices.

## Top GitHub Trading Frameworks

| Framework | Stars | Key Edge | URL |
|-----------|-------|----------|-----|
| Freqtrade | ~48K | FreqAI adaptive ML retraining, Optuna optimization | github.com/freqtrade/freqtrade |
| Hummingbot | ~18K | Market making, cross-exchange arb, $34B+ volume | github.com/hummingbot/hummingbot |
| QuantConnect LEAN | ~18K | Multi-asset (stocks/forex/crypto/options), institutional grade | github.com/QuantConnect/Lean |
| FinRL | ~15K | Deep RL (PPO/A2C/DDPG), ensemble achieved Sharpe 2.81 | github.com/AI4Finance-Foundation/FinRL |
| ML for Trading (Jansen) | ~13K | Full ML pipeline textbook, feature engineering reference | github.com/stefan-jansen/machine-learning-for-trading |
| Jesse AI | ~7.6K | Cleanest strategy API, multi-TF native, JesseGPT | github.com/jesse-ai/jesse |
| OctoBot | ~5.5K | AI connectors (OpenAI/Ollama), TradingView webhooks | github.com/Drakkar-Software/OctoBot |
| VectorBT | ~4K | 1000x faster backtesting, NumPy/Numba accelerated | github.com/polakowo/vectorbt |
| Passivbot | ~3K | Evolutionary optimizer, grid/DCA on perpetual futures | github.com/enarjord/passivbot |
| PyBroker | ~2K | ML-native backtester, walk-forward built-in | github.com/edtechre/pybroker |
| HFTBacktest | ~2K | Queue position + latency simulation, L2/L3 order book | github.com/nkaz001/hftbacktest |

### Meta-Resources (Bookmarks)
- **best-of-algorithmic-trading**: github.com/merovinh/best-of-algorithmic-trading — 97 projects ranked by quality, updated weekly
- **awesome-systematic-trading (Papers)**: github.com/paperswithbacktest/awesome-systematic-trading — Academic strategies ordered by Sharpe ratio
- **awesome-systematic-trading (Resources)**: github.com/wangzhe3224/awesome-systematic-trading — Covers all asset classes
- **Freqtrade community strategies**: github.com/paulcpk/freqtrade-strategies-that-work — EMAPriceCrossover (118% total), DoubleEMACrossover (122% total)
- **FreqST.com**: Curated strategies from top Freqtrade performers

---

## Strategies to Implement (Priority Order)

### Tier 1 — High Impact, Medium Effort

#### 1. Meta-Labeling (ML Position Sizing)
- **Source**: Marcos Lopez de Prado, "Advances in Financial Machine Learning"
- **Repo**: github.com/hudson-and-thames/meta-labeling
- **How it works**: Train a LightGBM classifier on top of existing strategy signals to predict "will this signal be profitable?" Output probability adjusts position size.
- **Why it's #1**: Directly leverages our 12 existing strategies. No new signal generation needed. Strongest empirical support.
- **Features**: strategy name, conviction, regime, volatility, volume, recent win rate per strategy
- **Retraining**: Weekly on rolling 90-day window
- **Integration point**: Between orchestrator and risk manager, adjusting conviction scores

#### 2. Funding Rate Arbitrage (Delta-Neutral)
- **How it works**: Long spot + short perpetual futures. Collect funding rate (paid every 8h). Market-neutral.
- **Real numbers**: 21%+ APY on Pionex. Available on Binance, OKX, Bybit.
- **Entry**: When funding rate > 0.03% per 8h period
- **Exit**: When funding rate normalizes or goes negative
- **Risk**: Exchange counterparty risk, liquidation on short leg during extreme moves

#### 3. Pairs Trading / Statistical Arbitrage
- **Repos**: github.com/georgia-pj/statistical-arbitrage-strategy
- **How it works**: Find cointegrated crypto pairs (BTC/ETH, SOL/AVAX), trade the spread when Z-score > 2.0, exit at Z < 0.5
- **Edge**: Market-neutral. Works in CHOPPY regime where trend strategies fail.
- **Extends**: Our existing zscore_mean_reversion.py

#### 4. LightGBM Direction Predictor
- **Repo**: github.com/stefan-jansen/machine-learning-for-trading
- **How it works**: 100+ features from OHLCV → LightGBM predicts direction probability → conviction score
- **Key features** (ranked): lagged returns (1/5/10/20 bars), volatility (ATR, Garman-Klass), volume ratios, RSI, MACD histogram, Bollinger %B, time-of-day, regime
- **Critical**: NEVER use raw prices. Always returns, ratios, or normalized values.
- **Rule of thumb**: Need 10x more samples than features

### Tier 2 — Medium Impact, Low-Medium Effort

#### 5. Donchian Channel Breakout (Turtle Trading)
- **Source**: Original Turtle Trading rules (1983, proven for 40+ years)
- **How it works**: Enter on 20-day high/low breakout, exit on 10-day opposite breakout, ATR position sizing
- **Complements**: EMA crossover and multi-TF momentum as pure trend-following

#### 6. Grid/DCA Hybrid Strategy
- **Source**: Passivbot, OctoBot
- **How it works**: Grid captures range-bound oscillations, DCA reduces average entry on drawdowns
- **Yields**: 0.1-0.3%/day in ranging markets
- **Fills gap**: CHOPPY and HIGH_VOL regimes where trend and mean-reversion both struggle

#### 7. Liquidation Cascade Detector
- **Data**: Oct 2025 — $3.21B liquidated in 60 seconds
- **Monitor**: Open interest, funding rates, order book depth, bid-ask imbalance
- **Edge**: When OI is extreme + funding elevated, small price move triggers cascading liquidations. Position WITH the cascade.
- **Risk**: Very tight stops required — wrong direction means you're caught in it

#### 8. On-Chain Whale Tracking
- **Tools**: Glassnode (free tier), Whale Alert API, Arkham Intelligence
- **Signals**: Exchange inflows (selling pressure), outflows (accumulation), dormant wallet movements
- **Evidence**: Q1 2026 whales increased holdings 3.7% during corrections, preceded 23% rally

### Tier 3 — High Effort, Uncertain Return

#### 9. RL Ensemble Agent (FinRL)
- **How it works**: Train PPO + A2C + DDPG agents, use voting/ensemble for decisions
- **Reported**: Sharpe 2.81 (likely overfit — realistic target: 1.0-2.0)
- **Best use**: Portfolio-level allocator, not standalone signal generator
- **Warning**: RL agents are prone to overfitting and non-stationarity issues

#### 10. Transformer Directional Bias (PatchTST)
- **Repo**: github.com/yuqinie98/PatchTST (ICLR 2023)
- **Edge**: 21% MSE reduction over other transformer architectures
- **Best for**: Medium-term (daily+) directional bias, not precise entry/exit
- **Needs**: Large datasets, GPU for training

---

## Critical ML Infrastructure (Must-Have Before ML Strategies)

### Triple Barrier Labeling
- Labels: +1 (hit TP), -1 (hit SL), 0 (time expired)
- Compatible with Atlas Signal dataclass (already has stop_loss/take_profit)
- Package: `mlfinlab`

### Purged Cross-Validation
- Standard k-fold is INVALID for time series — guarantees overfit
- Purged CV removes overlapping train/test labels + embargo gap
- Package: `mlfinlab` or `skfolio`
- NON-NEGOTIABLE for all ML model training

### Fractional Differentiation
- Makes price series stationary while preserving memory (d=0.3-0.5)
- Integer differencing (d=1) throws away too much information
- Apply to all price-based features before ML training

---

## What Separates Profitable Bots from Losers

### Transaction Cost Reality Check
- Binance: 0.1% per side = 0.2% round trip
- Add slippage: 0.05% per side = 0.3% total round trip
- **Any strategy with avg gain/trade below 0.5% is likely unprofitable live**
- Short-term reversal: 41 bps without costs → 3 bps with costs
- Sharpe ratios above 3.0 are almost certainly overfit. Target: 1.0-2.0

### Fractional Kelly Sizing
- Full Kelly has severe volatility. Use 0.25x-0.5x Kelly.
- Formula: Kelly = (win_rate * avg_win - (1-win_rate) * avg_loss) / avg_win
- Apply per-strategy, not uniform

### HMM Regime Detection (Upgrade Path)
- Hidden Markov Models are gold standard for probabilistic regime detection
- Train on daily returns to find 2-3 hidden states
- Probabilistic output is more nuanced than our current hard-threshold classifier
- Ensemble HMM voting framework (multiple models) is most robust

### Adaptive Retraining
- FreqAI approach: retrain models every N candles in background thread
- Rolling window: 90 days training, retrain weekly
- This is what keeps models from going stale

---

## Deployment Recommendation

### For Live Trading (Crypto on Binance)
| Option | Cost | Pros | Cons |
|--------|------|------|------|
| **Hetzner VPS** | $6-20/mo | Cheapest, always on, low latency | Shared resources |
| **DigitalOcean** | $12-48/mo | Good docs, predictable pricing | Higher cost |
| **Raspberry Pi 5 (8GB)** | ~$80 one-time | No monthly cost, home control | Home internet dependency |
| **Mac Mini** | ~$600 one-time | Overkill but reliable | Expensive |

**Recommendation**: Hetzner VPS in Frankfurt or Singapore (close to Binance). 4 vCPU, 8GB RAM, 100GB NVMe. $20/mo. Docker deployment ready (config already built).

**Key insight**: Consistent latency > minimum latency. A VPS with steady 0.8ms beats one fluctuating 0.3-2.1ms.

---

## Python Packages to Add

```
lightgbm>=4.0          # Gradient boosted trees (meta-labeling, direction prediction)
mlfinlab>=2.0           # Triple barrier, purged CV, fractional differentiation
scikit-learn>=1.3       # ML infrastructure
hmmlearn>=0.3           # Hidden Markov Model regime detection
pytorch>=2.0            # GRU/LSTM (later)
neuralforecast          # PatchTST (later)
```

---

## YouTube / Educational Resources
- **Moon Dev** (@moondevonyt) — Daily algo trading streams, genetic algorithms, funding program
- **Part Time Larry** (@hackingthemarkets) — Python + markets, ORB strategies, 84 GitHub repos
- **Nicholas Renotte** — RL fundamentals applied to trading
- **QuantInsti** — Free workshops on HFT, algo trading conferences
- **QuantStart** — Kelly Criterion, HMM regime detection articles

---

*Compiled from deep research across GitHub, Reddit r/algotrading, academic papers, and trading communities. March 2026.*
