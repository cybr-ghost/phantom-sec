from phantom_sec import computer_checks
from phantom_sec.computer_checks import battery_info
from phantom_sec.modules import get_modules


def test_battery_tool_is_registered():
    assert "system.battery" in {item.module_id for item in get_modules()}


def test_linux_battery_reads_capacity_and_status(tmp_path, monkeypatch):
    battery = tmp_path / "BAT0"
    battery.mkdir()
    (battery / "capacity").write_text("83", encoding="ascii")
    (battery / "status").write_text("Discharging", encoding="ascii")
    original_path = computer_checks.Path
    monkeypatch.setattr(computer_checks.platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        original_path, "glob",
        lambda self, pattern: [battery] if str(self) == "/sys/class/power_supply" else [],
    )
    result = battery_info()
    assert result["available"] is True
    assert result["batteries"][0]["charge_percent"] == 83
    assert result["batteries"][0]["status"] == "Discharging"


def test_unsupported_battery_platform_returns_explanation(monkeypatch):
    monkeypatch.setattr(computer_checks.platform, "system", lambda: "FreeBSD")
    result = battery_info()
    assert result["available"] is False
    assert "not implemented" in result["note"]
