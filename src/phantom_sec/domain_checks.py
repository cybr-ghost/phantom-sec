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



def _assess_spf(records: list[str]) -> dict[str, object]:
    """Summarise SPF TXT record count and its terminal all mechanism."""
    if not records:
        return {"status": "missing", "record_count": 0, "all_mechanism": None,
                "assessment": "No SPF record was found."}
    if len(records) != 1:
        return {"status": "multiple", "record_count": len(records), "all_mechanism": None,
                "assessment": "Multiple SPF records were found; publish one SPF record per domain."}
    mechanisms = [part.lower() for part in records[0].split()]
    terminal = next((part for part in reversed(mechanisms)
                     if part in {"-all", "~all", "?all", "+all", "all"}), None)
    descriptions = {
        "-all": "The record ends with a hard-fail policy.",
        "~all": "The record ends with a soft-fail policy.",
        "?all": "The record ends with a neutral policy.",
        "+all": "The record explicitly permits all senders and is overly permissive.",
        "all": "The record uses an unqualified all mechanism.",
    }
    return {
        "status": "configured",
        "record_count": 1,
        "all_mechanism": terminal,
        "assessment": descriptions.get(terminal, "No terminal all mechanism was found."),
    }


def _assess_dmarc(records: list[str]) -> dict[str, object]:
    """Summarise DMARC policy without exposing reporting mailbox addresses."""
    if not records:
        return {"status": "missing", "record_count": 0, "policy": None,
                "assessment": "No DMARC record was found."}
    if len(records) != 1:
        return {"status": "multiple", "record_count": len(records), "policy": None,
                "assessment": "Multiple DMARC records were found; publish one DMARC record."}
    tags = {}
    for part in records[0].split(";"):
        if "=" in part:
            key, value = part.split("=", 1)
            tags[key.strip().lower()] = value.strip().lower()
    policy = tags.get("p")
    descriptions = {
        "none": "Monitoring policy only; messages are not requested to be quarantined or rejected.",
        "quarantine": "The policy requests suspicious messages to be quarantined.",
        "reject": "The policy requests failing messages to be rejected.",
    }
    if tags.get("v") != "dmarc1" or policy not in descriptions:
        return {"status": "invalid", "record_count": 1, "policy": policy,
                "assessment": "The DMARC record is missing a valid version or policy tag."}
    return {"status": "configured", "record_count": 1, "policy": policy,
            "assessment": descriptions[policy]}


def email_domain_posture(domain: str | None = None, **_: object) -> dict[str, object]:
    """Check public MX, SPF, and DMARC DNS configuration for an email domain."""
    name = _normalise_domain(domain)
    resolver = dns.resolver.Resolver()
    resolver.timeout = 3
    resolver.lifetime = 5

    def query_txt(owner: str) -> list[str]:
        try:
            answer = resolver.resolve(owner, "TXT", raise_on_no_answer=False)
            if not answer.rrset:
                return []
            values = []
            for item in answer:
                parts = getattr(item, "strings", ())
                if parts:
                    values.append(b"".join(parts).decode("utf-8", "replace"))
                else:
                    values.append(item.to_text().strip('"'))
            return values
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer,
                dns.resolver.NoNameservers, dns.exception.Timeout):
            return []

    try:
        mx_answer = resolver.resolve(name, "MX", raise_on_no_answer=False)
        mx_records = [item.to_text() for item in mx_answer] if mx_answer.rrset else []
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer,
            dns.resolver.NoNameservers, dns.exception.Timeout):
        mx_records = []

    txt_records = query_txt(name)
    dmarc_records = query_txt(f"_dmarc.{name}")
    spf = _assess_spf([record for record in txt_records
                       if record.strip().lower().startswith("v=spf1")])
    dmarc = _assess_dmarc([record for record in dmarc_records
                           if record.strip().lower().startswith("v=dmarc1")])
    recommendations = []
    if spf["status"] == "missing":
        recommendations.append("Add an SPF record if this domain sends email.")
    elif spf["status"] == "multiple":
        recommendations.append("Combine SPF rules into a single SPF record.")
    elif spf["all_mechanism"] in {"+all", "all", "?all"}:
        recommendations.append("Review the SPF all mechanism; the current policy is permissive or neutral.")
    if dmarc["status"] == "missing":
        recommendations.append("Add a DMARC record and begin with a policy appropriate to your mail setup.")
    elif dmarc["status"] in {"multiple", "invalid"}:
        recommendations.append("Correct the DMARC record so there is exactly one valid policy.")
    elif dmarc["policy"] == "none":
        recommendations.append("Review DMARC reports before considering a stricter enforcement policy.")
    if not mx_records:
        recommendations.append("No MX record was found; confirm whether this domain is intended to receive email.")
    return {
        "domain": name,
        "mx_records": mx_records,
        "spf": spf,
        "dmarc": dmarc,
        "recommendations": recommendations,
        "source": "Public DNS records",
        "note": "This is a DNS configuration snapshot, not a mail-delivery test or a guarantee against spoofing. DNS answers may be cached or delayed.",
    }
