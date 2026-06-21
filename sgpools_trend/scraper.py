from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from .parser import parse_upcoming_football

SPORTS_URL = "https://online.singaporepools.com/en/sports"
UPCOMING_FOOTBALL_PATH = "/mfp/api/adapters/spplMfpApi/event/upcoming/football"


async def scrape_upcoming_football(headless: bool = True, timeout_ms: int = 45000):
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright is not installed. Run: python -m pip install -r requirements.txt "
            "then python -m playwright install chromium"
        ) from exc

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=headless)
        page = await browser.new_page()
        try:
            async with page.expect_response(_is_upcoming_football_response, timeout=timeout_ms) as response_info:
                await page.goto(SPORTS_URL, wait_until="domcontentloaded", timeout=timeout_ms)
            response = await response_info.value
            payload: dict[str, Any] = await response.json()
        finally:
            await browser.close()

    captured_at = now_utc()
    return parse_upcoming_football(payload, captured_at=captured_at, source_url=SPORTS_URL)


def scrape_upcoming_football_sync(headless: bool = True, timeout_ms: int = 45000):
    return asyncio.run(scrape_upcoming_football(headless=headless, timeout_ms=timeout_ms))


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _is_upcoming_football_response(response) -> bool:
    return UPCOMING_FOOTBALL_PATH in response.url and response.status == 200

