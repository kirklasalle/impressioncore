#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #deployment #documentation #python #source_code #src/dev_tools/batch_d_to_f_drive_migration.py #testing #training
**Category:** Development Tools
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #deployment #documentation #python #source_code #src\\dev_tools\\batch_d_to_f_drive_migration.py #testing #training
# Category:** Development Tools
# Status:** Active

"""
ImpressionCore B1 - Batch D: to F: Drive Migration Script
=======================================================

Sacred Covenant Compliance: File Integrity Protection
- Comprehensive audit of all models, datasets, and training outputs
- Batch move operations with verification and logging
- Configuration update automation
- Complete compliance reporting

Author: Virtually Robotic GitHub Copilot
Date: 2025-01-17
Version: 1.0
"""

import hashlib
import json
import logging
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from .core.utils.rich_enhancements import RichEnhancementManager
from .core.utils.rich_logging import RichLogger
from .core.utils.rich_status_animation import RichStatusAnimation


@dataclass
class FileAuditResult:
    """Data class for file audit results"""
    file_path: str
    size_bytes: int
    file_type: str
    is_real_data: bool
    target_f_drive_path: str
    md5_hash: str
    last_modified: str
    file_category: str  # 'model', 'dataset', 'export', 'config', 'other'

@dataclass
class MigrationPlan:
    """Migration plan with batch operations"""
    total_files: int
    total_size_bytes: int
    batches: list[list[FileAuditResult]]
    config_files_to_update: list[str]
    estimated_duration_minutes: int

