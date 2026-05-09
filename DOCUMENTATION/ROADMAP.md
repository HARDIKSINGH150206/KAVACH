# KAVACH — Project Roadmap

> From hackathon prototype to production-grade national cybersecurity infrastructure.

---

## Roadmap Overview

```
PHASE 0          PHASE 1          PHASE 2          PHASE 3          PHASE 4          PHASE 5
Pre-Hackathon ──► Hackathon  ──►  Post-Hack   ──►  MVP / Beta  ──►  Scale Up    ──►  National
  (1 week)        (12 hours)      (1 month)        (3 months)       (6 months)       (12 months)
  Setup &         Working         Hardened          Android          Bank / MNO        CERT-In
  Prep            Demo            Python CLI        App              Integration       Integration
```

---

## Phase 0 — Pre-Hackathon Preparation
**Timeline: 1 week before hackathon**

### Goal
Have everything downloaded, installed, and tested so zero time is wasted at the venue on setup or downloads.

### Tasks

#### Environment
- [ ] Set up Python 3.10+ virtual environment
- [ ] Install all pip dependencies from `requirements.txt`
- [ ] Install Node.js 18+ and frontend deps
- [ ] Verify CUDA with `torch.cuda.is_available()` — must return `True`
- [ ] Confirm GPU drivers (CUDA 11.8+) and NVIDIA toolkit installed

#### Model Downloads (~1.5 GB total — do this on home WiFi)
- [ ] Download AASIST pre-trained checkpoint (~50 MB) from clovaai/aasist GitHub releases
- [ ] Download MuRIL base model (~900 MB) from HuggingFace via `download_models.py`
- [ ] Download Whisper base model (~140 MB) via `whisper.load_model("base")`
- [ ] Run all three models once to verify no import errors

#### Data
- [ ] Assemble Indian phishing SMS corpus (min 5,000 phishing + 2,500 legit)
- [ ] Augment e-challan / KYC / FASTag / OTP templates with regex variation
- [ ] Run `train_sms_classifier.py` and save `sms_classifier.pkl`
- [ ] Record or generate a deepfake voice sample using Coqui TTS or ElevenLabs free tier

#### Verification
- [ ] Run `pytest tests/ -v` — all tests green
- [ ] Run full pipeline once end-to-end with mock data
- [ ] Confirm FastAPI starts and WebSocket connects to React frontend

### Deliverable
A fully functional development environment ready to build at venue with zero internet dependency.

---

## Phase 1 — Hackathon (12 Hours)
**Timeline: Hackathon day**

### Goal
A working, demoable prototype with both pipelines live and a polished dashboard.

### Hour-by-Hour Plan

| Hours | Task | Owner Suggestion |
|---|---|---|
| 0 – 1 | Repo setup, team role assignment, FastAPI skeleton with `/health` endpoint | Lead |
| 1 – 3 | SMS pipeline: classifier, URL scorer, rule engine, mock SMS feed | Backend Dev 1 |
| 3 – 5 | Audio pipeline: sounddevice capture, librosa features, AASIST inference | Backend Dev 2 |
| 5 – 6 | Whisper STT + MuRIL urgency scorer wired into audio pipeline | Backend Dev 2 |
| 6 – 7 | Fusion engine: NumPy formula, threshold mapping, WebSocket streaming | Lead |
| 7 – 9 | React dashboard: ThreatBanner, Spectrogram, SMSFeed, live WebSocket hook | Frontend Dev |
| 9 – 10 | ConfidenceTimeline + FusionFormula display + GPULatencyCard | Frontend Dev |
| 10 – 11 | End-to-end integration test: deepfake audio → spectrogram lights red | All |
| 11 – 12 | Demo rehearsal: hit 2-minute flow 3 times, fix polish issues | All |

