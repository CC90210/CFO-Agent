# ATLAS Setup Guide — Complete Installation

**Version:** 2.0  
**Last Updated:** 2026-04-14  
**Time to complete:** 30 minutes (first run)

This guide walks a new owner through every step. Assumes Python 3.12, Git, and a terminal. Nothing else.

---

## Pre-Flight Checklist (5 minutes)

Before you start, gather these:

- [ ] **Python 3.12+** — Check with `python --version`
- [ ] **Git** — Check with `git --version`
- [ ] **Anthropic API key** — Sign up at `console.anthropic.com`, generate a key (~$5 API credits gets you 1 month of stock picks)
- [ ] **Telegram account** — Free. Create at `telegram.org`
- [ ] **Gmail account** (optional but recommended) — For receipt scanning
- [ ] **30 minutes** — First-time setup takes a half-hour. Subsequent runs are 5 seconds

---

## Step 1: Clone the Repository

```bash
git clone <repo-url> atlas
cd atlas
```

Replace `<repo-url>` with the actual GitHub URL.

---

## Step 2: Create a Python Virtual Environment

This keeps Atlas's dependencies isolated from your system Python.

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt. Good sign.

---

## Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs ~40 packages:
- `anthropic` — Claude API access
- `ccxt` — Crypto exchange integration (Kraken balance reads)
- `oandapyV20` — Forex (OANDA balance reads)
- `yfinance` — Stock data
- `python-telegram-bot` — Telegram bot framework
- `pydantic` — Configuration validation
- `python-dotenv` — `.env` file loading
- Plus: SQLAlchemy, requests, pandas, pytest, and utilities

**Time:** 2–3 minutes.

---

## Step 4: The `.env` File — Complete Key Reference

Copy the template:

```bash
cp .env.example .env
```

Now open `.env` in your editor. Fill in each variable.

### Required Keys

#### `ANTHROPIC_API_KEY`

**What it is:** Claude API token for stock research and natural-language reasoning.

**Get it:**
1. Go to `console.anthropic.com`
2. Sign up or log in
3. Create an API key
4. Copy and paste into `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-v0-abc123def456...
   ```

**Cost:** ~$0.003 per stock pick. $5 API credits = ~1,500 picks. Enough for a month.

**If you skip it:** Slash commands still work, but natural-language intent classification falls back to echoing your message. Stock picker returns "no API key configured."

---

#### `TELEGRAM_BOT_TOKEN`

**What it is:** Your Telegram bot's authentication token.

**Get it:**
1. Open Telegram, search for `@BotFather`
2. Send `/newbot`
3. Follow prompts (give bot a name, username)
4. BotFather sends you a token like `123456:ABC-DEFxyz789...`
5. Paste into `.env`:
   ```
   TELEGRAM_BOT_TOKEN=123456:ABC-DEFxyz789...
   ```

