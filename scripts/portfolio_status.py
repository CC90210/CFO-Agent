"""Quick portfolio status check — reads live positions from open_positions.json."""
import json, ccxt, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

k = ccxt.kraken({
    'apiKey': os.getenv('EXCHANGE_API_KEY'),
    'secret': os.getenv('EXCHANGE_SECRET'),
})

# Load live positions from engine state
pos_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'open_positions.json')
with open(pos_file) as f:
    raw = json.load(f)

positions = {}
for sym, p in raw.items():
    positions[sym] = {
        'entry': p['entry_price'],
        'size': p['size'],
        'sl': p['stop_loss'],
        'tp': p['take_profit'],
        'strategy': p.get('strategy_name', '?'),
        'opened': p.get('opened_at', '?'),
    }

print('=== PORTFOLIO STATUS ===')
total_unrealised = 0
total_value = 0
for sym, p in positions.items():
    t = k.fetch_ticker(sym)
    price = t['last']
    pnl = (price - p['entry']) * p['size']
    pnl_pct = (price / p['entry'] - 1) * 100
    risk = abs(p['entry'] - p['sl']) * p['size']
    reward = abs(p['tp'] - p['entry']) * p['size']
    rr = reward / risk if risk > 0 else 0
    dist_sl = (price - p['sl']) / price * 100
    dist_tp = (p['tp'] - price) / price * 100
    total_unrealised += pnl
    total_value += price * p['size']
    print(f"{sym}: {price:.5f} | PnL ${pnl:+.4f} ({pnl_pct:+.2f}%) | R:R 1:{rr:.1f} | SL {dist_sl:.2f}% TP {dist_tp:.2f}% | {p['strategy']}")

# Fetch account balances from Kraken
balance = k.fetch_balance()
usd_free = balance.get('USD', {}).get('free', 0) or 0
btc_total = balance.get('BTC', {}).get('total', 0) or 0
btc_price = k.fetch_ticker('BTC/USD')['last']
btc_value = btc_total * btc_price

# Non-trade DOGE (total DOGE minus what's in positions)
doge_total = balance.get('DOGE', {}).get('total', 0) or 0
doge_in_trade = positions.get('DOGE/USD', {}).get('size', 0)
doge_extra = max(0, doge_total - doge_in_trade)
doge_price = k.fetch_ticker('DOGE/USD')['last']
doge_value = doge_extra * doge_price

print(f"\nUnrealised PnL: ${total_unrealised:+.4f}")
print(f"Position value: ${total_value:.2f}")
print(f"USD cash: ${usd_free:.2f}")
print(f"BTC hold: ${btc_value:.2f} ({btc_total:.6f} BTC)")
if doge_extra > 0:
    print(f"DOGE hold: ${doge_value:.2f} ({doge_extra:.2f} non-trade)")
print(f"Estimated total: ${usd_free + btc_value + doge_value + total_value:.2f}")
