from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "backend" / "models"
AASIST_DIR = MODELS_DIR / "aasist_checkpoint"
WHISPER_DIR = MODELS_DIR / "whisper"
MURIL_DIR = MODELS_DIR / "muril"
SMS_MODEL = MODELS_DIR / "sms_classifier.pkl"
MANIFEST = MODELS_DIR / "manifest.json"
AASIST_URL = "https://raw.githubusercontent.com/clovaai/aasist/main/models/weights/AASIST.pth"
AASIST_OUTPUT = AASIST_DIR / "AASIST.pth"


@dataclass(frozen=True)
class ModelAsset:
    name: str
    path: Path
    required: bool
    status: str
    note: str

    def to_json(self) -> dict[str, object]:
        payload = asdict(self)
        payload["path"] = str(self.path.relative_to(ROOT))
        return payload


def _has_files(path: Path) -> bool:
    return path.exists() and any(child.is_file() for child in path.rglob("*"))


def ensure_model_dirs() -> None:
    for path in (MODELS_DIR, AASIST_DIR, WHISPER_DIR, MURIL_DIR):
        path.mkdir(parents=True, exist_ok=True)


def inspect_assets() -> list[ModelAsset]:
    ensure_model_dirs()
    return [
        ModelAsset(
            name="sms_classifier",
            path=SMS_MODEL,
            required=True,
            status="ready" if SMS_MODEL.exists() else "missing",
            note="Train with scripts/train_sms_classifier.py if missing.",
        ),
        ModelAsset(
            name="aasist",
            path=AASIST_DIR,
            required=False,
            status="ready" if _has_files(AASIST_DIR) else "missing",
            note="Download with --download-aasist or place a compatible AASIST checkpoint here.",
        ),
        ModelAsset(
            name="whisper",
            path=WHISPER_DIR,
            required=False,
            status="ready" if _has_files(WHISPER_DIR) else "missing",
            note="Optional STT asset cache; runtime transcription uses it when openai-whisper is installed.",
        ),
        ModelAsset(
            name="muril",
            path=MURIL_DIR,
            required=False,
            status="ready" if _has_files(MURIL_DIR) else "missing",
            note="Optional HuggingFace model cache; MuRIL is not wired into runtime yet.",
        ),
    ]


def write_manifest(assets: list[ModelAsset]) -> None:
    ensure_model_dirs()
    MANIFEST.write_text(
        json.dumps({"assets": [asset.to_json() for asset in assets]}, indent=2) + "\n",
        encoding="utf-8",
    )


def download_whisper(model_name: str = "base") -> str:
    try:
        import whisper
    except ImportError:
        return "skipped: openai-whisper is not installed"

    WHISPER_DIR.mkdir(parents=True, exist_ok=True)
    whisper.load_model(model_name, download_root=str(WHISPER_DIR))
    return f"downloaded: whisper {model_name}"


def download_aasist(url: str = AASIST_URL) -> str:
    import requests

    AASIST_DIR.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    AASIST_OUTPUT.write_bytes(response.content)
    return f"downloaded: {AASIST_OUTPUT.relative_to(ROOT)}"


def download_muril(model_name: str = "google/muril-base-cased") -> str:
    try:
        from transformers import AutoModel, AutoTokenizer
    except ImportError:
        return "skipped: transformers is not installed"

    MURIL_DIR.mkdir(parents=True, exist_ok=True)
    AutoTokenizer.from_pretrained(model_name, cache_dir=str(MURIL_DIR))
    AutoModel.from_pretrained(model_name, cache_dir=str(MURIL_DIR))
    return f"downloaded: {model_name}"


def print_status(assets: list[ModelAsset]) -> None:
    for asset in assets:
        marker = "OK" if asset.status == "ready" else "--"
        print(f"{marker} {asset.name:15} {asset.status:8} {asset.path.relative_to(ROOT)}")
        print(f"   {asset.note}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare and inspect KAVACH model asset directories.")
    parser.add_argument("--download-aasist", action="store_true", help="Download official AASIST pretrained weights")
    parser.add_argument(
        "--download-whisper", action="store_true", help="Download Whisper through openai-whisper if installed"
    )
    parser.add_argument("--whisper-model", default="base", help="Whisper model name for --download-whisper")
    parser.add_argument(
        "--download-muril", action="store_true", help="Download MuRIL through transformers if installed"
    )
    parser.add_argument(
        "--muril-model", default="google/muril-base-cased", help="HuggingFace model id for --download-muril"
    )
    args = parser.parse_args()

    ensure_model_dirs()
    if args.download_aasist:
        print(download_aasist())
    if args.download_whisper:
        print(download_whisper(args.whisper_model))
    if args.download_muril:
        print(download_muril(args.muril_model))

    assets = inspect_assets()
    write_manifest(assets)
    print_status(assets)
    print(f"Manifest written to {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
