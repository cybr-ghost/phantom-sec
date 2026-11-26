# Beginner's User Guide

This guide explains how to use the tools that are included in Phantom Sec today.

## First: check your setup\n\nRun `phantom-sec doctor` to check that Python, the tool catalogue, and the local history folder are ready.\n\n## First: how commands work

A command starts with `phantom-sec`. The word after it tells the app what you want to do.

For example:

```bash
phantom-sec list
```

This displays the built-in tool list. The interactive menu also stays open after each tool, so you can run several checks before typing `q` to quit.

To run one tool, use `run` followed by its ID:

```bash
phantom-sec run system.info
```

Some tools need extra information. These are called options. For example, a DNS lookup needs a domain:

```bash
phantom-sec run network.dns --domain example.com
```

## Computer information

| Command | What it does |
|---|---|
| `phantom-sec run system.info` | Shows basic operating system and Python information. |
| `phantom-sec run system.memory` | Shows memory information where supported. |
| `phantom-sec run system.process-count` | Counts running processes. It does not collect their command lines. |
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

These tools are designed to read information, not change your files.

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

Phantom Sec can save small preferences on your computer:

- `phantom-sec settings show` lists saved preferences.
- `phantom-sec settings get theme` displays the saved value for `theme`.
- `phantom-sec settings set theme dark` saves `dark` as the value for `theme`.

These settings stay in the local Phantom Sec database. No account or cloud sync is used.

## Module Workshop

The Workshop can create and check a JSON description file for a future module:

```bash
phantom-sec create-module demo.sample "Sample Module" --output module.json
phantom-sec validate-module module.json
```

Important: this checks the description only. Phantom Sec does not currently run code from community modules.

## Need help with a term?

See the [Glossary](GLOSSARY.md) or return to [Getting Started](GETTING_STARTED.md).
