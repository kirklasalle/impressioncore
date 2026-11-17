"""Project and execution tests against temporary files and the real native model."""

import hashlib
import io
import json
import threading
import time
import zipfile
from copy import deepcopy
from unittest.mock import patch

import pytest
from flask import Flask
from tokenizers import Tokenizer
from tokenizers.models import WordLevel
from tokenizers.pre_tokenizers import Whitespace

from src.interfaces.web.routes import builder, workbench as wb, workbench_runtime as runtime


@pytest.fixture
def client(tmp_path, monkeypatch):
    app = Flask(__name__)
    app.config.update(
        TESTING=True, SECRET_KEY="isolated-test",
        WORKBENCH_PROJECT_ROOT=tmp_path / "projects",
        WORKBENCH_ARTIFACT_ROOT=tmp_path / "artifacts",
    )
    app.register_blueprint(wb.workbench_bp)
    app.register_blueprint(builder.builder_bp)
    monkeypatch.setattr(builder, "_WALKTHROUGH_FILE", str(tmp_path / "progress.json"))
    monkeypatch.setattr(builder, "_training_state", {"running": False})
    monkeypatch.setattr(builder, "_workbench_busy", False, raising=False)
    monkeypatch.setattr(wb, "_ACTIVE", None)
    monkeypatch.setattr(wb, "_STOP", threading.Event())
    with app.test_client() as value:
        with value.session_transaction() as session:
            session["user"] = "test-operator"
        yield value


def new_project(client, name="Experiment", offering="b3_504m"):
    response = client.post("/api/v1/builder/workbench/projects", json={"name": name, "offering": offering})
    assert response.status_code == 201, response.json
    return response.json["project"]


def url(project, suffix=""):
    return f"/api/v1/builder/workbench/projects/{project['id']}{suffix}"


def configured(client, tmp_path, offering="b3_504m"):
    project = new_project(client, offering=offering)
    tokenizer = Tokenizer(WordLevel(
        vocab={"[UNK]": 0, "alpha": 1, "beta": 2, "gamma": 3, "delta": 4,
               "one": 5, "two": 6, "three": 7, "four": 8, "five": 9,
               "six": 10, "seven": 11, "eight": 12, "nine": 13, "ten": 14, "end": 15},
        unk_token="[UNK]",
    ))
    tokenizer.pre_tokenizer = Whitespace()
    tokenizer.save(str(tmp_path / "tokenizer.json"))
    (tmp_path / "train.txt").write_text("alpha beta gamma delta\none two three four\n", encoding="utf-8")
    (tmp_path / "valid.txt").write_text("alpha gamma beta\nfive six seven\n", encoding="utf-8")
    native = deepcopy(wb.NATIVE_TEMPLATE)
    native.update(embed_dim=16, num_heads=2, num_layers=1, vocab_size=16,
                  num_experts=2, expert_dim=16, experts_per_token=1,
                  image_embed_dim=16, audio_embed_dim=16, max_seq_length=16,
                  use_mhc=False, use_gradient_checkpointing=False, dropout=0.0)
    project["native_config"] = native
    project["dataset"].update(path=str(tmp_path / "train.txt"), validation_path=str(tmp_path / "valid.txt"))
    project["tokenizer"]["path"] = str(tmp_path / "tokenizer.json")
    project["training"].update(mode="scratch", maxSteps=2, epochs=2, sequenceLength=8, gradAccumSteps=2)
    response = client.put(url(project), json=project)
    assert response.status_code == 200
    return response.json["project"]


def wait_run(client, project, run):
    for _ in range(300):
        response = client.get(url(project, f"/runs/{run['id']}"))
        assert response.status_code == 200, response.json
        value = response.json["run"]
        if value["state"] in ("failed", "stopped", "completed") and wb._ACTIVE is None:
            return value
        time.sleep(0.05)
    pytest.fail("Native test run did not finish")


def test_authentication_required(client):
    with client.session_transaction() as session:
        session.clear()
    assert client.get("/api/v1/builder/workbench/bootstrap").status_code == 401
    assert client.post("/api/v1/builder/workbench/projects", json={"name": "x"}).status_code == 401


