# Atlas on Telegram — Complete Guide

**Version:** 2.0  
**Last Updated:** 2026-04-14

---

## What Atlas on Telegram Is

Your CFO in your pocket. Telegram lets you talk to Atlas naturally from anywhere—your phone, desktop, wherever. Ask a question in plain English, and Atlas runs the right analysis instantly. Or use slash commands for speed when you know exactly what you need.

This is how most owners use Atlas day-to-day: quick financial checks, stock research while commuting, tax updates. The CLI is for deep work; Telegram is for living.

---

## First-Time Setup (10 minutes)

### Step 1: Create a Telegram Bot

1. Open Telegram, search for `@BotFather`
2. Send `/newbot`
3. Follow the prompts (give it a name, username)
4. BotFather gives you a token (example: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
5. Copy this token and paste it into `.env`:

```
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
```

### Step 2: Start the Bot Process

Open a terminal in your atlas directory and run:

```bash
python telegram_bridge.py
```

You'll see:

```
2026-04-14 12:34:56 | INFO | atlas.telegram_bridge | Atlas Telegram bot started. Polling for messages.
```

Leave this terminal open. (Optional: run it as a daemon via pm2, systemd, or Windows Task Scheduler — see **Daemonize the Bot** below.)

### Step 3: Send `/start` From Your Phone

1. Find your newly created bot in Telegram (search the username you gave it)
2. Send `/start`
3. Atlas auto-registers your Telegram user ID (if not already set in `.env`)
4. You'll see the help text. You're live.

**That's it.** No passwords, no OAuth, no third-party apps. Just your bot token and your Telegram user ID.

---

## Two Ways to Talk to Atlas

### 1. Slash Commands (Fast & Deterministic)

Slash commands are pre-built. They run instantly, no AI reasoning needed. Use these for routine checks.

```
/networth
```
→ Instant net-worth snapshot. Shows all accounts, balances, total.

```
/runway
```
→ Montreal cashflow estimate. How many months of runway given current burn?

```
/status
```
→ Quick financial pulse: cash on hand, MRR, months of runway, any immediate risks.

```
/taxes
```
→ Quarterly tax estimate. YTD income, deductions, tax owing, next payment date.

```
/receipts [YYYY-MM-DD]
```
→ Sync Gmail receipts since date. Pull all receipts from inbox, categorize them, give you a summary.

```
/picks <query>
```
→ Generate stock picks. Example: `/picks AI infrastructure plays for 6 months`

```
/deepdive <TICKER>
```
→ Full analysis on one stock. Bull case, bear case, base case, catalysts, risks.

```
/news <topic>
```
→ Top 5 headlines on a topic (last 7 days). Example: `/news Fed policy`

```
/macro
```
→ Current geopolitical flashpoints + their market impact. What's moving sectors?

```
/brain <file>
```
→ Read a brain/ document. Example: `/brain USER` reads `brain/USER.md`

```
/help
```
→ Show command list.

---

### 2. Natural Language (Powerful & Flexible)

Type ANY non-slash message, and Atlas interprets it via Claude. This is where the CFO intelligence lives.

Examples:

```
"am I going to make it in Montreal?"
```
→ Atlas runs cashflow analysis, reads runway scenarios, current MRR vs rent. Verdict: "You have 4–7 months depending on revenue. Breakeven at $2,500/mo. Diversify within 3 months."

```
"give me 3 AI plays for the next 6 months"
```
→ Full research pipeline. Returns: ticker, conviction, entry/exit, thesis, catalysts, risks.

```
"should I sell my DOGE?"
```
→ Atlas reads your Kraken position, ACB, current price, tax impact. Recommendation with risks.

```
"how much tax should I set aside?"
```
→ YTD income from all sources, applies Ontario rates, suggests quarterly reserve and payment dates.

```
"what's the Fed doing this week?"
```
→ News ingest + macro watch synthesized. Plain-English summary of Fed announcements and impact on your sectors.

```
"deep dive on NVDA"
```
→ Fundamentals (valuation, growth, margins), news (last 14 days), technicals, bull/bear/base cases.

```
"is there an earnings trap on my watchlist?"
```
→ Atlas checks earnings calendar, identifies companies with earnings near your entries, flags risks.

```
"pull my receipts from January"
```
→ Scans Gmail since 2026-01-01, OCRs, categorizes (meals, software, equipment, travel). Exports summary.

```
"who owns NVDA besides me?"
```
→ 13F tracking. Shows insider/institutional positions, who's accumulating, who's selling.

```
"am I overbought on NVDA?"
```
→ Technical check. RSI, Bollinger bands, price vs 50/200 SMA. Verdict: overbought/neutral/oversold.

```
"closest historical analog to today's market?"
```
→ Atlas pulls macro context (Fed policy, recession risk, sector rotation), matches to past regimes. "This looks like 2018 trade war escalation."

```
"rebalance my portfolio"
```
→ Reads holdings, calculates target allocation, recommends account placement for tax efficiency.

```
"am I ready to incorporate?"
```
→ Reads revenue, checks $80K threshold, models CCPC vs sole prop tax. ROI calculation.

```
"what's my tax bill for 2025?"
```
→ Aggregates income, applies deductions, calculates liability, filing deadline.

---

## Execution-Ready Stock Pick Format

When you ask for picks (e.g., `/picks "AI plays"`), here's exactly what comes back:

```
📊 TICKER (Company Name) — Conviction 7/10 [⚠️ CONFLICT: insider selling vs growth thesis]

THESIS
3–5 sentences explaining why now. What changed? What catalyst is coming?

EXECUTION
Account: TFSA (growth → tax-free forever)
Order type: LIMIT BUY GTC (Good 'til Cancelled, 90 days)
Price: $85–90 CAD
Shares: 50 ($4,500 position)

STOP LOSS: $75 (12% downside protection)
TP1: $100 (sell 33% at +18%)
TP2: $110 (sell 33% at +29%)
TP3: $120+ (let final 34% ride, +41%)

WEALTHSIMPLE CLICKS
1. Go to TFSA account
2. Search TICKER
3. Set LIMIT order, $85, 50 shares
4. Set order to GTC
5. Click Submit
6. (Atlas never executes; you do this step)

SIGNAL STRENGTH
Fundamentals: ✓ Growth 25%+ YoY, margin expanding
Technicals:  ✓ Support at $80, above 200-SMA
Macro:       ✓ AI capex cycle heating up
Insider:     ✗ CEO sold 5% last month (weakens conviction by 1 point)
Institutional: ✓ Vanguard accumulating
Earnings:    7 days away — watch for guidance
Options:     Call volume elevated, puts cheap (bullish skew)

RISKS
- Valuation at 35x forward PE (elevated if growth slows)
- Taiwan supply chain risk
- Competitive pressure from 2 new entrants (2026 Q2)

TAX NOTE
- If you sell for gain, that goes in taxable account or non-reg (can offset other losses)
- Cost basis for ACB tracking: $87.50 avg
- Max time horizon: 18 months (conviction weakens after)
```

**Key points:**

- **Conviction** is 0–10. We reject anything < 6. No meme stocks.
- **Conflicts** are flagged. If insiders are selling but growth is booming, you know there's tension.
- **Execution** is click-by-click. CC (you) executes. Atlas never touches your money.
- **Account routing** is tax-optimized. Growth → TFSA. Dividend/qualified → RRSP.
- **Stop and targets** are specific prices, not percentages. Copy them directly into your broker.
- **Tax note** tells you what happens if you sell, when to expect tax, and account placement.

---

## Natural-Language Examples (20+ Real Scenarios)

| You Say | What Atlas Does | Output Shape |
|---------|-----------------|--------------|
| "how much runway?" | Reads cash + MRR + rent. Models 3 scenarios. | "Base case: 5 months. Best: 9 months. Worst: 3 months. Breakeven at $2,500/mo." |
| "give me 3 plays" | News scan → macro → fundamentals → technicals → research → Claude synthesis. Runs full pipeline. | 3 execution-ready picks with conviction, entry/exit, risks, catalysts. |
| "should I hold crypto through summer?" | Macro (geopolitical risk), technicals (cycle position), fundamentals (adoption curve), psychology (sentiment). | Bull case ($X), bear case ($Y), base case, 90-day outlook. |
| "what's my net worth?" | Aggregates Kraken + OANDA + Wise + RBC + Wealthsimple balances live. | Single table: assets by class, liabilities, net total, change vs last month. |
| "pull January receipts" | IMAP scans conaugh@oasisai.work, OCRs, categorizes. | "Meals: $342. Software: $89. Equipment: $0. Travel: $156. Total: $587." |
| "Fed raising rates?" | News ingest + macro watch. | "Yes, 0.25% hike announced. Impact: growth → downside, financials → upside. Sector rotation: shift out of high-multiple tech." |
| "is NVDA a buy?" | Deep dive: fundamentals, technicals, insider, 13F, options flow, earnings date. | Bull case ($110+), bear case ($60), conviction 7/10, entry $85–90. |
| "how much tax this year?" | YTD income (all sources), applies deductions, calculates bracket. | "YTD: $95K. Reserve: $22K (53.53% rate in Ontario). Next payment: June 15." |
| "what's VIX saying?" | Psychology + fear/greed index + realized vs implied vol. | "VIX at 18 — neutral. Skew bullish (puts expensive). Sentiment: cautious optimism." |
| "Fear & Greed?" | Real-time CNN Fear & Greed index + derivatives positioning. | "Current: 58/100 (Greed). Up from 45 last week. Retail accumulating. Pros taking profits." |
| "rebalance my portfolio" | Reads holdings + target allocation, suggests moves for tax efficiency. | "Move $5K from TFSA growth to FHSA. Save $1K in tax. Reduces overlap with Kraken." |
| "should I incorporate?" | Revenue check against $80K threshold, CCPC vs sole prop tax model. | "Revenue: $95K. CCPC saves $18K/year starting year 2. Cost: $2K legal. ROI: 1.3 months. Yes." |
| "what's my tax bill?" | T2125 simulation: income + deductions + credits + capital gains. | "2025 income: $94K. Deductions: $12K (home office, software, equipment). Taxable: $82K. Tax: ~$19K. File by June 15." |
| "who's buying NVIDIA?" | 13F tracking from latest SEC filings. | "Burry (Scion): 5% position, holding. Tepper (Appaloosa): bought +2% last Q. Vanguard: slowly accumulating." |
| "earnings trap on watchlist?" | Earnings calendar scan + days-to-date filter. | "NVDA earnings in 3 days. If misses, down 5–10% historical. TSLA earnings in 8 days." |
| "set up FHSA strategy" | Calculates combined FHSA + RRSP HBP withdrawal for home. | "Contribute $8K/year to FHSA (4 years = $32K tax-free growth). HBP: withdraw $35K from RRSP. Total down payment fund: $67K (10-year timeline)." |
| "track crypto ACB" | Reads all Kraken trades, calculates weighted-average cost basis. | "BTC: $45K ACB, current $52K, unrealized +$7K. If you sell now, $1.86K tax owing (53.53% on 50% inclusion)." |
| "island tax strategy?" | Reads UK passport + revenue projections. Models Isle of Man vs Ontario. | "At $120K CAD, Isle of Man saves $18K/year. Requires UK residency. Timeline: 12 months. Departure tax: ~$5K." |
| "how much software cost deductible?" | Reads expense records + tax code. | "$2,847 software this year. 100% deductible vs income (not CCA). Saves $1,522 in tax (53.53% rate)." |
| "OSAP repayment vs investing?" | Models RAP (Repayment Assistance Plan), interest tax deductibility, investment returns. | "Current income ~$95K. You qualify for RAP (0 payment). Every $1K invested at 10% compounds to $25K in 20 years. Keep OSAP as is for now." |

---

## Bot Management

### Stopping the Bot

**While running (interactive):**
- Press `Ctrl+C` in the terminal where `python telegram_bridge.py` is running
- The process stops. No more messages go through.

**To restart:**
```bash
python telegram_bridge.py
```

### Running Permanently (Daemonize)

You want the bot to survive a reboot and keep listening 24/7. Pick one:

#### Windows: Task Scheduler

1. Create a `.bat` file: `run_atlas_bot.bat`
   ```batch
   @echo off
   cd /d C:\Users\User\APPS\trading-agent
   C:\Users\User\APPS\trading-agent\.venv\Scripts\python.exe telegram_bridge.py
   pause
   ```

2. Open Task Scheduler (search "Task Scheduler")
3. Create Basic Task
   - **Name:** Atlas Telegram Bot
   - **Trigger:** "At log on"
   - **Action:** Start program → point to `run_atlas_bot.bat`
4. Save

#### macOS: launchd

Create `~/Library/LaunchAgents/com.atlas.telegram.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.atlas.telegram</string>
    <key>Program</key>
    <string>/full/path/to/venv/bin/python</string>
    <key>ProgramArguments</key>
    <array>
        <string>telegram_bridge.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/full/path/to/trading-agent</string>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/tmp/atlas_telegram.err</string>
    <key>StandardOutPath</key>
    <string>/tmp/atlas_telegram.log</string>
</dict>
</plist>
```

Then:
```bash
launchctl load ~/Library/LaunchAgents/com.atlas.telegram.plist
```

#### Linux: systemd

Create `/etc/systemd/system/atlas-telegram.service`:

```ini
[Unit]
Description=ATLAS Telegram CFO Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/trading-agent
ExecStart=/path/to/.venv/bin/python telegram_bridge.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable atlas-telegram
sudo systemctl start atlas-telegram
```

#### Any OS: pm2 (Node.js process manager)

Install: `npm install -g pm2`

```bash
pm2 start "python telegram_bridge.py" --name atlas-bot --cwd /path/to/trading-agent
pm2 startup
pm2 save
```

### Checking Logs

Logs are written to `logs/atlas_telegram.log`. Read the latest 50 lines:

```bash
tail -50 logs/atlas_telegram.log
```

Or grep for errors:

```bash
grep "ERROR\|WARN" logs/atlas_telegram.log
```

### Security: User ID Locking

Only the registered `TELEGRAM_USER_ID` can command the bot. If someone else finds your bot:

1. They can message it
2. The bot responds with "You are not authorized" and logs the attempt
3. Their message is ignored

If you want to allow a second user (spouse, partner):

1. Edit `.env` and change `TELEGRAM_USER_ID` to a list (future feature — currently single user only)
2. Or run a second instance with a different bot token and `.env`

---

## Troubleshooting

### Bot Not Responding

**Check 1: Is the process running?**
```bash
ps aux | grep telegram_bridge.py
```
If not listed, restart: `python telegram_bridge.py`

**Check 2: Is the token correct?**
Look at `.env`:
```
TELEGRAM_BOT_TOKEN=...
```
Copy the full token from BotFather and verify no trailing spaces.

**Check 3: Is your user ID registered?**
Look at `.env`:
```
TELEGRAM_USER_ID=...
```
If empty, send `/start` to the bot. It auto-registers on first contact.

**Check 4: Check logs**
```bash
tail -100 logs/atlas_telegram.log
```
Look for connection errors, API errors, or Anthropic errors.

### "ANTHROPIC_API_KEY missing"

If you haven't set `ANTHROPIC_API_KEY` in `.env`:
- Slash commands still work (they don't need Claude)
- Natural language falls back to echoing your message
- Set the key to enable full NL understanding

Get a key: `console.anthropic.com` → create account → generate API key → add to `.env`

### "Long responses are truncated"

Telegram has a 4,096 character limit per message. Atlas automatically chunks long responses:
- Pick: sent as 2–3 messages
- Deep dive: sent as 3–4 messages

This is normal. Be patient for the full read.

### "Gmail receipts not syncing"

1. Check `.env` has `GMAIL_APP_PASSWORD` (not your normal Gmail password)
2. Verify IMAP is enabled: Gmail Settings → Forwarding and POP/IMAP → enable IMAP
3. App password needs spaces stripped: `xxxx xxxx xxxx xxxx` → `xxxxyyyyzzzzwwww`

---

## Privacy & Security

- **Self-hosted:** The bot runs on your machine (or your VPS). Nothing is sent to a central server.
- **`.env` stays local:** Your API keys, passwords, bot token are never committed to version control. `.env` is in `.gitignore`.
- **Data sent:** Only to Anthropic Claude (for reasoning), your chosen brokers (read-only balance calls), and Gmail (receipt scanning).
- **No ad tracking, no analytics, no third-party data brokers.**

---

## What's Next: Roadmap

- **Voice messages** → Speech-to-text (planned Q2 2026)
- **Multi-user mode** → Support spouse/partner with role-based access (planned Q2 2026)
- **Automated weekly check-ins** → Atlas proactively alerts you on runway drops, tax deadlines, earnings (planned Q3 2026)
- **Mobile app** → Lightweight React Native app for net-worth / runway / alerts (planned 2027)
- **Crypto wallet scanner** → Auto-detect cold wallets and add to ACB (planned Q2 2026)

---

## Quick Reference Card

Print this and stick it on your fridge (or phone background):

| Task | Command | Example |
|------|---------|---------|
| Net worth | `/networth` | — |
| Runway | `/runway` | — |
| Status pulse | `/status` | — |
| Quarterly tax | `/taxes` | — |
| Receipts | `/receipts YYYY-MM-DD` | `/receipts 2026-01-01` |
| Stock picks | `/picks <query>` | `/picks "AI infrastructure 6mo"` |
| Deep dive | `/deepdive TICK` | `/deepdive NVDA` |
| News | `/news <topic>` | `/news Fed policy` |
| Geopolitics | `/macro` | — |
| Brain docs | `/brain <file>` | `/brain USER` |
| **Anything else** | **Just type** | "am I making it?" |

---

**Last Updated:** 2026-04-14  
**Maintainer:** CC McKenna, OASIS AI Solutions  
**Status:** Production-ready Telegram interface
