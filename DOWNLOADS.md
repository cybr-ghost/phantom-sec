# Phantom Sec downloads

Phantom Sec is free and open source under the **GNU GPL v3.0**. This page explains where official builds come from and which package is right for your computer.

## Official downloads

**[Open the official GitHub Releases page](https://github.com/cybr-ghost/phantom-sec/releases)**

Choose the newest version and download the file matching your operating system and processor. Releases are permanent versioned downloads. Avoid third-party download sites and unofficial mirrors.

> **Release status:** automated release packaging is now configured. The first permanent release will appear on the Releases page after the release builds pass. Until then, GitHub Actions artifacts are temporary test builds and expire.

## Which file should I choose?

| Your computer | Package to look for |
|---|---|
| Linux PC, Intel or AMD 64-bit | `Phantom-Sec-linux-x86_64.AppImage` |
| Linux ARM64 device | `Phantom-Sec-linux-arm64.tar.gz` |
| Windows 10/11, Intel or AMD 64-bit | `Phantom-Sec-Setup-x64.exe` or `Phantom-Sec-Windows-x64.zip` |
| Windows ARM64 device | `Phantom-Sec-Windows-arm64.zip` |
| Mac with Intel processor | `Phantom-Sec-macos-x64.zip` |
| Mac with Apple Silicon (M1/M2/M3/M4) | `Phantom-Sec-macos-arm64.zip` |

**32-bit Windows and Linux are not currently supported.** Android and iOS are not supported because Phantom Sec is currently a desktop application.

The platform packages above are release targets. Treat a package as available only when its matching file is actually attached to a published release.

## Beginner installation

### Linux x86_64

1. Download the AppImage from the official release.
2. Open a terminal in your Downloads folder.
3. Make the file executable:

```bash
chmod +x Phantom-Sec-linux-x86_64.AppImage
```

4. Start it:

```bash
./Phantom-Sec-linux-x86_64.AppImage
```

On Arch Linux, if the system reports a FUSE compatibility error, install `fuse2` or use the AppImage's extraction-and-run option.

### Linux ARM64

1. Download and extract `Phantom-Sec-linux-arm64.tar.gz`.
2. Open a terminal in the extracted folder.
3. Run `chmod +x phantom-sec`, then `./phantom-sec`.

This is a portable executable archive, not an AppImage.

### Windows x64

- **Installer:** download `Phantom-Sec-Setup-x64.exe`, open it, and follow the setup wizard.
- **Portable:** extract `Phantom-Sec-Windows-x64.zip` and open `Phantom-Sec.exe`.

### Windows ARM64

Extract `Phantom-Sec-Windows-arm64.zip` and open `Phantom-Sec.exe`. This preview package is portable and does not include an installer.

### macOS

1. Download the ZIP matching your Mac's processor.
2. Open the ZIP to extract `Phantom Sec.app`.
3. Move the app to Applications if you want.
4. Open it from Finder.

Preview builds are not notarized or code-signed yet. macOS may display a security warning. Only use packages downloaded from the official GitHub Releases page.

## Verify a download

Each release includes `SHA256SUMS.txt`. A SHA-256 checksum can confirm that your downloaded file matches the file published in that release. It does **not** prove who built or signed the file.

Linux/macOS:

```bash
sha256sum -c SHA256SUMS.txt
```

Windows PowerShell:

```powershell
Get-FileHash .\Phantom-Sec-Setup-x64.exe -Algorithm SHA256
```

Compare the displayed hash with the matching line in `SHA256SUMS.txt`.

## Inspect the source before installing

- [Browse the source code](https://github.com/cybr-ghost/phantom-sec/tree/main/src)
- [Read the GPL-3.0 license](LICENSE)
- [Review build workflows](.github/workflows)
- [Read the security policy](SECURITY.md)
- [Read the project overview](docs/project-guide.md)

You can also build Phantom Sec yourself by following the [developer installation instructions](README.md#install-it).

## Transparency notes

- The project is an early preview, not a certified security product.
- The app is not currently code-signed or notarized.
- Release packages are built by GitHub Actions from tagged source code.
- Published releases include generated release notes and SHA-256 checksums.
- Use the tool only on devices and networks you own or are authorized to assess.
