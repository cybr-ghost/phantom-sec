"""Passive web and network inspection helpers for authorised use."""

from __future__ import annotations

import ipaddress
import socket
import ssl
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen


def analyze_url(url: str | None = None, **_: object) -> dict[str, object]:
    """Inspect URL structure locally; does not open or contact the URL."""
    if not url:
        raise ValueError("Provide --url with an HTTP or HTTPS URL.")
    candidate = url.strip()
    try:
        parts = urlsplit(candidate)
        hostname = parts.hostname
        port = parts.port
    except ValueError as exc:
        raise ValueError(f"Invalid URL: {exc}") from exc
    if parts.scheme.lower() not in {"http", "https"} or not hostname:
        raise ValueError("Enter a complete HTTP or HTTPS URL, including its hostname.")
    flags: list[str] = []
    if parts.scheme.lower() != "https":
        flags.append("The URL uses HTTP rather than HTTPS.")
    if parts.username is not None or parts.password is not None:
        flags.append("The URL contains user information before the hostname.")
    try:
        ipaddress.ip_address(hostname)
        host_is_ip = True
        flags.append("The URL uses an IP address instead of a domain name.")
    except ValueError:
        host_is_ip = False
    if port not in (None, 80, 443):
        flags.append(f"The URL specifies a non-standard port ({port}).")
    if len(candidate) > 200:
        flags.append("The URL is unusually long.")
    if unquote(parts.path).count("/") != parts.path.count("/"):
        flags.append("The path contains percent-encoded characters.")
    if not flags:
        flags.append("No basic structural indicators were detected.")
    return {
        "url": candidate,
        "scheme": parts.scheme.lower(),
        "hostname": hostname,
        "host_is_ip_address": host_is_ip,
        "port": port or (443 if parts.scheme.lower() == "https" else 80),
        "path": parts.path,
        "query_present": bool(parts.query),
        "fragment_present": bool(parts.fragment),
        "indicators": flags,
        "network_access": False,
        "note": "Structural indicators are not a verdict. This check does not determine whether a URL is safe or malicious.",
    }


def calculate_subnet(network: str | None = None, **_: object) -> dict[str, object]:
    """Calculate network boundaries locally without sending traffic."""
    if not network:
        raise ValueError("Provide --network with an IP network, for example 192.168.1.0/24.")
    try:
        parsed = ipaddress.ip_network(network.strip(), strict=False)
    except ValueError as exc:
        raise ValueError(f"Invalid IP network: {exc}") from exc
    result: dict[str, object] = {
        "input": network,
        "network": str(parsed.network_address),
        "netmask": str(parsed.netmask),
        "prefix_length": parsed.prefixlen,
        "broadcast": str(parsed.broadcast_address) if parsed.version == 4 else None,
        "address_family": f"IPv{parsed.version}",
        "total_addresses": parsed.num_addresses,
        "usable_hosts": max(parsed.num_addresses - (2 if parsed.version == 4 and parsed.prefixlen < 31 else 0), 0),
        "first_address": str(parsed[0]),
        "last_address": str(parsed[-1]),
        "network_access": False,
    }
    return result


def inspect_tls(hostname: str | None = None, **_: object) -> dict[str, object]:
    """Read the public TLS certificate presented by a hostname on TCP port 443."""
    if not hostname:
        raise ValueError("Provide --hostname with a hostname.")
    host = hostname.strip().rstrip(".")
    if not host or "/" in host or " " in host or ":" in host:
        raise ValueError("Enter a hostname only, without a URL, path, or port.")
    context = ssl.create_default_context()
    try:
        with socket.create_connection((host, 443), timeout=5) as raw_socket:
            with context.wrap_socket(raw_socket, server_hostname=host) as tls_socket:
                certificate = tls_socket.getpeercert()
                cipher = tls_socket.cipher()
                version = tls_socket.version()
    except (OSError, ssl.SSLError) as exc:
        raise ValueError(f"TLS inspection could not complete: {exc}") from exc
    not_after = certificate.get("notAfter")
    expires_at = None
    days_remaining = None
    if not_after:
        expiry = datetime.fromtimestamp(ssl.cert_time_to_seconds(not_after), tz=timezone.utc)
        expires_at = expiry.isoformat()
        days_remaining = (expiry - datetime.now(timezone.utc)).days
    subject = {
        key: value
        for group in certificate.get("subject", ())
        for key, value in group
        if key in {"commonName", "organizationName"}
    }
    issuer = {
        key: value
        for group in certificate.get("issuer", ())
        for key, value in group
        if key in {"commonName", "organizationName"}
    }
    return {
        "hostname": host,
        "tls_version": version,
        "cipher": cipher[0] if cipher else None,
        "certificate_subject": subject,
        "certificate_issuer": issuer,
        "expires_at": expires_at,
        "days_until_expiry": days_remaining,
        "subject_alt_name_count": len(certificate.get("subjectAltName", ())),
        "verification": "passed (system trust store)",
        "note": "Connects to the supplied hostname on TCP port 443 and reads its public certificate. Use only on systems you are authorised to assess.",
    }


_SECURITY_HEADERS = {
    "strict-transport-security": "Helps browsers require HTTPS on future visits.",
    "content-security-policy": "Restricts the sources a browser may load content from.",
    "x-content-type-options": "Helps prevent MIME-type sniffing.",
    "x-frame-options": "Can reduce clickjacking risk in older browser implementations.",
    "referrer-policy": "Controls how much referrer information browsers send.",
    "permissions-policy": "Controls access to selected browser features.",
}


def audit_security_headers(url: str | None = None, **_: object) -> dict[str, object]:
    """Request HTTP response headers and report common browser security headers."""
    if not url:
        raise ValueError("Provide --url with an HTTP or HTTPS URL.")
    candidate = url.strip()
    try:
        parts = urlsplit(candidate)
        if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
            raise ValueError("Enter a complete HTTP or HTTPS URL.")
    except ValueError as exc:
        raise ValueError(f"Invalid URL: {exc}") from exc
    request = Request(candidate, headers={"User-Agent": "PhantomSec-HeaderAudit/1.0"}, method="HEAD")
    try:
        with urlopen(request, timeout=7) as response:
            status = response.status
            final_url = response.geturl()
            headers = response.headers
    except HTTPError as exc:
        status = exc.code
        final_url = exc.geturl()
        headers = exc.headers
    except (URLError, OSError, TimeoutError) as exc:
        raise ValueError(f"Could not retrieve response headers: {exc}") from exc
    found = {name: bool(headers.get(name)) for name in _SECURITY_HEADERS}
    return {
        "requested_url": candidate,
        "final_url": final_url,
        "http_status": status,
        "security_headers": {
            name: {"present": found[name], "purpose": purpose}
            for name, purpose in _SECURITY_HEADERS.items()
        },
        "missing_headers": [name for name, present in found.items() if not present],
        "note": "A missing header is not automatically a vulnerability. HEAD requests may be handled differently from normal page requests.",
    }
