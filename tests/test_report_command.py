import json

from phantom_sec import cli


class FakeStore:
    recorded = None

    def record_run(self, module_id, result):
        self.recorded = (module_id, result)


def test_report_command_is_available():
    args = cli.build_parser().parse_args(["report", "--output", "snapshot.json"])
    assert args.command == "report"
    assert str(args.output) == "snapshot.json"


def test_report_command_writes_json_report(tmp_path, monkeypatch):
    destination = tmp_path / "snapshot.json"
    fake_store = FakeStore()
    monkeypatch.setattr(cli, "run_module", lambda module_id: {
        "module": module_id, "result": {"scope": "local computer only"}
    })
    monkeypatch.setattr(cli, "Store", lambda: fake_store)

    assert cli.main(["report", "--output", str(destination)]) == 0

    data = json.loads(destination.read_text(encoding="utf-8"))
    assert data["application"] == "Phantom Sec"
    assert data["report_type"] == "local_system_overview"
    assert data["report"]["scope"] == "local computer only"
    assert fake_store.recorded[0] == "system.overview"
    assert data["generated_at"]
