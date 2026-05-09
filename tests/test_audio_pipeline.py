import asyncio

import backend.audio.capture as capture
from backend.audio.aasist_infer import (
    AASIST_TARGET_SAMPLES,
    AASISTScorer,
    find_checkpoint,
    heuristic_audio_score,
    normalize_checkpoint_state_dict,
    prepare_aasist_audio,
)
from backend.audio.capture import audio_windows, synthetic_window
from backend.audio.features import extract_features
from backend.audio.scoring import normalize_audio_samples
from backend.audio.urgency_nlp import muril_status, score_transcript, urgency_score
from backend.audio.whisper_stt import whisper_status


def test_feature_extraction() -> None:
    features = extract_features(synthetic_window())
    assert features["mfcc"].shape[0] == 40
    assert features["delta_mfcc"].shape[0] == 40
    assert features["delta2_mfcc"].shape[0] == 40
    assert features["log_mel"].shape[0] == 64
    assert features["raw"].ndim == 1


def test_spoof_demo_scores_higher_than_genuine() -> None:
    scorer = AASISTScorer()
    genuine, _ = scorer.score(synthetic_window(spoof=False))
    spoof, _ = scorer.score(synthetic_window(spoof=True))
    assert spoof > genuine


def test_heuristic_score_is_bounded() -> None:
    score = heuristic_audio_score(synthetic_window(spoof=True))

    assert 0.0 <= score <= 1.0


def test_prepare_aasist_audio_pads_and_normalizes() -> None:
    audio = prepare_aasist_audio([0.0, 2.0, -2.0])

    assert audio.shape[0] == AASIST_TARGET_SAMPLES
    assert audio.max() <= 1.0
    assert audio.min() >= -1.0


def test_normalize_audio_resamples_to_16khz() -> None:
    samples = [0.1] * 8_000
    audio = normalize_audio_samples(samples, sample_rate=8_000)

    assert 15_900 <= audio.shape[0] <= 16_100


def test_transcript_urgency_scores_scam_script_higher_than_normal_text() -> None:
    scam = score_transcript("CBI case file opened. Share OTP immediately warna legal action hoga.")
    normal = score_transcript("Hello, your appointment is confirmed for tomorrow morning.")

    assert scam["urgency_score"] > normal["urgency_score"]
    assert scam["matched_phrases"]
    assert urgency_score("share otp immediately") > 0


def test_whisper_and_muril_statuses_are_fallback_safe() -> None:
    whisper = whisper_status()
    muril = muril_status()

    assert "backend" in whisper
    assert "model_state" in whisper
    assert "backend" in muril
    assert muril["backend"] == "rule_fallback"


def test_aasist_status_missing_checkpoint(tmp_path) -> None:
    scorer = AASISTScorer(checkpoint_dir=tmp_path)
    assert scorer.status.backend == "heuristic"
    assert scorer.status.checkpoint_state == "missing"
    assert scorer.status.checkpoint_path is None
    assert scorer.status.expected_sample_rate == 16_000


def test_aasist_detects_checkpoint_file(tmp_path) -> None:
    checkpoint = tmp_path / "model.pt"
    checkpoint.write_bytes(b"not a real torch checkpoint")
    scorer = AASISTScorer(checkpoint_dir=tmp_path)
    assert find_checkpoint(tmp_path) == checkpoint
    assert scorer.status.backend == "heuristic"
    assert scorer.status.checkpoint_path == str(checkpoint)
    assert scorer.status.checkpoint_state in {"present_unvalidated", "invalid"}


def test_normalize_checkpoint_state_dict_supports_common_layouts() -> None:
    checkpoint = {"state_dict": {"module.layer.weight": "value"}}

    assert normalize_checkpoint_state_dict(checkpoint) == {"layer.weight": "value"}


def test_demo_audio_source_yields_window() -> None:
    async def get_window():
        source = audio_windows("demo")
        return await source.__anext__()

    window, spoof_hint, tick = asyncio.run(get_window())
    assert window.shape[0] == int(capture.SAMPLE_RATE * capture.WINDOW_SEC)
    assert isinstance(spoof_hint, bool)
    assert tick == 0


def test_mic_source_falls_back_to_demo_when_sounddevice_missing(monkeypatch) -> None:
    monkeypatch.setattr(capture, "sd", None)

    async def get_window():
        source = audio_windows("mic")
        return await source.__anext__()

    window, spoof_hint, tick = asyncio.run(get_window())
    assert window.shape[0] == int(capture.SAMPLE_RATE * capture.WINDOW_SEC)
    assert isinstance(spoof_hint, bool)
    assert tick == 0
