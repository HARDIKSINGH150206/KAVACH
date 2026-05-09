from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> tuple[int, str]:
    process = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return process.returncode, process.stdout + process.stderr


def main() -> None:
    checks = []

    rc, out = run([str(ROOT / "kavach-env/bin/python"), "scripts/check_readiness.py"])
    readiness = json.loads(out) if rc == 0 else {"state": "attention_required"}
    checks.append(("readiness_ready", readiness.get("state") == "ready"))

    rc, out = run(
        [
            str(ROOT / "kavach-env/bin/python"),
            "scripts/evaluate_sms_classifier.py",
            "--strict",
            "--min-adversarial-accuracy",
            "0.75",
        ]
    )
    checks.append(("adversarial_threshold", rc == 0))

    rc_backend, _ = run([str(ROOT / "kavach-env/bin/python"), "-m", "pytest", "tests/", "-q"])
    checks.append(("backend_tests", rc_backend == 0))

    rc_front, _ = run(["npm", "--prefix", "frontend", "run", "test", "--", "--run"])
    checks.append(("frontend_unit_tests", rc_front == 0))

    rc_e2e, _ = run(["npm", "--prefix", "frontend", "run", "e2e", "--", "--list"])
    checks.append(("e2e_scaffold_available", rc_e2e == 0))

    passed = all(ok for _, ok in checks)
    payload = {"passed": passed, "checks": [{"name": name, "ok": ok} for name, ok in checks]}
    print(json.dumps(payload, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
