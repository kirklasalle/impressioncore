"""Readiness checks never initialize hardware, download weights or run inference."""

import pytest
import sys
from types import SimpleNamespace
import torch
from torch import nn

from src.orchestrator.unified_triad import MockBrainModel, UnifiedBrainTriad
from src.orchestrator import unified_triad


def make_triad(module):
    triad = UnifiedBrainTriad.__new__(UnifiedBrainTriad)
    nn.Module.__init__(triad)
    triad.config = {"model_id": "test/local-model"}
    triad.device = torch.device("cpu")
    triad.simultaneous_load = True
    triad.loading_phase = "READY"
    triad.left = triad.right = triad.colossus = module
    return triad


def test_real_model_reports_identity_and_readiness():
    triad = make_triad(nn.Linear(2, 2))
    result = triad.get_model_status()
    assert result["llm_loaded"] is True
    assert result["model_kind"] == "external_pretrained"
    assert result["implementation"] == "Linear"
    assert result["parameter_count"] == 6
    assert result["dtype"] == "torch.float32"
    assert result["native_impressioncore"] is False


@pytest.mark.parametrize("module", [None, MockBrainModel(None)])
def test_missing_or_mock_weights_never_report_ready(module):
    triad = make_triad(module)
    result = triad.get_model_status()
    assert result["llm_loaded"] is False
    assert result["status"] == "UNAVAILABLE"
    assert all(role["status"] != "ACTIVE" for role in result["agents"].values())
    with pytest.raises(RuntimeError, match="Real model is not ready"):
        triad.generate("Do not generate")


def test_actual_loader_failure_is_not_replaced_by_a_mock(monkeypatch):
    class Nexus:
        def set_triad(self, triad):
            self.triad = triad

    tokenizer = SimpleNamespace(pad_token="pad", eos_token="eos", padding_side="left")

    def fail_load(*args, **kwargs):
        raise OSError("test checkpoint unavailable")

    transformers = SimpleNamespace(
        AutoProcessor=SimpleNamespace(from_pretrained=lambda *args, **kwargs: SimpleNamespace(tokenizer=tokenizer)),
        AutoModel=SimpleNamespace(from_pretrained=fail_load),
        BitsAndBytesConfig=object,
        PreTrainedModel=type("PreTrainedModel", (), {}),
    )
    monkeypatch.setitem(sys.modules, "transformers", transformers)
    for path, name in [
        ("agent0core.core.pose_interpreter", "PoseInterpreter"),
        ("src.orchestrator.orbcloud_vision", "OrbCloudVision"),
        ("src.orchestrator.audio_engine", "AudioEngine"),
        ("src.orchestrator.avatar_engine", "AvatarEngine"),
    ]:
        monkeypatch.setitem(sys.modules, path, SimpleNamespace(**{name: lambda: None}))
    monkeypatch.setattr(unified_triad, "NexusInterpreter", Nexus)
    monkeypatch.setattr(unified_triad, "ImageGenerator", lambda: None)
    monkeypatch.setattr(UnifiedBrainTriad, "_load_config", lambda *args: {"model_id": "test/missing"})
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    original_linspace = torch.linspace
    with pytest.raises(RuntimeError, match="Unable to load real model test/missing"):
        UnifiedBrainTriad()
    assert torch.linspace is original_linspace


@pytest.mark.parametrize("failure", ["exception", "empty"])
def test_generation_failure_is_not_returned_as_a_successful_message(failure):
    class Model(nn.Linear):
        def generate(self, **kwargs):
            if failure == "exception":
                raise OSError("test generation failure")
            return torch.tensor([[1, 2, 3]])

    class Tokenizer:
        pad_token_id = 0

        def __call__(self, *args, **kwargs):
            return {"input_ids": torch.tensor([[1, 2]])}

        def decode(self, *args, **kwargs):
            return ""

    triad = make_triad(Model(2, 2))
    triad.vision_active = False
    triad.vision = None
    triad.processor = None
    triad.tokenizer = Tokenizer()
    with pytest.raises(RuntimeError, match="Left generation failed"):
        triad.generate("Do not return a fabricated response")
