# Module Manifest Specification (Draft)

The current release includes built-in modules and a metadata validator only. It does not load third-party Python modules.

A JSON manifest uses these fields:

| Field | Required | Meaning |
|---|---|---|
| id | Yes | Stable unique identifier, such as `file.sha256` |
| name | Yes | Human-readable name |
| version | Yes | Module version |
| description | Yes | What the module does |
| category | Yes | Catalogue category |
| author | Yes | Contributor name or handle |
| entry_point | Yes | Reserved metadata; not executed |
| permissions | No | List of declared permission labels |

Currently recognized permission labels: `read_system_info`, `read_local_files`, and `resolve_dns`.

Manifest validation checks structure and declared permissions only. It does not inspect code, verify authorship, resolve dependencies, sandbox code, or prove a module safe. Third-party execution is deliberately disabled until a separately reviewed isolation design exists.
