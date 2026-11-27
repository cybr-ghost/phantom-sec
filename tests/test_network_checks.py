from phantom_sec.network_checks import interfaces, reverse_dns


def test_interfaces_returns_list():
    result = interfaces()
    assert isinstance(result["interfaces"], list)


def test_reverse_dns_rejects_invalid_address():
    try:
        reverse_dns(address="not-an-ip")
    except ValueError as exc:
        assert "valid IPv4 or IPv6" in str(exc)
    else:
        raise AssertionError("Expected ValueError")



def test_local_addresses_only_reports_ip_address_records():
    from phantom_sec.network_checks import local_addresses

    result = local_addresses()
    assert isinstance(result["addresses"], list)
    assert result["hostname"]
    assert all(item["family"] in {"IPv4", "IPv6"} for item in result["addresses"])