### Build Priority Order (if time runs short)
1. SMS classifier + fusion + basic alert (core functionality — judges must see this)
2. AASIST audio pipeline (the wow moment)
3. React spectrogram (visual proof)
4. Timeline + formula display (explainability)
5. Polish (colours, latency card, audio alarm)

### Deliverable
Live demo: e-challan SMS scores HIGH → deepfake voice triggers CRITICAL → spectrogram lights red → formula visible on screen.

---

## Phase 2 — Post-Hackathon Hardening
**Timeline: 1 month after hackathon**

### Goal
Transform the hackathon prototype into a stable, tested Python CLI tool that runs reliably on any machine.

### 2.1 Code Quality
- [ ] Refactor all modules with proper error handling and logging
- [ ] Replace `print()` statements with `logging` module (DEBUG / INFO / WARNING / ERROR)
- [ ] Add type hints across all Python files
- [ ] Write comprehensive docstrings for every public function
- [ ] Set up `black` + `flake8` + `isort` for code formatting
- [ ] Add `pre-commit` hooks

### 2.2 Test Coverage
- [ ] Expand test suite to cover edge cases: silence, background noise, multilingual SMS
- [ ] Add integration tests for full pipeline (audio → score → WebSocket → dashboard)
- [ ] Add adversarial test cases: attempted prompt injection in SMS text
- [ ] Achieve > 85% test coverage via `pytest-cov`

### 2.3 Model Improvements
- [ ] Fine-tune AASIST on ElevenLabs + RVC-generated Hindi voices (India-specific deepfakes)
- [ ] Expand SMS corpus to 20,000+ samples across more scam categories
- [ ] Add FP/FN analysis on held-out test set and reduce false positives
- [ ] Experiment with MuRIL large model for improved accuracy
- [ ] Add confidence calibration (Platt scaling) to SMS classifier

### 2.4 CLI Tool
- [ ] Package as a proper Python CLI with `argparse` or `click`
- [ ] Add `kavach start` / `kavach stop` / `kavach status` commands
- [ ] Add config file (`kavach.yml`) for tunable weights and thresholds
- [ ] Add log file output with timestamped threat events
- [ ] Package with `pyproject.toml` for `pip install kavach`

### 2.5 Documentation
- [ ] Write proper `README.md` with installation, usage, and architecture
- [ ] Add `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`
- [ ] Publish to GitHub with MIT or Apache-2.0 license
- [ ] Record a 5-minute demo video for GitHub README

### Deliverable
A stable Python CLI (`pip install kavach`) with > 85% test coverage and published GitHub repo.

---

## Phase 3 — MVP / Beta Release
**Timeline: Months 2–4 after hackathon**

### Goal
An Android app that protects real users with no technical setup required.

### 3.1 Android App
- [ ] Build Android app in React Native or Kotlin
- [ ] Implement Android Accessibility Service to intercept incoming calls
- [ ] Implement SMS ContentObserver to monitor incoming SMS natively (no ADB)
- [ ] Add local notification system for SUSPICIOUS / HIGH / CRITICAL alerts
- [ ] Build minimal in-app UI: threat history, per-call scores, SMS feed

### 3.2 On-Device ML
- [ ] Convert AASIST PyTorch model to ONNX format
- [ ] Convert ONNX to TensorFlow Lite for Android
- [ ] Quantise TFLite model to INT8 for mobile inference (reduces size 4x)
- [ ] Benchmark on Snapdragon 8 Gen 1 / Dimensity 9000 — target < 150ms per window
- [ ] Convert sklearn SMS classifier to ONNX or CoreML for mobile

### 3.3 MuRIL Mobile
- [ ] Quantise MuRIL to 4-bit using `bitsandbytes` or GGUF
- [ ] Test inference speed on mid-range devices (Snapdragon 778G target)
- [ ] Build fallback to TF-IDF-only classifier for low-end devices (< 4GB RAM)

