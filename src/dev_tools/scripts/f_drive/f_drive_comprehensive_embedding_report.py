#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** July-30-2025
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #multimodal #python #source_code #src/scripts\f_drive\f_drive_comprehensive_embedding_report.py #training
**Category:** Source Code
**Status:** Active
"""



import json
import sys
import traceback
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

# Rich for beautiful output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import track  # noqa: F401
    from rich.table import Table
    from rich.text import Text  # noqa: F401
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    console = None

class F_DriveEmbeddingAnalyzer:
    """
    Comprehensive analyzer for F: drive embeddings used in ImpressionCore B3 training.
    """

    def __init__(self):
        """Initialize the F: drive embedding analyzer."""
        self.source_root = Path("F:/datasets/embeddings")
        self.analysis_timestamp = datetime.now()

        # Analysis results
        self.analysis_results = {
            'directories': {},
            'file_stats': {},
            'modality_breakdown': {},
            'embedding_dimensions': {},
            'metadata_analysis': {},
            'quality_metrics': {},
            'training_readiness': {},
            'recommendations': []
        }

        # Required modalities for B3
        self.required_modalities = ["text", "image", "audio", "video", "cross_modal"]
        self.required_metadata = ["stats.json", "metadata.json"]

        print("🔍 F: Drive Embedding Analyzer initialized")
        print(f"📁 Source: {self.source_root}")
        print("📁 Target: Using F:/datasets/embeddings exclusively")

    def check_directory_structure(self):
        """Check and validate F: drive directory structure."""
        print("\n🏗️  Analyzing F: Drive Directory Structure...")

        # Check source directory
        if not self.source_root.exists():
            print(f"❌ Source directory does not exist: {self.source_root}")
            self.analysis_results['directories']['source_exists'] = False
            return False

        self.analysis_results['directories']['source_exists'] = True

        # Scan source directory structure
        print(f"✅ Source directory found: {self.source_root}")

        # Get directory contents
        source_contents = []
        if self.source_root.exists():
            for item in self.source_root.iterdir():
                if item.is_dir():
                    file_count = len(list(item.rglob("*.*")))
                    source_contents.append({
                        'name': item.name,
                        'type': 'directory',
                        'file_count': file_count,
                        'path': str(item)
                    })
                elif item.is_file():
                    source_contents.append({
                        'name': item.name,
                        'type': 'file',
                        'size_mb': item.stat().st_size / (1024 * 1024),
                        'path': str(item)
                    })

        self.analysis_results['directories']['source_contents'] = source_contents

        # Display source structure
        if RICH_AVAILABLE:
            structure_table = Table(title="F:/datasets/embeddings Structure")
            structure_table.add_column("Name", style="cyan")
            structure_table.add_column("Type", style="green")
            structure_table.add_column("Details", style="yellow")

            for item in source_contents:
                details = f"{item['file_count']} files" if item['type'] == 'directory' else f"{item['size_mb']:.2f} MB"
                structure_table.add_row(item['name'], item['type'], details)

            console.print(structure_table)
        else:
            print("\n📊 F:/datasets/embeddings Structure:")
            for item in source_contents:
                if item['type'] == 'directory':
                    print(f"  📁 {item['name']}: {item['file_count']} files")
                else:
                    print(f"  📄 {item['name']}: {item['size_mb']:.2f} MB")

        return True

    def analyze_modality_distributions(self):
        """Analyze embedding distributions across modalities."""
        print("\n🌐 Analyzing Multimodal Embedding Distributions...")

        modality_stats = {}

        for modality in self.required_modalities:
            modality_path = self.source_root / modality
            stats = {
                'exists': modality_path.exists(),
                'file_count': 0,
                'total_size_mb': 0,
                'file_types': defaultdict(int),
                'sample_shapes': [],
                'embedding_dimensions': set()
            }

            if modality_path.exists():
                # Count files and analyze
                all_files = list(modality_path.rglob("*.*"))
                stats['file_count'] = len(all_files)

                for file_path in all_files:
                    if file_path.is_file():
                        # File size
                        stats['total_size_mb'] += file_path.stat().st_size / (1024 * 1024)

                        # File type
                        extension = file_path.suffix.lower()
                        stats['file_types'][extension] += 1

                        # Sample embedding analysis (for .npy files)
                        if extension == '.npy' and len(stats['sample_shapes']) < 10:
                            try:
                                embedding = np.load(file_path)
                                stats['sample_shapes'].append(embedding.shape)
                                if len(embedding.shape) >= 2:
                                    stats['embedding_dimensions'].add(embedding.shape[-1])
                            except Exception:
                                continue

            modality_stats[modality] = stats

        self.analysis_results['modality_breakdown'] = modality_stats

        # Display modality analysis
        if RICH_AVAILABLE:
            modality_table = Table(title="Multimodal Embedding Analysis")
            modality_table.add_column("Modality", style="cyan")
            modality_table.add_column("Status", style="green")
            modality_table.add_column("Files", style="yellow")
            modality_table.add_column("Size (MB)", style="magenta")
            modality_table.add_column("Dimensions", style="blue")

            for modality, stats in modality_stats.items():
                status = "✅ Ready" if stats['exists'] and stats['file_count'] > 0 else "❌ Missing"
                dimensions = ", ".join(map(str, sorted(stats['embedding_dimensions']))) if stats['embedding_dimensions'] else "Unknown"

                modality_table.add_row(
                    modality,
                    status,
                    f"{stats['file_count']:,}",
                    f"{stats['total_size_mb']:.1f}",
                    dimensions
                )

            console.print(modality_table)
        else:
            print("\n📊 Multimodal Analysis:")
            for modality, stats in modality_stats.items():
                status = "✅ Ready" if stats['exists'] and stats['file_count'] > 0 else "❌ Missing"
                print(f"  {modality}: {status} - {stats['file_count']:,} files ({stats['total_size_mb']:.1f}MB)")

        return modality_stats

    def analyze_metadata_files(self):
        """Analyze metadata files for training pipeline configuration."""
        print("\n📋 Analyzing Metadata Files...")

        metadata_analysis = {}

        for metadata_file in self.required_metadata:
            file_path = self.source_root / metadata_file
            analysis = {
                'exists': file_path.exists(),
                'size_mb': 0,
                'content': None,
                'structure_valid': False,
                'modality_coverage': []
            }

            if file_path.exists():
                analysis['size_mb'] = file_path.stat().st_size / (1024 * 1024)

                try:
                    with open(file_path) as f:
                        content = json.load(f)
                    analysis['content'] = content
                    analysis['structure_valid'] = True

                    # Check modality coverage
                    for modality in self.required_modalities:
                        if modality in content:
                            analysis['modality_coverage'].append(modality)

                except Exception as e:
                    analysis['error'] = str(e)

            metadata_analysis[metadata_file] = analysis

        self.analysis_results['metadata_analysis'] = metadata_analysis

        # Display metadata analysis
        if RICH_AVAILABLE:
            metadata_table = Table(title="Metadata File Analysis")
            metadata_table.add_column("File", style="cyan")
            metadata_table.add_column("Status", style="green")
            metadata_table.add_column("Size", style="yellow")
            metadata_table.add_column("Modalities Covered", style="blue")

            for file_name, analysis in metadata_analysis.items():
                status = "✅ Valid" if analysis['structure_valid'] else "❌ Invalid" if analysis['exists'] else "❌ Missing"
                modalities = ", ".join(analysis['modality_coverage']) if analysis['modality_coverage'] else "None"

                metadata_table.add_row(
                    file_name,
                    status,
                    f"{analysis['size_mb']:.3f} MB" if analysis['exists'] else "N/A",
                    modalities
                )

            console.print(metadata_table)
        else:
            print("\n📊 Metadata Analysis:")
            for file_name, analysis in metadata_analysis.items():
                status = "✅ Valid" if analysis['structure_valid'] else "❌ Invalid" if analysis['exists'] else "❌ Missing"
                print(f"  {file_name}: {status}")

        return metadata_analysis

    def analyze_embedding_quality(self):
        """Analyze embedding quality and compatibility."""
        print("\n🎯 Analyzing Embedding Quality and B3 Compatibility...")

        quality_metrics = {
            'total_embeddings': 0,
            'compatible_embeddings': 0,
            'dimension_distribution': defaultdict(int),
            'format_distribution': defaultdict(int),
            'quality_issues': [],
            'b3_compatibility': {
                'standard_768': 0,
                'enhanced_4096': 0,
                'other_dimensions': 0
            }
        }

        # Sample embeddings from each modality
        sample_count = 0
        max_samples = 1000  # Limit for performance

        for modality in self.required_modalities:
            modality_path = self.source_root / modality
            if modality_path.exists():
                npy_files = list(modality_path.rglob("*.npy"))

                for file_path in npy_files[:100]:  # Sample first 100 files per modality
                    if sample_count >= max_samples:
                        break

                    try:
                        embedding = np.load(file_path)
                        quality_metrics['total_embeddings'] += 1
                        sample_count += 1

                        # Dimension analysis
                        if len(embedding.shape) >= 2:
                            dim = embedding.shape[-1]
                            quality_metrics['dimension_distribution'][dim] += 1

                            # B3 compatibility check
                            if dim == 768:
                                quality_metrics['b3_compatibility']['standard_768'] += 1
                                quality_metrics['compatible_embeddings'] += 1
                            elif dim == 4096:
                                quality_metrics['b3_compatibility']['enhanced_4096'] += 1
                                quality_metrics['compatible_embeddings'] += 1
                            else:
                                quality_metrics['b3_compatibility']['other_dimensions'] += 1

                        # Format analysis
                        quality_metrics['format_distribution'][str(embedding.dtype)] += 1

                        # Quality checks
                        if np.isnan(embedding).any():
                            quality_metrics['quality_issues'].append(f"NaN values in {file_path}")
                        if np.isinf(embedding).any():
                            quality_metrics['quality_issues'].append(f"Inf values in {file_path}")

                    except Exception as e:
                        quality_metrics['quality_issues'].append(f"Failed to load {file_path}: {e!s}")

        self.analysis_results['quality_metrics'] = quality_metrics

        # Display quality analysis
        if RICH_AVAILABLE:
            quality_table = Table(title="Embedding Quality Analysis")
            quality_table.add_column("Metric", style="cyan")
            quality_table.add_column("Value", style="green")
            quality_table.add_column("Details", style="yellow")

            quality_table.add_row("Total Sampled", f"{quality_metrics['total_embeddings']:,}", "Embeddings analyzed")
            quality_table.add_row("B3 Compatible", f"{quality_metrics['compatible_embeddings']:,}", "768D or 4096D embeddings")
            quality_table.add_row("Standard (768D)", f"{quality_metrics['b3_compatibility']['standard_768']:,}", "GTX 1050 Ti compatible")
            quality_table.add_row("Enhanced (4096D)", f"{quality_metrics['b3_compatibility']['enhanced_4096']:,}", "High-end hardware")
            quality_table.add_row("Quality Issues", f"{len(quality_metrics['quality_issues'])}", "NaN/Inf/Load errors")

            console.print(quality_table)

            # Dimension distribution
            if quality_metrics['dimension_distribution']:
                dim_table = Table(title="Embedding Dimension Distribution")
                dim_table.add_column("Dimension", style="cyan")
                dim_table.add_column("Count", style="green")
                dim_table.add_column("Percentage", style="yellow")

                total = sum(quality_metrics['dimension_distribution'].values())
                for dim, count in sorted(quality_metrics['dimension_distribution'].items()):
                    percentage = (count / total) * 100
                    dim_table.add_row(str(dim), f"{count:,}", f"{percentage:.1f}%")

                console.print(dim_table)
        else:
            print("\n📊 Quality Analysis:")
            print(f"  Total Sampled: {quality_metrics['total_embeddings']:,}")
            print(f"  B3 Compatible: {quality_metrics['compatible_embeddings']:,}")
            print(f"  Quality Issues: {len(quality_metrics['quality_issues'])}")

        return quality_metrics

    def assess_training_readiness(self):
        """Assess overall training readiness for ImpressionCore B3."""
        print("\n🚀 Assessing ImpressionCore B3 Training Readiness...")

        readiness = {
            'overall_ready': True,
            'readiness_score': 0,
            'requirements_met': {},
            'critical_issues': [],
            'warnings': [],
            'recommendations': []
        }

        # Check requirements
        requirements = {
            'source_directory': self.analysis_results['directories']['source_exists'],
            'required_modalities': True,
            'metadata_files': True,
            'compatible_embeddings': True,
            'quality_standards': True
        }

        # Check modalities
        modality_count = 0
        for modality in self.required_modalities:
            if modality in self.analysis_results['modality_breakdown']:
                if self.analysis_results['modality_breakdown'][modality]['file_count'] > 0:
                    modality_count += 1

        if modality_count < len(self.required_modalities):
            requirements['required_modalities'] = False
            readiness['critical_issues'].append(f"Missing modalities: {len(self.required_modalities) - modality_count}")

        # Check metadata
        metadata_count = 0
        for metadata_file in self.required_metadata:
            if metadata_file in self.analysis_results['metadata_analysis']:
                if self.analysis_results['metadata_analysis'][metadata_file]['structure_valid']:
                    metadata_count += 1

        if metadata_count < len(self.required_metadata):
            requirements['metadata_files'] = False
            readiness['critical_issues'].append(f"Invalid metadata files: {len(self.required_metadata) - metadata_count}")

        # Check embedding compatibility
        if 'quality_metrics' in self.analysis_results:
            compatible_ratio = 0
            if self.analysis_results['quality_metrics']['total_embeddings'] > 0:
                compatible_ratio = (self.analysis_results['quality_metrics']['compatible_embeddings'] /
                                  self.analysis_results['quality_metrics']['total_embeddings'])

            if compatible_ratio < 0.8:  # 80% compatibility threshold
                requirements['compatible_embeddings'] = False
                readiness['critical_issues'].append(f"Low B3 compatibility: {compatible_ratio:.1%}")

        # Quality standards
        if 'quality_metrics' in self.analysis_results:
            issue_count = len(self.analysis_results['quality_metrics']['quality_issues'])
            if issue_count > 10:  # Quality threshold
                requirements['quality_standards'] = False
                readiness['warnings'].append(f"Quality issues detected: {issue_count}")

        # Calculate readiness score
        met_requirements = sum(requirements.values())
        total_requirements = len(requirements)
        readiness['readiness_score'] = (met_requirements / total_requirements) * 100
        readiness['requirements_met'] = requirements

        # Overall readiness
        readiness['overall_ready'] = all(requirements.values())

        # Generate recommendations
        if not requirements['source_directory']:
            readiness['recommendations'].append("Create F:/datasets/embeddings directory structure")
        if not requirements['required_modalities']:
            readiness['recommendations'].append("Populate missing modality directories with embeddings")
        if not requirements['metadata_files']:
            readiness['recommendations'].append("Create/fix stats.json and metadata.json files")
        if not requirements['compatible_embeddings']:
            readiness['recommendations'].append("Convert embeddings to 768D or 4096D format for B3 compatibility")
        if not requirements['quality_standards']:
            readiness['recommendations'].append("Clean up embeddings with NaN/Inf values")

        self.analysis_results['training_readiness'] = readiness

        # Display readiness assessment
        if RICH_AVAILABLE:
            readiness_table = Table(title="ImpressionCore B3 Training Readiness")
            readiness_table.add_column("Requirement", style="cyan")
            readiness_table.add_column("Status", style="green")
            readiness_table.add_column("Details", style="yellow")

            for req_name, status in requirements.items():
                status_emoji = "✅" if status else "❌"
                details = "Met" if status else "Not Met"
                readiness_table.add_row(req_name.replace('_', ' ').title(), f"{status_emoji} {status}", details)

            console.print(readiness_table)

            # Overall status
            overall_status = "🚀 READY" if readiness['overall_ready'] else "⚠️ NOT READY"
            score_color = "green" if readiness['readiness_score'] >= 80 else "yellow" if readiness['readiness_score'] >= 60 else "red"

            status_content = f"""
