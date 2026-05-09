import pandas as pd

from scripts.audit_sms_dataset import audit
from scripts.evaluate_sms_classifier import _evaluate_adversarial_cases
from scripts.train_sms_classifier import build_pipeline


def test_sms_dataset_audit_reports_categories() -> None:
    report = audit.__wrapped__() if hasattr(audit, "__wrapped__") else None
    if report is None:
        from scripts.train_sms_classifier import DEFAULT_LEGIT_CSV, DEFAULT_PHISHING_CSV

        report = audit(DEFAULT_PHISHING_CSV, DEFAULT_LEGIT_CSV)

    assert report["dataset"]["readiness_level"] == "seed_or_incomplete"
    assert "phishing_categories" in report
    assert report["action_items"]


def test_adversarial_evaluation_missing_file(tmp_path) -> None:
    pipeline = build_pipeline()
    data = pd.DataFrame(
        {
            "text": ["verify otp now", "salary credited today", "kyc blocked", "meeting rescheduled"],
            "label": [1, 0, 1, 0],
        }
    )
    pipeline.fit(data["text"], data["label"])
    report = _evaluate_adversarial_cases(pipeline, tmp_path / "missing.json")
    assert report["state"] == "missing"
    assert report["total"] == 0
