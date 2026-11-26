"""Public domain intelligence checks with bounded requests and no account access."""

from __future__ import annotations

import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import dns.exception
import dns.resolver

_DOMAIN_LABEL = re.compile(r"^(?=.{1,63}$)[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?$")
_RECORD_TYPES = ("A", "AAAA", "MX", "TXT", "NS", "SOA", "CAA")


def _normalise_domain(domain: str | None) -> str:
    if not domain:
        raise ValueError("Provide --domain with a domain name.")
    value = domain.strip().rstrip(".").encode("idna").decode("ascii").lower()
    if len(value) > 253 or "." not in value or any(
        not _DOMAIN_LABEL.fullmatch(label) for label in value.split(".")
    ):
        raise ValueError("Enter a valid public domain name, not a URL or IP address.")
    return value


def inspect_dns_records(domain: str | None = None, **_: object) -> dict[str, object]:
    """Query common DNS record types and return independent results."""
    name = _normalise_domain(domain)
    resolver = dns.resolver.Resolver()
    resolver.timeout = 3
    resolver.lifetime = 5
    records: dict[str, list[str]] = {}
    errors: dict[str, str] = {}
    for record_type in _RECORD_TYPES:
        try:
            answer = resolver.resolve(name, record_type, raise_on_no_answer=False)
            records[record_type] = [item.to_text() for item in answer] if answer.rrset else []
        except dns.resolver.NXDOMAIN:
            raise ValueError(f"The domain {name} does not exist.") from None
        except (dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.exception.Timeout) as exc:
            records[record_type] = []
            errors[record_type] = type(exc).__name__
    return {
        "domain": name,
        "records": records,
        "lookup_errors": errors,
        "record_types_checked": list(_RECORD_TYPES),
        "note": "Queries public DNS records through the configured resolver. Missing records are not automatically a security issue.",
    }


def _get_json(url: str, *, user_agent: str) -> object:
    request = Request(url, headers={
        "Accept": "application/json",
        "User-Agent": user_agent,
    })
    try:
        with urlopen(request, timeout=8) as response:
            if response.status != 200:
                raise ValueError(f"Service returned HTTP {response.status}.")
            payload = response.read(1_500_001)
    except HTTPError as exc:
        raise ValueError(f"Public data service returned HTTP {exc.code}.") from exc
    except (URLError, OSError, TimeoutError) as exc:
        raise ValueError(f"Could not reach the public data service: {exc}") from exc
    if len(payload) > 1_500_000:
        raise ValueError("The response was larger than the allowed 1.5 MB limit.")
    try:
        return json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("The public data service returned invalid JSON.") from exc


def domain_registration(domain: str | None = None, **_: object) -> dict[str, object]:
    """Retrieve public domain registration metadata from the RDAP aggregator."""
    name = _normalise_domain(domain)
    data = _get_json(
        f"https://rdap.org/domain/{quote(name, safe='.-')}",
        user_agent="PhantomSec-DomainResearch/1.0",
    )
    if not isinstance(data, dict):
        raise ValueError("The RDAP service returned an unexpected response.")
    events = [
        {"action": event.get("eventAction"), "date": event.get("eventDate")}
        for event in data.get("events", [])
        if isinstance(event, dict)
    ]
    nameservers = [
        item.get("ldhName") for item in data.get("nameservers", [])
        if isinstance(item, dict) and item.get("ldhName")
    ]
    statuses = data.get("status", [])
    return {
        "domain": name,
        "handle": data.get("handle"),
        "status": statuses if isinstance(statuses, list) else [],
        "events": events,
        "nameservers": nameservers,
        "rdap_conformance": data.get("rdapConformance", []),
        "source": "rdap.org",
        "note": "Uses public registration data. Registrant contact details may be redacted or unavailable.",
    }


def certificate_transparency_search(domain: str | None = None, **_: object) -> dict[str, object]:
    """Search public Certificate Transparency entries for a domain and its subdomains."""
    name = _normalise_domain(domain)
    data = _get_json(
        f"https://crt.sh/?q={quote('%.' + name, safe='.*-')}&output=json",
        user_agent="PhantomSec-CertificateResearch/1.0",
    )
    if not isinstance(data, list):
        raise ValueError("The certificate transparency service returned an unexpected response.")
    unique: dict[tuple[object, object], dict[str, object]] = {}
    for item in data[:5000]:
        if not isinstance(item, dict):
            continue
        key = (item.get("id"), item.get("serial_number"))
        unique[key] = {
            "id": item.get("id"),
            "common_name": item.get("common_name"),
            "name_value": item.get("name_value"),
            "issuer": item.get("issuer_name"),
            "not_before": item.get("not_before"),
            "not_after": item.get("not_after"),
        }
    entries = list(unique.values())
    return {
        "domain": name,
        "entries_returned": len(data),
        "unique_certificates": len(entries),
        "certificates": entries[:100],
        "truncated": len(entries) > 100 or len(data) > 5000,
        "source": "crt.sh (public Certificate Transparency logs)",
        "note": "Certificate issuance records are public transparency data. A listed certificate does not prove that a hostname is currently active or trustworthy.",
    }
