"""Read-only local file inspection helpers."""

from __future__ import annotations

import hashlib
import math
import stat
import tarfile
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any


_SIGNATURES = (
    (b"\x7fELF", "ELF executable or shared object"),
    (b"MZ", "Windows PE/DOS executable (signature only)"),
    (b"\x89PNG\r\n\x1a\n", "PNG image"),
    (b"\xff\xd8\xff", "JPEG image"),
    (b"GIF87a", "GIF image"),
    (b"GIF89a", "GIF image"),
    (b"%PDF-", "PDF document"),
    (b"PK\x03\x04", "ZIP-based archive (could also be DOCX, XLSX, APK, etc.)"),
    (b"7z\xbc\xaf\x27\x1c", "7-Zip archive"),
    (b"Rar!\x1a\x07", "RAR archive"),
    (b"\x1f\x8b", "Gzip-compressed data"),
    (b"SQLite format 3\x00", "SQLite database"),
)


def detect_file_type(path: str | None = None, **_: Any) -> dict[str, Any]:
    """Identify a few common file formats from their leading bytes."""
    if not path:
        raise ValueError("Provide --path to a file.")
    target = Path(path).expanduser()
    if target.is_symlink() or not target.is_file():
        raise ValueError("Provide a regular file, not a folder or symbolic link.")
    try:
        with target.open("rb") as stream:
            header = stream.read(32)
    except OSError as exc:
        raise ValueError(f"Could not read the file: {exc}") from exc
    detected = next((label for signature, label in _SIGNATURES
                     if header.startswith(signature)), "Unknown signature")
    return {
        "path": str(target.resolve()),
        "detected_type": detected,
        "extension": target.suffix.lower(),
        "signature_hex": header[:16].hex(),
        "note": "Signature-based hint only. It does not execute or fully validate the file.",
    }


def text_file_profile(path: str | None = None, **_: Any) -> dict[str, Any]:
    """Report basic text encoding and line statistics without returning file contents."""
    if not path:
        raise ValueError("Provide --path to a text file.")
    target = Path(path).expanduser()
    if target.is_symlink() or not target.is_file():
        raise ValueError("Provide a regular file, not a folder or symbolic link.")
    maximum = 10 * 1024 * 1024
    try:
        size = target.stat().st_size
        if size > maximum:
            raise ValueError("File is larger than the 10 MiB text-inspection limit.")
        raw = target.read_bytes()
    except OSError as exc:
        raise ValueError(f"Could not read the file: {exc}") from exc
    if b"\x00" in raw:
        return {"path": str(target.resolve()), "size_bytes": size,
                "looks_like_text": False,
                "note": "NUL bytes were found. Text statistics were not calculated."}
    try:
        text = raw.decode("utf-8-sig")
        encoding = "UTF-8"
    except UnicodeDecodeError:
        return {"path": str(target.resolve()), "size_bytes": size,
                "looks_like_text": False,
                "note": "The file is not valid UTF-8. No content was displayed."}
    lines = text.splitlines()
    return {
        "path": str(target.resolve()),
        "size_bytes": size,
        "looks_like_text": True,
        "encoding": encoding,
        "line_count": len(lines),
        "character_count": len(text),
        "empty": size == 0,
        "newline_style": ("CRLF" if b"\r\n" in raw else
                          "LF" if b"\n" in raw else "none"),
        "note": "Only structural statistics are returned; file contents are never printed.",
    }


def find_duplicate_files(path: str | None = None, **_: Any) -> dict[str, Any]:
    """Find byte-identical regular files under a chosen directory, without following symlinks."""
    if not path:
        raise ValueError("Provide --path to a directory.")
    root = Path(path).expanduser()
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Provide a directory, not a file or symbolic link.")
    size_groups: dict[int, list[Path]] = {}
    scanned = skipped = 0
    truncated = False
    maximum_files = 10000
    for item in root.rglob("*"):
        if item.is_symlink() or not item.is_file():
            continue
        if scanned + skipped >= maximum_files:
            truncated = True
            break
        try:
            size = item.stat().st_size
            size_groups.setdefault(size, []).append(item)
            scanned += 1
        except OSError:
            skipped += 1
    duplicates = []
    for same_size in size_groups.values():
        if len(same_size) < 2:
            continue
        by_hash: dict[str, list[str]] = {}
        for item in same_size:
            try:
                digest = hashlib.sha256()
                with item.open("rb") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(chunk)
                by_hash.setdefault(digest.hexdigest(), []).append(str(item))
            except OSError:
                skipped += 1
        for digest, paths in by_hash.items():
            if len(paths) > 1:
                duplicates.append({"sha256": digest, "files": paths,
                                   "copies_beyond_first": len(paths) - 1})
    return {
        "directory": str(root.resolve()),
        "files_scanned": scanned,
        "duplicate_groups": len(duplicates),
        "duplicate_groups_found": duplicates,
        "skipped_files": skipped,
        "scan_limit_reached": truncated,
        "note": "Read-only scan. Symbolic links are ignored; no files are deleted or changed.",
    }



