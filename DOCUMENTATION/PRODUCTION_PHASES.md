# KAVACH Production Phases Tracker

This tracker is the execution plan to move KAVACH from demo-ready to production-ready.
Status values:
- `done`
- `in_progress`
- `pending`

## Phase 1 - Stabilize Current Runtime
Status: `done` (May 9, 2026)

Completed:
- Main frontend/backend integration stabilized under `MAIN_FRONTEND`.
- Landing page launch flow fixed and made deterministic.
- Landing page scroll behavior fixed.
- React hook-order crash in `App` resolved by isolating dashboard hooks.
- WebSocket startup/teardown lifecycle hardened to avoid handshake-close warnings.
- Main frontend proxy wiring for `/api` and `/ws` validated.
- Main frontend build and lint pass.

Artifacts touched:
- `MAIN_FRONTEND/src/App.jsx`
- `MAIN_FRONTEND/src/hooks/useKavachBackend.js`
- `MAIN_FRONTEND/src/components/LandingPage.jsx`
- `MAIN_FRONTEND/src/components/dashboard/LiveSpectrogram.jsx`
- `MAIN_FRONTEND/src/index.css`
- `MAIN_FRONTEND/vite.config.js`
- `MAIN_FRONTEND/eslint.config.js`

Exit criteria check:
- Frontend opens reliably: `pass`
- Dashboard navigation works: `pass`
- Build/lint clean: `pass`
- Backend health endpoint reachable: `pass`

## Phase 2 - Backend Hardening
Status: `done` (May 9, 2026)

Completed:
- Added explicit demo control gate via `security.allow_demo_controls`.
- Enforced demo endpoint lockdown (`/sms/mock`, `/demo/scenario`) when disabled.
- Added websocket auth enforcement for both `api_key` and `bearer` modes.
- Added websocket rate-limit enforcement aligned with HTTP request limiter.
- Refactored auth and rate-limit logic into reusable backend helpers.
- Extended API tests for demo-control lockout and websocket auth rejection.

Exit criteria:
- API and websocket behavior are predictable under failures: `pass`
- Auth/rate-limit behavior is test-covered and documented: `pass`

Validation:
- `./kavach-env/bin/python -m pytest tests/test_api.py -q` -> `21 passed`
- `./kavach-env/bin/python -m pytest tests/ -q` -> `73 passed, 1 skipped`

## Phase 3 - Frontend Hardening
Status: `done` (May 9, 2026)

Completed:
- Replaced hash/storage-only dashboard switch with explicit path flow using `/` and `/dashboard`.
- Added backend-readiness-gated dashboard rendering to avoid unstable startup UX.
- Kept websocket offline indication tied to actual backend/socket state.
- Removed spectrogram mock transcript and static audio-score placeholders.
- Removed static SMS feed metadata placeholders and bound to live event metadata.

Exit criteria:
- No hidden fallback behavior in production path: `pass` (core dashboard panels now avoid mock fallback content)
- Frontend clearly reflects real backend state: `pass`

Validation:
- `npm run lint` in `MAIN_FRONTEND` -> `pass`
- `npm run build` in `MAIN_FRONTEND` -> `pass`

## Phase 4 - Model and Data Readiness
Status: `done` (May 9, 2026)

Completed:
- Switched training defaults to the augmented corpus (`5000 phishing / 2500 legit`) in `scripts/train_sms_classifier.py`.
- Updated readiness dataset selection to prefer the largest available corpus instead of tiny seed CSVs.
- Added `dataset_source` metadata to readiness output (`seed` vs `augmented`).
- Added `runtime_sms_model` metadata to readiness output so model state/version info is surfaced with readiness.
- Updated readiness tests for the new dataset-selection behavior.

Exit criteria:
- Dataset target scale integrated into readiness pipeline: `pass` (augmented dataset now selected)
- Alert/model metadata surfaced in readiness: `pass`
- Note: dataset quality gate is still not fully green due high duplicate count; readiness correctly reports this risk.

Validation:
- `./kavach-env/bin/python -m pytest tests/test_readiness.py -q` -> `4 passed`
- `./kavach-env/bin/python -m pytest tests/ -q` -> `73 passed, 1 skipped`

## Phase 5 - Deployment and Operations
Status: `done` (May 9, 2026)

Completed:
- Added deployment smoke-check script: `scripts/smoke_check.sh`.
- Added `make smoke-check` target in `Makefile`.
- Updated CI workflow to lint/build both frontend apps (`frontend` and `MAIN_FRONTEND`).
- Updated Docker Compose default frontend service to the integrated app (`MAIN_FRONTEND` on port `5175`).
- Updated deployment docs with smoke-check procedure and URL overrides.
- Aligned README operational references to current main frontend path and port.

Exit criteria:
- Deployment verification is scriptable and repeatable: `pass`
- CI now enforces frontend lint/build gates across active UI paths: `pass`
- Operational runbook includes post-deploy smoke validation: `pass`

Validation:
- `npm run lint && npm run build` in `MAIN_FRONTEND` -> `pass`
- `./kavach-env/bin/python -m pytest tests/test_api.py -q` -> `21 passed`
- `FRONTEND_URL=http://127.0.0.1:5176 ./scripts/smoke_check.sh` -> `smoke checks passed`

## Phase 6 - Security and Compliance
Status: `done` (May 9, 2026)

Completed:
- Hardened runtime profile defaults:
  - `pilot` and `prod` now force `KAVACH_ALLOW_DEMO_CONTROLS=false`.
  - `pilot` uses `api_key`; `prod` uses `bearer`.
- Expanded environment template security section:
  - Added explicit `KAVACH_ALLOW_DEMO_CONTROLS`.
  - Updated CORS example to main frontend port.
- Added deployment documentation guidance for secure auth/demo-control defaults.
- Added config tests for `allow_demo_controls` parsing and env override behavior.

Exit criteria:
- Security posture and controls are explicit in runtime profiles and docs: `pass`
- Security behavior is test-backed in CI: `pass`
- Note: vulnerability scanning and formal privacy policy artifacts remain future hardening items.

Validation:
- `./kavach-env/bin/python -m pytest tests/test_config_cli.py -q` -> `9 passed`
- `./kavach-env/bin/python -m pytest tests/test_api.py -q` -> `21 passed`
- `./kavach-env/bin/python -m pytest tests/ -q` -> `75 passed, 1 skipped`

## Phase 7 - Staging and Pilot Rollout
Status: `done` (May 9, 2026)

Completed:
- Added staging/pilot execution runbook: `DOCUMENTATION/STAGING_PILOT_RUNBOOK.md`.
- Hardened `scripts/pilot_gate.py` to run deterministic pilot-profile checks:
  - strict readiness under pilot-safe env (`audio_source=demo`, `auth_mode=api_key`, demo controls disabled)
  - adversarial SMS threshold
  - backend tests
  - main frontend lint/build
  - legacy frontend build
  - deployment smoke check
- Validated end-to-end gate pass via `make pilot-gate` / `scripts/pilot_gate.py`.

Exit criteria:
- Pilot quality gates met on readiness, build, tests, and smoke checks: `pass`
- Staging/pilot operational runbook documented: `pass`

Validation:
- `./kavach-env/bin/python scripts/pilot_gate.py` -> `passed: true` (all checks `ok`)
