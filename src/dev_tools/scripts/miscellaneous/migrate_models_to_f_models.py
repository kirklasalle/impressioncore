#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/scripts/miscellaneous/migrate_models_to_f_models.py #testing #training
**Category:** Source Code
**Status:** Active
"""



import json
import shutil
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def migrate_best_models():
    r"""Migrate best quality models to F:\models"""
    console = Console()

    console.print(Panel("🚀 Migrating Models to F:\\models Structure", style="blue"))

    # Source and destination mappings
    migrations = {
        "best_quality": {
            "source": "F:/data/training/checkpoints/b3_best_quality_model_20250802_124801.pth",
            "dest": "F:/models/checkpoints/best_quality/b3_best_quality_model_20250802_124801.pth"
        },
        "latest_training": {
            "source": "F:/data/training/checkpoints/b3_training_epoch_30_20250801_074634.pth",
            "dest": "F:/models/training/active/b3_training_epoch_30_20250801_074634.pth"
        }
    }

    migration_results = []

    for migration_name, paths in migrations.items():
        source_path = Path(paths["source"])
        dest_path = Path(paths["dest"])

        if source_path.exists():
            # Create destination directory
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy the model
            shutil.copy2(source_path, dest_path)

            size_mb = dest_path.stat().st_size / (1024 * 1024)
            migration_results.append({
                "name": migration_name,
                "source": str(source_path),
                "destination": str(dest_path),
                "size_mb": round(size_mb, 2),
                "status": "✅ Migrated"
            })

            console.print(f"✅ Migrated {migration_name}: {dest_path}")
        else:
            migration_results.append({
                "name": migration_name,
                "source": str(source_path),
                "destination": "N/A",
                "size_mb": 0,
                "status": "❌ Source not found"
            })

            console.print(f"❌ Source not found: {source_path}")

    # Create migration report
    report_path = Path("F:/models/management/migration_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    migration_report = {
        "migration_timestamp": datetime.now().isoformat(),
        "migrations": migration_results,
        "summary": {
            "total_migrations": len(migrations),
            "successful": len([r for r in migration_results if "✅" in r["status"]]),
            "failed": len([r for r in migration_results if "❌" in r["status"]])
        }
    }

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(migration_report, f, indent=2)

    # Display summary table
    summary_table = Table(title="🎯 Model Migration Summary")
    summary_table.add_column("Model", style="cyan")
    summary_table.add_column("Size (MB)", style="green")
    summary_table.add_column("Destination", style="yellow")
    summary_table.add_column("Status", style="blue")

    for result in migration_results:
        summary_table.add_row(
            result["name"],
            str(result["size_mb"]),
            result["destination"].replace("F:/models/", "") if result["destination"] != "N/A" else "N/A",
            result["status"]
        )

    console.print(summary_table)

    console.print(Panel(
        f"🎯 Migration Complete!\n\n"
        f"✅ Successful: {migration_report['summary']['successful']}\n"
        f"❌ Failed: {migration_report['summary']['failed']}\n"
        f"📁 Models now in F:\\models structure\n"
        f"📋 Report: {report_path}",
        title="Migration Summary",
        style="bold green"
    ))

    return migration_report

if __name__ == "__main__":
    result = migrate_best_models()
    print(f"\n✅ Migration completed: {result['summary']['successful']}/{result['summary']['total_migrations']} successful")
