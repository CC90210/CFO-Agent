@echo off
:: ATLAS Paper Trading — Persistent Launcher
:: Double-click this to start paper trading in a separate window.
:: The process runs independently of any terminal/IDE session.
:: Logs go to logs/paper_trade.log (file handler in paper_trade.py)
:: and stdout goes to logs/paper_trade_live.log
::
:: To stop: close the window or press Ctrl+C in it.

title ATLAS Paper Trading
cd /d "%~dp0"

echo ============================================
echo   ATLAS Paper Trading — Starting...
echo   Log: logs/paper_trade_live.log
echo   Close this window to stop.
echo ============================================

:: Create logs dir if missing
if not exist logs mkdir logs

:: Run with stdout/stderr captured
python paper_trade.py >> logs/paper_trade_live.log 2>&1

echo.
echo Paper trading exited. Press any key to close.
pause >nul
