from __future__ import annotations

from pathlib import Path

MURIL_MODEL_DIR = Path(__file__).resolve().parents[1] / "models" / "muril"

PHRASE_CATEGORIES = {
    "authority": (
        "cbi",
        "police",
        "crime branch",
        "court notice",
        "case file",
        "digital arrest",
        "rbi",
        "bank officer",
    ),
    "urgency": (
        "abhi",
        "turant",
        "immediate",
        "last warning",
        "within 10 minutes",
        "aaj hi",
        "right now",
        "final notice",
    ),
    "account_risk": (
        "account band",
        "account block",
        "account blocked",
        "account suspend",
        "kyc expire",
        "card block",
    ),
    "credential_theft": ("otp", "share otp", "otp batao", "verify otp", "pin", "password"),
    "legal_threat": ("arrest", "legal action", "penalty", "fine", "fir"),
    "payment_pressure": ("pay now", "transfer", "upi", "wallet", "recharge now", "send money"),
}


def muril_status(model_dir: Path = MURIL_MODEL_DIR) -> dict[str, object]:
    try:
        import torch
        import transformers  # noqa: F401
    except ImportError as exc:
        return {
            "backend": "rule_fallback",
            "model_state": "dependency_missing",
            "model_path": str(model_dir),
            "device": "cpu",
            "message": f"MuRIL dependencies are not installed: {exc}",
        }

    has_files = model_dir.exists() and any(path.is_file() for path in model_dir.rglob("*"))
    return {
        "backend": "rule_fallback",
        "model_state": "cache_present" if has_files else "missing",
        "model_path": str(model_dir),
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "message": "MuRIL inference is not wired yet; rule-based urgency scoring is active.",
    }


def muril_infer_status(enabled: bool) -> dict[str, object]:
    status = muril_status()
    if not enabled:
        status["message"] = "MuRIL runtime is disabled by config; rule-based urgency scoring is active."
        status["enabled"] = False
        return status
    status["enabled"] = True
    if status["model_state"] == "cache_present":
        status["message"] = "MuRIL runtime is enabled, but model inference path still falls back to rules."
    return status


def score_transcript(transcript: str) -> dict[str, object]:
    text = transcript.strip()
    text_lower = text.lower()
    matched: list[str] = []
    category_scores: dict[str, float] = {}

    for category, phrases in PHRASE_CATEGORIES.items():
        hits = [phrase for phrase in phrases if phrase in text_lower]
        if hits:
            matched.extend(f"{category}:{phrase}" for phrase in hits)
            category_scores[category] = min(len(hits) / 2.0, 1.0)
        else:
            category_scores[category] = 0.0

    category_weight = {
        "authority": 0.18,
        "urgency": 0.18,
        "account_risk": 0.18,
        "credential_theft": 0.20,
        "legal_threat": 0.14,
        "payment_pressure": 0.12,
    }
    score = sum(category_scores[category] * weight for category, weight in category_weight.items())
    if len(matched) >= 4:
        score += 0.15
    if len(text) < 8:
        score *= 0.5

    urgency = round(min(score, 1.0), 3)
    return {
        "urgency_score": urgency,
        "backend": "rule_fallback",
        "matched_phrases": matched,
        "category_scores": {key: round(value, 3) for key, value in category_scores.items()},
        "text_preview": text[:160],
    }


def urgency_score(transcript: str) -> float:
    return float(score_transcript(transcript)["urgency_score"])
