from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np

WHISPER_MODEL_DIR = Path(__file__).resolve().parents[1] / "models" / "whisper"
DEFAULT_WHISPER_MODEL = "base"


def whisper_status(model_dir: Path = WHISPER_MODEL_DIR) -> dict[str, object]:
    try:
        import torch
        import whisper  # noqa: F401
    except ImportError as exc:
        return {
            "backend": "unavailable",
            "model_state": "dependency_missing",
            "model_path": str(model_dir),
            "device": "cpu",
            "message": f"Whisper dependencies are not installed: {exc}",
        }

    has_files = model_dir.exists() and any(path.is_file() for path in model_dir.rglob("*"))
    return {
        "backend": "whisper",
        "model_state": "cache_present" if has_files else "missing",
        "model_path": str(model_dir),
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "message": "Whisper package is installed; runtime transcription is available when model assets are present.",
    }


@lru_cache(maxsize=1)
def _load_whisper_model(model_name: str = DEFAULT_WHISPER_MODEL):
    import whisper

    WHISPER_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    return whisper.load_model(model_name, download_root=str(WHISPER_MODEL_DIR))


def transcribe_audio_array(audio: np.ndarray, language: str | None = None) -> dict[str, object]:
    status = whisper_status()
    if status["backend"] != "whisper" or status["model_state"] == "missing":
        return {
            "text": "",
            "language": None,
            "backend": status["backend"],
            "message": status["message"],
        }

    try:
        model = _load_whisper_model()
        audio = np.asarray(audio, dtype=np.float32).flatten()
        result = model.transcribe(audio, language=language, fp16=status["device"] == "cuda")
    except Exception as exc:
        return {
            "text": "",
            "language": None,
            "backend": "unavailable",
            "message": f"Whisper transcription failed: {exc}",
        }

    return {
        "text": str(result.get("text", "")).strip(),
        "language": result.get("language"),
        "backend": "whisper",
        "message": "Transcription complete.",
    }


def transcribe_audio_file(_audio_path: str) -> dict[str, object]:
    status = whisper_status()
    return {
        "text": "",
        "language": None,
        "backend": status["backend"],
        "message": "File transcription is not exposed yet; use transcribe_audio_array for live audio windows.",
    }
