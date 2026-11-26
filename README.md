# Phantom Sec

A modular, open-source toolkit for defensive security, responsible OSINT, network diagnostics, and system administration.

> **Developer preview: 0.1.0.** This repository contains a Python CLI, read-only local utilities, basic DNS diagnostics, a metadata-only Module Workshop, SQLite history, and report exports. It is not a finished security suite.

## Included
- Rich terminal catalogue and interactive single-module prompt
- System information, memory counters, process count, disk usage, and hostname
- File SHA-256 hashing, metadata, and directory size analysis
- Local network interface names, forward DNS, and reverse DNS
- SQLite run history and settings storage
- JSON and CSV history exports
- Module manifest template generation and validation
- pytest tests and GitHub Actions workflow

## Quick start
```bash
git clone https://github.com/cybr-ghost/phantom-sec.git
cd phantom-sec
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
phantom-sec
``

See [Installation](docs/INSTALLATION.md) and [Usage](docs/USAGE.md).

## Documentation
- [Project overview](docs/PROJECT_OVERVIEW.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Tool catalogue](docs/TOOL_CATALOGUE.md)
- [Module specification](docs/MODULE_SPECIFICATION.md)
- [Roadmap](docs/ROADMAP.md)
- [Usage](docs/USAGE.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

## Safety
Phantom Sec is intended for education, defensive security, system administration, and explicitly authorized testing. Current network tools perform basic DNS and local interface inspection only. No port scanning, exploitation, credential collection, stealth feature, or third-party plugin execution is included.

## Development
```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
``

## License
GNU GPL-3.0-only. See [LICENSE](LICENSE).
