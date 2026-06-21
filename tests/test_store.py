import unittest

from sgpools_trend.models import OddsRow
from sgpools_trend.store import OddsStore


def make_row(captured_at, odds):
    return OddsRow(
        captured_at=captured_at,
        event_id="140085",
        event_code="5895",
        event_name="Spain vs Saudi Arabia",
        start_time="2026-06-21T16:00:00Z",
        competition="W Cup",
        category="Football",
        market_id="2201373",
        market_name="1X2",
        bet_type_code="MR",
        outcome_id="10772574",
        selection_code="H",
        selection_name="Spain",
        decimal_odds=odds,
        source_url="sample",
    )


def make_selection(captured_at, selection_code, selection_name, outcome_id, odds):
    row = make_row(captured_at, odds)
    return OddsRow(
        captured_at=row.captured_at,
        event_id=row.event_id,
        event_code=row.event_code,
        event_name=row.event_name,
        start_time=row.start_time,
        competition=row.competition,
        category=row.category,
        market_id=row.market_id,
        market_name=row.market_name,
        bet_type_code=row.bet_type_code,
        outcome_id=outcome_id,
        selection_code=selection_code,
        selection_name=selection_name,
        decimal_odds=odds,
        source_url=row.source_url,
    )


class StoreTests(unittest.TestCase):
    def test_store_inserts_and_lists_latest_match_rows(self):
        with self.subTest("latest match rows"):
            from tempfile import TemporaryDirectory

            with TemporaryDirectory() as tmp_dir:
                store = OddsStore(f"{tmp_dir}/odds.sqlite")
                store.insert_rows([make_row("2026-06-21T08:10:00Z", 1.05)])
                store.insert_rows([make_row("2026-06-21T08:20:00Z", 1.08)])

                rows = store.latest_for_match("spain saudi")

                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0].captured_at, "2026-06-21T08:20:00Z")
                self.assertEqual(rows[0].decimal_odds, 1.08)

    def test_store_orders_1x2_home_draw_away(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmp_dir:
            store = OddsStore(f"{tmp_dir}/odds.sqlite")
            store.insert_rows(
                [
                    make_selection("2026-06-21T08:10:00Z", "A", "Saudi Arabia", "away", 15.0),
                    make_selection("2026-06-21T08:10:00Z", "D", "Draw", "draw", 8.0),
                    make_selection("2026-06-21T08:10:00Z", "H", "Spain", "home", 1.05),
                ]
            )

            rows = store.latest_for_match("spain saudi")

            self.assertEqual([row.selection_name for row in rows], ["Spain", "Draw", "Saudi Arabia"])

    def test_store_calculates_latest_change_against_previous_snapshot(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmp_dir:
            store = OddsStore(f"{tmp_dir}/odds.sqlite")
            store.insert_rows([make_row("2026-06-21T08:10:00Z", 1.05)])
            store.insert_rows([make_row("2026-06-21T08:20:00Z", 1.08)])

            changes = store.change_for_match("spain saudi")

            self.assertEqual(len(changes), 1)
            self.assertEqual(changes[0].selection_name, "Spain")
            self.assertEqual(changes[0].previous_odds, 1.05)
            self.assertEqual(changes[0].latest_odds, 1.08)
            self.assertEqual(changes[0].absolute_change, 0.03)

    def test_store_lists_match_summaries_for_dashboard(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmp_dir:
            store = OddsStore(f"{tmp_dir}/odds.sqlite")
            store.insert_rows(
                [
                    make_selection("2026-06-21T08:10:00Z", "H", "Spain", "home", 1.05),
                    make_selection("2026-06-21T08:20:00Z", "H", "Spain", "home", 1.08),
                ]
            )

            matches = store.list_matches()

            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0]["event_id"], "140085")
            self.assertEqual(matches[0]["event_name"], "Spain vs Saudi Arabia")
            self.assertEqual(matches[0]["snapshot_count"], 2)
            self.assertEqual(matches[0]["latest_captured_at"], "2026-06-21T08:20:00Z")

    def test_store_returns_trend_series_for_match(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmp_dir:
            store = OddsStore(f"{tmp_dir}/odds.sqlite")
            store.insert_rows(
                [
                    make_selection("2026-06-21T08:10:00Z", "H", "Spain", "home", 1.05),
                    make_selection("2026-06-21T08:10:00Z", "D", "Draw", "draw", 8.0),
                    make_selection("2026-06-21T08:20:00Z", "H", "Spain", "home", 1.08),
                    make_selection("2026-06-21T08:20:00Z", "D", "Draw", "draw", 8.5),
                ]
            )

            trend = store.trend_for_event("140085", market_name="1X2")

            self.assertEqual(trend["event_name"], "Spain vs Saudi Arabia")
            self.assertEqual(trend["market_name"], "1X2")
            self.assertEqual([series["selection_name"] for series in trend["series"]], ["Spain", "Draw"])
            self.assertEqual(trend["series"][0]["points"][1]["decimal_odds"], 1.08)


if __name__ == "__main__":
    unittest.main()
