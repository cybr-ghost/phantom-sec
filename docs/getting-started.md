# Getting Started

This guide explains the simplest way to install Phantom Sec, plus the developer setup if you want to work on its source code.

## 1. Choose your download

Open the [GitHub Actions page](https://github.com/cybr-ghost/phantom-sec/actions) and select the latest successful build for your operating system. Open its **Artifacts** section and download the matching package. Artifacts are temporary during the early preview; tagged releases will also publish permanent downloads on the [Releases page](https://github.com/cybr-ghost/phantom-sec/releases).

- **Linux x86_64:** `Phantom-Sec-x86_64.AppImage`
- **Windows 10/11 x64 installer:** `Phantom-Sec-Setup-x64.exe`
- **Windows 10/11 x64 portable:** `Phantom-Sec-Windows-x64.zip`

## 2. Install on Linux

1. Download the AppImage.
2. Open a terminal in the folder where it was downloaded.
3. Run:

```bash
chmod +x Phantom-Sec-x86_64.AppImage
./Phantom-Sec-x86_64.AppImage
```

If Arch Linux reports a FUSE compatibility error, run `sudo pacman -S fuse2` and try again. Alternatively, use `./Phantom-Sec-x86_64.AppImage --appimage-extract-and-run`.

## 3. Install on Windows

**Normal installation:** download and open `Phantom-Sec-Setup-x64.exe`, follow the setup wizard, then launch Phantom Sec from the Start menu.

**Portable version:** download `Phantom-Sec-Windows-x64.zip`, extract it, and double-click `Phantom-Sec.exe`. No setup wizard is needed.

Early builds may show a Microsoft SmartScreen warning because the installer is not code-signed yet. Only use packages downloaded from the official Phantom Sec GitHub repository.

## 4. Developer installation (optional)

You only need this if you want to edit the source code or run the CLI directly. Python 3.10 or newer is required.

**Linux:**

```bash
git clone https://github.com/cybr-ghost/phantom-sec.git
cd phantom-sec
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
phantom-sec doctor
phantom-sec gui
```

**Windows PowerShell:**

```powershell
git clone https://github.com/cybr-ghost/phantom-sec.git
cd phantom-sec
py -3 -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -e .
phantom-sec doctor
phantom-sec gui
```

If PowerShell blocks activation, use the environment's executable directly:

```powershell
.\\.venv\\Scripts\\python.exe -m pip install -e .
.\\.venv\\Scripts\\phantom-sec.exe gui
```

## 5. First launch

The desktop app opens to the dashboard. Choose **Tool library**, search for a tool, select it, enter any requested value, and choose **Run tool**. Start with read-only tools such as System Overview or File SHA-256.

## Troubleshooting

- **Linux says permission denied:** run `chmod +x Phantom-Sec-x86_64.AppImage` in the download folder.
- **Linux reports FUSE is missing:** install `fuse2` on Arch, or use `--appimage-extract-and-run`.
- **Windows SmartScreen appears:** early builds are not code-signed. Verify the download came from the official repository before proceeding.
- **Desktop app does not open:** use the developer installation and check whether your operating system has desktop/Tk support.
- **CLI says command not found:** this applies to the developer install; activate the virtual environment first.

For help with individual tools, see the [Beginner's User Guide](user-guide.md).
