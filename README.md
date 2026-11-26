# Phantom Sec

**[🔵 DOWNLOAD PHANTOM SEC](DOWNLOADS.md)** · Choose your computer and follow the graphical installation steps.

**Phantom Sec** is a free, open-source desktop toolkit for defensive security, responsible OSINT, network diagnostics, and system administration. It is licensed under the **GNU General Public License v3.0 (GPL-3.0-only)**. You can inspect, build, modify, and redistribute the source under the terms of that license.

> **Current version: 0.1.0 (early preview).** Phantom Sec is actively developed and currently includes a command-line app, a desktop interface, and 27 built-in tools. It is not a complete security suite. Preview builds are not code-signed.

## New here? Start here

1. Open the **[Downloads page](DOWNLOADS.md)**.
2. Choose the package for your operating system and processor.
3. Follow the graphical installation steps. The normal user installation does not require the terminal on supported desktop environments.
4. Read the [Beginner's user guide](docs/user-guide.md).

If a command or word is unfamiliar, check the [Beginner's glossary](docs/glossary.md).

## What can it do today?

- Show basic information about your computer, including uptime and battery status where supported.
- Create a read-only local system overview with memory, storage, process count, network interfaces, and basic firewall status.
- Check UFW/firewalld on Linux or Windows Defender Firewall profiles without changing firewall settings.
- Save a timestamped JSON report of your local system overview.
- Calculate file hashes, inspect file signatures and text structure, find duplicate files, and check permissions.
- Look up DNS information for a hostname or IP address.
- Calculate IPv4 and IPv6 subnet boundaries locally.
- Inspect URL structure without opening the URL.
- Inspect public TLS certificates and common HTTP security headers for supplied websites.
- Inspect common DNS records, public RDAP registration data, and Certificate Transparency entries.
- Save a local history of tool runs and export it as JSON or CSV.
- Save and view simple local preferences.
- Search and run tools from a desktop interface with a run-history view.

## Downloads

**[🔵 Open the official Phantom Sec Downloads page](DOWNLOADS.md)**

Published, permanent versioned packages will appear on the [GitHub Releases page](https://github.com/cybr-ghost/phantom-sec/releases). Only use packages attached to an actual release. See the downloads guide for supported systems, installation steps, and release status.

## Developer installation

This section is for people who want to work on the source code. Regular users should use the graphical packages on the [Downloads page](DOWNLOADS.md).

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

The desktop app includes live search across tool names, IDs and descriptions, category filters, contextual input fields, background execution, copyable JSON output, and local run history. The interface uses Python's built-in Tk toolkit and does not add a large GUI dependency.

## Create a system report

Run `phantom-sec report` to create a timestamped JSON overview. Choose another location with `--output`. The report contains local device information, so review it before sharing.

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

## Supported release targets

| Platform | Architecture | Package format |
|---|---|---|
| Linux | x86_64 | AppImage |
| Linux | ARM64 | Portable tar.gz |
| Windows | x64 | Installer and portable ZIP |
| Windows | ARM64 | Portable ZIP |
| macOS | Intel x86_64 | App bundle ZIP |
| macOS | Apple Silicon ARM64 | App bundle ZIP |

32-bit systems and mobile operating systems are not supported. These are automated release targets, not a claim that every build has already been tested on physical hardware. A platform should be considered available only when its package is attached to a successful release.

## Development checks

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
```

## Open source, security, and transparency

- **Source code:** [Browse the complete source on GitHub](https://github.com/cybr-ghost/phantom-sec/tree/main/src).
- **License:** [GNU GPL v3.0](LICENSE).
- **Security policy:** [Report a vulnerability privately](SECURITY.md).
- **Contributing:** [Read the contribution guide](CONTRIBUTING.md).
- **Build automation:** [Review the GitHub Actions workflows](.github/workflows).
- **Integrity:** published release assets include a `SHA256SUMS.txt` file so downloads can be checked for accidental corruption.

Phantom Sec is an early preview, provided without warranty under the GPL. Builds are not currently code-signed, so checksums verify file integrity but do not prove publisher identity.

## License

GNU GPL-3.0-only. See `LICENSE`.
