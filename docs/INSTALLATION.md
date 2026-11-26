# Installation

## Requirements
- Python 3.10 or newer
- Linux is the initial target; other platforms may work but are not yet officially supported.

## Install from a clone
```bash
git clone https://github.com/cybr-ghost/phantom-sec.git
cd phantom-sec
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
``

## Run
```bash
phantom-sec
phantom-sec list
phantom-sec run system.info
phantom-sec run network.dns --domain example.com
phantom-sec run file.sha256 --path ./README.md
``

On Windows PowerShell, activate the environment with `.venv\\Scripts\\Activate.ps1`. Windows is not yet a supported release target.

## Development checks
```bash
pytest
ruff check .
``
