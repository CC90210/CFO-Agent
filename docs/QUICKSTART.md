# ATLAS Quick Start — 15 Minutes

Get Atlas running and making your first decisions in 15 minutes.

---

## 1. Clone & Install (3 min)

```bash
git clone https://github.com/oasisai/atlas.git
cd atlas
pip install -r requirements.txt
```

---

## 2. Configure (2 min)

```bash
cp .env.example .env
```

Open `.env` and fill in **at minimum**:

```
ANTHROPIC_API_KEY=sk-...       # Get from console.anthropic.com (free $5/month)
```

Optional, add-as-you-go:

```
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx

EXCHANGE_API_KEY=...
EXCHANGE_SECRET=...

OANDA_TOKEN=...
OANDA_ACCOUNT_ID=...

TELEGRAM_BOT_TOKEN=...
```

Leave blanks blank for now. You can add them later.

---

## 3. Personalize (5 min)

Edit `brain/USER.md`. Replace placeholder values with your actual info:

- **Name, age, location**
- **Income sources** (Stripe, Wise, salary, freelance, crypto)
- **Accounts** (bank, brokers, registered accounts)
- **Assets & debts** (cash, crypto, real estate, student loans)
- **Tax situation** (last return filed, estimated 2026 income)
- **Goals** (FIRE? first home? tax optimization? incorporation?)

Don't overthink it. Rough estimates are fine. You can edit this anytime.

---

## 4. First Command (3 min)

```bash
python main.py networth
```

You should see a table:

```
Account          Balance        Asset Type
──────────────────────────────────────────
Wealthsimple TFSA    $155      CAD Cash
Wealthsimple RRSP    $0        CAD Cash
Wealthsimple Crypto  $206      BTC
Kraken              $133 USD   Crypto (4 positions)
Wise USD           $1,900 USD   USD Cash
RBC Chequing       $6,419      CAD Cash
──────────────────────────────────────────
TOTAL NET WORTH:   ~$12,813    (CAD equivalent)
```

If you see errors about missing API keys, that's fine. It skips those accounts and moves on.

---

## 5. Try Three More Commands (2 min)

### Runway (are you going to make it?)
```bash
python main.py runway
```

Output: "You have 4–7 months of cash runway. Breakeven at $2,500/mo. Diversify income within 90 days to reduce risk."

### Tax Estimate (quarterly check-in)
```bash
python main.py taxes
```

Output: "2026 YTD income: $X. Reserve for taxes: $Y. Estimated owing: $Z."

### Stock Pick (on-demand research)
```bash
python main.py picks "AI infrastructure for 6 months"
```

Output: 3 stock picks with entry/exit, conviction scores, catalysts, risks.

---

## 6. Optional: Set Up Telegram (2 min)

Send `/start` to `@BotFather` on Telegram, create a bot, save token to `.env`.

Then run:

```bash
python telegram_bridge.py
```

(In another terminal, or background process.)

Now in Telegram, try:

```
/networth
/runway
/pick "AI plays"
/tax
```

---

## Now What?

| Goal | Command |
|------|---------|
| **Monthly check-in** | `python main.py networth` then `python main.py runway` |
| **Quarterly tax planning** | `python main.py taxes` then `python main.py crypto-acb` |
| **Get stock ideas** | `python main.py picks "your theme"` or `/pick` on Telegram |
| **Deep dive on a stock** | `python main.py deepdive NVDA` |
| **Pull receipts for taxes** | `python main.py receipts --since 2026-01-01` |
| **Check if you should incorporate** | `python main.py taxes --detailed` (look for $80K+ income) |

---

## Common Issues

**"ModuleNotFoundError: No module named 'cfo'"**  
→ Run `pip install -r requirements.txt` again. Make sure you're in the `atlas/` directory.

**"ANTHROPIC_API_KEY not set"**  
→ Create `.env` file with `ANTHROPIC_API_KEY=sk-...` from console.anthropic.com.

**"Kraken API error: Invalid nonce"**  
→ Your system clock is out of sync. Run `ntpdate -s time.nist.gov` (Linux/Mac) or check Settings > Time on Windows.

**"Can't find Gmail"**  
→ `GMAIL_USER` and `GMAIL_APP_PASSWORD` not set. Leave blank for now. Add later via `.env`.

---

## Next: Read the Full Guide

Once you're comfortable with these 5 commands, read `ATLAS_USER_GUIDE.md` for:

- All 20+ CLI commands
- Telegram bot full reference (16 commands)
- How to set up receipt scanning
- Tax strategy deep dives
- Stock research methodology
- Incorporating as a business

---

**You're done. Atlas is live.**

Next: `python main.py networth` and tell Atlas what you're working on.
