from __future__ import annotations

import numpy as np

SR = 16_000
N_MFCC = 40
N_MELS = 64
N_FFT = 512
HOP_LEN = 160

try:
    import librosa
except ImportError:  # pragma: no cover
    librosa = None


def _fallback_log_spectrogram(audio: np.ndarray) -> np.ndarray:
    """Return a compact log spectrogram for browser rendering."""
    frame = 512
    hop = 256
    if len(audio) < frame:
        audio = np.pad(audio, (0, frame - len(audio)))

    windows = []
    for start in range(0, len(audio) - frame + 1, hop):
        chunk = audio[start : start + frame] * np.hanning(frame)
        spectrum = np.abs(np.fft.rfft(chunk))
        windows.append(spectrum)

    spec = np.array(windows, dtype=np.float32).T
    if spec.shape[0] > N_MELS:
        bins = np.array_split(spec, N_MELS, axis=0)
        spec = np.array([b.mean(axis=0) for b in bins], dtype=np.float32)

    spec = 20 * np.log10(spec + 1e-6)
    return np.clip(spec, -80, 0)


def _fallback_feature_bundle(audio: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "mfcc": _fallback_log_spectrogram(audio)[:N_MFCC],
        "delta_mfcc": np.zeros((N_MFCC, 1), dtype=np.float32),
        "delta2_mfcc": np.zeros((N_MFCC, 1), dtype=np.float32),
        "log_mel": _fallback_log_spectrogram(audio),
        "f0": np.zeros((1,), dtype=np.float32),
        "raw": audio.astype(np.float32, copy=False),
    }


def extract_features(audio: np.ndarray) -> dict[str, np.ndarray]:
    audio = np.asarray(audio, dtype=np.float32).flatten()
    if librosa is None:
        return _fallback_feature_bundle(audio)

    if audio.size == 0:
        audio = np.zeros(SR, dtype=np.float32)

    if audio.size < SR:
        audio = np.pad(audio, (0, SR - audio.size))

    mfcc = librosa.feature.mfcc(
        y=audio,
        sr=SR,
        n_mfcc=N_MFCC,
        n_fft=N_FFT,
        hop_length=HOP_LEN,
    ).astype(np.float32)
    delta_mfcc = librosa.feature.delta(mfcc).astype(np.float32)
    delta2_mfcc = librosa.feature.delta(mfcc, order=2).astype(np.float32)
    mel = librosa.feature.melspectrogram(
        y=audio,
        sr=SR,
        n_mels=N_MELS,
        n_fft=N_FFT,
        hop_length=HOP_LEN,
        power=2.0,
    ).astype(np.float32)
    log_mel = librosa.power_to_db(mel, ref=np.max).astype(np.float32)
    f0, _, _ = librosa.pyin(
        audio,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"),
        sr=SR,
    )
    f0 = np.nan_to_num(f0, nan=0.0).astype(np.float32)

    return {
        "mfcc": mfcc,
        "delta_mfcc": delta_mfcc,
        "delta2_mfcc": delta2_mfcc,
        "log_mel": log_mel,
        "f0": f0,
        "raw": audio,
    }
