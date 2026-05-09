from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

from backend.config import ROOT, AppConfig
from backend.sms.evaluation import profile_dataset
from scripts.download_models import inspect_assets
from scripts.train_sms_classifier import DEFAULT_LEGIT_CSV, DEFAULT_PHISHING_CSV, load_training_data

PYTHON_DEPENDENCIES = {
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "numpy": "numpy",
    "scipy": "scipy",
    "librosa": "librosa",
    "sounddevice": "sounddevice",
    "scikit-learn": "sklearn",
    "pandas": "pandas",
    "joblib": "joblib",
    "tldextract": "tldextract",
    "requests": "requests",
    "httpx": "httpx",
    "PyYAML": "yaml",
}


def _state(ok: bool) -> str:
    return "ready" if ok else "missing"


def dependency_status() -> dict[str, str]:
    statuses = {}
    for name, module in PYTHON_DEPENDENCIES.items():
        try:
            importlib.import_module(module)
        except Exception:
            statuses[name] = "unavailable"
        else:
            statuses[name] = "ready"
    return statuses


def dataset_status(
    phishing_csv: Path = DEFAULT_PHISHING_CSV,
    legit_csv: Path = DEFAULT_LEGIT_CSV,
) -> dict[str, Any]:
    try:
        data = load_training_data(phishing_csv, legit_csv)
        profile = profile_dataset(data).to_dict()
    except Exception as exc:
        return {
            "state": "unreadable",
            "phishing_csv": (
                str(phishing_csv.relative_to(ROOT)) if phishing_csv.is_relative_to(ROOT) else str(phishing_csv)
            ),
            "legit_csv": str(legit_csv.relative_to(ROOT)) if legit_csv.is_relative_to(ROOT) else str(legit_csv),
            "error": str(exc),
        }

    return {
        "state": profile["readiness_level"],
        "phishing_csv": str(phishing_csv.relative_to(ROOT)),
        "legit_csv": str(legit_csv.relative_to(ROOT)),
        **profile,
    }


def frontend_status() -> dict[str, Any]:
    frontend_dir = ROOT / "frontend"
    package_json = frontend_dir / "package.json"
    lockfile = frontend_dir / "package-lock.json"
    node_modules = frontend_dir / "node_modules"

    return {
        "state": _state(package_json.exists() and lockfile.exists()),
        "package_json": str(package_json.relative_to(ROOT)),
        "lockfile": str(lockfile.relative_to(ROOT)),
        "dependencies_installed": node_modules.exists(),
    }


def config_status(config: AppConfig) -> dict[str, Any]:
    return {
        "audio_source": config.audio_source,
        "fusion": {
            "audio_weight": config.fusion.audio_weight,
            "sms_weight": config.fusion.sms_weight,
            "transcript_weight": config.fusion.transcript_weight,
            "thresholds": config.fusion.resolved_thresholds(),
        },
        "logging": {
            "level": config.logging.level,
            "directory": config.logging.directory,
            "threat_events_file": config.logging.threat_events_file,
        },
    }


def readiness_report(config: AppConfig) -> dict[str, Any]:
    dependencies = dependency_status()
    assets = [asset.to_json() for asset in inspect_assets()]
    required_assets_ready = all(asset["status"] == "ready" for asset in assets if asset["required"])
    required_dependencies_ready = all(state == "ready" for state in dependencies.values())
    mic_dependencies_ready = dependencies.get("sounddevice") == "ready"

    blocking = []
    if not required_dependencies_ready:
        if config.audio_source == "demo" and mic_dependencies_ready is False:
            # sounddevice is only required in mic mode
            blocking_dependencies_ready = all(
                state == "ready" for name, state in dependencies.items() if name != "sounddevice"
            )
            if not blocking_dependencies_ready:
                blocking.append("One or more Python runtime dependencies are missing.")
        else:
            blocking.append("One or more Python runtime dependencies are missing.")
    if config.audio_source == "mic" and not mic_dependencies_ready:
        blocking.append("Microphone mode requires the sounddevice dependency.")
    if not blocking and config.audio_source == "demo" and not mic_dependencies_ready:
        optional_warnings = ["Microphone mode is unavailable because sounddevice is not installed."]
    else:
        optional_warnings = []
    if not blocking and required_dependencies_ready is False and config.audio_source == "demo":
        # non-blocking demo mode can still report partial dependency state
        pass
    if not required_assets_ready:
        blocking.append("Required model assets are missing.")

    dataset = dataset_status()
    return {
        "state": "ready" if not blocking else "attention_required",
        "blocking": blocking,
        "warnings": optional_warnings,
        "dependencies": dependencies,
        "models": assets,
        "dataset": dataset,
        "frontend": frontend_status(),
        "config": config_status(config),
    }
