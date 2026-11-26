# Contributing to Phantom Sec

Thanks for considering a contribution.

## Before starting
- Open an issue for substantial changes so the scope can be discussed.
- Keep changes focused and document user-visible behavior.
- Never submit credentials, private data, malware, or tools for unauthorized access.

## Development setup
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
ruff check .
``

## Module contributions
At this stage, Phantom Sec supports built-in modules only. The Module Workshop validates JSON metadata but does not execute third-party code. Do not add dynamic plugin loading or automatic installation. Every proposed module needs a clear purpose, permissions, tests, and documentation.

## Pull requests
Explain the problem, changes, testing performed, and any platform limitations.
