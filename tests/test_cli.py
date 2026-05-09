from backend.cli import build_parser


def test_cli_parses_status() -> None:
    parser = build_parser()
    args = parser.parse_args(["status"])
    assert args.command == "status"
    assert hasattr(args, "func")


def test_cli_parses_score_sms() -> None:
    parser = build_parser()
    args = parser.parse_args(["score-sms", "test message"])
    assert args.command == "score-sms"
    assert args.text == "test message"


def test_cli_parses_score_fusion() -> None:
    parser = build_parser()
    args = parser.parse_args(["score-fusion", "--audio-score", "0.5", "--sms-score", "0.6"])
    assert args.command == "score-fusion"
    assert args.audio_score == 0.5
    assert args.sms_score == 0.6
    assert args.transcript_score == -1.0


def test_cli_start_command_writes_pid_file(monkeypatch, tmp_path) -> None:
    from backend.cli import start_command

    class FakeProcess:
        pid = 12345

    def fake_popen(*args, **kwargs):
        return FakeProcess()

    monkeypatch.setattr("backend.cli.subprocess.Popen", fake_popen)
    pid_file = tmp_path / ".kavach.pid"
    log_file = tmp_path / "logs" / "kavach.log"
    args = type("Args", (), {"host": "127.0.0.1", "port": 9000, "pid_file": pid_file, "log_file": log_file})

    start_command(args)

    assert pid_file.exists()
    assert pid_file.read_text() == "12345"
    assert log_file.exists()


def test_cli_stop_command_removes_pid_file(monkeypatch, tmp_path) -> None:
    from backend.cli import stop_command

    pid_file = tmp_path / ".kavach.pid"
    pid_file.write_text("12345")

    monkeypatch.setattr("backend.cli._is_process_running", lambda pid: True)
    killed = {}

    def fake_kill(pid, sig):
        killed["pid"] = pid
        killed["signal"] = sig

    monkeypatch.setattr("backend.cli.os.kill", fake_kill)
    args = type("Args", (), {"pid_file": pid_file})

    stop_command(args)

    assert killed["pid"] == 12345
    assert pid_file.exists() is False
