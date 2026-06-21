from __future__ import annotations

from collections import defaultdict

from .models import OddsChange, OddsRow


def format_latest(rows: list[OddsRow]) -> str:
    if not rows:
        return "No stored odds found for that match."

    grouped: dict[tuple[str, str], list[OddsRow]] = defaultdict(list)
    for row in rows:
        grouped[(row.event_name, row.market_name)].append(row)

    lines: list[str] = []
    for (event_name, market_name), market_rows in grouped.items():
        lines.append(f"{event_name} - {market_name}")
        lines.append("")
        for row in market_rows:
            lines.append(f"{row.selection_name}: {row.decimal_odds:.2f}")
        lines.append("")
        lines.append(f"Last updated: {market_rows[0].captured_at}")
        lines.append("")

    return "\n".join(lines).strip()


def format_changes(changes: list[OddsChange]) -> str:
    if not changes:
        return "No odds change found yet. The tracker needs at least two snapshots for this match."

    grouped: dict[tuple[str, str], list[OddsChange]] = defaultdict(list)
    for change in changes:
        grouped[(change.event_name, change.market_name)].append(change)

    lines: list[str] = []
    for (event_name, market_name), market_changes in grouped.items():
        lines.append(f"{event_name} - {market_name}")
        lines.append("")
        for change in market_changes:
            absolute = _signed(change.absolute_change)
            percentage = _signed(change.percentage_change)
            lines.append(
                f"{change.selection_name}: {change.previous_odds:.2f} -> "
                f"{change.latest_odds:.2f} ({absolute}, {percentage}%)"
            )
        lines.append("")
        lines.append(f"Previous: {market_changes[0].previous_captured_at}")
        lines.append(f"Latest: {market_changes[0].latest_captured_at}")
        lines.append("")

    return "\n".join(lines).strip()


def _signed(value: float) -> str:
    return f"{value:+.2f}"

