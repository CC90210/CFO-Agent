import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os
from dotenv import load_dotenv
load_dotenv()

kraken_key = os.getenv('KRAKEN_API_KEY', '')
kraken_secret = os.getenv('KRAKEN_SECRET', '') or os.getenv('KRAKEN_API_SECRET', '')

print('=' * 60)
print('  KRAKEN API KEY CHECK')
print('=' * 60)
print()

if not kraken_key:
    print('  WARNING: No KRAKEN_API_KEY found in .env')
    print('  Checking for alternative key names...')
    # Check all env vars for kraken-related keys
    for k, v in os.environ.items():
        if 'KRAKEN' in k.upper():
            masked = v[:4] + '...' + v[-4:] if len(v) > 8 else '***'
            print(f'    Found: {k} = {masked}')
else:
    masked_key = kraken_key[:4] + '...' + kraken_key[-4:] if len(kraken_key) > 8 else '***'
    masked_secret = kraken_secret[:4] + '...' + kraken_secret[-4:] if len(kraken_secret) > 8 else '***'
    print(f'  API Key: {masked_key}')
    print(f'  Secret:  {masked_secret}')
    print()

    # Try to connect and read balance
    import ccxt
    try:
        kraken = ccxt.kraken({
            'apiKey': kraken_key,
            'secret': kraken_secret,
            'enableRateLimit': True,
        })

        # Test: fetch balance
        balance = kraken.fetch_balance()
        print('  CONNECTION: SUCCESS')
        print()
        print('  ACCOUNT BALANCE:')
        total = balance.get('total', {})
        for asset, amount in sorted(total.items()):
            if amount and float(amount) > 0:
                print(f'    {asset:8s}: {float(amount):>12.6f}')

        # Check USD equivalent
        usdt_bal = float(total.get('USDT', 0))
        usd_bal = float(total.get('USD', 0))
        print()
        print(f'  Available for trading: ${usdt_bal + usd_bal:.2f} (USDT + USD)')

        # Check if we can place orders (permissions test)
        print()
        print('  PERMISSION CHECK:')
        print('    Read balance: OK')

        # Try fetching open orders (tests trade read permission)
        try:
            orders = kraken.fetch_open_orders()
            print(f'    Read orders: OK ({len(orders)} open orders)')
        except Exception as e:
            print(f'    Read orders: FAILED — {e}')

    except ccxt.AuthenticationError as e:
        print(f'  CONNECTION: AUTHENTICATION FAILED')
        print(f'  Error: {e}')
        print()
        print('  This means the API key/secret is invalid or lacks permissions.')

    except Exception as e:
        print(f'  CONNECTION: FAILED')
        print(f'  Error: {e}')

print()
print('=' * 60)
