@echo off
setlocal
cd /d "%~dp0"
".venv\Scripts\python.exe" -m sgpools_trend.cli scrape-loop --interval-minutes 60
