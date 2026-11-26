import pytest

from phantom_sec.modules import get_modules, run_module


def test_file_permissions_reports_octal_mode(tmp_path):
    target = tmp_path / "example.txt"
    target.write_text("hello", encoding="utf-8")
    target.chmod(0o640)
    result = run_module("file.permissions", path=str(target))["result"]
    if "permissions_octal" in result:
        assert result["permissions_octal"] == "0640"
        assert result["owner_read"] is True
        assert result["group_write"] is False
        assert result["other_read"] is False
        assert result["world_writable"] is False
    else:
        assert result["current_user_read"] is True
        assert "Windows ACL permissions are not decoded" in result["note"]


def test_file_permissions_rejects_missing_path():
    with pytest.raises(ValueError, match="Provide --path"):
        run_module("file.permissions")


def test_file_permissions_rejects_symlink(tmp_path):
    target = tmp_path / "target.txt"
    target.write_text("safe", encoding="utf-8")
    link = tmp_path / "link.txt"
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks are not available on this platform")
    with pytest.raises(ValueError, match="Symbolic links"):
        run_module("file.permissions", path=str(link))


def test_permission_tool_is_registered():
    assert "file.permissions" in {module.module_id for module in get_modules()}