[bold {score_color}]Readiness Score: {readiness['readiness_score']:.1f}%[/bold {score_color}]
[bold]Overall Status: {overall_status}[/bold]

[yellow]Critical Issues: {len(readiness['critical_issues'])}[/yellow]
[yellow]Warnings: {len(readiness['warnings'])}[/yellow]
[blue]Recommendations: {len(readiness['recommendations'])}[/blue]
            """
            console.print(Panel(status_content, title="Training Readiness Summary", border_style=score_color))
        else:
            print(f"\n🎯 Training Readiness: {readiness['readiness_score']:.1f}%")
            print(f"Overall Status: {'✅ READY' if readiness['overall_ready'] else '❌ NOT READY'}")

        return readiness

    def generate_comprehensive_report(self):
        """Generate a comprehensive report and save to file."""
        print("\n📄 Generating Comprehensive F: Drive Embedding Report...")

        # Create detailed report
        report = {
            'analysis_timestamp': self.analysis_timestamp.isoformat(),
            'source_directory': str(self.source_root),
            'analysis_results': self.analysis_results,
            'executive_summary': {
                'total_modalities_found': 0,
                'total_embeddings_estimated': 0,
                'total_size_gb': 0,
                'b3_compatibility_score': 0,
                'training_ready': False
            }
        }

        # Calculate executive summary
        if 'modality_breakdown' in self.analysis_results:
            report['executive_summary']['total_modalities_found'] = len([
                m for m in self.analysis_results['modality_breakdown']
                if self.analysis_results['modality_breakdown'][m]['file_count'] > 0
            ])

            total_files = sum([
                self.analysis_results['modality_breakdown'][m]['file_count']
                for m in self.analysis_results['modality_breakdown']
            ])
            report['executive_summary']['total_embeddings_estimated'] = total_files

            total_size_mb = sum([
                self.analysis_results['modality_breakdown'][m]['total_size_mb']
                for m in self.analysis_results['modality_breakdown']
            ])
            report['executive_summary']['total_size_gb'] = total_size_mb / 1024

        if 'quality_metrics' in self.analysis_results:
            quality = self.analysis_results['quality_metrics']
            if quality['total_embeddings'] > 0:
                compatibility = (quality['compatible_embeddings'] / quality['total_embeddings']) * 100
                report['executive_summary']['b3_compatibility_score'] = compatibility

        if 'training_readiness' in self.analysis_results:
            report['executive_summary']['training_ready'] = self.analysis_results['training_readiness']['overall_ready']

        # Save report
        report_file = Path("f_drive_embedding_comprehensive_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"✅ Comprehensive report saved: {report_file}")

        # Display executive summary
        if RICH_AVAILABLE:
            summary_content = f"""
