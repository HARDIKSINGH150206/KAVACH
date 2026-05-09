# KAVACH

Real-time demo scaffold for a dual-vector fraud shield: audio deepfake scoring + SMS phishing scoring + fusion dashboard.

## Project Status ✅

KAVACH is a demo-ready prototype with strong local tooling, tests, and container support. It is not yet production-ready.

### ✅ Completed Features
- **Backend**: FastAPI with WebSocket streaming, audio processing, SMS classification, fusion engine
- **Frontend**: React dashboard with real-time spectrogram, threat visualization, demo controls
- **Testing**: 64 backend tests + 5 frontend tests passing, integration tests included
- **Containerization**: Docker support with multi-stage builds
- **CLI**: Start/stop commands with PID management
- **Configuration**: YAML-based config with environment overrides
- **Deployment**: Docker Compose, systemd service, Nginx reverse proxy docs

### 🔧 Technical Stack
- **Backend**: Python 3.12, FastAPI, WebSocket, PyTorch, scikit-learn, librosa
- **Frontend**: React 18, Vite, WebSocket hooks, Canvas spectrogram
- **Models**: AASIST (deepfake detection), TF-IDF + LR (SMS classification), MuRIL (urgency NLP)
- **Infrastructure**: Docker, systemd, Nginx, pre-commit hooks

### 📊 Test Coverage
- Backend: 64 tests passing (pytest)
- Frontend: 5 tests passing (Vitest + jsdom)
- Integration: End-to-end API and CLI testing
- Docker: Container builds successfully

## Quick Start

### With Docker (Recommended)
```bash
docker build -t kavach .
docker run -p 8000:8000 kavach
```

### Manual Setup
```bash
# Setup environment
python3 -m venv kavach-env
source kavach-env/bin/activate
pip install -r requirements.txt

# Download models (optional)
python3 scripts/download_models.py

# Start server
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Access dashboard at http://localhost:8000

## Current Execution Mode

This implementation is runnable without large model downloads. It uses:

- synthetic demo audio windows with heuristic artifact scoring through the future `AASISTScorer` interface
- `librosa` feature extraction for MFCC, delta MFCC, log-mel, f0, and raw waveform data
- SMS scam rules, URL risk analysis, and a trained TF-IDF + logistic regression classifier
- typed FastAPI REST/WebSocket payloads
- React/Vite dashboard with demo controls, spectrogram, SMS feed, confidence timeline, and threat banner

Production audio/NLP models are not wired yet. AASIST, Whisper, MuRIL, Android ingestion, and deployment packaging are still roadmap items.

## Run Backend

```bash
python -m venv kavach-env
source kavach-env/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend defaults to synthetic demo audio. To request live microphone input:

```bash
KAVACH_AUDIO_SOURCE=mic uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

If microphone capture is unavailable, the stream falls back to demo audio.

Runtime defaults live in `kavach.yml`. `KAVACH_AUDIO_SOURCE` still overrides the configured audio source.
Copy `.env.example` to `.env` if you want a local place to track runtime overrides.

Health check:

```bash
curl http://localhost:8000/api/v1/health
```

Setup/readiness check:

```bash
./scripts/setup_dev.sh
./kavach-env/bin/python scripts/check_readiness.py
./scripts/verify.sh
```

`/api/v1/health` and `kavach status` include a readiness report covering Python dependencies, model assets, SMS dataset state,
frontend dependency state, and active runtime config.

Config and direct scoring:

```bash
curl http://localhost:8000/api/v1/config
curl -X POST http://localhost:8000/api/v1/score/sms \
  -H "Content-Type: application/json" \
  -d '{"text":"Vehicle MH12AB1234 ka e-challan Rs.500 pending hai. Pay immediately https://bit.ly/challan99"}'
curl -X POST http://localhost:8000/api/v1/score/audio \
  -H "Content-Type: application/json" \
  -d '{"sample_rate":16000,"samples":[0.0,0.1,0.0,-0.1]}'
curl -X POST http://localhost:8000/api/v1/score/transcript \
  -H "Content-Type: application/json" \
  -d '{"transcript":"CBI case file opened. Share OTP immediately or legal action will start."}'
curl -X POST http://localhost:8000/api/v1/score/fusion \
  -H "Content-Type: application/json" \
  -d '{"audio_score":0.9,"sms_score":0.85,"transcript_score":0.7}'
```

Fusion now accepts audio, SMS, and optional transcript urgency signals. Missing signals can be passed as `-1` or omitted where defaults are defined.

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Docker

Build and run the backend with Docker:

```bash
docker build -t kavach-backend .
docker run --rm -p 8000:8000 kavach-backend
```

Or run the backend and frontend together with Docker Compose:

```bash
docker compose up --build
```

This exposes the backend on `http://localhost:8000` and the frontend on `http://localhost:5173`.

## Makefile

Common repository commands are available through the top-level Makefile:

```bash
make install-dev
make test
make lint
make docker-build
make compose-up
make start
make stop
make status
make readiness
make pilot-gate
```

### Runtime Profiles

Start backend with profile defaults:

