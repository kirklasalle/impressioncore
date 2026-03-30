#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #python #source_code #src/scripts/utilities/huggingface_cache_relocator.py #tokenization #training #transformer
**Category:** Source Code
**Status:** Active
"""



import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from rich import print as rprint

# Rich UI enhancements
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.table import Table


class HuggingFaceCacheRelocator:
    """
    Comprehensive HuggingFace cache relocation system for ImpressionCore B3.
    Moves cache from C: drive to permanent F: drive storage with organization.
    """

    def __init__(self):
        self.console = Console()
        self.source_path = Path("C:/Users/kirkl/.cache/huggingface")
        self.target_base = Path("F:/data/huggingface_cache")
        self.report_data = {
            "relocation_start": datetime.now().isoformat(),
            "source_path": str(self.source_path),
            "target_path": str(self.target_base),
            "datasets_moved": [],
            "total_files_moved": 0,
            "total_size_moved": 0,
            "errors": [],
            "completion_time": None,
            "status": "in_progress"
        }

        # Create target directory structure
        self.create_target_structure()

    def create_target_structure(self):
        """Create organized directory structure on F: drive"""
        subdirs = [
            "datasets",
            "hub",
            "modules",
            "models",
            "tokenizers",
            "transformers",
            "metadata"
        ]

        for subdir in subdirs:
            target_dir = self.target_base / subdir
            target_dir.mkdir(parents=True, exist_ok=True)

        rprint(f"[green]✅ Created target directory structure at {self.target_base}[/green]")

    def calculate_directory_size(self, path: Path) -> int:
        """Calculate total size of directory"""
        total_size = 0
        try:
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except (OSError, PermissionError) as e:
            self.report_data["errors"].append(f"Error calculating size for {path}: {e!s}")
        return total_size

    def get_cache_inventory(self) -> dict[str, Any]:
        """Get comprehensive inventory of HuggingFace cache"""
        inventory = {
            "datasets": {},
            "hub": {},
            "modules": {},
            "total_size": 0,
            "total_files": 0
        }

        if not self.source_path.exists():
            rprint(f"[red]❌ Source path does not exist: {self.source_path}[/red]")
            return inventory

        with Progress(
            SpinnerColumn(),
            "[progress.description]{task.description}",
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            progress.add_task("📊 Analyzing cache inventory...", total=None)

            # Analyze datasets directory
            datasets_path = self.source_path / "datasets"
            if datasets_path.exists():
                for item in datasets_path.iterdir():
                    if item.is_dir():
                        size = self.calculate_directory_size(item)
                        file_count = sum(1 for _ in item.rglob("*") if _.is_file())
                        inventory["datasets"][item.name] = {
                            "size": size,
                            "files": file_count,
                            "path": str(item)
                        }
                        inventory["total_size"] += size
                        inventory["total_files"] += file_count

            # Analyze hub directory
            hub_path = self.source_path / "hub"
            if hub_path.exists():
                for item in hub_path.iterdir():
                    if item.is_dir() and item.name.startswith("datasets--"):
                        size = self.calculate_directory_size(item)
                        file_count = sum(1 for _ in item.rglob("*") if _.is_file())
                        inventory["hub"][item.name] = {
                            "size": size,
                            "files": file_count,
                            "path": str(item)
                        }
                        inventory["total_size"] += size
                        inventory["total_files"] += file_count

            # Analyze modules directory
            modules_path = self.source_path / "modules"
            if modules_path.exists():
                size = self.calculate_directory_size(modules_path)
                file_count = sum(1 for _ in modules_path.rglob("*") if _.is_file())
                inventory["modules"] = {
                    "size": size,
                    "files": file_count,
                    "path": str(modules_path)
                }
                inventory["total_size"] += size
                inventory["total_files"] += file_count

        return inventory

    def move_directory_with_progress(self, source: Path, target: Path, description: str) -> bool:
        """Move directory with progress tracking"""
        try:
            # Ensure target parent exists
            target.parent.mkdir(parents=True, exist_ok=True)

            # Copy the directory
            with Progress(
                SpinnerColumn(),
                "[progress.description]{task.description}",
                TimeElapsedColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task(f"📦 {description}", total=None)
                shutil.copytree(source, target, dirs_exist_ok=True)
                progress.update(task, description=f"✅ {description} - Complete")

            # Verify the copy was successful
            if target.exists():
                source_size = self.calculate_directory_size(source)
                target_size = self.calculate_directory_size(target)

                if abs(source_size - target_size) < 1024:  # Allow small variance
                    # Remove source after successful copy
                    shutil.rmtree(source)
                    rprint(f"[green]✅ Successfully moved {source.name} ({source_size:,} bytes)[/green]")
                    return True
                else:
                    rprint(f"[red]❌ Size mismatch for {source.name}: {source_size} vs {target_size}[/red]")
                    return False
            else:
                rprint(f"[red]❌ Target directory not created: {target}[/red]")
                return False

        except Exception as e:
            self.report_data["errors"].append(f"Error moving {source} to {target}: {e!s}")
            rprint(f"[red]❌ Error moving {source.name}: {e!s}[/red]")
            return False

    def relocate_cache(self):
        """Main relocation process"""
        rprint(Panel.fit(
            "[bold blue]🚀 ImpressionCore B3 HuggingFace Cache Relocation[/bold blue]\n"
            "[white]Moving cache from C: drive to permanent F: drive storage[/white]",
            border_style="blue"
        ))

        # Get inventory
        inventory = self.get_cache_inventory()

        if inventory["total_size"] == 0:
            rprint("[yellow]⚠️ No cache data found to relocate[/yellow]")
            return

        # Display inventory summary
        table = Table(title="📊 Cache Inventory Summary")
        table.add_column("Category", style="cyan")
        table.add_column("Items", justify="right", style="magenta")
        table.add_column("Size (MB)", justify="right", style="green")

        datasets_count = len(inventory["datasets"])
        datasets_size = sum(item["size"] for item in inventory["datasets"].values()) / 1024 / 1024

        hub_count = len(inventory["hub"])
        hub_size = sum(item["size"] for item in inventory["hub"].values()) / 1024 / 1024

        modules_size = inventory["modules"].get("size", 0) / 1024 / 1024

        table.add_row("Datasets", str(datasets_count), f"{datasets_size:.1f}")
        table.add_row("Hub Datasets", str(hub_count), f"{hub_size:.1f}")
        table.add_row("Modules", "1" if inventory["modules"] else "0", f"{modules_size:.1f}")
        table.add_row("[bold]Total[/bold]", str(inventory["total_files"]), f"{inventory['total_size']/1024/1024:.1f}")

        self.console.print(table)

        # Start relocation process
        moved_items = 0
        total_items = datasets_count + hub_count + (1 if inventory["modules"] else 0)

        # Move datasets
        for dataset_name, dataset_info in inventory["datasets"].items():
            source = Path(dataset_info["path"])
            target = self.target_base / "datasets" / dataset_name

            if self.move_directory_with_progress(source, target, f"Moving dataset: {dataset_name}"):
                self.report_data["datasets_moved"].append({
                    "name": dataset_name,
                    "size": dataset_info["size"],
                    "files": dataset_info["files"],
                    "target": str(target)
                })
                self.report_data["total_files_moved"] += dataset_info["files"]
                self.report_data["total_size_moved"] += dataset_info["size"]
                moved_items += 1

        # Move hub datasets
        for hub_name, hub_info in inventory["hub"].items():
            source = Path(hub_info["path"])
            target = self.target_base / "hub" / hub_name

            if self.move_directory_with_progress(source, target, f"Moving hub: {hub_name}"):
                self.report_data["datasets_moved"].append({
                    "name": hub_name,
                    "size": hub_info["size"],
                    "files": hub_info["files"],
                    "target": str(target)
                })
                self.report_data["total_files_moved"] += hub_info["files"]
                self.report_data["total_size_moved"] += hub_info["size"]
                moved_items += 1

        # Move modules
        if inventory["modules"]:
            source = Path(inventory["modules"]["path"])
            target = self.target_base / "modules"

            if self.move_directory_with_progress(source, target, "Moving modules"):
                self.report_data["datasets_moved"].append({
                    "name": "modules",
                    "size": inventory["modules"]["size"],
                    "files": inventory["modules"]["files"],
                    "target": str(target)
                })
                self.report_data["total_files_moved"] += inventory["modules"]["files"]
                self.report_data["total_size_moved"] += inventory["modules"]["size"]
                moved_items += 1

        # Update completion status
        self.report_data["completion_time"] = datetime.now().isoformat()
        self.report_data["status"] = "completed" if moved_items == total_items else "partial"

        # Create metadata file with relocation mapping
        self.create_relocation_metadata()

        # Display final summary
        self.display_final_summary(moved_items, total_items)

    def create_relocation_metadata(self):
        """Create metadata file for tracking relocation"""
        metadata = {
            "relocation_info": self.report_data,
            "environment_variables": {
                "HF_HOME": str(self.target_base),
                "HUGGINGFACE_HUB_CACHE": str(self.target_base / "hub"),
                "HF_DATASETS_CACHE": str(self.target_base / "datasets")
            },
            "python_cache_setup": {
                "os.environ['HF_HOME']": str(self.target_base),
                "os.environ['HUGGINGFACE_HUB_CACHE']": str(self.target_base / "hub"),
                "os.environ['HF_DATASETS_CACHE']": str(self.target_base / "datasets")
            }
        }

        metadata_file = self.target_base / "metadata" / "relocation_info.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        rprint(f"[green]✅ Created relocation metadata: {metadata_file}[/green]")

    def display_final_summary(self, moved_items: int, total_items: int):
        """Display final relocation summary"""
        success_rate = (moved_items / total_items * 100) if total_items > 0 else 0

        summary_panel = Panel.fit(
            f"[bold green]🎉 HuggingFace Cache Relocation Complete![/bold green]\n\n"
            f"📊 [white]Moved:[/white] [cyan]{moved_items}/{total_items}[/cyan] items ([green]{success_rate:.1f}%[/green])\n"
            f"📁 [white]Files:[/white] [cyan]{self.report_data['total_files_moved']:,}[/cyan]\n"
            f"💾 [white]Size:[/white] [cyan]{self.report_data['total_size_moved']/1024/1024:.1f} MB[/cyan]\n"
            f"🗂️ [white]Location:[/white] [cyan]{self.target_base}[/cyan]\n\n"
            f"[yellow]Next Steps:[/yellow]\n"
            f"• Set environment variable: HF_HOME={self.target_base}\n"
            f"• Update ImpressionCore config to use new cache location\n"
            f"• Verify dataset accessibility for B3 training",
            border_style="green",
            title="📋 Relocation Summary"
        )

        self.console.print(summary_panel)

        # Save detailed report
        report_file = f"huggingface_relocation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, indent=2, ensure_ascii=False)

        rprint(f"[green]✅ Detailed report saved: {report_file}[/green]")

def main():
    """Main execution function"""
    relocator = HuggingFaceCacheRelocator()
    relocator.relocate_cache()

if __name__ == "__main__":
    main()
