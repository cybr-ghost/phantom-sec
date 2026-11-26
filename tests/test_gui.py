from phantom_sec.gui import input_kind, search_modules


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
