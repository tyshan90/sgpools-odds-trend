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

# Observed sample odds

| Match | Home | Draw | Away |
|---|---:|---:|---:|
| Spain vs Saudi Arabia | 1.05 | 8.00 | 15.00 |
| Belgium vs Iran | 1.28 | 4.40 | 8.00 |
| Uruguay vs Cape Verde | 1.42 | 3.80 | 5.80 |

# Near-term plan

1. Set `TELEGRAM_BOT_TOKEN` from BotFather.
2. Run `run_scraper_loop.bat` in one terminal to collect snapshots every 10 minutes.
3. Run `run_bot.bat` in another terminal to answer `/odds` and `/change`.
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
- Whether polling every 10 to 15 minutes is enough for the intended personal use.
- Whether Linkup has a useful role later for discovery/docs; current odds collection still requires Playwright because Singapore Pools loads odds dynamically.
