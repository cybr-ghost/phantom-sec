"""Helpers for exporting local Phantom Sec reports."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def export_json(data: dict[str, Any], destination: Path) -> Path:
    destination = destination.expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(data, indent=2, sort_keys=True, default=str) + "\n",
                           encoding="utf-8")
    return destination


def export_history_csv(rows: list[dict[str, Any]], destination: Path) -> Path:
    destination = destination.expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["id", "module_id", "created_at", "result"])
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "result": json.dumps(row["result"], sort_keys=True)})
    return destination
