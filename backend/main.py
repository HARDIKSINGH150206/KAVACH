# KAVACH Backend API - Production Version
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.audio.aasist_infer import AASISTScorer
from backend.audio.capture import audio_windows
from backend.audio.features import extract_features
from backend.audio.scoring import audio_summary, normalize_audio_samples
from backend.audio.urgency_nlp import muril_infer_status, score_transcript
from backend.audio.whisper_stt import transcribe_audio_array, whisper_status
from backend.config import load_config
from backend.contracts import (
    AudioEvent,
    ConfigResponse,
    DemoScenarioRequest,
    DemoScenarioResponse,
    FusionEvent,
    HealthResponse,
    MockSmsRequest,
    MockSmsResponse,
    ScoreAudioRequest,
    ScoreAudioResponse,
    ScoreFusionRequest,
    ScoreSmsRequest,
    ScoreSmsResponse,
    ScoreTranscriptRequest,
    ScoreTranscriptResponse,
    SmsEvent,
    TranscriptEvent,
)
from backend.events import append_threat_event
from backend.fusion import engine as fusion_engine
from backend.fusion.engine import configure_fusion, fuse
from backend.logging_config import configure_logging
from backend.readiness import readiness_report
from backend.sms.classifier import score_sms, sms_model_status
from backend.sms.ingestion import demo_sms_pump, get_next_sms, inject_mock_sms

logger = logging.getLogger("kavach.api")
aasist = AASISTScorer()
_pump_task: asyncio.Task | None = None
_demo_override: dict | None = None
APP_CONFIG = load_config()
AUDIO_SOURCE = APP_CONFIG.audio_source
configure_logging(APP_CONFIG.logging.level)
configure_fusion(
    APP_CONFIG.fusion.audio_weight,
    APP_CONFIG.fusion.sms_weight,
    APP_CONFIG.fusion.resolved_thresholds(),
    transcript_weight=APP_CONFIG.fusion.transcript_weight,
)

DEMO_SCENARIOS = {
    "auto": None,
    "safe": {
        "audio_score": 0.08,
        "sms_score": 0.05,
        "label": "Normal call + legitimate SMS",
    },
    "high": {
        "audio_score": 0.34,
        "sms_score": 0.88,
        "label": "Phishing SMS drives high risk",
    },
    "critical": {
        "audio_score": 0.91,
        "sms_score": 0.84,
        "label": "Deepfake voice + phishing SMS",
    },
}
DEMO_TRANSCRIPTS = {
    "high": "Account block ho jayega. KYC verify karo abhi.",
    "critical": "CBI case file opened. Share OTP immediately or legal action will start.",
}
_rate_limit_windows: dict[str, deque[float]] = defaultdict(deque)
_metrics = {"http_requests_total": 0, "http_4xx_total": 0, "http_5xx_total": 0}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global _pump_task
    logger.info("Starting KAVACH API in %s audio mode", AUDIO_SOURCE)
    if _pump_task is None:
        _pump_task = asyncio.create_task(demo_sms_pump())
    try:
        yield
    finally:
        if _pump_task:
            _pump_task.cancel()
        logger.info("KAVACH API shutdown complete")