### 3.4 Beta Testing
- [ ] Recruit 50–100 beta testers in Tier 1 / Tier 2 / Tier 3 Indian cities
- [ ] Set up crash reporting with Sentry
- [ ] Set up anonymous usage analytics (no personal data — scores only)
- [ ] Run 30-day field trial, collect FP/FN feedback from users
- [ ] Publish beta on Google Play (closed testing track)

### 3.5 Privacy & Compliance
- [ ] Legal review: verify compliance with IT Act 2000, DPDP Act 2023
- [ ] Write privacy policy: zero data leaves device, no cloud, no PII stored
- [ ] VAPT (Vulnerability Assessment & Penetration Testing) of the app
- [ ] Implement certificate pinning for any future backend communication

### Deliverable
Android app in closed beta with 100 real users, zero cloud dependency confirmed, < 150ms latency on mid-range devices.

---

## Phase 4 — Scale Up
**Timeline: Months 5–9 after hackathon**

### Goal
Integrate KAVACH's detection engine into bank call centres and telecom SMS gateways.

### 4.1 Bank Call Centre Integration
- [ ] Build FastAPI microservice variant for server-side deployment
- [ ] Expose REST API: `POST /score/audio` and `POST /score/sms`
- [ ] Add async batch scoring for call recordings (post-call fraud analysis)
- [ ] Build admin dashboard for fraud operations teams
- [ ] Implement SLA: < 200ms p99 latency for audio scoring
- [ ] Sign pilot agreements with 2–3 Indian private banks (HDFC, ICICI, Axis)

### 4.2 Telecom / MNO SMS Gateway Integration
- [ ] Build SMS gateway plugin (SMPP protocol integration)
- [ ] Deploy as a filtering layer between MNO and subscriber delivery
- [ ] Process SMS at ingestion: block CRITICAL, flag HIGH for human review
- [ ] Benchmark throughput: target 10,000 SMS/second on 8-core server
- [ ] Pilot with one MNO (Jio / Airtel / Vi preferred)

### 4.3 Model Retraining Pipeline
- [ ] Set up automated retraining pipeline triggered weekly
- [ ] Build data flywheel: anonymised threat signal aggregation across devices
- [ ] Implement federated learning (PySyft or Flower framework)
- [ ] New scam patterns detected in field auto-added to training corpus
- [ ] A/B test new model versions on 5% of traffic before full rollout

### 4.4 Scalability & Infrastructure
- [ ] Containerise backend with Docker + Docker Compose
- [ ] Write Kubernetes deployment manifests for bank/MNO on-premise
- [ ] Add horizontal autoscaling based on call volume
- [ ] Set up Prometheus + Grafana monitoring
- [ ] Add Redis caching for repeated SMS pattern scoring

### 4.5 iOS App
- [ ] Port Android app to iOS using React Native shared codebase
- [ ] Convert TFLite models to CoreML for Apple Silicon (A15+)
- [ ] Submit to Apple App Store (review process ~2 weeks)

### Deliverable
Live pilot with at least 1 bank and 1 MNO. 10,000+ active Android users. iOS app in review.

---

## Phase 5 — National Infrastructure
**Timeline: Months 10–15 after hackathon**

### Goal
Integrate KAVACH into India's national cybercrime defence infrastructure and reach 1 million users.

### 5.1 CERT-In Integration
- [ ] Formal engagement with CERT-In (Indian Computer Emergency Response Team)
- [ ] Build automated threat intelligence reporting API
- [ ] New scam phone numbers and URL patterns reported to national blocklist
- [ ] Bi-directional sync: CERT-In known-bad patterns feed into KAVACH model
- [ ] Participate in CERT-In coordinated vulnerability disclosure program

### 5.2 MHA / Cybercrime Portal
- [ ] API integration with National Cybercrime Reporting Portal (cybercrime.gov.in)
- [ ] Auto-generate structured incident reports for CRITICAL alerts (with user consent)
- [ ] Anonymised threat map: city-level scam pattern heatmap for law enforcement

