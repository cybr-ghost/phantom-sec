"""Basic, low-impact network information and DNS checks."""

from __future__ import annotations

import socket
from typing import Any


def interfaces(**_: Any) -> dict[str, Any]:
    try:
        names = [{"index": index, "name": name} for index, name in socket.if_nameindex()]
    except OSError as exc:
        raise ValueError(f"Could not list network interfaces: {exc}") from exc
    return {"interfaces": names, "note": "Interface names only; no packet capture is performed."}


def reverse_dns(address: str | None = None, **_: Any) -> dict[str, Any]:
    if not address:
        raise ValueError("Provide --address with an IP address.")
    try:
        socket.inet_pton(socket.AF_INET, address)
        family = socket.AF_INET
    except OSError:
        try:
            socket.inet_pton(socket.AF_INET6, address)
            family = socket.AF_INET6
        except OSError as exc:
            raise ValueError("Enter a valid IPv4 or IPv6 address.") from exc
    try:
        hostname, aliases, _ = socket.gethostbyaddr(address)
    except (socket.herror, socket.gaierror) as exc:
        raise ValueError(f"Reverse DNS lookup failed: {exc}") from exc
    return {"address": address, "hostname": hostname, "aliases": aliases,
            "address_family": "IPv6" if family == socket.AF_INET6 else "IPv4"}



def local_addresses(**_: Any) -> dict[str, Any]:
    """List IP addresses returned for this computer's own hostname only."""
    hostname = socket.gethostname()
    try:
        records = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError(f"Could not resolve local addresses: {exc}") from exc
    found: dict[tuple[int, str], dict[str, str]] = {}
    for family, _, _, _, sockaddr in records:
        if family not in (socket.AF_INET, socket.AF_INET6):
            continue
        address = sockaddr[0]
        version = "IPv6" if family == socket.AF_INET6 else "IPv4"
        found[(family, address)] = {
            "address": address,
            "family": version,
            "scope": "loopback" if ip_is_loopback(address) else "local interface",
        }
    addresses = sorted(found.values(), key=lambda item: (item["family"], item["address"]))
    return {
        "hostname": hostname,
        "addresses": addresses,
        "address_count": len(addresses),
        "note": "Only the local computer hostname is resolved. No remote hosts are scanned.",
    }


def ip_is_loopback(address: str) -> bool:
    """Return whether an IP address is in a loopback range."""
    import ipaddress

    return ipaddress.ip_address(address).is_loopback
