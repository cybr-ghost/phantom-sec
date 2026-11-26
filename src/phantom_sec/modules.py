"""Built-in, read-only modules. No third-party module code is executed."""

from __future__ import annotations

import hashlib
import os
import platform
import shutil
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from phantom_sec.network_tools import interfaces, reverse_dns
from phantom_sec.system_tools import environment_summary, memory_info, process_overview


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
    stat = target.stat()
    return {"path": str(target.resolve()), "size_bytes": stat.st_size,
            "modified_time": stat.st_mtime, "suffix": target.suffix.lower()}


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
    Module("system.memory", "Memory overview", "System", "Show available memory counters where supported.", memory_info),
    Module("system.process-count", "Process count", "System", "Show a process count without reading process arguments.", process_overview),
    Module("system.environment", "Environment summary", "System", "Show basic local environment information.", environment_summary),
    Module("system.disk", "Disk usage", "System", "Show storage usage for a local path.", disk_usage),
    Module("system.hostname", "Local hostname", "System", "Show the local machine hostname.", local_hostname),
    Module("file.sha256", "SHA-256 file hash", "File analysis", "Hash a file without modifying it.", file_hash),
    Module("file.metadata", "File metadata", "File analysis", "Show basic metadata for a local file.", file_metadata),
    Module("file.directory-size", "Directory size", "File analysis", "Calculate regular-file sizes in a directory.", directory_size),
    Module("network.interfaces", "Network interfaces", "Network diagnostics", "List local network interface names.", interfaces),
    Module("network.dns", "DNS lookup", "Network diagnostics", "Resolve a hostname with the system resolver.", dns_lookup),
    Module("network.reverse-dns", "Reverse DNS", "Network diagnostics", "Look up the PTR hostname for an IP address.", reverse_dns),
)


def get_modules() -> tuple[Module, ...]:
    return _MODULES


def run_module(module_id: str, **kwargs: Any) -> dict[str, Any]:
    module = next((item for item in _MODULES if item.module_id == module_id), None)
    if module is None:
        raise ValueError(f"Unknown module: {module_id}")
    return {"module": module.module_id, "name": module.name, "result": module.handler(**kwargs)}
