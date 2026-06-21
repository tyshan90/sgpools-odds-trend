import json
import unittest
from pathlib import Path

from sgpools_trend.parser import parse_upcoming_football


def load_sample():
    sample_path = Path(__file__).resolve().parents[1] / "upcoming-football-response.network-response"
    return json.loads(sample_path.read_text(encoding="utf-8"))


class ParserTests(unittest.TestCase):
    def test_parse_upcoming_football_flattens_1x2_outcomes(self):
        rows = parse_upcoming_football(load_sample(), captured_at="2026-06-21T08:10:00Z", source_url="sample")

        spain_rows = [row for row in rows if row.event_name == "Spain vs Saudi Arabia"]

        self.assertEqual(len(spain_rows), 3)
        self.assertEqual([row.selection_name for row in spain_rows], ["Spain", "Draw", "Saudi Arabia"])
        self.assertEqual([row.selection_code for row in spain_rows], ["H", "D", "A"])
        self.assertEqual([row.decimal_odds for row in spain_rows], [1.05, 8.00, 15.00])
        self.assertTrue(all(row.market_name == "1X2" for row in spain_rows))
        self.assertTrue(all(row.bet_type_code == "MR" for row in spain_rows))


    def test_parse_upcoming_football_includes_event_metadata(self):
        rows = parse_upcoming_football(load_sample(), captured_at="2026-06-21T08:10:00Z", source_url="sample")
        first = rows[0]

        self.assertEqual(first.captured_at, "2026-06-21T08:10:00Z")
        self.assertEqual(first.event_id, "140085")
        self.assertEqual(first.event_code, "5895")
        self.assertEqual(first.start_time, "2026-06-21T16:00:00Z")
        self.assertEqual(first.competition, "W Cup")
        self.assertEqual(first.category, "Football")
        self.assertEqual(first.source_url, "sample")


if __name__ == "__main__":
    unittest.main()
