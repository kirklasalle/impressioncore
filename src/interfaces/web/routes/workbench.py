"""Local, project-scoped contracts for the ImpressionCore engineering workbench."""

import hashlib
import io
import json
import logging
import math
import os
import threading
import uuid
import zipfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request, send_file, session
from werkzeug.exceptions import HTTPException

from src.core.config.data_paths import CHECKPOINTS_ROOT, DATA_DRIVE, PROJECT_ROOT
from src.core.config.presets import get_builder_offering_presets
from src.core.utils.temp_paths import get_temp_dir

workbench_bp = Blueprint("workbench", __name__, url_prefix="/api/v1/builder/workbench")
logger = logging.getLogger(__name__)
_STORE_LOCK = threading.RLock()
_ACTIVE_LOCK = threading.Lock()
_ACTIVE = None
_STOP = threading.Event()
MAX_DATA_BYTES = 8 * 1024 * 1024
MAX_RECORDS = 4096
NATIVE_TEMPLATE = {
    "embed_dim": 224, "num_heads": 8, "num_layers": 12, "vocab_size": 16384,
    "num_experts": 4, "expert_dim": 320, "experts_per_token": 2,
    "image_embed_dim": 224, "audio_embed_dim": 224, "phoneme_vocab_size": 256,
    "dropout": 0.1, "max_seq_length": 2048, "use_gradient_checkpointing": True,
    "use_mhc": True, "mhc_iterations": 20, "b3_ultra": False,
}
ARCHITECTURE = {
    "id": "impressioncore_b3", "name": "Native ImpressionCore B3",
    "source": "src/core/models/impressioncore_b3_architecture.py",
    "objective": "prefix_next_token",
    "detail": "Text research adapter: each record contributes one bounded prefix and its next-token target; "
              "there is no all-position loss or GPT-2 substitution. "
              "The native expert router attends across a prefix; this is not all-position causal LM training. "
              "The research template comes from train_b3_39m.py; its parameter count is measured at execution, not inferred from its name.",
}


def offering_execution_map():
    """Describe registered reference offerings without inventing native adapters."""
    result = {}
    for offering_id, preset in get_builder_offering_presets().items():
        stage = preset.get("stage")
        if stage in ("B1", "B2"):
            status = "unavailable"
            detail = f"No native {stage} implementation is registered; reference dimensions are not translated."
        elif stage == "B3":
            status = "reference_only"
            detail = "A custom native B3 configuration can run, but this named reference is not certified or dimension-mapped."
        else:
            status = "unavailable"
            detail = f"No native {stage or 'unknown-stage'} implementation is registered."
        result[offering_id] = {
            "id": offering_id,
            "name": preset.get("name", offering_id),
            "status": status,
            "certified": False,
            "detail": detail,
        }
    return result


def offering_execution(offering_id):
    """Return execution truth for a reference offering, if one was selected."""
    return offering_execution_map().get(offering_id) if offering_id else None
CAPABILITIES = [
    {"id": "projects", "name": "Named local projects", "status": "available", "detail": "Revision-checked save, import and configuration export."},
    {"id": "native", "name": "Native B3 text experiments", "status": "available", "detail": "Bounded, local-only prefix/next-token training; strict workbench checkpoint fine-tuning."},
    {"id": "evaluation", "name": "Held-out evaluation", "status": "available", "detail": "Token-weighted prefix prediction cross-entropy and perplexity; no demo scores."},
    {"id": "inference", "name": "Checkpoint inference", "status": "available", "detail": "Explicit local native checkpoint loading and bounded generation."},
    {"id": "export", "name": "Reproducible artifact bundle", "status": "available", "detail": "Native checkpoint, tokenizer, hashes, configuration and run provenance."},
    {"id": "resume", "name": "Exact optimizer resume / pause", "status": "unavailable", "detail": "Fine-tuning starts a new optimizer. Stop is cooperative; no false resume or pause."},
    {"id": "multimodal", "name": "Multimodal / cognitive experiments", "status": "research", "detail": "Native architecture retains multimodal modules; this adapter trains text only. No unverified module toggles."},
    {"id": "tokenizer_training", "name": "Tokenizer training", "status": "unavailable", "detail": "Use an existing local tokenizer.json. Legacy tokenizer training is simulated; not exposed as execution."},
    {"id": "legacy", "name": "Legacy tools", "status": "legacy", "detail": "Existing pages remain accessible; they are not project-scoped and may contain experimental operations.", "route": "/documentation"},
]


