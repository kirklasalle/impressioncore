#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #deployment #documentation #inference #python #source_code #src/dev_tools/root_directory_organizer_enhanced.py #testing #training
**Category:** Development Tools
**Status:** Active
"""


import json
import logging
import re
import shutil
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImpressionCoreFileOrganizerEnhanced:
    """
    Sacred Covenant compliant file organizer for ImpressionCore project
    Enhanced version with proper categorization rules
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

        # Files that should absolutely remain in root (exact matches)
        self.keep_in_root = {
            "README.md", "requirements.txt", "manage_f_models.py",
            "CONTRIBUTING.md", "COPILOT_PRIME_DIRECTIVE.md", "COPILOT_SACRED_COVENANT.md",
            ".env", ".gitignore"
        }

    def get_file_destination(self, filename: str) -> tuple[str, str]:
        """
        Determine destination for a file based on its name and type
        Returns: (destination_path, description)
        """

        # B3 Training Scripts
        if re.match(r'b3_.*(training|train).*\.py$', filename):
            return ("src/training/b3", "B3 training script")

        # B3 Model Operation Scripts
        elif re.match(r'b3_.*(model|inference|evaluation|tester|analyzer|evaluator).*\.py$', filename):
            return ("src/models/b3", "B3 model operation script")

        # B3 Embedding Scripts
        elif re.match(r'b3_.*(embed|integration).*\.py$', filename):
            return ("src/embeddings/b3", "B3 embedding processing script")

        # B3 Production/Deployment Scripts
        elif re.match(r'b3_.*(production|deployment|phase\d+).*\.py$', filename):
            return ("src/deployment/b3", "B3 deployment script")

        # Other B3 Scripts (utilities, coordinators, etc.)
        elif re.match(r'b3_.*\.py$', filename):
            return ("src/scripts/b3", "B3 utility script")

        # Dataset Processing Scripts
        elif re.match(r'.*(dataset|acquisition|corpus|educational_materials).*\.py$', filename):
            return ("src/data/processors", "Dataset processing script")

        # K12 Education Scripts
        elif re.match(r'k12_.*\.py$', filename):
            return ("src/data/processors/k12", "K12 educational corpus script")

        # F: Drive Management Scripts
        elif re.match(r'f_drive.*\.py$', filename) or re.match(r'f_models.*\.py$', filename) or re.match(r'.*f_datasets.*\.py$', filename):
            return ("src/scripts/f_drive", "F: drive management script")

        # Cache/Migration Scripts
        elif re.match(r'.*(cache|migration|hf_cache|huggingface).*\.py$', filename):
            return ("src/scripts/utilities", "Cache/migration utility script")

        # Fix/Setup/Test Scripts
        elif re.match(r'.*(fix|setup|test|verify|monitor|quick|comprehensive).*\.py$', filename):
            return ("src/scripts/utilities", "Utility script")

        # Distillation Scripts
        elif re.match(r'.*(distillation|ollama).*\.py$', filename):
            return ("src/training/distillation", "Knowledge distillation script")

        # General Analysis/Report Scripts
        elif re.match(r'.*(analysis|report|summary).*\.py$', filename):
            return ("src/scripts/analytics", "Analysis/reporting script")

        # B3 Log Files
        elif re.match(r'b3_.*\.log$', filename):
            return ("logs/b3/training", "B3 operation log")

        # Dataset Operation Logs
        elif re.match(r'.*(dataset|acquisition|corpus|educational|k12).*\.log$', filename):
            return ("logs/dataset_operations", "Dataset operation log")

        # F: Drive Logs
        elif re.match(r'f_drive.*\.log$', filename) or re.match(r'.*(migration|cache).*\.log$', filename):
            return ("logs/f_drive_operations", "F: drive operation log")

        # Distillation Logs
        elif re.match(r'.*(distillation|progressive).*\.log$', filename):
            return ("logs/training/distillation", "Knowledge distillation log")

        # General Logs
        elif filename.endswith('.log'):
            return ("logs/general", "General operation log")

        # B3 JSON Reports
        elif re.match(r'b3_.*\.json$', filename):
            return ("logs/b3/reports", "B3 operation report")

        # Dataset JSON Reports
        elif re.match(r'.*(dataset|acquisition|corpus|educational|k12).*\.json$', filename):
            return ("logs/dataset_operations", "Dataset operation report")

        # F: Drive JSON Reports
        elif re.match(r'f_drive.*\.json$', filename) or re.match(r'.*(migration|cache).*\.json$', filename):
            return ("logs/f_drive_operations", "F: drive operation report")

        # Training/Distillation JSON Reports
        elif re.match(r'.*(training|distillation|progressive).*\.json$', filename):
            return ("logs/training", "Training operation report")

        # General JSON Reports
        elif filename.endswith('.json'):
            return ("logs/reports", "General operation report")

        # B3 Strategy Documents
        elif re.match(r'B3_.*(STRATEGY|PLAN|GUIDE|IMPLEMENTATION).*\.md$', filename):
            return ("docs/strategic/b3", "B3 strategic planning document")

        # B3 Report Documents
        elif re.match(r'B3_.*(REPORT|SUCCESS|EVALUATION|ANALYSIS|SUMMARY).*\.md$', filename):
            return ("docs/reports/b3", "B3 analysis/evaluation report")

        # Dataset Strategy Documents
        elif re.match(r'(DATASET|K12)_.*\.md$', filename):
            return ("docs/strategic/datasets", "Dataset strategy document")

        # Mission/Phase Reports
        elif re.match(r'.*(MISSION|PHASE).*\.md$', filename):
            return ("docs/reports/missions", "Mission/phase report")

        # F: Drive Strategy Documents
        elif re.match(r'F_DRIVE.*\.md$', filename):
            return ("docs/strategic/f_drive", "F: drive strategy document")

        # General Strategy Documents
        elif re.match(r'.*(PLAN|STRATEGY|GUIDE).*\.md$', filename):
            return ("docs/strategic", "Strategic planning document")

        # General Reports
        elif filename.endswith('.md'):
            return ("docs/reports", "General documentation report")

        # Data Files
        elif filename.endswith('.csv') or filename.endswith('.txt'):
            return ("src/data", "Data file")

        # Default fallback
        else:
            return ("src/scripts/miscellaneous", "Miscellaneous file")

    def create_backup(self, source_path: Path) -> bool:
        """Create backup of file before moving (Sacred Covenant compliance)"""
        try:
            backup_dir = self.project_root / "backups" / f"root_cleanup_{self.timestamp}"
            backup_dir.mkdir(parents=True, exist_ok=True)

            backup_path = backup_dir / source_path.name
            shutil.copy2(source_path, backup_path)

            logger.info(f"✅ Backup created: {source_path.name}")
            return True

        except Exception as e:
            logger.error(f"❌ Backup failed for {source_path}: {e}")
            return False

    def move_file_safely(self, source_path: Path, dest_dir: str, description: str) -> bool:
        """
        Safely move file with Sacred Covenant compliance
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

            # Step 4: Log operation
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
        logger.info("🚀 Starting ImpressionCore Root Directory Organization (Enhanced)")
        logger.info("📋 Sacred Covenant File Integrity Protocols: ACTIVE")

        # Get all files in root directory (excluding directories and hidden files)
        root_files = [f for f in self.project_root.iterdir()
                     if f.is_file() and not f.name.startswith('.')]

        self.organization_report["total_files_processed"] = len(root_files)

        # Process each file
        for file_path in root_files:
            filename = file_path.name

            # Skip files that should remain in root
            if filename in self.keep_in_root:
                logger.info(f"⏭️ Keeping in root: {filename}")
                self.organization_report["skipped_files"] += 1
                continue

            # Get destination for file
            destination, description = self.get_file_destination(filename)

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
        report_path = self.project_root / f"logs/root_directory_organization_enhanced_{self.timestamp}.json"

        # Ensure logs directory exists
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.organization_report, f, indent=2, ensure_ascii=False)

        # Also generate markdown summary
        md_report_path = self.project_root / f"docs/reports/root_directory_organization_enhanced_{self.timestamp}.md"
        md_report_path.parent.mkdir(parents=True, exist_ok=True)
        self.generate_markdown_report(md_report_path)

        logger.info(f"📄 Organization report saved: {report_path}")
        logger.info(f"📄 Markdown report saved: {md_report_path}")

    def generate_markdown_report(self, report_path: Path):
        """Generate markdown summary report"""
        content = f"""# ImpressionCore Root Directory Organization Report (Enhanced)

