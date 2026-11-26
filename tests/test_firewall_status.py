from types import SimpleNamespace

from phantom_sec import modules


def test_firewall_check_is_registered():
    assert "system.firewall" in {item.module_id for item in modules.get_modules()}


def test_firewall_check_reports_ufw_active(monkeypatch):
    monkeypatch.setattr(modules.platform, "system", lambda: "Linux")
    monkeypatch.setattr(modules.shutil, "which", lambda name: "/usr/sbin/ufw" if name == "ufw" else None)
    monkeypatch.setattr(
        modules.subprocess, "run",
        lambda *args, **kwargs: SimpleNamespace(stdout="Status: active\n", returncode=0),
    )

    result = modules.run_module("system.firewall")["result"]

    assert result["read_only"] is True
    assert result["managers"] == [{
        "name": "ufw", "status": "active", "details": "Status: active"
    }]


def test_firewall_check_reports_missing_managers_without_claiming_firewall_is_off(monkeypatch):
    monkeypatch.setattr(modules.platform, "system", lambda: "Linux")
    monkeypatch.setattr(modules.shutil, "which", lambda _name: None)

    result = modules.run_module("system.firewall")["result"]

    assert result["managers"] == []
    assert "Other firewall systems may still be active" in result["note"]


def test_firewall_check_handles_unsupported_platform(monkeypatch):
    monkeypatch.setattr(modules.platform, "system", lambda: "Darwin")

    result = modules.run_module("system.firewall")["result"]

    assert result["supported"] is False
    assert result["managers"] == []


def test_firewall_check_times_out_safely(monkeypatch):
    import subprocess

    monkeypatch.setattr(modules.platform, "system", lambda: "Linux")
    monkeypatch.setattr(modules.shutil, "which", lambda name: "/usr/sbin/ufw" if name == "ufw" else None)

    def timeout(*_args, **_kwargs):
        raise subprocess.TimeoutExpired("ufw", 3)

    monkeypatch.setattr(modules.subprocess, "run", timeout)
    result = modules.run_module("system.firewall")["result"]

    assert result["managers"][0]["status"] == "unknown"
    assert result["managers"][0]["details"] == "Status check timed out."