[bold blue]ImpressionCore B3 F: Drive Embedding Analysis[/bold blue]
[bold]Analysis Date: {self.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}[/bold]

[green]📊 Executive Summary:[/green]
• Modalities Found: {report['executive_summary']['total_modalities_found']}/{len(self.required_modalities)}
• Total Embeddings: ~{report['executive_summary']['total_embeddings_estimated']:,}
• Total Size: {report['executive_summary']['total_size_gb']:.2f} GB
• B3 Compatibility: {report['executive_summary']['b3_compatibility_score']:.1f}%
• Training Ready: {'✅ YES' if report['executive_summary']['training_ready'] else '❌ NO'}

[yellow]📁 Directory:[/yellow]
• Source: {self.source_root} (F:/datasets/embeddings ONLY)

[cyan]🎯 Next Steps:[/cyan]
• Review detailed analysis in JSON report
• Address any critical issues identified
• Proceed with B3 initialization if ready
            """
            console.print(Panel(summary_content, title="F: Drive Embedding Analysis Complete", border_style="blue"))
        else:
            print("\n🎉 F: Drive Embedding Analysis Complete!")
            print(f"📊 Modalities: {report['executive_summary']['total_modalities_found']}/{len(self.required_modalities)}")
            print(f"📚 Embeddings: ~{report['executive_summary']['total_embeddings_estimated']:,}")
            print(f"💾 Size: {report['executive_summary']['total_size_gb']:.2f} GB")
            print(f"🎯 B3 Ready: {'✅ YES' if report['executive_summary']['training_ready'] else '❌ NO'}")

        return report

    def run_full_analysis(self):
        """Run the complete F: drive embedding analysis."""
        print("🚀 Starting Comprehensive F: Drive Embedding Analysis for ImpressionCore B3")
        print("=" * 80)

        try:
            # Step 1: Directory structure
            if not self.check_directory_structure():
                print("❌ Directory structure analysis failed")
                return None

            # Step 2: Modality analysis
            self.analyze_modality_distributions()

            # Step 3: Metadata analysis
            self.analyze_metadata_files()

            # Step 4: Quality analysis
            self.analyze_embedding_quality()

            # Step 5: Training readiness
            self.assess_training_readiness()

            # Step 6: Generate comprehensive report
            report = self.generate_comprehensive_report()

            print("\n🎉 F: Drive Embedding Analysis Complete!")
            return report

        except Exception as e:
            print(f"❌ Analysis failed: {e!s}")
            traceback.print_exc()
            return None

def main():
    """Main function to run F: drive embedding analysis."""
    analyzer = F_DriveEmbeddingAnalyzer()
    report = analyzer.run_full_analysis()

    if report:
        print("\n✅ Analysis completed successfully!")
        print("📄 Report saved: f_drive_embedding_comprehensive_report.json")

        # Return key metrics for script usage
        return {
            'success': True,
            'modalities_found': report['executive_summary']['total_modalities_found'],
            'total_embeddings': report['executive_summary']['total_embeddings_estimated'],
            'training_ready': report['executive_summary']['training_ready'],
            'compatibility_score': report['executive_summary']['b3_compatibility_score']
        }
    else:
        print("❌ Analysis failed!")
        return {'success': False}

if __name__ == "__main__":
    result = main()
    if not result['success']:
        sys.exit(1)
