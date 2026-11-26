from phantom_sec.cli import build_parser, run_doctor


def test_default_command_is_desktop_app_entry_point():
    assert build_parser().parse_args([]).command is None


def test_doctor_command_is_available():
    assert build_parser().parse_args(["doctor"]).command == "doctor"


def test_run_command_accepts_domain_option():
    args = build_parser().parse_args(["run", "network.dns", "--domain", "example.com"])
    assert args.module_id == "network.dns"
    assert args.domain == "example.com"


def test_doctor_passes_with_writable_home(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    assert run_doctor() == 0


def test_menu_command_is_available_for_terminal_mode():
    assert build_parser().parse_args(["menu"]).command == "menu"
