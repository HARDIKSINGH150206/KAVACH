from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

DEFAULT_CHECKPOINT_DIR = Path(__file__).resolve().parents[1] / "models" / "aasist_checkpoint"
CHECKPOINT_EXTENSIONS = {".pt", ".pth", ".ckpt", ".bin"}
AASIST_SAMPLE_RATE = 16_000
AASIST_TARGET_SAMPLES = 64_600
AASIST_MODEL_CONFIG = {
    "architecture": "AASIST",
    "nb_samp": AASIST_TARGET_SAMPLES,
    "first_conv": 128,
    "filts": [70, [1, 32], [32, 32], [32, 64], [64, 64]],
    "gat_dims": [64, 32],
    "pool_ratios": [0.5, 0.7, 0.5, 0.5],
    "temperatures": [2.0, 2.0, 100.0, 100.0],
}


@dataclass(frozen=True)
class AASISTStatus:
    backend: str
    checkpoint_path: str | None
    checkpoint_state: str
    device: str
    expected_sample_rate: int
    expected_samples: int
    message: str

    def model_dump(self) -> dict[str, object]:
        return asdict(self)


def find_checkpoint(checkpoint_dir: Path = DEFAULT_CHECKPOINT_DIR) -> Path | None:
    if not checkpoint_dir.exists():
        return None
    candidates = sorted(
        path for path in checkpoint_dir.rglob("*") if path.is_file() and path.suffix.lower() in CHECKPOINT_EXTENSIONS
    )
    return candidates[0] if candidates else None


class AASISTScorer:
    """AASIST inference wrapper with deterministic heuristic scoring fallback."""

    def __init__(self, checkpoint_dir: Path = DEFAULT_CHECKPOINT_DIR) -> None:
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_path = find_checkpoint(checkpoint_dir)
        self._model = None
        self._torch = None
        self._status = self._inspect_checkpoint()

    @property
    def status(self) -> AASISTStatus:
        return self._status

    def _inspect_checkpoint(self) -> AASISTStatus:
        if self.checkpoint_path is None:
            return AASISTStatus(
                backend="heuristic",
                checkpoint_path=None,
                checkpoint_state="missing",
                device="cpu",
                expected_sample_rate=AASIST_SAMPLE_RATE,
                expected_samples=AASIST_TARGET_SAMPLES,
                message="No AASIST checkpoint found; heuristic audio scorer is active.",
            )

        try:
            import torch

            from backend.audio.aasist_model import Model
        except ImportError as exc:
            return AASISTStatus(
                backend="heuristic",
                checkpoint_path=str(self.checkpoint_path),
                checkpoint_state="present_unvalidated",
                device="cpu",
                expected_sample_rate=AASIST_SAMPLE_RATE,
                expected_samples=AASIST_TARGET_SAMPLES,
                message=f"AASIST dependency is not installed: {exc}; heuristic audio scorer is active.",
            )

        device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            checkpoint = torch.load(self.checkpoint_path, map_location=device)
            state_dict = normalize_checkpoint_state_dict(checkpoint)
            model = Model(AASIST_MODEL_CONFIG).to(device)
            model.load_state_dict(state_dict)
            model.eval()
        except Exception as exc:
            return AASISTStatus(
                backend="heuristic",
                checkpoint_path=str(self.checkpoint_path),
                checkpoint_state="invalid",
                device=device,
                expected_sample_rate=AASIST_SAMPLE_RATE,
                expected_samples=AASIST_TARGET_SAMPLES,
                message=f"Checkpoint could not be loaded by PyTorch: {exc}",
            )

        self._model = model
        self._torch = torch
        return AASISTStatus(
            backend="aasist",
            checkpoint_path=str(self.checkpoint_path),
            checkpoint_state="validated",
            device=device,
            expected_sample_rate=AASIST_SAMPLE_RATE,
            expected_samples=AASIST_TARGET_SAMPLES,
            message="AASIST checkpoint loaded; neural audio anti-spoofing scorer is active.",
        )

    def score(self, audio: np.ndarray) -> tuple[float, AASISTStatus]:
        audio = prepare_aasist_audio(audio)
        if audio.size == 0:
            return 0.0, self.status
        if self._model is not None and self._torch is not None:
            try:
                return self._score_aasist(audio), self.status
            except Exception:
                pass

        return heuristic_audio_score(audio), self.status

    def _score_aasist(self, audio: np.ndarray) -> float:
        tensor = self._torch.from_numpy(audio).float().unsqueeze(0).to(self.status.device)
        with self._torch.no_grad():
            _, logits = self._model(tensor)
            probabilities = self._torch.softmax(logits, dim=1)
            spoof_probability = float(probabilities[0, 0].detach().cpu().item())
        return round(float(np.clip(spoof_probability, 0.0, 1.0)), 3)


def heuristic_audio_score(audio: np.ndarray) -> float:
    """Return deterministic artifact-risk fallback when AASIST is unavailable."""
    if audio.size == 0:
        return 0.0
    spectrum = np.abs(np.fft.rfft(audio * np.hanning(len(audio))))
    freqs = np.fft.rfftfreq(len(audio), d=1 / AASIST_SAMPLE_RATE)
    total = float(np.sum(spectrum) + 1e-9)
    high_band = float(np.sum(spectrum[freqs > 2_800]) / total)
    clipping = float(np.mean(np.abs(audio) > 0.11))
    periodicity = float(np.std(np.diff(np.signbit(audio))))

    score = (high_band * 7.5) + (clipping * 1.8) + (periodicity * 0.35)
    return round(float(np.clip(score, 0.03, 0.96)), 3)


def normalize_checkpoint_state_dict(checkpoint: object) -> dict[str, object]:
    """Extract and normalize a PyTorch state_dict from common checkpoint layouts."""
    if not isinstance(checkpoint, dict):
        raise ValueError("checkpoint is not a state_dict or checkpoint dictionary")

    state_dict = checkpoint
    for key in ("state_dict", "model_state_dict", "model"):
        candidate = checkpoint.get(key)
        if isinstance(candidate, dict):
            state_dict = candidate
            break

    normalized = {}
    for key, value in state_dict.items():
        if not isinstance(key, str):
            raise ValueError("checkpoint contains non-string parameter names")
        normalized[key.removeprefix("module.")] = value
    return normalized


def prepare_aasist_audio(audio: np.ndarray) -> np.ndarray:
    """Return mono float32 audio padded or trimmed to AASIST's expected sample count."""
    audio = np.asarray(audio, dtype=np.float32).flatten()
    if audio.size == 0:
        return np.zeros(AASIST_TARGET_SAMPLES, dtype=np.float32)
    audio = np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0)
    peak = float(np.max(np.abs(audio)))
    if peak > 1.0:
        audio = audio / peak
    if audio.size < AASIST_TARGET_SAMPLES:
        audio = np.pad(audio, (0, AASIST_TARGET_SAMPLES - audio.size))
    return audio[:AASIST_TARGET_SAMPLES].astype(np.float32, copy=False)
