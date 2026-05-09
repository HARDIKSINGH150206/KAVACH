from pathlib import Path

from scripts import download_models


def test_model_asset_inspection_uses_expected_paths(tmp_path, monkeypatch) -> None:
    models_dir = tmp_path / "models"
    monkeypatch.setattr(download_models, "ROOT", tmp_path)
    monkeypatch.setattr(download_models, "MODELS_DIR", models_dir)
    monkeypatch.setattr(download_models, "AASIST_DIR", models_dir / "aasist_checkpoint")
    monkeypatch.setattr(download_models, "WHISPER_DIR", models_dir / "whisper")
    monkeypatch.setattr(download_models, "MURIL_DIR", models_dir / "muril")
    monkeypatch.setattr(download_models, "SMS_MODEL", models_dir / "sms_classifier.pkl")
    monkeypatch.setattr(download_models, "MANIFEST", models_dir / "manifest.json")

    assets = download_models.inspect_assets()
    statuses = {asset.name: asset.status for asset in assets}

    assert statuses["sms_classifier"] == "missing"
    assert statuses["aasist"] == "missing"
    assert (models_dir / "aasist_checkpoint").is_dir()
    assert (models_dir / "whisper").is_dir()
    assert (models_dir / "muril").is_dir()
    assert "download-aasist" in assets[1].note


def test_model_manifest_marks_ready_assets(tmp_path, monkeypatch) -> None:
    models_dir = tmp_path / "models"
    sms_model = models_dir / "sms_classifier.pkl"
    aasist_dir = models_dir / "aasist_checkpoint"
    aasist_dir.mkdir(parents=True)
    sms_model.write_bytes(b"model")
    (aasist_dir / "checkpoint.pt").write_bytes(b"checkpoint")

    monkeypatch.setattr(download_models, "ROOT", tmp_path)
    monkeypatch.setattr(download_models, "MODELS_DIR", models_dir)
    monkeypatch.setattr(download_models, "AASIST_DIR", aasist_dir)
    monkeypatch.setattr(download_models, "WHISPER_DIR", models_dir / "whisper")
    monkeypatch.setattr(download_models, "MURIL_DIR", models_dir / "muril")
    monkeypatch.setattr(download_models, "SMS_MODEL", sms_model)
    monkeypatch.setattr(download_models, "MANIFEST", models_dir / "manifest.json")

    assets = download_models.inspect_assets()
    download_models.write_manifest(assets)
    manifest = Path(download_models.MANIFEST).read_text(encoding="utf-8")

    statuses = {asset.name: asset.status for asset in assets}
    assert statuses["sms_classifier"] == "ready"
    assert statuses["aasist"] == "ready"
    assert "sms_classifier.pkl" in manifest