def test_bootstrap_read_only_no_model_load(client):
    with patch.object(builder, "get_model_tokenizer", side_effect=AssertionError("Must not load weights")):
        response = client.get("/api/v1/builder/workbench/bootstrap")
    assert response.status_code == 200
    assert response.json["architecture"]["objective"] == "prefix_next_token"
    assert response.json["projects"] == []
    assert response.json["telemetry"]["sampled_at"]
    assert not client.application.config["WORKBENCH_PROJECT_ROOT"].exists()


def test_offerings_are_reference_metadata_not_certified_native_models(client):
    bootstrap = client.get("/api/v1/builder/workbench/bootstrap").json
    offerings = bootstrap["offering_execution"]
    assert offerings["b1_39m"]["status"] == "unavailable"
    assert offerings["b2_50m"]["status"] == "unavailable"
    assert offerings["b1_39m"]["certified"] is False
    assert offerings["b3_504m"]["status"] == "reference_only"
    assert offerings["b3_504m"]["certified"] is False

    b1 = client.post("/api/v1/builder/workbench/projects", json={
        "name": "B1 reference only", "offering": "b1_39m",
    }).json["project"]
    result = client.post(url(b1, "/preflight")).json
    architecture = next(item for item in result["checks"] if item["id"] == "architecture")
    assert architecture["status"] == "blocked"
    assert "No native B1 implementation" in architecture["detail"]


def test_explicit_native_b3_config_does_not_certify_b1_reference(client, tmp_path):
    project = configured(client, tmp_path, offering="b1_39m")
    result = client.post(url(project, "/preflight")).json
    assert result["ready"] is True
    assert result["offering_execution"]["status"] == "unavailable"
    assert result["offering_execution"]["certified"] is False
    assert project["model"]["preset"] == "b1_39m"
    assert project["native_config"]["embed_dim"] == 16


@pytest.mark.parametrize("offering", list(wb.get_builder_offering_presets()))
def test_offering_starter_preserves_reference_and_safe_execution_defaults(client, offering):
    preset = wb.get_builder_offering_presets()[offering]
    response = client.post("/api/v1/builder/workbench/projects", json={
        "name": f"{preset['name']} experiment", "offering": offering,
    })
    assert response.status_code == 201
    project = response.json["project"]
    assert project["offering"] == offering and project["model"] == preset["model"]
    for key in ("epochs", "batchSize", "learningRate", "gradAccumSteps"):
        assert project["training"][key] == preset["training"][key]
    assert project["native_config"] is None
    assert project["objective"] == "prefix_next_token"
    assert project["training"]["maxSteps"] == 100
    assert project["training"]["mode"] == "finetune" and project["training"]["device"] == "cpu"
    assert project["dataset"]["path"] == "" and project["tokenizer"]["path"] == ""
    assert client.get(url(project, "/runs")).json["runs"] == []


def test_project_round_trip_conflict_and_export(client):
    project = new_project(client)
    assert project["native_config"] is None
    project["notes"] = "A reproducible study"
    response = client.put(url(project), json=project)
    assert response.status_code == 200
    assert response.json["project"]["revision"] == 2
    assert client.put(url(project), json=project).status_code == 409
    assert client.get(url(project)).json["project"]["notes"] == project["notes"]
    exported = client.get(url(project, "/export"))
    assert exported.status_code == 200
    package = json.loads(exported.data)
    imported = client.post("/api/v1/builder/workbench/projects", json={"name": "Imported", "configuration": package})
    assert imported.status_code == 201
    assert imported.json["project"]["id"] != project["id"]
    assert imported.json["project"]["notes"] == project["notes"]


@pytest.mark.parametrize("changes", [
    {"name": ""}, {"dataset": []}, {"native_config": {}},
    {"training": {"batchSize": 0}}, {"notes": []},
])
def test_bad_projects_rejected_without_overwrite(client, changes):
    project = new_project(client)
    project.update(changes)
    assert client.put(url(project), json=project).status_code == 400
    assert client.get(url(project)).json["project"]["revision"] == 1


