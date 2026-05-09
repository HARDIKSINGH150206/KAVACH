from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.sms.evaluation import profile_dataset
from backend.sms.rule_engine import classify_scam_type
from scripts.train_sms_classifier import DEFAULT_LEGIT_CSV, DEFAULT_PHISHING_CSV, load_training_data


def audit(phishing_csv: Path, legit_csv: Path) -> dict[str, object]:
    data = load_training_data(phishing_csv, legit_csv)
    profile = profile_dataset(data).to_dict()
    scam_counts: dict[str, int] = {}
    for text in data.loc[data["label"] == 1, "text"]:
        result = classify_scam_type(str(text))
        scam_type = result["scam_type"] or "Uncategorized"
        scam_counts[scam_type] = scam_counts.get(scam_type, 0) + 1

    return {
        "dataset": profile,
        "phishing_categories": dict(sorted(scam_counts.items())),
        "action_items": profile["readiness_notes"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit KAVACH SMS dataset readiness and category coverage.")
    parser.add_argument("--phishing", type=Path, default=DEFAULT_PHISHING_CSV)
    parser.add_argument("--legit", type=Path, default=DEFAULT_LEGIT_CSV)
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    args = parser.parse_args()

    report = audit(args.phishing, args.legit)
    payload = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
