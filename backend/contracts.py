from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ThreatLevel = Literal["SAFE", "SUSPICIOUS", "HIGH", "CRITICAL"]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    mode: Literal["demo", "mic"]
    override: dict | None
    models: dict[str, object]
    readiness: dict[str, object]


class ConfigResponse(BaseModel):
    audio_weight: float
    sms_weight: float
    transcript_weight: float
    thresholds: dict[str, float]
    audio_source: Literal["demo", "mic"]


class MockSmsRequest(BaseModel):
    text: str = Field(min_length=1, max_length=500)


class MockSmsResponse(BaseModel):
    accepted: bool
    error: str | None = None


class ScoreSmsRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1_000)


class ScoreSmsResponse(BaseModel):
    sms_score: float
    riskScore: float = Field(default=0.0)
    ml_score: float
    ml_source: str
    rule_score: float
    url_risk: float
    entropy: float = Field(default=0.0)
    tld: str = Field(default=".in")
    highlights: list[dict] = Field(default_factory=list)
    confidence_band: str
    scam_type: str | None
    matched_rules: list[str]
    url_flags: list[str]
    text_preview: str
    text: str = Field(default="")


class ScoreAudioRequest(BaseModel):
    samples: list[float] = Field(min_length=1, max_length=192_000)
    sample_rate: int = Field(default=16_000, ge=8_000, le=96_000)


class ScoreAudioResponse(BaseModel):
    audio_score: float
    backend: str
    checkpoint_state: str
    latency_ms: float
    sample_rate: int
    summary: dict[str, float | int]
    message: str


class ScoreTranscriptRequest(BaseModel):
    transcript: str = Field(min_length=1, max_length=2_000)


class ScoreTranscriptResponse(BaseModel):
    urgency_score: float
    backend: str
    matched_phrases: list[str]
    category_scores: dict[str, float]
    text_preview: str


class ScoreFusionRequest(BaseModel):
    audio_score: float = Field(ge=-1.0, le=1.0)
    sms_score: float = Field(ge=-1.0, le=1.0)
    transcript_score: float = Field(default=-1.0, ge=-1.0, le=1.0)


class DemoScenarioRequest(BaseModel):
    scenario: Literal["auto", "safe", "high", "critical"]


class DemoScenarioResponse(BaseModel):
    accepted: bool
    scenario: str
    override: dict | None
    error: str | None = None


class AudioEvent(BaseModel):
    type: Literal["audio"]
    audio_score: float
    latency_ms: float
    spoof_hint: bool
    timestamp: float


class SmsEvent(BaseModel):
    type: Literal["sms"]
    sms_score: float
    riskScore: float = Field(default=0.0)
    ml_score: float
    ml_source: str
    rule_score: float
    url_risk: float
    entropy: float = Field(default=0.0)
    tld: str = Field(default=".in")
    highlights: list[dict] = Field(default_factory=list)
    scam_type: str | None
    matched_rules: list[str]
    url_flags: list[str]
    text_preview: str
    text: str = Field(default="")
    timestamp: float


class TranscriptEvent(BaseModel):
    type: Literal["transcript"]
    transcript: str
    urgency_score: float
    backend: str
    matched_phrases: list[str]
    timestamp: float


class FusionEvent(BaseModel):
    type: Literal["fusion"]
    audio_score: float
    sms_score: float
    transcript_score: float
    threat_score: float
    threat_level: ThreatLevel
    color: str
    formula_str: str
    explanation: list[str]
    scenario: str
    timestamp: float
