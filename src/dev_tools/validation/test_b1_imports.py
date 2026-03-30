#!/usr/bin/env python3
"""
B1 Model Import Validation Test

This script validates that all imports required by the B1 unified model
are properly available and can be imported without errors.

Created: 2025-01-06
Purpose: Verify import structure for ImpressionCore-B1 model integration
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

def test_import(module_path, component=None):
    """Test importing a module or component and report results."""
    try:
        if component:
            module = __import__(module_path, fromlist=[component])
            getattr(module, component)
            print(f"✓ Successfully imported {component} from {module_path}")
        else:
            __import__(module_path)
            print(f"✓ Successfully imported {module_path}")
        return True
    except Exception as e:
        print(f"✗ Failed to import {component or 'module'} from {module_path}: {e}")
        traceback.print_exc()
        return False

def validate_b1_imports():
    """Validate all imports required by the B1 unified model."""
    print("=" * 60)
    print("ImpressionCore B1 Model Import Validation")
    print("=" * 60)
    
    success_count = 0
    total_tests = 0
    
    # Core model imports from src.models
    imports_to_test = [
        ("src.models.latent_diffusion_transformer", "LatentDiffusionTransformer"),
        ("src.models.latent_diffusion_transformer", "TransformerConfig"),
        ("src.models.vae_encoder", "VAE"),
        ("src.models.memory_optimization", "MemoryOptimizer"),
        ("src.models.transformer", "ImpressionTransformerBlock"),
        ("src.models.diffusion_transformer", "MixtureOfExperts"),
        ("src.models.layers.vector_quantizer", "VectorQuantizer"),
    ]
    
    # Phoneme processing imports
    phoneme_imports = [
        ("src.modules.phoneme_embedding.config", "PhonemeEmbeddingConfig"),
        ("src.modules.phoneme_embedding.phoneme_extractor", "PhonemeExtractor"),
        ("src.modules.phoneme_embedding.phoneme_embedder", "PhonemeTokenizer"),
        ("src.modules.phoneme_embedding.phoneme_to_sound", "PhonemeToSoundSynthesizer"),
    ]
    
    imports_to_test.extend(phoneme_imports)
    
    print(f"\nTesting {len(imports_to_test)} imports...\n")
    
    for module_path, component in imports_to_test:
        total_tests += 1
        if test_import(module_path, component):
            success_count += 1
        print()  # Add spacing between tests
    
    # Test package-level imports
    package_tests = [
        "src.models",
        "src.modules.phoneme_embedding",
        "src.models.layers",
    ]
    
    print("Testing package-level imports...")
    for package in package_tests:
        total_tests += 1
        if test_import(package):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"Import Validation Results: {success_count}/{total_tests} passed")
    
    if success_count == total_tests:
        print("🎉 All imports validated successfully!")
        print("✓ B1 unified model import structure is ready")
    else:
        print(f"❌ {total_tests - success_count} import(s) failed")
        print("⚠️  Some components need attention before B1 model can run")
    
    print("=" * 60)
    return success_count == total_tests

if __name__ == "__main__":
    success = validate_b1_imports()
    sys.exit(0 if success else 1)
