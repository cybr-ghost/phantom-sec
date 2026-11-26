from phantom_sec.cli import build_parser


def test_default_command_opens_menu():
    assert build_parser().parse_args([]).command is None


def test_doctor_command_is_available():
    assert build_parser().parse_args(["doctor"]).command == "doctor"


def test_run_command_accepts_domain_option():
    args = build_parser().parse_args(["run", "network.dns", "--domain", "example.com"])
    assert args.module_id == "network.dns"
    assert args.domain == "example.com"
