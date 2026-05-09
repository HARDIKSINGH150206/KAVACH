from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> tuple[int, str]:
    process = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return process.returncode, process.stdout + process.stderr


def main() -> None:
    checks = []
    pilot_env = os.environ.copy()
    pilot_env["KAVACH_AUDIO_SOURCE"] = "demo"
    pilot_env["KAVACH_AUTH_MODE"] = "api_key"
    pilot_env["KAVACH_ALLOW_DEMO_CONTROLS"] = "false"
    pilot_env.setdefault("KAVACH_API_KEY", "pilot-key")

    readiness_proc = subprocess.run(
        [str(ROOT / "kavach-env/bin/python"), "scripts/check_readiness.py", "--strict"],
        cwd=ROOT,
        env=pilot_env,
        capture_output=True,
        text=True,
    )
    rc = readiness_proc.returncode
    out = readiness_proc.stdout + readiness_proc.stderr
    readiness = json.loads(out) if rc == 0 else {"state": "attention_required"}
    checks.append(("readiness_ready", readiness.get("state") == "ready"))

    eval_proc = subprocess.run(
        [
            str(ROOT / "kavach-env/bin/python"),
            "scripts/evaluate_sms_classifier.py",
            "--strict",
            "--min-adversarial-accuracy",
            "0.75",
        ],
        cwd=ROOT,
        env=pilot_env,
        capture_output=True,
        text=True,
    )
    rc = eval_proc.returncode
    checks.append(("adversarial_threshold", rc == 0))

    rc_backend, _ = run([str(ROOT / "kavach-env/bin/python"), "-m", "pytest", "tests/", "-q"])
    checks.append(("backend_tests", rc_backend == 0))

    rc_front_main_lint, _ = run(["npm", "--prefix", "MAIN_FRONTEND", "run", "lint"])
    checks.append(("main_frontend_lint", rc_front_main_lint == 0))

    rc_front_main_build, _ = run(["npm", "--prefix", "MAIN_FRONTEND", "run", "build"])
    checks.append(("main_frontend_build", rc_front_main_build == 0))

    rc_front_legacy_build, _ = run(["npm", "--prefix", "frontend", "run", "build"])
    checks.append(("legacy_frontend_build", rc_front_legacy_build == 0))

    smoke_env = os.environ.copy()
    smoke_env.setdefault("BACKEND_URL", "http://127.0.0.1:8000")
    smoke_env.setdefault("FRONTEND_URL", "http://127.0.0.1:5175")
    smoke_proc = subprocess.run(
        ["./scripts/smoke_check.sh"],
        cwd=ROOT,
        env=smoke_env,
        capture_output=True,
        text=True,
    )
    checks.append(("smoke_check", smoke_proc.returncode == 0))

    passed = all(ok for _, ok in checks)
    payload = {"passed": passed, "checks": [{"name": name, "ok": ok} for name, ok in checks]}
    print(json.dumps(payload, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
