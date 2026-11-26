# Phantom Sec

A modular, open-source toolkit for defensive security, responsible OSINT, network diagnostics, and system administration.

> **Project status:** Early planning and foundation stage. The roadmap and tool catalogue describe planned functionality; not every listed tool is implemented yet.

## Project documentation

- [Project overview](docs/PROJECT_OVERVIEW.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Development roadmap](docs/ROADMAP.md)
- [Tool catalogue](docs/TOOL_CATALOGUE.md)

## Goals

- Organize useful system and defensive security tools in one application.
- Use a modular architecture with clear metadata and documentation.
- Make permissions and expected actions visible before tools run.
- Support responsible community contributions through review and testing.

## Safety

Phantom Sec is intended for education, defensive security, system administration, and authorized testing. Do not use it to access systems without permission, collect credentials, deploy malware, conduct covert surveillance, or target private individuals. Network testing must be limited to systems you own or are explicitly authorized to assess.

Community modules must be reviewed before use. Untrusted modules must never execute automatically.

## Planned technology

- Python
- Rich terminal interface
- SQLite for local settings and metadata
- pytest for testing
- GitHub Actions for automation
- Linux as the first development target

## Contributing

Contribution guidance will be added as the project moves from planning into implementation. Please open an issue before starting a large change so its scope can be discussed.

## License

Licensed under the GNU General Public License v3.0. See [LICENSE](LICENSE).
