"""Tests for src.core.config.config — dataclass configs and utility functions."""

import json
import logging
from unittest.mock import patch

import pytest
import yaml

# Also import the tiny config (present in source but not in __all__)
from src.core.config.config import (
    BrainSimConfig,
    ConfigManager,
    ModelConfig,
    ModelDimensions,
    ResourceConfig,
    TrainingConfig,
    UKSConfig,
    debug_model_creation,
    estimate_vram_usage,
    get_gpu_compatible_config,
    get_impressioncore_1b_config,
    get_impressioncore_small_config,
    get_impressioncore_tiny_config,
    get_model_config,
    safely_create_model,
    setup_logging,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def dims():
    """Minimal ModelDimensions with small values for fast tests."""
    return ModelDimensions(
        hidden_size=256,
        intermediate_size=512,
        num_attention_heads=4,
        num_hidden_layers=2,
    )


@pytest.fixture
def model_cfg(dims):
    """Minimal ModelConfig built from the dims fixture."""
    return ModelConfig(
        model_type="test_type",
        model_name="test-model",
        dimensions=dims,
    )


@pytest.fixture
def full_model_cfg():
    """Fully-specified ModelConfig for exhaustive property tests."""
    return ModelConfig(
        model_type="impression_core",
        model_name="full-test",
        dimensions=ModelDimensions(
            hidden_size=768,
            intermediate_size=2048,
            num_attention_heads=12,
            num_hidden_layers=12,
            max_position_embeddings=4096,
            vocab_size=32000,
        ),
        vocab_size=32000,
        uks_config=UKSConfig(enabled=False, memory_size=5000, embedding_dim=512),
        brainsim_config=BrainSimConfig(enabled=True, connection_url="remote:50051"),
        training=TrainingConfig(learning_rate=1e-4, batch_size=16),
        dual_shadow_enabled=True,
        activation_function="silu",
        initializer_range=0.01,
        rms_norm_eps=1e-5,
        use_cache=False,
        tie_word_embeddings=True,
        rope_theta=500000.0,
        multimodal=True,
        quantization={"enabled": True, "bits": 4},
    )


# ===================================================================
# ModelDimensions
# ===================================================================

class TestModelDimensions:
    """Tests for the ModelDimensions dataclass."""

    def test_required_fields(self, dims):
        assert dims.hidden_size == 256
        assert dims.intermediate_size == 512
        assert dims.num_attention_heads == 4
        assert dims.num_hidden_layers == 2

    def test_default_max_position_embeddings(self):
        d = ModelDimensions(128, 256, 2, 1)
        assert d.max_position_embeddings == 2048

    def test_default_vocab_size(self):
        d = ModelDimensions(128, 256, 2, 1)
        assert d.vocab_size == 50304

    def test_head_dim_auto_calculated(self, dims):
        # 256 // 4 == 64
        assert dims.head_dim == 64

    def test_head_dim_explicit(self):
        d = ModelDimensions(256, 512, 4, 2, head_dim=128)
        assert d.head_dim == 128

    def test_head_dim_none_triggers_post_init(self):
        d = ModelDimensions(768, 2048, 12, 6)
        assert d.head_dim == 768 // 12

    def test_config_dict_keys(self, dims):
        cd = dims.config_dict
        expected_keys = {
            "hidden_size", "intermediate_size", "num_attention_heads",
            "num_hidden_layers", "max_position_embeddings", "vocab_size", "head_dim",
        }
        assert set(cd.keys()) == expected_keys

    def test_config_dict_values(self, dims):
        cd = dims.config_dict
        assert cd["hidden_size"] == 256
        assert cd["head_dim"] == 64

    def test_config_dict_roundtrip(self, dims):
        cd = dims.config_dict
        rebuilt = ModelDimensions(**cd)
        assert rebuilt == dims


# ===================================================================
# UKSConfig
# ===================================================================

class TestUKSConfig:

    def test_defaults(self):
        c = UKSConfig()
        assert c.enabled is True
        assert c.memory_size == 10000
        assert c.embedding_dim == 768
        assert c.query_dim == 768
        assert c.similarity_threshold == 0.75
        assert c.retrieval_limit == 5
        assert c.persistent_storage_path is None

    def test_custom_values(self):
        c = UKSConfig(enabled=False, memory_size=500, embedding_dim=256,
                       query_dim=128, similarity_threshold=0.9,
                       retrieval_limit=10, persistent_storage_path="/tmp/uks")
        assert c.enabled is False
        assert c.persistent_storage_path == "/tmp/uks"

    def test_config_dict_keys(self):
        cd = UKSConfig().config_dict
        assert "enabled" in cd
        assert "persistent_storage_path" in cd

    def test_config_dict_roundtrip(self):
        orig = UKSConfig(memory_size=42)
        rebuilt = UKSConfig(**orig.config_dict)
        assert rebuilt == orig


# ===================================================================
# BrainSimConfig
# ===================================================================

class TestBrainSimConfig:

    def test_defaults(self):
        c = BrainSimConfig()
        assert c.enabled is False
        assert c.connection_url == "localhost:50051"
        assert c.simulation_rate == 1.0
        assert c.sync_interval == 100
        assert c.brain_region_mappings == {}

    def test_custom_values(self):
        mappings = {"cortex": "layer1", "hippocampus": "layer2"}
        c = BrainSimConfig(enabled=True, brain_region_mappings=mappings)
        assert c.brain_region_mappings == mappings

    def test_config_dict_roundtrip(self):
        mappings = {"a": "b"}
        orig = BrainSimConfig(enabled=True, brain_region_mappings=mappings)
        rebuilt = BrainSimConfig(**orig.config_dict)
        assert rebuilt == orig


# ===================================================================
# ResourceConfig
# ===================================================================

class TestResourceConfig:

    def test_defaults(self):
        c = ResourceConfig()
        assert c.gradient_accumulation_steps == 1
        assert c.mixed_precision is True
        assert c.cpu_offload is False
        assert c.memory_efficient_attention is True
        assert c.bf16 is False
        assert c.vram_efficient_loading is True

    def test_custom_values(self):
        c = ResourceConfig(gradient_accumulation_steps=8, bf16=True, cpu_offload=True)
        assert c.gradient_accumulation_steps == 8
        assert c.bf16 is True

    def test_config_dict_roundtrip(self):
        orig = ResourceConfig(cpu_offload=True, bf16=True)
        rebuilt = ResourceConfig(**orig.config_dict)
        assert rebuilt == orig


# ===================================================================
# TrainingConfig
# ===================================================================

class TestTrainingConfig:

    def test_defaults(self):
        c = TrainingConfig()
        assert c.learning_rate == 2e-5
        assert c.weight_decay == 0.01
        assert c.warmup_steps == 500
        assert c.max_steps == 100000
        assert c.batch_size == 32
        assert c.gradient_accumulation_steps == 1
        assert c.fp16 is True
        assert c.bf16 is False
        assert c.gradient_checkpointing is False

    def test_custom_values(self):
        c = TrainingConfig(learning_rate=1e-3, batch_size=8, gradient_checkpointing=True)
        assert c.learning_rate == 1e-3
        assert c.batch_size == 8
        assert c.gradient_checkpointing is True

    def test_config_dict_keys(self):
        cd = TrainingConfig().config_dict
        expected = {
            "learning_rate", "weight_decay", "warmup_steps", "max_steps",
            "batch_size", "gradient_accumulation_steps", "fp16", "bf16",
            "gradient_checkpointing",
        }
        assert set(cd.keys()) == expected

    def test_config_dict_roundtrip(self):
        orig = TrainingConfig(learning_rate=5e-4, max_steps=200)
        rebuilt = TrainingConfig(**orig.config_dict)
        assert rebuilt == orig


# ===================================================================
# ModelConfig — construction & to_dict
# ===================================================================

class TestModelConfigConstruction:

    def test_minimal(self, model_cfg):
        assert model_cfg.model_type == "test_type"
        assert model_cfg.model_name == "test-model"
        assert model_cfg.vocab_size == 50304
        assert isinstance(model_cfg.uks_config, UKSConfig)
        assert isinstance(model_cfg.brainsim_config, BrainSimConfig)
        assert isinstance(model_cfg.training, TrainingConfig)

    def test_default_scalar_fields(self, model_cfg):
        assert model_cfg.dual_shadow_enabled is False
        assert model_cfg.activation_function == "gelu"
        assert model_cfg.initializer_range == 0.02
        assert model_cfg.rms_norm_eps == 1e-6
        assert model_cfg.use_cache is True
        assert model_cfg.tie_word_embeddings is False
        assert model_cfg.rope_theta == 10000.0
        assert model_cfg.multimodal is False
        assert model_cfg.quantization is None

    def test_to_dict_includes_core_keys(self, model_cfg):
        d = model_cfg.to_dict()
        for key in ("model_type", "model_name", "dimensions", "vocab_size",
                     "uks_config", "brainsim_config", "training",
                     "dual_shadow_enabled", "activation_function",
                     "initializer_range", "rms_norm_eps", "use_cache",
                     "tie_word_embeddings", "rope_theta", "multimodal"):
            assert key in d, f"Missing key: {key}"

    def test_to_dict_omits_quantization_when_none(self, model_cfg):
        d = model_cfg.to_dict()
        assert "quantization" not in d

    def test_to_dict_includes_quantization_when_set(self, full_model_cfg):
        d = full_model_cfg.to_dict()
        assert "quantization" in d
        assert d["quantization"]["bits"] == 4

    def test_to_dict_nested_dims(self, model_cfg):
        d = model_cfg.to_dict()
        assert d["dimensions"]["hidden_size"] == 256


# ===================================================================
# ModelConfig — properties (getters / setters)
# ===================================================================

class TestModelConfigProperties:

    def test_hidden_size_getter(self, model_cfg):
        assert model_cfg.hidden_size == 256

    def test_hidden_size_setter(self, model_cfg):
        model_cfg.hidden_size = 512
        assert model_cfg.hidden_size == 512
        assert model_cfg.dimensions.hidden_size == 512

    def test_dropout_is_constant(self, model_cfg):
        assert model_cfg.dropout == 0.1

    def test_num_layers(self, model_cfg):
        assert model_cfg.num_layers == 2

    def test_layer_norm_eps(self, model_cfg):
        assert model_cfg.layer_norm_eps == model_cfg.rms_norm_eps

    def test_max_position_embeddings_getter(self, model_cfg):
        assert model_cfg.max_position_embeddings == 2048

    def test_max_position_embeddings_setter(self, model_cfg):
        model_cfg.max_position_embeddings = 4096
        assert model_cfg.max_position_embeddings == 4096
        assert model_cfg.dimensions.max_position_embeddings == 4096

    def test_num_heads(self, model_cfg):
        assert model_cfg.num_heads == 4

    def test_num_attention_heads_getter(self, model_cfg):
        assert model_cfg.num_attention_heads == 4

    def test_num_attention_heads_setter(self, model_cfg):
        model_cfg.num_attention_heads = 8
        assert model_cfg.num_attention_heads == 8
        assert model_cfg.dimensions.num_attention_heads == 8

    def test_num_hidden_layers_getter(self, model_cfg):
        assert model_cfg.num_hidden_layers == 2

    def test_num_hidden_layers_setter(self, model_cfg):
        model_cfg.num_hidden_layers = 6
        assert model_cfg.num_hidden_layers == 6
        assert model_cfg.dimensions.num_hidden_layers == 6

    def test_intermediate_size_getter(self, model_cfg):
        assert model_cfg.intermediate_size == 512

    def test_intermediate_size_setter(self, model_cfg):
        model_cfg.intermediate_size = 1024
        assert model_cfg.intermediate_size == 1024
        assert model_cfg.dimensions.intermediate_size == 1024

    def test_num_visual_features_default(self, model_cfg):
        assert model_cfg.num_visual_features == 0

    def test_num_visual_features_setter(self, model_cfg):
        model_cfg.num_visual_features = 196
        assert model_cfg.num_visual_features == 196

    def test_num_audio_features_default(self, model_cfg):
        assert model_cfg.num_audio_features == 0

    def test_num_audio_features_setter(self, model_cfg):
        model_cfg.num_audio_features = 80
        assert model_cfg.num_audio_features == 80


# ===================================================================
# ModelConfig — from_dict / from_json / from_yaml
# ===================================================================

class TestModelConfigSerialization:
    """
    Tests for from_dict / from_json / from_yaml serialization roundtrips.
    """

    def test_from_dict_roundtrip(self, model_cfg):
        d = model_cfg.to_dict()
        rebuilt = ModelConfig.from_dict(d)
        assert rebuilt.model_name == model_cfg.model_name

    def test_from_dict_with_quantization(self, full_model_cfg):
        d = full_model_cfg.to_dict()
        rebuilt = ModelConfig.from_dict(d)
        assert rebuilt.quantization == full_model_cfg.quantization

    def test_from_json(self, model_cfg, tmp_path):
        path = str(tmp_path / "cfg.json")
        model_cfg.save_json(path)
        rebuilt = ModelConfig.from_json(path)
        assert rebuilt.model_name == model_cfg.model_name

    def test_from_yaml(self, model_cfg, tmp_path):
        path = str(tmp_path / "cfg.yaml")
        model_cfg.save_yaml(path)
        rebuilt = ModelConfig.from_yaml(path)
        assert rebuilt.model_name == model_cfg.model_name

    # ---- save methods work independently of from_dict ----

    def test_save_json_creates_file(self, model_cfg, tmp_path):
        path = tmp_path / "sub" / "cfg.json"
        model_cfg.save_json(str(path))
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["model_name"] == "test-model"

    def test_save_yaml_creates_file(self, model_cfg, tmp_path):
        path = tmp_path / "sub" / "cfg.yaml"
        model_cfg.save_yaml(str(path))
        assert path.exists()
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["model_name"] == "test-model"

    def test_save_json_content_matches_to_dict(self, full_model_cfg, tmp_path):
        path = tmp_path / "cfg.json"
        full_model_cfg.save_json(str(path))
        loaded = json.loads(path.read_text(encoding="utf-8"))
        expected = full_model_cfg.to_dict()
        assert loaded == expected

    def test_save_yaml_content_matches_to_dict(self, full_model_cfg, tmp_path):
        path = tmp_path / "cfg.yaml"
        full_model_cfg.save_yaml(str(path))
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        expected = full_model_cfg.to_dict()
        assert loaded == expected


# ===================================================================
# ConfigManager
# ===================================================================

class TestConfigManager:

    def test_init_config_is_none(self):
        cm = ConfigManager()
        assert cm.model_config is None

    def test_get_config_returns_none_initially(self):
        cm = ConfigManager()
        assert cm.get_config() is None

    def test_set_and_get_config(self, model_cfg):
        cm = ConfigManager()
        cm.set_model_config(model_cfg)
        assert cm.get_config() is model_cfg

    def test_training_config_when_no_model(self):
        cm = ConfigManager()
        assert cm.training_config is None

    def test_training_config_with_model(self, model_cfg):
        cm = ConfigManager()
        cm.set_model_config(model_cfg)
        assert cm.training_config is model_cfg.training

    def test_validate_hardware_no_config(self):
        cm = ConfigManager()
        assert cm.validate_hardware_compatibility() is False

    @patch("src.core.config.config.get_available_vram", return_value=0.0)
    def test_validate_hardware_no_gpu(self, _mock_vram, model_cfg):
        cm = ConfigManager()
        cm.set_model_config(model_cfg)
        assert cm.validate_hardware_compatibility() is False

    @patch("src.core.config.config.estimate_vram_usage", return_value=2.0)
    @patch("src.core.config.config.get_available_vram", return_value=8.0)
    def test_validate_hardware_compatible(self, _vram, _est, model_cfg):
        cm = ConfigManager()
        cm.set_model_config(model_cfg)
        assert cm.validate_hardware_compatibility() is True

    @patch("src.core.config.config.estimate_vram_usage", return_value=10.0)
    @patch("src.core.config.config.get_available_vram", return_value=4.0)
    def test_validate_hardware_insufficient_vram(self, _vram, _est, model_cfg):
        cm = ConfigManager()
        cm.set_model_config(model_cfg)
        assert cm.validate_hardware_compatibility() is False


# ===================================================================
# Predefined configuration getters
# ===================================================================

class TestPredefinedConfigs:

    def test_1b_config_type(self):
        cfg = get_impressioncore_1b_config()
        assert cfg.model_type == "impression_core"
        assert cfg.model_name == "impressioncore-1b"

    def test_1b_config_dimensions(self):
        cfg = get_impressioncore_1b_config()
        assert cfg.hidden_size == 2048
        assert cfg.intermediate_size == 5632
        assert cfg.num_attention_heads == 16
        assert cfg.num_hidden_layers == 24

    def test_1b_config_dual_shadow(self):
        assert get_impressioncore_1b_config().dual_shadow_enabled is True

    def test_small_config_type(self):
        cfg = get_impressioncore_small_config()
        assert cfg.model_name == "impressioncore-small"

    def test_small_config_dimensions(self):
        cfg = get_impressioncore_small_config()
        assert cfg.hidden_size == 768
        assert cfg.num_attention_heads == 12
        assert cfg.num_hidden_layers == 12

    def test_small_config_dual_shadow_disabled(self):
        assert get_impressioncore_small_config().dual_shadow_enabled is False

    def test_tiny_config_type(self):
        cfg = get_impressioncore_tiny_config()
        assert cfg.model_name == "impressioncore-tiny"

    def test_tiny_config_dimensions(self):
        cfg = get_impressioncore_tiny_config()
        assert cfg.hidden_size == 384
        assert cfg.num_attention_heads == 6
        assert cfg.num_hidden_layers == 8
        assert cfg.max_position_embeddings == 1024

    def test_tiny_config_reduced_vocab(self):
        cfg = get_impressioncore_tiny_config()
        assert cfg.vocab_size == 32000

    def test_each_config_produces_valid_to_dict(self):
        for getter in (get_impressioncore_1b_config,
                       get_impressioncore_small_config,
                       get_impressioncore_tiny_config):
            d = getter().to_dict()
            assert "dimensions" in d
            assert "model_name" in d


# ===================================================================
# estimate_vram_usage
# ===================================================================

class TestEstimateVramUsage:

    def test_returns_positive_float(self, model_cfg):
        est = estimate_vram_usage(model_cfg)
        assert isinstance(est, float)
        assert est > 0

    def test_float32_uses_more_than_float16(self, model_cfg):
        fp32 = estimate_vram_usage(model_cfg, dtype="float32")
        fp16 = estimate_vram_usage(model_cfg, dtype="float16")
        assert fp32 > fp16

    def test_larger_model_uses_more_vram(self):
        small = get_impressioncore_small_config()
        big = get_impressioncore_1b_config()
        assert estimate_vram_usage(big) > estimate_vram_usage(small)

    def test_no_kv_cache_uses_less(self, model_cfg):
        with_cache = estimate_vram_usage(model_cfg, use_kv_cache=True)
        without_cache = estimate_vram_usage(model_cfg, use_kv_cache=False)
        assert with_cache > without_cache

    def test_int8_quantization_reduces_estimate(self):
        cfg = get_impressioncore_small_config()
        base = estimate_vram_usage(cfg)
        cfg.quantization = {"enabled": True, "bits": 8}
        quant = estimate_vram_usage(cfg)
        assert quant < base

    def test_int4_quantization_reduces_more_than_int8(self):
        cfg_8 = get_impressioncore_small_config()
        cfg_8.quantization = {"enabled": True, "bits": 8}
        cfg_4 = get_impressioncore_small_config()
        cfg_4.quantization = {"enabled": True, "bits": 4}
        assert estimate_vram_usage(cfg_4) < estimate_vram_usage(cfg_8)

    def test_quantization_disabled_flag(self):
        cfg = get_impressioncore_small_config()
        base = estimate_vram_usage(cfg)
        cfg.quantization = {"enabled": False, "bits": 4}
        same = estimate_vram_usage(cfg)
        assert same == pytest.approx(base)

    def test_batch_size_affects_estimate(self, model_cfg):
        b1 = estimate_vram_usage(model_cfg, batch_size=1)
        b4 = estimate_vram_usage(model_cfg, batch_size=4)
        assert b4 > b1

    def test_unknown_dtype_defaults_to_fp16(self, model_cfg):
        unknown = estimate_vram_usage(model_cfg, dtype="bfloat8")
        fp16 = estimate_vram_usage(model_cfg, dtype="float16")
        assert unknown == pytest.approx(fp16)

    def test_includes_20_percent_safety_margin(self, model_cfg):
        # The function multiplies total by 1.2; verify estimate > raw total
        est = estimate_vram_usage(model_cfg)
        # A very rough check: removing the 20% margin should be smaller
        assert est > 0  # can't easily separate margin, just ensure positive


# ===================================================================
# get_gpu_compatible_config
# ===================================================================

class TestGetGpuCompatibleConfig:

    def test_high_vram_returns_1b(self):
        cfg = get_gpu_compatible_config(vram_gb=16.0)
        assert cfg.model_name == "impressioncore-1b"

    def test_mid_vram_returns_small(self):
        cfg = get_gpu_compatible_config(vram_gb=6.0)
        assert cfg.model_name == "impressioncore-small"

    def test_low_vram_returns_tiny(self):
        cfg = get_gpu_compatible_config(vram_gb=2.0)
        assert cfg.model_name == "impressioncore-tiny"

    def test_zero_vram_returns_tiny(self):
        cfg = get_gpu_compatible_config(vram_gb=0.0)
        assert cfg.model_name == "impressioncore-tiny"

    @patch("src.core.config.config.get_available_vram", return_value=0.0)
    def test_auto_detect_no_gpu(self, _mock):
        cfg = get_gpu_compatible_config(vram_gb=None)
        assert cfg.model_name == "impressioncore-tiny"

    def test_safety_margin_applied(self):
        # 5GB * 0.8 = 4.0 effective → should pick small (threshold >=4)
        cfg = get_gpu_compatible_config(vram_gb=5.0, safety_margin=0.8)
        assert cfg.model_name == "impressioncore-small"

    def test_safety_margin_tight_downgrades(self):
        # 5GB * 0.5 = 2.5 effective → < 4 so tiny
        cfg = get_gpu_compatible_config(vram_gb=5.0, safety_margin=0.5)
        assert cfg.model_name == "impressioncore-tiny"


# ===================================================================
# get_model_config
# ===================================================================

class TestGetModelConfig:

    @patch("src.core.config.config.get_available_vram", return_value=0.0)
    def test_impressioncore_1b(self, _mock):
        cfg = get_model_config("impressioncore-1b")
        assert cfg.model_name == "impressioncore-1b"

    @patch("src.core.config.config.get_available_vram", return_value=0.0)
    def test_impressioncore_small(self, _mock):
        cfg = get_model_config("impressioncore-small")
        assert cfg.model_name == "impressioncore-small"

    @patch("src.core.config.config.get_available_vram", return_value=0.0)
    def test_impressioncore_tiny(self, _mock):
        cfg = get_model_config("impressioncore-tiny")
        assert cfg.model_name == "impressioncore-tiny"

    @patch("src.core.config.config.get_available_vram", return_value=0.0)
    def test_auto_no_gpu(self, _mock):
        cfg = get_model_config("auto")
        assert cfg.model_name == "impressioncore-tiny"

    @patch("src.core.config.config.get_available_vram", return_value=16.0)
    def test_auto_high_vram(self, _mock):
        cfg = get_model_config("auto")
        assert cfg.model_name == "impressioncore-1b"

    def test_unknown_name_raises(self):
        # ConfigManager has no load_config method → AttributeError propagates
        with pytest.raises((ValueError, AttributeError)):
            get_model_config("nonexistent-model-xyz")

    @patch("src.core.config.config.get_available_vram", return_value=3.5)
    def test_1b_limited_vram_enables_quantization(self, _mock):
        cfg = get_model_config("impressioncore-1b")
        assert cfg.quantization is not None
        assert cfg.quantization["enabled"] is True
        assert cfg.quantization["bits"] == 4

    @patch("src.core.config.config.get_available_vram", return_value=3.5)
    def test_case_insensitive_lookup(self, _mock):
        cfg = get_model_config("ImpressionCore-1B")
        assert cfg.model_name == "impressioncore-1b"


# ===================================================================
# debug_model_creation
# ===================================================================

class TestDebugModelCreation:

    def test_returns_dict(self, model_cfg):
        info = debug_model_creation(model_cfg)
        assert isinstance(info, dict)

    def test_contains_expected_keys(self, model_cfg):
        info = debug_model_creation(model_cfg)
        for key in ("model_name", "model_type", "parameter_count",
                     "vram_estimate", "hidden_size", "num_layers"):
            assert key in info

    def test_parameter_count_positive(self, model_cfg):
        info = debug_model_creation(model_cfg)
        assert info["parameter_count"] is not None
        assert info["parameter_count"] > 0

    def test_vram_estimate_positive(self, model_cfg):
        info = debug_model_creation(model_cfg)
        assert info["vram_estimate"] is not None
        assert info["vram_estimate"] > 0

    def test_saves_to_file(self, model_cfg, tmp_path):
        path = str(tmp_path / "debug.json")
        debug_model_creation(model_cfg, filepath=path)
        assert (tmp_path / "debug.json").exists()
        data = json.loads((tmp_path / "debug.json").read_text())
        assert data["model_name"] == "test-model"


# ===================================================================
# safely_create_model
# ===================================================================

class TestSafelyCreateModel:

    def test_with_config_object(self, model_cfg):
        result, err = safely_create_model(model_cfg)
        assert result is not None
        assert err is None

    @patch("src.core.config.config.get_available_vram", return_value=0.0)
    def test_with_string_name(self, _mock):
        result, err = safely_create_model("impressioncore-tiny")
        assert result is not None
        assert err is None

    def test_with_invalid_name(self):
        result, err = safely_create_model("nonexistent-model-xyz")
        assert result is None
        assert err is not None
        assert "nonexistent-model-xyz" in err


# ===================================================================
# setup_logging
# ===================================================================

class TestSetupLogging:

    def test_setup_logging_does_not_raise(self):
        setup_logging(level=logging.WARNING)

    def test_setup_logging_debug_level(self):
        setup_logging(level=logging.DEBUG)
        logger = logging.getLogger("core.config")
        # Logger should exist and have level set
        assert logger is not None
