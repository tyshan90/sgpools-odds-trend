import unittest

from sgpools_trend.formatting import format_changes, format_latest
from sgpools_trend.models import OddsChange, OddsRow


class FormattingTests(unittest.TestCase):
    def test_format_latest_groups_rows_by_match(self):
        rows = [
            OddsRow(
                captured_at="2026-06-21T08:20:00Z",
                event_id="140085",
                event_code="5895",
                event_name="Spain vs Saudi Arabia",
                start_time="2026-06-21T16:00:00Z",
                competition="W Cup",
                category="Football",
                market_id="2201373",
                market_name="1X2",
                bet_type_code="MR",
                outcome_id="1",
                selection_code="H",
                selection_name="Spain",
                decimal_odds=1.05,
                source_url="sample",
            )
        ]

        text = format_latest(rows)

        self.assertIn("Spain vs Saudi Arabia - 1X2", text)
        self.assertIn("Spain: 1.05", text)
        self.assertIn("Last updated: 2026-06-21T08:20:00Z", text)

    def test_format_changes_shows_direction_and_percent(self):
        changes = [
            OddsChange(
                event_id="140085",
                event_name="Spain vs Saudi Arabia",
                market_name="1X2",
                selection_name="Spain",
                previous_captured_at="2026-06-21T08:10:00Z",
                latest_captured_at="2026-06-21T08:20:00Z",
                previous_odds=1.05,
                latest_odds=1.08,
                absolute_change=0.03,
                percentage_change=2.86,
            )
        ]

        text = format_changes(changes)

        self.assertIn("Spain vs Saudi Arabia - 1X2", text)
        self.assertIn("Spain: 1.05 -> 1.08 (+0.03, +2.86%)", text)


if __name__ == "__main__":
    unittest.main()
