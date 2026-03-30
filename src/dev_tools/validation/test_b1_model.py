#!/usr/bin/env python3
"""
B1 Unified Model Import Test

Test importing and instantiating the B1 unified model to ensure
it works with our corrected import structure.

Created: 2025-01-06
Purpose: Validate B1 model instantiation
"""

import sys
import traceback
from pathlib import Path

# Add project root to path for testing (to allow src.* imports)
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Also add src directly to path for relative imports
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

def test_b1_model_import():
    """Test importing and instantiating the B1 unified model."""
    print("=" * 60)
    print("ImpressionCore B1 Unified Model Import Test")
    print("=" * 60)
    
    try:
        print("Importing B1 unified model...")        # Import using absolute path due to hyphen in directory name
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "b1_unified_model", 
            src_path / "training" / "models" / "impressioncore-base" / "b1_unified_model.py"
        )
        b1_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(b1_module)
        ImpressionCoreB1Model = b1_module.ImpressionCoreB1UnifiedModel
        print("✓ Successfully imported ImpressionCoreB1UnifiedModel")
        
        print("\nCreating model configuration...")
        config = {
            'hidden_dim': 512,
            'vocab_size': 32000,
            'image_size': 256,
            'audio_sample_rate': 16000,
            'max_seq_length': 1024,
            'num_layers': 4,
            'num_heads': 8,
            'embed_dim': 512
        }
        print("✓ Configuration created")
        
        print("\nInstantiating B1 model...")
        model = ImpressionCoreB1Model(config)
        print("✓ Model instantiated successfully")
        
        print(f"\nModel summary:")
        print(f"- Total parameters: {sum(p.numel() for p in model.parameters()):,}")
        print(f"- Trainable parameters: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")
        
        print("\n🎉 B1 unified model import and instantiation successful!")
        return True
        
    except Exception as e:
        print(f"✗ Failed to import/instantiate B1 model: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_b1_model_import()
    sys.exit(0 if success else 1)
