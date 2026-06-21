---
type: Working Notes
title: Singapore Pools Odds Trend Working Notes
description: Current state and implementation notes for the personal odds tracker.
tags: [sgpools, odds, scraper, telegram, working-notes]
timestamp: 2026-06-21T08:30:00Z
---

# Current state

- A rendered browser check on 2026-06-21 confirmed that football odds are visible on `https://online.singaporepools.com/en/sports`.
- The observed `Upcoming Football` tab used a `Bet Type` selector and displayed `1X2` odds.
- A saved response file exists at `C:\Code\SGpools trend\upcoming-football-response.network-response`.
- That response file is useful for inspecting the JSON shape, but future code should fetch fresh data through the public page flow instead of depending on a saved snapshot.
- A local Python MVP has been implemented under `sgpools_trend/`.
- A local venv exists at `.venv/` with Playwright and `python-telegram-bot` installed.
- Playwright Chromium has been installed for live scraping.
- The live scraper was verified on 2026-06-21 and inserted 72 current odds rows into `.runtime\odds.sqlite`.
- Unit tests pass through `run_tests.bat`.
- `C:\Code\goalsbot\.env` was inspected only for variable names and can now be passed with `--env-file`; secret values were not copied into this repository.
- CLI env-file smoke check succeeded with `latest "spain saudi"`.
- Bot env-file smoke check loaded the token but could not reach Telegram from the sandbox; the app now reports a concise `NetworkError`.
- `start.bat` and `stop.bat` were added and verified. Scraper-only lifecycle started PID `26248` and stopped it. Env-file lifecycle started scraper PID `14140` and bot PID `3116`, then stopped both.
- Dashboard was added and verified in Chrome at `http://127.0.0.1:8765`. Browser network requests returned `/`, `/app.css`, `/app.js`, `/api/matches`, `/api/trend`, and `/favicon.ico` successfully, with no console messages.
- The dashboard verification screenshot was written to `.runtime\dashboard-verify.png`.

# Observed sample odds

| Match | Home | Draw | Away |
|---|---:|---:|---:|
| Spain vs Saudi Arabia | 1.05 | 8.00 | 15.00 |
| Belgium vs Iran | 1.28 | 4.40 | 8.00 |
| Uruguay vs Cape Verde | 1.42 | 3.80 | 5.80 |

# Near-term plan

1. Set `TELEGRAM_BOT_TOKEN` from BotFather.
2. Set `SGPOOLS_ENV_FILE=C:\Code\goalsbot\.env` if reusing the existing env file.
3. Run `start.bat` to collect snapshots, run the dashboard, and run the Telegram bot in the background.
4. Run `stop.bat` to stop the background processes.
4. Add more bet type mappings after `1X2` has collected enough history.
5. Add chart image output after text replies are reliable.

# Bet type mapping notes

- Confirmed mapping: `MR` appears to map to `1X2`.
- Unknown mappings should be discovered by changing the Bet Type dropdown and observing the request URL and response body.
- Store both `market_name` and `bet_type_code` to keep history readable if codes change later.

# Open questions

- Whether the internal response includes all desired bet types or only the selected market.
- Whether opening odds are exposed in a separate page/endpoint or need to be approximated by the first collected snapshot.
- Whether live odds use the same response shape or a separate live/event stream.
- Whether hourly polling is enough for the intended personal use.
- Whether Linkup has a useful role later for discovery/docs; current odds collection still requires Playwright because Singapore Pools loads odds dynamically.
- Whether the dashboard should add other bet types after mapping their Singapore Pools market codes.
