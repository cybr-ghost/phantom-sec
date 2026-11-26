"""Portable, read-only checks about the local computer."""

from __future__ import annotations

import csv
import ctypes
import os
import platform
import subprocess
from pathlib import Path
from typing import Any


def _windows_memory_info() -> dict[str, Any]:
    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatus()
    status.dwLength = ctypes.sizeof(MemoryStatus)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    if not kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError(ctypes.get_last_error(), "GlobalMemoryStatusEx failed")
    return {
        "platform": "Windows",
        "MemTotal": status.ullTotalPhys,
        "MemAvailable": status.ullAvailPhys,
        "memory_load_percent": status.dwMemoryLoad,
        "SwapTotal": status.ullTotalPageFile - status.ullTotalPhys,
        "SwapFree": status.ullAvailPageFile - status.ullAvailPhys,
    }


def memory_info(**_: Any) -> dict[str, Any]:
    if platform.system() == "Windows":
        try:
            return _windows_memory_info()
        except (AttributeError, OSError) as exc:
            return {"platform": "Windows", "note": f"Windows memory counters unavailable: {exc}"}
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
    current_platform = platform.system()
    if current_platform == "Windows":
        try:
            completed = subprocess.run(
                ["tasklist", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            if completed.returncode != 0:
                raise OSError((completed.stderr or "tasklist returned an error")[:200])
            rows = list(csv.reader(completed.stdout.splitlines()))
            count = sum(1 for row in rows if row and len(row) >= 2)
            return {"platform": "Windows", "process_count": count,
                    "note": "Only the process count is collected; command lines are not read."}
        except (OSError, subprocess.TimeoutExpired, csv.Error) as exc:
            return {"platform": "Windows", "process_count": None,
                    "note": f"Could not count processes: {exc}"}
    if current_platform != "Linux" or not Path("/proc").is_dir():
        return {"platform": current_platform, "process_count": None,
                "note": "Process counting is not implemented for this platform."}
    pids = [entry.name for entry in Path("/proc").iterdir() if entry.name.isdigit()]
    return {"platform": "Linux", "process_count": len(pids),
            "note": "Only the count is collected; process arguments and user data are not read."}


def environment_summary(**_: Any) -> dict[str, Any]:
    return {"platform": platform.system(), "architecture": platform.machine(),
            "python": platform.python_version(), "cpu_count": os.cpu_count(),
            "home_directory": str(Path.home())}



def battery_info(**_: Any) -> dict[str, Any]:
    """Read battery charge and status where the operating system exposes it."""
    current_platform = platform.system()
    if current_platform == "Windows":
        class PowerStatus(ctypes.Structure):
            _fields_ = [
                ("ACLineStatus", ctypes.c_ubyte),
                ("BatteryFlag", ctypes.c_ubyte),
                ("BatteryLifePercent", ctypes.c_ubyte),
                ("SystemStatusFlag", ctypes.c_ubyte),
                ("BatteryLifeTime", ctypes.c_ulong),
                ("BatteryFullLifeTime", ctypes.c_ulong),
            ]

        status = PowerStatus()
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        if not kernel32.GetSystemPowerStatus(ctypes.byref(status)):
            return {"platform": "Windows", "available": False,
                    "note": "Windows did not provide battery status."}
        if status.BatteryFlag == 128:
            return {"platform": "Windows", "available": False,
                    "note": "No battery is present or battery status is unavailable."}
        percent = status.BatteryLifePercent
        return {
            "platform": "Windows",
            "available": percent <= 100,
            "charge_percent": percent if percent <= 100 else None,
            "charging": status.ACLineStatus == 1,
            "on_ac_power": status.ACLineStatus == 1,
            "note": "Read from the Windows power status API.",
        }
    if current_platform == "Linux":
        batteries = []
        for entry in Path("/sys/class/power_supply").glob("BAT*"):
            try:
                capacity = int((entry / "capacity").read_text(encoding="ascii").strip())
                status = (entry / "status").read_text(encoding="ascii").strip()
                batteries.append({"name": entry.name, "charge_percent": capacity,
                                  "status": status})
            except (OSError, ValueError):
                continue
        if batteries:
            return {"platform": "Linux", "available": True, "batteries": batteries,
                    "note": "Read battery details from the Linux power-supply interface."}
        return {"platform": "Linux", "available": False,
                "note": "No readable battery was detected. Desktop computers may not have one."}
    return {"platform": current_platform, "available": False,
            "note": "Battery status is not implemented for this platform."}
