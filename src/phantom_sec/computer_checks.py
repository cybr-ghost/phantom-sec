"""Portable, read-only checks about the local computer."""

from __future__ import annotations

import os
import platform
from pathlib import Path
from typing import Any


def memory_info(**_: Any) -> dict[str, Any]:
    if platform.system() == "Linux":
        values: dict[str, int] = {}
        try:
            for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
                key, raw = line.split(":", 1)
                if key in {"MemTotal", "MemAvailable", "SwapTotal", "SwapFree"}:
                    values[key] = int(raw.strip().split()[0]) * 1024
            return {"platform": "Linux", **values}
        except (OSError, ValueError, IndexError):
            pass
    return {"platform": platform.system(), "note": "Memory counters are unavailable on this platform."}


def process_overview(**_: Any) -> dict[str, Any]:
    if platform.system() != "Linux" or not Path("/proc").is_dir():
        return {"platform": platform.system(), "process_count": None,
                "note": "Portable process enumeration is not implemented for this platform."}
    pids = [entry.name for entry in Path("/proc").iterdir() if entry.name.isdigit()]
    return {"platform": "Linux", "process_count": len(pids),
            "note": "Only the count is collected; process arguments and user data are not read."}


def environment_summary(**_: Any) -> dict[str, Any]:
    return {"platform": platform.system(), "architecture": platform.machine(),
            "python": platform.python_version(), "cpu_count": os.cpu_count(),
            "home_directory": str(Path.home())}
