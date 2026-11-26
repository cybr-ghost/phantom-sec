"""Privacy-conscious local report export helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def export_json(data: dict[str, Any], destination: Path) -> Path:
    destination = destination.expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(data, indent=2, sort_keys=True, default=str) + "\n",
                           encoding="utf-8")
    return destination
