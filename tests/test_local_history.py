from phantom_sec.local_history import Store


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

def test_all_settings_returns_saved_values(tmp_path):
    store = Store(tmp_path / "test.sqlite3")
    store.set_setting("theme", "dark")
    store.set_setting("language", "en")
    assert store.all_settings() == {"language": "en", "theme": "dark"}


def test_favourites_can_be_added_removed_and_persisted(tmp_path):
    database = tmp_path / "favourites.sqlite3"
    store = Store(database)
    store.set_favorite("system.info")
    store.set_favorite("network.dns")
    assert store.favorites() == ["network.dns", "system.info"]
    assert store.is_favorite("system.info") is True
    store.set_favorite("system.info", False)
    assert store.favorites() == ["network.dns"]
    assert Store(database).favorites() == ["network.dns"]
