# Memory Update Log

## 2026-06-21

* **goalsbot env compatibility**: Added `--env-file` support, accepted both `LINKUP_API_KEY` and lowercase `linkup`, documented use of `C:\Code\goalsbot\.env`, updated `run_bot.bat` to honor `SGPOOLS_ENV_FILE`, and verified 10 passing tests plus a CLI env-file smoke check.
* **Local MVP build**: Added the tested Python package `sgpools_trend` with response parsing, SQLite persistence, CLI import/scrape/latest/change commands, Playwright live scraping, Telegram bot scaffold, README, requirements, `.env.example`, and Windows helper scripts.
* **Verification**: Created `.venv`, installed dependencies, installed Playwright Chromium, verified `run_tests.bat` with 7 passing tests, ran one live scrape from the public Singapore Pools sports page, inserted 72 rows, and confirmed `change "spain saudi"` reported Draw `8.00 -> 8.50` and Saudi Arabia `15.00 -> 19.00`.
* **Initialization**: Created the Singapore Pools odds trend OKF memory bundle based on the Open Knowledge Format v0.1 convention from `C:\Code\xhs-ads\ref\knowledge-catalog-main`.
* **Source verification**: Recorded that the rendered Singapore Pools sports page showed public football `1X2` odds again, while the raw static HTML did not contain odds.
* **Endpoint observation**: Recorded the observed internal upcoming-football JSON response shape and the decision to treat it as private and unstable.
* **MVP direction**: Recorded the personal-use MVP plan: Playwright snapshots, SQLite storage, and Telegram bot queries from stored history.
