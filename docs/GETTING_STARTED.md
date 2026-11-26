# Getting Started

This guide helps you install Phantom Sec and open it for the first time.

## 1. What you need

- A computer running Linux (the first development platform).
- Python 3.10 or newer.
- An internet connection for the initial download and installation.
- A terminal window.

Windows and macOS are not official supported targets yet.

## 2. Download the project

Open a terminal and run:

```bash
git clone https://github.com/cybr-ghost/phantom-sec.git
cd phantom-sec
```

The first command downloads the project. The second moves your terminal into the project folder.

## 3. Create a private Python environment

Run:

```bash
python -m venv .venv
source .venv/bin/activate
```

This creates a separate Python environment for Phantom Sec, so its packages do not interfere with other projects.

When it is active, your terminal usually shows `.venv` near the start of the command line.

## 4. Install Phantom Sec

```bash
python -m pip install -e .
```

Wait for the installation to finish.

If you also want to help develop the project or run its tests, use:

```bash
python -m pip install -e ".[dev]"
```

## 5. Start Phantom Sec

```bash
phantom-sec
```

You should see the tool catalogue. Choose a tool by entering its ID. Enter `q` to quit.

You can also list the tools without opening the menu:

```bash
phantom-sec list
```

## 6. Try a safe first command

For example, show basic information about your computer:

```bash
phantom-sec run system.info
```

Or look up the DNS information for a public example domain:

```bash
phantom-sec run network.dns --domain example.com
```

## Troubleshooting

- **Command not found:** Check that the virtual environment is active. Run `source .venv/bin/activate` from the project folder.
- **Python is too old:** Install Python 3.10 or newer.
- **Installation errors:** Check your internet connection and read the error printed in the terminal.

For examples of every current command, see the [Beginner's User Guide](USER_GUIDE.md).
