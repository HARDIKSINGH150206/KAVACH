from backend.config import load_config
from backend.readiness import dataset_status, dependency_status, frontend_status, readiness_report


def test_dependency_status_reports_required_modules() -> None:
    dependencies = dependency_status()

    assert dependencies["fastapi"] == "ready"
    assert dependencies["numpy"] == "ready"


def test_dataset_status_marks_seed_data_incomplete() -> None:
    status = dataset_status()

    assert status["state"] == "seed_or_incomplete"
    assert status["phishing_examples"] < 5_000
    assert status["legit_examples"] < 2_500


def test_frontend_status_reports_package_files() -> None:
    status = frontend_status()

    assert status["state"] == "ready"
    assert status["package_json"] == "frontend/package.json"
    assert status["lockfile"] == "frontend/package-lock.json"


def test_readiness_report_includes_major_sections() -> None:
    report = readiness_report(load_config())

    assert report["state"] in {"ready", "attention_required"}
    assert "dependencies" in report
    assert "models" in report
    assert "dataset" in report
    assert "frontend" in report
    assert "config" in report
