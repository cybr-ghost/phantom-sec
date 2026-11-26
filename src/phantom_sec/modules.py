"""Built-in, read-only tools. No third-party module code is executed."""

from __future__ import annotations

import ctypes
import hashlib
import os
import platform
import shutil
import socket
import stat
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from phantom_sec.computer_checks import (
    battery_info,
    environment_summary,
    memory_info,
    process_overview,
)
from phantom_sec.network_checks import interfaces, reverse_dns
from phantom_sec.web_checks import analyze_url, audit_security_headers, calculate_subnet, inspect_tls
from phantom_sec.domain_checks import certificate_transparency_search, domain_registration, inspect_dns_records


@dataclass(frozen=True)
class Module:
    module_id: str
    name: str
    category: str
    description: str
    handler: Callable[..., dict[str, Any]]


def system_info(**_: Any) -> dict[str, Any]:
    return {"os": platform.platform(), "system": platform.system(), "release": platform.release(),
            "machine": platform.machine(), "python": platform.python_version(),
            "cpu_count": os.cpu_count()}


def system_uptime(**_: Any) -> dict[str, Any]:
    """Show OS uptime without collecting process or user activity."""
    current_platform = platform.system()
    if current_platform == "Windows":
        try:
            tick_counter = ctypes.windll.kernel32.GetTickCount64
            tick_counter.restype = ctypes.c_ulonglong
            uptime_seconds = int(tick_counter() // 1000)
        except (AttributeError, OSError) as exc:
            return {"platform": "Windows", "uptime_seconds": None,
                    "note": f"Could not read Windows uptime: {exc}"}
    elif current_platform == "Linux":
        try:
            raw_uptime = Path("/proc/uptime").read_text(encoding="ascii").split()[0]
            uptime_seconds = int(float(raw_uptime))
        except (OSError, ValueError, IndexError) as exc:
            return {"platform": "Linux", "uptime_seconds": None,
                    "note": f"Could not read Linux uptime information: {exc}"}
    else:
        return {"platform": current_platform, "uptime_seconds": None,
                "note": "Uptime is not implemented for this platform."}
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours or days:
        parts.append(f"{hours}h")
    if minutes or hours or days:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return {"platform": current_platform, "uptime_seconds": uptime_seconds,
            "uptime_human": " ".join(parts),
            "note": "Reads the operating system uptime counter only."}


def firewall_status(**_: Any) -> dict[str, Any]:
    """Read basic UFW/firewalld status without changing firewall configuration."""
    current_platform = platform.system()
    if current_platform == "Windows":
        executable = shutil.which("powershell") or shutil.which("powershell.exe")
        if not executable:
            return {"platform": "Windows", "supported": True, "manager": "Windows Defender Firewall",
                    "profiles": {}, "note": "PowerShell was not found; firewall status is unknown.",
                    "read_only": True}
        command = (
            "Get-NetFirewallProfile | Select-Object Name, Enabled | "
            "ConvertTo-Json -Compress"
        )
        try:
            completed = subprocess.run(
                [executable, "-NoProfile", "-NonInteractive", "-Command", command],
                capture_output=True, text=True, check=False, timeout=5,
            )
            if completed.returncode != 0:
                detail = (completed.stderr or "PowerShell returned an error.").strip()[:200]
                return {"platform": "Windows", "supported": True,
                        "manager": "Windows Defender Firewall", "profiles": {},
                        "note": f"Could not read firewall profiles: {detail}", "read_only": True}
            import json
            raw_profiles = json.loads(completed.stdout or "[]")
            if isinstance(raw_profiles, dict):
                raw_profiles = [raw_profiles]
            profiles = {item["Name"]: bool(item["Enabled"]) for item in raw_profiles
                        if isinstance(item, dict) and "Name" in item and "Enabled" in item}
            note = ("Windows Defender Firewall profile status was read."
                    if profiles else "No firewall profile status was returned.")
            return {"platform": "Windows", "supported": True,
                    "manager": "Windows Defender Firewall", "profiles": profiles,
                    "note": note, "read_only": True}
        except (OSError, subprocess.TimeoutExpired, ValueError, TypeError, KeyError) as exc:
            return {"platform": "Windows", "supported": True,
                    "manager": "Windows Defender Firewall", "profiles": {},
                    "note": f"Firewall status is unknown: {exc}", "read_only": True}
    if current_platform != "Linux":
        return {
            "platform": current_platform,
            "supported": False,
            "managers": [],
            "note": "This read-only check currently supports Linux and Windows.",
        }

    managers = []
    commands = (
        ("ufw", ["status"]),
        ("firewalld", ["--state"]),
    )
    for name, arguments in commands:
        executable = shutil.which("ufw" if name == "ufw" else "firewall-cmd")
        if not executable:
            continue
        try:
            completed = subprocess.run(
                [executable, *arguments],
                capture_output=True,
                text=True,
                check=False,
                timeout=3,
            )
            output = (completed.stdout or "").strip()
            if name == "ufw":
                first_line = output.splitlines()[0].strip().lower() if output else ""
                if first_line == "status: active":
                    status = "active"
                elif first_line == "status: inactive":
                    status = "inactive"
                else:
                    status = "unknown"
            else:
                status = "active" if output.lower() == "running" and completed.returncode == 0 else (
                    "inactive" if output.lower() == "not running" else "unknown"
                )
            managers.append({
                "name": name,
                "status": status,
                "details": output.splitlines()[0][:160] if output else (
                    "No status text returned." if status == "unknown" else ""
                ),
            })
        except subprocess.TimeoutExpired:
            managers.append({"name": name, "status": "unknown", "details": "Status check timed out."})
        except OSError as exc:
            managers.append({"name": name, "status": "unknown", "details": str(exc)[:160]})

    if not managers:
        note = "Neither UFW nor firewalld was detected. Other firewall systems may still be active."
    elif any(manager["status"] == "active" for manager in managers):
        note = "At least one supported firewall manager reports active."
    elif all(manager["status"] == "inactive" for manager in managers):
        note = "Detected firewall managers report inactive. Check whether another firewall system is used."
    else:
        note = "A definitive status was not available for every detected firewall manager."

    return {
        "platform": "Linux",
        "supported": True,
        "managers": managers,
        "note": note,
        "read_only": True,
    }


def system_overview(**_: Any) -> dict[str, Any]:
    """Create a quick local snapshot from existing read-only computer checks."""
    info = system_info()
    memory = memory_info()
    disk = disk_usage()
    processes = process_overview()
    network = interfaces()
    uptime = system_uptime()
    firewall = firewall_status()
    alerts = []

    total_memory = memory.get("MemTotal")
    available_memory = memory.get("MemAvailable")
    if total_memory and available_memory is not None:
        available_percent = round((available_memory / total_memory) * 100, 1)
        if available_percent < 10:
            alerts.append({
                "level": "notice",
                "area": "memory",
                "message": f"Available memory is low ({available_percent}% reported available).",
            })

    if disk["total_bytes"] > 0:
        free_percent = round((disk["free_bytes"] / disk["total_bytes"]) * 100, 1)
        if free_percent < 10:
            alerts.append({
                "level": "notice",
                "area": "storage",
                "message": f"Free disk space is low ({free_percent}% available).",
            })
    else:
        free_percent = None

    return {
        "scope": "local computer only",
        "system": info,
        "uptime": uptime,
        "memory": memory,
        "storage": {**disk, "free_percent": free_percent},
        "processes": processes,
        "network": network,
        "firewall": firewall,
        "notices": alerts,
        "disclaimer": (
            "This is an informational system snapshot, not a full security audit. "
            "It does not scan networks, change settings, or inspect process command lines."
        ),
    }


def disk_usage(path: str | None = None, **_: Any) -> dict[str, Any]:
    target = Path(path or Path.home()).expanduser().resolve()
    usage = shutil.disk_usage(target)
    return {"path": str(target), "total_bytes": usage.total, "used_bytes": usage.used,
            "free_bytes": usage.free}


def file_hash(path: str | None = None, **_: Any) -> dict[str, Any]:
    if not path:
        raise ValueError("Provide --path to a file.")
    target = Path(path).expanduser()
    if not target.is_file():
        raise ValueError("The supplied path is not a regular file.")
    digest = hashlib.sha256()
    with target.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"path": str(target.resolve()), "algorithm": "SHA-256", "digest": digest.hexdigest()}


