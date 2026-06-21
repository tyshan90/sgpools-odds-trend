from __future__ import annotations

from typing import Any

from .models import OddsRow


def parse_upcoming_football(payload: dict[str, Any], captured_at: str, source_url: str) -> list[OddsRow]:
    rows: list[OddsRow] = []
    event_codes = _mapping(payload, "retailIds", "event")

    for event in payload.get("events", []):
        event_type = event.get("type") or {}
        sport_class = event_type.get("sportClass") or {}
        category = sport_class.get("category") or {}

        event_id = str(event.get("id", ""))
        for market in event.get("markets", []):
            market_id = str(market.get("id", ""))
            market_name = str(market.get("name", ""))
            bet_type_code = str(market.get("minorCode", ""))

            for outcome in market.get("outcomes", []):
                price = _first_decimal_price(outcome.get("prices", []))
                if price is None:
                    continue

                rows.append(
                    OddsRow(
                        captured_at=captured_at,
                        event_id=event_id,
                        event_code=event_codes.get(event_id, ""),
                        event_name=str(event.get("name", "")),
                        start_time=str(event.get("startTime", "")),
                        competition=str(event_type.get("name", "")),
                        category=str(category.get("name", "")),
                        market_id=market_id,
                        market_name=market_name,
                        bet_type_code=bet_type_code,
                        outcome_id=str(outcome.get("id", "")),
                        selection_code=str(outcome.get("minorCode", "")),
                        selection_name=str(outcome.get("name", "")),
                        decimal_odds=price,
                        source_url=source_url,
                    )
                )

    return rows


def _first_decimal_price(prices: list[dict[str, Any]]) -> float | None:
    for price in prices:
        decimal = price.get("decimal")
        if decimal is None:
            continue
        try:
            return float(decimal)
        except (TypeError, ValueError):
            continue
    return None


def _mapping(payload: dict[str, Any], group: str, level: str) -> dict[str, str]:
    raw_mapping = (((payload.get(group) or {}).get(level) or {}).get("mapping") or {})
    return {str(key): str(value) for key, value in raw_mapping.items()}

