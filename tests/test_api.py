from dataclasses import replace

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

import backend.main as main_mod
from backend.audio.capture import synthetic_window
from backend.main import app

client = TestClient(app)


def test_health_reports_model_details() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["mode"] in {"demo", "mic"}
    assert payload["models"]["audio"]["backend"] in {"heuristic", "aasist"}
    assert "checkpoint_state" in payload["models"]["audio"]
    assert payload["models"]["audio"]["expected_sample_rate"] == 16000
    assert "speech_to_text" in payload["models"]
    assert "urgency_nlp" in payload["models"]
    assert payload["models"]["sms"]["backend"] == "trained_model"
    assert payload["models"]["sms"]["model_state"] == "ready"
    assert payload["readiness"]["state"] in {"ready", "attention_required"}
    assert payload["readiness"]["dataset"]["state"] == "seed_or_incomplete"
    assert payload["readiness"]["frontend"]["state"] == "ready"


def test_v1_health_alias_works() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "x-request-id" in response.headers


def test_live_ready_metrics_endpoints() -> None:
    live = client.get("/api/v1/live")
    ready = client.get("/api/v1/ready")
    metrics = client.get("/api/v1/metrics")
    assert live.status_code == 200
    assert live.json()["status"] == "alive"
    assert ready.status_code == 200
    assert ready.json()["status"] in {"ready", "not_ready"}
    assert metrics.status_code == 200
    assert "http_requests_total" in metrics.json()


def test_config_reports_fusion_weights_and_thresholds() -> None:
    response = client.get("/config")
    assert response.status_code == 200
    payload = response.json()
    assert payload["audio_weight"] == 0.55
    assert payload["sms_weight"] == 0.45
    assert payload["transcript_weight"] == 0.2
    assert payload["thresholds"]["critical"] == 0.8


