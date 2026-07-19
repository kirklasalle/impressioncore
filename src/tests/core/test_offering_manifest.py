"""Tests for offering manifest schema validation.

Covers WS1 (startup schema validation) and WS5 (coverage gate).
"""
import pytest
from copy import deepcopy

from src.core.config.offering_manifest import (
    validate_offering_preset,
    validate_all_offerings,
    validate_offerings_at_startup,
)
from src.core.config.presets import OFFERING_PRESETS


class TestValidateOfferingPreset:
    def test_valid_b1_returns_no_errors(self):
        errors = validate_offering_preset("b1_39m", OFFERING_PRESETS["b1_39m"])
        assert errors == []

    def test_valid_b2_returns_no_errors(self):
        errors = validate_offering_preset("b2_50m", OFFERING_PRESETS["b2_50m"])
        assert errors == []

    def test_valid_b3_returns_no_errors(self):
        errors = validate_offering_preset("b3_504m", OFFERING_PRESETS["b3_504m"])
        assert errors == []

    def test_missing_top_key_detected(self):
        broken = deepcopy(OFFERING_PRESETS["b1_39m"])
        del broken["stage"]
        errors = validate_offering_preset("b1_39m", broken)
        assert any("Missing top-level keys" in e for e in errors)

    def test_id_mismatch_detected(self):
        broken = deepcopy(OFFERING_PRESETS["b1_39m"])
        broken["id"] = "wrong_id"
        errors = validate_offering_preset("b1_39m", broken)
        assert any("does not match key" in e for e in errors)

    def test_invalid_stage_detected(self):
        broken = deepcopy(OFFERING_PRESETS["b1_39m"])
        broken["stage"] = "C1"
        errors = validate_offering_preset("b1_39m", broken)
        assert any("Invalid stage" in e for e in errors)

    def test_negative_target_params_detected(self):
        broken = deepcopy(OFFERING_PRESETS["b1_39m"])
        broken["target_params_m"] = -5
        errors = validate_offering_preset("b1_39m", broken)
        assert any("positive number" in e for e in errors)

    def test_missing_model_key_detected(self):
        broken = deepcopy(OFFERING_PRESETS["b1_39m"])
        del broken["model"]["layers"]
        errors = validate_offering_preset("b1_39m", broken)
        assert any("Missing model keys" in e for e in errors)

    def test_missing_training_key_detected(self):
        broken = deepcopy(OFFERING_PRESETS["b1_39m"])
        del broken["training"]["epochs"]
        errors = validate_offering_preset("b1_39m", broken)
        assert any("Missing training keys" in e for e in errors)


class TestValidateAllOfferings:
    def test_canonical_presets_all_valid(self):
        is_valid, errors = validate_all_offerings(OFFERING_PRESETS)
        assert is_valid is True
        assert errors == []

    def test_empty_presets_invalid(self):
        is_valid, errors = validate_all_offerings({})
        assert is_valid is False
        assert any("No offering presets found" in e for e in errors)

    def test_one_broken_makes_invalid(self):
        presets = deepcopy(OFFERING_PRESETS)
        del presets["b1_39m"]["stage"]
        is_valid, errors = validate_all_offerings(presets)
        assert is_valid is False


class TestValidateOfferingsAtStartup:
    def test_startup_validation_returns_bool(self):
        result = validate_offerings_at_startup()
        assert isinstance(result, bool)

    def test_startup_validation_passes_with_canonical_presets(self):
        assert validate_offerings_at_startup() is True