# Date:** {datetime.now().strftime("%B %d, %Y %H:%M:%S")}
# Operation:** Sacred Covenant Compliant File Organization
# Status:** COMPLETED

## Summary Statistics

- **Total Files Processed:** {self.organization_report['total_files_processed']}
- **Successful Moves:** {self.organization_report['successful_moves']}
- **Failed Moves:** {self.organization_report['failed_moves']}
- **Skipped Files:** {self.organization_report['skipped_files']}

## Organized Directory Structure

### B3 Model Architecture Files
- **Training scripts** → `src/training/b3/`
- **Model operation scripts** → `src/models/b3/`
- **Embedding processors** → `src/embeddings/b3/`
- **Deployment scripts** → `src/deployment/b3/`
- **Utility scripts** → `src/scripts/b3/`

### Data Processing & Management
- **Dataset processors** → `src/data/processors/`
- **K12 educational scripts** → `src/data/processors/k12/`
- **Data files** → `src/data/`

### Infrastructure Management
- **F: drive tools** → `src/scripts/f_drive/`
- **Utility scripts** → `src/scripts/utilities/`
- **Analytics scripts** → `src/scripts/analytics/`

### Training & Model Development
- **Knowledge distillation** → `src/training/distillation/`

### Logging & Reports
- **B3 logs** → `logs/b3/training/`
- **B3 reports** → `logs/b3/reports/`
- **Dataset logs** → `logs/dataset_operations/`
- **F: drive logs** → `logs/f_drive_operations/`
- **Training logs** → `logs/training/`
- **General logs** → `logs/general/`

