#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/dev_tools/validation/b3_final_verification_system.py #training
**Category:** Development Tools
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\dev_tools\\validation\\b3_final_verification_system.py #training
# Category:** Development Tools
# Status:** Active

"""
🔍 B3 FINAL VERIFICATION & NEXT PHASE READINESS SYSTEM
ImpressionCore B3 - COMPREHENSIVE PIPELINE VALIDATION

MISSION:
1. VERIFY all generated embeddings are accessible and valid
2. VALIDATE classification results and data integrity
3. CONFIRM next phase readiness with detailed metrics
4. GENERATE comprehensive readiness report for Phase 2
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

import numpy as np
from rich import box
from rich.align import Align
from rich.columns import Columns

# Rich imports for beautiful verification display
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.table import Table
from rich.text import Text


class B3FinalVerificationSystem:
    """
    Comprehensive verification system for B3 pipeline validation
    Ensures 100% readiness for Phase 2: Training & Optimization
    """

    def __init__(self):
        self.f_drive_path = Path("F:\\")
        self.professional_dataset_path = self.f_drive_path / "b3_professional_dataset"
        self.generation_output_path = self.professional_dataset_path / "embeddings"
        self.reports_path = self.professional_dataset_path / "reports"

        # Verification targets
        self.target_total_embeddings = 500000
        self.quality_thresholds = {
            'embedding_dimension': 768,
            'min_file_size_bytes': 100,
            'max_file_size_mb': 50,
            'data_type_valid': np.float32
        }

        # Rich console for beautiful output
        self.console = Console()
        self.start_time = time.time()

        # Verification results
        self.verification_results = {
            'total_files_found': 0,
            'valid_embeddings': 0,
            'invalid_embeddings': 0,
            'file_integrity_issues': [],
            'dimension_mismatches': [],
            'data_type_issues': [],
            'classification_accuracy': {},
            'phase_readiness_score': 0.0,
            'critical_issues': [],
            'warnings': [],
            'recommendations': []
        }

    def create_verification_panel(self, title: str, status: str, stats: dict | None = None) -> Panel:
        """Create beautiful verification status panel"""

        content = []
        content.append(Text(status, style="bold cyan"))
        content.append("")

        if stats:
            stats_table = Table(show_header=False, box=None, padding=(0, 1))
            for key, value in stats.items():
                if isinstance(value, int | float):
                    formatted_value = f"{value:,}" if isinstance(value, int) else f"{value:.2f}"
                else:
                    formatted_value = str(value)
                stats_table.add_row(f"{key}:", formatted_value)
            content.append(stats_table)

        elapsed = time.time() - self.start_time
        content.append("")
        content.append(f"⏱️ Elapsed: {elapsed/60:.1f} minutes")
        content.append(f"🎯 Target: {self.target_total_embeddings:,} embeddings")

        return Panel(
            Align.center(Columns(content, equal=True, expand=True)),
            title=f"🔍 {title}",
            border_style="bright_green",
            box=box.ROUNDED
        )

    def verify_file_integrity(self, file_path: str) -> dict:
        """Verify individual embedding file integrity"""

        integrity_result = {
            'file_path': file_path,
            'exists': False,
            'readable': False,
            'valid_numpy': False,
            'correct_dimension': False,
            'correct_dtype': False,
            'file_size_bytes': 0,
            'embedding_count': 0,
            'dimension': 0,
            'dtype': None,
            'issues': []
        }

        try:
            # Check file existence
            if not os.path.exists(file_path):
                integrity_result['issues'].append('File does not exist')
                return integrity_result

            integrity_result['exists'] = True
            integrity_result['file_size_bytes'] = os.path.getsize(file_path)

            # Check file size
            if integrity_result['file_size_bytes'] < self.quality_thresholds['min_file_size_bytes']:
                integrity_result['issues'].append('File too small')

            if integrity_result['file_size_bytes'] > self.quality_thresholds['max_file_size_mb'] * 1024 * 1024:
                integrity_result['issues'].append('File too large')

            # Try to load and validate numpy array
            try:
                embedding_data = np.load(file_path)
                integrity_result['readable'] = True
                integrity_result['valid_numpy'] = True

                # Check shape and dimension
                if len(embedding_data.shape) == 2:
                    integrity_result['embedding_count'] = embedding_data.shape[0]
                    integrity_result['dimension'] = embedding_data.shape[1]

                    if embedding_data.shape[1] == self.quality_thresholds['embedding_dimension']:
                        integrity_result['correct_dimension'] = True
                    else:
                        integrity_result['issues'].append(f'Dimension mismatch: {embedding_data.shape[1]} != {self.quality_thresholds["embedding_dimension"]}')
                else:
                    integrity_result['issues'].append(f'Invalid shape: {embedding_data.shape}')

                # Check data type
                integrity_result['dtype'] = embedding_data.dtype
                if embedding_data.dtype == self.quality_thresholds['data_type_valid']:
                    integrity_result['correct_dtype'] = True
                else:
                    integrity_result['issues'].append(f'Data type mismatch: {embedding_data.dtype} != {self.quality_thresholds["data_type_valid"]}')

                # Check for NaN or infinite values
                if np.any(np.isnan(embedding_data)):
                    integrity_result['issues'].append('Contains NaN values')

                if np.any(np.isinf(embedding_data)):
                    integrity_result['issues'].append('Contains infinite values')

            except Exception as e:
                integrity_result['issues'].append(f'Failed to load numpy array: {e!s}')

        except Exception as e:
            integrity_result['issues'].append(f'General error: {e!s}')

        return integrity_result

    def scan_and_verify_all_embeddings(self):
        """Scan F: drive and verify all embedding files"""

        self.console.print("\n🔍 [bold cyan]COMPREHENSIVE EMBEDDING VERIFICATION[/bold cyan]")

        # Scan for all .npy files
        all_embedding_files = []

        with Live(self.create_verification_panel("File Discovery", "🔍 Scanning F: drive for embedding files..."),
                  console=self.console, refresh_per_second=2) as live:

            for root, _dirs, files in os.walk(self.f_drive_path):
                for file in files:
                    if file.endswith('.npy'):
                        all_embedding_files.append(os.path.join(root, file))

                # Update progress occasionally
                if len(all_embedding_files) % 5000 == 0:
                    live.update(self.create_verification_panel(
                        "File Discovery",
                        f"📁 Found {len(all_embedding_files):,} embedding files...",
                        {"Files Discovered": len(all_embedding_files)}
                    ))

        self.verification_results['total_files_found'] = len(all_embedding_files)
        self.console.print(f"📁 [bold green]Found {len(all_embedding_files):,} embedding files to verify[/bold green]")

        # Verify each file
        verified_files = []
        invalid_files = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            TextColumn("[progress.completed]{task.completed:,}/{task.total:,}"),
            "•",
            TimeElapsedColumn(),
            "•",
            TimeRemainingColumn(),
            console=self.console
        ) as progress:

            verify_task = progress.add_task("🔍 Verifying file integrity", total=len(all_embedding_files))

            for file_path in all_embedding_files:
                integrity_result = self.verify_file_integrity(file_path)

                if not integrity_result['issues']:
                    verified_files.append(integrity_result)
                    self.verification_results['valid_embeddings'] += integrity_result.get('embedding_count', 1)
                else:
                    invalid_files.append(integrity_result)
                    self.verification_results['invalid_embeddings'] += 1
                    self.verification_results['file_integrity_issues'].extend(integrity_result['issues'])

                # Track specific issues
                if not integrity_result['correct_dimension']:
                    self.verification_results['dimension_mismatches'].append(file_path)

                if not integrity_result['correct_dtype']:
                    self.verification_results['data_type_issues'].append(file_path)

                progress.advance(verify_task, 1)

        return verified_files, invalid_files

    def verify_classification_results(self):
        """Verify the classification results from massive generation"""

        self.console.print("\n📋 [bold magenta]VERIFYING CLASSIFICATION RESULTS[/bold magenta]")

        classification_file = self.reports_path / "embedding_classification_results.json"

        if not classification_file.exists():
            self.verification_results['critical_issues'].append("Classification results file missing")
            return {}

        try:
            with open(classification_file) as f:
                classification_data = json.load(f)

            # Verify classification accuracy by sampling files
            modality_counts = {
                'text_embeddings': len(classification_data.get('text_embeddings', [])),
                'image_embeddings': len(classification_data.get('image_embeddings', [])),
                'audio_embeddings': len(classification_data.get('audio_embeddings', [])),
                'unknown_embeddings': len(classification_data.get('unknown_embeddings', []))
            }

            total_classified = sum(modality_counts.values())

            # Calculate classification distribution
            for modality, count in modality_counts.items():
                percentage = (count / total_classified * 100) if total_classified > 0 else 0
                self.verification_results['classification_accuracy'][modality] = {
                    'count': count,
                    'percentage': percentage
                }

            # Check for classification quality
            unknown_percentage = modality_counts['unknown_embeddings'] / total_classified * 100
            if unknown_percentage > 20:
                self.verification_results['warnings'].append(f"High percentage of unknown embeddings: {unknown_percentage:.1f}%")

            return classification_data

        except Exception as e:
            self.verification_results['critical_issues'].append(f"Failed to load classification results: {e!s}")
            return {}

    def verify_generation_reports(self):
        """Verify all generation and verification reports"""

        self.console.print("\n📊 [bold yellow]VERIFYING GENERATION REPORTS[/bold yellow]")

        required_reports = [
            "massive_generation_report.json",
            "embedding_classification_results.json"
        ]

        report_status = {}

        for report_name in required_reports:
            report_path = self.reports_path / report_name

            if report_path.exists():
                try:
                    with open(report_path) as f:
                        report_data = json.load(f)

                    report_status[report_name] = {
                        'exists': True,
                        'valid_json': True,
                        'size_bytes': report_path.stat().st_size,
                        'last_modified': datetime.fromtimestamp(report_path.stat().st_mtime).isoformat(),
                        'data_keys': list(report_data.keys()) if isinstance(report_data, dict) else []
                    }

                except Exception as e:
                    report_status[report_name] = {
                        'exists': True,
                        'valid_json': False,
                        'error': str(e)
                    }
                    self.verification_results['critical_issues'].append(f"Invalid JSON in {report_name}: {e!s}")
            else:
                report_status[report_name] = {
                    'exists': False
                }
                self.verification_results['critical_issues'].append(f"Missing required report: {report_name}")

        return report_status

    def calculate_phase_readiness_score(self, verified_files: list, classification_data: dict, report_status: dict):
        """Calculate comprehensive Phase 2 readiness score"""

        self.console.print("\n🎯 [bold red]CALCULATING PHASE 2 READINESS SCORE[/bold red]")

        score_components = {}

        # 1. Data Volume Score (30 points)
        total_embeddings = self.verification_results['valid_embeddings']
        volume_score = min(30, (total_embeddings / self.target_total_embeddings) * 30)
        score_components['data_volume'] = volume_score

        # 2. Data Quality Score (25 points)
        quality_ratio = self.verification_results['valid_embeddings'] / max(1, self.verification_results['total_files_found'])
        quality_score = quality_ratio * 25
        score_components['data_quality'] = quality_score

        # 3. Classification Completeness (20 points)
        if classification_data:
            unknown_ratio = len(classification_data.get('unknown_embeddings', [])) / max(1, self.verification_results['total_files_found'])
            classification_score = max(0, 20 - (unknown_ratio * 20))
        else:
            classification_score = 0
        score_components['classification_completeness'] = classification_score

        # 4. Infrastructure Readiness (15 points)
        required_dirs = [
            self.professional_dataset_path,
            self.generation_output_path,
            self.reports_path
        ]

        dir_score = 0
        for dir_path in required_dirs:
            if dir_path.exists():
                dir_score += 5

        score_components['infrastructure_readiness'] = dir_score

        # 5. Report Completeness (10 points)
        report_score = 0
        for _report_name, status in report_status.items():
            if status.get('exists') and status.get('valid_json', True):
                report_score += 5

        score_components['report_completeness'] = report_score

        # Calculate total score
        total_score = sum(score_components.values())
        self.verification_results['phase_readiness_score'] = total_score

        # Determine readiness level
        if total_score >= 90:
            readiness_level = "FULLY READY"
            readiness_color = "bold green"
        elif total_score >= 75:
            readiness_level = "MOSTLY READY"
            readiness_color = "bold yellow"
        elif total_score >= 60:
            readiness_level = "PARTIALLY READY"
            readiness_color = "bold orange"
        else:
            readiness_level = "NOT READY"
            readiness_color = "bold red"

        return score_components, total_score, readiness_level, readiness_color

    def generate_next_phase_recommendations(self, score_components: dict, total_score: float):
        """Generate specific recommendations for Phase 2 preparation"""

        recommendations = []

        # Data volume recommendations
        if score_components['data_volume'] < 25:
            recommendations.append("🔄 Generate additional embeddings to reach 500K+ target")

        # Data quality recommendations
        if score_components['data_quality'] < 20:
            recommendations.append("🔧 Fix file integrity issues and invalid embeddings")

        # Classification recommendations
        if score_components['classification_completeness'] < 15:
            recommendations.append("📋 Improve classification accuracy, reduce unknown embeddings")

        # Infrastructure recommendations
        if score_components['infrastructure_readiness'] < 12:
            recommendations.append("🏗️ Complete directory structure and file organization")

        # Report recommendations
        if score_components['report_completeness'] < 8:
            recommendations.append("📊 Generate missing reports and fix JSON validation issues")

        # Phase 2 specific recommendations
        if total_score >= 75:
            recommendations.extend([
                "🚀 Ready to proceed with Phase 2: Training Pipeline Setup",
                "⚡ Implement batch loading system for efficient training",
                "🎯 Set up model architecture and training configuration",
                "📈 Create performance monitoring and validation systems"
            ])

        self.verification_results['recommendations'] = recommendations
        return recommendations

    def execute_final_verification(self):
        """Execute comprehensive final verification pipeline"""

        self.console.print(Panel.fit(
            "🔍 EXECUTING COMPREHENSIVE B3 FINAL VERIFICATION\n"
            "✅ VALIDATING ALL DATA, REPORTS, AND PHASE READINESS\n"
            "🎯 PREPARING FOR PHASE 2: TRAINING & OPTIMIZATION",
            style="bold white on blue",
            title="🚀 B3 FINAL VERIFICATION SYSTEM",
            subtitle="Comprehensive Pipeline Validation"
        ))

        start_time = time.time()

        # 1. Scan and verify all embeddings
        verified_files, invalid_files = self.scan_and_verify_all_embeddings()

        # 2. Verify classification results
        classification_data = self.verify_classification_results()

        # 3. Verify generation reports
        report_status = self.verify_generation_reports()

        # 4. Calculate readiness score
        score_components, total_score, readiness_level, readiness_color = self.calculate_phase_readiness_score(
            verified_files, classification_data, report_status
        )

        # 5. Generate recommendations
        recommendations = self.generate_next_phase_recommendations(score_components, total_score)

        # 6. Create comprehensive verification report
        end_time = time.time()
        verification_time = end_time - start_time

        final_verification_report = {
            'verification_timestamp': datetime.now().isoformat(),
            'verification_time_minutes': verification_time / 60,
            'verification_results': self.verification_results,
            'score_components': score_components,
            'total_readiness_score': total_score,
            'readiness_level': readiness_level,
            'verified_files_count': len(verified_files),
            'invalid_files_count': len(invalid_files),
            'classification_data_summary': classification_data,
            'report_status': report_status,
            'recommendations': recommendations,
            'phase_2_ready': total_score >= 75,
            'critical_blockers': self.verification_results['critical_issues'],
            'next_steps': recommendations[:3] if recommendations else []
        }

        # Save verification report
        verification_report_path = self.reports_path / "b3_final_verification_report.json"
        verification_report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(verification_report_path, 'w') as f:
            json.dump(final_verification_report, f, indent=2, default=str)

        # Create beautiful verification summary
        self.console.print("\n" + "="*80)
        self.console.print(Panel.fit(
            f"PHASE 2 READINESS: {readiness_level}",
            style=readiness_color,
            title="🎯 FINAL VERIFICATION RESULTS"
        ))

        # Detailed results table
        results_table = Table(title="📊 COMPREHENSIVE VERIFICATION RESULTS", show_header=True, header_style="bold cyan")
        results_table.add_column("Component", style="cyan", width=25)
        results_table.add_column("Score", justify="right", style="green", width=10)
        results_table.add_column("Max", justify="right", style="yellow", width=10)
        results_table.add_column("Status", justify="center", style="white", width=15)

        for component, score in score_components.items():
            max_scores = {'data_volume': 30, 'data_quality': 25, 'classification_completeness': 20,
                         'infrastructure_readiness': 15, 'report_completeness': 10}
            max_score = max_scores.get(component, 0)
            status = "✅ Excellent" if score >= max_score * 0.9 else "⚠️ Good" if score >= max_score * 0.7 else "❌ Needs Work"
            results_table.add_row(component.replace('_', ' ').title(), f"{score:.1f}", str(max_score), status)

        results_table.add_row("", "", "", "")
        results_table.add_row("TOTAL SCORE", f"{total_score:.1f}", "100.0", f"{readiness_level}")

        self.console.print(results_table)

        # Key metrics table
        metrics_table = Table(title="📈 KEY METRICS SUMMARY", show_header=True, header_style="bold magenta")
        metrics_table.add_column("Metric", style="cyan", width=30)
        metrics_table.add_column("Value", justify="right", style="green", width=20)
        metrics_table.add_column("Target/Status", justify="center", style="yellow", width=20)

        metrics_table.add_row("⏱️ Verification Time", f"{verification_time/60:.1f} minutes", "✅ Complete")
        metrics_table.add_row("📁 Total Files Found", f"{self.verification_results['total_files_found']:,}", "📊 Discovered")
        metrics_table.add_row("✅ Valid Embeddings", f"{self.verification_results['valid_embeddings']:,}",
                             f"🎯 {self.target_total_embeddings:,}")
        metrics_table.add_row("❌ Invalid Files", f"{self.verification_results['invalid_embeddings']:,}", "⚠️ Review Needed")
        metrics_table.add_row("🎯 Readiness Score", f"{total_score:.1f}/100", readiness_level)
        metrics_table.add_row("🚀 Phase 2 Ready", "YES" if final_verification_report['phase_2_ready'] else "NO",
                             "✅ Proceed" if final_verification_report['phase_2_ready'] else "⏸️ Address Issues")

        self.console.print(metrics_table)

        # Recommendations
        if recommendations:
            self.console.print("\n📋 [bold cyan]NEXT PHASE RECOMMENDATIONS:[/bold cyan]")
            for i, rec in enumerate(recommendations[:5], 1):
                self.console.print(f"   {i}. {rec}")

        # Critical issues
        if self.verification_results['critical_issues']:
            self.console.print("\n🚨 [bold red]CRITICAL ISSUES TO ADDRESS:[/bold red]")
            for issue in self.verification_results['critical_issues'][:3]:
                self.console.print(f"   ❌ {issue}")

        self.console.print(Panel.fit(
            f"📋 VERIFICATION REPORT SAVED: {verification_report_path}\n"
            f"🎯 READINESS LEVEL: {readiness_level}\n"
            "🚀 Ready to proceed with next phase planning!",
            style="bold green"
        ))

        return final_verification_report

def main():
    """Execute comprehensive B3 final verification"""

    console = Console()

    # Beautiful startup banner
    console.print(Panel.fit(
        "🔍 B3 COMPREHENSIVE FINAL VERIFICATION SYSTEM\n"
        "✅ VALIDATING ALL PIPELINE COMPONENTS\n"
        "🎯 ENSURING PHASE 2 READINESS\n"
        f"📅 Verification Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        style="bold white on green",
        title="🚀 IMPRESSIONCORE B3 VERIFICATION",
        subtitle="Comprehensive Pipeline Validation System"
    ))

    # Initialize verification system
    verifier = B3FinalVerificationSystem()

    # Execute complete verification
    verification_report = verifier.execute_final_verification()

    # Final status
    if verification_report['phase_2_ready']:
        console.print(Panel.fit(
            "🎉 B3 PIPELINE FULLY VERIFIED!\n"
            "✅ ALL SYSTEMS GO FOR PHASE 2\n"
            "🚀 TRAINING & OPTIMIZATION READY!",
            style="bold green on black",
            title="🎯 VERIFICATION COMPLETE - SUCCESS!"
        ))
    else:
        console.print(Panel.fit(
            "⚠️ VERIFICATION COMPLETE - ISSUES FOUND\n"
            "🔧 ADDRESS CRITICAL ISSUES BEFORE PHASE 2\n"
            "📋 SEE RECOMMENDATIONS FOR NEXT STEPS",
            style="bold yellow on black",
            title="🎯 VERIFICATION COMPLETE - ACTION NEEDED"
        ))

if __name__ == "__main__":
    main()
