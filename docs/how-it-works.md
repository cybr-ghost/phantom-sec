# How Phantom Sec Works

Phantom Sec is split into smaller Python files. Each file has a clear job, which makes the project easier to understand and maintain.

## Main parts

- **Command line (`cli.py`):** Reads commands and displays results.
- **Tool catalogue (`modules.py`):** Registers built-in tools and runs the selected one.
- **Computer checks (`computer_checks.py`):** Reads basic local system information.
- **Network checks (`network_checks.py`):** Provides local interface information and basic DNS helpers.
- **History (`local_history.py`):** Saves tool-run history and settings in a local SQLite database.
- **Exports (`export_tools.py`):** Exports saved results.
- **Module Workshop (`module_workshop.py`):** Creates and checks JSON descriptions for possible future modules.

## What happens when you run a tool?

1. You enter a command or choose a tool in the menu.
2. Phantom Sec finds the selected built-in tool.
3. The tool performs its supported task.
4. The result is displayed in your terminal or desktop app.
5. The run is saved in local history.

## System overview

The `system.overview` tool combines several existing read-only checks into one local snapshot. It does not scan the network, change system settings, or inspect process command lines.

## Module Workshop

The Workshop checks module description files. It does not execute third-party code. A valid description does not prove that future code is safe.

## Technology

- Python for the application.
- Rich for readable terminal output.
- SQLite for local history and settings.
- Tk for the desktop interface.
- pytest for tests.
- GitHub Actions for automated project checks.