### 5.3 TRAI Collaboration
- [ ] Share smishing pattern signatures with TRAI DND registry
- [ ] Help TRAI build a proactive (ML-based) blocklist vs current reactive blocklist
- [ ] Participate in TRAI's TCCCP (Telecom Commercial Communications Customer Preference) consultation

### 5.4 Reach & Distribution
- [ ] Publish to Google Play open track — target 1 million downloads
- [ ] Partner with state government cybercrime awareness programs
- [ ] Integration with DigiSaathi (RBI's helpline for digital payment fraud)
- [ ] Publish research paper on dual-vector fusion methodology (conference target: ACM CCS or IEEE S&P)
- [ ] Open-source the core detection engine (models stay proprietary)

### 5.5 Sustainability
- [ ] B2B SaaS model: charge banks and MNOs per API call (₹0.001/score)
- [ ] Government contract: CERT-In / MHA national deployment license
- [ ] Grant applications: DST, MeitY Startup Hub, Startup India seed fund
- [ ] Series A fundraising target: ₹15–20 Cr for team expansion and infra

### Deliverable
CERT-In integration live. 1 million app users. Research paper submitted. Sustainable revenue from B2B API.

---

## Milestone Summary

| Milestone | Target Date | Success Metric |
|---|---|---|
| Phase 0 complete | 1 week before hackathon | All models downloaded, tests green, env verified |
| Hackathon demo | Hackathon day | Live demo: deepfake caught, spectrogram lights red |
| GitHub published | Week 1 post-hack | Repo live with README, tests, install instructions |
| CLI tool `pip install` | Month 1 | Works on clean Ubuntu 22.04 install |
| Android beta | Month 3 | 100 beta users, < 150ms latency on mid-range device |
| Bank pilot live | Month 6 | 1 bank scoring live calls via KAVACH API |
| MNO SMS filter live | Month 7 | 1 MNO filtering SMS at gateway level |
| CERT-In integration | Month 12 | Threat patterns flowing to national blocklist |
| 1 million users | Month 14 | Google Play install count |
| Research paper | Month 15 | Submitted to peer-reviewed conference |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| AASIST model unavailable at venue (WiFi) | High | Critical | Download checkpoint before hackathon — Phase 0 |
| GPU not available at hackathon | Medium | High | CPU fallback mode in `aasist_infer.py` — 300ms latency acceptable for demo |
| False positive on legitimate calls | Medium | High | Tune SUSPICIOUS threshold conservatively; add user feedback loop |
| DPDP Act compliance gap | Low | High | Privacy-by-architecture (offline) is the strongest compliance argument |
| Android Accessibility Service rejected by Play Store | Medium | Medium | Submit as Device Admin app; have APK sideload as backup |
| MuRIL inference too slow on low-end Android | High | Medium | TF-IDF-only fallback classifier for < 4GB RAM devices |
| Scammer adapts to KAVACH (adversarial SMS) | Low | Medium | Federated retraining picks up new patterns within 1 week |

---

## Tech Stack Evolution

| Phase | Audio Model | SMS Model | Platform | Latency |
|---|---|---|---|---|
| Phase 1 (Hackathon) | AASIST (PyTorch, GPU) | MuRIL + sklearn | Python desktop | < 80ms GPU |
| Phase 2 (CLI) | AASIST (PyTorch, CPU) | MuRIL + sklearn | Python, any OS | < 300ms CPU |
| Phase 3 (Android) | AASIST TFLite INT8 | MuRIL 4-bit GGUF | Android (Kotlin) | < 150ms mobile |
| Phase 4 (Bank API) | AASIST (multi-GPU) | MuRIL large | FastAPI + K8s | < 50ms p50 |
| Phase 5 (National) | Ensemble + fine-tuned | Custom Indian LLM | Distributed | < 30ms p50 |

---

*KAVACH — Built for Cybersecurity Hackathon 2026*
*Roadmap version 1.0 — May 2026*y