def test_unsupported_objective_is_rejected_without_overwrite(client):
    project = new_project(client)
    project["objective"] = "all_position_causal_lm"
    response = client.put(url(project), json=project)
    assert response.status_code == 400
    assert "prefix_next_token" in response.json["error"]
    assert client.get(url(project)).json["project"]["revision"] == 1


def test_invalid_identifier_and_missing_project(client):
    assert client.get("/api/v1/builder/workbench/projects/not-an-id").status_code == 400
    assert client.get("/api/v1/builder/workbench/projects/" + "a" * 32).status_code == 404


def test_preflight_has_real_blockers_not_fallbacks(client):
    project = new_project(client)
    result = client.post(url(project, "/preflight")).json
    assert result["success"] is True
    assert result["ready"] is False
    assert {"architecture", "dataset", "tokenizer", "checkpoint"} <= {
        item["id"] for item in result["checks"] if item["status"] == "blocked"
    }
    response = client.post(url(project, "/runs"), json={"revision": 1, "confirmation": True})
    assert response.status_code == 422
    assert client.get(url(project, "/runs")).json["runs"] == []


def test_preflight_local_inputs_and_no_global_config_mutation(client, tmp_path):
    before_model = deepcopy(builder._model_definition)
    before_training = deepcopy(builder._training_config)
    project = configured(client, tmp_path)
    result = client.post(url(project, "/preflight"))
    assert result.status_code == 200
    assert result.json["ready"] is True
    assert result.json["tokenizer"]["vocab_size"] == 16
    assert result.json["dataset"]["samples"] == 2
    assert builder._model_definition == before_model
    assert builder._training_config == before_training


def test_wrong_tokenizer_vocabulary_blocks(client, tmp_path):
    project = configured(client, tmp_path)
    project["native_config"]["vocab_size"] = 17
    project = client.put(url(project), json=project).json["project"]
    result = client.post(url(project, "/preflight")).json
    assert result["ready"] is False
    assert any("vocabulary" in check["detail"] for check in result["checks"])


def test_start_requires_confirmation_and_current_revision(client, tmp_path):
    project = configured(client, tmp_path)
    assert client.post(url(project, "/runs"), json={"revision": project["revision"]}).status_code == 400
    assert client.post(url(project, "/runs"), json={"revision": 1, "confirmation": True}).status_code == 409


def test_dataset_read_is_bounded_and_jsonl_errors_explicit(client, tmp_path, monkeypatch):
    project = configured(client, tmp_path)
    monkeypatch.setattr(wb, "MAX_RECORDS", 1)
    response = client.post(url(project, "/preflight"))
    assert not response.json["ready"]
    assert any("exceeds" in check["detail"] for check in response.json["checks"])


