"""Explicit native B3 text experiments; never substitute a generic remote model."""

import gc
import hashlib
import math
import os
import random
from copy import deepcopy
from pathlib import Path

from . import workbench as workspace


def digest_file(path):
    """Hash a local artifact in bounded chunks."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(value):
    """Hash a JSON-compatible identity using a stable representation."""
    return hashlib.sha256(
        workspace.json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def implementation_identity():
    """Identify the exact native B3 implementation source used for execution."""
    from src.core.models import impressioncore_b3_architecture
    source = Path(impressioncore_b3_architecture.__file__).resolve()
    return {
        "id": workspace.ARCHITECTURE["id"],
        "source": workspace.ARCHITECTURE["source"],
        "source_sha256": digest_file(source),
    }


def measured_model_identity(config, parameter_count, tokenizer_info, offering):
    """Bind measured native model facts to the explicit run configuration."""
    return {
        "status": "measured",
        "implementation": implementation_identity(),
        "native_config": deepcopy(config),
        "native_config_sha256": canonical_digest(config),
        "parameter_count": parameter_count,
        "objective": workspace.ARCHITECTURE["objective"],
        "tokenizer": {
            "vocab_size": tokenizer_info["vocab_size"],
            "sha256": tokenizer_info["sha256"],
        },
        "offering_reference": workspace.offering_execution(offering),
    }


def construct(config):
    """Construct the native architecture, preserving every explicit dimension."""
    from src.core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model
    return ImpressionCoreB3Model(B3Config(**config))


def checkpoint_load(run):
    """Load a verified internal checkpoint with strict shape and tokenizer identity."""
    import torch
    from tokenizers import Tokenizer
    directory = workspace.run_dir(run["project_id"], run["id"])
    if digest_file(directory / "checkpoint.pt") != run.get("checkpoint_sha256"):
        raise workspace.WorkbenchError("Checkpoint hash changed; loading was refused.")
    raw = workspace.bounded_file(str(directory / "tokenizer.json"), 32 * 1024 * 1024)
    if hashlib.sha256(raw).hexdigest() != run["tokenizer"]["sha256"]:
        raise workspace.WorkbenchError("Checkpoint tokenizer hash changed; loading was refused.")
    checkpoint = torch.load(directory / "checkpoint.pt", map_location="cpu", weights_only=True)
    config = run["configuration"]["native_config"]
    objective = run.get("objective", run["configuration"].get("objective", workspace.ARCHITECTURE["objective"]))
    if objective != workspace.ARCHITECTURE["objective"] or checkpoint.get("objective") != objective:
        raise workspace.WorkbenchError("Checkpoint objective metadata is unsupported or mismatched.")
    if checkpoint.get("schema_version") not in (1, 2) or checkpoint.get("native_config") != config:
        raise workspace.WorkbenchError("Checkpoint architecture metadata does not match the run.")
    model = construct(config)
    parameter_count = sum(parameter.numel() for parameter in model.parameters())
    if run.get("parameter_count") is not None and run["parameter_count"] != parameter_count:
        raise workspace.WorkbenchError("Measured parameter count does not match the checkpoint architecture.")
    if checkpoint["schema_version"] == 2:
        identity = run.get("model_identity")
        checkpoint_identity = run.get("checkpoint_identity")
        if not isinstance(identity, dict) or identity.get("status") != "measured":
            raise workspace.WorkbenchError("Measured native model identity is missing.")
        expected_identity = measured_model_identity(
            config, parameter_count, run["tokenizer"], run["configuration"].get("offering")
        )
        if identity != expected_identity or checkpoint.get("model_identity") != identity:
            raise workspace.WorkbenchError("Checkpoint implementation, configuration, count, or tokenizer identity does not match.")
        if (
            not isinstance(checkpoint_identity, dict)
            or checkpoint_identity.get("schema_version") != 2
            or checkpoint_identity.get("sha256") != run.get("checkpoint_sha256")
            or checkpoint_identity.get("model_identity_sha256") != canonical_digest(identity)
        ):
            raise workspace.WorkbenchError("Checkpoint provenance metadata does not match the run.")
    elif checkpoint.get("native_config") != config:
        raise workspace.WorkbenchError("Legacy checkpoint configuration does not match the run.")
    model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    tokenizer = Tokenizer.from_str(raw.decode("utf-8"))
    tokenizer.no_truncation()
    tokenizer.no_padding()
    return model, tokenizer


def examples(tokenizer, samples, length):
    """Hold out exactly each record's final included token as its next-token target."""
    result = []
    for text in samples:
        ids = tokenizer.encode(text).ids[:length + 1]
        if len(ids) >= 2:
            result.append((ids[:-1], ids[-1]))
    if not result:
        raise workspace.WorkbenchError("No record produces a usable prefix and target.")
    return result


