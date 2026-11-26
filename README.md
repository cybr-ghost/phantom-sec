# Phantom Sec

**Phantom Sec** is an open-source project for learning about defensive security, responsible OSINT, network basics, and looking after your own computer.

> **Current version: 0.1.0 (early preview).** Phantom Sec is still being built. It currently has a small command-line app and 12 built-in tools. It is not a complete security suite.

## New here? Start here

You do not need to know everything about cybersecurity to explore this project.

1. Read the [Getting Started guide](docs/GETTING_STARTED.md).
2. Follow the installation steps.
3. Open the app by running `phantom-sec`.
4. Choose a tool from the list, or read the [Beginner's User Guide](docs/USER_GUIDE.md).

If a command or word is unfamiliar, check the [Glossary](docs/GLOSSARY.md).

## What can it do today?

- Show basic information about your computer.
- Show memory and disk usage.
- Count running processes without collecting their command lines.
- Calculate a file's SHA-256 hash and show basic file details.
- Show local network interface names.
- Look up DNS information for a hostname or IP address.
- Save a local history of tool runs.
- Export that history as JSON or CSV.

## Install it

You need Python 3.10 or newer. Linux is the first development platform.

```bash
git clone https://github.com/cybr-ghost/phantom-sec.git
cd phantom-sec
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
phantom-sec
```

For development and tests, install the extra tools with `python -m pip install -e ".[dev]"`.

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

Use Phantom Sec only on your own devices and networks, or where you have clear permission. Current network tools are basic DNS lookups and local interface information. The project does not include exploitation, password collection, stealth features, or automatic execution of third-party modules.

## Development checks

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
```

## License

GNU GPL-3.0-only. See [LICENSE](LICENSE).
