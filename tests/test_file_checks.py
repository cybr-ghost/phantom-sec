import zipfile

import pytest

from phantom_sec.modules import get_modules, run_module


def test_file_type_signature_detects_png(tmp_path):
    target = tmp_path / "image.bin"
    target.write_bytes(b"\x89PNG\r\n\x1a\n" + b"payload")
    result = run_module("file.type-signature", path=str(target))["result"]
    assert result["detected_type"] == "PNG image"


def test_file_type_signature_rejects_directory(tmp_path):
    with pytest.raises(ValueError, match="regular file"):
        run_module("file.type-signature", path=str(tmp_path))


def test_text_profile_reports_structure_without_content(tmp_path):
    target = tmp_path / "notes.txt"
    target.write_text("one\ntwo\n", encoding="utf-8")
    result = run_module("file.text-profile", path=str(target))["result"]
    assert result["line_count"] == 2
    assert result["encoding"] == "UTF-8"
    assert "contents" not in result


def test_text_profile_rejects_binary_file(tmp_path):
    target = tmp_path / "binary.dat"
    target.write_bytes(b"abc\x00def")
    result = run_module("file.text-profile", path=str(target))["result"]
    assert result["looks_like_text"] is False


def test_duplicate_finder_groups_identical_files(tmp_path):
    (tmp_path / "one.txt").write_bytes(b"same data")
    (tmp_path / "two.txt").write_bytes(b"same data")
    (tmp_path / "different.txt").write_bytes(b"other")
    result = run_module("file.duplicate-finder", path=str(tmp_path))["result"]
    assert result["files_scanned"] == 3
    assert result["duplicate_groups"] == 1
    assert result["duplicate_groups_found"][0]["copies_beyond_first"] == 1


def test_duplicate_finder_rejects_file_path(tmp_path):
    target = tmp_path / "file.txt"
    target.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="directory"):
        run_module("file.duplicate-finder", path=str(target))


def test_new_file_tools_are_registered():
    ids = {module.module_id for module in get_modules()}
    assert {"file.type-signature", "file.text-profile", "file.duplicate-finder"} <= ids



def test_archive_inspector_lists_zip_without_extracting_and_flags_traversal(tmp_path):
    archive_path = tmp_path / "sample.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("docs/readme.txt", "safe")
        archive.writestr("../outside.txt", "not extracted")
    result = run_module("file.archive-inspector", path=str(archive_path))["result"]
    assert result["archive_format"] == "ZIP"
    assert result["entries_found"] == 2
    assert result["unsafe_path_entries"] == 1
    assert any(item["unsafe_path"] for item in result["entries"])
    assert not (tmp_path.parent / "outside.txt").exists()


def test_archive_inspector_rejects_non_archive(tmp_path):
    target = tmp_path / "notes.txt"
    target.write_text("not an archive", encoding="utf-8")
    with pytest.raises(ValueError, match="supported ZIP or TAR"):
        run_module("file.archive-inspector", path=str(target))


def test_file_entropy_profile_reports_constant_file_as_low_entropy(tmp_path):
    target = tmp_path / "repeated.bin"
    target.write_bytes(b"A" * 2048)
    result = run_module("file.entropy-profile", path=str(target))["result"]
    assert result["bytes_sampled"] == 2048
    assert result["shannon_entropy_bits_per_byte"] == 0.0
    assert result["interpretation"] == "low byte diversity"


def test_file_entropy_profile_rejects_directory(tmp_path):
    with pytest.raises(ValueError, match="regular file"):
        run_module("file.entropy-profile", path=str(tmp_path))


def test_new_archive_and_entropy_tools_are_registered():
    ids = {module.module_id for module in get_modules()}
    assert {"file.archive-inspector", "file.entropy-profile"} <= ids



def test_large_file_finder_reports_files_over_threshold(tmp_path):
    (tmp_path / "large.bin").write_bytes(b"x" * 20)
    (tmp_path / "small.bin").write_bytes(b"x")
    result = run_module("file.large-file-finder", path=str(tmp_path), minimum_bytes=10)["result"]
    assert result["large_files_found"] == 1
    assert result["files"][0]["path"].endswith("large.bin")


def test_empty_file_finder_reports_zero_byte_files(tmp_path):
    (tmp_path / "empty.txt").write_bytes(b"")
    (tmp_path / "filled.txt").write_text("data", encoding="utf-8")
    result = run_module("file.empty-file-finder", path=str(tmp_path))["result"]
    assert result["empty_files_found"] == 1
    assert result["files"][0].endswith("empty.txt")


def test_extension_check_detects_mismatch_without_execution(tmp_path):
    target = tmp_path / "image.exe"
    target.write_bytes(b"\x89PNG\r\n\x1a\n" + b"payload")
    result = run_module("file.extension-check", path=str(target))["result"]
    assert result["status"] == "extension_mismatch"
    assert result["detected_type"] == "PNG image"


def test_extension_check_rejects_directory(tmp_path):
    with pytest.raises(ValueError, match="regular file"):
        run_module("file.extension-check", path=str(tmp_path))


def test_new_file_audit_tools_are_registered():
    ids = {module.module_id for module in get_modules()}
    assert {"file.large-file-finder", "file.empty-file-finder", "file.extension-check"} <= ids
