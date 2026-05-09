import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests


class TestIntegration:
    """Integration tests for the full KAVACH pipeline."""

    @pytest.fixture(scope="class")
    def server_process(self):
        """Start the server for integration tests."""
        # Start server in background
        env = os.environ.copy()
        env["KAVACH_MODE"] = "demo"
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=Path(__file__).parent.parent,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for server to start
        time.sleep(3)

        yield process

        # Cleanup
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

    def test_health_endpoint(self, server_process):
        """Test that the health endpoint returns expected data."""
        response = requests.get("http://127.0.0.1:8000/health")
        assert response.status_code == 200

        data = response.json()
        assert "models" in data
        assert "readiness" in data
        assert "mode" in data

    def test_sms_scoring_pipeline(self, server_process):
        """Test end-to-end SMS scoring."""
        payload = {"text": "Your package has been delivered successfully. Track at: http://bit.ly/abc123"}
        response = requests.post("http://127.0.0.1:8000/score/sms", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "sms_score" in data
        assert "ml_score" in data
        assert isinstance(data["sms_score"], int | float)

    def test_fusion_pipeline(self, server_process):
        """Test fusion scoring with mock signals."""
        payload = {"audio_score": 0.8, "sms_score": 0.6, "transcript_score": 0.3}
        response = requests.post("http://127.0.0.1:8000/score/fusion", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "threat_level" in data
        assert "threat_score" in data
        assert "formula_str" in data

    def test_demo_scenario_setting(self, server_process):
        """Test setting demo scenarios."""
        payload = {"scenario": "high"}
        response = requests.post("http://127.0.0.1:8000/demo/scenario", json=payload)
        assert response.status_code == 200

        # Check that the override was set
        response = requests.get("http://127.0.0.1:8000/health")
        data = response.json()
        assert "override" in data
        assert data["override"] is not None

    def test_websocket_connection(self, server_process):
        """Test WebSocket threat stream connection."""
        try:
            import websocket

            ws = websocket.create_connection("ws://127.0.0.1:8000/ws/threat")
            # Should receive initial state
            result = ws.recv()
            assert result
            ws.close()
        except ImportError:
            pytest.skip("websocket-client not installed for WebSocket testing")

    def test_cli_integration(self):
        """Test CLI commands work end-to-end."""
        # Test SMS scoring via CLI
        result = subprocess.run(
            [sys.executable, "-m", "backend.cli", "score-sms", "Test SMS message"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "sms_score" in result.stdout.lower()

        # Test fusion scoring via CLI
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "backend.cli",
                "score-fusion",
                "--audio-score",
                "0.5",
                "--sms-score",
                "0.3",
                "--transcript-score",
                "0.8",
            ],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "threat_level" in result.stdout.lower()

    def test_config_loading(self):
        """Test configuration loading and validation."""
        from backend.config import load_config

        config = load_config()
        assert config.fusion.audio_weight >= 0
        assert config.fusion.sms_weight >= 0
        assert config.fusion.transcript_weight >= 0
        # Weights can sum to more than 1.0 as they get normalized by available signals

    def test_model_readiness(self):
        """Test that required models are ready."""
        from backend.config import load_config
        from backend.readiness import readiness_report

        config = load_config()
        status = readiness_report(config)
        # Should have some status information
        assert isinstance(status, dict)
        assert len(status) > 0
