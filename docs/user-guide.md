# Beginner's User Guide

This guide explains how to use the tools included in Phantom Sec today.

## First: check your setup

Run `phantom-sec doctor` to check that Python, the tool catalogue, and the local history folder are ready.

## Use the desktop app

Run `phantom-sec` or `phantom-sec gui` to open the graphical interface. The **Tool library** tab includes a search field that filters by tool name, ID, description, or category as you type. Select a tool to see its description and any required input, then choose **Run tool**. Results appear in the output panel. You can copy results, clear the panel, and review previous runs in **Run history**. Press `Ctrl+K` to focus the search field.

The GUI runs checks in the background so the window remains responsive. The interface uses Tk, included with many Python installations. Some Linux distributions package Tk separately.

## Open the tool list

Run:

```bash
phantom-sec list
```

To open the terminal menu, run `phantom-sec menu`. It stays open after each tool. Type `q` when you want to quit.

## Your first system overview

Run:

```bash
phantom-sec run system.overview
```

It collects basic local information about the operating system, uptime, memory, storage, process count, network interface names, and basic firewall status.

The firewall part checks UFW/firewalld on Linux or Windows Defender Firewall profiles on Windows. It only reads their status. If a check cannot confirm the status, the tool reports that limitation rather than guessing.

This is an informational snapshot, not a complete security audit. It does not scan other devices or change your computer.

## Check firewall status on its own

Run:

```bash
phantom-sec run system.firewall
```

This checks UFW/firewalld on Linux or Windows Defender Firewall profiles on Windows. It does not enable, disable, or edit firewall rules. A result of `unknown` means the status could not be confirmed.

## Save a system report

Run:

```bash
phantom-sec report
```

By default, this creates `phantom-sec-report.json` in the current folder. You can choose another location:

```bash
phantom-sec report --output ~/Documents/my-system-report.json
```

The report includes the date and time it was created. It contains information about your computer, so review it before sending it to anyone.

## Computer information

| Command | What it does |
|---|---|
| `phantom-sec run system.info` | Shows basic operating system and Python information. |
| `phantom-sec run system.uptime` | Shows uptime on Linux and Windows. |
| `phantom-sec run system.memory` | Shows memory information where supported. |
| `phantom-sec run system.battery` | Shows battery charge and status where available. |
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
| `phantom-sec run file.permissions --path ./README.md` | Shows Unix permission bits on Linux, or current-process access checks on Windows. Windows ACLs are not decoded. |

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

For more terms, see the [Glossary](glossary.md).
