from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
from pathlib import Path

from backend.audio.aasist_infer import AASISTScorer
from backend.audio.urgency_nlp import muril_status, score_transcript
from backend.audio.whisper_stt import whisper_status
from backend.config import DEFAULT_CONFIG_PATH, load_config
from backend.events import threat_event_path
from backend.fusion.engine import configure_fusion, fuse
from backend.readiness import readiness_report
from backend.sms.classifier import score_sms, sms_model_status
from scripts.download_models import inspect_assets


def _print_json(payload: object) -> None:
    """Print a JSON payload to stdout with indentation."""
    print(json.dumps(payload, indent=2))


PID_FILE_DEFAULT = Path(".kavach.pid")
LOG_FILE_DEFAULT = Path("logs/kavach.log")


def _write_pid(pid_file: Path, pid: int) -> None:
    """Write the process ID to a PID file."""
    pid_file.write_text(str(pid), encoding="utf-8")


def _read_pid(pid_file: Path) -> int | None:
    """Read the process ID from a PID file, or None if not found/invalid."""
    if not pid_file.exists():
        return None
    try:
        return int(pid_file.read_text(encoding="utf-8").strip())
    except ValueError:
        return None


def _is_process_running(pid: int) -> bool:
    """Check if a process with the given PID is running."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _start_background_server(host: str, port: int, log_file: Path, pid_file: Path) -> int:
    """Start the FastAPI server in the background and return the PID."""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    handle = open(log_file, "a", encoding="utf-8")
    process = subprocess.Popen(
        command, cwd=Path(__file__).resolve().parents[1], stdout=handle, stderr=handle, close_fds=True
    )
    _write_pid(pid_file, process.pid)
    return process.pid


def start_command(args: argparse.Namespace) -> None:
    """Start the KAVACH backend server in the background."""
    pid_file = args.pid_file
    existing_pid = _read_pid(pid_file)
    if existing_pid and _is_process_running(existing_pid):
        print(f"KAVACH is already running with PID {existing_pid}")
        return
    pid = _start_background_server(args.host, args.port, args.log_file, pid_file)
    print(f"Started KAVACH backend with PID {pid}. Logs are written to {args.log_file}")


def stop_command(args: argparse.Namespace) -> None:
    """Stop the running KAVACH backend server."""
    pid_file = args.pid_file
    pid = _read_pid(pid_file)
    if not pid or not _is_process_running(pid):
        print("No running KAVACH process found.")
        pid_file.unlink(missing_ok=True)
        return
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"Stopped KAVACH backend with PID {pid}.")
    except PermissionError as exc:
        print(f"Permission denied when stopping process {pid}: {exc}")
    finally:
        pid_file.unlink(missing_ok=True)


def status_command(args: argparse.Namespace) -> None:
    """Display the current configuration and model status."""
    config = load_config(args.config)
    assets = inspect_assets()
    aasist = AASISTScorer()
    _print_json(
        {
            "audio_source": config.audio_source,
            "fusion": {
                "audio_weight": config.fusion.audio_weight,
                "sms_weight": config.fusion.sms_weight,
                "transcript_weight": config.fusion.transcript_weight,
                "thresholds": config.fusion.resolved_thresholds(),
            },
            "models": [asset.to_json() for asset in assets],
            "runtime_models": {
                "audio": aasist.status.model_dump(),
                "speech_to_text": whisper_status(),
                "urgency_nlp": muril_status(),
                "sms": sms_model_status(),
            },
            "logging": {
                "level": config.logging.level,
                "threat_events": str(threat_event_path(config.logging)),
            },
            "readiness": readiness_report(config),
        }
    )


def score_sms_command(args: argparse.Namespace) -> None:
    """Score an SMS message for phishing likelihood."""
    _print_json(score_sms(args.text))


def score_transcript_command(args: argparse.Namespace) -> None:
    """Score a call transcript for urgency indicators."""
    _print_json(score_transcript(args.text))


def score_fusion_command(args: argparse.Namespace) -> None:
    """Fuse audio, SMS, and transcript scores into a threat assessment."""
    config = load_config(args.config)
    configure_fusion(
        config.fusion.audio_weight,
        config.fusion.sms_weight,
        config.fusion.resolved_thresholds(),
        transcript_weight=config.fusion.transcript_weight,
    )
    result = fuse(args.audio_score, args.sms_score, args.transcript_score)
    _print_json(
        {
            "audio_score": result.audio_score,
            "sms_score": result.sms_score,
            "transcript_score": result.transcript_score,
            "threat_score": result.threat_score,
            "threat_level": result.threat_level.value,
            "formula": result.formula_str,
            "explanation": result.explanation,
        }
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(prog="kavach", description="KAVACH local scoring CLI")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="Path to kavach.yml")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="Show config and model asset status")
    status.set_defaults(func=status_command)

    start = subparsers.add_parser("start", help="Start the KAVACH backend in the background")
    start.add_argument("--host", default="0.0.0.0", help="Host address for the backend")
    start.add_argument("--port", type=int, default=8000, help="Port for the backend")
    start.add_argument(
        "--pid-file",
        type=Path,
        default=PID_FILE_DEFAULT,
        help="PID file path for the running backend",
    )
    start.add_argument(
        "--log-file",
        type=Path,
        default=LOG_FILE_DEFAULT,
        help="Log file path for the backend",
    )
    start.set_defaults(func=start_command)

    stop = subparsers.add_parser("stop", help="Stop the running KAVACH backend")
    stop.add_argument(
        "--pid-file",
        type=Path,
        default=PID_FILE_DEFAULT,
        help="PID file path for the running backend",
    )
    stop.set_defaults(func=stop_command)

    sms = subparsers.add_parser("score-sms", help="Score an SMS message")
    sms.add_argument("text", help="SMS text to score")
    sms.set_defaults(func=score_sms_command)

    transcript = subparsers.add_parser("score-transcript", help="Score a call transcript for urgency")
    transcript.add_argument("text", help="Transcript text to score")
    transcript.set_defaults(func=score_transcript_command)

    fusion = subparsers.add_parser("score-fusion", help="Fuse audio and SMS scores")
    fusion.add_argument("--audio-score", type=float, required=True, help="Audio score from -1 to 1")
    fusion.add_argument("--sms-score", type=float, required=True, help="SMS score from -1 to 1")
    fusion.add_argument("--transcript-score", type=float, default=-1.0, help="Optional transcript urgency score")
    fusion.set_defaults(func=score_fusion_command)
    return parser


def main() -> None:
    """Main entry point for the KAVACH CLI."""
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
