from __future__ import annotations

import os
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    linkup_api_key: str
    database_path: Path

    @classmethod
    def from_mapping(cls, values: Mapping[str, str] | None = None) -> "Settings":
        source = os.environ if values is None else values
        return cls(
            telegram_bot_token=source.get("TELEGRAM_BOT_TOKEN", "").strip(),
            linkup_api_key=(source.get("LINKUP_API_KEY") or source.get("linkup") or "").strip(),
            database_path=Path(source.get("DATABASE_PATH", ".runtime/odds.sqlite")),
        )


def load_settings(env_file: str | Path | None = None, overrides: Mapping[str, str] | None = None) -> Settings:
    values: dict[str, str] = dict(os.environ)
    if env_file:
        values.update(load_env_file(env_file))
    if overrides:
        values.update({key: value for key, value in overrides.items() if value is not None})
    return Settings.from_mapping(values)


def load_env_file(path: str | Path) -> dict[str, str]:
    env_path = Path(path)
    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        key = key.strip()
        if not key or not key.replace("_", "").isalnum() or key[0].isdigit():
            continue
        values[key] = _parse_env_value(raw_value.strip())
    return values


def _parse_env_value(value: str) -> str:
    if not value:
        return ""
    try:
        parsed = shlex.split(value, posix=True)
    except ValueError:
        return value.strip("\"'")
    if len(parsed) == 1:
        return parsed[0]
    return value.strip("\"'")
