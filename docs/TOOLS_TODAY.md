# Tools Available Today

This page lists the tools included in the current Phantom Sec preview.

## Computer information

| Tool ID | What it does |
|---|---|
| `system.info` | Basic operating system and runtime information. |
| `system.uptime` | Shows how long a Linux computer has been running. |
| `system.overview` | Combines local system, uptime, memory, storage, process-count, and interface information into one read-only snapshot. |
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
| `file.permissions` | Shows permission bits for a local file or folder without changing them. |

## Network basics

| Tool ID | What it does |
|---|---|
| `network.interfaces` | Lists local network interface names. |
| `network.dns` | Looks up a hostname. |
| `network.reverse-dns` | Looks up a hostname for an IP address when available. |

## Important limits

The system overview is a quick informational snapshot, not a security audit. It does not scan networks, change settings, inspect process command lines, or claim that a device is secure.

A graphical interface, firewall status checks, broader OSINT helpers, and a reviewed community module process are not included yet.
