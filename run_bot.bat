@echo off
setlocal
cd /d "%~dp0"
if not "%SGPOOLS_ENV_FILE%"=="" (
  ".venv\Scripts\python.exe" -m sgpools_trend.bot --env-file "%SGPOOLS_ENV_FILE%"
) else (
  ".venv\Scripts\python.exe" -m sgpools_trend.bot
)
