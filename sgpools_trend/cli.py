from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from .formatting import format_changes, format_latest
from .parser import parse_upcoming_football
from .scraper import SPORTS_URL, now_utc, scrape_upcoming_football_sync
from .store import OddsStore

DEFAULT_DB = Path(".runtime") / "odds.sqlite"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    store = OddsStore(args.db)

    if args.command == "import-file":
        payload = json.loads(Path(args.path).read_text(encoding="utf-8"))
        captured_at = args.captured_at or now_utc()
        rows = parse_upcoming_football(payload, captured_at=captured_at, source_url=str(args.path))
        inserted = store.insert_rows(rows)
        print(f"Imported {inserted} new odds rows into {args.db}")
        return 0

    if args.command == "scrape":
        try:
            rows = scrape_upcoming_football_sync(headless=not args.headful, timeout_ms=args.timeout_ms)
        except RuntimeError as exc:
            print(exc)
            return 1
        inserted = store.insert_rows(rows)
        print(f"Scraped {len(rows)} odds rows from {SPORTS_URL}")
        print(f"Inserted {inserted} new rows into {args.db}")
        return 0

    if args.command == "scrape-loop":
        interval_seconds = args.interval_minutes * 60
        print(f"Starting scraper loop. Interval: {args.interval_minutes} minutes. DB: {args.db}")
        while True:
            try:
                rows = scrape_upcoming_football_sync(headless=not args.headful, timeout_ms=args.timeout_ms)
                inserted = store.insert_rows(rows)
                print(f"{now_utc()} scraped={len(rows)} inserted={inserted}")
            except KeyboardInterrupt:
                print("Stopping scraper loop.")
                return 0
            except Exception as exc:
                print(f"{now_utc()} scrape failed: {exc}")
            time.sleep(interval_seconds)

    if args.command == "latest":
        rows = store.latest_for_match(args.match, market_name=args.market)
        print(format_latest(rows))
        return 0

    if args.command == "change":
        changes = store.change_for_match(args.match, market_name=args.market)
        print(format_changes(changes))
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Personal Singapore Pools football odds trend tracker")
    parser.add_argument("--db", default=DEFAULT_DB, type=Path, help=f"SQLite database path. Default: {DEFAULT_DB}")

    subparsers = parser.add_subparsers(dest="command", required=True)

    import_file = subparsers.add_parser("import-file", help="Import a saved Singapore Pools JSON response")
    import_file.add_argument("path", type=Path)
    import_file.add_argument("--captured-at", help="Override capture timestamp, e.g. 2026-06-21T08:10:00Z")

    scrape = subparsers.add_parser("scrape", help="Open the public sports page and capture current odds")
    scrape.add_argument("--headful", action="store_true", help="Show the browser while scraping")
    scrape.add_argument("--timeout-ms", type=int, default=45000)

    scrape_loop = subparsers.add_parser("scrape-loop", help="Continuously scrape odds at a fixed interval")
    scrape_loop.add_argument("--interval-minutes", type=int, default=10)
    scrape_loop.add_argument("--headful", action="store_true", help="Show the browser while scraping")
    scrape_loop.add_argument("--timeout-ms", type=int, default=45000)

    latest = subparsers.add_parser("latest", help="Show latest stored odds for a match")
    latest.add_argument("match", help='Match search terms, e.g. "spain saudi"')
    latest.add_argument("--market", default="1X2")

    change = subparsers.add_parser("change", help="Show latest odds movement for a match")
    change.add_argument("match", help='Match search terms, e.g. "spain saudi"')
    change.add_argument("--market", default="1X2")

    return parser


if __name__ == "__main__":
    raise SystemExit(main())