def _unsafe_archive_path(name: str) -> bool:
    """Return whether an archive member name attempts to escape its extraction root."""
    posix_name = PurePosixPath(name.replace("\\", "/"))
    windows_name = PureWindowsPath(name)
    return (
        posix_name.is_absolute()
        or windows_name.is_absolute()
        or bool(windows_name.drive)
        or ".." in posix_name.parts
    )


def inspect_archive(path: str | None = None, **_: Any) -> dict[str, Any]:
    """List ZIP or TAR archive metadata without extracting or executing any member."""
    if not path:
        raise ValueError("Provide --path to a ZIP or TAR archive.")
    target = Path(path).expanduser()
    if target.is_symlink() or not target.is_file():
        raise ValueError("Provide a regular archive file, not a folder or symbolic link.")
    maximum_bytes = 100 * 1024 * 1024
    maximum_entries = 2000
    try:
        archive_size = target.stat().st_size
        if archive_size > maximum_bytes:
            raise ValueError("Archive is larger than the 100 MiB inspection limit.")
        entries: list[dict[str, Any]] = []
        total_entries = 0
        archive_format = ""
        if zipfile.is_zipfile(target):
            archive_format = "ZIP"
            with zipfile.ZipFile(target) as archive:
                infos = archive.infolist()
                total_entries = len(infos)
                for info in infos[:maximum_entries]:
                    mode = (info.external_attr >> 16) & 0xFFFF
                    is_link = stat.S_ISLNK(mode)
                    entries.append({
                        "name": info.filename[:500],
                        "type": "directory" if info.is_dir() else ("symbolic link" if is_link else "file"),
                        "size_bytes": info.file_size,
                        "compressed_size_bytes": info.compress_size,
                        "encrypted": bool(info.flag_bits & 0x1),
                        "unsafe_path": _unsafe_archive_path(info.filename),
                        "symbolic_link": is_link,
                    })
        else:
            try:
                with tarfile.open(target, mode="r:*") as archive:
                    archive_format = "TAR"
                    for member in archive:
                        total_entries += 1
                        if total_entries > maximum_entries:
                            break
                        kind = (
                            "directory" if member.isdir()
                            else "symbolic link" if member.issym()
                            else "hard link" if member.islnk()
                            else "file" if member.isfile()
                            else "special"
                        )
                        entries.append({
                            "name": member.name[:500],
                            "type": kind,
                            "size_bytes": member.size,
                            "compressed_size_bytes": None,
                            "encrypted": False,
                            "unsafe_path": _unsafe_archive_path(member.name),
                            "symbolic_link": member.issym() or member.islnk(),
                        })
            except (tarfile.ReadError, tarfile.CompressionError, EOFError):
                raise ValueError("The file is not a supported ZIP or TAR archive.") from None
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        raise ValueError(f"Could not inspect the archive: {exc}") from exc
    return {
        "path": str(target.resolve()),
        "archive_format": archive_format,
        "archive_size_bytes": archive_size,
        "entries_found": total_entries,
        "entries_returned": len(entries),
        "truncated": total_entries > maximum_entries,
        "unsafe_path_entries": sum(1 for entry in entries if entry["unsafe_path"]),
        "entries": entries,
        "note": "Metadata-only inspection. No files were extracted, executed, or modified. Review unsafe paths before extracting archives.",
    }


def file_entropy_profile(path: str | None = None, **_: Any) -> dict[str, Any]:
    """Calculate whole-file Shannon entropy without returning file contents."""
    if not path:
        raise ValueError("Provide --path to a regular file.")
    target = Path(path).expanduser()
    if target.is_symlink() or not target.is_file():
        raise ValueError("Provide a regular file, not a folder or symbolic link.")
    maximum_bytes = 50 * 1024 * 1024
    try:
        size = target.stat().st_size
        if size > maximum_bytes:
            raise ValueError("File is larger than the 50 MiB entropy-inspection limit.")
        frequencies = [0] * 256
        sampled = 0
        with target.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                sampled += len(chunk)
                for value in chunk:
                    frequencies[value] += 1
    except OSError as exc:
        raise ValueError(f"Could not read the file: {exc}") from exc
    entropy = 0.0
    if sampled:
        entropy = -sum(
            (count / sampled) * math.log2(count / sampled)
            for count in frequencies if count
        )
    if entropy < 4.0:
        interpretation = "low byte diversity"
    elif entropy < 7.0:
        interpretation = "moderate byte diversity"
    else:
        interpretation = "high byte diversity"
    return {
        "path": str(target.resolve()),
        "size_bytes": size,
        "bytes_sampled": sampled,
        "shannon_entropy_bits_per_byte": round(entropy, 4),
        "interpretation": interpretation,
        "note": "Entropy is a statistical property, not a malware verdict. Compression, encryption, and many legitimate file formats can all produce high entropy.",
    }