```bash
./scripts/run_profile.sh demo
./scripts/run_profile.sh pilot
./scripts/run_profile.sh prod
```

`pilot` and `prod` profiles enable auth defaults suitable for controlled environments.

## CLI

The package includes a local CLI wrapper. From the repository root:

```bash
./kavach-env/bin/python -m backend.cli start
./kavach-env/bin/python -m backend.cli status
./kavach-env/bin/python -m backend.cli stop
```

The `start` command launches the backend with `uvicorn` in the background and writes a PID to `.kavach.pid`.

## Tests

### Backend

```bash
pytest tests/ -v
```

### Frontend

```bash
cd frontend && npm run test -- --run
```

### All tests

```bash
make test
make frontend-test
```

When using the checked-in local virtual environment:

```bash
./kavach-env/bin/python -m pytest tests/ -v
```

With coverage:

```bash
./kavach-env/bin/python -m pytest tests/ -v --cov=backend --cov=scripts --cov-report=term-missing
```

## Train SMS Classifier

Seed datasets live in `backend/data/phishing_sms.csv` and `backend/data/legit_sms.csv`. Train or refresh the local model with:

```bash
./kavach-env/bin/python scripts/train_sms_classifier.py
```

The trained artifact is saved to `backend/models/sms_classifier.pkl`. Runtime SMS scoring falls back to lexical scoring if that file is missing.

Evaluate the checked-in model against the labeled CSVs with:

```bash
./kavach-env/bin/python scripts/evaluate_sms_classifier.py
./kavach-env/bin/python scripts/evaluate_sms_classifier.py --output reports/sms_eval.json
./kavach-env/bin/python scripts/audit_sms_dataset.py --output reports/sms_dataset_audit.json
```

The current checked-in dataset is intentionally a small seed set. The evaluator reports dataset readiness and will continue marking it incomplete until it reaches the planned credible-prototype target of at least 5,000 phishing and 2,500 legitimate SMS examples.

## Model Assets

Inspect and prepare model asset directories with:

```bash
./kavach-env/bin/python scripts/download_models.py
```

This writes `backend/models/manifest.json` and checks:

- `backend/models/sms_classifier.pkl`
- `backend/models/aasist_checkpoint/`
- `backend/models/whisper/`
- `backend/models/muril/`

Whisper and MuRIL downloads are optional hooks:

```bash
./kavach-env/bin/python scripts/download_models.py --download-whisper
./kavach-env/bin/python scripts/download_models.py --download-muril
```

AASIST checkpoint selection is still manual, and runtime audio scoring still uses the heuristic fallback until the AASIST wrapper is implemented.

## AASIST Status

Place selected AASIST checkpoint files under:

```bash
backend/models/aasist_checkpoint/
```

Supported checkpoint extensions are `.pt`, `.pth`, `.ckpt`, and `.bin`. The backend discovers the first matching file and reports checkpoint state through `/api/v1/health`.

To activate real AASIST inference:

```bash
./kavach-env/bin/python -m pip install -e ".[aasist]"
./kavach-env/bin/python scripts/download_models.py --download-aasist
```

Restart the backend after installing PyTorch and downloading the checkpoint. `/api/v1/health` should then report:

```json
{"models":{"audio":{"backend":"aasist","checkpoint_state":"validated"}}}
```

If PyTorch or a valid checkpoint is unavailable, runtime audio scoring falls back to the deterministic heuristic scorer.

The `/score/audio` endpoint accepts mono waveform samples as JSON, normalizes/resamples them to 16 kHz, and pads/trims internally to AASIST's expected 64,600-sample input shape.

## Whisper and MuRIL Status

The backend reports Whisper and MuRIL readiness through `/api/v1/health`.

- Whisper STT is wired for live audio windows and remains optional. Install and prepare it with:

```bash
./kavach-env/bin/python -m pip install -e ".[stt]"
./kavach-env/bin/python scripts/download_models.py --download-whisper
```

- MuRIL urgency NLP is currently a status hook; runtime urgency scoring uses the deterministic rule fallback in `backend/audio/urgency_nlp.py`.
- `/score/transcript` is available now for scoring already-transcribed scam scripts and returns matched phrase categories plus an urgency score.
- The WebSocket stream can emit `transcript` events, and the dashboard displays the latest transcript urgency panel.

## CLI

Run local scoring commands without starting the API:

```bash
./kavach-env/bin/python -m backend.cli status
./kavach-env/bin/python -m backend.cli score-sms "KYC blocked verify urgently"
./kavach-env/bin/python -m backend.cli score-transcript "CBI case file share OTP immediately"
./kavach-env/bin/python -m backend.cli score-fusion --audio-score 0.9 --sms-score 0.85
```

After installing the package, the same commands are available through `kavach`.

## Logging

Runtime logging defaults are configured in `kavach.yml`. Fusion events at SUSPICIOUS, HIGH, or CRITICAL are written as JSON Lines to:

```bash
logs/threat_events.jsonl
```

The log directory is ignored by git. Override the directory with `KAVACH_LOG_DIR` and the log level with `KAVACH_LOG_LEVEL`.
# KAVACH_v1
