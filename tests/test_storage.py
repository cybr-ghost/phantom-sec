from phantom_sec.storage import Store


def test_history_round_trip(tmp_path):
    store = Store(tmp_path / "test.sqlite3")
    store.record_run("system.info", {"ok": True})
    rows = store.history()
    assert rows[0]["module_id"] == "system.info"
    assert rows[0]["result"]["ok"] is True


def test_settings_round_trip(tmp_path):
    store = Store(tmp_path / "test.sqlite3")
    store.set_setting("theme", "dark")
    assert store.get_setting("theme") == "dark"
    assert store.get_setting("missing", "fallback") == "fallback"