def test_native_training_finetune_evaluation_inference_and_export(client, tmp_path):
    import torch
    old_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        project = configured(client, tmp_path)
        response = client.post(url(project, "/runs"), json={"revision": project["revision"], "confirmation": True})
        assert response.status_code == 202, response.json
        run = wait_run(client, project, response.json["run"])
        assert run["state"] == "completed", run.get("error")
        assert run["step"] == 2 and run["total_steps"] == 2
        assert math_is_finite(run["loss"])
        assert run["parameter_count"] > 0
        assert run["checkpoint"] is True
        assert run["checkpoint_sha256"]
        identity = run["model_identity"]
        assert identity["status"] == "measured"
        assert identity["implementation"]["id"] == "impressioncore_b3"
        assert identity["implementation"]["source_sha256"]
        assert identity["native_config"] == project["native_config"]
        assert identity["parameter_count"] == run["parameter_count"]
        assert identity["tokenizer"]["sha256"] == run["tokenizer"]["sha256"]
        assert identity["objective"] == "prefix_next_token"
        assert identity["offering_reference"]["certified"] is False
        assert run["checkpoint_identity"]["sha256"] == run["checkpoint_sha256"]
        base = f"/runs/{run['id']}"
        assert client.post(url(project, base + "/stop"), json={}).status_code == 409
        evaluation = client.post(url(project, base + "/evaluate"), json={"confirmation": True})
        assert evaluation.status_code == 200, evaluation.json
        assert evaluation.json["result"]["samples"] == 2
        assert evaluation.json["result"]["perplexity"] > 0
        generation = client.post(url(project, base + "/generate"), json={"confirmation": True, "prompt": "alpha beta", "max_new_tokens": 2})
        assert generation.status_code == 200, generation.json
        assert generation.json["result"]["generated_tokens"] == 2
        exported = client.get(url(project, base + "/export"))
        assert exported.status_code == 200
        with zipfile.ZipFile(io.BytesIO(exported.data)) as archive:
            assert {"checkpoint.pt", "tokenizer.json", "run.json", "evaluation.json", "manifest.json"} <= set(archive.namelist())
            assert json.loads(archive.read("run.json"))["metrics"]["samples"] == 2
            manifest = json.loads(archive.read("manifest.json"))
            assert manifest["provenance_status"] == "measured"
            assert manifest["model_identity"] == identity
            assert manifest["artifacts_sha256"]["checkpoint.pt"] == hashlib.sha256(
                archive.read("checkpoint.pt")
            ).hexdigest()
            assert manifest["artifacts_sha256"]["tokenizer.json"] == hashlib.sha256(
                archive.read("tokenizer.json")
            ).hexdigest()
        project["training"].update(mode="finetune", checkpoint_run_id=run["id"], maxSteps=1)
        project = client.put(url(project), json=project).json["project"]
        assert client.post(url(project, "/preflight")).json["ready"] is True
        response = client.post(url(project, "/runs"), json={"revision": project["revision"], "confirmation": True})
        fine = wait_run(client, project, response.json["run"])
        assert fine["state"] == "completed", fine.get("error")
        assert fine["step"] == 1
        # A modified local checkpoint must never silently load with strict=False.
        with client.application.app_context():
            path = wb.run_dir(project["id"], run["id"]) / "checkpoint.pt"
        path.write_bytes(b"corrupt")
        assert client.post(url(project, base + "/generate"), json={"confirmation": True, "prompt": "alpha"}).status_code == 400
        assert client.get(url(project, base + "/export")).status_code == 400
    finally:
        torch.set_num_threads(old_threads)


def math_is_finite(value):
    import math
    return value is not None and math.isfinite(value)


def test_prefix_next_token_examples_exclude_target_and_later_tokens():
    tokenizer = Tokenizer(WordLevel(
        vocab={"[UNK]": 0, "alpha": 1, "beta": 2, "gamma": 3, "delta": 4,
               "five": 5, "different": 6, "suffix": 7},
        unk_token="[UNK]",
    ))
    tokenizer.pre_tokenizer = Whitespace()
    original = runtime.examples(tokenizer, ["alpha beta gamma delta five"], 3)
    perturbed_future = runtime.examples(tokenizer, ["alpha beta gamma delta different suffix"], 3)

    assert original == perturbed_future == [([1, 2, 3], 4)]
    prefix, target = original[0]
    assert target not in prefix
    assert tokenizer.decode(prefix) == "alpha beta gamma"
    assert tokenizer.decode([target]) == "delta"


def test_real_accumulation_matches_mean_gradient():
    import torch
    from torch import nn

    class Tiny(nn.Module):
        def __init__(self):
            super().__init__()
            self.weight = nn.Parameter(torch.tensor([[0.2, -0.1], [0.4, 0.3]]))

        def forward(self, input_ids):
            return {"logits": self.weight[input_ids], "expert_loss": self.weight.sum() * 0}

    model = Tiny()
    expected = deepcopy(model)
    optimizer = torch.optim.AdamW(expected.parameters(), lr=0.001)
    rows = [([0], 1), ([1], 0)]
    loss = sum(torch.nn.functional.cross_entropy(expected(input_ids=torch.tensor([prefix]))["logits"][:, -1, :], torch.tensor([target])) for prefix, target in rows) / 2
    loss.backward()
    torch.nn.utils.clip_grad_norm_(expected.parameters(), 1.0)
    optimizer.step()
    steps = []
    runtime.training_batches(model, rows, {
        "learningRate": 0.001, "seed": 42, "epochs": 1, "maxSteps": 1, "gradAccumSteps": 2,
    }, threading.Event(), lambda *values: steps.append(values))
    assert len(steps) == 1
    assert torch.allclose(model.weight, expected.weight)


