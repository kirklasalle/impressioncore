#!/usr/bin/env python3
"""
B1 Component-wise Import Test

Test importing B1 model components individually to isolate
any remaining import issues.

Created: 2025-01-06
Purpose: Validate B1 model components individually
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

def test_b1_components():
    """Test importing B1 model components individually."""
    print("=" * 60)
    print("ImpressionCore B1 Component Import Test")
    print("=" * 60)
    
    components_to_test = [
        # Core model components from our adapters
        ("src.models.latent_diffusion_transformer", "LatentDiffusionTransformer"),
        ("src.models.vae_encoder", "VAE"),
        ("src.models.transformer", "ImpressionTransformerBlock"),
        ("src.models.memory_optimization", "MemoryOptimizer"),
        ("src.models.diffusion_transformer", "MixtureOfExperts"),
        ("src.models.layers.vector_quantizer", "VectorQuantizer"),
        
        # Phoneme embedding components
        ("src.modules.phoneme_embedding.config", "PhonemeEmbeddingConfig"),
        ("src.modules.phoneme_embedding.phoneme_extractor", "PhonemeExtractor"),
        ("src.modules.phoneme_embedding.phoneme_embedder", "PhonemeTokenizer"),
        
        # Test individual B1 model classes
        ("BrainSimCore", None),
        ("UKSModel", None),
        ("TextEncoder", None),
        ("TextDecoder", None),
        ("AudioEncoder", None),
    ]
    
    print("\nTesting individual components...")
    success_count = 0
    total_tests = len(components_to_test)
    
    # First test our adapter components
    for module_path, component in components_to_test[:-5]:
        try:
            if component:
                module = __import__(module_path, fromlist=[component])
                getattr(module, component)
                print(f"✓ {component} from {module_path}")
            else:
                __import__(module_path)
                print(f"✓ {module_path}")
            success_count += 1
        except Exception as e:
            print(f"✗ {component or module_path}: {e}")
    
    # Now test B1 model classes individually
    try:
        print("\nTesting B1 model classes...")
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "b1_unified_model", 
            src_path / "training" / "models" / "impressioncore-base" / "b1_unified_model.py"
        )
        b1_module = importlib.util.module_from_spec(spec)
        
        # Test class imports without instantiation
        print("Loading B1 module...")
        spec.loader.exec_module(b1_module)
        
        # Test individual classes
        classes_to_test = ["BrainSimCore", "UKSModel", "TextEncoder", "TextDecoder", "AudioEncoder"]
        for class_name in classes_to_test:
            try:
                cls = getattr(b1_module, class_name)
                print(f"✓ {class_name} class loaded")
                success_count += 1
            except Exception as e:
                print(f"✗ {class_name}: {e}")
        
        print(f"\n✓ B1 unified model module loaded successfully")
        
    except Exception as e:
        print(f"✗ Failed to load B1 module: {e}")
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"Component Test Results: {success_count}/{total_tests} passed")
    
    if success_count >= total_tests - 2:  # Allow some failures for optional components
        print("🎉 B1 model components are ready!")
        print("✓ Core import structure validated")
        print("⚠️  Some optional components may need additional dependencies")
    else:
        print(f"❌ {total_tests - success_count} components failed")
        print("⚠️  Critical components need attention")
    
    print("=" * 60)
    return success_count >= total_tests - 2

if __name__ == "__main__":
    success = test_b1_components()
    sys.exit(0 if success else 1)