def persist_run(run):
    run["updated_at"] = workspace.now()
    run["logs"] = run["logs"][-300:]
    workspace.atomic_json(workspace.run_dir(run["project_id"], run["id"]) / "run.json", run)


def training_batches(model, rows, settings, stop, update):
    """Optimize true accumulated microbatches; optimizer-step counts are authoritative."""
    import torch
    from torch.optim import AdamW
    device = next(model.parameters()).device
    optimizer = AdamW(model.parameters(), lr=settings["learningRate"])
    generator = random.Random(settings["seed"])
    total = min(settings["maxSteps"], settings["epochs"] * math.ceil(len(rows) / settings["gradAccumSteps"]))
    step = 0
    model.train()
    for epoch in range(settings["epochs"]):
        order = list(range(len(rows)))
        generator.shuffle(order)
        for offset in range(0, len(order), settings["gradAccumSteps"]):
            if stop.is_set() or step >= total:
                return step, total
            group = order[offset:offset + settings["gradAccumSteps"]]
            optimizer.zero_grad(set_to_none=True)
            loss_sum = 0.0
            for index in group:
                if stop.is_set():
                    # Do not publish a partial optimizer step or partial gradient checkpoint.
                    optimizer.zero_grad(set_to_none=True)
                    return step, total
                prefix, target = rows[index]
                tokens = torch.tensor([prefix], dtype=torch.long, device=device)
                output = model(input_ids=tokens)
                prediction_loss = torch.nn.functional.cross_entropy(
                    output["logits"][:, -1, :].float(),
                    torch.tensor([target], dtype=torch.long, device=device),
                )
                objective = prediction_loss + output["expert_loss"]
                if not torch.isfinite(objective):
                    raise workspace.WorkbenchError("Non-finite training loss; experiment stopped without reporting success.")
                (objective / len(group)).backward()
                loss_sum += prediction_loss.detach().item()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
            optimizer.step()
            step += 1
            update(step, total, loss_sum / len(group), epoch + 1)
            if step >= total:
                return step, total
    return step, total


def train(application, run):
    """Execute one project snapshot and persist status, provenance, and a native checkpoint."""
    import torch
    model = None
    with application.app_context():
        try:
            project = run["configuration"]
            if run.get("objective") != workspace.ARCHITECTURE["objective"]:
                raise workspace.WorkbenchError("Unsupported native training objective; no model was constructed.")
            samples, dataset = workspace.load_dataset(project)
            tokenizer, tokenizer_info = workspace.tokenizer_load(project)
            if dataset["sha256"] != run["dataset"]["sha256"] or tokenizer_info != run["tokenizer"]:
                raise workspace.WorkbenchError("Dataset or tokenizer changed after preflight. Run validation again.")
            settings = project["training"]
            with torch.random.fork_rng(devices=[]):
                torch.manual_seed(settings["seed"])
                if settings["mode"] == "finetune":
                    source = workspace.run_get(project["id"], settings["checkpoint_run_id"])
                    model, tokenizer = checkpoint_load(source)
                else:
                    model = construct(project["native_config"])
                count = sum(parameter.numel() for parameter in model.parameters())
                run["parameter_count"] = count
                run["model_identity"] = measured_model_identity(
                    project["native_config"], count, tokenizer_info, project.get("offering")
                )
                model.to(torch.device(settings["device"]))
                rows = examples(tokenizer, samples, settings["sequenceLength"])
                run.update(state="running", total_steps=min(settings["maxSteps"], settings["epochs"] * math.ceil(len(rows) / settings["gradAccumSteps"])))
                run["logs"].append(f"Native ImpressionCore B3: {count:,} parameters; {len(rows)} prefix/target examples; FP32; {settings['device']}.")
                persist_run(run)

                def update(step, total, loss, epoch):
                    run.update(step=step, total_steps=total, loss=loss, epoch=epoch)
                    run["logs"].append(f"Optimizer step {step}/{total}: next-token cross-entropy={loss:.6f}")
                    if workspace._STOP.is_set():
                        run["state"] = "stopping"
                    persist_run(run)

                training_batches(model, rows, settings, workspace._STOP, update)
            directory = workspace.run_dir(project["id"], run["id"])
            # Preserve the exact parsed tokenizer used by this run.
            # Input hash records the original file; serialize the original bytes only if unchanged.
            original = workspace.bounded_file(project["tokenizer"]["path"], 32 * 1024 * 1024)
            if hashlib.sha256(original).hexdigest() != tokenizer_info["sha256"]:
                raise workspace.WorkbenchError("Tokenizer changed during training; checkpoint was not published.")
            (directory / "tokenizer.json").write_bytes(original)
            temporary = directory / "checkpoint.pt.tmp"
            try:
                torch.save({
                    "schema_version": 2, "native_config": deepcopy(project["native_config"]),
                    "model_state_dict": {key: value.detach().cpu() for key, value in model.state_dict().items()},
                    "optimizer_steps": run["step"], "objective": run["objective"],
                    "model_identity": deepcopy(run["model_identity"]),
                }, temporary)
                os.replace(temporary, directory / "checkpoint.pt")
            finally:
                if temporary.exists():
                    temporary.unlink()
            if workspace._STOP.is_set():
                # The native stop event is only observed at microbatch/optimizer boundaries.
                run["logs"].append("Stop acknowledged at a safe boundary; no partial gradient step was applied.")
            checkpoint_sha256 = digest_file(directory / "checkpoint.pt")
            run.update(
                checkpoint=True,
                checkpoint_sha256=checkpoint_sha256,
                checkpoint_identity={
                    "schema_version": 2,
                    "sha256": checkpoint_sha256,
                    "model_identity_sha256": canonical_digest(run["model_identity"]),
                },
                state="stopped" if workspace._STOP.is_set() else "completed",
            )
            run["logs"].append("Native weights and exact tokenizer saved. Fine-tuning is supported; exact optimizer resume is not.")
            persist_run(run)
        except Exception as exc:
            workspace.logger.exception("Native workbench training failed")
            run.update(state="failed", error=str(exc))
            run["logs"].append(f"Training failed: {exc}")
            try:
                persist_run(run)
            except OSError:
                workspace.logger.exception("Unable to persist failed run status")
        finally:
            del model
            gc.collect()
            workspace.release()


