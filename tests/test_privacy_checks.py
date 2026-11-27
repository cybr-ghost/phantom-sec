import pytest

from phantom_sec.modules import get_modules, run_module


def test_email_syntax_check_does_not_verify_mailbox():
    result = run_module("privacy.email-syntax", address="person@example.com")["result"]
    assert result["address_syntax_valid"] is True
    assert result["network_access"] is False


def test_email_auth_header_audit_extracts_only_verdicts():
    headers = "From: sender@example.com\nAuthentication-Results: mx.example; spf=pass; dkim=pass; dmarc=fail\n"
    result = run_module("privacy.email-auth-headers", headers=headers)["result"]
    assert [item["method"] for item in result["authentication_results"]] == ["spf", "dkim", "dmarc"]


def test_tracking_pixel_detector_finds_tiny_images(tmp_path):
    target = tmp_path / "mail.html"
    target.write_text('<img src="https://example.test/pixel" width="1" height="1">', encoding="utf-8")
    result = run_module("privacy.email-tracking-pixels", path=str(target))["result"]
    assert result["tiny_image_candidates"] == 1


def test_email_attachment_inventory_does_not_return_attachment_names(tmp_path):
    target = tmp_path / "message.eml"
    target.write_bytes(
        b"Subject: Test\r\nMIME-Version: 1.0\r\n"
        b"Content-Type: multipart/mixed; boundary=x\r\n\r\n"
        b"--x\r\nContent-Type: text/plain\r\n\r\nhello\r\n"
        b"--x\r\nContent-Type: application/octet-stream\r\n"
        b"Content-Disposition: attachment; filename=secret.bin\r\n"
        b"Content-Transfer-Encoding: base64\r\n\r\neHl6\r\n--x--\r\n"
    )
    result = run_module("privacy.email-attachments", path=str(target))["result"]
    assert result["attachment_count"] == 1
    assert "secret.bin" not in str(result)


def test_phone_format_and_country_code():
    valid = run_module("privacy.phone-format", number="+4915123456789")["result"]
    code = run_module("privacy.phone-country-code", number="+4915123456789")["result"]
    assert valid["format_valid"] is True
    assert code["calling_code"] == "+49"
    assert code["calling_code_region"] == "Germany"


def test_phone_format_rejects_non_international_input():
    result = run_module("privacy.phone-format", number="555-1234")["result"]
    assert result["format_valid"] is False


def test_ip_classifier_handles_private_and_public_addresses():
    private = run_module("privacy.ip-classifier", address="192.168.1.5")["result"]
    public = run_module("privacy.ip-classifier", address="8.8.8.8")["result"]
    assert private["scope"] == "private"
    assert public["scope"] == "public"
    assert public["network_access"] is False


def test_hosts_audit_reports_non_loopback_overrides(tmp_path):
    target = tmp_path / "hosts"
    target.write_text("127.0.0.1 localhost\n203.0.113.7 example.test\n", encoding="utf-8")
    result = run_module("privacy.hosts-audit", path=str(target))["result"]
    assert result["entries_reviewed"] == 1
    assert result["non_loopback_overrides"][0]["mapped_names"] == ["example.test"]


def test_proxy_audit_does_not_disclose_values(monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "https://user:password@example.test:8443")
    result = run_module("privacy.proxy-audit")["result"]
    assert "HTTPS_PROXY" in result["configured_variables"]
    assert "password" not in str(result)


def test_local_listener_inventory_has_safe_shape():
    result = run_module("network.listening-ports")["result"]
    assert "supported" in result
    assert isinstance(result["listening_ports"], list)


def test_all_ten_privacy_tools_are_registered():
    ids = {module.module_id for module in get_modules()}
    assert {
        "privacy.email-syntax",
        "privacy.email-auth-headers",
        "privacy.email-tracking-pixels",
        "privacy.email-attachments",
        "privacy.phone-format",
        "privacy.phone-country-code",
        "privacy.ip-classifier",
        "privacy.hosts-audit",
        "privacy.proxy-audit",
        "network.listening-ports",
    } <= ids


def test_email_auth_header_limit_is_enforced():
    with pytest.raises(ValueError, match="50 KB"):
        run_module("privacy.email-auth-headers", headers="x" * 50001)
