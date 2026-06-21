---
type: Decision
title: Start with a Personal Public-Odds Tracker
description: Keep the first version local, conservative, and limited to publicly visible odds.
tags: [sgpools, odds, scraper, mvp, decision]
status: accepted
date: 2026-06-21
---

# Decision

Build the first version as a personal-use tracker that captures publicly visible Singapore Pools football odds snapshots and stores them locally.

# Rationale

- Personal use reduces infrastructure cost and operational complexity.
- Trend answers require historical snapshots, so local collection should start before building a larger platform.
- The page can be loaded by an automated browser for each snapshot; it does not need to stay visibly open.
- A local SQLite database is enough for early trend queries and Telegram replies.

# Guardrails

- Do not implement login, account access, betting actions, CAPTCHA bypass, or session-token reuse.
- Use conservative polling, initially every 60 minutes by default.
- Treat internal endpoints as unstable and private implementation details.
- Keep collected data limited to odds and event metadata needed for trend analysis.

# Consequences

- The first trend lines begin only after the tracker starts collecting snapshots.
- Maintenance may be needed if Singapore Pools changes its page, preauth flow, or response shape.
- Other bet types can be added incrementally after `1X2` is stable.
