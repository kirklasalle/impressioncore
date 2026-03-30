#!/usr/bin/env python3
"""
Test Script to Verify 400% Scaled Dataset Usage
==============================================

This script tests that the training system is correctly using the new 400% scaled datasets.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_datasets():
    """Check which datasets are available and their sizes."""
    
    print("🔍 Checking Dataset Availability")
    print("=" * 50)
    
    # Check 400% scaled datasets (priority)
    scaled_path = project_root / "src/data/real_datasets/synthetic_scaled"
    if scaled_path.exists():
        print("✅ 400% Scaled Datasets Found:")
        
        text_count = len(list((scaled_path / "text_samples").glob("*.txt"))) if (scaled_path / "text_samples").exists() else 0
        image_count = len(list((scaled_path / "images").glob("*.jpg"))) if (scaled_path / "images").exists() else 0 
        audio_count = len(list((scaled_path / "audio").glob("*.wav"))) if (scaled_path / "audio").exists() else 0
        
        print(f"  📝 Text: {text_count} samples")
        print(f"  🖼️  Images: {image_count} samples")
        print(f"  🎵 Audio: {audio_count} samples")
        print(f"  🎯 Total: {text_count + image_count + audio_count} samples")
        
        if text_count >= 40 and image_count >= 40 and audio_count >= 40:
            print("🎉 SUCCESS: All modalities have 40+ samples (400% scaling achieved!)")
            return True
        else:
            print("⚠️  WARNING: Some modalities have fewer than 40 samples")
    else:
        print("❌ 400% Scaled Datasets NOT FOUND")
    
    # Check original minimal datasets (fallback)
    minimal_path = project_root / "src/data/minimal_datasets"
    if minimal_path.exists():
        print("\n📦 Original Minimal Datasets Found:")
        
        text_count = len(list((minimal_path / "text_samples").glob("*.txt"))) if (minimal_path / "text_samples").exists() else 0
        image_count = len(list((minimal_path / "images").glob("*.jpg"))) if (minimal_path / "images").exists() else 0
        audio_count = len(list((minimal_path / "audio").glob("*.wav"))) if (minimal_path / "audio").exists() else 0
        
        print(f"  📝 Text: {text_count} samples")
        print(f"  🖼️  Images: {image_count} samples") 
        print(f"  🎵 Audio: {audio_count} samples")
    else:
        print("\n❌ Original Minimal Datasets NOT FOUND")
    
    return False

def test_training_with_scaled_datasets():
    """Test training with the 400% scaled datasets."""
    
    print("\n🧪 Testing Training with 400% Scaled Datasets")
    print("=" * 50)
    
    try:        # Import the launcher
        from bulletproof_training_launcher import ProductionTrainingLauncher
        
        launcher = ProductionTrainingLauncher()
        datasets = launcher.discover_datasets()
        
        print("🔍 Discovered Datasets:")
        for key, value in datasets.items():
            print(f"  {key}: {value}")
          # Check if 400% scaled datasets are being used
        scaled_path_str = "synthetic_scaled"  # Simple substring check
        
        is_using_scaled = any(scaled_path_str in str(path) for path in datasets.values() if isinstance(path, str))
        
        if is_using_scaled:
            print("\n✅ SUCCESS: Training system is using 400% scaled datasets!")
            return True
        else:
            print(f"\n⚠️  WARNING: Training system is NOT using 400% scaled datasets")
            print("    Checking paths:")
            for key, value in datasets.items():
                print(f"      {key}: {value}")
            print(f"    Looking for: {scaled_path_str}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR testing training system: {e}")
        return False

def main():
    """Main test execution."""
    
    print("🚀 ImpressionCore-B1 400% Dataset Scaling Test")
    print("=" * 60)
    
    # Test 1: Check dataset availability
    datasets_available = check_datasets()
    
    # Test 2: Test training system usage
    training_using_scaled = test_training_with_scaled_datasets()
    
    # Final assessment
    print("\n📊 Final Assessment")
    print("=" * 30)
    
    if datasets_available and training_using_scaled:
        print("🎉 COMPLETE SUCCESS: 400% dataset scaling is working perfectly!")
        print("   ✅ 40+ samples per modality available")
        print("   ✅ Training system using scaled datasets")
        print("   🚀 Ready for production training with 400% more data!")
    elif datasets_available:
        print("🔶 PARTIAL SUCCESS: Datasets available but training needs configuration")
        print("   ✅ 40+ samples per modality available")
        print("   ⚠️  Training system needs update to use scaled datasets")
    else:
        print("❌ NEEDS WORK: Dataset scaling not complete")
        print("   ❌ Missing 40+ samples per modality")
        print("   ❌ Training system cannot use scaled datasets")
    
    print(f"\n🎯 Next Steps:")
    if not datasets_available:
        print("   1. Run: python src/data/real_world_dataset_manager.py")
        print("   2. Verify dataset generation completed successfully")
    if not training_using_scaled:
        print("   3. Update training launcher to prioritize scaled datasets")
        print("   4. Test training with: python bulletproof_training_launcher.py --epochs 1")

if __name__ == "__main__":
    main()
