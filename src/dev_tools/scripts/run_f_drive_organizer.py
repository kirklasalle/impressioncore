#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/scripts\run_f_drive_organizer.py
**Category:** Source Code
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\scripts\\run_f_drive_organizer.py
# Category:** Source Code
# Status:** Active

"""
F: Drive Datasets Organizer Runner

User-friendly interface for running the F: drive datasets organization.
Includes safety checks, user confirmation, and progress reporting.

Author: GitHub Copilot
Date: 2025-07-24
Sacred Covenant: File Integrity Protected
"""

import contextlib
import sys
from pathlib import Path

# Add the 'src' directory to Python path for correct imports
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Rich imports (optional - graceful fallback)
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Confirm, Prompt  # noqa: F401
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

def count_files_in_directory(directory: Path) -> int:
    """Count total files in a directory recursively."""
    if not directory.exists():
        return 0

    count = 0
    try:
        for item in directory.rglob("*"):
            if item.is_file():
                count += 1
    except (PermissionError, OSError):
        pass
    return count

def get_directory_size(directory: Path) -> int:
    """Get total size of directory in bytes."""
    if not directory.exists():
        return 0

    total_size = 0
    try:
        for item in directory.rglob("*"):
            if item.is_file():
                with contextlib.suppress(PermissionError, OSError):
                    total_size += item.stat().st_size
    except (PermissionError, OSError):
        pass
    return total_size