def file_metadata(path: str | None = None, **_: Any) -> dict[str, Any]:
    if not path:
        raise ValueError("Provide --path to a file.")
    target = Path(path).expanduser()
    if not target.is_file():
        raise ValueError("The supplied path is not a regular file.")
    details = target.stat()
    return {"path": str(target.resolve()), "size_bytes": details.st_size,
            "modified_time": details.st_mtime, "suffix": target.suffix.lower()}


def directory_size(path: str | None = None, **_: Any) -> dict[str, Any]:
    if not path:
        raise ValueError("Provide --path to a directory.")
    root = Path(path).expanduser()
    if not root.is_dir():
        raise ValueError("The supplied path is not a directory.")
    total = count = 0
    for item in root.rglob("*"):
        try:
            if item.is_file() and not item.is_symlink():
                total += item.stat().st_size
                count += 1
        except OSError:
            continue
    return {"path": str(root.resolve()), "files": count, "total_bytes": total}


def file_permissions(path: str | None = None, **_: Any) -> dict[str, Any]:
    """Read permission bits for a local file or folder without changing it."""
    if not path:
        raise ValueError("Provide --path to a file or folder.")
    target = Path(path).expanduser()
    if target.is_symlink():
        raise ValueError("Symbolic links are not checked. Provide the target path instead.")
    try:
        details = target.stat()
    except OSError as exc:
        raise ValueError(f"Could not inspect that path: {exc}") from exc
    if os.name == "nt":
        return {
            "path": str(target.resolve()),
            "type": "directory" if target.is_dir() else "file",
            "current_user_read": os.access(target, os.R_OK),
            "current_user_write": os.access(target, os.W_OK),
            "current_user_execute": os.access(target, os.X_OK),
            "note": "Windows ACL permissions are not decoded. These flags only report access checks for the current process.",
        }
    mode = stat.S_IMODE(details.st_mode)
    return {
        "path": str(target.resolve()),
        "type": "directory" if target.is_dir() else "file",
        "permissions_octal": format(mode, "04o"),
        "owner_read": bool(mode & stat.S_IRUSR),
        "owner_write": bool(mode & stat.S_IWUSR),
        "owner_execute": bool(mode & stat.S_IXUSR),
        "group_read": bool(mode & stat.S_IRGRP),
        "group_write": bool(mode & stat.S_IWGRP),
        "group_execute": bool(mode & stat.S_IXGRP),
        "other_read": bool(mode & stat.S_IROTH),
        "other_write": bool(mode & stat.S_IWOTH),
        "other_execute": bool(mode & stat.S_IXOTH),
        "world_writable": bool(mode & stat.S_IWOTH),
        "note": "Read-only permission check. It does not change file permissions.",
    }


