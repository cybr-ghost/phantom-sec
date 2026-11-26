import json

from phantom_sec.module_workshop import validate_manifest


def test_valid_manifest_is_metadata_only(tmp_path):
    manifest = tmp_path / "module.json"
    manifest.write_text(json.dumps({
        "id": "demo.sample", "name": "Sample", "version": "0.1.0",
        "description": "Example", "category": "Demo", "author": "Tester",
        "entry_point": "disabled", "permissions": []
    }), encoding="utf-8")
    result = validate_manifest(manifest)
    assert result["valid"] is True
    assert "not executable" in result["errors"][-1]


def test_unknown_permission_fails(tmp_path):
    manifest = tmp_path / "module.json"
    manifest.write_text(json.dumps({
        "id": "demo.sample", "name": "Sample", "version": "0.1.0",
        "description": "Example", "category": "Demo", "author": "Tester",
        "entry_point": "disabled", "permissions": ["admin_everything"]
    }), encoding="utf-8")
    assert validate_manifest(manifest)["valid"] is False
