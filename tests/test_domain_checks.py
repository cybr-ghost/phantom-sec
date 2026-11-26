from phantom_sec.web_checks import analyze_url, calculate_subnet


def test_url_analyzer_is_offline_and_flags_plain_http():
    result = analyze_url(url="http://example.com/path")
    assert result["network_access"] is False
    assert any("HTTP rather than HTTPS" in item for item in result["indicators"])


def test_url_analyzer_rejects_non_web_scheme():
    try:
        analyze_url(url="file:///etc/passwd")
    except ValueError as exc:
        assert "HTTP or HTTPS" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_url_analyzer_flags_userinfo():
    result = analyze_url(url="https://user:pass@example.com/")
    assert any("user information" in item for item in result["indicators"])


def test_subnet_calculator_ipv4():
    result = calculate_subnet(network="192.168.1.17/24")
    assert result["network"] == "192.168.1.0"
    assert result["broadcast"] == "192.168.1.255"
    assert result["usable_hosts"] == 254


def test_subnet_calculator_ipv6():
    result = calculate_subnet(network="2001:db8::1/64")
    assert result["address_family"] == "IPv6"
    assert result["broadcast"] is None
    assert result["total_addresses"] == 2**64


def test_subnet_calculator_rejects_invalid_input():
    try:
        calculate_subnet(network="not-a-network")
    except ValueError as exc:
        assert "Invalid IP network" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


from phantom_sec.domain_checks import _normalise_domain


def test_domain_normalisation_accepts_case_and_trailing_dot():
    assert _normalise_domain("Example.COM.") == "example.com"


def test_domain_normalisation_rejects_url():
    try:
        _normalise_domain("https://example.com")
    except ValueError as exc:
        assert "valid public domain" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_domain_normalisation_rejects_single_label():
    try:
        _normalise_domain("localhost")
    except ValueError as exc:
        assert "valid public domain" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