def dns_lookup(domain: str | None = None, **_: Any) -> dict[str, Any]:
    if not domain:
        raise ValueError("Provide --domain with a hostname.")
    name = domain.strip().rstrip(".")
    if not name or len(name) > 253 or "/" in name or " " in name:
        raise ValueError("Enter a valid hostname, not a URL or path.")
    try:
        records = sorted({entry[4][0] for entry in socket.getaddrinfo(name, None)})
    except socket.gaierror as exc:
        raise ValueError(f"DNS lookup failed: {exc}") from exc
    return {"hostname": name, "addresses": records, "method": "system DNS resolver"}


def local_hostname(**_: Any) -> dict[str, Any]:
    return {"hostname": socket.gethostname(), "fqdn": socket.getfqdn()}


_MODULES = (
    Module("system.info", "System information", "System", "Show basic OS and runtime information.", system_info),
    Module("system.uptime", "System uptime", "System", "Show how long the computer has been running on Linux.", system_uptime),
    Module("system.overview", "System overview", "System", "Create a quick read-only snapshot of this computer.", system_overview),
    Module("system.firewall", "Firewall status", "System", "Check basic UFW and firewalld status without changing settings.", firewall_status),
    Module("system.memory", "Memory overview", "System", "Show available memory counters where supported.", memory_info),
    Module("system.battery", "Battery status", "System", "Read battery charge and charging status where available.", battery_info),
    Module("system.process-count", "Process count", "System", "Show a process count without reading process arguments.", process_overview),
    Module("system.environment", "Environment summary", "System", "Show basic local environment information.", environment_summary),
    Module("system.disk", "Disk usage", "System", "Show storage usage for a local path.", disk_usage),
    Module("system.hostname", "Local hostname", "System", "Show the local machine hostname.", local_hostname),
    Module("file.sha256", "SHA-256 file hash", "File analysis", "Hash a file without modifying it.", file_hash),
    Module("file.metadata", "File metadata", "File analysis", "Show basic metadata for a local file.", file_metadata),
    Module("file.directory-size", "Directory size", "File analysis", "Calculate regular-file sizes in a directory.", directory_size),
    Module("file.permissions", "File permissions", "File analysis", "Inspect permission bits without changing them.", file_permissions),
    Module("network.interfaces", "Network interfaces", "Network diagnostics", "List local network interface names.", interfaces),
    Module("network.dns", "DNS lookup", "Network diagnostics", "Resolve a hostname with the system resolver.", dns_lookup),
    Module("network.reverse-dns", "Reverse DNS", "Network diagnostics", "Look up the PTR hostname for an IP address.", reverse_dns),
    Module("network.subnet-calculator", "Subnet calculator", "Network intelligence", "Calculate network ranges and address boundaries locally.", calculate_subnet),
    Module("web.url-analyzer", "URL structure analyzer", "Website security", "Inspect URL structure and basic indicators without contacting the URL.", analyze_url),
    Module("web.tls-inspector", "TLS certificate inspector", "Website security", "Inspect a hostname’s public TLS certificate on port 443.", inspect_tls),
    Module("web.security-headers", "Security headers auditor", "Website security", "Review common browser security headers using an HTTP HEAD request.", audit_security_headers),
    Module("domain.dns-records", "DNS record inspector", "Domain intelligence", "Inspect A, AAAA, MX, TXT, NS, SOA and CAA records.", inspect_dns_records),
    Module("domain.rdap", "Domain registration lookup", "Domain intelligence", "Retrieve public RDAP registration events, status and nameservers.", domain_registration),
    Module("domain.certificate-transparency", "Certificate transparency search", "Domain intelligence", "Find publicly logged TLS certificates for a domain and its subdomains.", certificate_transparency_search),
)


def get_modules() -> tuple[Module, ...]:
    return _MODULES


def run_module(module_id: str, **kwargs: Any) -> dict[str, Any]:
    module = next((item for item in _MODULES if item.module_id == module_id), None)
    if module is None:
        raise ValueError(f"Unknown module: {module_id}")
    return {"module": module.module_id, "name": module.name, "result": module.handler(**kwargs)}
