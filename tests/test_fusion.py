from backend.fusion.engine import ThreatLevel, fuse


def test_fusion_critical() -> None:
    result = fuse(0.92, 0.85)
    assert result.threat_level == ThreatLevel.CRITICAL
    assert result.threat_score >= 0.8


def test_fusion_single_signal_audio() -> None:
    result = fuse(0.9, -1.0)
    assert result.threat_score == 0.9
    assert result.threat_level == ThreatLevel.CRITICAL


def test_fusion_safe() -> None:
    result = fuse(0.05, 0.08)
    assert result.threat_level == ThreatLevel.SAFE


def test_fusion_includes_transcript_signal() -> None:
    result = fuse(0.2, 0.2, 0.9)

    assert result.transcript_score == 0.9
    assert result.threat_score > 0.2
    assert "transcript" in result.formula_str
