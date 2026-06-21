from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable

from .models import OddsChange, OddsRow


class OddsStore:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def insert_rows(self, rows: Iterable[OddsRow]) -> int:
        rows = list(rows)
        if not rows:
            return 0

        with self._connect() as conn:
            before = conn.total_changes
            conn.executemany(
                """
                INSERT OR IGNORE INTO odds_snapshots (
                    captured_at, event_id, event_code, event_name, start_time,
                    competition, category, market_id, market_name, bet_type_code,
                    outcome_id, selection_code, selection_name, decimal_odds, source_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [self._row_tuple(row) for row in rows],
            )
            return conn.total_changes - before

    def latest_for_match(self, query: str, market_name: str | None = None) -> list[OddsRow]:
        where, params = self._match_where(query, market_name)
        with self._connect() as conn:
            latest = conn.execute(
                f"SELECT MAX(captured_at) FROM odds_snapshots WHERE {where}",
                params,
            ).fetchone()[0]
            if latest is None:
                return []

            rows = conn.execute(
                f"""
                SELECT * FROM odds_snapshots
                WHERE {where} AND captured_at = ?
                ORDER BY event_name, market_name,
                    CASE selection_code
                        WHEN 'H' THEN 1
                        WHEN 'D' THEN 2
                        WHEN 'A' THEN 3
                        ELSE 9
                    END,
                    selection_name
                """,
                [*params, latest],
            ).fetchall()
            return [self._from_sql_row(row) for row in rows]

    def change_for_match(self, query: str, market_name: str | None = None) -> list[OddsChange]:
        latest_rows = self.latest_for_match(query, market_name)
        changes: list[OddsChange] = []

        with self._connect() as conn:
            for latest in latest_rows:
                previous = conn.execute(
                    """
                    SELECT * FROM odds_snapshots
                    WHERE event_id = ?
                      AND market_id = ?
                      AND outcome_id = ?
                      AND captured_at < ?
                    ORDER BY captured_at DESC
                    LIMIT 1
                    """,
                    [latest.event_id, latest.market_id, latest.outcome_id, latest.captured_at],
                ).fetchone()
                if previous is None:
                    continue

                previous_row = self._from_sql_row(previous)
                absolute = round(latest.decimal_odds - previous_row.decimal_odds, 4)
                percentage = 0.0
                if previous_row.decimal_odds:
                    percentage = round((absolute / previous_row.decimal_odds) * 100, 2)

                changes.append(
                    OddsChange(
                        event_id=latest.event_id,
                        event_name=latest.event_name,
                        market_name=latest.market_name,
                        selection_name=latest.selection_name,
                        previous_captured_at=previous_row.captured_at,
                        latest_captured_at=latest.captured_at,
                        previous_odds=previous_row.decimal_odds,
                        latest_odds=latest.decimal_odds,
                        absolute_change=absolute,
                        percentage_change=percentage,
                    )
                )

        return changes

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS odds_snapshots (
                    captured_at TEXT NOT NULL,
                    event_id TEXT NOT NULL,
                    event_code TEXT NOT NULL,
                    event_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    competition TEXT NOT NULL,
                    category TEXT NOT NULL,
                    market_id TEXT NOT NULL,
                    market_name TEXT NOT NULL,
                    bet_type_code TEXT NOT NULL,
                    outcome_id TEXT NOT NULL,
                    selection_code TEXT NOT NULL,
                    selection_name TEXT NOT NULL,
                    decimal_odds REAL NOT NULL,
                    source_url TEXT NOT NULL,
                    PRIMARY KEY (captured_at, event_id, market_id, outcome_id)
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_odds_event_name ON odds_snapshots(event_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_odds_lookup ON odds_snapshots(event_id, market_id, outcome_id, captured_at)")

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _match_where(self, query: str, market_name: str | None) -> tuple[str, list[str]]:
        tokens = [token for token in query.lower().split() if token]
        clauses = ["LOWER(event_name) LIKE ?" for _ in tokens]
        params = [f"%{token}%" for token in tokens]
        if not clauses:
            clauses.append("1 = 1")
        if market_name:
            clauses.append("market_name = ?")
            params.append(market_name)
        return " AND ".join(clauses), params

    @staticmethod
    def _row_tuple(row: OddsRow) -> tuple[object, ...]:
        return (
            row.captured_at,
            row.event_id,
            row.event_code,
            row.event_name,
            row.start_time,
            row.competition,
            row.category,
            row.market_id,
            row.market_name,
            row.bet_type_code,
            row.outcome_id,
            row.selection_code,
            row.selection_name,
            row.decimal_odds,
            row.source_url,
        )

    @staticmethod
    def _from_sql_row(row: sqlite3.Row) -> OddsRow:
        return OddsRow(
            captured_at=row["captured_at"],
            event_id=row["event_id"],
            event_code=row["event_code"],
            event_name=row["event_name"],
            start_time=row["start_time"],
            competition=row["competition"],
            category=row["category"],
            market_id=row["market_id"],
            market_name=row["market_name"],
            bet_type_code=row["bet_type_code"],
            outcome_id=row["outcome_id"],
            selection_code=row["selection_code"],
            selection_name=row["selection_name"],
            decimal_odds=float(row["decimal_odds"]),
            source_url=row["source_url"],
        )
