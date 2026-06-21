from dataclasses import dataclass


@dataclass(frozen=True)
class OddsRow:
    captured_at: str
    event_id: str
    event_code: str
    event_name: str
    start_time: str
    competition: str
    category: str
    market_id: str
    market_name: str
    bet_type_code: str
    outcome_id: str
    selection_code: str
    selection_name: str
    decimal_odds: float
    source_url: str


@dataclass(frozen=True)
class OddsChange:
    event_id: str
    event_name: str
    market_name: str
    selection_name: str
    previous_captured_at: str
    latest_captured_at: str
    previous_odds: float
    latest_odds: float
    absolute_change: float
    percentage_change: float

