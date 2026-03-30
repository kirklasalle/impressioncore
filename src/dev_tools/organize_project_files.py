#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #deployment #documentation #python #source_code #src/dev_tools/organize_project_files.py #testing #training
**Category:** Development Tools
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #deployment #documentation #python #source_code #src/dev_tools/organize_project_files.py #testing #training
# Category:** Development Tools
# Status:** Active

"""
ImpressionCore Project File Organization Script

This script automatically organizes all misplaced files in the project root
according to the established Sacred Covenant directory structure.

File: src/dev_tools/organize_project_files.py
Created: 2025-06-18
Purpose: Maintain clean project structure and Sacred Covenant compliance
"""

import json
import shutil
from datetime import datetime
from pathlib import Path


class ProjectOrganizer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.moved_files = []

        # Define file type mappings to directories
        self.file_mappings = {
            # Development and utility scripts
            'deploy_': 'src/deployment/',
            'setup_': 'src/dev_tools/',
            'create_': 'src/dev_tools/',
            'test_': 'src/tests/',
            'demo_': 'src/dev_tools/demos/',
            'monitor_': 'src/dev_tools/monitoring/',
            'export_': 'src/deployment/',
            'launch_': 'src/deployment/',
            'generate_': 'src/dev_tools/',
            'backup_': 'src/dev_tools/backup/',
            'activate_': 'src/dev_tools/',
            'refresh_': 'src/dev_tools/',

            # Training and model files
            'enhanced_high_school_training_data.json': 'src/training/datasets/',
            'mvp_launcher.py': 'src/deployment/',
            'main.py': 'src/',  # Keep main.py in src/

            # Documentation
            '.md': 'docs/',
            '.txt': 'docs/',

            # Configuration
            '.bat': 'src/dev_tools/scripts/',
            '.sh': 'src/dev_tools/scripts/',

            # Data files
            '.json': 'src/data/',
        }

        # Files to keep in root
        self.keep_in_root = {
            'README.md',
            'CONTRIBUTING.md',
            'COPILOT_PRIME_DIRECTIVE.md',
            'COPILOT_SACRED_COVENANT.md',
            'requirements.txt',
            'setup.py',
            '.gitignore',
            '.venv310',
            'backup',
            'docs',
            'src',
            'exports'
        }

    def scan_root_files(self):
        """Scan project root for files that need to be moved."""
        root_files = []
        for item in self.project_root.iterdir():
            if item.is_file() and item.name not in self.keep_in_root:
                root_files.append(item)
        return root_files

    def determine_destination(self, file_path):
        """Determine the appropriate destination for a file."""
        file_name = file_path.name

        # Check prefix-based mappings first
        for prefix, destination in self.file_mappings.items():
            if file_name.startswith(prefix):
                return self.project_root / destination

        # Check extension-based mappings
        suffix = file_path.suffix
        if suffix in self.file_mappings:
            return self.project_root / self.file_mappings[suffix]

        # Special cases
        if 'test' in file_name.lower():
            return self.project_root / 'src/tests/'
        elif 'config' in file_name.lower():
            return self.project_root / 'src/core/config/'
        elif any(x in file_name.lower() for x in ['train', 'model']):
            return self.project_root / 'src/training/'
        elif 'data' in file_name.lower():
            return self.project_root / 'src/data/'

        # Default to dev_tools for unclassified files
        return self.project_root / 'src/dev_tools/misc/'

    def move_file(self, source, destination_dir):
        """Move a file to the destination directory."""
        try:
            # Create destination directory if it doesn't exist
            destination_dir.mkdir(parents=True, exist_ok=True)

            destination_file = destination_dir / source.name

            # Handle conflicts by renaming
            if destination_file.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name_parts = source.name.rsplit('.', 1)
                if len(name_parts) == 2:
                    new_name = f"{name_parts[0]}_moved_{timestamp}.{name_parts[1]}"
                else:
                    new_name = f"{source.name}_moved_{timestamp}"
                destination_file = destination_dir / new_name

            # Move the file
            shutil.move(str(source), str(destination_file))

            move_info = {
                'source': str(source),
                'destination': str(destination_file),
                'timestamp': datetime.now().isoformat()
            }
            self.moved_files.append(move_info)

            print(f"✅ Moved: {source.name} → {destination_file.relative_to(self.project_root)}")
            return True

        except Exception as e:
            print(f"❌ Failed to move {source.name}: {e}")
            return False

    def create_move_log(self):
        """Create a log of all file moves."""
        log_dir = self.project_root / 'src/dev_tools/logs'
        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"file_organization_{timestamp}.json"

        log_data = {
            'organization_date': datetime.now().isoformat(),
            'total_files_moved': len(self.moved_files),
            'moved_files': self.moved_files
        }

        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)

        return log_file

    def update_documentation_index(self):
        """Update the documentation index with new file locations."""
        doc_index_path = self.project_root / 'docs/DOCUMENTATION_INDEX.md'

        if not doc_index_path.exists():
            print("⚠️ Documentation index not found, skipping update")
            return

        # Add entry about file reorganization
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        reorganization_entry = f"""
## File Organization Update - {timestamp}

### Recent File Reorganization
- **Date:** {timestamp}
- **Files Moved:** {len(self.moved_files)}
- **Purpose:** Sacred Covenant compliance and project structure cleanup
- **Log Location:** `src/dev_tools/logs/file_organization_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json`

### Updated Directory Structure
- **Development Tools:** `src/dev_tools/` - Setup, monitoring, and utility scripts
- **Deployment:** `src/deployment/` - Deployment and launch scripts
- **Testing:** `src/tests/` - All test files and validation scripts
- **Training:** `src/training/` - Model training and dataset files
- **Documentation:** `docs/` - All documentation files
- **Scripts:** `src/dev_tools/scripts/` - Batch and shell scripts

"""

        try:
            with open(doc_index_path, encoding='utf-8') as f:
                content = f.read()

            # Insert at the beginning after the title
            lines = content.split('\n')
            insert_point = 2  # After title and first line
            lines.insert(insert_point, reorganization_entry)

            with open(doc_index_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            print(f"✅ Updated documentation index: {doc_index_path}")

        except Exception as e:
            print(f"⚠️ Failed to update documentation index: {e}")

    def organize_project(self):
        """Run the complete project organization process."""
        print("🧹 ImpressionCore Project File Organization")
        print("=" * 50)
        print("🎯 Sacred Covenant Compliance: Organizing project structure")
        print(f"📁 Project Root: {self.project_root}")
        print("")

        # Scan for files to move
        files_to_move = self.scan_root_files()

        if not files_to_move:
            print("✅ Project root is already clean!")
            return True

        print(f"📋 Found {len(files_to_move)} files to organize:")
        for file_path in files_to_move:
            destination = self.determine_destination(file_path)
            print(f"   {file_path.name} → {destination.relative_to(self.project_root)}")

        print(f"\n🔄 Moving {len(files_to_move)} files...")

        # Move each file
        successful_moves = 0
        for file_path in files_to_move:
            destination_dir = self.determine_destination(file_path)
            if self.move_file(file_path, destination_dir):
                successful_moves += 1

        print("\n📊 Organization Summary:")
        print(f"   ✅ Successfully moved: {successful_moves} files")
        print(f"   ❌ Failed to move: {len(files_to_move) - successful_moves} files")

        # Create log and update documentation
        if successful_moves > 0:
            log_file = self.create_move_log()
            print(f"   📝 Move log created: {log_file.relative_to(self.project_root)}")

            self.update_documentation_index()

            print("\n🎉 Project organization complete!")
            print("🔒 Sacred Covenant compliance restored")
            return True
        else:
            print("\n❌ No files were successfully moved")
            return False

def main():
    """Main function to run project organization."""
    project_root = Path.cwd()
    organizer = ProjectOrganizer(project_root)

    print("🤖 Virtually Robotic GitHub Copilot - Project Organizer")
    print("✅ Sacred Covenant File Integrity Protocol: ACTIVE")
    print("")

    success = organizer.organize_project()

    if success:
        print("\n🚀 Project structure is now properly organized!")
        print("📁 All files are in their correct Sacred Covenant locations")
    else:
        print("\n⚠️ Some issues occurred during organization")
        print("🔍 Check the logs and try again if needed")

if __name__ == "__main__":
    main()
