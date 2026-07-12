"""Unit tests for src.core.config.config_utils."""

import pytest
from src.core.config.config_utils import merge_configs, validate_config, filter_config, ConfigMixin


class TestMergeConfigs:
    def test_none_override_returns_deep_copy(self):
        default = {"a": 1, "nested": {"b": 2}}
        result = merge_configs(default, None)
        assert result == default
        result["nested"]["b"] = 999
        assert default["nested"]["b"] == 2  # original unchanged

    def test_flat_override(self):
        result = merge_configs({"a": 1, "b": 2}, {"a": 10})
        assert result == {"a": 10, "b": 2}

    def test_nested_merge(self):
        default = {"model": {"hidden": 768, "layers": 12}, "lr": 5e-5}
        override = {"model": {"hidden": 1024}}
        result = merge_configs(default, override)
        assert result["model"]["hidden"] == 1024
        assert result["model"]["layers"] == 12
        assert result["lr"] == 5e-5

    def test_new_key_added(self):
        result = merge_configs({"a": 1}, {"b": 2})
        assert result == {"a": 1, "b": 2}

    def test_empty_configs(self):
        assert merge_configs({}, {}) == {}
        assert merge_configs({}, None) == {}


class TestValidateConfig:
    def test_passes_with_all_required_keys(self):
        validate_config({"a": 1, "b": 2}, required_keys=["a", "b"])

    def test_raises_on_missing_required_key(self):
        with pytest.raises(ValueError, match="Missing required"):
            validate_config({"a": 1}, required_keys=["a", "b"])

    def test_passes_with_correct_types(self):
        validate_config(
            {"name": "test", "count": 5},
            value_types={"name": str, "count": int},
        )

    def test_raises_on_wrong_type(self):
        with pytest.raises(ValueError, match="expected one of"):
            validate_config({"name": 123}, value_types={"name": str})

    def test_multi_type_accepted(self):
        validate_config({"val": 3.14}, value_types={"val": [int, float]})

    def test_no_validation_params(self):
        validate_config({"anything": "goes"})


class TestFilterConfig:
    def test_keeps_allowed_keys_only(self):
        result = filter_config({"a": 1, "b": 2, "c": 3}, {"a", "c"})
        assert result == {"a": 1, "c": 3}

    def test_empty_allowed_returns_empty(self):
        assert filter_config({"a": 1}, set()) == {}


class TestConfigMixin:
    def test_mixin_default_config(self):
        mixin = ConfigMixin()
        result = mixin._get_config_dict()
        assert result == {}

    def test_mixin_with_overrides(self):
        class MyComponent(ConfigMixin):
            def _get_default_config(self):
                return {"param1": "default", "param2": 42}

        comp = MyComponent()
        config = comp._get_config_dict({"param1": "custom"})
        assert config["param1"] == "custom"
        assert config["param2"] == 42

    def test_mixin_validate_is_noop_by_default(self):
        mixin = ConfigMixin()
        mixin._validate_config({"any": "thing"})
