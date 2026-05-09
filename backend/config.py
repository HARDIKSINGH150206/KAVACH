from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = ROOT / "kavach.yml"


@dataclass(frozen=True)
class FusionConfig:
    audio_weight: float = 0.55
    sms_weight: float = 0.45
    transcript_weight: float = 0.20
    thresholds: dict[str, float] | None = None

    def resolved_thresholds(self) -> dict[str, float]:
        return self.thresholds or {"suspicious": 0.30, "high": 0.55, "critical": 0.80}


@dataclass(frozen=True)
class ModelConfig:
    aasist_checkpoint_dir: str = "backend/models/aasist_checkpoint"
    sms_classifier: str = "backend/models/sms_classifier.pkl"
    muril_enabled: bool = False


@dataclass(frozen=True)
class LoggingConfig:
    level: str = "INFO"
    directory: str = "logs"
    threat_events_file: str = "threat_events.jsonl"


@dataclass(frozen=True)
class SecurityConfig:
    auth_mode: str = "none"
    api_key: str = ""
    bearer_token: str = ""
    rate_limit_per_minute: int = 120


@dataclass(frozen=True)
class AppConfig:
    audio_source: str = "demo"
    fusion: FusionConfig = FusionConfig()
    models: ModelConfig = ModelConfig()
    logging: LoggingConfig = LoggingConfig()
    security: SecurityConfig = SecurityConfig()
    cors_origins: tuple[str, ...] = (
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:5178",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
        "http://127.0.0.1:5177",
        "http://127.0.0.1:5178",
    )


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> AppConfig:
    data = _read_yaml(path)
    fusion_data = data.get("fusion") if isinstance(data.get("fusion"), dict) else {}
    model_data = data.get("models") if isinstance(data.get("models"), dict) else {}
    logging_data = data.get("logging") if isinstance(data.get("logging"), dict) else {}
    security_data = data.get("security") if isinstance(data.get("security"), dict) else {}

    audio_source = str(os.getenv("KAVACH_AUDIO_SOURCE", data.get("audio_source", "demo"))).strip().lower()
    if audio_source not in {"demo", "mic"}:
        audio_source = "demo"

    thresholds = fusion_data.get("thresholds") if isinstance(fusion_data.get("thresholds"), dict) else None
    resolved_thresholds = None
    if thresholds:
        resolved_thresholds = {
            "suspicious": float(thresholds.get("suspicious", 0.30)),
            "high": float(thresholds.get("high", 0.55)),
            "critical": float(thresholds.get("critical", 0.80)),
        }

    cors_csv = str(
        os.getenv(
            "KAVACH_CORS_ORIGINS",
            data.get(
                "cors_origins",
                "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173",
            ),
        )
    )
    cors_origins = tuple(origin.strip() for origin in cors_csv.split(",") if origin.strip())

    return AppConfig(
        audio_source=audio_source,
        fusion=FusionConfig(
            audio_weight=float(fusion_data.get("audio_weight", 0.55)),
            sms_weight=float(fusion_data.get("sms_weight", 0.45)),
            transcript_weight=float(fusion_data.get("transcript_weight", 0.20)),
            thresholds=resolved_thresholds,
        ),
        models=ModelConfig(
            aasist_checkpoint_dir=str(model_data.get("aasist_checkpoint_dir", "backend/models/aasist_checkpoint")),
            sms_classifier=str(model_data.get("sms_classifier", "backend/models/sms_classifier.pkl")),
            muril_enabled=str(os.getenv("KAVACH_MURIL_ENABLED", model_data.get("muril_enabled", False))).lower()
            in {"1", "true", "yes", "on"},
        ),
        logging=LoggingConfig(
            level=str(os.getenv("KAVACH_LOG_LEVEL", logging_data.get("level", "INFO"))).upper(),
            directory=str(os.getenv("KAVACH_LOG_DIR", logging_data.get("directory", "logs"))),
            threat_events_file=str(logging_data.get("threat_events_file", "threat_events.jsonl")),
        ),
        security=SecurityConfig(
            auth_mode=str(os.getenv("KAVACH_AUTH_MODE", security_data.get("auth_mode", "none"))).strip().lower(),
            api_key=str(os.getenv("KAVACH_API_KEY", security_data.get("api_key", ""))).strip(),
            bearer_token=str(os.getenv("KAVACH_BEARER_TOKEN", security_data.get("bearer_token", ""))).strip(),
            rate_limit_per_minute=int(
                os.getenv("KAVACH_RATE_LIMIT_PER_MINUTE", security_data.get("rate_limit_per_minute", 120))
            ),
        ),
        cors_origins=cors_origins,
    )
