# Phantom Sec

**Phantom Sec** is an open-source project for learning about defensive security, responsible OSINT, network basics, and looking after your own computer.

> **Current version: 0.1.0 (early preview).** Phantom Sec is still being built. It currently includes a command-line app, a desktop interface, and 24 built-in tools. It is not a complete security suite.

## New here? Start here

1. Read the [Getting started guide](docs/getting-started.md).
2. Follow the installation steps.
3. Check your setup with `phantom-sec doctor`.
4. Open the desktop app with `phantom-sec gui`.
5. Read the [Beginner's user guide](docs/user-guide.md).

If a command or word is unfamiliar, check the [Beginner's glossary](docs/glossary.md).

## What can it do today?

- Show basic information about your computer, including uptime and battery status where supported.
- Create a read-only local system overview with memory, storage, process count, network interfaces, and basic firewall status.
- Check UFW/firewalld on Linux or Windows Defender Firewall profiles without changing firewall settings.
- Save a timestamped JSON report of your local system overview.
- Calculate a file's SHA-256 hash, inspect file details, and check permission bits.
- Look up DNS information for a hostname or IP address.
- Calculate IPv4 and IPv6 subnet boundaries locally.
- Inspect URL structure without opening the URL.
- Inspect public TLS certificates and common HTTP security headers for supplied websites.
- Inspect common DNS records, public RDAP registration data, and Certificate Transparency entries.
- Save a local history of tool runs and export it as JSON or CSV.
- Save and view simple local preferences.
- Search and run tools from a desktop interface with a run-history view.

## Install it

Choose the download for your operating system from the latest successful build in the [GitHub Actions tab](https://github.com/cybr-ghost/phantom-sec/actions). Versioned releases will also be published on the [Releases page](https://github.com/cybr-ghost/phantom-sec/releases).

### Linux (x86_64)

1. Download `Phantom-Sec-x86_64.AppImage` from the **Build Linux AppImage** workflow artifact.
2. Open a terminal in the download folder.
3. Run:

```bash
chmod +x Phantom-Sec-x86_64.AppImage
./Phantom-Sec-x86_64.AppImage
```

The AppImage contains the app runtime and Python dependencies. If it reports a FUSE error on Arch Linux, install compatibility support with `sudo pacman -S fuse2`, or run it with `./Phantom-Sec-x86_64.AppImage --appimage-extract-and-run`.

### Windows 10/11 (x64)

1. Download `Phantom-Sec-Setup-x64.exe` for a normal installation, or `Phantom-Sec-Windows-x64.zip` for the portable version, from the **Build Windows** workflow artifact.
2. For the installer, open the EXE and follow the setup steps. For the portable version, extract the ZIP and open `Phantom-Sec.exe`.
3. Launch **Phantom Sec** from the Start menu or desktop shortcut (installer), or from the extracted folder (portable).

Windows may show a SmartScreen warning because early project builds are not code-signed. Only download builds from this official repository and inspect the release notes/checksums before running them.

### Developer installation (Linux or Windows)

Python 3.10 or newer is required. Clone the project and install it in a virtual environment:

```bash
git clone https://github.com/cybr-ghost/phantom-sec.git
cd phantom-sec
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
phantom-sec doctor
phantom-sec gui
```

On Windows PowerShell, use `py -3 -m venv .venv`, then `.\\.venv\\Scripts\\Activate.ps1`, then `python -m pip install -e .` and `phantom-sec gui`.

For development and tests, install the extra tools with `python -m pip install -e ".[dev]"`.

## Desktop interface

Launch the graphical desktop app with `phantom-sec gui`. It includes live search across tool names, IDs and descriptions, category filters, contextual input fields, background execution, copyable JSON output, and local run history. The interface uses Python's built-in Tk toolkit and does not add a large GUI dependency.

## Create a system report

Run:

```bash
phantom-sec report
```

This creates `phantom-sec-report.json` in the current folder. Choose another location with `--output`. The report contains local device information, so review it before sharing.

## Project guides

- [Getting started](docs/getting-started.md)
- [Beginner's user guide](docs/user-guide.md)
- [Tools available today](docs/tools-today.md)
- [Project overview](docs/project-guide.md)
- [How the project works](docs/how-it-works.md)
- [Module guide](docs/module-guide.md)
- [Development roadmap](docs/roadmap.md)
- [Beginner's glossary](docs/glossary.md)
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

GNU GPL-3.0-only. See `LICENSE`.
