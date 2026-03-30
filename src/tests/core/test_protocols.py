"""Tests for src.core.protocols — verify protocol definitions are importable
and that runtime_checkable works as expected."""
from __future__ import annotations


class TestProtocolImports:
    """All protocol modules must be importable without side effects."""

    def test_import_memory_protocols(self):
        from src.core.protocols.memory import (
            MemoryManagerProtocol,
        )
        assert MemoryManagerProtocol is not None

    def test_import_model_protocols(self):
        from src.core.protocols.model import (
            ModelBackendProtocol,
        )
        assert ModelBackendProtocol is not None

    def test_import_training_protocols(self):
        from src.core.protocols.training import (
            TrainingPipelineProtocol,
        )
        assert TrainingPipelineProtocol is not None

    def test_import_config_protocols(self):
        from src.core.protocols.config import (
            ConfigProviderProtocol,
        )
        assert ConfigProviderProtocol is not None

    def test_import_inference_protocols(self):
        from src.core.protocols.inference import (
            InferenceSessionProtocol,
        )
        assert InferenceSessionProtocol is not None

    def test_top_level_reexports(self):
        from src.core.protocols import (
            MemoryManagerProtocol,
        )

        # All should be the same objects as the submodule versions
        from src.core.protocols.memory import MemoryManagerProtocol as MMP  # noqa: N817
        assert MemoryManagerProtocol is MMP


class TestCheckpointDataRoundTrip:
    """CheckpointData should serialize and deserialize cleanly."""

    def test_to_save_dict_and_back(self):
        from collections import OrderedDict

        from src.core.protocols.training import CheckpointData

        original = CheckpointData(
            global_step=42,
            model_state_dict=OrderedDict({"w": "fake_tensor"}),
            config={"hidden_dim": 64},
            loss_history=[1.0, 0.5],
        )

        d = original.to_save_dict()
        assert d["global_step"] == 42
        assert d["config"]["hidden_dim"] == 64

        restored = CheckpointData.from_save_dict(d)
        assert restored.global_step == original.global_step
        assert restored.loss_history == original.loss_history

    def test_extra_keys_preserved(self):
        from collections import OrderedDict

        from src.core.protocols.training import CheckpointData

        d = {
            "global_step": 10,
            "model_state_dict": OrderedDict(),
            "config": {},
            "loss_history": [],
            "custom_metric": 0.95,
        }
        restored = CheckpointData.from_save_dict(d)
        assert restored.extra["custom_metric"] == 0.95


class TestRuntimeCheckable:
    """Protocol classes should support isinstance checks at runtime."""

    def test_memory_manager_protocol_isinstance(self):
        from src.core.protocols.memory import MemoryManagerProtocol

        class FakeManager:
            def get_vram_usage(self): return 0.0
            def get_ram_usage(self): return 0.0
            def get_gpu_info(self): return {}
            def optimize_memory(self, required_bytes=0): return 0
            def cleanup(self): pass
            def get_stats(self): return {}

        assert isinstance(FakeManager(), MemoryManagerProtocol)

    def test_non_conforming_class_fails(self):
        from src.core.protocols.memory import MemoryManagerProtocol

        class Incomplete:
            def get_vram_usage(self): return 0.0
            # Missing all other methods

        assert not isinstance(Incomplete(), MemoryManagerProtocol)