def test_legacy_training_cannot_start_during_workbench_operation(client, monkeypatch):
    monkeypatch.setattr(builder, "_workbench_busy", True)
    assert client.post("/api/v1/builder/training/start", json={}).status_code == 409


def test_interrupted_job_is_not_reported_as_running(client):
    project = new_project(client)
    with client.application.app_context():
        run_id = "b" * 32
        wb.atomic_json(wb.run_dir(project["id"], run_id) / "run.json", {
            "id": run_id, "project_id": project["id"], "state": "running",
            "created_at": wb.now(), "checkpoint": False,
        })
    result = client.get(url(project, f"/runs/{run_id}")).json["run"]
    assert result["state"] == "interrupted"
    assert "restarted" in result["error"]


def test_invalid_tokenizer_is_a_preflight_blocker(client, tmp_path):
    project = configured(client, tmp_path)
    (tmp_path / "tokenizer.json").write_text("{}", encoding="utf-8")
    response = client.post(url(project, "/preflight"))
    assert response.status_code == 200
    assert not response.json["ready"]
    assert any("Unable to parse" in check["detail"] for check in response.json["checks"])


def test_heldout_overlap_is_rejected(client, tmp_path, monkeypatch):
    project = configured(client, tmp_path)
    run = {"configuration": project, "dataset": {"sha256": ""}}
    with client.application.app_context():
        _, dataset = wb.load_dataset(project)
        run["dataset"] = dataset
        project["dataset"]["validation_path"] = project["dataset"]["path"]
        with pytest.raises(wb.WorkbenchError, match="overlaps"):
            runtime.evaluate(run, project)


def test_atomic_project_save_failure_keeps_revision(client):
    project = new_project(client)
    with patch.object(wb.os, "replace", side_effect=OSError("disk full")):
        response = client.put(url(project), json=project)
    assert response.status_code == 500
    assert client.get(url(project)).json["project"]["revision"] == 1


def test_cooperative_stop_does_not_apply_partial_accumulation():
    import torch
    from torch import nn
    stop = threading.Event()

    class StoppingModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.weight = nn.Parameter(torch.tensor([0.1, 0.2]))

        def forward(self, input_ids):
            stop.set()
            return {"logits": self.weight.view(1, 1, 2), "expert_loss": self.weight.sum() * 0}

    model = StoppingModel()
    before = model.weight.detach().clone()
    updates = []
    steps, _ = runtime.training_batches(model, [([0], 1), ([0], 1)], {
        "seed": 42, "learningRate": 0.001, "epochs": 1, "maxSteps": 1, "gradAccumSteps": 2,
    }, stop, lambda *args: updates.append(args))
    assert steps == 0
    assert updates == []
    assert torch.equal(before, model.weight)


def test_native_worker_stops_at_boundary_and_publishes_checkpoint(client, tmp_path, monkeypatch):
    import torch
    old_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    step_reached = threading.Event()
    continue_training = threading.Event()
    original = runtime.training_batches

    def held_training(model, rows, settings, stop, update):
        def held_update(*args):
            update(*args)
            step_reached.set()
            assert continue_training.wait(10)
        return original(model, rows, settings, stop, held_update)

    monkeypatch.setattr(runtime, "training_batches", held_training)
    try:
        project = configured(client, tmp_path)
        response = client.post(url(project, "/runs"), json={"revision": project["revision"], "confirmation": True})
        run = response.json["run"]
        assert step_reached.wait(10)
        endpoint = url(project, f"/runs/{run['id']}")
        assert client.post(endpoint + "/stop", json={}).json["run"]["state"] == "stopping"
        assert client.get(endpoint).json["run"]["state"] == "stopping"
        continue_training.set()
        stopped = wait_run(client, project, run)
        assert stopped["state"] == "stopped" and stopped["step"] == 1
        assert stopped["checkpoint"] and stopped["checkpoint_sha256"]
        assert client.get(endpoint + "/export").status_code == 200
    finally:
        continue_training.set()
        torch.set_num_threads(old_threads)


