from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.sms.evaluation import classification_metrics, profile_dataset

DEFAULT_PHISHING_CSV = ROOT / "backend" / "data" / "phishing_sms.csv"
DEFAULT_LEGIT_CSV = ROOT / "backend" / "data" / "legit_sms.csv"
DEFAULT_OUTPUT = ROOT / "backend" / "models" / "sms_classifier.pkl"
DEFAULT_SPLIT_OUTPUT = ROOT / "backend" / "models" / "sms_split.json"


def _read_dataset(path: Path, label: int) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"missing dataset: {path}")
    frame = pd.read_csv(path)
    if "text" not in frame.columns:
        raise ValueError(f"{path} must contain a 'text' column")
    frame = frame[["text"]].dropna()
    frame["text"] = frame["text"].astype(str).str.strip()
    frame = frame[frame["text"] != ""]
    frame["label"] = label
    return frame


def load_training_data(phishing_csv: Path, legit_csv: Path) -> pd.DataFrame:
    phishing = _read_dataset(phishing_csv, 1)
    legit = _read_dataset(legit_csv, 0)
    data = pd.concat([phishing, legit], ignore_index=True)
    if data["label"].nunique() != 2:
        raise ValueError("training data must contain both phishing and legitimate examples")
    return data.sample(frac=1.0, random_state=42).reset_index(drop=True)


def build_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
                    min_df=1,
                    max_features=20_000,
                    strip_accents="unicode",
                ),
            ),
            ("classifier", LogisticRegression(max_iter=1_000, class_weight="balanced", random_state=42)),
        ]
    )


def train(phishing_csv: Path, legit_csv: Path, output: Path, split_output: Path | None = None) -> dict[str, object]:
    data = load_training_data(phishing_csv, legit_csv)
    profile = profile_dataset(data)
    pipeline = build_pipeline()

    train_x, test_x, train_y, test_y = train_test_split(
        data["text"],
        data["label"],
        test_size=0.25,
        random_state=42,
        stratify=data["label"],
    )
    pipeline.fit(train_x, train_y)
    predictions = pipeline.predict(test_x)
    metrics = classification_metrics(test_y, predictions)

    output.parent.mkdir(parents=True, exist_ok=True)
    split = {
        "train_examples": int(len(train_x)),
        "test_examples": int(len(test_x)),
        "test_size": 0.25,
        "random_state": 42,
        "train_indices": list(train_x.index.astype(int)),
        "test_indices": list(test_x.index.astype(int)),
    }
    if split_output:
        split_output.parent.mkdir(parents=True, exist_ok=True)
        split_output.write_text(json.dumps(split, indent=2) + "\n", encoding="utf-8")

    joblib.dump(
        {
            "pipeline": pipeline,
            "metadata": {
                **profile.to_dict(),
                "split": split,
                "holdout": metrics,
            },
        },
        output,
    )

    print(f"Saved SMS classifier: {output}")
    print(
        "Examples: "
        f"{profile.total_examples} total, {profile.phishing_examples} phishing, {profile.legit_examples} legit"
    )
    print(f"Dataset readiness: {profile.readiness_level}")
    for note in profile.readiness_notes:
        print(f"- {note}")
    print(
        "Holdout: "
        f"accuracy={metrics['accuracy']:.3f} precision={metrics['precision']:.3f} "
        f"recall={metrics['recall']:.3f} f1={metrics['f1']:.3f}"
    )
    print(classification_report(test_y, predictions, target_names=["legit", "phishing"], zero_division=0))
    return {"dataset": profile.to_dict(), "split": split, "holdout": metrics, "examples": float(len(data))}


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the KAVACH SMS phishing classifier.")
    parser.add_argument("--phishing", type=Path, default=DEFAULT_PHISHING_CSV, help="CSV with phishing SMS text column")
    parser.add_argument("--legit", type=Path, default=DEFAULT_LEGIT_CSV, help="CSV with legitimate SMS text column")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output .pkl model path")
    parser.add_argument(
        "--split-output", type=Path, default=DEFAULT_SPLIT_OUTPUT, help="Output JSON split artifact path"
    )
    args = parser.parse_args()
    train(args.phishing, args.legit, args.output, args.split_output)


if __name__ == "__main__":
    main()
