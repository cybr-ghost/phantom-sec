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
