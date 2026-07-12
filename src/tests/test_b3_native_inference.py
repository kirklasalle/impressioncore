#!/usr/bin/env python3
"""
Test B3 Native Inference Engine.

Validates that:
1. The inference engine initializes correctly
2. B3 Hope v1 checkpoint can be found on F:\
3. The model loads and generates text
"""

import pytest
import sys
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_inference_engine_init():
    """Test that the inference engine initializes without errors."""
    from inference.b3_native_inference import B3NativeInference

    engine = B3NativeInference(device="cpu")
    status = engine.get_status()

    assert status["loaded"] is False
    assert status["device"] == "cpu"
    assert "checkpoint" in status


def test_data_paths_module():
    """Test that the centralized data paths module loads correctly."""
    from core.config.data_paths import (
        DATA_DRIVE, MODELS_ROOT, DATA_ROOT,
        B3_HOPE_V1_WEIGHTS, B3_HOPE_V1_CONFIG,
        verify_data_drive, get_data_drive_summary,
    )

    summary = get_data_drive_summary()
    assert "drive_available" in summary
    assert "b3_hope_v1_available" in summary
    assert "rlm_policy_available" in summary

    if DATA_DRIVE.exists():
        assert verify_data_drive() is True


def test_checkpoint_inventory():
    """Test checkpoint inventory utility."""
    from core.config.data_paths import get_checkpoint_inventory, CHECKPOINTS_ROOT

    if not CHECKPOINTS_ROOT.exists():
        pytest.skip("F:\\ drive not available")

    inventory = get_checkpoint_inventory()
    assert isinstance(inventory, dict)
    assert len(inventory) > 0
    print(f"Found {len(inventory)} checkpoint categories:")
    for name, files in inventory.items():
        print(f"  {name}: {len(files)} files")


@pytest.mark.skipif(
    not Path("F:/models/production/b3_hope_v1/impressioncore_b3_hope.pt").exists(),
    reason="B3 Hope v1 checkpoint not available on F:\\"
)
def test_b3_hope_v1_load():
    """Test loading B3 Hope v1 from F:\\ drive (CPU only)."""
    from inference.b3_native_inference import B3NativeInference

    engine = B3NativeInference(device="cpu")
    loaded = engine.load()

    assert loaded is True
    status = engine.get_status()
    assert status["loaded"] is True
    assert status["parameters"] > 0
    print(f"B3 Hope v1 loaded: {status['parameters']:,} parameters")


def test_b3_native_generation_mocked():
    """Test the complete B3NativeInference flow (load, generate) with a tiny mock config/model."""
    from inference.b3_native_inference import B3NativeInference
    from src.core.models.impressioncore_b3_architecture import ImpressionCoreB3Model, B3Config
    import tempfile
    import json
    import torch
    
    # 1. Create a tiny mock config dict
    mock_config = {
        "embed_dim": 64,
        "num_heads": 2,
        "num_layers": 1,
        "vocab_size": 50257,
        "num_experts": 2,
        "expert_dim": 128,
        "experts_per_token": 1,
        "dropout": 0.0,
        "max_seq_length": 128,
        "use_gradient_checkpointing": False,
        "use_mhc": False
    }
    
    # 2. Write it to temporary files
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg_path = Path(tmpdir) / "config.json"
        ckpt_path = Path(tmpdir) / "model.pt"
        
        with open(cfg_path, 'w') as f:
            json.dump(mock_config, f)
            
        # Instantiate a tiny model and save its state dict as a mock checkpoint
        config_obj = B3Config(**mock_config)
        model = ImpressionCoreB3Model(config_obj)
        torch.save({"model_state_dict": model.state_dict()}, ckpt_path)
        
        # 3. Create inference engine pointing to temporary files
        engine = B3NativeInference(
            checkpoint_path=str(ckpt_path),
            config_path=str(cfg_path),
            device="cpu"
        )
        
        # Load
        assert engine.load() is True
        assert engine.get_status()["loaded"] is True
        
        # Generate
        result = engine.generate("Test prompt", max_new_tokens=5, temperature=0.7)
        
        # Verify result fields
        assert "text" in result
        assert "tokens_generated" in result
        assert result["tokens_generated"] > 0
        assert "latency_ms" in result
        assert "tokens_per_second" in result
