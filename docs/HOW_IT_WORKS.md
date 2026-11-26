# How Phantom Sec Works

This page gives a simple overview of how the current project is organized.

## The basic idea

Phantom Sec is split into smaller Python files. Each file has a job, which makes the project easier to understand and maintain.

## Main parts

- **Command line (`cli.py`):** Reads the command you enter and shows the result.
- **Tool list (`modules.py`):** Keeps track of the built-in tools and starts the selected one.
- **System tools (`system_tools.py`):** Reads basic information from the local computer.
- **Network tools (`network_tools.py`):** Provides basic local interface and DNS helpers.
- **History (`storage.py`):** Saves tool-run history and settings in a local SQLite database.
- **Reports (`reports.py`):** Exports saved results.
- **Workshop (`workshop.py`):** Creates and checks JSON descriptions for possible future modules.

## What happens when you run a tool?

1. You enter a command or choose a tool in the menu.
2. Phantom Sec checks which built-in tool you selected.
3. The tool performs its current supported task.
4. The result is shown in your terminal.
5. The run is saved in local history.

## A note about the Module Workshop

The Workshop currently checks module description files. It does not inspect or safely isolate Python code, and it does not execute third-party modules.

Checking a description file does not prove that code is safe. Automatic third-party code execution is disabled.

## Technology used

- Python for the application.
- Rich for readable terminal output.
- SQLite for local history and settings.
- pytest for tests.
- GitHub Actions for automated project checks.
