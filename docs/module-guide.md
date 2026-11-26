# Module Guide

## What is a module?

A module is one small tool inside Phantom Sec. For example, `file.sha256` calculates a file's SHA-256 hash.

Each module has an ID, a name, and a description so the app can show it in the tool list.

## What the Workshop can do today

The Module Workshop currently supports two simple actions:

1. Create a JSON description template.
2. Check whether a JSON description follows the expected format.

Example:

```bash
phantom-sec create-module demo.sample "Sample Module" --output module.json
phantom-sec validate-module module.json
```

## What is inside a module description?

| Field | Meaning |
|---|---|
| `id` | A unique ID, such as `file.sha256`. |
| `name` | The name people see. |
| `version` | The module version. |
| `description` | A short explanation of the tool. |
| `category` | The type of tool. |
| `author` | The contributor's name or handle. |
| `entry_point` | Reserved information for a future design. It is not run. |
| `permissions` | Optional labels describing what information a module may need. |

Currently recognized permission labels are `read_system_info`, `read_local_files`, and `resolve_dns`.

## Important safety note

The current Workshop checks the JSON description only. It does not inspect code, verify who wrote it, install dependencies, or prove that a module is safe.

Phantom Sec currently supports built-in modules only. It does not execute third-party module code. Do not add automatic plugin loading.