app = FastAPI(title="KAVACH API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(APP_CONFIG.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    logger.info("request_id=%s method=%s path=%s", request_id, request.method, request.url.path)

    path = request.url.path
    if path in {"/docs", "/openapi.json", "/redoc"}:
        response = await call_next(request)
        _metrics["http_requests_total"] += 1
        if 400 <= response.status_code < 500:
            _metrics["http_4xx_total"] += 1
        if response.status_code >= 500:
            _metrics["http_5xx_total"] += 1
        response.headers["x-request-id"] = request_id
        return response

    auth_mode = APP_CONFIG.security.auth_mode
    if auth_mode == "api_key":
        api_key = APP_CONFIG.security.api_key
        supplied = request.headers.get("x-api-key", "")
        if not api_key or supplied != api_key:
            _metrics["http_requests_total"] += 1
            _metrics["http_4xx_total"] += 1
            return JSONResponse(
                status_code=401, content={"detail": "invalid API key"}, headers={"x-request-id": request_id}
            )
    elif auth_mode == "bearer":
        token = APP_CONFIG.security.bearer_token
        auth_header = request.headers.get("authorization", "")
        expected = f"Bearer {token}" if token else ""
        if not token or auth_header != expected:
            _metrics["http_requests_total"] += 1
            _metrics["http_4xx_total"] += 1
            return JSONResponse(
                status_code=401, content={"detail": "invalid bearer token"}, headers={"x-request-id": request_id}
            )

    limit = max(1, APP_CONFIG.security.rate_limit_per_minute)
    bucket_key = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - 60.0
    bucket = _rate_limit_windows[bucket_key]
    while bucket and bucket[0] < window_start:
        bucket.popleft()
    if len(bucket) >= limit:
        _metrics["http_requests_total"] += 1
        _metrics["http_4xx_total"] += 1
        return JSONResponse(
            status_code=429, content={"detail": "rate limit exceeded"}, headers={"x-request-id": request_id}
        )
    bucket.append(now)

    response = await call_next(request)
    _metrics["http_requests_total"] += 1
    if 400 <= response.status_code < 500:
        _metrics["http_4xx_total"] += 1
    if response.status_code >= 500:
        _metrics["http_5xx_total"] += 1
    response.headers["x-request-id"] = request_id
    return response


@app.get("/live")
@app.get("/api/v1/live")
def live() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/ready")
@app.get("/api/v1/ready")
def ready() -> dict[str, object]:
    report = readiness_report(APP_CONFIG)
    return {"status": "ready" if report["state"] == "ready" else "not_ready", "readiness": report}


@app.get("/metrics")
@app.get("/api/v1/metrics")
def metrics() -> dict[str, int]:
    return dict(_metrics)


@app.get("/health")
@app.get("/api/v1/health")
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        mode=AUDIO_SOURCE,
        override=_demo_override,
        models={
            "audio": aasist.status.model_dump(),
            "speech_to_text": whisper_status(),
            "urgency_nlp": muril_infer_status(APP_CONFIG.models.muril_enabled),
            "sms": sms_model_status(),
            "fusion": {
                "audio_weight": fusion_engine.AUDIO_WEIGHT,
                "sms_weight": fusion_engine.SMS_WEIGHT,
                "transcript_weight": fusion_engine.TRANSCRIPT_WEIGHT,
                "thresholds": fusion_engine.THRESHOLDS,
            },
        },
        readiness=readiness_report(APP_CONFIG),
    )


@app.get("/config")
@app.get("/api/v1/config")
def config() -> ConfigResponse:
    return ConfigResponse(
        audio_weight=fusion_engine.AUDIO_WEIGHT,
        sms_weight=fusion_engine.SMS_WEIGHT,
        transcript_weight=fusion_engine.TRANSCRIPT_WEIGHT,
        thresholds=fusion_engine.THRESHOLDS,
        audio_source=AUDIO_SOURCE,
    )


@app.post("/score/sms")
@app.post("/api/v1/score/sms")
async def score_sms_endpoint(payload: ScoreSmsRequest) -> ScoreSmsResponse:
    return ScoreSmsResponse(**score_sms(payload.text.strip()))


@app.post("/score/audio")
@app.post("/api/v1/score/audio")
async def score_audio_endpoint(payload: ScoreAudioRequest) -> ScoreAudioResponse:
    start = time.perf_counter()
    try:
        audio = normalize_audio_samples(payload.samples, payload.sample_rate)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    score, status = aasist.score(audio)
    latency_ms = (time.perf_counter() - start) * 1_000
    return ScoreAudioResponse(
        audio_score=score,
        backend=status.backend,
        checkpoint_state=status.checkpoint_state,
        latency_ms=round(latency_ms, 1),
        sample_rate=status.expected_sample_rate,
        summary=audio_summary(audio),
        message=status.message,
    )


@app.post("/score/transcript")
@app.post("/api/v1/score/transcript")
async def score_transcript_endpoint(payload: ScoreTranscriptRequest) -> ScoreTranscriptResponse:
    return ScoreTranscriptResponse(**score_transcript(payload.transcript))


