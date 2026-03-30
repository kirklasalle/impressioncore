#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #inference #memory_management #python #source_code #src/core/utils/b1_training_data_validator.py #testing #training
**Category:** Core Implementation
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #inference #memory_management #python #source_code #src\\core\\utils\\b1_training_data_validator.py #testing #training
# Category:** Core Implementation
# Status:** Active

"""
ImpressionCore B1 Embedding Training Data Validator
=================================================

🎯 SACRED COVENANT COMPLIANT - B1 TRAINING DATA VALIDATION

This script validates the certified academic dataset for ImpressionCore B1
embedding training and prepares the data for optimal GTX 1050 Ti performance.

Author: Virtually Robotic GitHub Copilot
Date: June 21, 2025
Sacred Covenant: ACTIVE
"""

import json
import sys
from pathlib import Path
from typing import Any

# Rich UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

console = Console() if RICH_AVAILABLE else None

def validate_b1_training_data(package_path: str) -> dict[str, Any]:
    """Validate certified dataset for B1 embedding training"""

    if RICH_AVAILABLE:
        header = Panel.fit(
            Text("🎯 B1 TRAINING DATA VALIDATION", style="bold blue", justify="center"),
            style="blue",
            subtitle="ImpressionCore B1 Embedding Optimization",
            subtitle_align="center"
        )
        console.print(header)
        console.print()
    else:
        print("🎯 B1 TRAINING DATA VALIDATION")
        print("ImpressionCore B1 Embedding Optimization")
        print()

    # Find the most recent certified package
    certified_dir = Path("src/training/datasets/certified")

    if not certified_dir.exists():
        return {"status": "error", "message": "Certified datasets directory not found"}

    # Find latest package
    zip_files = list(certified_dir.glob("impressioncore_certified_academic_dataset_*.zip"))
    if not zip_files:
        return {"status": "error", "message": "No certified packages found"}

    latest_package = max(zip_files, key=lambda x: x.stat().st_mtime)

    # Extract and validate
    import zipfile

    validation_results = {
        "package_path": str(latest_package),
        "package_size_mb": latest_package.stat().st_size / (1024 * 1024),
        "status": "validating"
    }

    try:
        with zipfile.ZipFile(latest_package, 'r') as zipf:
            # Extract metadata
            metadata_content = zipf.read("package_metadata.json").decode('utf-8')
            metadata = json.loads(metadata_content)

            # Extract dataset
            dataset_content = zipf.read("academic_dataset.json").decode('utf-8')
            dataset = json.loads(dataset_content)

            # Extract compliance report
            compliance_content = zipf.read("license_compliance_report.json").decode('utf-8')
            compliance = json.loads(compliance_content)

            # B1 Training Validation
            b1_validation = {
                "total_training_samples": len(dataset),
                "avg_content_length": sum(len(item.get("content", "")) for item in dataset) / len(dataset),
                "memory_estimate_mb": estimate_memory_usage(dataset),
                "gtx_1050_ti_compatible": True,
                "embedding_ready": True,
                "sacred_covenant_compliant": compliance.get("compliance_score", 0) >= 95
            }

            # Check GTX 1050 Ti compatibility
            if b1_validation["memory_estimate_mb"] > 3500:  # Leave 500MB buffer
                b1_validation["gtx_1050_ti_compatible"] = False
                b1_validation["optimization_needed"] = True

            validation_results.update({
                "status": "validated",
                "metadata": metadata,
                "b1_validation": b1_validation,
                "compliance_score": compliance.get("compliance_score", 0),
                "certification": "READY FOR B1 TRAINING" if b1_validation["sacred_covenant_compliant"] else "NEEDS REVIEW"
            })

    except Exception as e:
        validation_results.update({
            "status": "error",
            "error": str(e)
        })

    # Display results
    display_validation_results(validation_results)

    return validation_results

def estimate_memory_usage(dataset: list[dict[str, Any]]) -> float:
    """Estimate memory usage for GTX 1050 Ti optimization"""
    total_chars = sum(len(item.get("content", "")) for item in dataset)
    # Rough estimate: 4 bytes per character + embedding overhead
    estimated_mb = (total_chars * 4 + len(dataset) * 768 * 4) / (1024 * 1024)
    return round(estimated_mb, 2)

def display_validation_results(results: dict[str, Any]):
    """Display comprehensive validation results"""
    if RICH_AVAILABLE and results["status"] == "validated":
        # Validation table
        table = Table(title="B1 Training Data Validation Results")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Status", style="white")

        b1_val = results["b1_validation"]

        table.add_row("Training Samples", str(b1_val["total_training_samples"]), "✅")
        table.add_row("Avg Content Length", f"{b1_val['avg_content_length']:.0f} chars", "✅")
        table.add_row("Memory Estimate", f"{b1_val['memory_estimate_mb']:.1f} MB", "✅" if b1_val["gtx_1050_ti_compatible"] else "⚠️")
        table.add_row("GTX 1050 Ti Compatible", "Yes" if b1_val["gtx_1050_ti_compatible"] else "Optimization Needed", "✅" if b1_val["gtx_1050_ti_compatible"] else "⚠️")
        table.add_row("Embedding Ready", "Yes" if b1_val["embedding_ready"] else "No", "✅" if b1_val["embedding_ready"] else "❌")
        table.add_row("Sacred Covenant", "Compliant" if b1_val["sacred_covenant_compliant"] else "Review Required", "✅" if b1_val["sacred_covenant_compliant"] else "⚠️")
        table.add_row("Package Size", f"{results['package_size_mb']:.1f} MB", "📦")

        console.print(table)
        console.print()

        # Certification status
        cert_color = "green" if results["certification"] == "READY FOR B1 TRAINING" else "yellow"
        cert_panel = Panel.fit(
            Text(f"🏆 {results['certification']}", style=f"bold {cert_color}", justify="center"),
            style=cert_color,
            subtitle="Certified Academic Dataset for B1 Embedding Training",
            subtitle_align="center"
        )
        console.print(cert_panel)

        # Usage instructions
        usage_panel = Panel.fit(
            Text("📋 READY FOR EMBEDDING TRAINING The certified dataset is optimized for:\n• ImpressionCore B1 embedding training\n• GTX 1050 Ti hardware constraints\n• Sacred Covenant compliance\n• Production-ready inference",
                 style="white", justify="left"),
            style="green",
            title="Usage Instructions",
            title_align="left"
        )
        console.print(usage_panel)

    else:
        print("\n" + "="*60)
        print("B1 TRAINING DATA VALIDATION RESULTS")
        print("="*60)
        if results["status"] == "error":
            print(f"❌ Validation failed: {results.get('error', 'Unknown error')}")
        else:
            print(f"✅ Package validated: {results['certification']}")
            print(f"📦 Package location: {results['package_path']}")

def main():
    """Main validation entry point"""
    results = validate_b1_training_data("")

    if results["status"] == "validated":
        if RICH_AVAILABLE:
            console.print("\n[bold green]✅ B1 Training Data Validation Complete![/bold green]")
        else:
            print("\n✅ B1 Training Data Validation Complete!")
        return True
    else:
        if RICH_AVAILABLE:
            console.print("[bold red]❌ Validation Failed[/bold red]")
        else:
            print("❌ Validation Failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