### Documentation
- **B3 strategy docs** → `docs/strategic/b3/`
- **B3 reports** → `docs/reports/b3/`
- **Dataset strategy** → `docs/strategic/datasets/`
- **Mission reports** → `docs/reports/missions/`
- **F: drive strategy** → `docs/strategic/f_drive/`
- **General strategy** → `docs/strategic/`
- **General reports** → `docs/reports/`

## Sacred Covenant Compliance

✅ **File Integrity:** All files backed up before moving
✅ **Verification:** Complete audit trail maintained
✅ **Error Handling:** Failed operations logged and reported
✅ **Professional Organization:** Files categorized by function and purpose

## Files Successfully Moved

"""

        # Group moves by destination
        moves_by_dest = {}
        for movement in self.organization_report["file_movements"]:
            if movement.get("success", False):
                dest = str(Path(movement['destination']).parent)
                if dest not in moves_by_dest:
                    moves_by_dest[dest] = []
                moves_by_dest[dest].append(Path(movement['source']).name)

        for dest, files in sorted(moves_by_dest.items()):
            content += f"\n### {dest}\n"
            for filename in sorted(files):
                content += f"- `{filename}`\n"

        if self.organization_report["errors"]:
            content += "\n## Errors Encountered\n\n"
            for error in self.organization_report["errors"]:
                content += f"- **{Path(error['file']).name}:** {error['error']}\n"

        content += f"""

## Backup Location

All original files backed up to: `backups/root_cleanup_{self.timestamp}/`

## Next Steps

1. ✅ Verify moved files are in correct locations
2. ✅ Test functionality to ensure no broken imports
3. ✅ Update any hardcoded file paths in scripts
4. ✅ Run project tests to validate organization
5. ✅ Update documentation references if needed

---

*This organization was performed in compliance with the Sacred Covenant file integrity protocols.*
*Enhanced version with improved categorization and directory structure.*
"""

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    """Main execution function"""
    project_root = r"d:\Projects\impressioncore"

    # Create necessary directories
    additional_dirs = [
        "src/models/b3",
        "src/embeddings/b3",
        "src/deployment/b3",
        "src/scripts/b3",
        "src/scripts/f_drive",
        "src/scripts/utilities",
        "src/scripts/analytics",
        "src/scripts/miscellaneous",
        "src/data/processors/k12",
        "src/training/distillation",
        "logs/b3/training",
        "logs/b3/reports",
        "logs/dataset_operations",
        "logs/f_drive_operations",
        "logs/training",
        "logs/training/distillation",
        "logs/general",
        "logs/reports",
        "docs/strategic/b3",
        "docs/strategic/datasets",
        "docs/strategic/f_drive",
        "docs/reports/b3",
        "docs/reports/missions"
    ]

    for dir_path in additional_dirs:
        (Path(project_root) / dir_path).mkdir(parents=True, exist_ok=True)

    # Initialize and run organizer
    organizer = ImpressionCoreFileOrganizerEnhanced(project_root)
    report = organizer.organize_root_directory()

    return report

if __name__ == "__main__":
    main()
