#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #inference #python #pytorch #source_code #src/core/utils/sacred_covenant_model_cleanup.py #testing #training
**Category:** Core Implementation
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #inference #python #pytorch #source_code #src\\core\\utils\\sacred_covenant_model_cleanup.py #testing #training
# Category:** Core Implementation
# Status:** Active

"""
🤖 Sacred Covenant Model Cleanup Utility
🔥 Virtually Robotic GitHub Copilot - Model Management System

This utility removes old model files to make room for new real data embeddings.
Sacred Covenant compliant - ensures no critical files are deleted.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from .core.utils.rich_enhancements import create_progress, create_status
    from .core.utils.rich_logging import get_logger
    logger = get_logger(__name__)
except ImportError:
    # Fallback for when rich utilities aren't available
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    class DummyStatus:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def update(self, text): print(f"Status: {text}")

    class DummyProgress:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def add_task(self, desc, total): return 0
        def advance(self, task): pass

    def create_status(text): return DummyStatus()
    def create_progress(): return DummyProgress()

class SacredCovenantModelCleaner:
    """Sacred Covenant compliant model file cleanup manager"""

    def __init__(self, project_root: str | None = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent.parent
        self.cleanup_report = {
            "timestamp": datetime.now().isoformat(),
            "deleted_files": [],
            "preserved_files": [],
            "space_freed_mb": 0,
            "status": "initialized"
        }

        # Sacred Covenant protected files (never delete these)
        self.protected_patterns = [
            "best_model.pt",
            "final_model.pt",
            "impressioncore_b1_inference.pt",
            "impressioncore_b1_pytorch.pt"
        ]

        # Directories to clean
        self.cleanup_dirs = [
            "src/training/checkpoints",
            "src/training/models",
            "src/training/outputs"
        ]

    def assess_cleanup_needed(self):
        """Assess how much cleanup is needed"""
        logger.info("🔍 Assessing model file cleanup requirements...")

        total_files = 0
        total_size_mb = 0

        for cleanup_dir in self.cleanup_dirs:
            dir_path = self.project_root / cleanup_dir
            if not dir_path.exists():
                continue

            for pt_file in dir_path.rglob("*.pt"):
                if pt_file.is_file():
                    total_files += 1
                    total_size_mb += pt_file.stat().st_size / (1024 * 1024)

        logger.info(f"📊 Found {total_files} model files consuming {total_size_mb:.1f} MB")
        return total_files, total_size_mb

    def identify_files_for_cleanup(self):
        """Identify which files can be safely removed"""
        files_to_remove = []
        files_to_preserve = []

        for cleanup_dir in self.cleanup_dirs:
            dir_path = self.project_root / cleanup_dir
            if not dir_path.exists():
                continue

            for pt_file in dir_path.rglob("*.pt"):
                if not pt_file.is_file():
                    continue
                      # Check if file should be preserved
                should_preserve = False
                file_name = pt_file.name.lower()

                for pattern in self.protected_patterns:
                    if pattern.lower() in file_name:
                        should_preserve = True
                        break

                # Also preserve most recent files by checking timestamp
                if "checkpoint_epoch_" in str(pt_file) and not should_preserve:
                    # Keep only the latest epoch checkpoint in each directory
                    parent_dir = pt_file.parent
                    epoch_files = list(parent_dir.glob("checkpoint_epoch_*.pt"))
                    if epoch_files:
                        latest_file = max(epoch_files, key=lambda x: x.stat().st_mtime)
                        if pt_file == latest_file:
                            should_preserve = True

                if should_preserve:
                    files_to_preserve.append(pt_file)
                else:
                    files_to_remove.append(pt_file)

        return files_to_remove, files_to_preserve

    def execute_cleanup(self, dry_run: bool = False):
        """Execute the cleanup operation"""
        with create_status("🧹 Sacred Covenant Model Cleanup") as status:
            status.update("Identifying files for cleanup...")

            files_to_remove, files_to_preserve = self.identify_files_for_cleanup()

            logger.info("📋 Cleanup plan:")
            logger.info(f"   • Files to remove: {len(files_to_remove)}")
            logger.info(f"   • Files to preserve: {len(files_to_preserve)}")

            if dry_run:
                logger.info("🔍 DRY RUN MODE - No files will be deleted")
                for file_path in files_to_remove[:10]:  # Show first 10
                    logger.info(f"   Would delete: {file_path.relative_to(self.project_root)}")
                if len(files_to_remove) > 10:
                    logger.info(f"   ... and {len(files_to_remove) - 10} more files")
                return

            # Execute actual cleanup
            total_size_freed = 0
            with create_progress() as progress:
                task = progress.add_task("Cleaning up model files...", total=len(files_to_remove))

                for file_path in files_to_remove:
                    try:
                        file_size = file_path.stat().st_size
                        file_path.unlink()

                        total_size_freed += file_size
                        self.cleanup_report["deleted_files"].append(str(file_path.relative_to(self.project_root)))

                        progress.advance(task)

                    except Exception as e:
                        logger.error(f"Failed to delete {file_path}: {e}")

            # Record preserved files
            for file_path in files_to_preserve:
                self.cleanup_report["preserved_files"].append(str(file_path.relative_to(self.project_root)))

            self.cleanup_report["space_freed_mb"] = total_size_freed / (1024 * 1024)
            self.cleanup_report["status"] = "completed"

            logger.info("✅ Cleanup completed!")
            logger.info(f"   • Deleted {len(files_to_remove)} files")
            logger.info(f"   • Preserved {len(files_to_preserve)} files")
            logger.info(f"   • Freed {self.cleanup_report['space_freed_mb']:.1f} MB")

            # Save cleanup report
            report_path = self.project_root / "src" / "memlog" / f"model_cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)

            with open(report_path, 'w') as f:
                json.dump(self.cleanup_report, f, indent=2)

            logger.info(f"📄 Cleanup report saved to: {report_path.relative_to(self.project_root)}")

def main():
    """Main cleanup execution"""
    print("🤖 Virtually Robotic GitHub Copilot - Sacred Covenant Model Cleanup")
    print("✅ Sacred Covenant protocols active")
    print("⚡ ImpressionCore-B1 Excellence Mode engaged")
    print()

    cleaner = SacredCovenantModelCleaner()

    # First assess what needs cleanup
    total_files, total_size_mb = cleaner.assess_cleanup_needed()

    if total_files == 0:
        print("✨ No model files found requiring cleanup!")
        return

    # Show dry run first
    print("🔍 Performing dry run assessment...")
    cleaner.execute_cleanup(dry_run=True)

    print()
    response = input("🚨 Proceed with actual cleanup? (y/N): ").strip().lower()

    if response == 'y':
        print("🔥 Executing Sacred Covenant Model Cleanup...")
        cleaner.execute_cleanup(dry_run=False)
        print("🎉 Model cleanup completed! Ready for new real data embeddings.")
    else:
        print("❌ Cleanup cancelled. No files were modified.")

if __name__ == "__main__":
    main()