def test_score_sms_endpoint_scores_text() -> None:
    response = client.post(
        "/score/sms",
        json={"text": "Vehicle MH12AB1234 ka e-challan Rs.500 pending hai. Pay immediately https://bit.ly/challan99"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["sms_score"] > 0.5
    assert payload["ml_source"] in {"trained_model", "lexical_fallback"}
    assert "url_shortener" in payload["url_flags"]


def test_v1_score_sms_alias_works() -> None:
    response = client.post("/api/v1/score/sms", json={"text": "KYC blocked verify immediately"})
    assert response.status_code == 200
    assert "sms_score" in response.json()


def test_score_sms_endpoint_validates_empty_text() -> None:
    response = client.post("/score/sms", json={"text": ""})
    assert response.status_code == 422


def test_score_audio_endpoint_scores_samples() -> None:
    response = client.post(
        "/score/audio",
        json={"samples": synthetic_window(spoof=True).tolist(), "sample_rate": 16000},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["audio_score"] > 0
    assert payload["backend"] in {"heuristic", "aasist"}
    assert payload["checkpoint_state"] in {"missing", "present_unvalidated", "invalid", "validated"}
    assert payload["sample_rate"] == 16000
    assert payload["summary"]["samples"] == 32000


def test_score_audio_endpoint_validates_empty_samples() -> None:
    response = client.post("/score/audio", json={"samples": [], "sample_rate": 16000})
    assert response.status_code == 422


def test_score_transcript_endpoint_scores_urgency() -> None:
    response = client.post(
        "/score/transcript",
        json={"transcript": "CBI case file opened. Share OTP immediately or legal action will start."},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["urgency_score"] > 0.4
    assert payload["backend"] == "rule_fallback"
    assert payload["matched_phrases"]


def test_score_transcript_endpoint_validates_empty_text() -> None:
    response = client.post("/score/transcript", json={"transcript": ""})
    assert response.status_code == 422


def test_score_fusion_endpoint_combines_scores() -> None:
    response = client.post("/score/fusion", json={"audio_score": 0.9, "sms_score": 0.85})
    assert response.status_code == 200
    payload = response.json()
    assert payload["type"] == "fusion"
    assert payload["threat_level"] == "CRITICAL"
    assert payload["threat_score"] >= 0.8
    assert payload["transcript_score"] == -1.0


def test_score_fusion_endpoint_validates_score_range() -> None:
    response = client.post("/score/fusion", json={"audio_score": 1.2, "sms_score": 0.5})
    assert response.status_code == 422


def test_demo_scenario_endpoint_accepts_known_scenario() -> None:
    response = client.post("/demo/scenario", json={"scenario": "critical"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] is True
    assert payload["scenario"] == "critical"
    assert payload["override"]["audio_score"] == 0.91


def test_mock_sms_endpoint_accepts_text() -> None:
    response = client.post("/sms/mock", json={"text": "This is a test scam SMS"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] is True
    assert payload["error"] is None


def test_ws_threat_stream_emits_events() -> None:
    with client.websocket_connect("/ws/threat") as websocket:
        first = websocket.receive_json()
        assert first["type"] in {"audio", "sms", "fusion", "transcript"}

        second = websocket.receive_json()
        assert second["type"] in {"audio", "sms", "fusion", "transcript"}

        third = websocket.receive_json()
        assert third["type"] in {"audio", "sms", "fusion", "transcript"}
        websocket.close()


def test_demo_controls_disabled_blocks_mutating_demo_endpoints(monkeypatch) -> None:
    secured = replace(
        main_mod.APP_CONFIG,
        security=replace(main_mod.APP_CONFIG.security, allow_demo_controls=False),
    )
    monkeypatch.setattr(main_mod, "APP_CONFIG", secured)

    mock_resp = client.post("/sms/mock", json={"text": "test"})
    scenario_resp = client.post("/demo/scenario", json={"scenario": "safe"})

    assert mock_resp.status_code == 403
    assert scenario_resp.status_code == 403


def test_websocket_rejects_missing_api_key_when_configured(monkeypatch) -> None:
    main_mod._rate_limit_windows.clear()
    secured = replace(
        main_mod.APP_CONFIG,
        security=replace(main_mod.APP_CONFIG.security, auth_mode="api_key", api_key="kavach-secret"),
    )
    monkeypatch.setattr(main_mod, "APP_CONFIG", secured)

    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/ws/threat"):
            pass
    assert exc.value.code == 1008

    with client.websocket_connect("/ws/threat", headers={"x-api-key": "kavach-secret"}) as websocket:
        first = websocket.receive_json()
        assert first["type"] in {"audio", "sms", "fusion", "transcript"}
        websocket.close()


def test_api_key_enforced_when_configured(monkeypatch) -> None:
    secured = replace(
        main_mod.APP_CONFIG,
        security=replace(main_mod.APP_CONFIG.security, auth_mode="api_key", api_key="kavach-secret"),
    )
    monkeypatch.setattr(main_mod, "APP_CONFIG", secured)
    unauth = client.get("/api/v1/health")
    assert unauth.status_code == 401
    auth = client.get("/api/v1/health", headers={"x-api-key": "kavach-secret"})
    assert auth.status_code == 200


def test_bearer_auth_enforced_when_configured(monkeypatch) -> None:
    secured = replace(
        main_mod.APP_CONFIG,
        security=replace(main_mod.APP_CONFIG.security, auth_mode="bearer", bearer_token="token-123"),
    )
    monkeypatch.setattr(main_mod, "APP_CONFIG", secured)
    unauth = client.get("/api/v1/health")
    assert unauth.status_code == 401
    auth = client.get("/api/v1/health", headers={"authorization": "Bearer token-123"})
    assert auth.status_code == 200


def test_rate_limit_enforced(monkeypatch) -> None:
    main_mod._rate_limit_windows.clear()
    limited = replace(main_mod.APP_CONFIG, security=replace(main_mod.APP_CONFIG.security, rate_limit_per_minute=1))
    monkeypatch.setattr(main_mod, "APP_CONFIG", limited)
    first = client.get("/api/v1/health")
    second = client.get("/api/v1/health")
    assert first.status_code == 200
    assert second.status_code == 429
    main_mod._rate_limit_windows.clear()
