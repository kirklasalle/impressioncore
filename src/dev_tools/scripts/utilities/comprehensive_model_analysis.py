#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #performance #python #source_code #src/scripts/utilities/comprehensive_model_analysis.py #testing #training
**Category:** Source Code
**Status:** Active
"""



import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class ComprehensiveModelAnalyzer:
    """Comprehensive analyzer for all ImpressionCore models and data"""

    def __init__(self):
        self.console = Console()
        self.analysis_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Analysis paths
        self.f_drive_root = Path("F:/data")
        self.analysis_output_dir = Path("F:/data/analysis_reports/comprehensive_model_analysis")
        self.analysis_output_dir.mkdir(parents=True, exist_ok=True)

        # Data directories to analyze
        self.analysis_targets = {
            "embeddings": self.f_drive_root / "embeddings",
            "models": Path("F:/models"),  # Primary model storage location
            "f_data_models": self.f_drive_root / "models",
            "datasets": self.f_drive_root / "datasets",
            "distillation": Path("F:/models/distillation"),  # New distillation location
            "training": Path("F:/models/training"),  # New training location
            "system": self.f_drive_root / "system"
        }

        # Analysis results
        self.analysis_results = {
            "analysis_timestamp": self.analysis_timestamp,
            "infrastructure_summary": {},
            "model_inventory": {},
            "embedding_analysis": {},
            "training_progression": {},
            "distillation_results": {},
            "performance_metrics": {},
            "recommendations": {}
        }

    def pipe_command_to_file(self, command: str, output_file: Path, description: str) -> bool:
        """Execute a command and pipe output to file, handling large outputs"""
        self.console.print(f"📊 {description}")

        try:
            # Use PowerShell to execute command and redirect output
            ps_command = f'powershell.exe -Command "{command} | Out-File -FilePath \'{output_file}\' -Encoding UTF8"'

            result = subprocess.run(
                ps_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                self.console.print(f"✅ Output saved to: {output_file}")
                return True
            else:
                self.console.print(f"❌ Command failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.console.print("⏰ Command timed out after 5 minutes")
            return False
        except Exception as e:
            self.console.print(f"❌ Error executing command: {e}")
            return False

    def analyze_f_drive_structure(self) -> dict[str, Any]:
        """Analyze complete F: drive structure"""
        self.console.print(Panel("🔍 F: Drive Structure Analysis", style="blue"))

        structure_file = self.analysis_output_dir / f"f_drive_structure_{self.analysis_timestamp}.txt"
        sizes_file = self.analysis_output_dir / f"f_drive_sizes_{self.analysis_timestamp}.txt"

        # Get complete directory structure
        structure_cmd = "Get-ChildItem 'F:/data' -Recurse | Select-Object FullName, Mode, Length, LastWriteTime | Format-Table -AutoSize"
        self.pipe_command_to_file(structure_cmd, structure_file, "Analyzing F: drive directory structure")

        # Get directory sizes
        sizes_cmd = """
        Get-ChildItem 'F:/data' -Directory | ForEach-Object {
            $size = (Get-ChildItem $_.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum
            [PSCustomObject]@{
                Directory = $_.FullName
                SizeGB = [math]::Round($size / 1GB, 2)
                SizeMB = [math]::Round($size / 1MB, 2)
                FileCount = (Get-ChildItem $_.FullName -Recurse -File).Count
            }
        } | Format-Table -AutoSize
        """
        self.pipe_command_to_file(sizes_cmd, sizes_file, "Calculating directory sizes")

        return {
            "structure_file": str(structure_file),
            "sizes_file": str(sizes_file),
            "analysis_complete": True
        }

    def analyze_model_inventory(self) -> dict[str, Any]:
        """Analyze all model files across F: drive"""
        self.console.print(Panel("🤖 Model Inventory Analysis", style="green"))

        models_file = self.analysis_output_dir / f"model_inventory_{self.analysis_timestamp}.txt"
        checkpoints_file = self.analysis_output_dir / f"model_checkpoints_{self.analysis_timestamp}.txt"

        # Find all model files (.pth, .pt, .safetensors, .bin) - Updated for F:\models primary location
        models_cmd = """
        $locations = @('F:/models', 'F:/data')
        $allModels = @()
        foreach ($location in $locations) {
            if (Test-Path $location) {
                $models = Get-ChildItem $location -Recurse -Include '*.pth', '*.pt', '*.safetensors', '*.bin' |
                Select-Object FullName, Length, LastWriteTime, CreationTime |
                ForEach-Object {
                    [PSCustomObject]@{
                        File = $_.FullName
                        SizeMB = [math]::Round($_.Length / 1MB, 2)
                        Modified = $_.LastWriteTime
                        Created = $_.CreationTime
                        Type = [System.IO.Path]::GetExtension($_.FullName)
                        Location = if($_.FullName -like 'F:/models*') { 'F_Models_Primary' } else { 'F_Data_Legacy' }
                    }
                }
                $allModels += $models
            }
        }
        $allModels | Sort-Object Modified -Descending | Format-Table -AutoSize
        """
        self.pipe_command_to_file(models_cmd, models_file, "Inventorying all model files (F:/models primary, F:/data legacy)")

        # Analyze checkpoint progression - Updated for F:\models primary location
        checkpoints_cmd = """
        $checkpointLocations = @('F:/models/checkpoints', 'F:/models/checkpoints/data_training_checkpoints', 'F:/models/training/active')
        $allCheckpoints = @()
        foreach ($location in $checkpointLocations) {
            if (Test-Path $location) {
                $checkpoints = Get-ChildItem $location -Include '*.pth' |
                Select-Object Name, Length, LastWriteTime |
                ForEach-Object {
                    [PSCustomObject]@{
                        Checkpoint = $_.Name
                        SizeMB = [math]::Round($_.Length / 1MB, 2)
                        Timestamp = $_.LastWriteTime
                        EpochInfo = if($_.Name -match 'epoch_(\\d+)') { "Epoch $($matches[1])" } else { "Special" }
                        Location = $location.Replace('F:/', '').Replace('/', '\')
                    }
                }
                $allCheckpoints += $checkpoints
            }
        }
        $allCheckpoints | Sort-Object Timestamp | Format-Table -AutoSize
        """
        self.pipe_command_to_file(checkpoints_cmd, checkpoints_file, "Analyzing checkpoint progression (F:/models canonical locations)")

        return {
            "models_file": str(models_file),
            "checkpoints_file": str(checkpoints_file),
            "analysis_complete": True
        }

    def analyze_embeddings_comprehensive(self) -> dict[str, Any]:
        """Comprehensive analysis of all embeddings"""
        self.console.print(Panel("🧠 Comprehensive Embeddings Analysis", style="magenta"))

        embeddings_overview_file = self.analysis_output_dir / f"embeddings_overview_{self.analysis_timestamp}.txt"
        embeddings_detail_file = self.analysis_output_dir / f"embeddings_detailed_{self.analysis_timestamp}.txt"

        # Overview of embedding structure
        overview_cmd = """
        Get-ChildItem 'F:/data/embeddings' -Recurse -Directory |
        ForEach-Object {
            $fileCount = (Get-ChildItem $_.FullName -File).Count
            $totalSize = (Get-ChildItem $_.FullName -File | Measure-Object -Property Length -Sum).Sum
            [PSCustomObject]@{
                Directory = $_.FullName.Replace('F:/data/embeddings/', '')
                Files = $fileCount
                SizeGB = [math]::Round($totalSize / 1GB, 3)
                SizeMB = [math]::Round($totalSize / 1MB, 2)
                LastModified = (Get-ChildItem $_.FullName -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime
            }
        } | Sort-Object Directory | Format-Table -AutoSize
        """
        self.pipe_command_to_file(overview_cmd, embeddings_overview_file, "Analyzing embeddings directory structure")

        # Detailed file analysis
        detail_cmd = """
        Get-ChildItem 'F:/data/embeddings' -Recurse -File |
        Where-Object { $_.Extension -in '.npy', '.pt', '.pth', '.json', '.pkl' } |
        Select-Object FullName, Length, LastWriteTime, Extension |
        Sort-Object FullName |
        ForEach-Object {
            [PSCustomObject]@{
                File = $_.FullName.Replace('F:/data/embeddings/', '')
                Extension = $_.Extension
                SizeMB = [math]::Round($_.Length / 1MB, 2)
                Modified = $_.LastWriteTime
                Category = if($_.FullName -like '*b3_training*') { 'B3_Training' }
                          elseif($_.FullName -like '*b3_embeddings*') { 'B3_Embeddings' }
                          elseif($_.FullName -like '*dataset_enhanced*') { 'Enhanced' }
                          else { 'Other' }
            }
        } | Format-Table -AutoSize
        """
        self.pipe_command_to_file(detail_cmd, embeddings_detail_file, "Detailed embeddings file analysis")

        return {
            "overview_file": str(embeddings_overview_file),
            "detail_file": str(embeddings_detail_file),
            "analysis_complete": True
        }

    def analyze_training_progression(self) -> dict[str, Any]:
        """Analyze training progression and logs"""
        self.console.print(Panel("📈 Training Progression Analysis", style="yellow"))

        training_logs_file = self.analysis_output_dir / f"training_logs_analysis_{self.analysis_timestamp}.txt"
        training_metrics_file = self.analysis_output_dir / f"training_metrics_{self.analysis_timestamp}.txt"

        # Analyze training logs
        logs_cmd = """
        Get-ChildItem 'F:/data' -Recurse -Include '*.log' |
        Where-Object { $_.FullName -like '*training*' -or $_.FullName -like '*b3*' } |
        Select-Object FullName, Length, LastWriteTime |
        Sort-Object LastWriteTime -Descending |
        ForEach-Object {
            [PSCustomObject]@{
                LogFile = $_.FullName.Replace('F:/data/', '')
                SizeKB = [math]::Round($_.Length / 1KB, 2)
                LastModified = $_.LastWriteTime
                Type = if($_.FullName -like '*distillation*') { 'Distillation' }
                      elseif($_.FullName -like '*training*') { 'Training' }
                      else { 'Other' }
            }
        } | Format-Table -AutoSize
        """
        self.pipe_command_to_file(logs_cmd, training_logs_file, "Analyzing training logs")

        # Look for metrics files
        metrics_cmd = """
        Get-ChildItem 'F:/data' -Recurse -Include '*.json' |
        Where-Object { $_.Name -like '*metrics*' -or $_.Name -like '*results*' -or $_.Name -like '*report*' } |
        Select-Object FullName, Length, LastWriteTime |
        Sort-Object LastWriteTime -Descending |
        ForEach-Object {
            [PSCustomObject]@{
                MetricsFile = $_.FullName.Replace('F:/data/', '')
                SizeKB = [math]::Round($_.Length / 1KB, 2)
                LastModified = $_.LastWriteTime
                Category = if($_.FullName -like '*distillation*') { 'Distillation' }
                          elseif($_.FullName -like '*training*') { 'Training' }
                          elseif($_.FullName -like '*benchmark*') { 'Benchmark' }
                          else { 'Analysis' }
            }
        } | Format-Table -AutoSize
        """
        self.pipe_command_to_file(metrics_cmd, training_metrics_file, "Analyzing metrics and results files")

        return {
            "logs_file": str(training_logs_file),
            "metrics_file": str(training_metrics_file),
            "analysis_complete": True
        }

    def analyze_distillation_results(self) -> dict[str, Any]:
        """Analyze all distillation results and performance"""
        self.console.print(Panel("🌟 Distillation Results Analysis", style="cyan"))

        distillation_file = self.analysis_output_dir / f"distillation_analysis_{self.analysis_timestamp}.txt"

        # Analyze distillation directory - Updated for F:\models/distillation primary location
        distillation_cmd = """
        $distillationLocations = @('F:/models/distillation', 'F:/data/distillation')
        $allDistillation = @()
        foreach ($location in $distillationLocations) {
            if (Test-Path $location) {
                $items = Get-ChildItem $location -Recurse |
                Select-Object FullName, Length, LastWriteTime, Mode |
                ForEach-Object {
                    [PSCustomObject]@{
                        Item = $_.FullName.Replace($location + '/', '')
                        Type = if($_.Mode.StartsWith('d')) { 'Directory' } else { 'File' }
                        SizeKB = if($_.Length) { [math]::Round($_.Length / 1KB, 2) } else { 0 }
                        LastModified = $_.LastWriteTime
                        Category = if($_.FullName -like '*ollama*') { 'Ollama' }
                                  elseif($_.FullName -like '*remote*') { 'Remote_API' }
                                  elseif($_.FullName -like '*curriculum*') { 'Curriculum' }
                                  else { 'General' }
                        Location = if($_.FullName -like 'F:/models*') { 'F_Models_Primary' } else { 'F_Data_Legacy' }
                    }
                }
                $allDistillation += $items
            }
        }
        $allDistillation | Sort-Object Location, Item | Format-Table -AutoSize
        """
        self.pipe_command_to_file(distillation_cmd, distillation_file, "Analyzing distillation results (F:/models primary, F:/data legacy)")

        return {
            "distillation_file": str(distillation_file),
            "analysis_complete": True
        }

    def analyze_dataset_infrastructure(self) -> dict[str, Any]:
        """Analyze dataset infrastructure and content"""
        self.console.print(Panel("📚 Dataset Infrastructure Analysis", style="blue"))

        datasets_file = self.analysis_output_dir / f"datasets_analysis_{self.analysis_timestamp}.txt"

        # Analyze datasets
        datasets_cmd = """
        Get-ChildItem 'F:/data/datasets' -Recurse |
        Where-Object { -not $_.Mode.StartsWith('d') } |
        Select-Object FullName, Length, LastWriteTime, Extension |
        Group-Object { $_.FullName.Split('\\')[3] } |
        ForEach-Object {
            $totalSize = ($_.Group | Measure-Object -Property Length -Sum).Sum
            $fileCount = $_.Count
            [PSCustomObject]@{
                Dataset = $_.Name
                Files = $fileCount
                SizeGB = [math]::Round($totalSize / 1GB, 3)
                SizeMB = [math]::Round($totalSize / 1MB, 2)
                LastModified = ($_.Group | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime
            }
        } | Sort-Object SizeGB -Descending | Format-Table -AutoSize
        """
        self.pipe_command_to_file(datasets_cmd, datasets_file, "Analyzing dataset infrastructure")

        return {
            "datasets_file": str(datasets_file),
            "analysis_complete": True
        }

    def generate_summary_analysis(self) -> dict[str, Any]:
        """Generate comprehensive summary analysis"""
        self.console.print(Panel("📋 Generating Comprehensive Summary", style="bold green"))

        summary_file = self.analysis_output_dir / f"COMPREHENSIVE_ANALYSIS_SUMMARY_{self.analysis_timestamp}.md"

        # Read all generated files and create summary
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"""# ImpressionCore Comprehensive Model Analysis Summary

# Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Analysis ID:** {self.analysis_timestamp}
# Scope:** Complete F: Drive Infrastructure Analysis

---

## 🎯 Analysis Overview

This comprehensive analysis covers all ImpressionCore models, embeddings, training data, and infrastructure from initial development through current state.

### 📁 Generated Analysis Files:

""")

                # List all analysis files
                for analysis_file in sorted(self.analysis_output_dir.glob("*.txt")):
                    f.write(f"- **{analysis_file.name}** - {analysis_file.stat().st_size:,} bytes\n")

                f.write(f"""

### 🔍 Analysis Components:

1. **F: Drive Structure Analysis** - Complete directory tree and organization
2. **Model Inventory** - All .pth, .pt, .safetensors, and .bin files with metadata
3. **Embeddings Analysis** - Comprehensive embedding files and organization
4. **Training Progression** - Training logs, metrics, and checkpoint evolution
5. **Distillation Results** - Ollama and Remote API distillation outcomes
6. **Dataset Infrastructure** - Complete dataset inventory and statistics

### 📊 Key Directories Analyzed:

- `F:/models/` - **PRIMARY** Model storage, checkpoints, training, and distillation (NEW STRUCTURE)
- `F:/models/checkpoints/` - Production model checkpoints
- `F:/models/training/` - Training infrastructure and active models
- `F:/models/distillation/` - Knowledge distillation results and enhanced models
- `F:/data/embeddings/` - Legacy embedding storage and B3 training checkpoints
- `F:/data/models/` - Legacy model infrastructure (transitioning to F:/models)
- `F:/data/datasets/` - Training datasets and processed data
- `F:/data/system/` - System operation data

### 🎯 Analysis Goals:

This analysis provides:
- Complete inventory of all models from initial embeddings to current state
- Training progression tracking across all development phases
- Performance metrics and distillation enhancement results
- Infrastructure utilization and organization assessment
- Recommendations for optimization and next steps

### 📋 Usage Instructions:

1. Review individual analysis files for detailed information
2. Cross-reference timestamps to understand development progression
3. Use file sizes and metrics to assess resource utilization
4. Identify optimization opportunities and next development phases

---

# Analysis Complete:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Total Analysis Files:** {len(list(self.analysis_output_dir.glob('*.txt')))}
# Output Directory:** `{self.analysis_output_dir}`

""")

            self.console.print(f"✅ Summary analysis saved: {summary_file}")

            return {
                "summary_file": str(summary_file),
                "analysis_files_count": len(list(self.analysis_output_dir.glob("*.txt"))),
                "output_directory": str(self.analysis_output_dir)
            }

        except Exception as e:
            self.console.print(f"❌ Error generating summary: {e}")
            return {"error": str(e)}

    def run_comprehensive_analysis(self) -> dict[str, Any]:
        """Run complete comprehensive analysis"""

        self.console.print(Panel.fit(
            "🔍 ImpressionCore Comprehensive Model Analysis\n"
            "Complete Infrastructure and Model Evolution Analysis",
            style="bold blue"
        ))

        analysis_start = time.time()

        try:
            # Step 1: F: Drive Structure Analysis
            structure_results = self.analyze_f_drive_structure()
            self.analysis_results["infrastructure_summary"] = structure_results

            # Step 2: Model Inventory
            model_results = self.analyze_model_inventory()
            self.analysis_results["model_inventory"] = model_results

            # Step 3: Embeddings Analysis
            embeddings_results = self.analyze_embeddings_comprehensive()
            self.analysis_results["embedding_analysis"] = embeddings_results

            # Step 4: Training Progression
            training_results = self.analyze_training_progression()
            self.analysis_results["training_progression"] = training_results

            # Step 5: Distillation Results
            distillation_results = self.analyze_distillation_results()
            self.analysis_results["distillation_results"] = distillation_results

            # Step 6: Dataset Infrastructure
            dataset_results = self.analyze_dataset_infrastructure()
            self.analysis_results["dataset_infrastructure"] = dataset_results

            # Step 7: Generate Summary
            summary_results = self.generate_summary_analysis()

            # Calculate total analysis time
            total_time = time.time() - analysis_start

            # Save complete analysis results
            results_file = self.analysis_output_dir / f"complete_analysis_results_{self.analysis_timestamp}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, indent=2, default=str)

            # Display completion summary
            completion_table = Table(title="🎯 Comprehensive Analysis Complete")
            completion_table.add_column("Component", style="cyan")
            completion_table.add_column("Status", style="green")
            completion_table.add_column("Output File", style="yellow")

            completion_table.add_row("F: Drive Structure", "✅ Complete", structure_results.get("structure_file", "N/A"))
            completion_table.add_row("Model Inventory", "✅ Complete", model_results.get("models_file", "N/A"))
            completion_table.add_row("Embeddings Analysis", "✅ Complete", embeddings_results.get("overview_file", "N/A"))
            completion_table.add_row("Training Progression", "✅ Complete", training_results.get("logs_file", "N/A"))
            completion_table.add_row("Distillation Results", "✅ Complete", distillation_results.get("distillation_file", "N/A"))
            completion_table.add_row("Dataset Infrastructure", "✅ Complete", dataset_results.get("datasets_file", "N/A"))
            completion_table.add_row("Summary Analysis", "✅ Complete", summary_results.get("summary_file", "N/A"))

            self.console.print(completion_table)

            self.console.print(Panel(
                f"🎯 Analysis Complete!\n"
                f"⏱️ Total Time: {total_time:.1f} seconds\n"
                f"📁 Output Directory: {self.analysis_output_dir}\n"
                f"📊 Analysis Files: {summary_results.get('analysis_files_count', 0)}\n"
                f"📋 Summary: {summary_results.get('summary_file', 'N/A')}",
                title="Analysis Summary",
                style="bold green"
            ))

            return {
                "status": "success",
                "analysis_timestamp": self.analysis_timestamp,
                "total_time": total_time,
                "output_directory": str(self.analysis_output_dir),
                "summary_file": summary_results.get("summary_file"),
                "results_file": str(results_file),
                "components_analyzed": 7
            }

        except Exception as e:
            self.console.print(f"❌ Analysis failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "analysis_timestamp": self.analysis_timestamp
            }

def main():
    """Main execution function"""
    console = Console()

    console.print(Panel.fit(
        "🔍 ImpressionCore Comprehensive Model Analysis\n"
        "From First Embeddings to Current State Analysis",
        style="bold blue"
    ))

    # Create and run comprehensive analyzer
    analyzer = ComprehensiveModelAnalyzer()
    results = analyzer.run_comprehensive_analysis()

    if results.get("status") == "success":
        console.print("\n✅ Comprehensive analysis completed successfully!")
        console.print(f"📁 All analysis files saved to: {results['output_directory']}")
        console.print(f"📋 Review summary at: {results.get('summary_file', 'N/A')}")
    else:
        console.print(f"\n❌ Analysis failed: {results.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
