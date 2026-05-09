from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np


class ThreatLevel(str, Enum):
    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


THREAT_COLORS = {
    ThreatLevel.SAFE: "#1F9D55",
    ThreatLevel.SUSPICIOUS: "#B7791F",
    ThreatLevel.HIGH: "#C05621",
    ThreatLevel.CRITICAL: "#C53030",
}
AUDIO_WEIGHT = 0.55
SMS_WEIGHT = 0.45
TRANSCRIPT_WEIGHT = 0.20
THRESHOLDS = {
    "suspicious": 0.30,
    "high": 0.55,
    "critical": 0.80,
}


def configure_fusion(
    audio_weight: float,
    sms_weight: float,
    thresholds: dict[str, float] | None = None,
    transcript_weight: float | None = None,
) -> None:
    global AUDIO_WEIGHT, SMS_WEIGHT, TRANSCRIPT_WEIGHT, THRESHOLDS
    AUDIO_WEIGHT = audio_weight
    SMS_WEIGHT = sms_weight
    if transcript_weight is not None:
        TRANSCRIPT_WEIGHT = transcript_weight
    if thresholds is not None:
        THRESHOLDS = thresholds


@dataclass(frozen=True)
class FusionResult:
    audio_score: float
    sms_score: float
    transcript_score: float
    threat_score: float
    threat_level: ThreatLevel
    color: str
    formula_str: str
    explanation: list[str]


def _level(score: float) -> ThreatLevel:
    if score >= THRESHOLDS["critical"]:
        return ThreatLevel.CRITICAL
    if score >= THRESHOLDS["high"]:
        return ThreatLevel.HIGH
    if score >= THRESHOLDS["suspicious"]:
        return ThreatLevel.SUSPICIOUS
    return ThreatLevel.SAFE


def fuse(audio_score: float, sms_score: float, transcript_score: float = -1.0) -> FusionResult:
    signals = [
        ("audio", audio_score, AUDIO_WEIGHT),
        ("sms", sms_score, SMS_WEIGHT),
        ("transcript", transcript_score, TRANSCRIPT_WEIGHT),
    ]
    available = [(name, float(np.clip(score, 0.0, 1.0)), weight) for name, score, weight in signals if score >= 0]

    clean_audio = float(np.clip(audio_score, 0.0, 1.0)) if audio_score >= 0 else -1.0
    clean_sms = float(np.clip(sms_score, 0.0, 1.0)) if sms_score >= 0 else -1.0
    clean_transcript = float(np.clip(transcript_score, 0.0, 1.0)) if transcript_score >= 0 else -1.0

    if not available:
        threat_score = 0.0
        formula = "threat = 0.000 (no signals available)"
    elif len(available) == 1:
        name, score, _ = available[0]
        threat_score = score
        formula = f"threat = {name} only = {score:.3f}"
    else:
        weight_total = sum(weight for _, _, weight in available)
        weighted_parts = [(name, score, weight / weight_total) for name, score, weight in available]
        threat_score = sum(score * normalized_weight for _, score, normalized_weight in weighted_parts)
        formula_terms = " + ".join(f"{weight:.2f} x {score:.2f} {name}" for name, score, weight in weighted_parts)
        formula = f"threat = {formula_terms} = {threat_score:.3f}"

    threat_score = round(float(np.clip(threat_score, 0.0, 1.0)), 3)
    level = _level(threat_score)

    explanation = []
    if clean_audio > 0.6:
        explanation.append(f"Voice synthesis artifacts detected ({clean_audio:.2f})")
    if clean_sms > 0.5:
        explanation.append(f"SMS phishing pattern matched ({clean_sms:.2f})")
    if clean_transcript > 0.45:
        explanation.append(f"Call transcript urgency detected ({clean_transcript:.2f})")

    return FusionResult(
        audio_score=round(clean_audio, 3),
        sms_score=round(clean_sms, 3),
        transcript_score=round(clean_transcript, 3),
        threat_score=threat_score,
        threat_level=level,
        color=THREAT_COLORS[level],
        formula_str=formula,
        explanation=explanation,
    )
