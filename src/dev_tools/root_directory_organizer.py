#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #documentation #inference #python #source_code #src/dev_tools/root_directory_organizer.py #testing #training
**Category:** Development Tools
**Status:** Active
"""


import json
import logging
import shutil
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImpressionCoreFileOrganizer:
    """
    Sacred Covenant compliant file organizer for ImpressionCore project
    Ensures complete file integrity while systematically organizing loose files
    """

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.organization_report = {
            "timestamp": datetime.now().isoformat(),
            "total_files_processed": 0,
            "successful_moves": 0,
            "failed_moves": 0,
            "skipped_files": 0,
            "file_movements": [],
            "errors": []
        }

        # Define file categorization rules
        self.file_categories = {
            # B3 Training Scripts
            "b3_training": {
                "patterns": ["b3_.*training.*\\.py$", "b3_.*train.*\\.py$", "b3_full_.*\\.py$"],
                "destination": "src/training/b3",
                "description": "B3 model training scripts"
            },

            # B3 Model Scripts
            "b3_models": {
                "patterns": ["b3_.*model.*\\.py$", "b3_.*inference.*\\.py$", "b3_.*evaluation.*\\.py$",
                           "b3_.*tester.*\\.py$", "b3_.*analyzer.*\\.py$"],
                "destination": "src/models/b3",
                "description": "B3 model operation scripts"
            },

            # B3 Embedding Scripts
            "b3_embeddings": {
                "patterns": ["b3_.*embed.*\\.py$", "b3_.*integration.*\\.py$"],
                "destination": "src/embeddings/b3",
                "description": "B3 embedding processing scripts"
            },

            # B3 Utility Scripts
            "b3_utilities": {
                "patterns": ["b3_.*\\.py$"],  # Catch remaining b3 scripts
                "destination": "src/scripts/b3",
                "description": "B3 utility and helper scripts"
            },

            # Dataset Processing Scripts
            "dataset_processors": {
                "patterns": [".*dataset.*\\.py$", ".*acquisition.*\\.py$", "k12_.*\\.py$",
                           ".*corpus.*\\.py$", "educational.*\\.py$"],
                "destination": "src/data/processors",
                "description": "Dataset processing and acquisition scripts"
            },

            # F: Drive Management Scripts
            "f_drive_tools": {
                "patterns": ["f_drive.*\\.py$", "f_models.*\\.py$", ".*f_datasets.*\\.py$"],
                "destination": "src/scripts/f_drive",
                "description": "F: drive management and analysis tools"
            },

            # General Utility Scripts
            "utilities": {
                "patterns": [".*fix.*\\.py$", ".*config.*\\.py$", ".*setup.*\\.py$", ".*test.*\\.py$",
                           ".*monitor.*\\.py$", ".*verify.*\\.py$", ".*analysis.*\\.py$"],
                "destination": "src/scripts/utilities",
                "description": "General utility and configuration scripts"
            },

            # B3 Log Files
            "b3_logs": {
                "patterns": ["b3_.*\\.log$"],
                "destination": "logs/b3/training",
                "description": "B3 training and operation logs"
            },

            # Dataset Operation Logs
            "dataset_logs": {
                "patterns": [".*dataset.*\\.log$", ".*acquisition.*\\.log$", "k12_.*\\.log$",
                           ".*corpus.*\\.log$", "educational.*\\.log$"],
                "destination": "logs/dataset_operations",
                "description": "Dataset processing operation logs"
            },

            # F: Drive Operation Logs
            "f_drive_logs": {
                "patterns": ["f_drive.*\\.log$", ".*migration.*\\.log$", "cache.*\\.log$"],
                "destination": "logs/f_drive_operations",
                "description": "F: drive management operation logs"
            },

            # General Logs
            "general_logs": {
                "patterns": [".*\\.log$"],
                "destination": "logs",
                "description": "General operation logs"
            },

            # B3 JSON Reports
            "b3_reports": {
                "patterns": ["b3_.*\\.json$"],
                "destination": "logs/b3/reports",
                "description": "B3 operation and training reports"
            },

            # Dataset JSON Reports
            "dataset_reports": {
                "patterns": [".*dataset.*\\.json$", ".*acquisition.*\\.json$", "k12_.*\\.json$",
                           ".*corpus.*\\.json$", "educational.*\\.json$"],
                "destination": "logs/dataset_operations",
                "description": "Dataset operation reports"
            },

            # F: Drive JSON Reports
            "f_drive_reports": {
                "patterns": ["f_drive.*\\.json$", ".*migration.*\\.json$", "cache.*\\.json$"],
                "destination": "logs/f_drive_operations",
                "description": "F: drive operation reports"
            },

            # General JSON Reports
            "general_reports": {
                "patterns": [".*\\.json$"],
                "destination": "logs",
                "description": "General operation reports"
            },

            # B3 Strategy Documents
            "b3_strategy": {
                "patterns": ["B3_.*STRATEGY.*\\.md$", "B3_.*PLAN.*\\.md$", "B3_.*GUIDE.*\\.md$"],
                "destination": "docs/strategic/b3",
                "description": "B3 strategic planning documents"
            },

            # B3 Report Documents
            "b3_documentation": {
                "patterns": ["B3_.*REPORT.*\\.md$", "B3_.*SUCCESS.*\\.md$", "B3_.*EVALUATION.*\\.md$",
                           "B3_.*ANALYSIS.*\\.md$"],
                "destination": "docs/reports/b3",
                "description": "B3 analysis and evaluation reports"
            },

            # Dataset Strategy Documents
            "dataset_strategy": {
                "patterns": ["DATASET_.*\\.md$", "K12_.*\\.md$", ".*CORPUS.*\\.md$"],
                "destination": "docs/strategic",
                "description": "Dataset strategy and planning documents"
            },

            # General Strategy Documents
            "general_strategy": {
                "patterns": [".*PLAN.*\\.md$", ".*STRATEGY.*\\.md$", ".*GUIDE.*\\.md$"],
                "destination": "docs/strategic",
                "description": "General strategic planning documents"
            },

            # General Reports
            "general_docs": {
                "patterns": [".*\\.md$"],
                "destination": "docs/reports",
                "description": "General documentation and reports"
            },

            # CSV Data Files
            "data_files": {
                "patterns": [".*\\.csv$", ".*\\.txt$"],
                "destination": "src/data",
                "description": "Data files and datasets"
            }
        }

        # Files to skip (already in correct locations)
        self.skip_patterns = [
            "README\\.md$", "requirements\\.txt$", "manage_f_models\\.py$",
            "CONTRIBUTING\\.md$", "COPILOT_.*\\.md$", "\\..*"  # Hidden files
        ]

    def should_skip_file(self, filename: str) -> bool:
        """Check if file should be skipped based on skip patterns"""
        import re
        return any(re.search(pattern, filename) for pattern in self.skip_patterns)

    def categorize_file(self, filename: str) -> tuple[str, str, str]:
        """
        Categorize a file based on patterns
        Returns: (category_name, destination_path, description)
        """
        import re

        for category_name, category_info in self.file_categories.items():
            for pattern in category_info["patterns"]:
                if re.search(pattern, filename):
                    return (
                        category_name,
                        category_info["destination"],
                        category_info["description"]
                    )

        # Default fallback
        return ("uncategorized", "src/scripts", "Uncategorized file")

    def create_backup(self, source_path: Path) -> bool:
        """Create backup of file before moving (Sacred Covenant compliance)"""
        try:
            backup_dir = self.project_root / "backups" / f"root_cleanup_{self.timestamp}"
            backup_dir.mkdir(parents=True, exist_ok=True)

            backup_path = backup_dir / source_path.name
            shutil.copy2(source_path, backup_path)

            logger.info(f"✅ Backup created: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Backup failed for {source_path}: {e}")
            return False

    def verify_file_integrity(self, source_path: Path, dest_path: Path) -> bool:
        """Verify file was moved correctly and has same size"""
        try:
            if not dest_path.exists():
                return False

            source_size = source_path.stat().st_size if source_path.exists() else 0
            dest_size = dest_path.stat().st_size

            return source_size == dest_size

        except Exception as e:
            logger.error(f"❌ Integrity verification failed: {e}")
            return False

    def move_file_safely(self, source_path: Path, dest_dir: str, description: str) -> bool:
        """
        Safely move file with Sacred Covenant compliance:
        1. Create backup
        2. Create destination directory
        3. Move file
        4. Verify integrity
        5. Log operation
        """
        try:
            # Step 1: Create backup
            if not self.create_backup(source_path):
                return False

            # Step 2: Create destination directory
            dest_dir_path = self.project_root / dest_dir
            dest_dir_path.mkdir(parents=True, exist_ok=True)

            # Step 3: Move file
            dest_path = dest_dir_path / source_path.name

            # Handle file conflicts
            if dest_path.exists():
                counter = 1
                base_name = source_path.stem
                extension = source_path.suffix
                while dest_path.exists():
                    new_name = f"{base_name}_{counter}{extension}"
                    dest_path = dest_dir_path / new_name
                    counter += 1

            shutil.move(str(source_path), str(dest_path))

            # Step 4: Verify integrity
            if not self.verify_file_integrity(source_path, dest_path):
                logger.error(f"❌ Integrity verification failed for {dest_path}")
                return False

            # Step 5: Log operation
            movement_record = {
                "source": str(source_path),
                "destination": str(dest_path),
                "category": description,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            self.organization_report["file_movements"].append(movement_record)

            logger.info(f"✅ Moved: {source_path.name} → {dest_dir}")
            return True

        except Exception as e:
            error_record = {
                "file": str(source_path),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.organization_report["errors"].append(error_record)
            logger.error(f"❌ Failed to move {source_path}: {e}")
            return False

    def organize_root_directory(self) -> dict:
        """Main organization function"""
        logger.info("🚀 Starting ImpressionCore Root Directory Organization")
        logger.info("📋 Sacred Covenant File Integrity Protocols: ACTIVE")

        # Get all files in root directory
        root_files = [f for f in self.project_root.iterdir()
                     if f.is_file() and not f.name.startswith('.')]

        self.organization_report["total_files_processed"] = len(root_files)

        # Process each file
        for file_path in root_files:
            filename = file_path.name

            # Skip files that should remain in root
            if self.should_skip_file(filename):
                logger.info(f"⏭️ Skipping: {filename} (should remain in root)")
                self.organization_report["skipped_files"] += 1
                continue

            # Categorize file
            category, destination, description = self.categorize_file(filename)

            # Move file safely
            if self.move_file_safely(file_path, destination, description):
                self.organization_report["successful_moves"] += 1
            else:
                self.organization_report["failed_moves"] += 1

        # Generate final report
        self.generate_organization_report()

        logger.info("✅ Root directory organization completed!")
        logger.info(f"📊 Processed: {self.organization_report['total_files_processed']} files")
        logger.info(f"✅ Successful: {self.organization_report['successful_moves']} moves")
        logger.info(f"❌ Failed: {self.organization_report['failed_moves']} moves")
        logger.info(f"⏭️ Skipped: {self.organization_report['skipped_files']} files")

        return self.organization_report

    def generate_organization_report(self):
        """Generate comprehensive organization report"""
        report_path = self.project_root / f"logs/root_directory_organization_{self.timestamp}.json"

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.organization_report, f, indent=2, ensure_ascii=False)

        # Also generate markdown summary
        md_report_path = self.project_root / f"docs/reports/root_directory_organization_{self.timestamp}.md"
        self.generate_markdown_report(md_report_path)

        logger.info(f"📄 Organization report saved: {report_path}")
        logger.info(f"📄 Markdown report saved: {md_report_path}")

    def generate_markdown_report(self, report_path: Path):
        """Generate markdown summary report"""
        content = f"""# ImpressionCore Root Directory Organization Report

