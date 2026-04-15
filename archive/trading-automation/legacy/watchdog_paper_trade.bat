@echo off
:: ATLAS Paper Trading Watchdog
:: Automatically restarts paper_trade.py if it exits.
:: Double-click to start. Runs independently of IDE/terminal sessions.
:: To stop permanently: close this window.

title ATLAS Watchdog
cd /d "%~dp0"

if not exist logs mkdir logs

:loop
echo [%date% %time%] Starting ATLAS paper trading... >> logs/watchdog.log
echo [%date% %time%] Starting ATLAS paper trading...

python paper_trade.py >> logs/paper_trade_live.log 2>&1

echo [%date% %time%] Paper trading exited! Restarting in 30 seconds... >> logs/watchdog.log
echo [%date% %time%] Paper trading exited! Restarting in 30 seconds...
timeout /t 30 /nobreak
goto loop
