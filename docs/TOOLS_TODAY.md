# Tools Available Today

This page lists the tools included in the current Phantom Sec preview. Use `phantom-sec gui` to search and launch them from the desktop interface.

## Computer information

| Tool ID | What it does |
|---|---|
| `system.info` | Basic operating system and runtime information. |
| `system.uptime` | Shows how long a Linux computer has been running. |
| `system.overview` | Combines local system, uptime, memory, storage, process-count, interface, and basic firewall information into one read-only snapshot. |
| `system.firewall` | Checks basic UFW and firewalld status on Linux without changing settings. |
| `system.memory` | Memory counters on supported systems. |
| `system.battery` | Read battery charge and charging status where available. |
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

The firewall check currently supports UFW and firewalld on Linux. If neither is detected, it does not conclude that the computer has no firewall. Other firewall systems may be active.

The system overview is a quick informational snapshot, not a security audit. It does not scan networks, change settings, inspect process command lines, or claim that a device is secure.

A graphical interface, broader OSINT helpers, and a reviewed community module process are not included yet.
