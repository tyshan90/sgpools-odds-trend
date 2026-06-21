# Singapore Pools Odds Trend Tracker

Personal-use tracker for publicly visible Singapore Pools football odds.

The first version stores odds snapshots in SQLite and answers trend questions
from stored history. It does not log in, place bets, bypass CAPTCHA, or store
browser tokens.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install chromium
```

For Telegram, create a bot with BotFather and set:

```powershell
$env:TELEGRAM_BOT_TOKEN="your-token"
```

You can also reuse an existing env file, for example:

```powershell
python -m sgpools_trend.bot --env-file C:\Code\goalsbot\.env
python -m sgpools_trend.cli --env-file C:\Code\goalsbot\.env latest "spain saudi"
```

The config loader accepts both `LINKUP_API_KEY` and the lowercase `linkup`
alias used by `goalsbot`. The current odds scraper still uses Playwright
because Singapore Pools loads odds through a browser-side flow.

## Local Smoke Test

Import the saved sample response:

```powershell
python -m sgpools_trend.cli import-file upcoming-football-response.network-response --captured-at 2026-06-21T08:10:00Z
```

Query latest odds:

```powershell
python -m sgpools_trend.cli latest "spain saudi"
```

Query odds changes after at least two snapshots exist:

```powershell
python -m sgpools_trend.cli change "spain saudi"
```

## Live Collection

Run one live scrape:

```powershell
python -m sgpools_trend.cli scrape
```

Run continuously every 10 minutes:

```powershell
python -m sgpools_trend.cli scrape-loop --interval-minutes 10
```

Or double-click/run:

```powershell
.\run_scraper_loop.bat
```

Run only the dashboard:

```powershell
.\run_dashboard.bat
```

Open:

```text
http://127.0.0.1:8765
```

Or start the scraper loop, dashboard, and Telegram bot as background processes:

```powershell
$env:SGPOOLS_ENV_FILE="C:\Code\goalsbot\.env"
.\start.bat
```

The default snapshot interval is 10 minutes. Override it with:

```powershell
$env:SGPOOLS_SCRAPE_INTERVAL_MINUTES="5"
```

The default dashboard port is `8765`. Override it with:

```powershell
$env:SGPOOLS_DASHBOARD_PORT="8770"
```

Stop background processes:

```powershell
.\stop.bat
```

## Telegram Bot

Run the bot in a separate terminal while the scraper loop is collecting data:

```powershell
python -m sgpools_trend.bot
```

With the existing `goalsbot` env file:

```powershell
python -m sgpools_trend.bot --env-file C:\Code\goalsbot\.env
```

Or with the batch file:

```powershell
$env:SGPOOLS_ENV_FILE="C:\Code\goalsbot\.env"
.\run_bot.bat
```

Or double-click/run:

```powershell
.\run_bot.bat
```

Bot commands:

```text
/odds spain saudi
/change spain saudi
```

## Tests

```powershell
python -m unittest discover -s tests -v
```

Or:

```powershell
.\run_tests.bat
```
