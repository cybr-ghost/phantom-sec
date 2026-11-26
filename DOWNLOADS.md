# Download Phantom Sec

Welcome! This page is the easiest place to download Phantom Sec. Pick your computer below.

> **Latest build:** 26 November 2026 · Phantom Sec 0.1.0 preview · 27 built-in tools

## 1. Choose your download

### Linux (64-bit)

**[⬇️ DOWNLOAD FOR LINUX (AppImage)](https://github.com/cybr-ghost/phantom-sec/actions/runs/45826403944/artifacts/15119908365)**

File: `Phantom-Sec-x86_64.AppImage`

1. Open the download link above.
2. On the artifact page, select **Download**. GitHub may ask you to sign in.
3. Open the downloaded ZIP archive and extract it.
4. Open a terminal in the extracted folder.
5. Run these commands:

```bash
chmod +x Phantom-Sec-x86_64.AppImage
./Phantom-Sec-x86_64.AppImage
```

**Arch Linux note:** If the app reports a FUSE error, install compatibility support with `sudo pacman -S fuse2`, or launch it with:

```bash
./Phantom-Sec-x86_64.AppImage --appimage-extract-and-run
```

### Windows 10/11 (64-bit)

**[⬇️ DOWNLOAD FOR WINDOWS (Installer + Portable ZIP)](https://github.com/cybr-ghost/phantom-sec/actions/runs/45826403915/artifacts/15119508653)**

The ZIP contains both files:

- `Phantom-Sec-Setup-x64.exe` — recommended for most users. Open it and follow the setup steps.
- `Phantom-Sec-Windows-x64.zip` — portable version. Extract the ZIP, then open `Phantom-Sec.exe`.

1. Open the download link above.
2. Select **Download** on the artifact page. GitHub may ask you to sign in.
3. Extract the downloaded ZIP.
4. Choose the installer or portable version listed above.

Windows may show a SmartScreen warning because these preview builds are not code-signed. Only download them from this official repository.

## 2. Need help?

- **[Getting started guide](docs/getting-started.md)** — beginner-friendly setup instructions.
- **[Beginner's user guide](docs/user-guide.md)** — how to use the app.
- **[Latest build list](https://github.com/cybr-ghost/phantom-sec/actions)** — all automated builds.
- **[GitHub Releases](https://github.com/cybr-ghost/phantom-sec/releases)** — permanent versioned downloads when a release is published.

## Important

GitHub Actions downloads are temporary and currently expire after 30 days. If a link above has expired, open the latest successful build from the **Latest build list** and download its artifact. Versioned files published on the Releases page will not use this temporary artifact link.

Phantom Sec is an early preview. Use it only on your own devices and networks, or where you have clear permission.
