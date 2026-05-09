import json

from backend.cli import main
from backend.config import load_config
from backend.events import append_threat_event, threat_event_path


def test_load_config_reads_yaml(tmp_path, monkeypatch) -> None:
    config_path = tmp_path / "kavach.yml"
    config_path.write_text(
        """
audio_source: mic
fusion:
  audio_weight: 0.6
  sms_weight: 0.4
  thresholds:
    suspicious: 0.2
    high: 0.5
    critical: 0.75
models:
  aasist_checkpoint_dir: custom/aasist
  sms_classifier: custom/sms.pkl
logging:
  level: DEBUG
  directory: custom-logs
  threat_events_file: events.jsonl
""",
        encoding="utf-8",
    )
    monkeypatch.delenv("KAVACH_AUDIO_SOURCE", raising=False)

    config = load_config(config_path)

    assert config.audio_source == "mic"
    assert config.fusion.audio_weight == 0.6
    assert config.fusion.sms_weight == 0.4
    assert config.fusion.transcript_weight == 0.2
    assert config.fusion.resolved_thresholds()["critical"] == 0.75
    assert config.models.aasist_checkpoint_dir == "custom/aasist"
    assert config.logging.level == "DEBUG"
    assert config.logging.directory == "custom-logs"
    assert config.logging.threat_events_file == "events.jsonl"


def test_config_env_audio_source_override(tmp_path, monkeypatch) -> None:
    config_path = tmp_path / "kavach.yml"
    config_path.write_text("audio_source: mic\n", encoding="utf-8")
    monkeypatch.setenv("KAVACH_AUDIO_SOURCE", "demo")

    config = load_config(config_path)

    assert config.audio_source == "demo"


def test_load_config_reads_security_allow_demo_controls(tmp_path, monkeypatch) -> None:
    config_path = tmp_path / "kavach.yml"
    config_path.write_text(
        """
security:
  auth_mode: bearer
  bearer_token: test-token
  allow_demo_controls: false
""",
        encoding="utf-8",
    )
    monkeypatch.delenv("KAVACH_ALLOW_DEMO_CONTROLS", raising=False)

    config = load_config(config_path)

    assert config.security.auth_mode == "bearer"
    assert config.security.bearer_token == "test-token"
    assert config.security.allow_demo_controls is False


def test_security_allow_demo_controls_env_override(tmp_path, monkeypatch) -> None:
    config_path = tmp_path / "kavach.yml"
    config_path.write_text(
        """
security:
  allow_demo_controls: false
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("KAVACH_ALLOW_DEMO_CONTROLS", "true")

    config = load_config(config_path)

    assert config.security.allow_demo_controls is True


def test_cli_score_fusion_outputs_json(capsys, monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        ["kavach", "score-fusion", "--audio-score", "0.9", "--sms-score", "0.85", "--transcript-score", "0.7"],
    )

    main()
    payload = json.loads(capsys.readouterr().out)

    assert payload["threat_level"] == "CRITICAL"
    assert payload["threat_score"] >= 0.8
    assert payload["transcript_score"] == 0.7


def test_cli_score_sms_outputs_json(capsys, monkeypatch) -> None:
    monkeypatch.setattr("sys.argv", ["kavach", "score-sms", "KYC blocked verify urgently"])

    main()
    payload = json.loads(capsys.readouterr().out)

    assert "sms_score" in payload
    assert payload["ml_source"] in {"trained_model", "lexical_fallback"}


def test_cli_status_reports_runtime_models(capsys, monkeypatch) -> None:
    monkeypatch.setattr("sys.argv", ["kavach", "status"])

    main()
    payload = json.loads(capsys.readouterr().out)

    assert "runtime_models" in payload
    assert "audio" in payload["runtime_models"]
    assert "logging" in payload
    assert "readiness" in payload
    assert payload["readiness"]["dataset"]["state"] == "seed_or_incomplete"


def test_cli_score_transcript_outputs_json(capsys, monkeypatch) -> None:
    monkeypatch.setattr("sys.argv", ["kavach", "score-transcript", "CBI case file share OTP immediately"])

    main()
    payload = json.loads(capsys.readouterr().out)

    assert payload["urgency_score"] > 0
    assert payload["backend"] == "rule_fallback"


def test_threat_event_logging_writes_only_actionable_levels(tmp_path) -> None:
    config_path = tmp_path / "kavach.yml"
    config_path.write_text(
        f"""
logging:
  directory: {tmp_path / "event-logs"}
  threat_events_file: events.jsonl
""",
        encoding="utf-8",
    )
    config = load_config(config_path)

    safe_path = append_threat_event({"threat_level": "SAFE", "threat_score": 0.1}, config.logging)
    high_path = append_threat_event({"threat_level": "HIGH", "threat_score": 0.7}, config.logging)

    assert safe_path is None
    assert high_path == threat_event_path(config.logging)
    assert "HIGH" in high_path.read_text(encoding="utf-8")
