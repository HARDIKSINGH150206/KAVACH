# KAVACH Implementation Blueprint (Current)

This blueprint reflects the current repository implementation as of May 2026.

## 1. What Is Implemented

KAVACH is a local, demo-first dual-signal fraud detection system with:

- audio risk scoring (`AASIST` when available, deterministic fallback otherwise)
- SMS phishing scoring (rules + URL risk + trained TF-IDF/LR model fallback chain)
- optional transcript urgency scoring (currently rule-based fallback)
- fusion scoring with configurable thresholds/weights
- FastAPI REST + WebSocket streaming dashboard
- React/Vite operator dashboard

## 2. Runtime Interfaces

Primary API (versioned):

- `GET /api/v1/health`
- `GET /api/v1/config`
- `POST /api/v1/score/sms`
- `POST /api/v1/score/audio`
- `POST /api/v1/score/transcript`
- `POST /api/v1/score/fusion`
- `POST /api/v1/sms/mock`
- `POST /api/v1/demo/scenario`

Compatibility aliases without `/api/v1` are still available.

WebSocket stream:

- `GET ws://<host>:<port>/ws/threat`

## 3. Core Backend Modules

- API app: `backend/main.py`
- Runtime config: `backend/config.py`
- Readiness report: `backend/readiness.py`
- Contracts/schemas: `backend/contracts.py`
- Audio scoring: `backend/audio/aasist_infer.py`, `backend/audio/scoring.py`, `backend/audio/capture.py`
- Transcript urgency: `backend/audio/urgency_nlp.py`
- SMS scoring: `backend/sms/classifier.py`, `backend/sms/rule_engine.py`, `backend/sms/url_scorer.py`
- Fusion engine: `backend/fusion/engine.py`
- CLI: `backend/cli.py`

## 4. Frontend Modules

- App shell: `frontend/src/App.jsx`
- Backend URL/env config: `frontend/src/config.js`
- WebSocket hook: `frontend/src/hooks/useWebSocket.js`
- Backend status hook: `frontend/src/hooks/useBackendStatus.js`
- Panels/components: `frontend/src/components/*`

Environment variables used by frontend:

- `VITE_API_BASE` (default `http://localhost:8000`)
- `VITE_WS_THREAT_URL` (default derived from API base)

## 5. Security and Traffic Controls

Configured via `kavach.yml` or env:

- API key (optional): `security.api_key` / `KAVACH_API_KEY`
- Basic in-memory rate limiting: `security.rate_limit_per_minute` / `KAVACH_RATE_LIMIT_PER_MINUTE`

When API key is set, clients must send `x-api-key`.

## 6. Model and Data Status

- Required runtime artifact: `backend/models/sms_classifier.pkl`
- Optional artifacts:
  - `backend/models/aasist_checkpoint/*`
  - `backend/models/whisper/*`
  - `backend/models/muril/*`

Current dataset files:

- `backend/data/phishing_sms.csv`
- `backend/data/legit_sms.csv`
- `backend/data/sms_adversarial_cases.json`

Dataset readiness still reports seed-scale and incomplete for production targets.

## 7. Validation and CI

Local validation commands:

- backend tests: `./kavach-env/bin/python -m pytest tests/ -q`
- frontend unit tests: `npm --prefix frontend run test -- --run`
- frontend build: `npm --prefix frontend run build`
- readiness report: `./kavach-env/bin/python scripts/check_readiness.py`

Smoke e2e scaffold:

- Playwright config: `frontend/playwright.config.js`
- Spec: `frontend/tests/e2e/dashboard.spec.js`
- Command: `npm --prefix frontend run e2e`

## 8. Known Gaps (Intentional / Pending)

- Large production-scale labeled SMS corpus is not yet integrated.
- MuRIL runtime inference is not wired; transcript urgency is rule fallback.
- Rate limiter is local-memory only (non-distributed).
- Full production authn/authz stack is not implemented.
