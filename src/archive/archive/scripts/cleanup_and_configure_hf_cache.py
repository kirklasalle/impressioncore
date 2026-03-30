"""
Cleanup HuggingFace Cache from C: Drive and Configure F: Drive Usage

This script:
1. Deletes HuggingFace cache from C: drive (freed up space)
2. Configures environment to use F: drive for all future downloads
3. Creates proper directory structure on F: drive

Created: October 8, 2025
Author: Kirk LaSalle; GitHub Copilot
"""

import os
import shutil
from pathlib import Path

# Define paths
C_CACHE_PATH = Path("C:/Users/kirkl/.cache/huggingface")
F_CACHE_PATH = Path("F:/huggingface_cache")
F_HUB_CACHE = F_CACHE_PATH / "hub"
F_DATASETS_CACHE = F_CACHE_PATH / "datasets"


def get_dir_size(path: Path) -> float:
    """Get directory size in GB."""
    if not path.exists():
        return 0.0

    total_size = 0
    try:
        for item in path.rglob('*'):
            if item.is_file():
                total_size += item.stat().st_size
    except Exception as e:
        print(f"   Warning: Could not calculate full size: {e}")

    return total_size / (1024 ** 3)  # Convert to GB


def delete_c_drive_cache():
    """Delete HuggingFace cache from C: drive."""
    print("\n" + "=" * 70)
    print("STEP 1: DELETE C: DRIVE CACHE")
    print("=" * 70)

    if not C_CACHE_PATH.exists():
        print("   ℹ️  No HuggingFace cache found on C: drive")
        return

    # Calculate size before deletion
    size_gb = get_dir_size(C_CACHE_PATH)
    print(f"\n📊 C: drive cache size: {size_gb:.2f} GB")

    # Confirm deletion
    print("\n⚠️  This will delete all HuggingFace cache from C: drive")
    print(f"   Location: {C_CACHE_PATH}")
    print(f"   Space to free: {size_gb:.2f} GB")

    confirm = input("\n❓ Proceed with deletion? (yes/no): ").lower().strip()

    if confirm != 'yes':
        print("   ❌ Deletion cancelled")
        return

    print("\n🗑️  Deleting C: drive cache...")
    try:
        shutil.rmtree(C_CACHE_PATH)
        print(f"   ✅ Deleted {size_gb:.2f} GB from C: drive")
    except Exception as e:
        print(f"   ❌ Error deleting cache: {e}")
        print("   💡 You may need to close programs using these files")


def create_f_drive_structure():
    """Create proper directory structure on F: drive."""
    print("\n" + "=" * 70)
    print("STEP 2: CREATE F: DRIVE STRUCTURE")
    print("=" * 70)

    directories = [
        F_CACHE_PATH,
        F_HUB_CACHE,
        F_DATASETS_CACHE,
    ]

    print("\n📁 Creating directories...")
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}")


def configure_environment():
    """Configure environment variables for F: drive usage."""
    print("\n" + "=" * 70)
    print("STEP 3: CONFIGURE ENVIRONMENT")
    print("=" * 70)

    # Set environment variables for current session
    os.environ['HF_HOME'] = str(F_CACHE_PATH)
    os.environ['HUGGINGFACE_HUB_CACHE'] = str(F_HUB_CACHE)
    os.environ['HF_DATASETS_CACHE'] = str(F_DATASETS_CACHE)

    print("\n✅ Environment variables set for current session:")
    print(f"   HF_HOME = {F_CACHE_PATH}")
    print(f"   HUGGINGFACE_HUB_CACHE = {F_HUB_CACHE}")
    print(f"   HF_DATASETS_CACHE = {F_DATASETS_CACHE}")

    print("\n📝 To make this permanent, add to your system:")
    print("\n   PowerShell (add to profile):")
    print(f'   $env:HF_HOME="{F_CACHE_PATH}"')
    print(f'   $env:HUGGINGFACE_HUB_CACHE="{F_HUB_CACHE}"')
    print(f'   $env:HF_DATASETS_CACHE="{F_DATASETS_CACHE}"')

    print("\n   Or use Windows System Environment Variables:")
    print("   1. Search 'Environment Variables' in Windows")
    print("   2. Add these variables under 'User variables'")


def create_batch_file():
    """Create batch file to set environment variables."""
    print("\n" + "=" * 70)
    print("STEP 4: CREATE SETUP SCRIPT")
    print("=" * 70)

    # Create PowerShell script
    ps_script = Path("setup_hf_cache_f_drive.ps1")
    ps_content = f"""# HuggingFace Cache Configuration for F: Drive
# Run this before running any HuggingFace downloads

$env:HF_HOME="{F_CACHE_PATH}"
$env:HUGGINGFACE_HUB_CACHE="{F_HUB_CACHE}"
$env:HF_DATASETS_CACHE="{F_DATASETS_CACHE}"

Write-Host "✅ HuggingFace cache configured to use F: drive" -ForegroundColor Green
Write-Host "   HF_HOME: $env:HF_HOME"
Write-Host "   HUGGINGFACE_HUB_CACHE: $env:HUGGINGFACE_HUB_CACHE"
Write-Host "   HF_DATASETS_CACHE: $env:HF_DATASETS_CACHE"
"""

    with open(ps_script, 'w') as f:
        f.write(ps_content)

    print(f"\n✅ Created: {ps_script}")
    print("\n   To use, run before any HuggingFace operations:")
    print(f"   . .\\{ps_script}")


def verify_configuration():
    """Verify the configuration is correct."""
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)

    print("\n✅ Configuration complete!")
    print("\n📊 Summary:")
    print(f"   C: drive cache: {'DELETED' if not C_CACHE_PATH.exists() else 'STILL EXISTS'}")
    print(f"   F: drive structure: {'CREATED' if F_CACHE_PATH.exists() else 'FAILED'}")
    print(f"   Environment: {'CONFIGURED' if 'HF_HOME' in os.environ else 'NOT SET'}")

    print("\n⚠️  IMPORTANT: Run setup script before training:")
    print("   . .\\setup_hf_cache_f_drive.ps1")
    print("   python run_option_a_pipeline.py")


def main():
    """Main execution."""
    print("=" * 70)
    print("HUGGINGFACE CACHE CLEANUP AND F: DRIVE CONFIGURATION")
    print("=" * 70)

    # Step 1: Delete C: drive cache
    delete_c_drive_cache()

    # Step 2: Create F: drive structure
    create_f_drive_structure()

    # Step 3: Configure environment
    configure_environment()

    # Step 4: Create setup script
    create_batch_file()

    # Verification
    verify_configuration()


if __name__ == "__main__":
    main()
