"""Regression tests for the academy offering handoff, isolated from user state."""

import json
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from threading import Barrier
from unittest.mock import patch

import pytest
from flask import Flask

from src.interfaces.web.routes import builder


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Provide Builder APIs with temporary progress and configuration storage."""
    monkeypatch.setattr(builder, "_WALKTHROUGH_FILE", str(tmp_path / "progress.json"))
    monkeypatch.setattr(builder, "_MODEL_CONFIG_FILE", str(tmp_path / "model.json"))
    monkeypatch.setattr(builder, "_TRAINING_CONFIG_FILE", str(tmp_path / "training.json"))
    monkeypatch.setattr(builder, "_model_definition", deepcopy(builder._model_definition))
    monkeypatch.setattr(builder, "_training_config", deepcopy(builder._training_config))
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(builder.builder_bp)
    return app.test_client()


@pytest.mark.parametrize("offering", ["b1_39m", "b2_50m", "b3_504m"])
def test_offering_round_trip(client, offering):
    response = client.put(
        "/api/v1/builder/walkthrough/progress",
        json={"selected_offering": offering},
    )
    assert response.status_code == 200
    assert response.json["progress"]["selected_offering"] == offering
    assert client.get("/api/v1/builder/walkthrough/progress").json["progress"][
        "selected_offering"
    ] == offering
    with open(builder._WALKTHROUGH_FILE, encoding="utf-8") as saved:
        assert json.load(saved)["selected_offering"] == offering


def test_partial_updates_preserve_pipeline_and_academy_state(client):
    url = "/api/v1/builder/walkthrough/progress"
    client.put(url, json={"current_step": 7, "completed": [2, 1, 2]})
    client.put(url, json={"selected_offering": "b3_504m"})
    client.put(url, json={"academy_step": 4, "academy_completed": True})
    progress = client.get(url).json["progress"]
    assert progress["current_step"] == 7
    assert progress["completed"] == [1, 2]
    client.put(url, json={"current_step": 8, "completed": [1, 2, 7]})
    progress = client.get(url).json["progress"]
    assert progress["selected_offering"] == "b3_504m"
    assert progress["academy_step"] == 4
    assert progress["academy_completed"] is True


@pytest.mark.parametrize("payload", [
    {"selected_offering": "unknown"}, {"selected_offering": []},
    {"selected_offering": None}, {"current_step": True},
    {"current_step": 9}, {"completed": [False]}, {"completed": "all"},
    {"academy_step": 5}, {"academy_completed": "yes"}, [], None,
])
def test_invalid_progress_does_not_overwrite_selection(client, payload):
    url = "/api/v1/builder/walkthrough/progress"
    client.put(url, json={"selected_offering": "b2_50m"})
    before = client.get(url).json["progress"]
    response = client.put(url, data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 400
    assert response.json["success"] is False
    assert client.get(url).json["progress"] == before


def test_legacy_progress_get_is_backward_compatible_and_read_only(client):
    legacy = {"current_step": 3, "completed": [0, 1], "updated_at": None}
    with open(builder._WALKTHROUGH_FILE, "w", encoding="utf-8") as saved:
        json.dump(legacy, saved)
    progress = client.get("/api/v1/builder/walkthrough/progress").json["progress"]
    assert progress["current_step"] == 3
    assert progress["selected_offering"] is None
    assert progress["academy_completed"] is False
    with open(builder._WALKTHROUGH_FILE, encoding="utf-8") as saved:
        assert json.load(saved) == legacy


@pytest.mark.parametrize("contents", ["{broken", "[]"])
def test_corrupt_storage_is_not_reported_as_success(client, contents):
    with open(builder._WALKTHROUGH_FILE, "w", encoding="utf-8") as saved:
        saved.write(contents)
    url = "/api/v1/builder/walkthrough/progress"
    assert client.get(url).status_code == 500
    assert client.put(url, json={"selected_offering": "b1_39m"}).status_code == 500
    with open(builder._WALKTHROUGH_FILE, encoding="utf-8") as saved:
        assert saved.read() == contents


def test_save_failure_is_explicit(client):
    with patch.object(builder, "_save_walkthrough_progress", side_effect=OSError("disk full")):
        response = client.put(
            "/api/v1/builder/walkthrough/progress",
            json={"selected_offering": "b3_504m"},
        )
    assert response.status_code == 500
    assert response.json["success"] is False


def test_failed_atomic_save_keeps_previous_progress(client):
    url = "/api/v1/builder/walkthrough/progress"
    client.put(url, json={"selected_offering": "b1_39m"})
    before = client.get(url).json["progress"]
    with patch.object(builder.os, "replace", side_effect=OSError("storage unavailable")):
        response = client.put(url, json={"selected_offering": "b3_504m"})
    assert response.status_code == 500
    assert client.get(url).json["progress"] == before


def test_concurrent_partial_updates_preserve_both_clients_fields(client):
    barrier = Barrier(2)
    url = "/api/v1/builder/walkthrough/progress"

    def update(fields):
        with client.application.test_client() as concurrent_client:
            barrier.wait(timeout=5)
            return concurrent_client.put(url, json=fields).status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(update, [
            {"current_step": 7, "completed": [1, 2]},
            {"selected_offering": "b3_504m", "academy_completed": True},
        ]))
    assert responses == [200, 200]
    saved = client.get(url).json["progress"]
    assert saved["current_step"] == 7
    assert saved["completed"] == [1, 2]
    assert saved["selected_offering"] == "b3_504m"
    assert saved["academy_completed"] is True


@pytest.mark.parametrize("offering", ["b1_39m", "b2_50m", "b3_504m"])
def test_handoff_uses_existing_canonical_configuration_contract(client, offering):
    response = client.post("/api/v1/builder/model/configure", json={"preset": offering})
    assert response.status_code == 200
    assert response.json["success"] is True
    for key, value in builder._OFFERING_PRESETS[offering]["model"].items():
        assert response.json["config"][key] == value
    training = client.get("/api/v1/builder/training/configure").json["config"]
    for key, value in builder._OFFERING_PRESETS[offering]["training"].items():
        assert training[key] == value