def evaluation_metrics(model, tokenizer, samples, sequence_length):
    """Compute real held-out prediction loss without expert regularization."""
    import torch
    rows = examples(tokenizer, samples, sequence_length)
    total_loss = 0.0
    model.eval()
    with torch.no_grad():
        for prefix, target in rows:
            output = model(input_ids=torch.tensor([prefix], dtype=torch.long))
            loss = torch.nn.functional.cross_entropy(output["logits"][:, -1, :].float(), torch.tensor([target]))
            if not torch.isfinite(loss):
                raise workspace.WorkbenchError("Non-finite evaluation result; no score was reported.")
            total_loss += loss.item()
    average = total_loss / len(rows)
    return {"loss": average, "perplexity": math.exp(average) if average < 700 else None, "samples": len(rows)}


def evaluate(run, project):
    """Evaluate the exact run checkpoint on explicit, disjoint held-out records."""
    samples, dataset = workspace.load_dataset(project, validation=True)
    training_samples, training_dataset = workspace.load_dataset(run["configuration"])
    if training_dataset["sha256"] != run["dataset"]["sha256"]:
        raise workspace.WorkbenchError("Original training dataset changed; held-out provenance cannot be verified.")
    if dataset["sha256"] == run["dataset"]["sha256"] or set(samples) & set(training_samples):
        raise workspace.WorkbenchError("Held-out data overlaps training data. Select a separate validation shard.")
    model, tokenizer = checkpoint_load(run)
    try:
        result = evaluation_metrics(model, tokenizer, samples, run["configuration"]["training"]["sequenceLength"])
        result.update(dataset_sha256=dataset["sha256"], run_id=run["id"], objective=run["objective"],
                      measured_at=workspace.now(), device="cpu")
        workspace.atomic_json(workspace.run_dir(run["project_id"], run["id"]) / "evaluation.json", result)
        return result
    finally:
        del model
        gc.collect()


def generate(run, data):
    """Generate bounded text from one exact native checkpoint, without downloads."""
    import torch
    prompt = data.get("prompt")
    maximum = data.get("max_new_tokens", 32)
    temperature = data.get("temperature", 0.7)
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 4000:
        raise workspace.WorkbenchError("Prompt must contain 1-4000 characters.")
    if type(maximum) is not int or not 1 <= maximum <= 128:
        raise workspace.WorkbenchError("Generate 1-128 new tokens.")
    if type(temperature) not in (int, float) or not math.isfinite(temperature) or not 0.05 <= temperature <= 2:
        raise workspace.WorkbenchError("Temperature must be finite and between 0.05 and 2.")
    model, tokenizer = checkpoint_load(run)
    try:
        ids = tokenizer.encode(prompt).ids
        if not ids:
            raise workspace.WorkbenchError("Prompt produced no tokens.")
        context = run["configuration"]["training"]["sequenceLength"]
        model.eval()
        with torch.no_grad():
            for _ in range(maximum):
                output = model(input_ids=torch.tensor([ids[-context:]], dtype=torch.long))
                probabilities = torch.softmax(output["logits"][:, -1, :].float() / temperature, dim=-1)
                if not torch.isfinite(probabilities).all():
                    raise workspace.WorkbenchError("Non-finite generation probabilities; generation was stopped.")
                ids.append(torch.multinomial(probabilities, 1).item())
        return {"text": tokenizer.decode(ids), "run_id": run["id"], "generated_tokens": maximum, "device": "cpu"}
    finally:
        del model
        gc.collect()
