from phantom_sec.modules import get_modules, run_module


def test_uptime_tool_is_registered():
    assert "system.uptime" in {module.module_id for module in get_modules()}


def test_uptime_result_has_clear_supported_or_unsupported_status():
    result = run_module("system.uptime")["result"]
    assert "platform" in result
    if result["platform"] == "Linux" and result["uptime_seconds"] is not None:
        assert result["uptime_seconds"] >= 0
        assert result["uptime_human"]
    else:
        assert result["uptime_seconds"] is None
        assert result["note"]
