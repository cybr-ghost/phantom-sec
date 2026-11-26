# Tools Available Today

This page lists the tools that are actually included in the current Phantom Sec preview. A tool appearing here means it is registered in the current built-in tool list.

## Computer information

| Tool ID | What it does |
|---|---|
| `system.info` | Basic operating system and runtime information. |
| `system.memory` | Memory counters where supported. |
| `system.process-count` | Counts running processes without collecting command lines. |
| `system.environment` | A small summary of the local environment. |
| `system.disk` | Disk usage for a selected path. |
| `system.hostname` | The local computer's hostname. |

## File information

| Tool ID | What it does |
|---|---|
| `file.sha256` | Calculates a file's SHA-256 hash. |
| `file.metadata` | Shows basic file metadata. |
| `file.directory-size` | Calculates the size of a directory. |

## Network basics

| Tool ID | What it does |
|---|---|
| `network.interfaces` | Lists local network interface names. |
| `network.dns` | Looks up a hostname. |
| `network.reverse-dns` | Looks up a hostname for an IP address when available. |

## Not included yet

The following are ideas for future versions, not features you can use today:

- A graphical desktop interface.
- A larger OSINT research collection.
- Firewall status checks.
- More advanced network diagnostics.
- A reviewed community module library.

See the [Development Plan](WHAT_WE_ARE_BUILDING.md) for the wider plan.
