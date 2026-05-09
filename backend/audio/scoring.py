from __future__ import annotations

from math import gcd

import numpy as np
from scipy.signal import resample_poly

from backend.audio.aasist_infer import AASIST_SAMPLE_RATE

MAX_AUDIO_SAMPLES = AASIST_SAMPLE_RATE * 12


def normalize_audio_samples(samples: list[float], sample_rate: int) -> np.ndarray:
    """Convert API audio samples to mono 16 kHz float32 waveform data."""
    if sample_rate <= 0:
        raise ValueError("sample_rate must be greater than zero")
    if len(samples) > MAX_AUDIO_SAMPLES:
        raise ValueError(f"audio sample payload is too large; maximum is {MAX_AUDIO_SAMPLES} samples")

    audio = np.asarray(samples, dtype=np.float32).flatten()
    if audio.size == 0:
        raise ValueError("samples cannot be empty")
    audio = np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0)

    peak = float(np.max(np.abs(audio)))
    if peak > 1.0:
        audio = audio / peak

    if sample_rate != AASIST_SAMPLE_RATE:
        factor = gcd(sample_rate, AASIST_SAMPLE_RATE)
        up = AASIST_SAMPLE_RATE // factor
        down = sample_rate // factor
        audio = resample_poly(audio, up, down).astype(np.float32)

    return audio.astype(np.float32, copy=False)


def audio_summary(audio: np.ndarray) -> dict[str, float | int]:
    if audio.size == 0:
        return {"samples": 0, "duration_sec": 0.0, "peak": 0.0, "rms": 0.0}
    return {
        "samples": int(audio.size),
        "duration_sec": round(float(audio.size / AASIST_SAMPLE_RATE), 3),
        "peak": round(float(np.max(np.abs(audio))), 4),
        "rms": round(float(np.sqrt(np.mean(np.square(audio)))), 4),
    }
