"""Quick market scan — check position P&L and opportunities."""
import ccxt, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

k = ccxt.kraken({
    'apiKey': os.getenv('EXCHANGE_API_KEY'),
    'secret': os.getenv('EXCHANGE_SECRET'),
})

doge = k.fetch_ticker('DOGE/USD')
ada = k.fetch_ticker('ADA/USD')

doge_pnl = (doge['last'] - 0.0961) * 13
ada_pnl = (ada['last'] - 0.269132) * 15

print("=== LIVE POSITION STATUS ===")
print(f"DOGE/USD: {doge['last']:.5f} | entry 0.09610 | PnL ${doge_pnl:.4f} ({(doge['last']/0.0961 - 1)*100:+.2f}%)")
print(f"  SL: 0.09500 ({(0.09500/doge['last'] - 1)*100:+.2f}%) | TP: 0.09660 ({(0.09660/doge['last'] - 1)*100:+.2f}%)")
print(f"ADA/USD:  {ada['last']:.6f} | entry 0.269132 | PnL ${ada_pnl:.4f} ({(ada['last']/0.269132 - 1)*100:+.2f}%)")
print(f"  SL: 0.265939 ({(0.265939/ada['last'] - 1)*100:+.2f}%) | TP: 0.270817 ({(0.270817/ada['last'] - 1)*100:+.2f}%)")
print(f"\nCombined unrealised PnL: ${doge_pnl + ada_pnl:.4f}")

print("\n=== MARKET SCAN ===")
syms = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD', 'AVAX/USD', 'DOT/USD', 'ATOM/USD', 'LINK/USD', 'LTC/USD']
for sym in syms:
    t = k.fetch_ticker(sym)
    chg = t.get('percentage', 0) or 0
    print(f"{sym:10s}: ${t['last']:>10.4f} | 24h {chg:+.1f}% | vol ${t.get('quoteVolume', 0):,.0f}")
