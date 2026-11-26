from phantom_sec.modules import get_modules, run_module


def test_system_overview_is_registered():
    assert "system.overview" in {module.module_id for module in get_modules()}


def test_system_overview_contains_local_read_only_sections():
    result = run_module("system.overview")["result"]
    assert result["scope"] == "local computer only"
    assert {"system", "uptime", "memory", "storage", "processes", "network"} <= set(result)
    assert isinstance(result["notices"], list)
    assert "not a full security audit" in result["disclaimer"]
    assert result["storage"]["total_bytes"] >= 0
    assert result["storage"]["free_bytes"] >= 0
