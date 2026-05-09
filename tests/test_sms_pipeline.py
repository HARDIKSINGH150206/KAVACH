from pathlib import Path

import joblib
import pandas as pd

import backend.sms.classifier as classifier
from backend.sms.classifier import score_sms
from backend.sms.evaluation import classification_metrics, profile_dataset
from backend.sms.rule_engine import classify_scam_type
from backend.sms.url_scorer import score_url, shannon_entropy
from scripts.evaluate_sms_classifier import evaluate
from scripts.train_sms_classifier import train


def test_url_scorer_shortener() -> None:
    result = score_url("https://bit.ly/challan99")
    assert result["url_risk"] >= 0.4
    assert "url_shortener" in result["flags"]


def test_url_entropy() -> None:
    assert shannon_entropy("xk9pq2mn") > 2.5


def test_echallan_rule() -> None:
    result = classify_scam_type("Vehicle MH12AB1234 ka challan Rs.500 hai. Pay: https://bit.ly/xyz")
    assert result["is_scam_pattern"] is True
    assert result["scam_type"] == "e-Challan"


def test_newer_scam_categories_are_classified() -> None:
    result = classify_scam_type("Electricity bill overdue. Pay now or disconnection today.")

    assert result["scam_type"] == "Utility Bill Scam"
    assert result["rule_score"] > 0


def test_legit_sms_stays_lower_risk() -> None:
    result = score_sms("HDFCBK: Your A/c XX4321 credited Rs.15000 on 07-May. Avl Bal Rs.87650.")
    assert result["sms_score"] < 0.35


def test_sms_classifier_falls_back_without_model(monkeypatch) -> None:
    classifier._load_model.cache_clear()
    monkeypatch.setattr(classifier, "MODEL_PATH", Path("/tmp/kavach-missing-sms-model.pkl"))
    result = score_sms("Your KYC is blocked. Verify urgently.")
    assert result["ml_source"] == "lexical_fallback"
    assert classifier.sms_model_status()["backend"] == "lexical_fallback"
    assert classifier.sms_model_status()["model_state"] == "missing"
    classifier._load_model.cache_clear()


def test_dataset_profile_marks_seed_data_incomplete() -> None:
    data = pd.DataFrame(
        {
            "text": ["KYC blocked", "Salary credited", "KYC blocked"],
            "label": [1, 0, 1],
        }
    )

    profile = profile_dataset(data)

    assert profile.readiness_level == "seed_or_incomplete"
    assert profile.phishing_examples == 2
    assert profile.legit_examples == 1
    assert profile.duplicate_texts == 1
    assert profile.readiness_notes


def test_classification_metrics_include_f1_and_confusion_matrix() -> None:
    metrics = classification_metrics([1, 1, 0, 0], [1, 0, 0, 0])

    assert metrics["accuracy"] == 0.75
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 0.5
    assert metrics["f1"] > 0
    assert metrics["confusion_matrix"]["labels"] == ["legit", "phishing"]


def test_trained_sms_classifier_can_score(tmp_path, monkeypatch) -> None:
    phishing = tmp_path / "phishing.csv"
    legit = tmp_path / "legit.csv"
    model = tmp_path / "sms_classifier.pkl"
    phishing.write_text(
        "text\n"
        '"KYC blocked verify now"\n'
        '"Pay challan fine immediately"\n'
        '"FASTag penalty recharge now"\n'
        '"Share OTP to stop legal action"\n',
        encoding="utf-8",
    )
    legit.write_text(
        "text\n"
        '"Salary credited to your account"\n'
        '"Package delivered successfully"\n'
        '"Appointment confirmed for tomorrow"\n'
        '"Payment received thank you"\n',
        encoding="utf-8",
    )

    metrics = train(phishing, legit, model)
    assert model.exists()
    assert metrics["examples"] == 8.0
    assert "holdout" in metrics
    assert "f1" in metrics["holdout"]
    assert "split" in metrics
    assert metrics["split"]["train_examples"] + metrics["split"]["test_examples"] == 8
    bundle = joblib.load(model)
    assert "pipeline" in bundle
    assert bundle["metadata"]["readiness_level"] == "seed_or_incomplete"

    classifier._load_model.cache_clear()
    monkeypatch.setattr(classifier, "MODEL_PATH", model)
    phishing_result = score_sms("Your KYC blocked. Verify now to avoid account suspension.")
    legit_result = score_sms("Salary credited to your account. Available balance updated.")
    assert phishing_result["ml_source"] == "trained_model"
    assert phishing_result["confidence_band"] in {"low", "medium", "high"}
    assert phishing_result["ml_score"] > legit_result["ml_score"]
    classifier._load_model.cache_clear()

    adversarial_cases = tmp_path / "adversarial.json"
    adversarial_cases.write_text(
        '{"cases":[{"id":"p1","text":"Share OTP now to avoid account block","expected_label":1},'
        '{"id":"l1","text":"Salary credited to your account","expected_label":0}]}',
        encoding="utf-8",
    )

    evaluation = evaluate(phishing, legit, model, adversarial_cases)
    assert evaluation["metrics"]["full_dataset"]["f1"] >= metrics["holdout"]["f1"]
    assert evaluation["dataset"]["total_examples"] == 8
    assert evaluation["metrics"]["test"]["accuracy"] >= 0.0
    assert evaluation["adversarial"]["state"] == "ready"
    assert evaluation["adversarial"]["total"] == 2
    assert evaluation["adversarial"]["accuracy"] is not None