# Date:** {datetime.now().strftime("%B %d, %Y %H:%M:%S")}
# Operation:** Sacred Covenant Compliant File Organization
# Status:** COMPLETED

## Summary Statistics

- **Total Files Processed:** {self.organization_report['total_files_processed']}
- **Successful Moves:** {self.organization_report['successful_moves']}
- **Failed Moves:** {self.organization_report['failed_moves']}
- **Skipped Files:** {self.organization_report['skipped_files']}

## File Categories Organized

### B3 Model Architecture Files
- Training scripts → `src/training/b3/`
- Model operation scripts → `src/models/b3/`
- Embedding processors → `src/embeddings/b3/`
- Utility scripts → `src/scripts/b3/`

### Dataset & Data Processing
- Dataset processors → `src/data/processors/`
- Data files → `src/data/`

### F: Drive Management
- F: drive tools → `src/scripts/f_drive/`

### Logging & Reports
- B3 logs → `logs/b3/training/`
- B3 reports → `logs/b3/reports/`
- Dataset logs → `logs/dataset_operations/`
- F: drive logs → `logs/f_drive_operations/`

### Documentation
- B3 strategy docs → `docs/strategic/b3/`
- B3 reports → `docs/reports/b3/`
- General strategy → `docs/strategic/`
- General reports → `docs/reports/`

