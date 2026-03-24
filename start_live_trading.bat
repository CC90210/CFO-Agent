@echo off
title Atlas Live Trading
cd /d %~dp0
set PYTHONUTF8=1
python -u live_trade.py
pause
