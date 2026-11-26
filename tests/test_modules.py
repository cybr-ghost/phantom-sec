from phantom_sec.modules import get_modules, run_module


def test_module_ids_are_unique():
    ids = [module.module_id for module in get_modules()]
    assert len(ids) == len(set(ids))


def test_system_info_returns_platform():
    result = run_module("system.info")
    assert result["result"]["system"]


def test_unknown_module_is_rejected():
    try:
        run_module("not.real")
    except ValueError as exc:
        assert "Unknown module" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
