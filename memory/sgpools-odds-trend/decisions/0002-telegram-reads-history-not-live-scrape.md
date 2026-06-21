---
type: Decision
title: Telegram Bot Reads Stored Odds History
description: Answer odds-change questions from persisted snapshots instead of scraping per message.
tags: [telegram, odds, sqlite, trend, decision]
status: accepted
date: 2026-06-21
---

# Decision

The Telegram bot should query the local odds-history database and should not trigger a fresh Singapore Pools scrape for every user message.

# Rationale

- Trend questions require historical data, not just current odds.
- Database reads are faster and more reliable than live page loads.
- Decoupling scraping from bot replies keeps the bot responsive even if the source page is slow or temporarily unavailable.
- A scheduled scraper can enforce conservative polling independent of chat volume.

# Initial commands

- `/odds <match>` shows the latest stored odds.
- `/change <match>` compares latest odds with the previous or opening snapshot.
- `/trend <match>` returns a compact trend summary and later a chart image.

# Consequences

- Bot replies must include the last captured timestamp.
- If the scraper has not collected enough history, the bot should say that trend data is not available yet.
