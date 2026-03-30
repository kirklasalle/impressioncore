#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/dev_tools/pre_migration_audit.py #testing #training
**Category:** Development Tools
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src/dev_tools/pre_migration_audit.py #testing #training
# Category:** Development Tools
# Status:** Active

"""
ImpressionCore B1 - Pre-Migration Audit Report
==============================================

Generates detailed audit report of D: drive contents before migration
Sacred Covenant Compliance: File Integrity Assessment

Author: Virtually Robotic GitHub Copilot
Date: 2025-01-17
Version: 1.0
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Simplified logging for audit
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

class SimpleLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def info(self, msg):
        print(f"ℹ️  {msg}")
        self.logger.info(msg)

    def warning(self, msg):
        print(f"⚠️  {msg}")
        self.logger.warning(msg)

    def error(self, msg):
        print(f"❌ {msg}")
        self.logger.error(msg)

class PreMigrationAudit:
    """Pre-migration audit and reporting system"""

    def __init__(self):
        self.logger = SimpleLogger("PreMigration_Audit")

        self.d_drive_root = Path("D:/Projects/impressioncore")
        self.f_drive_root = Path("F:")

        # File patterns to identify real vs test data
        self.test_data_patterns = [
            "test_", "demo_", "sample_", "example_", "mock_",
            "dummy_", "fake_", "simulated_", "synthetic_"
        ]

        self.model_extensions = ['.pt', '.pth', '.bin', '.safetensors', '.ckpt']
        self.dataset_extensions = ['.json', '.jsonl', '.csv', '.tsv', '.txt', '.pkl']

    def is_real_data(self, file_path: Path) -> bool:
        """Determine if file contains real data vs test/demo data"""
        file_name = file_path.name.lower()

        # Check for test data patterns
        for pattern in self.test_data_patterns:
            if pattern in file_name:
                return False

        # Check file size - real models should be substantial
        if file_path.suffix.lower() in self.model_extensions:
            try:
                size_mb = file_path.stat().st_size / (1024 * 1024)
                if size_mb < 1.0:  # Less than 1MB is likely test data
                    return False
            except Exception:
                return False
          # Check for specific test directories
        return not any(part in str(file_path).lower() for part in ['test', 'demo', 'sample', 'example'])

    def scan_directory(self, directory: Path, category: str) -> dict:
        """Scan directory and categorize files"""
        results = {
            "directory": str(directory),
            "category": category,
            "total_files": 0,
            "real_data_files": 0,
            "test_data_files": 0,
            "total_size_bytes": 0,
            "real_data_size_bytes": 0,
            "files": []
        }

        if not directory.exists():
            self.logger.warning(f"Directory does not exist: {directory}")
            return results

        self.logger.info(f"📁 Scanning: {directory}")

        for file_path in directory.rglob("*"):
            if file_path.is_file():
                try:
                    size_bytes = file_path.stat().st_size
                    is_real = self.is_real_data(file_path)

                    file_info = {
                        "path": str(file_path),
                        "name": file_path.name,
                        "size_bytes": size_bytes,
                        "size_mb": round(size_bytes / (1024 * 1024), 2),
                        "extension": file_path.suffix.lower(),
                        "is_real_data": is_real,
                        "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    }

                    results["files"].append(file_info)
                    results["total_files"] += 1
                    results["total_size_bytes"] += size_bytes

                    if is_real:
                        results["real_data_files"] += 1
                        results["real_data_size_bytes"] += size_bytes
                    else:
                        results["test_data_files"] += 1

                except Exception as e:
                    self.logger.error(f"Error processing {file_path}: {e}")

        results["total_size_mb"] = round(results["total_size_bytes"] / (1024 * 1024), 2)
        results["real_data_size_mb"] = round(results["real_data_size_bytes"] / (1024 * 1024), 2)

        return results

    def check_f_drive_space(self) -> dict:
        """Check F: drive available space - Windows compatible method"""
        try:
            # Use shutil.disk_usage instead of os.statvfs for Windows compatibility
            total_bytes, used_bytes, free_bytes = shutil.disk_usage("F:/")

            return {
                "total_bytes": total_bytes,
                "used_bytes": used_bytes,
                "free_bytes": free_bytes,
                "total_gb": round(total_bytes / (1024**3), 2),
                "used_gb": round(used_bytes / (1024**3), 2),
                "free_gb": round(free_bytes / (1024**3), 2),
                "usage_percent": round((used_bytes / total_bytes) * 100, 2) if total_bytes > 0 else 0
            }
        except Exception as e:
            self.logger.error(f"Could not check F: drive space: {e}")
            return {"error": str(e)}

    def generate_audit_report(self) -> dict:
        """Generate comprehensive audit report"""
        self.logger.info("🔍 Starting pre-migration audit...")

        # Directories to audit
        audit_directories = [
            ("src/training/models", "trained_models"),
            ("src/training/datasets", "datasets"),
            ("exports", "exports"),
            ("src/data", "data"),
            ("src/training/checkpoints", "checkpoints"),
            ("src/training/outputs", "outputs")
        ]

        audit_report = {
            "audit_timestamp": datetime.now().isoformat(),
            "d_drive_root": str(self.d_drive_root),
            "f_drive_root": str(self.f_drive_root),
            "directory_scans": [],
            "summary": {
                "total_directories": 0,
                "total_files": 0,
                "real_data_files": 0,
                "test_data_files": 0,
                "total_size_bytes": 0,
                "real_data_size_bytes": 0
            },
            "f_drive_space": self.check_f_drive_space(),
            "migration_recommendation": ""
        }

        # Scan each directory
        for dir_path, category in audit_directories:
            full_path = self.d_drive_root / dir_path
            scan_result = self.scan_directory(full_path, category)
            audit_report["directory_scans"].append(scan_result)

            # Update summary
            audit_report["summary"]["total_directories"] += 1
            audit_report["summary"]["total_files"] += scan_result["total_files"]
            audit_report["summary"]["real_data_files"] += scan_result["real_data_files"]
            audit_report["summary"]["test_data_files"] += scan_result["test_data_files"]
            audit_report["summary"]["total_size_bytes"] += scan_result["total_size_bytes"]
            audit_report["summary"]["real_data_size_bytes"] += scan_result["real_data_size_bytes"]

        # Convert bytes to GB for summary
        audit_report["summary"]["total_size_gb"] = round(audit_report["summary"]["total_size_bytes"] / (1024**3), 2)
        audit_report["summary"]["real_data_size_gb"] = round(audit_report["summary"]["real_data_size_bytes"] / (1024**3), 2)

        # Generate recommendation
        if audit_report["f_drive_space"].get("free_gb", 0) > audit_report["summary"]["real_data_size_gb"] * 1.5:
            audit_report["migration_recommendation"] = "PROCEED - Sufficient F: drive space available"
        else:
            audit_report["migration_recommendation"] = "CAUTION - Limited F: drive space, consider cleanup first"

        return audit_report

    def save_audit_report(self, audit_report: dict) -> Path:
        """Save audit report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.d_drive_root / "src" / "memlog" / f"pre_migration_audit_{timestamp}.json"

        # Ensure memlog directory exists
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(audit_report, f, indent=2)

        self.logger.info(f"📋 Audit report saved: {report_path}")
        return report_path

    def print_audit_summary(self, audit_report: dict):
        """Print formatted audit summary"""
        print("\n" + "="*60)
        print("📊 PRE-MIGRATION AUDIT SUMMARY")
        print("="*60)

        summary = audit_report["summary"]
        print(f"📁 Total directories scanned: {summary['total_directories']}")
        print(f"📄 Total files found: {summary['total_files']}")
        print(f"✅ Real data files: {summary['real_data_files']}")
        print(f"🧪 Test data files: {summary['test_data_files']}")
        print(f"💾 Total size: {summary['total_size_gb']} GB")
        print(f"📦 Real data size: {summary['real_data_size_gb']} GB")

        print("\n💿 F: DRIVE SPACE:")
        f_space = audit_report["f_drive_space"]
        if "error" not in f_space:
            print(f"  Total: {f_space['total_gb']} GB")
            print(f"  Used: {f_space['used_gb']} GB ({f_space['usage_percent']}%)")
            print(f"  Free: {f_space['free_gb']} GB")
        else:
            print(f"  Error: {f_space['error']}")

        print(f"\n🎯 RECOMMENDATION: {audit_report['migration_recommendation']}")

        print("\n📋 DIRECTORY BREAKDOWN:")
        for scan in audit_report["directory_scans"]:
            if scan["total_files"] > 0:
                print(f"  {scan['category']}: {scan['real_data_files']} real files ({scan['real_data_size_mb']} MB)")

        print("="*60)

    def run_audit(self):
        """Run complete audit process"""
        try:
            audit_report = self.generate_audit_report()
            report_path = self.save_audit_report(audit_report)
            self.print_audit_summary(audit_report)

            self.logger.info("✅ Pre-migration audit completed successfully")
            return audit_report, report_path

        except Exception as e:
            self.logger.error(f"❌ Audit failed: {e}")
            return None, None

def main():
    """Main execution function"""
    audit = PreMigrationAudit()
    audit_report, report_path = audit.run_audit()

    if audit_report:
        print(f"\n📋 Full audit report saved to: {report_path}")
        print("Review the report before proceeding with migration.")
        return 0
    else:
        print("\n❌ Audit failed!")
        return 1

if __name__ == "__main__":
    exit(main())
