import argparse
import importlib.util
import json
import os
from datetime import datetime
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.models.model_track_contracts import ModelTrackContracts
from src.dev_tools.validation.check_model_track_boundaries import run_boundary_check


def _load_model_track_config_loader():
    config_path = PROJECT_ROOT / "src" / "core" / "config" / "model_track_config.py"
    spec = importlib.util.spec_from_file_location("model_track_config_module", config_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load model track config module from {config_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.load_model_track_config


load_model_track_config = _load_model_track_config_loader()


def _run_architecture_stage(contracts_report: dict[str, dict[str, object]]) -> dict:
    ok, violations = run_boundary_check()
    contract_status = contracts_report.get("architecture", {"ok": False, "errors": ["Missing contract report"]})
    return {
        "stage": "architecture",
        "ok": ok and bool(contract_status.get("ok", False)),
        "violations": violations,
        "contract": contract_status,
    }


def _run_data_stage(config, contracts_report: dict[str, dict[str, object]]) -> dict:
    datasets_root = Path(config.datasets_root)
    dpo_dataset = Path(config.dpo_dataset_path)
    contract_status = contracts_report.get("data", {"ok": False, "errors": ["Missing contract report"]})
    stage_ok = datasets_root.exists() and dpo_dataset.exists() and bool(contract_status.get("ok", False))
    return {
        "stage": "data",
        "ok": stage_ok,
        "datasets_root": datasets_root.as_posix(),
        "datasets_root_exists": datasets_root.exists(),
        "dpo_dataset_path": dpo_dataset.as_posix(),
        "dpo_dataset_exists": dpo_dataset.exists(),
        "contract": contract_status,
    }


def _run_embeddings_stage(config, contracts_report: dict[str, dict[str, object]]) -> dict:
    embeddings_root = Path(config.embeddings_root)
    contract_status = contracts_report.get("embeddings", {"ok": False, "errors": ["Missing contract report"]})
    stage_ok = embeddings_root.exists() and bool(contract_status.get("ok", False))
    return {
        "stage": "embeddings",
        "ok": stage_ok,
        "embeddings_root": embeddings_root.as_posix(),
        "embeddings_root_exists": embeddings_root.exists(),
        "contract": contract_status,
    }


def _run_training_stage(config, contracts_report: dict[str, dict[str, object]]) -> dict:
    checkpoints_root = Path(config.checkpoints_root)
    quickstart = Path("src/training/b3/b3_training_quickstart.py")
    dpo_pipeline = Path("src/training/pipelines/dpo_alignment.py")
    contract_status = contracts_report.get("training", {"ok": False, "errors": ["Missing contract report"]})
    stage_ok = checkpoints_root.exists() and quickstart.exists() and dpo_pipeline.exists() and bool(
        contract_status.get("ok", False)
    )
    return {
        "stage": "training",
        "ok": stage_ok,
        "checkpoints_root": checkpoints_root.as_posix(),
        "checkpoints_root_exists": checkpoints_root.exists(),
        "quickstart_exists": quickstart.exists(),
        "dpo_pipeline_exists": dpo_pipeline.exists(),
        "contract": contract_status,
    }


def _format_command(command: list[str]) -> str:
    return " ".join(command)


def _run_command(command: list[str], timeout_seconds: int, retries: int) -> dict[str, object]:
    """Execute a subprocess command with retries and timeout guardrails."""
    env = os.environ.copy()
    # Force UTF-8 IO to avoid cp1252 encode failures on Windows consoles.
    env.setdefault("PYTHONIOENCODING", "utf-8")

    attempts: list[dict[str, object]] = []
    max_attempts = max(1, retries + 1)
    for attempt_index in range(max_attempts):
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                env=env,
                timeout=max(1, timeout_seconds),
            )
            attempt = {
                "attempt": attempt_index + 1,
                "exit_code": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "timed_out": False,
            }
            attempts.append(attempt)
            if completed.returncode == 0:
                return {
                    "command": _format_command(command),
                    "exit_code": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                    "ok": True,
                    "attempts": attempts,
                }
        except subprocess.TimeoutExpired as timeout_error:
            attempts.append(
                {
                    "attempt": attempt_index + 1,
                    "exit_code": None,
                    "stdout": (timeout_error.stdout or ""),
                    "stderr": (timeout_error.stderr or ""),
                    "timed_out": True,
                }
            )

    last_attempt = attempts[-1]
    return {
        "command": _format_command(command),
        "exit_code": last_attempt.get("exit_code"),
        "stdout": last_attempt.get("stdout"),
        "stderr": last_attempt.get("stderr"),
        "ok": False,
        "attempts": attempts,
    }


def _resolve_execution_profile(profile: str) -> dict[str, object]:
    profiles: dict[str, dict[str, object]] = {
        "smoke": {
            "run_embeddings": True,
            "run_training": False,
            "run_dpo": False,
            "embedding_modalities": "text",
            "embedding_max_samples": 1,
            "embedding_dry_run": True,
            "training_epochs": 1,
            "timeout_seconds": 1800,
            "retries": 0,
            "fail_fast": True,
        },
        "standard": {
            "run_embeddings": True,
            "run_training": True,
            "run_dpo": False,
            "embedding_modalities": "text,image",
            "embedding_max_samples": 100,
            "embedding_dry_run": True,
            "training_epochs": 1,
            "timeout_seconds": 3600,
            "retries": 1,
            "fail_fast": True,
        },
        "full": {
            "run_embeddings": True,
            "run_training": True,
            "run_dpo": True,
            "embedding_modalities": "text,image,audio",
            "embedding_max_samples": 500,
            "embedding_dry_run": False,
            "training_epochs": 3,
            "timeout_seconds": 10800,
            "retries": 1,
            "fail_fast": False,
        },
    }
    return profiles.get(profile, profiles["smoke"])


def _write_run_artifact(result: dict[str, object], profile: str, artifact_dir: str) -> str:
    output_dir = Path(artifact_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"model_track_run_{profile}_{timestamp}.json"
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return output_path.as_posix()


def _build_execution_plan(
    python_exe: str,
    embedding_modalities: str,
    embedding_max_samples: int,
    embedding_dry_run: bool,
    training_epochs: int,
) -> dict[str, list[str]]:
    embedding_command = [
        python_exe,
        "src/data/pipelines/embed_f_drive_full.py",
        "--modalities",
        embedding_modalities,
        "--max-vram-gb",
        "3.0",
        "--max-samples",
        str(embedding_max_samples),
    ]
    if embedding_dry_run:
        embedding_command.append("--dry-run")

    training_command = [
        python_exe,
        "src/training/b3/b3_training_quickstart.py",
        "--phase",
        "single_modal",
        "--modality",
        "text",
        "--epochs",
        str(training_epochs),
    ]

    dpo_command = [
        python_exe,
        "src/training/pipelines/dpo_alignment.py",
    ]

    return {
        "embeddings": embedding_command,
        "training": training_command,
        "dpo": dpo_command,
    }


def run_model_track(
    dry_run: bool = True,
    run_embeddings: bool = False,
    run_training: bool = False,
    run_dpo: bool = False,
    profile: str = "smoke",
    python_exe: str = sys.executable,
    embedding_modalities: str | None = None,
    embedding_max_samples: int | None = None,
    embedding_dry_run: bool | None = None,
    training_epochs: int | None = None,
    timeout_seconds: int | None = None,
    retries: int | None = None,
    fail_fast: bool | None = None,
    artifact_dir: str = "src/training/pipelines/model_track_runs",
) -> dict:
    """Run model-only track verification in architecture->data->embeddings->training order."""
    config = load_model_track_config()
    contracts = ModelTrackContracts()
    contracts_report = contracts.validate_all(config)

    stages = [
        _run_architecture_stage(contracts_report),
        _run_data_stage(config, contracts_report),
        _run_embeddings_stage(config, contracts_report),
        _run_training_stage(config, contracts_report),
    ]

    all_ok = all(stage.get("ok", False) for stage in stages)

    selected_profile = _resolve_execution_profile(profile)

    # Profile defaults apply unless stage flags are explicitly provided.
    if not any([run_embeddings, run_training, run_dpo]):
        run_embeddings = bool(selected_profile["run_embeddings"])
        run_training = bool(selected_profile["run_training"])
        run_dpo = bool(selected_profile["run_dpo"])

    if embedding_modalities is None:
        embedding_modalities = str(selected_profile["embedding_modalities"])
    if embedding_max_samples is None:
        embedding_max_samples = int(selected_profile["embedding_max_samples"])
    if embedding_dry_run is None:
        embedding_dry_run = bool(selected_profile["embedding_dry_run"])
    if training_epochs is None:
        training_epochs = int(selected_profile["training_epochs"])
    if timeout_seconds is None:
        timeout_seconds = int(selected_profile["timeout_seconds"])
    if retries is None:
        retries = int(selected_profile["retries"])
    if fail_fast is None:
        fail_fast = bool(selected_profile["fail_fast"])

    execution_plan = _build_execution_plan(
        python_exe=python_exe,
        embedding_modalities=embedding_modalities,
        embedding_max_samples=embedding_max_samples,
        embedding_dry_run=embedding_dry_run,
        training_epochs=training_epochs,
    )
    execution_results: dict[str, dict[str, object]] = {}

    if not dry_run and all_ok:
        if run_embeddings:
            execution_results["embeddings"] = _run_command(
                execution_plan["embeddings"], timeout_seconds=timeout_seconds, retries=retries
            )
            if fail_fast and not execution_results["embeddings"].get("ok", False):
                execution_ok = False
                result = {
                    "mode": "execute",
                    "ok": False,
                    "profile": profile,
                    "contracts": contracts_report,
                    "stages": stages,
                    "execution_plan": {k: _format_command(v) for k, v in execution_plan.items()},
                    "execution_results": execution_results,
                }
                result["artifact_path"] = _write_run_artifact(result, profile=profile, artifact_dir=artifact_dir)
                return result
        if run_training:
            execution_results["training"] = _run_command(
                execution_plan["training"], timeout_seconds=timeout_seconds, retries=retries
            )
            if fail_fast and not execution_results["training"].get("ok", False):
                execution_ok = False
                result = {
                    "mode": "execute",
                    "ok": False,
                    "profile": profile,
                    "contracts": contracts_report,
                    "stages": stages,
                    "execution_plan": {k: _format_command(v) for k, v in execution_plan.items()},
                    "execution_results": execution_results,
                }
                result["artifact_path"] = _write_run_artifact(result, profile=profile, artifact_dir=artifact_dir)
                return result
        if run_dpo:
            execution_results["dpo"] = _run_command(
                execution_plan["dpo"], timeout_seconds=timeout_seconds, retries=retries
            )

    execution_ok = all(result.get("ok", False) for result in execution_results.values()) if execution_results else True
    final_result = {
        "mode": "dry-run" if dry_run else "execute",
        "ok": all_ok and execution_ok,
        "profile": profile,
        "contracts": contracts_report,
        "stages": stages,
        "execution_plan": {k: _format_command(v) for k, v in execution_plan.items()},
        "execution_results": execution_results,
        "guardrails": {
            "timeout_seconds": timeout_seconds,
            "retries": retries,
            "fail_fast": fail_fast,
        },
    }
    final_result["artifact_path"] = _write_run_artifact(final_result, profile=profile, artifact_dir=artifact_dir)
    return final_result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run model-only architecture->data->embeddings->training pipeline checks."
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Enable execution mode (still gated by stage validation and explicit run flags).",
    )
    parser.add_argument(
        "--profile",
        choices=["smoke", "standard", "full"],
        default="smoke",
        help="Execution profile defaults used when stage flags are not explicitly provided.",
    )
    parser.add_argument("--run-embeddings", action="store_true", help="Execute embedding stage command in execute mode.")
    parser.add_argument("--run-training", action="store_true", help="Execute baseline training stage command in execute mode.")
    parser.add_argument("--run-dpo", action="store_true", help="Execute DPO stage command in execute mode.")
    parser.add_argument(
        "--python-exe",
        default=sys.executable,
        help="Python executable to use for staged command execution.",
    )
    parser.add_argument(
        "--embedding-modalities",
        default=None,
        help="Comma-separated modalities for embedding stage command (profile default when omitted).",
    )
    parser.add_argument(
        "--embedding-max-samples",
        type=int,
        default=None,
        help="Sample cap used in embedding stage command (profile default when omitted).",
    )
    embedding_mode = parser.add_mutually_exclusive_group()
    embedding_mode.add_argument(
        "--embedding-write",
        dest="embedding_write",
        action="store_true",
        help="Set embedding stage command to write outputs.",
    )
    embedding_mode.add_argument(
        "--embedding-dry-run",
        dest="embedding_write",
        action="store_false",
        help="Force embedding stage command to dry-run mode.",
    )
    parser.set_defaults(embedding_write=None)
    parser.add_argument(
        "--training-epochs",
        type=int,
        default=None,
        help="Epoch count for baseline training stage command (profile default when omitted).",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=None,
        help="Per-stage timeout in seconds for execution commands (profile default when omitted).",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=None,
        help="Retry count per stage command when execution fails or times out (profile default when omitted).",
    )
    fail_fast_mode = parser.add_mutually_exclusive_group()
    fail_fast_mode.add_argument(
        "--fail-fast",
        dest="fail_fast",
        action="store_true",
        help="Stop execution after the first failing stage command.",
    )
    fail_fast_mode.add_argument(
        "--no-fail-fast",
        dest="fail_fast",
        action="store_false",
        help="Continue remaining stages even if a stage fails.",
    )
    parser.set_defaults(fail_fast=None)
    parser.add_argument(
        "--artifact-dir",
        default="src/training/pipelines/model_track_runs",
        help="Directory to persist structured run artifacts.",
    )
    args = parser.parse_args()

    result = run_model_track(
        dry_run=not args.execute,
        run_embeddings=args.run_embeddings,
        run_training=args.run_training,
        run_dpo=args.run_dpo,
        profile=args.profile,
        python_exe=args.python_exe,
        embedding_modalities=args.embedding_modalities,
        embedding_max_samples=(None if args.embedding_max_samples is None else max(1, args.embedding_max_samples)),
        embedding_dry_run=(None if args.embedding_write is None else not args.embedding_write),
        training_epochs=(None if args.training_epochs is None else max(1, args.training_epochs)),
        timeout_seconds=(None if args.timeout_seconds is None else max(1, args.timeout_seconds)),
        retries=(None if args.retries is None else max(0, args.retries)),
        fail_fast=args.fail_fast,
        artifact_dir=args.artifact_dir,
    )
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
