# Phantom Sec

**Phantom Sec** is an open-source project for learning about defensive security, responsible OSINT, network basics, and looking after your own computer.

> **Current version: 0.1.0 (early preview).** Phantom Sec is still being built. It currently has a small command-line app and 15 built-in tools. It is not a complete security suite.

## New here? Start here

1. Read the [Getting Started guide](docs/GETTING_STARTED.md).
2. Follow the installation steps.
3. Check your setup with `phantom-sec doctor`.
4. Open the app by running `phantom-sec`.
5. Choose tools from the menu, or read the [Beginner's User Guide](docs/USER_GUIDE.md).

If a command or word is unfamiliar, check the [Glossary](docs/GLOSSARY.md).

## What can it do today?

- Show basic information about your computer, including Linux uptime.
- Create a read-only local system overview with memory, storage, process count, and network interface information.
- Save a timestamped JSON report of your local system overview.
- Calculate a file's SHA-256 hash, inspect file details, and check permission bits.
- Look up DNS information for a hostname or IP address.
- Save a local history of tool runs and export it as JSON or CSV.
- Save and view simple local preferences.

## Install it

You need Python 3.10 or newer. Linux is the first development platform.

```bash
git clone https://github.com/cybr-ghost/phantom-sec.git
cd phantom-sec
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
phantom-sec doctor
phantom-sec
```

For development and tests, install the extra tools with `python -m pip install -e ".[dev]"`.

## Create a system report

Run:

```bash
phantom-sec report
```

This creates `phantom-sec-report.json` in the current folder. Choose another location with `--output`. The report contains local device information, so review it before sharing.

## Project guides

- [Getting Started](docs/GETTING_STARTED.md)
- [Beginner's User Guide](docs/USER_GUIDE.md)
- [Tools available today](docs/TOOLS_TODAY.md)
- [Project overview](docs/PROJECT_GUIDE.md)
- [How the project works](docs/HOW_IT_WORKS.md)
- [Module guide](docs/MODULE_GUIDE.md)
- [Development plan](docs/WHAT_WE_ARE_BUILDING.md)
- [Glossary](docs/GLOSSARY.md)
- [How to contribute](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

## Safety

Use Phantom Sec only on your own devices and networks, or where you have clear permission. Current network tools are basic DNS lookups and local interface information. The system overview is informational, not a full security audit. Third-party module code is not executed.

## Development checks

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
```

## License

GNU GPL-3.0-only. See [LICENSE](LICENSE).
