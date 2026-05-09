from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import DEFAULT_CONFIG_PATH, load_config
from backend.readiness import readiness_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Print KAVACH setup and runtime readiness as JSON.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="Path to kavach.yml")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if required items need attention")
    args = parser.parse_args()

    report = readiness_report(load_config(args.config))
    print(json.dumps(report, indent=2))
    if args.strict and report["state"] != "ready":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
