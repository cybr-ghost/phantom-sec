# Getting Started

This guide helps you install Phantom Sec and open it for the first time.

## 1. What you need

- Windows 10/11 or a supported Linux distribution.
- Python 3.10 or newer.
- An internet connection for the initial download and installation.
- PowerShell on Windows, or a terminal on Linux.

macOS is not an officially supported target yet.

## 2. Download the project

Open PowerShell or a terminal and run:

\`\`\`text
git clone https://github.com/cybr-ghost/phantom-sec.git
cd phantom-sec
\`\`\`

## 3. Create a private Python environment

**Windows PowerShell:**

\`\`\`powershell
py -3 -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
\`\`\`

If PowerShell blocks activation, use the environment's Python directly:

\`\`\`powershell
.\\.venv\\Scripts\\python.exe -m pip install -e .
.\\.venv\\Scripts\\phantom-sec.exe
\`\`\`

**Linux:**

\`\`\`bash
python3 -m venv .venv
source .venv/bin/activate
\`\`\`

## 4. Install Phantom Sec

With the environment active, run:

\`\`\`text
python -m pip install -e .
\`\`\`

For development and tests:

\`\`\`text
python -m pip install -e ".[dev]"
\`\`\`

## 5. Start the desktop app

\`\`\`text
phantom-sec
\`\`\`

The Phantom Sec desktop window opens. Search for a tool, select it, enter any requested value, and choose **Run tool**.

You can also launch the desktop app explicitly with \`phantom-sec gui\`, or use the terminal menu with \`phantom-sec menu\`.

## 6. Try a safe first command

\`\`\`text
phantom-sec run system.info
phantom-sec run system.overview
phantom-sec run system.battery
\`\`\`

The system overview includes local computer information, uptime, memory, storage, process count, network interface names, and firewall status. Battery information is shown when the computer exposes it.

## Troubleshooting

- **Command not found:** Check that the virtual environment is active.
- **PowerShell blocks activation:** Use the environment's Python and executable directly as shown above.
- **Desktop window does not open:** Your Python installation may be missing Tk support. Install the Tk package supplied by your Linux distribution, or use \`phantom-sec menu\` in the meantime.
- **Python is too old:** Install Python 3.10 or newer.
- **Installation errors:** Check your internet connection and read the error printed in the terminal.

For examples of every current command, see the [Beginner's User Guide](USER_GUIDE.md).
