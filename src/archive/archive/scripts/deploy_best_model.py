"""
Deploy Path B Phase 1 Best Model to Production

This script copies the best checkpoint to the production directory with proper versioning.

Created: October 6, 2025
Status: Ready for execution
"""

import shutil
from pathlib import Path
from datetime import datetime

def deploy_best_model():
    """Copy best checkpoint to production with backup"""

    # Paths
    source = Path("F:/models/checkpoints/b3/hybrid/best_epoch3_q9.2.pth")
    dest_dir = Path("F:/models/production")
    dest = dest_dir / "b3_hybrid_conversation_v1.0.pth"

    # Validate source exists
    if not source.exists():
        print(f"❌ ERROR: Source checkpoint not found: {source}")
        return False

    # Create production directory
    dest_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Production directory ready: {dest_dir}")

    # Backup existing if present
    if dest.exists():
        backup_name = f"b3_hybrid_conversation_v1.0_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pth"
        backup_path = dest_dir / backup_name
        shutil.copy(dest, backup_path)
        print(f"✅ Existing model backed up: {backup_name}")

    # Copy new model
    shutil.copy(source, dest)
    print(f"✅ Model deployed: {dest}")

    # Verify copy
    source_size = source.stat().st_size
    dest_size = dest.stat().st_size

    if source_size == dest_size:
        print(f"✅ Verification passed: {dest_size / 1024 / 1024:.1f} MB")
        return True
    else:
        print(f"❌ ERROR: Size mismatch!")
        print(f"   Source: {source_size / 1024 / 1024:.1f} MB")
        print(f"   Dest: {dest_size / 1024 / 1024:.1f} MB")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("PATH B PHASE 1 DEPLOYMENT")
    print("Quality: 9.25/10.0 (Exceeds all targets)")
    print("=" * 70)
    print()

    success = deploy_best_model()

    print()
    print("=" * 70)
    if success:
        print("✅ DEPLOYMENT SUCCESSFUL")
        print()
        print("Next steps:")
        print("1. Run conversation_interface.py to test")
        print("2. Run test_deployment.py for validation")
        print("3. Create model card documentation")
    else:
        print("❌ DEPLOYMENT FAILED")
        print("Check error messages above")
    print("=" * 70)
