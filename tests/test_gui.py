from phantom_sec.gui import PhantomSecWindow, dashboard_summary, input_kind, search_modules
from phantom_sec.local_history import Store


def test_search_matches_tool_name_id_and_description():
    assert any(item.module_id == "system.memory" for item in search_modules("memory"))
    assert any(item.module_id == "network.dns" for item in search_modules("network.dns"))
    assert any(item.module_id == "file.sha256" for item in search_modules("hash"))


def test_search_filters_by_category():
    results = search_modules("dns", "Network diagnostics")
    assert results
    assert all(item.category == "Network diagnostics" for item in results)


def test_search_is_case_insensitive_and_empty_search_returns_all():
    assert search_modules("FIREWALL")
    assert len(search_modules()) == len(search_modules("   "))


def test_input_fields_are_mapped_for_existing_tools():
    assert input_kind("file.sha256") == "path"
    assert input_kind("network.dns") == "domain"
    assert input_kind("network.reverse-dns") == "address"
    assert input_kind("system.overview") is None


def test_export_action_is_part_of_the_window_class():
    assert callable(getattr(PhantomSecWindow, "_export_output", None))


def test_dashboard_summary_reports_tools_categories_and_recent_run(tmp_path):
    store = Store(tmp_path / "dashboard.sqlite3")
    empty = dashboard_summary(store)
    assert empty["tool_count"] == 17
    assert empty["category_count"] >= 3
    assert empty["recent_run"] is None
    assert empty["favorite_count"] == 0

    store.record_run("system.info", {"ok": True})
    summary = dashboard_summary(store)
    assert summary["recent_run"]["module_id"] == "system.info"


def test_dashboard_summary_counts_favourites(tmp_path):
    store = Store(tmp_path / "dashboard-favourites.sqlite3")
    store.set_favorite("system.info")
    assert dashboard_summary(store)["favorite_count"] == 1
