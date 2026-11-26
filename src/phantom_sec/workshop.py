"""Safe module-manifest validation. This module never imports or executes plugins."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = {"id", "name", "version", "description", "category", "author", "entry_point"}
ALLOWED_PERMISSIONS = {"read_system_info", "read_local_files", "resolve_dns"}


def validate_manifest(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"valid": False, "errors": [str(exc)]}
    errors: list[str] = []
    if not isinstance(data, dict):
        return {"valid": False, "errors": ["Manifest root must be a JSON object."]}
    missing = sorted(REQUIRED_FIELDS - data.keys())
    if missing:
        errors.append("Missing fields: " + ", ".join(missing))
    for key in ("id", "name", "version", "description", "category", "author", "entry_point"):
        if key in data and (not isinstance(data[key], str) or not data[key].strip()):
            errors.append(f"{key} must be a non-empty string.")
    permissions = data.get("permissions", [])
    if not isinstance(permissions, list) or any(not isinstance(p, str) for p in permissions):
        errors.append("permissions must be a list of strings.")
    else:
        unknown = sorted(set(permissions) - ALLOWED_PERMISSIONS)
        if unknown:
            errors.append("Unknown permissions: " + ", ".join(unknown))
    errors.append("Validation does not make a module safe. Third-party code is not executable by Phantom Sec.")
    return {"valid": not any(not item.startswith("Validation does not") for item in errors),
            "errors": errors, "module_id": data.get("id")}


def write_template(destination: Path, module_id: str, name: str) -> Path:
    """Create a JSON manifest template only; no executable plugin source is generated."""
    manifest = {
        "id": module_id,
        "name": name,
        "version": "0.1.0",
        "description": "Describe the module's purpose.",
        "category": "Uncategorized",
        "author": "Your name or handle",
        "entry_point": "not-enabled",
        "permissions": [],
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return destination
