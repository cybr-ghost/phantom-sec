from phantom_sec.domain_checks import _assess_dmarc, _assess_spf, _normalise_domain


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


def test_spf_assessment_detects_hard_fail_policy():
    result = _assess_spf(["v=spf1 include:mail.example -all"])
    assert result["status"] == "configured"
    assert result["all_mechanism"] == "-all"


def test_spf_assessment_flags_multiple_records():
    result = _assess_spf(["v=spf1 -all", "v=spf1 ~all"])
    assert result["status"] == "multiple"


def test_spf_assessment_flags_permissive_all():
    result = _assess_spf(["v=spf1 +all"])
    assert result["all_mechanism"] == "+all"


def test_dmarc_assessment_reads_policy():
    result = _assess_dmarc(["v=DMARC1; p=reject; pct=100"])
    assert result["status"] == "configured"
    assert result["policy"] == "reject"


def test_dmarc_assessment_flags_monitoring_policy():
    result = _assess_dmarc(["v=DMARC1; p=none"])
    assert result["policy"] == "none"


def test_dmarc_assessment_rejects_invalid_policy():
    result = _assess_dmarc(["v=DMARC1; p=unknown"])
    assert result["status"] == "invalid"


def test_email_posture_tool_is_registered():
    from phantom_sec.modules import get_modules

    assert "domain.email-posture" in {item.module_id for item in get_modules()}