class WorkbenchError(ValueError):
    """Expected, actionable API failure."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def now():
    """Return a timezone-aware provenance timestamp."""
    return datetime.now(timezone.utc).isoformat()


def root(kind):
    """Resolve configured storage without moving existing user artifacts."""
    if kind == "projects":
        return Path(current_app.config.get("WORKBENCH_PROJECT_ROOT", PROJECT_ROOT / "data" / "knowledge" / "workbench"))
    return Path(current_app.config.get("WORKBENCH_ARTIFACT_ROOT", CHECKPOINTS_ROOT / "workbench"))


def identifier(value):
    """Accept only internally generated hexadecimal IDs."""
    if not isinstance(value, str) or len(value) != 32 or any(c not in "0123456789abcdef" for c in value):
        raise WorkbenchError("Invalid project or run identifier.")
    return value


def atomic_json(path, value):
    """Commit a complete JSON document with an atomic replacement."""
    with _STORE_LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f"{path.name}.{uuid.uuid4().hex}.tmp")
        try:
            temporary.write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")
            os.replace(temporary, path)
        finally:
            if temporary.exists():
                temporary.unlink()


def read_json(path):
    """Read an existing JSON object; do not mask corrupt project state."""
    # Windows readers must release handles before another thread replaces the file.
    with _STORE_LOCK:
        if not path.is_file():
            raise WorkbenchError("Project or run not found.", 404)
        value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise WorkbenchError("Stored configuration is not a JSON object.", 500)
    return value


def project_path(project_id):
    return root("projects") / f"{identifier(project_id)}.json"


def project_get(project_id):
    return read_json(project_path(project_id))


def run_dir(project_id, run_id):
    return root("artifacts") / identifier(project_id) / identifier(run_id)


def run_get(project_id, run_id):
    with _STORE_LOCK:
        value = read_json(run_dir(project_id, run_id) / "run.json")
        with _ACTIVE_LOCK:
            active = _ACTIVE == (project_id, run_id)
            stopping = active and _STOP.is_set()
        if value["state"] in ("queued", "running", "stopping") and not active:
            value.update(state="interrupted", error="Server restarted or job owner is unavailable. No automatic resume was attempted.", updated_at=now())
            atomic_json(run_dir(project_id, run_id) / "run.json", value)
        elif stopping and value["state"] in ("queued", "running"):
            value["state"] = "stopping"
    return value


def project_summary(value):
    return {key: value[key] for key in ("id", "name", "revision", "updated_at", "offering")}


def project_list():
    directory = root("projects")
    return sorted(
        [project_summary(read_json(path)) for path in directory.glob("*.json")],
        key=lambda item: item["updated_at"], reverse=True,
    ) if directory.exists() else []


def validate_project(value):
    """Validate editable project fields without loading weights or tokenizers."""
    if not isinstance(value, dict):
        raise WorkbenchError("Configuration must be a JSON object.")
    name = value.get("name")
    if not isinstance(name, str) or not name.strip() or len(name) > 100:
        raise WorkbenchError("Project name must contain 1-100 characters.")
    presets = get_builder_offering_presets()
    if value.get("offering") is not None and (
        not isinstance(value["offering"], str) or value["offering"] not in presets
    ):
        raise WorkbenchError("Unknown offering.")
    for key in ("model", "dataset", "tokenizer", "training"):
        if not isinstance(value.get(key), dict):
            raise WorkbenchError(f"{key} must be a JSON object.")
    if not isinstance(value.get("notes", ""), str) or len(value.get("notes", "")) > 20000:
        raise WorkbenchError("Notes must be text of at most 20,000 characters.")
    if value.get("objective", ARCHITECTURE["objective"]) != ARCHITECTURE["objective"]:
        raise WorkbenchError(
            f"Unsupported objective. The native adapter supports only {ARCHITECTURE['objective']}."
        )
    dataset = value["dataset"]
    if dataset.get("format") not in ("text", "jsonl"):
        raise WorkbenchError("Dataset format must be text or jsonl.")
    for key in ("path", "validation_path", "text_field"):
        if not isinstance(dataset.get(key), str) or len(dataset[key]) > 4096:
            raise WorkbenchError(f"Dataset {key} must be a path or field-name string.")
    if not dataset["text_field"]:
        raise WorkbenchError("JSONL text field cannot be empty.")
    if not isinstance(value["tokenizer"].get("path"), str):
        raise WorkbenchError("Tokenizer path must be a string.")
    training = value["training"]
    for key, lower, upper in (
        ("epochs", 1, 100), ("batchSize", 1, 1), ("gradAccumSteps", 1, 128),
        ("maxSteps", 1, 100000), ("sequenceLength", 2, 2048), ("seed", 0, 2147483647),
    ):
        if type(training.get(key)) is not int or not lower <= training[key] <= upper:
            raise WorkbenchError(f"{key} must be an integer {lower}-{upper}.")
    lr = training.get("learningRate")
    if type(lr) not in (int, float) or not math.isfinite(lr) or not 1e-8 <= lr <= 0.01:
        raise WorkbenchError("Learning rate must be finite and between 1e-8 and 0.01.")
    if training.get("device") not in ("cpu", "cuda") or training.get("mode") not in ("scratch", "finetune"):
        raise WorkbenchError("Choose CPU/CUDA and scratch/finetune explicitly.")
    if not isinstance(training.get("checkpoint_run_id"), str):
        raise WorkbenchError("Checkpoint run ID must be a string.")
    native = value.get("native_config")
    if native is not None:
        if not isinstance(native, dict) or set(native) != set(NATIVE_TEMPLATE):
            raise WorkbenchError("Native configuration must contain exactly the documented B3Config fields.")
        for key in ("use_gradient_checkpointing", "use_mhc", "b3_ultra"):
            if type(native[key]) is not bool:
                raise WorkbenchError(f"{key} must be a boolean.")
        if native["b3_ultra"]:
            raise WorkbenchError("B3 Ultra execution is not validated by this text adapter.")
        for key, lower, upper in (
            ("embed_dim", 8, 4096), ("num_heads", 1, 128), ("num_layers", 1, 32),
            ("vocab_size", 4, 256000), ("num_experts", 1, 64), ("expert_dim", 8, 16384),
            ("experts_per_token", 1, 64), ("image_embed_dim", 8, 4096),
            ("audio_embed_dim", 8, 4096), ("phoneme_vocab_size", 4, 4096),
            ("max_seq_length", 2, 32768), ("mhc_iterations", 1, 100),
        ):
            if type(native[key]) is not int or not lower <= native[key] <= upper:
                raise WorkbenchError(f"Native {key} must be an integer {lower}-{upper}.")
        if native["embed_dim"] % native["num_heads"] or native["embed_dim"] % 2:
            raise WorkbenchError("Native embedding size must be even and divisible by heads.")
        if native["experts_per_token"] > native["num_experts"]:
            raise WorkbenchError("Experts per token cannot exceed expert count.")
        if type(native["dropout"]) not in (int, float) or not 0 <= native["dropout"] < 1:
            raise WorkbenchError("Dropout must be between 0 and 1.")
        if training["sequenceLength"] > native["max_seq_length"]:
            raise WorkbenchError("Training sequence length exceeds the native context window.")
    return value


def _allowed_local_roots():
    """Return resolved directory roots permitted for local workbench file reads."""
    roots = [
        PROJECT_ROOT.resolve(),
        DATA_DRIVE.resolve(),
        CHECKPOINTS_ROOT.resolve(),
        root("projects").resolve(),
        root("artifacts").resolve(),
    ]
    for extra in current_app.config.get("WORKBENCH_ALLOWED_ROOTS", ()):
        roots.append(Path(extra).expanduser().resolve())
    if current_app.config.get("TESTING"):
        try:
            roots.append(get_temp_dir())
        except RuntimeError:
            pass
        for env_var in ("PYTEST_DEBUG_TEMPROOT", "TEMP", "TMP", "TMPDIR"):
            if os.environ.get(env_var):
                roots.append(Path(os.environ[env_var]).resolve())
    return roots


def bounded_file(path, maximum=MAX_DATA_BYTES):
    """Read a bounded local artifact confined to allowed roots, never a URL."""
    if not isinstance(path, str) or not path.strip():
        raise WorkbenchError("A local file path is required.")
    candidate = Path(path).expanduser().resolve()
    if not any(candidate.is_relative_to(allowed) for allowed in _allowed_local_roots()):
        raise WorkbenchError("Local file path must reside within an allowed workspace or data root.")
    if not candidate.is_file():
        raise WorkbenchError(f"Local file not found: {candidate}")
    with candidate.open("rb") as source:
        data = source.read(maximum + 1)
    if len(data) > maximum:
        raise WorkbenchError(f"File exceeds the {maximum // (1024 * 1024)} MiB workbench limit. Prepare a bounded dataset shard.")
    return data


def load_dataset(project, validation=False):
    """Read an explicit UTF-8 text/JSONL shard with no generated fallback."""
    config = project["dataset"]
    path = config["validation_path"] if validation else config["path"]
    raw = bounded_file(path)
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeError as exc:
        raise WorkbenchError("Selected dataset is not valid UTF-8 text.") from exc
    samples = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        if config["format"] == "jsonl":
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise WorkbenchError(f"Invalid JSONL at line {line_number}: {exc.msg}") from exc
            if not isinstance(record, dict) or not isinstance(record.get(config["text_field"]), str):
                raise WorkbenchError(f"JSONL line {line_number} needs string field '{config['text_field']}'.")
            line = record[config["text_field"]]
        if line.strip():
            samples.append(line.strip())
        if len(samples) > MAX_RECORDS:
            raise WorkbenchError(f"Dataset exceeds {MAX_RECORDS} records. Prepare an explicit shard.")
    if not samples:
        raise WorkbenchError("Dataset contains no non-empty text records.")
    return samples, {"samples": len(samples), "bytes": len(raw), "preview": [line[:300] for line in samples[:3]], "sha256": hashlib.sha256(raw).hexdigest()}


def tokenizer_load(project):
    """Load only the selected local tokenizer JSON, never model weights."""
    from tokenizers import Tokenizer
    raw = bounded_file(project["tokenizer"]["path"], 32 * 1024 * 1024)
    try:
        tokenizer = Tokenizer.from_str(raw.decode("utf-8"))
    except Exception as exc:
        raise WorkbenchError(f"Unable to parse the selected local tokenizer JSON: {exc}") from exc
    tokenizer.no_truncation()
    tokenizer.no_padding()
    return tokenizer, {"vocab_size": tokenizer.get_vocab_size(), "sha256": hashlib.sha256(raw).hexdigest()}


def parameter_bound(native):
    """Conservative native-module bound, not a measured model parameter count."""
    d, v, layers = native["embed_dim"], native["vocab_size"], native["num_layers"]
    # Includes unused multimodal/diffusion parameters, expert projections and routing.
    return int(4 * d * v + 2_000_000 + 32 * d * d + layers * (
        128 * d * d + 8 * native["num_experts"] * d * native["expert_dim"] + 2048 * d
    ))


def telemetry():
    """Report measured system/process metrics with explicit availability errors."""
    result = {"device": "cpu", "gpu_name": None, "vram_total_gb": None,
              "vram_allocated_gb": None, "cpu_percent": None, "ram_available_gb": None,
              "vram_free_gb": None, "sampled_at": now(), "errors": []}
    try:
        import psutil
        result.update(cpu_percent=psutil.cpu_percent(interval=None), ram_available_gb=round(psutil.virtual_memory().available / 1024**3, 2))
    except (ImportError, OSError) as exc:
        logger.warning("System telemetry unavailable: %s", exc)
        result["errors"].append("System telemetry unavailable.")
    try:
        import torch
        if torch.cuda.is_available():
            result.update(device="cuda", gpu_name=torch.cuda.get_device_name(0),
                          vram_total_gb=round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2),
                          vram_allocated_gb=round(torch.cuda.memory_allocated(0) / 1024**3, 2),
                          vram_free_gb=round(torch.cuda.mem_get_info(0)[0] / 1024**3, 2))
    except (ImportError, RuntimeError) as exc:
        logger.warning("GPU telemetry unavailable: %s", exc)
        result["errors"].append("GPU telemetry unavailable.")
    return result


def preflight(project):
    """Prove explicit artifact identity and bounded adapter inputs without model load."""
    validate_project(project)
    checks = []
    result = {
        "success": True, "ready": False, "checks": checks,
        "dataset": None, "tokenizer": None, "estimate": None,
        "objective": project.get("objective", ARCHITECTURE["objective"]),
        "offering_execution": offering_execution(project.get("offering")),
    }

    def check(key, label, status, detail):
        checks.append({"id": key, "label": label, "status": status, "detail": detail})

    native = project["native_config"]
    if native:
        detail = "Executes the explicit native B3 configuration; selected offering remains a non-certified reference."
        status = "pass"
    else:
        detail = (
            result["offering_execution"]["detail"]
            if result["offering_execution"]
            else "Select an explicit native B3 research configuration."
        )
        status = "blocked"
    check("architecture", "Native architecture", status, detail)
    samples, tokenizer = None, None
    try:
        samples, result["dataset"] = load_dataset(project)
        check("dataset", "Training dataset", "pass", f"{len(samples)} explicit UTF-8 records; no fallback data.")
    except (WorkbenchError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        check("dataset", "Training dataset", "blocked", str(exc))
    try:
        tokenizer, result["tokenizer"] = tokenizer_load(project)
        if native and result["tokenizer"]["vocab_size"] != native["vocab_size"]:
            raise WorkbenchError("Tokenizer vocabulary does not match native vocab_size. No resizing is performed.")
        if native and max(tokenizer.get_vocab().values()) >= native["vocab_size"]:
            raise WorkbenchError("Tokenizer contains token IDs outside the native vocabulary.")
        if samples and not any(len(tokenizer.encode(text).ids) >= 2 for text in samples):
            raise WorkbenchError("No dataset record produces at least two tokens.")
        check("tokenizer", "Local tokenizer", "pass", "Local tokenizer parsed and vocabulary checked.")
    except (WorkbenchError, OSError, ValueError, UnicodeError, ImportError) as exc:
        check("tokenizer", "Local tokenizer", "blocked", str(exc))
    if native:
        bound = parameter_bound(native)
        sequence = project["training"]["sequenceLength"]
        memory_gb = (
            bound * 20 + sequence * native["embed_dim"] * native["num_layers"] * 128
            + 16 * native["num_layers"] * native["num_heads"] * sequence**2
        ) / 1024**3
        result["estimate"] = {"parameters_upper_bound": bound, "training_memory_gb": round(memory_gb, 2), "kind": "conservative bound; not a fit guarantee"}
        hardware = telemetry()
        available = hardware["ram_available_gb"] if project["training"]["device"] == "cpu" else hardware["vram_free_gb"]
        allowed = available is not None and memory_gb < available * 0.75
        check("memory", "Device memory budget", "pass" if allowed else "blocked",
              f"Conservative FP32 Adam budget {memory_gb:.2f} GiB; requested {project['training']['device']}. Measured capacity: {available}. Fit is not guaranteed.")
        check("precision", "Execution precision", "warning", "Research adapter uses FP32 and microbatch 1. Mixed precision and quantization are not asserted.")
    checkpoint_id = project["training"]["checkpoint_run_id"]
    if project["training"]["mode"] == "finetune":
        try:
            source = run_get(project["id"], checkpoint_id)
            if source["state"] not in ("completed", "stopped") or not source.get("checkpoint") or source["configuration"]["native_config"] != native:
                raise WorkbenchError("Choose a completed/stopped workbench checkpoint with exactly matching native configuration.")
            if not result["tokenizer"] or source["tokenizer"]["sha256"] != result["tokenizer"]["sha256"]:
                raise WorkbenchError("Fine-tuning tokenizer hash does not match the checkpoint.")
            check("checkpoint", "Fine-tuning source", "pass", "Same-project native checkpoint and exact tokenizer identity.")
        except WorkbenchError as exc:
            check("checkpoint", "Fine-tuning source", "blocked", str(exc))
    else:
        check("checkpoint", "Training mode", "warning", "Training from random initialization, not loading pretrained weights.")
    from . import builder
    with _ACTIVE_LOCK:
        busy = _ACTIVE is not None
    check("execution", "Shared execution slot", "blocked" if busy or builder._training_state["running"] else "pass",
          "Another resource operation is active." if busy or builder._training_state["running"] else "No active workbench operation or legacy Builder training.")
    fingerprint = hashlib.sha256(json.dumps({"project": project, "dataset": result["dataset"], "tokenizer": result["tokenizer"]}, sort_keys=True).encode()).hexdigest()
    result.update(ready=not any(item["status"] == "blocked" for item in checks), fingerprint=fingerprint)
    return result


@workbench_bp.before_request
def authorize():
    if "user" not in session:
        return jsonify(success=False, error="Please sign in before using the workbench."), 401
    if request.content_length and request.content_length > 256 * 1024:
        raise WorkbenchError("Configuration request exceeds 256 KiB.", 413)


@workbench_bp.errorhandler(WorkbenchError)
def expected_error(exc):
    logger.warning("Workbench request rejected: %s", exc)
    return jsonify(success=False, error=str(exc)), exc.status


@workbench_bp.errorhandler(Exception)
def unexpected_error(exc):
    if isinstance(exc, HTTPException):
        return jsonify(success=False, error=exc.description), exc.code
    logger.exception("Workbench operation failed")
    return jsonify(success=False, error="Workbench operation failed. Check server logs; existing artifacts were not replaced."), 500


def payload():
    value = request.get_json(silent=True)
    if not isinstance(value, dict):
        raise WorkbenchError("Request body must be a JSON object.")
    return value


@workbench_bp.get("/bootstrap")
def bootstrap():
    from . import builder
    return jsonify(success=True, presets=list(get_builder_offering_presets().values()),
                   selected_offering=builder._load_walkthrough_progress().get("selected_offering"),
                   current_model=dict(builder._model_definition), current_training=dict(builder._training_config),
                   capabilities=CAPABILITIES, native_template=NATIVE_TEMPLATE, architecture=ARCHITECTURE,
                   offering_execution=offering_execution_map(),
                   projects=project_list(), telemetry=telemetry(),
                   legacy_training={"running": builder._training_state["running"]},
                   storage={"projects": str(root("projects")), "artifacts": str(root("artifacts"))})


@workbench_bp.get("/telemetry")
def get_telemetry():
    return jsonify(success=True, telemetry=telemetry())


@workbench_bp.get("/projects")
def projects():
    return jsonify(success=True, projects=project_list())


@workbench_bp.post("/projects")
def create_project():
    data = payload()
    presets = get_builder_offering_presets()
    offering = data.get("offering")
    if offering is not None and (not isinstance(offering, str) or offering not in presets):
        raise WorkbenchError("Unknown offering.")
    preset = presets.get(offering) or presets["b1_39m"]
    stamp = now()
    value = {"id": uuid.uuid4().hex, "name": data.get("name"), "revision": 1,
             "created_at": stamp, "updated_at": stamp, "offering": offering,
             "objective": ARCHITECTURE["objective"],
             "model": deepcopy(preset["model"]), "native_config": None,
             "dataset": {"path": "", "format": "text", "text_field": "text", "validation_path": ""},
             "tokenizer": {"path": ""},
             "training": {"mode": "finetune", "checkpoint_run_id": "", "epochs": 1, "batchSize": 1,
                          "learningRate": 2e-5, "gradAccumSteps": 8, "maxSteps": 100,
                          "sequenceLength": 64, "seed": 42, "device": "cpu"}, "notes": ""}
    if offering:
        for key in ("epochs", "batchSize", "learningRate", "gradAccumSteps"):
            value["training"][key] = preset["training"][key]
    if "configuration" in data:
        imported = data["configuration"]
        if not isinstance(imported, dict):
            raise WorkbenchError("Imported configuration must be an object.")
        if "project" in imported:
            if imported.get("schema_version") != 1:
                raise WorkbenchError("Unsupported configuration schema version.")
            imported = imported["project"]
        for key in ("offering", "objective", "model", "native_config", "dataset", "tokenizer", "training", "notes"):
            if key in imported:
                value[key] = deepcopy(imported[key])
    validate_project(value)
    with _STORE_LOCK:
        atomic_json(project_path(value["id"]), value)
    return jsonify(success=True, project=value), 201


@workbench_bp.route("/projects/<project_id>", methods=["GET", "PUT"])
def project_detail(project_id):
    with _STORE_LOCK:
        value = project_get(project_id)
        if request.method == "PUT":
            data = payload()
            if type(data.get("revision")) is not int or data["revision"] != value["revision"]:
                raise WorkbenchError("Project changed elsewhere. Reopen it before saving; your edits were not overwritten.", 409)
            for key in ("name", "offering", "objective", "model", "native_config", "dataset", "tokenizer", "training", "notes"):
                if key in data:
                    value[key] = deepcopy(data[key])
            validate_project(value)
            value.update(revision=value["revision"] + 1, updated_at=now())
            atomic_json(project_path(project_id), value)
    return jsonify(success=True, project=value)


@workbench_bp.get("/projects/<project_id>/export")
def export_project(project_id):
    value = project_get(project_id)
    return send_file(io.BytesIO(json.dumps({"schema_version": 1, "project": value}, indent=2).encode()),
                     mimetype="application/json", as_attachment=True, download_name=f"impressioncore-{project_id}.json")


@workbench_bp.post("/projects/<project_id>/preflight")
def project_preflight(project_id):
    return jsonify(preflight(project_get(project_id)))


@workbench_bp.get("/projects/<project_id>/runs")
def project_runs(project_id):
    project_get(project_id)
    directory = root("artifacts") / identifier(project_id)
    values = [run_get(project_id, path.parent.name) for path in directory.glob("*/run.json")] if directory.exists() else []
    return jsonify(success=True, runs=sorted(values, key=lambda value: value["created_at"], reverse=True))


@workbench_bp.get("/projects/<project_id>/runs/<run_id>")
def run_detail(project_id, run_id):
    project_get(project_id)
    return jsonify(success=True, run=run_get(project_id, run_id))


def reserve(project_id, run_id):
    """Share a resource exclusion flag with legacy training without starting it."""
    global _ACTIVE
    from . import builder
    with builder._training_lock, _ACTIVE_LOCK:
        if _ACTIVE is not None or builder._training_state["running"]:
            raise WorkbenchError("Another training or workbench operation owns the execution slot.", 409)
        _ACTIVE = (project_id, run_id)
        builder._workbench_busy = True
        _STOP.clear()


def release():
    global _ACTIVE
    from . import builder
    with builder._training_lock, _ACTIVE_LOCK:
        _ACTIVE = None
        builder._workbench_busy = False


@workbench_bp.post("/projects/<project_id>/runs")
def start_run(project_id):
    data = payload()
    project = project_get(project_id)
    if data.get("confirmation") is not True:
        raise WorkbenchError("Explicit training confirmation is required.")
    if type(data.get("revision")) is not int or data["revision"] != project["revision"]:
        raise WorkbenchError("Save and validate the latest project before starting.", 409)
    result = preflight(project)
    if not result["ready"]:
        return jsonify(success=False, error="Preflight blocked training.", checks=result["checks"]), 422
    run_id = uuid.uuid4().hex
    stamp = now()
    configuration = deepcopy(project)
    configuration["objective"] = project.get("objective", ARCHITECTURE["objective"])
    native_config = configuration["native_config"]
    configuration_digest = hashlib.sha256(
        json.dumps(native_config, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    value = {"id": run_id, "project_id": project_id, "state": "queued", "step": 0,
             "total_steps": project["training"]["maxSteps"], "loss": None,
             "learning_rate": project["training"]["learningRate"], "logs": ["Training explicitly requested; loading selected native artifacts."],
             "error": None, "checkpoint": False, "created_at": stamp, "updated_at": stamp,
             "configuration": configuration, "dataset": result["dataset"], "tokenizer": result["tokenizer"],
             "fingerprint": result["fingerprint"], "objective": ARCHITECTURE["objective"]}
    value.update(
        objective=configuration["objective"],
        parameter_count=None,
        model_identity={
            "status": "pending_measurement",
            "implementation_id": ARCHITECTURE["id"],
            "native_config": native_config,
            "native_config_sha256": configuration_digest,
            "parameter_count": None,
            "objective": configuration["objective"],
            "tokenizer": result["tokenizer"],
            "offering_reference": offering_execution(project.get("offering")),
        },
        checkpoint_identity=None,
    )
    reserve(project_id, run_id)
    try:
        atomic_json(run_dir(project_id, run_id) / "run.json", value)
        application = current_app._get_current_object()
        from .workbench_runtime import train
        thread = threading.Thread(target=train, args=(application, deepcopy(value)), daemon=True, name=f"workbench-{run_id[:8]}")
        thread.start()
    except Exception:
        release()
        raise
    return jsonify(success=True, run=value), 202


@workbench_bp.post("/projects/<project_id>/runs/<run_id>/stop")
def stop_run(project_id, run_id):
    value = run_get(project_id, run_id)
    if value["state"] not in ("queued", "running", "stopping"):
        raise WorkbenchError("This run is no longer training.", 409)
    with _ACTIVE_LOCK:
        if _ACTIVE != (project_id, run_id):
            raise WorkbenchError("This run is not active.", 409)
        _STOP.set()
    # The worker owns state persistence; do not overwrite a completing worker's run.
    value["state"] = "stopping"
    return jsonify(success=True, run=value)


@workbench_bp.post("/projects/<project_id>/runs/<run_id>/evaluate")
@workbench_bp.post("/projects/<project_id>/runs/<run_id>/generate")
def artifact_operation(project_id, run_id):
    data = payload()
    if data.get("confirmation") is not True:
        raise WorkbenchError("Explicit artifact operation confirmation is required.")
    value = run_get(project_id, run_id)
    if not value.get("checkpoint"):
        raise WorkbenchError("A compatible native checkpoint is required.")
    project = project_get(project_id)
    reserve(project_id, run_id)
    try:
        from .workbench_runtime import evaluate, generate
        if request.path.endswith("/evaluate"):
            result = evaluate(value, project)
            value["metrics"] = result
            from .workbench_runtime import persist_run
            persist_run(value)
        else:
            result = generate(value, data)
        return jsonify(success=True, result=result)
    finally:
        release()


@workbench_bp.get("/projects/<project_id>/runs/<run_id>/export")
def export_run(project_id, run_id):
    value = run_get(project_id, run_id)
    if not value.get("checkpoint"):
        raise WorkbenchError("This run has no completed checkpoint.")
    directory = run_dir(project_id, run_id)
    from .workbench_runtime import digest_file
    if digest_file(directory / "checkpoint.pt") != value.get("checkpoint_sha256"):
        raise WorkbenchError("Checkpoint hash changed; export was refused.")
    if digest_file(directory / "tokenizer.json") != value["tokenizer"]["sha256"]:
        raise WorkbenchError("Checkpoint tokenizer hash changed; export was refused.")
    model_identity = value.get("model_identity")
    checkpoint_identity = value.get("checkpoint_identity")
    if model_identity and model_identity.get("status") == "measured":
        if (
            not checkpoint_identity
            or checkpoint_identity.get("sha256") != value.get("checkpoint_sha256")
            or checkpoint_identity.get("model_identity_sha256") != hashlib.sha256(
                json.dumps(model_identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
        ):
            raise WorkbenchError("Checkpoint identity metadata is incomplete or inconsistent; export was refused.")
    # Spool large bundles to disk rather than holding all weights in RAM.
    import tempfile
    bundle = tempfile.SpooledTemporaryFile(max_size=4 * 1024 * 1024)
    try:
        with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_STORED) as archive:
            for name in ("checkpoint.pt", "tokenizer.json", "run.json"):
                archive.write(directory / name, name)
            if (directory / "evaluation.json").is_file():
                archive.write(directory / "evaluation.json", "evaluation.json")
            artifact_hashes = {
                name: digest_file(directory / name)
                for name in ("checkpoint.pt", "tokenizer.json", "run.json")
            }
            if (directory / "evaluation.json").is_file():
                artifact_hashes["evaluation.json"] = digest_file(directory / "evaluation.json")
            archive.writestr("manifest.json", json.dumps({
                "schema_version": 1,
                "provenance_status": "measured" if model_identity and model_identity.get("status") == "measured" else "legacy_or_unmeasured",
                "model_identity": model_identity,
                "checkpoint_identity": checkpoint_identity,
                "artifacts_sha256": artifact_hashes,
            }, indent=2))
        bundle.seek(0)
        response = send_file(bundle, mimetype="application/zip", as_attachment=True, download_name=f"impressioncore-run-{run_id}.zip")
        response.call_on_close(bundle.close)
        return response
    except Exception:
        bundle.close()
        raise
