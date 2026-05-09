from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.config import ROOT, LoggingConfig

LOGGABLE_LEVELS = {"SUSPICIOUS", "HIGH", "CRITICAL"}


def threat_event_path(config: LoggingConfig) -> Path:
    directory = Path(config.directory)
    if not directory.is_absolute():
        directory = ROOT / directory
    return directory / config.threat_events_file


def append_threat_event(event: dict[str, Any], config: LoggingConfig) -> Path | None:
    if event.get("threat_level") not in LOGGABLE_LEVELS:
        return None
    path = threat_event_path(config)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
    return path
