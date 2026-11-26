"""Read-only local file inspection helpers."""

from __future__ import annotations

import hashlib
from pathlib import Path
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
