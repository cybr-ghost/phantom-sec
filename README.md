# Phantom Sec

A modular, open-source toolkit for defensive security, responsible OSINT, network diagnostics, and system administration.

> **Status: early developer preview (0.1.0).** The repository now contains a working Python CLI foundation and a small set of read-only built-in utilities. The broader catalogue remains a roadmap, not a claim of completed features.

## Features in this preview
- Rich terminal catalogue and command-line interface
- Built-in module registry
- Basic system and disk information
- Local hostname information
- SHA-256 file hashing and directory size analysis
- DNS hostname lookup through the system resolver
- JSON module-manifest validation (no third-party code execution)
- pytest tests and GitHub Actions workflow

## Quick start
```bash
git clone https://github.com/cybr-ghost/phantom-sec.git
cd phantom-sec
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
phantom-sec
``

See [Installation](docs/INSTALLATION.md) and [Usage](docs/USAGE.md).

## Documentation
- [Project overview](docs/PROJECT_OVERVIEW.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Tool catalogue](docs/TOOL_CATALOGUE.md)
- [Module specification](docs/MODULE_SPECIFICATION.md)
- [Roadmap](docs/ROADMAP.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

## Safety
Phantom Sec is intended for education, defensive security, system administration, and explicitly authorized testing. Network testing must be limited to systems you own or are authorized to assess. The current preview contains no port scanner, exploit framework, credential collection, stealth feature, or third-party plugin execution.

## Development
```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
``

## License
GNU GPL-3.0-only. See [LICENSE](LICENSE).