**Cost:** Free (Telegram's bot API is always free).

**If you skip it:** You can't run `python telegram_bridge.py`. CLI commands still work.

---

### Optional Keys (Enable Automations)

#### `GMAIL_USER` + `GMAIL_APP_PASSWORD`

**What they are:** Email address and app password for receipt scanning.

**Get them:**
1. Gmail Settings → Security → App passwords (requires 2FA enabled)
2. Generate password for "Mail" on "Windows/Mac/Linux"
3. Gmail gives you 16 characters: `xxxx xxxx xxxx xxxx`
4. Paste into `.env` (strip spaces):
   ```
   GMAIL_USER=your-email@gmail.com
   GMAIL_APP_PASSWORD=xxxxyyyyzzzzwwww
   ```

**Cost:** Free (part of your Gmail).

**If you skip it:** `/receipts` command won't work. Other commands unaffected.

---

#### `EXCHANGE_API_KEY` + `EXCHANGE_SECRET`

**What they are:** Kraken API credentials for balance reads.

**Get them:**
1. Log in to Kraken
2. Settings → API → Generate New Key
3. Scope: Query Funds only (no trading perms)
4. Copy public key and private key
5. Paste into `.env`:
   ```
   EXCHANGE_API_KEY=abc123def456...
   EXCHANGE_SECRET=xyz789abc123...
   ```

**Cost:** Free.

**If you skip it:** `/networth` skips Kraken. Other accounts still appear.

---

#### `OANDA_TOKEN` + `OANDA_ACCOUNT_ID`

**What they are:** OANDA forex/metals trading account credentials.

**Get them:**
1. Log in to OANDA (oanda.com)
2. Account Settings → API Access
3. Copy API token and account ID
4. Paste into `.env`:
   ```
   OANDA_TOKEN=...
   OANDA_ACCOUNT_ID=...
   ```

**Cost:** Free.

**If you skip it:** `/networth` skips OANDA.

---

#### Research APIs (All Free-Tier)

These power stock research. All have free tiers; no payment required:

```
# Alpha Vantage (25 requests/day, free)
ALPHA_VANTAGE_KEY=...

# Finnhub (60 requests/minute, free)
FINNHUB_KEY=...

# NewsAPI (100 requests/day, free)
NEWSAPI_KEY=...

# Financial Modeling Prep (250 requests/day, free)
FMP_KEY=...
```

**Get them:** Sign up at each site (takes 2 minutes per site), get free API key.

**Cost:** Free tier is sufficient. Paid upgrades available ($43–$120/mo) for higher limits.

**If you skip them:** Stock picker still works, but with slower data fetching and limited historical analysis.

---

#### `STRIPE_API_KEY` + `WISE_API_TOKEN`

**What they are:** Payment processor read-only credentials (future features).

**Get them:** Currently unused. Optional. Can skip for now.

---

### Sample `.env` (Minimal, Ready to Use)

```bash
# Required for research + picks
ANTHROPIC_API_KEY=sk-ant-v0-abc123...

# Required for Telegram bot
TELEGRAM_BOT_TOKEN=123456:ABCxyz789...

# Optional but recommended: receipts
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=xxxxyyyyzzzzwwww

# Optional: balance reads
EXCHANGE_API_KEY=abc123...
EXCHANGE_SECRET=xyz789...
OANDA_TOKEN=...
OANDA_ACCOUNT_ID=...

# Optional: research (free tier)
ALPHA_VANTAGE_KEY=...
FINNHUB_KEY=...
NEWSAPI_KEY=...
FMP_KEY=...
```

---

## Step 5: Run the Setup Wizard

This interactive interview populates `brain/USER.md` with your financial profile.

```bash
python main.py setup
```

You'll be asked:
- Your name, age, location
- Citizenship (triggers tax planning)
- Income sources (MRR, revenue, currencies)
- Account platforms (Kraken, OANDA, Wise, banks, TFSA, RRSP, FHSA)
- Assets (cash, investments, real estate, debt)
- Tax info (last return filed, deductions, carryforwards)
- Risk tolerance and goals
- Data access preferences (Gmail, Stripe, Wise)

**Output:** `brain/USER.md` is created. Attestation saved in `memory/SESSION_LOG.md`.

**Time:** 10–15 minutes.

**Can't be bothered?** Skip this and manually edit `brain/USER.md` with rough estimates. You can refine anytime.

---

## Step 6: Verify Installation

```bash
python -c "import cfo.dashboard, research.stock_picker; print('✓ Atlas ready')"
```

You should see:
```
✓ Atlas ready
```

If you get import errors, check:
- Did `pip install -r requirements.txt` complete without errors?
- Are you in the `.venv` (check terminal prompt for `(.venv)`)?

---

## Step 7: First Run — Net Worth

```bash
python main.py networth
```

Expected output: A table of your account balances. If an API key is missing, that section is skipped gracefully.

Example:
```
================================================================================
  ATLAS NET WORTH SNAPSHOT  |  2026-04-14  |  CAD
================================================================================

CASH
  RBC CAD:           $6,419.00
  Wise USD:          $2,847.00 (~$3,994.00 CAD)
  Total Cash:        $10,413.00 CAD

CRYPTO
  Kraken BTC:        $350.00 USD (~$490.00 CAD)
  Kraken SOL:        ...
  Total Crypto:      ...

STOCKS
  Wealthsimple TFSA: ...

REGISTERED
  TFSA:              $155.16
  RRSP:              $0.00
  FHSA:              $0.00

NET WORTH:          $42,350.00 CAD
```

All values are in CAD. Change vs. last month is tracked if you run it regularly.

---

## Step 8: Start the Telegram Bot

Open a new terminal window (keep this one open in background):

```bash
python telegram_bridge.py
```

Expected output:
```
2026-04-14 12:34:56 | INFO | atlas.telegram_bridge | Atlas bot started. Listening for messages.
```

Keep this window open. The bot needs the process running to receive messages.

---

## Step 9: Test the Bot

1. Open Telegram on your phone or desktop
2. Search for the bot username you created (via BotFather)
3. Send `/start`
4. You should see:
   ```
   ATLAS — CC's CFO on your phone.
   
   Say anything naturally, or use commands:
   /networth /runway /status /taxes ...
   ```

5. Try a command: `/networth`
6. Bot responds with your net-worth snapshot

**You're live.** Try other commands: `/runway`, `/taxes`, or type naturally: "what's my runway?"

---

## (Optional) Step 10: Run Bot as a Daemon

The terminal window running `python telegram_bridge.py` needs to stay open. To make it permanent (survive reboots, run in background):

### Windows: Task Scheduler

1. Create a batch file `C:\atlas\run_bot.bat`:
   ```batch
   @echo off
   cd /d C:\Users\YourName\APPS\trading-agent
   C:\Users\YourName\APPS\trading-agent\.venv\Scripts\python.exe telegram_bridge.py
   pause
   ```

2. Open **Task Scheduler**
3. **Create Basic Task**
   - Name: Atlas Telegram Bot
   - Trigger: "At log on"
   - Action: "Start a program" → point to `run_bot.bat`
4. Save

Bot now starts automatically on login.

### macOS: launchd

Create `~/Library/LaunchAgents/com.atlas.telegram.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.atlas.telegram</string>
    <key>Program</key>
    <string>/path/to/.venv/bin/python</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/trading-agent/telegram_bridge.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/trading-agent</string>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

Then:
```bash
launchctl load ~/Library/LaunchAgents/com.atlas.telegram.plist
```

### Linux: systemd

Create `/etc/systemd/system/atlas.service`:

```ini
[Unit]
Description=ATLAS Telegram Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/atlas
ExecStart=/home/youruser/atlas/.venv/bin/python telegram_bridge.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable atlas.service
sudo systemctl start atlas.service
```

---

## Step 11: Optional Data to Add Manually

Atlas pulls account balances via API, but some data must be entered manually:

### `data/manual_balances.json`

Bank accounts, real estate, items without API access:

```json
{
  "accounts": {
    "RBC chequing": {
      "balance_cad": 6419.00,
      "last_updated": "2026-04-14"
    },
    "home_equity": {
      "estimated_value_cad": 400000.00,
      "mortgage_balance": 250000.00
    }
  }
}
```

### `data/crypto_trades.csv`

Every buy/sell for accurate ACB (average cost basis):

```
date,symbol,type,quantity,price_cad,fee_cad,notes
2024-06-15,BTC,BUY,0.005,42000,50,Kraken spot buy
2024-08-20,BTC,BUY,0.003,46000,30,DCA
2026-03-10,BTC,SELL,0.002,55000,50,Tax loss harvest
```

### `data/target_allocation.json`

Your target portfolio (for rebalancing recommendations):

```json
{
  "crypto": 0.15,
  "stocks": 0.55,
  "cash": 0.20,
  "bonds": 0.10
}
```

---

## Dependency Map — What You're Installing

| Package | Purpose | Required? |
|---------|---------|-----------|
| `anthropic` | Claude API (picks, research, natural language) | Yes |
| `python-telegram-bot` | Telegram bot framework | For bot only |
| `ccxt` | Crypto exchange integration (Kraken reads) | Optional |
| `oandapyV20` | OANDA forex integration | Optional |
| `yfinance` | Stock price + fundamentals | Stock picks |
| `pydantic` | Configuration validation | Core |
| `python-dotenv` | `.env` file loading | Core |
| `requests` | HTTP requests (news, APIs) | Core |
| `pandas` | Data manipulation | Optional |
| `sqlalchemy` | Database ORM | Optional |
| `pytest` | Testing framework | Dev only |

All packages are publicly available. No custom/proprietary packages.

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'cfo'"

**Problem:** You're not in the `.venv` or dependencies didn't install.

**Solution:**
1. Activate venv: `source .venv/bin/activate` (Mac/Linux) or `.venv\Scripts\activate` (Windows)
2. Re-run `pip install -r requirements.txt`
3. Try again: `python main.py networth`

---

### "I/O operation on closed file" (Telegram)

**Problem:** Stdout encoding issue on Windows.

**Solution:** Use Windows Terminal (built-in) instead of Command Prompt. Or set environment variable:
```bash
set PYTHONIOENCODING=utf-8
python telegram_bridge.py
```

---

### "ModuleNotFoundError: db"

**Problem:** Rare edge case where the db module was archived but config still references it.

**Solution:**
```bash
git pull origin master
pip install -r requirements.txt
```

---

### "Gmail receipts: authentication failed"

**Problem:** Wrong password or IMAP not enabled.

**Check 1:** Enable IMAP in Gmail
1. Gmail Settings → Forwarding and POP/IMAP
2. Enable IMAP
3. Save

**Check 2:** Use app password, not account password
1. Gmail Settings → Security → App passwords (requires 2FA)
2. Generate password for "Mail" device type
3. Copy the 16-character password (e.g., `xxxx xxxx xxxx xxxx`)
4. Paste into `.env`, strip spaces: `GMAIL_APP_PASSWORD=xxxxyyyyzzzzwwww`

---

### "Kraken API: invalid key"

**Problem:** API key doesn't have read-only scope or is malformed.

**Solution:**
1. Log in to Kraken
2. Settings → API → Create New Key
3. Scope: **Query Funds** (read-only)
4. Copy public + private key
5. Paste both into `.env`
6. Test: `python main.py networth`

---

### "ANTHROPIC_API_KEY missing"

**Problem:** You didn't set the API key.

**Solution:**
1. Get key: `console.anthropic.com`
2. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-v0-...`
3. Restart bot: `Ctrl+C`, then `python telegram_bridge.py`

---

## Security Best Practices

1. **Never commit `.env`** — It's in `.gitignore`. Do not add it to Git.
2. **Use read-only API keys** — Kraken, Stripe, Wise should all have read-only scope. Never share trading keys.
3. **Rotate keys quarterly** — Generate new API keys every 3 months and update `.env`.
4. **Keep repo updated** — `git pull origin master` regularly for security patches.
5. **Don't share `.env` with others** — It contains your secrets. Keep it local.

---

## Going to Production (Self-Hosted VPS)

If you want to run Atlas on a remote server (so the bot runs 24/7 without your laptop):

1. **Rent a small VPS:**
   - DigitalOcean: $6/mo (1 GB RAM, Ubuntu 22.04)
   - Hetzner Cloud: €4/mo (2 GB RAM, Germany)
   - Linode: $5/mo (1 GB RAM, US)

2. **SSH into the server** and repeat Steps 1–9 above (Git clone, venv, install, setup, run)

3. **Use a process manager:**
   ```bash
   # Install pm2 (Node.js package manager)
   npm install -g pm2
   
   # Start bot
   pm2 start "python telegram_bridge.py" --name atlas --cwd /path/to/atlas
   
   # Enable startup
   pm2 startup
   pm2 save
   ```

4. **Enable automated backups** of `brain/` and `memory/`:
   ```bash
   # Backup to S3 or cloud storage weekly
   0 2 * * 0 tar czf /tmp/atlas_backup.tar.gz ~/atlas/brain ~/atlas/memory && \
   aws s3 cp /tmp/atlas_backup.tar.gz s3://your-bucket/atlas/
   ```

---

## Frequently Asked Questions

**Q: Do I need all the API keys?**  
A: No. Only `ANTHROPIC_API_KEY` + `TELEGRAM_BOT_TOKEN` are truly required. Everything else is optional and enables specific features.

**Q: How much will this cost?**  
A: Depends on what you use:
- Anthropic API: $0–$5/month (for moderate stock research)
- Telegram: $0 (always free)
- Gmail/Wise/Kraken: $0 (free tier)
- Research APIs: $0 (free tier, or $43–$120/mo for paid)
- Server (optional): $0 (runs locally) or $5–15/mo (VPS for 24/7 daemon)

**Q: Can I use this for a business partner?**  
A: Not yet. Currently single-user. Multi-user mode planned for Q2 2026.

**Q: What if I move to a different country?**  
A: Update `brain/USER.md` with your new tax residency. Atlas has tax strategies for US, UK, Ireland, and Crown Dependencies. Recalculates everything automatically.

**Q: Can I sell picks Atlas generates?**  
A: Atlas is for personal use. If you repackage picks for clients, you're liable for investment advice. Check securities law in your jurisdiction.

**Q: Where is my data stored?**  
A: All data is on your machine (or your VPS, if you self-host remotely). Nothing is sent to a central server. APIs called: Anthropic (for reasoning), your brokers (balance reads), Gmail (receipts).

---

## Next Steps (After Setup)

1. **Run monthly commands:**
   ```bash
   python main.py networth
   python main.py runway
   python main.py taxes
   ```

2. **Use Telegram for daily checks:**
   ```
   /networth
   "am I going to make it in Montreal?"
   /picks "AI plays"
   ```

3. **Read the full user guide:** `docs/ATLAS_USER_GUIDE.md` for deep dives on each module.

4. **Update `brain/USER.md` quarterly** after major life changes (new income source, relocation, incorporation, etc.).

---

## Support

- **Bugs?** File an issue on GitHub with: command run, expected output, actual output, error message, Python version, OS.
- **Questions?** Read `ATLAS_USER_GUIDE.md` and `TELEGRAM_GUIDE.md` first.
- **Feature requests?** Open an issue on GitHub.

---

**Last Updated:** 2026-04-14  
**Maintainer:** CC McKenna, OASIS AI Solutions  
**Status:** Production-ready. Tested on Windows 11, macOS 13+, Ubuntu 22.04+