@app.post("/score/fusion")
@app.post("/api/v1/score/fusion")
async def score_fusion_endpoint(payload: ScoreFusionRequest) -> FusionEvent:
    result = fuse(payload.audio_score, payload.sms_score, payload.transcript_score)
    event = FusionEvent(
        type="fusion",
        audio_score=result.audio_score,
        sms_score=result.sms_score,
        transcript_score=result.transcript_score,
        threat_score=result.threat_score,
        threat_level=result.threat_level.value,
        color=result.color,
        formula_str=result.formula_str,
        explanation=result.explanation,
        scenario="Manual REST scoring",
        timestamp=time.time(),
    )
    append_threat_event(event.model_dump(), APP_CONFIG.logging)
    return event


@app.post("/sms/mock")
@app.post("/api/v1/sms/mock")
async def mock_sms(payload: MockSmsRequest) -> MockSmsResponse:
    text = payload.text.strip()
    if not text:
        return MockSmsResponse(accepted=False, error="text is required")
    inject_mock_sms(text)
    return MockSmsResponse(accepted=True)


@app.post("/demo/scenario")
@app.post("/api/v1/demo/scenario")
async def demo_scenario(payload: DemoScenarioRequest) -> DemoScenarioResponse:
    global _demo_override
    scenario = payload.scenario
    if scenario not in DEMO_SCENARIOS:
        return DemoScenarioResponse(
            accepted=False, scenario=scenario, override=None, error=f"unknown scenario: {scenario}"
        )
    _demo_override = DEMO_SCENARIOS[scenario]
    return DemoScenarioResponse(accepted=True, scenario=scenario, override=_demo_override)


@app.websocket("/ws/threat")
async def threat_websocket(websocket: WebSocket) -> None:
    await websocket.accept()
    audio_score = -1.0
    sms_score = -1.0
    transcript_score = -1.0
    last_transcript_text = ""

    try:
        audio_source = audio_windows(AUDIO_SOURCE)
        while True:
            start = time.perf_counter()
            window, spoof_hint, tick = await audio_source.__anext__()
            audio_score, _ = aasist.score(window)
            # FIXED: Added underscore to avoid 'unused variable' linting error
            _features = extract_features(window)
            latency_ms = (time.perf_counter() - start) * 1_000
            if _demo_override:
                audio_score = _demo_override["audio_score"]

            audio_event = AudioEvent(
                type="audio",
                audio_score=audio_score,
                latency_ms=round(latency_ms, 1),
                spoof_hint=spoof_hint,
                timestamp=time.time(),
            )
            await websocket.send_json(audio_event.model_dump())

            sms_text = await get_next_sms()
            if sms_text:
                sms_result = score_sms(sms_text)
                sms_score = sms_result["sms_score"]
                sms_event = SmsEvent(type="sms", **sms_result, timestamp=time.time())
                await websocket.send_json(sms_event.model_dump())
            if _demo_override:
                sms_score = _demo_override["sms_score"]

            transcript_text = ""
            if _demo_override:
                scenario = next((key for key, value in DEMO_SCENARIOS.items() if value == _demo_override), "auto")
                transcript_text = DEMO_TRANSCRIPTS.get(scenario, "")
            elif tick > 0 and tick % 20 == 0:
                transcript = transcribe_audio_array(window)
                transcript_text = str(transcript.get("text", "")).strip()

            if transcript_text and transcript_text != last_transcript_text:
                last_transcript_text = transcript_text
                transcript_result = score_transcript(transcript_text)
                transcript_score = float(transcript_result["urgency_score"])
                transcript_event = TranscriptEvent(
                    type="transcript",
                    transcript=transcript_text,
                    urgency_score=transcript_score,
                    backend=str(transcript_result["backend"]),
                    matched_phrases=list(transcript_result["matched_phrases"]),
                    timestamp=time.time(),
                )
                await websocket.send_json(transcript_event.model_dump())

            fusion = fuse(audio_score, sms_score, transcript_score)
            fusion_event = FusionEvent(
                type="fusion",
                audio_score=fusion.audio_score,
                sms_score=fusion.sms_score,
                transcript_score=fusion.transcript_score,
                threat_score=fusion.threat_score,
                threat_level=fusion.threat_level.value,
                color=fusion.color,
                formula_str=fusion.formula_str,
                explanation=fusion.explanation,
                scenario=_demo_override["label"] if _demo_override else "Automatic live demo stream",
                timestamp=time.time(),
            )
            append_threat_event(fusion_event.model_dump(), APP_CONFIG.logging)
            await websocket.send_json(fusion_event.model_dump())
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        return