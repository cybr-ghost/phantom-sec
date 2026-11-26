**Phantom Sec downloads**

Free desktop downloads for supported 64-bit computers. Choose your operating system below. Official packages will be linked from the GitHub Releases page.

**[🔵 OPEN OFFICIAL DOWNLOADS](https://github.com/cybr-ghost/phantom-sec/releases)**

The Releases page is the only official place to get published installers. Choose the newest release, then select the file matching your computer.

## Choose your download

| Your computer | File to choose | What happens next |
|---|---|---|
| Windows 10/11, Intel or AMD 64-bit | [Phantom-Sec-Setup-x64.exe](https://github.com/cybr-ghost/phantom-sec/releases) | Opens a normal setup wizard |
| Windows ARM64 | [Phantom-Sec-Windows-arm64.zip](https://github.com/cybr-ghost/phantom-sec/releases) | Extract the folder and open Phantom-Sec.exe |
| Linux, Intel or AMD 64-bit | [Phantom-Sec-linux-x86_64.AppImage](https://github.com/cybr-ghost/phantom-sec/releases) | Allow the file to run in its Properties, then double-click it |
| Linux ARM64 | [Phantom-Sec-linux-arm64.tar.gz](https://github.com/cybr-ghost/phantom-sec/releases) | Extract it, allow the app file to run in Properties, then double-click it |
| Mac with Intel processor | [Phantom-Sec-macos-x64.zip](https://github.com/cybr-ghost/phantom-sec/releases) | Open the ZIP, then move Phantom Sec to Applications |
| Mac with Apple Silicon (M1, M2, M3, M4) | [Phantom-Sec-macos-arm64.zip](https://github.com/cybr-ghost/phantom-sec/releases) | Open the ZIP, then move Phantom Sec to Applications |

**Not sure which processor you have?** On Windows, open Settings → System → About and look at System type. On macOS, choose Apple menu → About This Mac. On Linux, check Settings → About.

## Install without using the terminal

### Windows x64

1. Open the official [Releases page](https://github.com/cybr-ghost/phantom-sec/releases).
2. Download `Phantom-Sec-Setup-x64.exe`.
3. Open the downloaded file.
4. Follow the setup wizard. You can then launch Phantom Sec from the Start menu.

### Windows ARM64

1. Download `Phantom-Sec-Windows-arm64.zip` from the official release.
2. In File Explorer, right-click the ZIP and choose **Extract All**.
3. Open the extracted folder and double-click `Phantom-Sec.exe`.

This is a portable version, so it does not add a traditional setup wizard.

### Linux x86_64

1. Download `Phantom-Sec-linux-x86_64.AppImage`.
2. In your file manager, right-click the file and open **Properties**.
3. Find **Permissions** and enable **Allow executing file as a program** (the wording can vary by desktop).
4. Close Properties and double-click the AppImage.

If your desktop offers an **Execute** option when opening the file, choose that.

### Linux ARM64

1. Download `Phantom-Sec-linux-arm64.tar.gz`.
2. Open the archive and choose **Extract**.
3. In the extracted folder, right-click `phantom-sec` and open **Properties**.
4. Under **Permissions**, enable the option that allows the file to run as a program.
5. Double-click `phantom-sec`.

This is a portable application archive, not a traditional graphical installer.

### macOS

1. Download the ZIP that matches your Mac's processor.
2. Double-click the ZIP to extract it.
3. Drag **Phantom Sec.app** into **Applications**.
4. Open it from Applications.

Preview builds are not signed or notarized yet, so macOS may show a security warning. Only use files from the official Releases page.

## Downloads and release status

**[🔵 VIEW ALL OFFICIAL RELEASES](https://github.com/cybr-ghost/phantom-sec/releases)**

Automated packaging is configured for all six 64-bit desktop targets above. A package is available only after its build succeeds and the file appears in a published release. Until the first release is published, workflow test artifacts are temporary and may expire.

Every published release is intended to include `SHA256SUMS.txt`. This can help check that a download was not accidentally corrupted. It does not prove the identity of the publisher.

## Trust and transparency

- Phantom Sec is an early preview, not a certified security product.
- The source code and build workflows can be reviewed in this repository.
- Releases are built by GitHub Actions from tagged source code.
- Preview packages are not currently code-signed or notarized.
- Download only from the official [GitHub Releases page](https://github.com/cybr-ghost/phantom-sec/releases).

[View the source code](https://github.com/cybr-ghost/phantom-sec/tree/main/src) · [Read the license](LICENSE) · [Security policy](SECURITY.md) · [Getting started](docs/getting-started.md)
