from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import joblib

from .rule_engine import classify_scam_type
from .url_scorer import extract_urls, score_url

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "sms_classifier.pkl"

PHISHING_TERMS = {
    "blocked",
    "suspended",
    "kyc",
    "challan",
    "pay",
    "fine",
    "otp",
    "verify",
    "urgent",
    "turant",
    "abhi",
    "legal",
    "penalty",
    "recharge",
    "upi",
    "refund",
    "cashback",
    "parcel",
    "delivery",
    "disconnection",
    "loan",
}

CONFIDENCE_BANDS = {
    "low": 0.35,
    "medium": 0.65,
}


def _lexical_score(text: str) -> float:
    tokens = {token.strip(".,:;!?()[]{}\"'").lower() for token in text.split()}
    hits = len(tokens & PHISHING_TERMS)
    return min(hits / 5.0, 1.0)


def _load_bundle() -> object | None:
    if not MODEL_PATH.exists():
        return None
    try:
        return joblib.load(MODEL_PATH)
    except Exception:
        return None


@lru_cache(maxsize=1)
def _load_model() -> object | None:
    bundle = _load_bundle()
    if bundle is None:
        return None
    if isinstance(bundle, dict) and "pipeline" in bundle:
        return bundle["pipeline"]
    return bundle


def sms_model_status() -> dict[str, object]:
    model = _load_model()
    if model is None:
        state = "missing" if not MODEL_PATH.exists() else "unreadable"
        return {
            "backend": "lexical_fallback",
            "model_path": str(MODEL_PATH),
            "model_state": state,
            "fallback": "lexical_fallback",
        }

    bundle = _load_bundle()
    metadata = bundle.get("metadata", {}) if isinstance(bundle, dict) else {}
    return {
        "backend": "trained_model",
        "model_path": str(MODEL_PATH),
        "model_state": "ready",
        "fallback": "lexical_fallback",
        "metadata": metadata,
    }


def _model_score(text: str) -> tuple[float, str]:
    model = _load_model()
    if model is None:
        return _lexical_score(text), "lexical_fallback"

    if hasattr(model, "predict_proba"):
        probability = model.predict_proba([text])[0][1]
        return float(probability), "trained_model"

    if hasattr(model, "decision_function"):
        decision = float(model.decision_function([text])[0])
        return 1.0 / (1.0 + pow(2.718281828, -decision)), "trained_model"

    return _lexical_score(text), "lexical_fallback"


def score_sms(text: str) -> dict:
    rules = classify_scam_type(text)
    urls = extract_urls(text)
    url_results = [score_url(url) for url in urls]
    url_risk = max((result["url_risk"] for result in url_results), default=0.0)
    url_flags = [flag for result in url_results for flag in result["flags"]]
    # Extract entropy and TLD for frontend demo
    entropy = max((result.get("entropy", 0.0) for result in url_results), default=0.0)
    tld = next((result.get("tld", ".in") for result in url_results), ".in")

    ml_score, ml_source = _model_score(text)

    # Simple highlight generation for frontend
    highlights = []
    tokens = text.split()
    for token in tokens:
        clean = token.strip(".,:;!?()[]{}\"'").lower()
        if clean in PHISHING_TERMS:
            highlights.append({"word": clean, "score": "+0.15"})

    sms_score = (0.38 * rules["rule_score"]) + (0.27 * url_risk) + (0.35 * ml_score)
    sms_score = round(min(sms_score, 1.0), 3)
    confidence_band = "high"
    if sms_score < CONFIDENCE_BANDS["low"]:
        confidence_band = "low"
    elif sms_score < CONFIDENCE_BANDS["medium"]:
        confidence_band = "medium"
    return {
        "sms_score": sms_score,
        "riskScore": sms_score,  # Alias for frontend
        "ml_score": round(ml_score, 3),
        "ml_source": ml_source,
        "rule_score": rules["rule_score"],
        "url_risk": round(url_risk, 3),
        "entropy": entropy,
        "tld": tld,
        "highlights": highlights,
        "confidence_band": confidence_band,
        "scam_type": rules["scam_type"],
        "matched_rules": rules["matched_rules"],
        "url_flags": url_flags,
        "text_preview": text[:120],
        "text": text,  # Alias for frontend
    }
