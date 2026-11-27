"""Privacy-focused, read-only checks for user-supplied data and the local computer."""

from __future__ import annotations

import ipaddress
import os
import platform
import re
from email import policy
from email.parser import BytesParser, Parser
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


def check_email_address(address: str | None = None, **_: Any) -> dict[str, Any]:
    """Check email syntax only; never send mail or verify ownership."""
    if not address:
        raise ValueError("Provide --address with an email address.")
    value = address.strip()
    valid = False
    if len(value) <= 254 and value.count("@") == 1:
        local, domain = value.rsplit("@", 1)
        labels = domain.rstrip(".").split(".")
        valid = (
            0 < len(local) <= 64
            and bool(re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_{|}~-]+", local))
            and not local.startswith(".") and not local.endswith(".") and ".." not in local
            and len(labels) >= 2
            and all(0 < len(label) <= 63 and re.fullmatch(
                r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?", label
            ) for label in labels)
        )
    return {"address_syntax_valid": bool(valid),
            "domain": value.rsplit("@", 1)[1].lower() if valid else None,
            "network_access": False,
            "note": "Syntax only. Mailbox existence, ownership, deliverability, and identity are not checked."}


def audit_email_auth_headers(headers: str | None = None, **_: Any) -> dict[str, Any]:
    """Extract SPF, DKIM, and DMARC verdicts without exposing routing data."""
    if not headers:
        raise ValueError("Provide --headers with the message headers.")
    if len(headers) > 50000:
        raise ValueError("Email headers exceed the 50 KB analysis limit.")
    parsed = Parser(policy=policy.default, headersonly=True).parsestr(headers)
    results = []
    for value in parsed.get_all("Authentication-Results", []):
        for match in re.finditer(r"\b(spf|dkim|dmarc)\s*=\s*([A-Za-z]+)", str(value), re.I):
            results.append({"method": match.group(1).lower(), "result": match.group(2).lower()})
    return {
        "authentication_results": results,
        "headers_found": len(parsed.get_all("Authentication-Results", [])),
        "note": "Only authentication verdict labels are extracted. Routing IPs and sender details are not returned. Headers can be forged.",
    }


class _TrackingImageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.image_count = 0
        self.tiny_candidates = 0
        self.hidden_candidates = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "img":
            return
        self.image_count += 1
        values = {key.lower(): value for key, value in attrs if value is not None}
        width = values.get("width", "").strip().lower()
        height = values.get("height", "").strip().lower()
        style = values.get("style", "").lower().replace(" ", "")
        if width in {"0", "1", "1px"} or height in {"0", "1", "1px"}:
            self.tiny_candidates += 1
        if "display:none" in style or "visibility:hidden" in style:
            self.hidden_candidates += 1


def inspect_email_tracking_pixels(path: str | None = None, **_: Any) -> dict[str, Any]:
    """Find tiny or hidden image elements in a local HTML email without contacting them."""
    if not path:
        raise ValueError("Provide --path to a local HTML file.")
    target = Path(path).expanduser()
    if target.is_symlink() or not target.is_file() or target.suffix.lower() not in {".html", ".htm"}:
        raise ValueError("Provide a regular .html or .htm file, not a folder or symbolic link.")
    try:
        if target.stat().st_size > 2 * 1024 * 1024:
            raise ValueError("HTML file exceeds the 2 MiB inspection limit.")
        source = target.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise ValueError(f"Could not read the HTML file: {exc}") from exc
    parser = _TrackingImageParser()
    parser.feed(source)
    return {
        "path": str(target.resolve()), "images_found": parser.image_count,
        "tiny_image_candidates": parser.tiny_candidates,
        "hidden_image_candidates": parser.hidden_candidates,
        "possible_tracking_pixels": parser.tiny_candidates + parser.hidden_candidates,
        "note": "Heuristic only. Image URLs are never contacted and no tracking occurs.",
    }


def inventory_email_attachments(path: str | None = None, **_: Any) -> dict[str, Any]:
    """List metadata for attachments in a local .eml file; never extract them."""
    if not path:
        raise ValueError("Provide --path to a local .eml file.")
    target = Path(path).expanduser()
    if target.is_symlink() or not target.is_file() or target.suffix.lower() != ".eml":
        raise ValueError("Provide a regular .eml file, not a folder or symbolic link.")
    try:
        if target.stat().st_size > 5 * 1024 * 1024:
            raise ValueError("Email file exceeds the 5 MiB inspection limit.")
        raw = target.read_bytes()
    except OSError as exc:
        raise ValueError(f"Could not read the email file: {exc}") from exc
    message = BytesParser(policy=policy.default).parsebytes(raw)
    attachments = []
    for part in message.walk():
        if part.is_multipart():
            continue
        if part.get_content_disposition() == "attachment" or part.get_filename():
            payload = part.get_payload(decode=True) or b""
            attachments.append({"filename_present": bool(part.get_filename()),
                                "content_type": part.get_content_type(),
                                "size_bytes": len(payload)})
    return {"attachment_count": len(attachments), "attachments": attachments,
            "subject_present": bool(message.get("Subject")),
            "note": "Attachment names and contents are not returned. Nothing is extracted or executed."}


def check_phone_number_format(number: str | None = None, **_: Any) -> dict[str, Any]:
    """Check international phone-number formatting without identifying or locating anyone."""
    if not number:
        raise ValueError("Provide --number in international format, for example +4915123456789.")
    digits = re.sub(r"[ .()\-]", "", number.strip())
    valid = bool(re.fullmatch(r"\+[1-9][0-9]{7,14}", digits))
    return {"format_valid": valid, "normalised": digits if valid else None,
            "digit_count": len(digits.lstrip("+")), "international_format": digits.startswith("+"),
            "network_access": False,
            "note": "Format only. No subscriber, carrier, active-status, or location lookup is performed."}