def test_execution_slot_excludes_legacy_and_other_projects(client):
    project = new_project(client)
    wb.reserve(project["id"], "c" * 32)
    try:
        with pytest.raises(wb.WorkbenchError, match="owns"):
            wb.reserve(project["id"], "d" * 32)
        assert client.post("/api/v1/builder/training/start", json={}).status_code == 409
    finally:
        wb.release()


def test_concurrent_json_reads_and_atomic_replacement(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    path = tmp_path / "run.json"
    wb.atomic_json(path, {"step": 0})

    def write():
        for step in range(100):
            wb.atomic_json(path, {"step": step})

    def read():
        for _ in range(100):
            assert type(wb.read_json(path)["step"]) is int

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(write), executor.submit(read), executor.submit(read)]
        for future in futures:
            future.result()
    assert wb.read_json(path)["step"] == 99


@pytest.mark.parametrize("device", ["cpu", "cuda"])
def test_insufficient_or_unavailable_memory_blocks_execution(client, tmp_path, monkeypatch, device):
    project = configured(client, tmp_path)
    project["training"]["device"] = device
    project = client.put(url(project), json=project).json["project"]
    monkeypatch.setattr(wb, "telemetry", lambda: {
        "ram_available_gb": 0.001, "vram_free_gb": None,
    })
    response = client.post(url(project, "/preflight"))
    assert response.status_code == 200 and not response.json["ready"]
    assert next(item for item in response.json["checks"] if item["id"] == "memory")["status"] == "blocked"
    with patch.object(runtime, "construct", side_effect=AssertionError("Must not allocate a model")):
        response = client.post(url(project, "/runs"), json={"revision": project["revision"], "confirmation": True})
    assert response.status_code == 422


@pytest.mark.parametrize("content,format,detail", [
    (b"\xff\xfe", "text", "UTF-8"),
    (b'{"text":bad}\n', "jsonl", "line 1"),
    (b'{"not_text":5}\n', "jsonl", "string field"),
])
def test_invalid_dataset_has_actionable_preflight_error(client, tmp_path, content, format, detail):
    project = configured(client, tmp_path)
    (tmp_path / "train.txt").write_bytes(content)
    project["dataset"]["format"] = format
    project = client.put(url(project), json=project).json["project"]
    response = client.post(url(project, "/preflight"))
    check = next(item for item in response.json["checks"] if item["id"] == "dataset")
    assert check["status"] == "blocked" and detail in check["detail"]


def test_actual_flask_factory_registers_workspace_without_pipeline_start(tmp_path, monkeypatch):
    import logging
    from src.core.config import data_paths
    from src.interfaces.web import server
    monkeypatch.setattr(server, "PIPELINE_AVAILABLE", False)
    monkeypatch.setattr(server, "project_root", str(tmp_path))
    monkeypatch.setattr(server, "get_rich_logger", lambda *args, **kwargs: logging.getLogger("test-factory"))
    monkeypatch.setattr(data_paths, "enforce_data_drive", lambda: None)
    app = server.create_app()
    app.config.update(TESTING=True, WORKBENCH_PROJECT_ROOT=tmp_path / "projects",
                      WORKBENCH_ARTIFACT_ROOT=tmp_path / "artifacts")
    with app.test_client() as value:
        assert value.get("/api/v1/builder/workbench/bootstrap").status_code == 401
        with value.session_transaction() as session:
            session["user"] = "test-operator"
        assert value.get("/api/v1/builder/workbench/bootstrap").status_code == 200
        response = value.get("/unified_builder")
        assert response.status_code == 200
        assert b"js/workbench.js" in response.data
        assert b"css/unified_builder.css" in response.data