def main():
    """Main execution function with user-friendly interface."""

    if RICH_AVAILABLE:
        console = Console()
        console.print(Panel.fit("🔄 F: Drive Datasets Organizer", style="bold blue"))
    else:
        print("🔄 F: Drive Datasets Organizer")
        print("=" * 50)

    # Check if F: drive exists
    f_drive = Path("F:\\")
    if not f_drive.exists():
        if RICH_AVAILABLE:
            console.print("❌ F: drive not found. Please ensure F: drive is accessible.", style="red")
        else:
            print("❌ F: drive not found. Please ensure F: drive is accessible.")
        return False

    # Check datasets directory
    datasets_dir = f_drive / "datasets"
    if not datasets_dir.exists():
        if RICH_AVAILABLE:
            console.print("❌ F:\\datasets directory not found.", style="red")
            create_datasets = Confirm.ask("Would you like to create F:\\datasets directory?")
        else:
            print("❌ F:\\datasets directory not found.")
            response = input("Would you like to create F:\\datasets directory? (y/n): ").lower().strip()
            create_datasets = response in ['y', 'yes']

        if create_datasets:
            try:
                datasets_dir.mkdir(exist_ok=True)
                if RICH_AVAILABLE:
                    console.print("✅ Created F:\\datasets directory", style="green")
                else:
                    print("✅ Created F:\\datasets directory")
            except Exception as e:
                if RICH_AVAILABLE:
                    console.print(f"❌ Failed to create directory: {e}", style="red")
                else:
                    print(f"❌ Failed to create directory: {e}")
                return False
        else:
            if RICH_AVAILABLE:
                console.print("⚠️ Cannot proceed without datasets directory", style="yellow")
            else:
                print("⚠️ Cannot proceed without datasets directory")
            return False

    # Count files and get size
    if RICH_AVAILABLE:
        with console.status("[bold green]Analyzing F:\\datasets directory..."):
            file_count = count_files_in_directory(datasets_dir)
            dir_size = get_directory_size(datasets_dir)
    else:
        print("📊 Analyzing F:\\datasets directory...")
        file_count = count_files_in_directory(datasets_dir)
        dir_size = get_directory_size(datasets_dir)

    size_gb = dir_size / (1024**3)

    # Display current state
    if RICH_AVAILABLE:
        info_text = Text()
        info_text.append("📁 Directory: ", style="bold")
        info_text.append(str(datasets_dir), style="cyan")
        info_text.append("\n📄 Files: ", style="bold")
        info_text.append(f"{file_count:,}", style="yellow")
        info_text.append("\n💾 Size: ", style="bold")
        info_text.append(f"{size_gb:.2f} GB", style="yellow")

        console.print(Panel(info_text, title="Current State", border_style="blue"))
    else:
        print(f"\n📁 Directory: {datasets_dir}")
        print(f"📄 Files: {file_count:,}")
        print(f"💾 Size: {size_gb:.2f} GB")

    if file_count == 0:
        if RICH_AVAILABLE:
            console.print("ℹ️ No files found to organize", style="blue")
        else:
            print("ℹ️ No files found to organize")
        return True

    # Ask about backup creation
    if RICH_AVAILABLE:
        create_backup = Confirm.ask("\n💾 Would you like to create a backup before organizing?", default=True)
    else:
        response = input("\n💾 Would you like to create a backup before organizing? (Y/n): ").lower().strip()
        create_backup = response in ['', 'y', 'yes']

    # Confirmation prompt
    if RICH_AVAILABLE:
        console.print("\n⚠️ This will organize your F:\\datasets directory according to world-class ML/AI standards.", style="yellow")
        console.print("Files will be moved to appropriate subdirectories based on their type and content.", style="yellow")

        proceed = Confirm.ask("\n🚀 Proceed with organization?", default=False)
    else:
        print("\n⚠️ This will organize your F:\\datasets directory according to world-class ML/AI standards.")
        print("Files will be moved to appropriate subdirectories based on their type and content.")

        response = input("\n🚀 Proceed with organization? (y/N): ").lower().strip()
        proceed = response in ['y', 'yes']

    if not proceed:
        if RICH_AVAILABLE:
            console.print("❌ Organization cancelled by user", style="red")
        else:
            print("❌ Organization cancelled by user")
        return False

    # Import and run the organizer
    try:
        if RICH_AVAILABLE:
            with console.status("[bold green]Importing F: Drive Organizer..."):
                from dev_tools.analysis.f_drive_datasets_organizer import FDriveDatasetOrganizer
        else:
            print("📦 Importing F: Drive Organizer...")
            from dev_tools.analysis.f_drive_datasets_organizer import FDriveDatasetOrganizer

        # Initialize organizer
        organizer = FDriveDatasetOrganizer(create_backup=create_backup)

        # Run organization
        if RICH_AVAILABLE:
            console.print("\n🚀 Starting organization process...", style="bold green")
        else:
            print("\n🚀 Starting organization process...")

        success = organizer.organize_datasets()

        if success:
            if RICH_AVAILABLE:
                console.print(Panel.fit("✅ Organization completed successfully!", style="bold green"))
            else:
                print("\n✅ Organization completed successfully!")
                print("=" * 50)

            # Display final statistics
            final_count = count_files_in_directory(datasets_dir)
            if RICH_AVAILABLE:
                console.print(f"📄 Total files organized: {final_count:,}", style="green")
                console.print("📋 Check the organization log for detailed results", style="blue")
            else:
                print(f"📄 Total files organized: {final_count:,}")
                print("📋 Check the organization log for detailed results")

            return True
        else:
            if RICH_AVAILABLE:
                console.print("❌ Organization failed. Check logs for details.", style="red")
            else:
                print("❌ Organization failed. Check logs for details.")
            return False

    except ImportError as e:
        if RICH_AVAILABLE:
            console.print(f"❌ Import error: {e}", style="red")
            console.print("Please ensure you're running from the correct directory", style="yellow")
        else:
            print(f"❌ Import error: {e}")
            print("Please ensure you're running from the correct directory")
        return False

    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"❌ Unexpected error: {e}", style="red")
        else:
            print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        if RICH_AVAILABLE:
            console = Console()
            console.print("\n⚠️ Operation interrupted by user", style="yellow")
        else:
            print("\n⚠️ Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        if RICH_AVAILABLE:
            console = Console()
            console.print(f"\n❌ Critical error: {e}", style="red")
        else:
            print(f"\n❌ Critical error: {e}")
        sys.exit(1)