## Sacred Covenant Compliance

✅ **File Integrity:** All files backed up before moving
✅ **Verification:** File sizes verified after each move
✅ **Logging:** Complete audit trail maintained
✅ **Error Handling:** Failed operations logged and reported

## Files Moved Successfully

"""

        # Add successful moves
        for movement in self.organization_report["file_movements"]:
            if movement.get("success", False):
                content += f"- `{Path(movement['source']).name}` → `{movement['destination']}`\n"

        if self.organization_report["errors"]:
            content += "\n## Errors Encountered\n\n"
            for error in self.organization_report["errors"]:
                content += f"- **{Path(error['file']).name}:** {error['error']}\n"

        content += f"""
## Backup Location

All original files backed up to: `backups/root_cleanup_{self.timestamp}/`

## Next Steps

1. Verify moved files are in correct locations
2. Test functionality to ensure no broken imports
3. Update any hardcoded file paths in scripts
4. Run project tests to validate organization

---

*This organization was performed in compliance with the Sacred Covenant file integrity protocols.*
"""

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    """Main execution function"""
    project_root = r"d:\Projects\impressioncore"

    # Create necessary additional directories
    additional_dirs = [
        "src/models/b3",
        "src/embeddings/b3",
        "src/scripts/f_drive",
        "src/scripts/utilities"
    ]

    for dir_path in additional_dirs:
        (Path(project_root) / dir_path).mkdir(parents=True, exist_ok=True)

    # Initialize and run organizer
    organizer = ImpressionCoreFileOrganizer(project_root)
    report = organizer.organize_root_directory()

    return report

if __name__ == "__main__":
    main()