_COUNTRY_CALLING_CODES = {
    "+1": "North American Numbering Plan", "+7": "Russia and Kazakhstan",
    "+20": "Egypt", "+27": "South Africa", "+30": "Greece", "+31": "Netherlands",
    "+32": "Belgium", "+33": "France", "+34": "Spain", "+39": "Italy",
    "+41": "Switzerland", "+43": "Austria", "+44": "United Kingdom",
    "+45": "Denmark", "+46": "Sweden", "+47": "Norway", "+48": "Poland",
    "+49": "Germany", "+51": "Peru", "+52": "Mexico", "+55": "Brazil",
    "+61": "Australia", "+64": "New Zealand", "+81": "Japan",
    "+82": "South Korea", "+86": "China", "+91": "India",
}


def lookup_phone_country_code(number: str | None = None, **_: Any) -> dict[str, Any]:
    """Return a broad calling-code region, not a phone owner's location."""
    if not number or not number.strip().startswith("+"):
        raise ValueError("Provide an international number beginning with +.")
    digits = re.sub(r"[^0-9]", "", number)
    if not 8 <= len(digits) <= 15:
        raise ValueError("Enter a plausible international number with 8 to 15 digits.")
    match = next((code for code in sorted(_COUNTRY_CALLING_CODES, key=len, reverse=True)
                  if digits.startswith(code[1:])), None)
    return {"calling_code": match,
            "calling_code_region": _COUNTRY_CALLING_CODES.get(match, "Unknown or unlisted"),
            "note": "Calling code only. It does not reveal the subscriber's current location, identity, or carrier."}


def classify_ip_privacy(address: str | None = None, **_: Any) -> dict[str, Any]:
    """Classify IP address scope without geolocation, reverse lookup, or scanning."""
    if not address:
        raise ValueError("Provide --address with an IPv4 or IPv6 address.")
    try:
        parsed = ipaddress.ip_address(address.strip())
    except ValueError as exc:
        raise ValueError("Enter a valid IPv4 or IPv6 address.") from exc
    if parsed.is_loopback:
        scope = "loopback"
    elif parsed.is_private:
        scope = "private"
    elif parsed.is_link_local:
        scope = "link-local"
    elif parsed.is_multicast:
        scope = "multicast"
    elif parsed.is_reserved:
        scope = "reserved"
    elif parsed.is_global:
        scope = "public"
    else:
        scope = "special-purpose"
    return {"address_family": f"IPv{parsed.version}", "scope": scope,
            "is_global": parsed.is_global, "is_private": parsed.is_private,
            "is_loopback": parsed.is_loopback, "network_access": False,
            "note": "Classification only. No geolocation, person identification, or remote scan is performed."}


def audit_hosts_file(path: str | None = None, **_: Any) -> dict[str, Any]:
    """Review hosts-file overrides without resolving names or changing the file."""
    default = (r"C:\Windows\System32\drivers\etc\hosts" if platform.system() == "Windows"
               else "/etc/hosts")
    target = Path(path or default).expanduser()
    if target.is_symlink() or not target.is_file():
        raise ValueError("Provide a regular hosts file, not a folder or symbolic link.")
    try:
        if target.stat().st_size > 1024 * 1024:
            raise ValueError("Hosts file exceeds the 1 MiB inspection limit.")
        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        raise ValueError(f"Could not read hosts file: {exc}") from exc
    entries = []
    for line_number, raw in enumerate(lines, 1):
        parts = raw.split("#", 1)[0].split()
        if len(parts) < 2:
            continue
        try:
            address = ipaddress.ip_address(parts[0])
        except ValueError:
            continue
        names = [name.lower().rstrip(".") for name in parts[1:] if "." in name]
        if names and not address.is_loopback and not address.is_unspecified:
            scope = "private" if address.is_private else "public" if address.is_global else "special"
            entries.append({"line": line_number, "mapped_names": names, "address_scope": scope})
    return {"entries_reviewed": len(entries), "non_loopback_overrides": entries[:200],
            "truncated": len(entries) > 200,
            "note": "Read-only review. Non-loopback mappings may be intentional; no entries are changed."}


def audit_proxy_configuration(**_: Any) -> dict[str, Any]:
    """Report proxy variable names only, never proxy URLs or credentials."""
    names = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
             "http_proxy", "https_proxy", "all_proxy", "no_proxy")
    configured = sorted(name for name in names if os.environ.get(name))
    return {"configured_variables": configured, "proxy_configured": bool(configured),
            "values_disclosed": False,
            "note": "Proxy URLs, usernames, passwords, and bypass lists are not exposed."}


def inventory_local_listening_ports(**_: Any) -> dict[str, Any]:
    """List local Linux TCP listeners without probing remote systems or mapping processes."""
    if platform.system() != "Linux":
        return {"supported": False, "listening_ports": [],
                "note": "This check currently supports Linux /proc networking tables only."}
    entries = set()
    for filename, family in (("/proc/net/tcp", "IPv4"), ("/proc/net/tcp6", "IPv6")):
        try:
            lines = Path(filename).read_text(encoding="ascii").splitlines()[1:]
        except OSError:
            continue
        for line in lines:
            fields = line.split()
            if len(fields) < 4 or fields[3] != "0A":
                continue
            try:
                port = int(fields[1].rsplit(":", 1)[1], 16)
            except (ValueError, IndexError):
                continue
            entries.add((port, family))
    ports = [{"port": port, "family": family, "state": "LISTEN"}
             for port, family in sorted(entries)]
    return {"supported": True, "listening_ports": ports, "count": len(ports),
            "note": "Local TCP listeners only. No remote hosts, process names, or user identities are collected."}
