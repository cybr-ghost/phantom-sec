# Beginner's User Guide

This guide explains how to use the tools included in Phantom Sec today.

## First: check your setup

Run `phantom-sec doctor` to check that Python, the tool catalogue, and the local history folder are ready.

## Open the tool list

Run:

```bash
phantom-sec list
```

To open the interactive menu, run `phantom-sec`. It stays open after each tool. Type `q` when you want to quit.

## Your first system overview

The easiest way to get a quick picture of your own computer is:

```bash
phantom-sec run system.overview
```

It collects basic local information about the operating system, uptime, memory, storage, process count, and network interface names. It may show a notice if available memory or free disk space is low.

This is an informational snapshot, not a complete security audit. It does not scan other devices or change your computer.

## Computer information

| Command | What it does |
|---|---|
| `phantom-sec run system.info` | Shows basic operating system and Python information. |
| `phantom-sec run system.uptime` | Shows how long a Linux computer has been running. |
| `phantom-sec run system.memory` | Shows memory information where supported. |
| `phantom-sec run system.process-count` | Counts running processes without collecting command lines. |
| `phantom-sec run system.environment` | Shows a small summary of the local environment. |
| `phantom-sec run system.hostname` | Shows your computer's hostname. |
| `phantom-sec run system.disk --path ~` | Shows disk space for the selected path. |

## File tools

Replace the example path with a file or folder on your computer.

| Command | What it does |
|---|---|
| `phantom-sec run file.sha256 --path ./README.md` | Calculates a SHA-256 fingerprint of a file. |
| `phantom-sec run file.metadata --path ./README.md` | Shows basic file information. |
| `phantom-sec run file.directory-size --path ./docs` | Calculates the total size of a folder. |
| `phantom-sec run file.permissions --path ./README.md` | Shows permission bits without changing them. |

## Network basics

| Command | What it does |
|---|---|
| `phantom-sec run network.interfaces` | Lists local network interface names. |
| `phantom-sec run network.dns --domain example.com` | Looks up a hostname. |
| `phantom-sec run network.reverse-dns --address 1.1.1.1` | Tries to find the hostname associated with an IP address. |

Only investigate networks and systems that you own or have permission to assess.

## Run history and exports

Phantom Sec saves a local record of tool runs.

- `phantom-sec history --limit 20` shows the latest 20 records.
- `phantom-sec export-history json --output history.json` saves history as JSON.
- `phantom-sec export-history csv --output history.csv` saves history as CSV.

History is stored at `~/.local/share/phantom-sec/phantom-sec.sqlite3`. It can include file paths and tool results. Review an export before sharing it.

## Local preferences

- `phantom-sec settings show` lists saved preferences.
- `phantom-sec settings get theme` displays the saved value for `theme`.
- `phantom-sec settings set theme dark` saves `dark` as the value for `theme`.

## Module Workshop

The Workshop can create and check a JSON description file for a future module:

```bash
phantom-sec create-module demo.sample "Sample Module" --output module.json
phantom-sec validate-module module.json
```

This checks the description only. Phantom Sec does not currently run code from community modules.

For more terms, see the [Glossary](GLOSSARY.md).
