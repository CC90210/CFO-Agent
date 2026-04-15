# Atlas Trading Agent — Deployment Guide

Deploys the Atlas paper trading agent as a self-contained Docker container.
Runs headlessly and restarts automatically. Suitable for Mac Mini, Raspberry Pi 4/5,
or any Linux VPS (Ubuntu 22.04+ recommended).

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Docker Engine | 24+ | `docker --version` |
| Docker Compose | v2.20+ | `docker compose version` |
| A populated `.env` file | — | See section below |
| 1 GB RAM minimum | — | 512 MB reserved for Atlas |
| 2 GB free disk | — | Image + logs + database |

---

## 1. Prepare the .env File

Copy the example and fill in real values before deploying. The agent will not
start without a valid `.env`.

```bash
cp .env.example .env
nano .env
```

Minimum required keys:

```dotenv
# Exchange
EXCHANGE_API_KEY=your_binance_api_key
EXCHANGE_SECRET=your_binance_secret
DEFAULT_EXCHANGE=binance
PAPER_TRADE=true          # Keep true until you are confident in live trading

# AI (required for multi-agent analysis)
ANTHROPIC_API_KEY=sk-ant-...

# Telegram (optional but recommended for trade alerts)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Database — points to the Docker volume path
DATABASE_URL=sqlite:////app/data/trading_agent.db
```

Never commit `.env` to git. It is listed in both `.gitignore` and `.dockerignore`.

---

## 2. Deploy

### Mac Mini or Linux VPS

```bash
# Clone (first time) or pull latest changes
git clone https://github.com/your-org/trading-agent.git
cd trading-agent

# Build and start detached
docker compose up -d --build

# Confirm it is running
docker compose ps
```

### Raspberry Pi (ARM64)

The `python:3.11-slim` base image supports linux/arm64 natively.
No changes to the Dockerfile are needed.

```bash
# Same as above — Docker BuildKit handles the ARM64 platform automatically.
docker compose up -d --build
```

If your Pi is 32-bit (ARMv7), add a platform override:

```yaml
# docker-compose.yml — under atlas-trader:
platform: linux/arm/v7
```

---

## 3. View Logs

```bash
# Live tail (Docker log driver output — stdout from the process)
docker compose logs -f atlas-trader

# Full log file written by paper_trade.py
docker exec atlas-trader cat /app/logs/paper_trade.log

# Or tail it live inside the container
docker exec -it atlas-trader tail -f /app/logs/paper_trade.log
```

Log files are stored in the `atlas-logs` named volume and rotate automatically
(10 MB max, 3 files) via the Docker json-file logging driver.

---

## 4. Stop and Restart

```bash
# Graceful stop (sends SIGTERM — Atlas flushes and prints session summary)
docker compose stop

# Start again (does not rebuild)
docker compose start

# Full restart
docker compose restart atlas-trader
```

---

## 5. Run a One-Off Command

Override the default `CMD` to run a backtest or analysis without touching
the running paper trader:

```bash
# Run a backtest (separate container, does not interfere with paper trader)
docker compose run --rm atlas-trader \
    python main.py backtest --strategy ema_crossover --symbol BTC/USDT --start 2024-01-01

# Multi-agent analysis
docker compose run --rm atlas-trader \
    python main.py analyze --symbol BTC/USDT
```

---

## 6. Update (Git Pull + Rebuild)

```bash
git pull origin master

# Rebuild the image and restart the container
docker compose up -d --build

# Verify the new container is healthy
docker compose ps
docker compose logs --tail=50 atlas-trader
```

The named volumes (`atlas-db`, `atlas-logs`) are preserved across rebuilds.
The database and all log history survive updates.

---

## 7. Inspect the Database

The SQLite database lives in the `atlas-db` named volume at
`/app/data/trading_agent.db` inside the container.

```bash
# Open an interactive SQLite shell
docker exec -it atlas-trader sqlite3 /app/data/trading_agent.db

# Quick query — last 10 paper trades
docker exec atlas-trader sqlite3 /app/data/trading_agent.db \
    "SELECT symbol, side, pnl, closed_at FROM trades ORDER BY closed_at DESC LIMIT 10;"
```

---

## 8. Switch to Live Trading

Live trading requires three explicit gates — all must be satisfied before a
real order is ever placed:

1. Set `PAPER_TRADE=false` in `.env`
2. Set `CONFIRM_LIVE=true` in `.env`
3. Run with the `--confirm-live` CLI flag

To use live mode as the container's default command, edit `docker-compose.yml`:

```yaml
command: ["python", "main.py", "live", "--strategy", "all", "--confirm-live"]
```

Then rebuild and restart:

```bash
docker compose up -d --build
```

**Never set `CONFIRM_LIVE=true` during paper trading.** The safety validator in
`config/settings.py` will raise an error if `PAPER_TRADE=false` and
`CONFIRM_LIVE=false` are combined.

---

## 9. Health Check

Docker monitors the container health every 60 seconds. To inspect:

```bash
docker inspect --format='{{json .State.Health}}' atlas-trader | python -m json.tool
```

If the container is marked `unhealthy`, check the logs:

```bash
docker compose logs --tail=100 atlas-trader
```

Common causes: missing `.env` keys, exchange API credentials rejected,
network timeout on startup.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Container exits immediately | Missing `.env` or bad API key | Check `docker compose logs` |
| `Config validation error` on start | Invalid `.env` value | Check Pydantic error in logs |
| `PAPER_TRADE=false` error | Safety gate triggered | Set `PAPER_TRADE=true` for paper mode |
| High memory usage | vectorbt loading large datasets | Reduce backtest candle window |
| Container marked unhealthy | Import error in core module | Check logs, rebuild image |
| Pi: `exec format error` | Wrong architecture | Ensure Docker buildx is installed |
