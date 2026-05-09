from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support


@dataclass(frozen=True)
class DatasetProfile:
    total_examples: int
    phishing_examples: int
    legit_examples: int
    duplicate_texts: int
    phishing_ratio: float
    readiness_level: str
    readiness_notes: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "total_examples": self.total_examples,
            "phishing_examples": self.phishing_examples,
            "legit_examples": self.legit_examples,
            "duplicate_texts": self.duplicate_texts,
            "phishing_ratio": round(self.phishing_ratio, 3),
            "readiness_level": self.readiness_level,
            "readiness_notes": self.readiness_notes,
        }


MIN_PHISHING_EXAMPLES = 5_000
MIN_LEGIT_EXAMPLES = 2_500
RECOMMENDED_PHISHING_RATIO_RANGE = (0.35, 0.75)


def profile_dataset(data: pd.DataFrame) -> DatasetProfile:
    if "text" not in data.columns or "label" not in data.columns:
        raise ValueError("dataset must contain text and label columns")

    total = int(len(data))
    phishing = int((data["label"] == 1).sum())
    legit = int((data["label"] == 0).sum())
    duplicates = int(data["text"].astype(str).str.lower().duplicated().sum())
    ratio = phishing / total if total else 0.0

    notes: list[str] = []
    if phishing < MIN_PHISHING_EXAMPLES:
        notes.append(
            f"Need at least {MIN_PHISHING_EXAMPLES:,} phishing examples for the planned credible prototype target."
        )
    if legit < MIN_LEGIT_EXAMPLES:
        notes.append(
            f"Need at least {MIN_LEGIT_EXAMPLES:,} legitimate examples for the planned credible prototype target."
        )
    if duplicates:
        notes.append(f"Remove or review {duplicates} duplicate SMS texts.")
    min_ratio, max_ratio = RECOMMENDED_PHISHING_RATIO_RANGE
    if total and not min_ratio <= ratio <= max_ratio:
        notes.append(
            f"Class balance is outside the recommended {int(min_ratio * 100)}%-{int(max_ratio * 100)}% phishing range."
        )

    readiness = "production_ready" if not notes else "seed_or_incomplete"
    return DatasetProfile(
        total_examples=total,
        phishing_examples=phishing,
        legit_examples=legit,
        duplicate_texts=duplicates,
        phishing_ratio=ratio,
        readiness_level=readiness,
        readiness_notes=notes,
    )


def classification_metrics(y_true, y_pred) -> dict[str, object]:
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        average="binary",
        pos_label=1,
        zero_division=0,
    )
    labels = [0, 1]
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "confusion_matrix": {
            "labels": ["legit", "phishing"],
            "matrix": matrix.astype(int).tolist(),
        },
    }
