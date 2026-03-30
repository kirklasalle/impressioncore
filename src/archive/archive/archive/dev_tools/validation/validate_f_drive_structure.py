
⚠️ ARCHIVED FILE
This file has been archived for historical, compatibility, or deprecation reasons. Do not modify or use in active development.

#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #attention_mechanism #deployment #documentation #inference #multimodal #python #security #source_code #src/dev_tools/validation/validate_f_drive_structure.py #testing #training
**Category:** Development Tools
**Status:** Deprecated
"""









# !/usr/bin/env python3

**Created:** 2024-10-15
**Updated:** 2025-07-26 10_27_01
**Author:** ImpressionCore Team
**Tags:** #attention_mechanism #deployment #documentation #inference #multimodal #python #security #source_code #src/dev_tools/validation/validate_f_drive_structure.py #testing #training
**Category:** Development Tools
**Status:** Deprecated

"""
F: Drive Structure Validator

Validates the organization and compliance of the F:\datasets directory structure.
Provides comprehensive reporting and recommendations for improvement.

Author: GitHub Copilot
Date: 2025-07-24
Sacred Covenant: File Integrity Protected
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
from collections import defaultdict, Counter

# Rich imports (optional - graceful fallback)
try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import track
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Rich library not available. Using basic output.")

class FDriveStructureValidator:
    """Validates F: drive datasets structure and provides compliance reporting."""

    def __init__(self, f_drive_path: str = "F:\\"):
        self.f_drive_path = Path(f_drive_path)
        self.datasets_path = self.f_drive_path / "datasets"
        self.console = Console() if RICH_AVAILABLE else None

        # Expected structure definition
        self.expected_structure = {
            "text": [
                "raw", "processed", "embeddings", "tokenized", "annotations",
                "multilingual", "domain_specific", "synthetic"
            ],
            "vision": [
                "images", "video", "embeddings", "annotations", "synthetic"
            ],
            "audio": [
                "raw", "processed", "embeddings", "transcriptions", "synthetic"
            ],
            "multimodal": [
                "vision_text", "audio_text", "audio_vision", "all_modalities",
                "embeddings", "annotations"
            ],
            "structured": [
                "tabular", "time_series", "graphs", "knowledge_bases", "embeddings"
            ],
            "educational": [
                "materials", "assessments", "curricula", "tools", "research"
            ],
            "academic": [
                "papers", "datasets", "conferences", "journals", "preprints"
            ],
            "synthetic": [
                "text", "images", "audio", "multimodal", "structured"
            ],
            "metadata": [
                "catalogs", "schemas", "lineage", "quality", "documentation"
            ],
            "configurations": [
                "training", "inference", "preprocessing", "evaluation", "deployment"
            ],
            "working": [
                "staging", "preprocessing", "experiments", "temp", "backups"
            ],
            "archives": [
                "deprecated", "legacy", "backup_data", "historical"
            ],
            "tools": [
                "processors", "validators", "converters", "utilities", "scripts"
            ]
        }

        # File categorization patterns
        self.file_patterns = {
            "academic_papers": [r"^\d{4}\.\d{5}v\d+\.json$", r"arxiv_.*\.json$"],
            "embeddings": [r".*\.npy$", r".*\.faiss$", r".*embeddings.*", r".*\.pt$"],
            "configurations": [r".*config.*\.json$", r".*\.yaml$", r".*\.yml$"],
            "educational": [r".*grade.*", r".*education.*", r".*curriculum.*"],
            "facial_recognition": [r".*lfw.*", r".*celeba.*", r".*fairface.*"],
            "tools": [r".*\.py$", r".*\.sh$", r".*\.bat$"],
            "metadata": [r".*metadata.*", r".*catalog.*", r".*schema.*"]
        }

        self.validation_results = {}

    def setup_logging(self) -> None:
        """Setup comprehensive logging system."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"f_drive_validation_{timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger(__name__)
        self.logger.info(f"F: Drive Structure Validation started - {timestamp}")

    def validate_directory_structure(self) -> Dict[str, Any]:
        """Validate the existence and compliance of directory structure."""
        structure_compliance = {
            "exists": self.datasets_path.exists(),
            "missing_directories": [],
            "unexpected_directories": [],
            "compliance_score": 0.0
        }

        if not structure_compliance["exists"]:
            self.logger.error(f"Datasets directory does not exist: {self.datasets_path}")
            return structure_compliance

        # Check for expected directories
        existing_dirs = set()
        for item in self.datasets_path.iterdir():
            if item.is_dir():
                existing_dirs.add(item.name)

        expected_dirs = set(self.expected_structure.keys())

        # Find missing and unexpected directories
        structure_compliance["missing_directories"] = list(expected_dirs - existing_dirs)
        structure_compliance["unexpected_directories"] = list(existing_dirs - expected_dirs)

        # Calculate compliance score
        total_expected = len(expected_dirs)
        found_expected = len(expected_dirs & existing_dirs)
        structure_compliance["compliance_score"] = (found_expected / total_expected) * 100

        # Check subdirectory structure
        subdirectory_compliance = {}
        for main_dir in expected_dirs & existing_dirs:
            main_path = self.datasets_path / main_dir
            expected_subdirs = set(self.expected_structure[main_dir])
            existing_subdirs = set()

            if main_path.exists():
                for item in main_path.iterdir():
                    if item.is_dir():
                        existing_subdirs.add(item.name)

            subdirectory_compliance[main_dir] = {
                "missing": list(expected_subdirs - existing_subdirs),
                "unexpected": list(existing_subdirs - expected_subdirs),
                "compliance": (len(expected_subdirs & existing_subdirs) / len(expected_subdirs)) * 100 if expected_subdirs else 100
            }

        structure_compliance["subdirectories"] = subdirectory_compliance

        return structure_compliance

    def analyze_file_distribution(self) -> Dict[str, Any]:
        """Analyze file distribution across the directory structure."""
        if not self.datasets_path.exists():
            return {"error": "Datasets directory does not exist"}

        distribution = {
            "total_files": 0,
            "total_size": 0,
            "by_category": defaultdict(lambda: {"count": 0, "size": 0}),
            "by_extension": Counter(),
            "large_files": [],
            "empty_directories": []
        }

        # Traverse all files
        try:
            for file_path in self.datasets_path.rglob("*"):
                if file_path.is_file():
                    try:
                        file_size = file_path.stat().st_size
                        distribution["total_files"] += 1
                        distribution["total_size"] += file_size

                        # Categorize by directory
                        relative_path = file_path.relative_to(self.datasets_path)
                        category = str(relative_path.parts[0]) if relative_path.parts else "root"

                        distribution["by_category"][category]["count"] += 1
                        distribution["by_category"][category]["size"] += file_size

                        # Track extensions
                        extension = file_path.suffix.lower()
                        distribution["by_extension"][extension] += 1

                        # Track large files (>100MB)
                        if file_size > 100 * 1024 * 1024:
                            distribution["large_files"].append({
                                "path": str(file_path),
                                "size": file_size,
                                "size_mb": file_size / (1024 * 1024)
                            })

                    except (OSError, PermissionError) as e:
                        self.logger.warning(f"Could not access file {file_path}: {e}")

                elif file_path.is_dir():
                    # Check for empty directories
                    try:
                        if not any(file_path.iterdir()):
                            distribution["empty_directories"].append(str(file_path))
                    except (OSError, PermissionError):
                        pass

        except Exception as e:
            self.logger.error(f"Error analyzing file distribution: {e}")
            distribution["error"] = str(e)

        return distribution

    def check_file_categorization(self) -> Dict[str, Any]:
        """Check if files are properly categorized according to patterns."""
        if not self.datasets_path.exists():
            return {"error": "Datasets directory does not exist"}

        categorization = {
            "correctly_placed": 0,
            "misplaced_files": [],
            "suggestions": [],
            "unknown_files": []
        }

        try:
            for file_path in self.datasets_path.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.datasets_path)
                    current_category = str(relative_path.parts[0]) if relative_path.parts else "root"

                    # Determine expected category based on file patterns
                    expected_category = self._categorize_file(file_path.name, str(file_path))

                    if expected_category == "unknown":
                        categorization["unknown_files"].append({
                            "path": str(relative_path),
                            "current_location": current_category
                        })
                    elif expected_category == current_category:
                        categorization["correctly_placed"] += 1
                    else:
                        categorization["misplaced_files"].append({
                            "path": str(relative_path),
                            "current_location": current_category,
                            "suggested_location": expected_category
                        })
                        categorization["suggestions"].append({
                            "action": "move",
                            "from": str(file_path),
                            "to": str(self.datasets_path / expected_category / relative_path.name)
                        })

        except Exception as e:
            self.logger.error(f"Error checking file categorization: {e}")
            categorization["error"] = str(e)

        return categorization

    def _categorize_file(self, filename: str, filepath: str) -> str:
        """Determine the appropriate category for a file based on patterns."""
        import re

        filename_lower = filename.lower()
        filepath_lower = filepath.lower()

        # Check academic papers
        for pattern in self.file_patterns["academic_papers"]:
            if re.match(pattern, filename):
                return "academic"

        # Check embeddings
        for pattern in self.file_patterns["embeddings"]:
            if re.search(pattern, filename_lower) or re.search(pattern, filepath_lower):
                return "multimodal"  # or appropriate modality

        # Check configurations
        for pattern in self.file_patterns["configurations"]:
            if re.search(pattern, filename_lower):
                return "configurations"

        # Check educational content
        for pattern in self.file_patterns["educational"]:
            if re.search(pattern, filename_lower) or re.search(pattern, filepath_lower):
                return "educational"

        # Check facial recognition
        for pattern in self.file_patterns["facial_recognition"]:
            if re.search(pattern, filename_lower) or re.search(pattern, filepath_lower):
                return "vision"

        # Check tools
        for pattern in self.file_patterns["tools"]:
            if re.search(pattern, filename_lower):
                return "tools"

        # Check metadata
        for pattern in self.file_patterns["metadata"]:
            if re.search(pattern, filename_lower) or re.search(pattern, filepath_lower):
                return "metadata"

        # Default categorization by extension
        extension = Path(filename).suffix.lower()
        if extension in ['.json', '.jsonl']:
            return "structured"
        elif extension in ['.txt', '.md', '.doc', '.docx']:
            return "text"
        elif extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            return "vision"
        elif extension in ['.wav', '.mp3', '.flac', '.ogg']:
            return "audio"
        elif extension in ['.csv', '.tsv', '.xlsx']:
            return "structured"
        elif extension in ['.py', '.sh', '.bat']:
            return "tools"

        return "unknown"

    def generate_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on validation results."""
        recommendations = []

        # Structure recommendations
        structure = validation_results.get("structure", {})
        if structure.get("compliance_score", 0) < 100:
            missing = structure.get("missing_directories", [])
            if missing:
                recommendations.append(f"Create missing directories: {', '.join(missing)}")

        # File distribution recommendations
        distribution = validation_results.get("distribution", {})
        empty_dirs = distribution.get("empty_directories", [])
        if empty_dirs:
            recommendations.append(f"Consider removing {len(empty_dirs)} empty directories")

        large_files = distribution.get("large_files", [])
        if len(large_files) > 10:
            recommendations.append(f"Review {len(large_files)} large files (>100MB) for archival")

        # Categorization recommendations
        categorization = validation_results.get("categorization", {})
        misplaced = categorization.get("misplaced_files", [])
        if misplaced:
            recommendations.append(f"Reorganize {len(misplaced)} misplaced files")

        unknown = categorization.get("unknown_files", [])
        if unknown:
            recommendations.append(f"Classify {len(unknown)} unknown files")

        # Performance recommendations
        total_files = distribution.get("total_files", 0)
        if total_files > 50000:
            recommendations.append("Consider implementing file archival strategy for large dataset")

        # Security recommendations
        recommendations.append("Implement regular backup verification")
        recommendations.append("Set up automated structure monitoring")

        return recommendations

    def create_compliance_report(self, validation_results: Dict[str, Any]) -> str:
        """Create a detailed compliance report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""
F: Drive Datasets Structure Compliance Report
============================================
Generated: {timestamp}
Validator: FDriveStructureValidator v1.0

EXECUTIVE SUMMARY
================
"""

        # Structure compliance
        structure = validation_results.get("structure", {})
        compliance_score = structure.get("compliance_score", 0)

        if compliance_score >= 90:
            status = "EXCELLENT"
        elif compliance_score >= 75:
            status = "GOOD"
        elif compliance_score >= 50:
            status = "FAIR"
        else:
            status = "POOR"

        report += f"Overall Compliance: {compliance_score:.1f}% ({status})\n"
        report += f"Directory Structure: {'✅ COMPLIANT' if compliance_score >= 90 else '⚠️ NEEDS ATTENTION'}\n"

        # File statistics
        distribution = validation_results.get("distribution", {})
        total_files = distribution.get("total_files", 0)
        total_size_gb = distribution.get("total_size", 0) / (1024**3)

        report += f"Total Files: {total_files:,}\n"
        report += f"Total Size: {total_size_gb:.2f} GB\n\n"

        # Detailed findings
        report += "DETAILED FINDINGS\n"
        report += "================\n"

        # Missing directories
        missing_dirs = structure.get("missing_directories", [])
        if missing_dirs:
            report += f"Missing Directories ({len(missing_dirs)}):\n"
            for dir_name in missing_dirs:
                report += f"  - {dir_name}\n"
            report += "\n"

        # File distribution
        by_category = distribution.get("by_category", {})
        if by_category:
            report += "File Distribution by Category:\n"
            for category, stats in sorted(by_category.items()):
                size_mb = stats["size"] / (1024**2)
                report += f"  {category}: {stats['count']:,} files ({size_mb:.1f} MB)\n"
            report += "\n"

        # Recommendations
        recommendations = validation_results.get("recommendations", [])
        if recommendations:
            report += "RECOMMENDATIONS\n"
            report += "==============\n"
            for i, rec in enumerate(recommendations, 1):
                report += f"{i}. {rec}\n"
            report += "\n"

        report += "END OF REPORT\n"

        return report

    def run_full_validation(self) -> Dict[str, Any]:
        """Run complete validation and return comprehensive results."""
        self.setup_logging()

        if RICH_AVAILABLE and self.console:
            self.console.print(Panel.fit("🔍 F: Drive Structure Validation", style="bold blue"))
        else:
            print("🔍 F: Drive Structure Validation")
            print("=" * 50)

        # Run all validation checks
        validation_results = {}

        # 1. Directory structure validation
        if RICH_AVAILABLE:
            with self.console.status("[bold green]Validating directory structure..."):
                validation_results["structure"] = self.validate_directory_structure()
        else:
            print("📁 Validating directory structure...")
            validation_results["structure"] = self.validate_directory_structure()

        # 2. File distribution analysis
        if RICH_AVAILABLE:
            with self.console.status("[bold green]Analyzing file distribution..."):
                validation_results["distribution"] = self.analyze_file_distribution()
        else:
            print("📊 Analyzing file distribution...")
            validation_results["distribution"] = self.analyze_file_distribution()

        # 3. File categorization check
        if RICH_AVAILABLE:
            with self.console.status("[bold green]Checking file categorization..."):
                validation_results["categorization"] = self.check_file_categorization()
        else:
            print("🏷️  Checking file categorization...")
            validation_results["categorization"] = self.check_file_categorization()

        # 4. Generate recommendations
        validation_results["recommendations"] = self.generate_recommendations(validation_results)

        # 5. Create compliance report
        validation_results["report"] = self.create_compliance_report(validation_results)

        # Save results to file
        self._save_results(validation_results)

        # Display summary
        self._display_summary(validation_results)

        return validation_results

    def _save_results(self, results: Dict[str, Any]) -> None:
        """Save validation results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = Path(f"f_drive_validation_results_{timestamp}.json")

        # Create a serializable copy of results
        serializable_results = {}
        for key, value in results.items():
            if key == "report":
                continue  # Skip report text for JSON
            try:
                json.dumps(value)  # Test if serializable
                serializable_results[key] = value
            except (TypeError, ValueError):
                serializable_results[key] = str(value)

        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Validation results saved to: {results_file}")

            if RICH_AVAILABLE and self.console:
                self.console.print(f"💾 Results saved to: {results_file}", style="green")
            else:
                print(f"💾 Results saved to: {results_file}")

        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")

    def _display_summary(self, results: Dict[str, Any]) -> None:
        """Display validation summary."""
        structure = results.get("structure", {})
        distribution = results.get("distribution", {})
        categorization = results.get("categorization", {})
        recommendations = results.get("recommendations", [])

        if RICH_AVAILABLE and self.console:
            # Create summary table
            table = Table(title="Validation Summary")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="white")
            table.add_column("Status", style="green")

            # Add rows
            compliance = structure.get("compliance_score", 0)
            status = "✅ PASS" if compliance >= 90 else "⚠️ REVIEW" if compliance >= 75 else "❌ FAIL"
            table.add_row("Directory Compliance", f"{compliance:.1f}%", status)

            total_files = distribution.get("total_files", 0)
            table.add_row("Total Files", f"{total_files:,}", "📄")

            total_size = distribution.get("total_size", 0) / (1024**3)
            table.add_row("Total Size", f"{total_size:.2f} GB", "💾")

            misplaced = len(categorization.get("misplaced_files", []))
            table.add_row("Misplaced Files", str(misplaced), "🔄" if misplaced > 0 else "✅")

            table.add_row("Recommendations", str(len(recommendations)), "📋")

            self.console.print(table)

            # Display recommendations
            if recommendations:
                rec_panel = Panel(
                    "\n".join(f"• {rec}" for rec in recommendations[:5]),
                    title="Top Recommendations",
                    border_style="yellow"
                )
                self.console.print(rec_panel)

        else:
            # Basic text display
            print("\n📊 VALIDATION SUMMARY")
            print("=" * 50)
            print(f"Directory Compliance: {structure.get('compliance_score', 0):.1f}%")
            print(f"Total Files: {distribution.get('total_files', 0):,}")
            print(f"Total Size: {distribution.get('total_size', 0) / (1024**3):.2f} GB")
            print(f"Misplaced Files: {len(categorization.get('misplaced_files', []))}")
            print(f"Recommendations: {len(recommendations)}")

            if recommendations:
                print("\n📋 TOP RECOMMENDATIONS:")
                for i, rec in enumerate(recommendations[:5], 1):
                    print(f"{i}. {rec}")

        print(f"\n📝 Full report available in validation results file")

def main():
    """Main execution function."""
    try:
        # Initialize validator
        validator = FDriveStructureValidator()

        # Run full validation
        results = validator.run_full_validation()

        # Print completion message
        if RICH_AVAILABLE:
            console = Console()
            console.print(Panel.fit("✅ Validation Complete!", style="bold green"))
        else:
            print("\n✅ Validation Complete!")
            print("=" * 50)

        return results

    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
        return None
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        logging.error(f"Validation failed: {e}")
        return None

if __name__ == "__main__":
    main()
