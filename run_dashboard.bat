@echo off
setlocal
cd /d "%~dp0"
set "PORT=%SGPOOLS_DASHBOARD_PORT%"
if "%PORT%"=="" set "PORT=8765"

if not "%SGPOOLS_ENV_FILE%"=="" (
  ".venv\Scripts\python.exe" -m sgpools_trend.dashboard --env-file "%SGPOOLS_ENV_FILE%" --port %PORT%
) else (
  ".venv\Scripts\python.exe" -m sgpools_trend.dashboard --port %PORT%
)
