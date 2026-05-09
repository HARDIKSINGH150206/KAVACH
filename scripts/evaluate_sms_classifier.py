from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.sms.evaluation import classification_metrics, profile_dataset
from scripts.train_sms_classifier import DEFAULT_LEGIT_CSV, DEFAULT_OUTPUT, DEFAULT_PHISHING_CSV, load_training_data

DEFAULT_ADVERSARIAL_CASES = ROOT / "backend" / "data" / "sms_adversarial_cases.json"


def _load_pipeline(model_path: Path):
    if not model_path.exists():
        raise FileNotFoundError(f"missing model: {model_path}")
    bundle = joblib.load(model_path)
    if isinstance(bundle, dict) and "pipeline" in bundle:
        return bundle["pipeline"], bundle.get("metadata", {})
    return bundle, {}


def _evaluate_adversarial_cases(pipeline, cases_path: Path) -> dict[str, object]:
    if not cases_path.exists():
        return {"state": "missing", "path": str(cases_path), "total": 0, "accuracy": None, "failures": []}
    payload = json.loads(cases_path.read_text(encoding="utf-8"))
    cases = payload.get("cases", []) if isinstance(payload, dict) else []
    frame = pd.DataFrame(cases)
    if frame.empty:
        return {"state": "empty", "path": str(cases_path), "total": 0, "accuracy": None, "failures": []}
    required_cols = {"text", "expected_label", "id"}
    if not required_cols.issubset(frame.columns):
        return {
            "state": "invalid",
            "path": str(cases_path),
            "total": int(len(frame)),
            "accuracy": None,
            "failures": ["Missing one or more required keys: id, text, expected_label"],
        }

    predictions = pipeline.predict(frame["text"])
    frame = frame.assign(predicted_label=predictions)
    failed = frame[frame["expected_label"].astype(int) != frame["predicted_label"].astype(int)]
    failures = failed[["id", "expected_label", "predicted_label"]].to_dict(orient="records")
    accuracy = 1.0 - (len(failures) / len(frame))
    return {
        "state": "ready",
        "path": str(cases_path),
        "total": int(len(frame)),
        "accuracy": round(float(accuracy), 4),
        "failures": failures,
    }


def evaluate(phishing_csv: Path, legit_csv: Path, model_path: Path, adversarial_cases: Path) -> dict[str, object]:
    data = load_training_data(phishing_csv, legit_csv)
    profile = profile_dataset(data)
    pipeline, metadata = _load_pipeline(model_path)
    train_x, test_x, train_y, test_y = train_test_split(
        data["text"],
        data["label"],
        test_size=0.25,
        random_state=42,
        stratify=data["label"],
    )
    train_predictions = pipeline.predict(train_x)
    test_predictions = pipeline.predict(test_x)
    return {
        "model_path": str(model_path),
        "training_metadata": metadata,
        "dataset": profile.to_dict(),
        "metrics": {
            "train": classification_metrics(train_y, train_predictions),
            "test": classification_metrics(test_y, test_predictions),
            "full_dataset": classification_metrics(data["label"], pipeline.predict(data["text"])),
        },
        "adversarial": _evaluate_adversarial_cases(pipeline, adversarial_cases),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a trained KAVACH SMS classifier.")
    parser.add_argument("--phishing", type=Path, default=DEFAULT_PHISHING_CSV, help="CSV with phishing SMS text column")
    parser.add_argument("--legit", type=Path, default=DEFAULT_LEGIT_CSV, help="CSV with legitimate SMS text column")
    parser.add_argument("--model", type=Path, default=DEFAULT_OUTPUT, help="Trained .pkl model path")
    parser.add_argument(
        "--adversarial-cases",
        type=Path,
        default=DEFAULT_ADVERSARIAL_CASES,
        help="JSON file with adversarial SMS test cases",
    )
    parser.add_argument(
        "--min-adversarial-accuracy",
        type=float,
        default=0.75,
        help="Exit non-zero if adversarial accuracy is below this threshold",
    )
    parser.add_argument("--strict", action="store_true", help="Fail with non-zero exit code on threshold violations")
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    args = parser.parse_args()
    report = evaluate(args.phishing, args.legit, args.model, args.adversarial_cases)
    payload = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    if args.strict:
        adversarial = report["adversarial"]
        accuracy = adversarial.get("accuracy")
        if adversarial.get("state") != "ready" or accuracy is None:
            raise SystemExit("Adversarial cases are not ready")
        if float(accuracy) < float(args.min_adversarial_accuracy):
            raise SystemExit(
                f"Adversarial accuracy {accuracy:.3f} is below threshold {args.min_adversarial_accuracy:.3f}"
            )


if __name__ == "__main__":
    main()
