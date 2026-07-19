"""Tests for B-series offering presets and manifest schema validation.

Covers WS1 (offering manifest hardening) and WS5 (coverage gate uplift).
"""
import pytest
from copy import deepcopy

from src.core.config.presets import (
    OFFERING_PRESETS,
    get_builder_offering_presets,
)


# --- Schema constants ---
REQUIRED_TOP_KEYS = {"id", "stage", "name", "target_params_m", "model", "training"}
REQUIRED_MODEL_KEYS = {
    "architecture", "preset", "layers", "hiddenSize", "heads",
    "intermediateSize", "contextWindow", "vocabSize", "precision",
    "activation", "rope",
}
REQUIRED_TRAINING_KEYS = {
    "epochs", "batchSize", "learningRate", "warmupSteps",
    "scheduler", "precision", "gradCheckpoint", "gradAccumSteps",
    "maxSteps", "checkpointDir",
}
VALID_OFFERING_IDS = {"b1_39m", "b2_50m", "b3_504m"}
VALID_STAGES = {"B1", "B2", "B3"}


class TestOfferingPresetsExist:
    def test_offering_presets_has_three_entries(self):
        assert len(OFFERING_PRESETS) == 3

    def test_offering_ids_match_canonical_set(self):
        assert set(OFFERING_PRESETS.keys()) == VALID_OFFERING_IDS

    def test_get_builder_offering_presets_returns_deep_copy(self):
        copy = get_builder_offering_presets()
        assert copy == OFFERING_PRESETS
        copy["b1_39m"]["name"] = "MUTATED"
        assert OFFERING_PRESETS["b1_39m"]["name"] != "MUTATED"


class TestOfferingManifestSchema:
    @pytest.mark.parametrize("preset_id", VALID_OFFERING_IDS)
    def test_top_level_keys_present(self, preset_id):
        preset = OFFERING_PRESETS[preset_id]
        missing = REQUIRED_TOP_KEYS - set(preset.keys())
        assert not missing, f"{preset_id} missing top keys: {missing}"

    @pytest.mark.parametrize("preset_id", VALID_OFFERING_IDS)
    def test_model_keys_present(self, preset_id):
        model = OFFERING_PRESETS[preset_id]["model"]
        missing = REQUIRED_MODEL_KEYS - set(model.keys())
        assert not missing, f"{preset_id} model missing keys: {missing}"

    @pytest.mark.parametrize("preset_id", VALID_OFFERING_IDS)
    def test_training_keys_present(self, preset_id):
        training = OFFERING_PRESETS[preset_id]["training"]
        missing = REQUIRED_TRAINING_KEYS - set(training.keys())
        assert not missing, f"{preset_id} training missing keys: {missing}"

    @pytest.mark.parametrize("preset_id", VALID_OFFERING_IDS)
    def test_id_matches_key(self, preset_id):
        assert OFFERING_PRESETS[preset_id]["id"] == preset_id

    @pytest.mark.parametrize("preset_id", VALID_OFFERING_IDS)
    def test_stage_is_valid(self, preset_id):
        assert OFFERING_PRESETS[preset_id]["stage"] in VALID_STAGES

    @pytest.mark.parametrize("preset_id", VALID_OFFERING_IDS)
    def test_target_params_positive_int(self, preset_id):
        val = OFFERING_PRESETS[preset_id]["target_params_m"]
        assert isinstance(val, (int, float)) and val > 0


class TestOfferingPresetValues:
    def test_b1_target_params(self):
        assert OFFERING_PRESETS["b1_39m"]["target_params_m"] == 39

    def test_b2_target_params(self):
        assert OFFERING_PRESETS["b2_50m"]["target_params_m"] == 50

    def test_b3_target_params(self):
        assert OFFERING_PRESETS["b3_504m"]["target_params_m"] == 504

    def test_b1_layers_less_than_b3(self):
        assert OFFERING_PRESETS["b1_39m"]["model"]["layers"] < OFFERING_PRESETS["b3_504m"]["model"]["layers"]

    def test_b3_has_flash_attention(self):
        assert OFFERING_PRESETS["b3_504m"]["model"]["flashAttention"] is True

    def test_all_use_cosine_scheduler(self):
        for pid in VALID_OFFERING_IDS:
            assert OFFERING_PRESETS[pid]["training"]["scheduler"] == "cosine"

    def test_all_use_grad_checkpoint(self):
        for pid in VALID_OFFERING_IDS:
            assert OFFERING_PRESETS[pid]["training"]["gradCheckpoint"] is True

    def test_all_checkpoint_dirs_exist_as_strings(self):
        for pid in VALID_OFFERING_IDS:
            cdir = OFFERING_PRESETS[pid]["training"]["checkpointDir"]
            assert isinstance(cdir, str) and len(cdir) > 0