class ImpressionCoreD2FMigration:
    """Comprehensive D: to F: drive migration system"""

    def __init__(self):
        self.rich_manager = RichEnhancementManager()
        self.logger = RichLogger("D2F_Migration", level=logging.INFO)
        self.status = RichStatusAnimation()

        # Drive paths
        self.d_drive_root = Path("D:/Projects/impressioncore")
        self.f_drive_root = Path("F:")

        # Sacred Covenant F: drive structure
        self.f_drive_structure = {
            "models": "F:/models",
            "datasets": "F:/datasets",
            "exports": "F:/exports",
            "embeddings": "F:/embeddings",  # Already exists
            "backups": "F:/backups",
            "configs": "F:/configs",
            "logs": "F:/logs"
        }

        # File patterns to identify real vs test data
        self.test_data_patterns = [
            "test_", "demo_", "sample_", "example_", "mock_",
            "dummy_", "fake_", "simulated_", "synthetic_"
        ]

        # File extensions to process
        self.model_extensions = ['.pt', '.pth', '.bin', '.safetensors', '.ckpt']
        self.dataset_extensions = ['.json', '.jsonl', '.csv', '.tsv', '.txt', '.pkl']
        self.config_extensions = ['.yaml', '.yml', '.json', '.toml', '.ini']

        # Migration log
        self.migration_log = []
        self.compliance_report = {}

    def get_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file for verification"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.error(f"Failed to hash {file_path}: {e}")
            return ""

    def is_real_data(self, file_path: Path) -> bool:
        """Determine if file contains real data vs test/demo data"""
        file_name = file_path.name.lower()

        # Check for test data patterns
        for pattern in self.test_data_patterns:
            if pattern in file_name:
                return False

        # Check file size - real models should be substantial
        if file_path.suffix.lower() in self.model_extensions:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            if size_mb < 1.0:  # Less than 1MB is likely test data
                return False

        # Check for specific test directories
        return not any(part in str(file_path).lower() for part in ['test', 'demo', 'sample', 'example'])

    def categorize_file(self, file_path: Path) -> str:
        """Categorize file type"""
        if file_path.suffix.lower() in self.model_extensions:
            return "model"
        elif file_path.suffix.lower() in self.dataset_extensions:
            return "dataset"
        elif file_path.suffix.lower() in self.config_extensions:
            return "config"
        elif "export" in str(file_path).lower():
            return "export"
        else:
            return "other"

    def get_target_f_drive_path(self, file_path: Path, category: str) -> str:
        """Determine target F: drive path based on file category"""
        relative_path = file_path.relative_to(self.d_drive_root)

        if category == "model":  # noqa: SIM116
            return f"F:/models/{relative_path}"
        elif category == "dataset":
            return f"F:/datasets/{relative_path}"
        elif category == "export":
            return f"F:/exports/{relative_path}"
        elif category == "config":
            return f"F:/configs/{relative_path}"
        else:
            return f"F:/data/{relative_path}"

    def audit_d_drive(self) -> list[FileAuditResult]:
        """Comprehensive audit of D: drive files"""
        self.logger.info("🔍 Starting comprehensive D: drive audit...")

        audit_results = []

        # Directories to audit
        audit_dirs = [
            "src/training/models",
            "src/training/datasets",
            "exports",
            "src/data",
            "src/training/checkpoints",
            "src/training/outputs"
        ]

        with self.status.create_context("Auditing D: drive files..."):
            for audit_dir in audit_dirs:
                dir_path = self.d_drive_root / audit_dir
                if not dir_path.exists():
                    continue

                self.logger.info(f"📁 Auditing directory: {audit_dir}")

                for file_path in dir_path.rglob("*"):
                    if file_path.is_file():
                        try:
                            size_bytes = file_path.stat().st_size
                            file_type = file_path.suffix.lower()
                            is_real = self.is_real_data(file_path)
                            category = self.categorize_file(file_path)
                            target_path = self.get_target_f_drive_path(file_path, category)
                            file_hash = self.get_file_hash(file_path) if is_real else ""
                            last_modified = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()

                            audit_result = FileAuditResult(
                                file_path=str(file_path),
                                size_bytes=size_bytes,
                                file_type=file_type,
                                is_real_data=is_real,
                                target_f_drive_path=target_path,
                                md5_hash=file_hash,
                                last_modified=last_modified,
                                file_category=category
                            )

                            audit_results.append(audit_result)

                        except Exception as e:
                            self.logger.error(f"Error auditing {file_path}: {e}")

        self.logger.info(f"✅ Audit complete: {len(audit_results)} files found")
        return audit_results

    def create_migration_plan(self, audit_results: list[FileAuditResult]) -> MigrationPlan:
        """Create migration plan with batching"""
        self.logger.info("📋 Creating migration plan...")

        # Filter for real data only
        real_files = [result for result in audit_results if result.is_real_data]

        total_files = len(real_files)
        total_size_bytes = sum(result.size_bytes for result in real_files)

        # Create batches (max 100 files per batch or 1GB)
        batches = []
        current_batch = []
        current_batch_size = 0
        max_batch_size = 1024 * 1024 * 1024  # 1GB
        max_batch_files = 100

        for file_result in real_files:
            if (len(current_batch) >= max_batch_files or
                current_batch_size + file_result.size_bytes > max_batch_size) and current_batch:
                batches.append(current_batch)
                current_batch = []
                current_batch_size = 0

            current_batch.append(file_result)
            current_batch_size += file_result.size_bytes

        if current_batch:
            batches.append(current_batch)

        # Estimate duration (1 second per file + 1MB/s transfer)
        estimated_duration = total_files + (total_size_bytes / (1024 * 1024))
        estimated_duration_minutes = int(estimated_duration / 60) + 1

        # Find config files to update
        config_files = self.find_config_files_to_update()

        plan = MigrationPlan(
            total_files=total_files,
            total_size_bytes=total_size_bytes,
            batches=batches,
            config_files_to_update=config_files,
            estimated_duration_minutes=estimated_duration_minutes
        )

        self.logger.info("📊 Migration plan created:")
        self.logger.info(f"  - Total files: {total_files}")
        self.logger.info(f"  - Total size: {total_size_bytes / (1024**3):.2f} GB")
        self.logger.info(f"  - Batches: {len(batches)}")
        self.logger.info(f"  - Estimated duration: {estimated_duration_minutes} minutes")

        return plan

    def find_config_files_to_update(self) -> list[str]:
        """Find configuration files that need path updates"""
        config_files = []

        # Search for config files with D: drive references
        for config_file in self.d_drive_root.rglob("*.py"):
            try:
                with open(config_file, encoding='utf-8') as f:
                    content = f.read()
                    if 'D:/Projects/impressioncore' in content or 'D:\\Projects\\impressioncore' in content:
                        config_files.append(str(config_file))
            except Exception:
                continue

        for config_file in self.d_drive_root.rglob("*.yaml"):
            try:
                with open(config_file, encoding='utf-8') as f:
                    content = f.read()
                    if 'D:/Projects/impressioncore' in content or 'D:\\Projects\\impressioncore' in content:
                        config_files.append(str(config_file))
            except Exception:
                continue

        return config_files

    def create_f_drive_structure(self):
        """Create F: drive directory structure"""
        self.logger.info("📁 Creating F: drive directory structure...")

        for _category, path in self.f_drive_structure.items():
            Path(path).mkdir(parents=True, exist_ok=True)
            self.logger.info(f"  ✅ Created: {path}")

    def create_backup(self):
        """Create backup before migration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"pre_migration_backup_{timestamp}"
        backup_path = self.d_drive_root / "backup" / backup_name

        self.logger.info(f"💾 Creating backup: {backup_name}")

        # Create backup directory
        backup_path.mkdir(parents=True, exist_ok=True)

        # Copy critical files
        critical_files = [
            "src/training/impressioncore_b1_ultimate_trainer.py",
            "src/deployment/launch_b1_ultimate_trainer.py",
            "docs/DOCUMENTATION_INDEX.md"
        ]

        for file_path in critical_files:
            source = self.d_drive_root / file_path
            if source.exists():
                target = backup_path / file_path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)

        self.logger.info(f"✅ Backup created: {backup_path}")
        return backup_path

    def execute_migration(self, plan: MigrationPlan) -> bool:
        """Execute the migration plan"""
        self.logger.info("🚀 Starting migration execution...")

        # Create F: drive structure
        self.create_f_drive_structure()

        # Create backup
        self.create_backup()

        # Execute batches
        total_batches = len(plan.batches)
        successful_moves = 0
        failed_moves = 0

        for batch_idx, batch in enumerate(plan.batches):
            self.logger.info(f"📦 Processing batch {batch_idx + 1}/{total_batches} ({len(batch)} files)")

            with self.status.create_context(f"Processing batch {batch_idx + 1}/{total_batches}..."):
                for file_result in batch:
                    try:
                        source_path = Path(file_result.file_path)
                        target_path = Path(file_result.target_f_drive_path)

                        # Create target directory
                        target_path.parent.mkdir(parents=True, exist_ok=True)

                        # Move file
                        shutil.move(str(source_path), str(target_path))

                        # Verify move
                        if target_path.exists():
                            target_hash = self.get_file_hash(target_path)
                            if target_hash == file_result.md5_hash:
                                successful_moves += 1
                                self.migration_log.append({
                                    "status": "SUCCESS",
                                    "source": str(source_path),
                                    "target": str(target_path),
                                    "size": file_result.size_bytes,
                                    "hash_verified": True,
                                    "timestamp": datetime.now().isoformat()
                                })
                            else:
                                failed_moves += 1
                                self.logger.error(f"Hash mismatch for {target_path}")
                        else:
                            failed_moves += 1
                            self.logger.error(f"Failed to move {source_path}")

                    except Exception as e:
                        failed_moves += 1
                        self.logger.error(f"Error moving {file_result.file_path}: {e}")
                        self.migration_log.append({
                            "status": "FAILED",
                            "source": file_result.file_path,
                            "error": str(e),
                            "timestamp": datetime.now().isoformat()
                        })

        self.logger.info("📊 Migration complete:")
        self.logger.info(f"  - Successful: {successful_moves}")
        self.logger.info(f"  - Failed: {failed_moves}")

        return failed_moves == 0

    def update_config_files(self, config_files: list[str]):
        """Update configuration files with new F: drive paths"""
        self.logger.info("⚙️ Updating configuration files...")

        for config_file in config_files:
            try:
                with open(config_file, encoding='utf-8') as f:
                    content = f.read()

                # Replace D: drive paths with F: drive paths
                updated_content = content.replace(
                    'D:/Projects/impressioncore/src/training/models',
                    'F:/models'
                ).replace(
                    'D:/Projects/impressioncore/exports',
                    'F:/exports'
                ).replace(
                    'D:\\Projects\\impressioncore\\src\\training\\models',
                    'F:\\models'
                ).replace(
                    'D:\\Projects\\impressioncore\\exports',
                    'F:\\exports'
                )

                if updated_content != content:
                    with open(config_file, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    self.logger.info(f"  ✅ Updated: {config_file}")

            except Exception as e:
                self.logger.error(f"Failed to update {config_file}: {e}")

    def generate_compliance_report(self):
        """Generate Sacred Covenant compliance report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.d_drive_root / "src" / "memlog" / f"d2f_migration_compliance_report_{timestamp}.json"

        self.compliance_report = {
            "migration_timestamp": timestamp,
            "sacred_covenant_compliance": {
                "file_integrity_verified": True,
                "backup_created": True,
                "logging_complete": True,
                "verification_performed": True
            },
            "migration_statistics": {
                "total_files_processed": len(self.migration_log),
                "successful_moves": len([log for log in self.migration_log if log["status"] == "SUCCESS"]),
                "failed_moves": len([log for log in self.migration_log if log["status"] == "FAILED"]),
                "total_size_bytes": sum(log.get("size", 0) for log in self.migration_log if log["status"] == "SUCCESS")
            },
            "f_drive_structure": self.f_drive_structure,
            "migration_log": self.migration_log
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.compliance_report, f, indent=2)

        self.logger.info(f"📋 Compliance report generated: {report_path}")
        return report_path

    def run_full_migration(self):
        """Run complete migration process"""
        self.logger.info("🚀 STARTING FULL D: TO F: DRIVE MIGRATION")
        self.logger.info("Sacred Covenant File Integrity Protection ACTIVE")

        try:
            # Phase 1: Audit
            audit_results = self.audit_d_drive()

            # Phase 2: Plan
            migration_plan = self.create_migration_plan(audit_results)

            # Phase 3: Execute
            success = self.execute_migration(migration_plan)

            if success:
                # Phase 4: Update configs
                self.update_config_files(migration_plan.config_files_to_update)

                # Phase 5: Generate compliance report
                self.generate_compliance_report()

                self.logger.info("✅ MIGRATION COMPLETED SUCCESSFULLY")
                self.logger.info("Sacred Covenant compliance maintained")
                return True
            else:
                self.logger.error("❌ MIGRATION FAILED - Check logs for details")
                return False

        except Exception as e:
            self.logger.error(f"❌ MIGRATION FAILED: {e}")
            return False

def main():
    """Main execution function"""
    migration = ImpressionCoreD2FMigration()
    success = migration.run_full_migration()

    if success:
        print("\n✅ Migration completed successfully!")
        print("All real models, datasets, and outputs moved to F: drive")
        print("Sacred Covenant compliance maintained")
    else:
        print("\n❌ Migration failed!")
        print("Check logs for details")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
