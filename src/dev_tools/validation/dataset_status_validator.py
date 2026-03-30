#!/usr/bin/env python3
"""
Dataset Status Validator - ImpressionCore Championship Sprint

File: src/dev_tools/validation/dataset_status_validator.py
Purpose: Comprehensive dataset validation and organization for MVP launch
Created: 2025-06-10

This tool validates all datasets, ensures proper organization, and prepares
for immediate training commencement.
"""

import os
import sys
from pathlib import Path
import json
from typing import Dict, List, Tuple, Optional
import time
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Rich UI imports
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.text import Text
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    rprint = print

console = Console() if RICH_AVAILABLE else None

class DatasetStatusValidator:
    """Comprehensive dataset validation and organization system."""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.data_root = self.project_root / "src" / "data" / "datasets"
        self.validation_results = {
            "audio": {},
            "images": {},
            "text": {},
            "multimodal": {},
            "status": "initializing"
        }
        
    def print_header(self):
        """Print championship-style header."""
        if RICH_AVAILABLE:
            console.print(Panel(
                "[bold cyan]🚀 DATASET STATUS VALIDATOR - MVP CHAMPIONSHIP SPRINT! 🚀[/bold cyan]\n\n"
                "[yellow]Validating all datasets for immediate training commencement[/yellow]\n"
                f"[green]Project Root: {self.project_root}[/green]\n"
                f"[green]Datasets Root: {self.data_root}[/green]",
                title="[bold red]ImpressionCore-B1 Dataset Validator[/bold red]",
                border_style="cyan"
            ))
        else:
            print("🚀 DATASET STATUS VALIDATOR - MVP CHAMPIONSHIP SPRINT! 🚀")
            print(f"Project Root: {self.project_root}")
            print(f"Datasets Root: {self.data_root}")
            
    def validate_audio_datasets(self) -> Dict:
        """Validate audio datasets (LJSpeech, LibriSpeech alignments)."""
        audio_status = {
            "ljspeech": {"exists": False, "count": 0, "size_gb": 0},
            "librispeech_alignments": {"exists": False, "count": 0, "size_gb": 0},
            "total_audio_files": 0,
            "ready_for_training": False
        }
        
        # Check LJSpeech
        ljspeech_path = self.data_root / "audio" / "ljspeech" / "LJSpeech-1.1"
        if ljspeech_path.exists():
            wavs_path = ljspeech_path / "wavs"
            if wavs_path.exists():
                wav_files = list(wavs_path.glob("*.wav"))
                audio_status["ljspeech"]["exists"] = True
                audio_status["ljspeech"]["count"] = len(wav_files)
                audio_status["ljspeech"]["size_gb"] = self.calculate_directory_size(wavs_path)
                
        # Check LibriSpeech alignments
        alignments_path = self.data_root / "audio" / "alignments"
        if alignments_path.exists():
            alignment_dirs = [d for d in alignments_path.iterdir() if d.is_dir()]
            if alignment_dirs:
                audio_status["librispeech_alignments"]["exists"] = True
                audio_status["librispeech_alignments"]["count"] = len(alignment_dirs)
                audio_status["librispeech_alignments"]["size_gb"] = self.calculate_directory_size(alignments_path)
        
        # Calculate totals
        audio_status["total_audio_files"] = audio_status["ljspeech"]["count"]
        audio_status["ready_for_training"] = (
            audio_status["ljspeech"]["exists"] and 
            audio_status["ljspeech"]["count"] > 1000  # Minimum viable dataset
        )
        
        return audio_status
        
    def validate_image_datasets(self) -> Dict:
        """Validate image datasets (COCO 2017)."""
        image_status = {
            "coco_val2017": {"exists": False, "count": 0, "size_gb": 0},
            "coco_train2017": {"exists": False, "count": 0, "size_gb": 0},
            "coco_annotations": {"exists": False, "files": []},
            "total_image_files": 0,
            "ready_for_training": False
        }
        
        # Check COCO validation images
        coco_val_path = self.data_root / "images" / "coco2017" / "val2017"
        if coco_val_path.exists():
            jpg_files = list(coco_val_path.glob("*.jpg"))
            image_status["coco_val2017"]["exists"] = True
            image_status["coco_val2017"]["count"] = len(jpg_files)
            image_status["coco_val2017"]["size_gb"] = self.calculate_directory_size(coco_val_path)
            
        # Check COCO training images
        coco_train_path = self.data_root / "images" / "coco2017" / "train2017"
        if coco_train_path.exists():
            jpg_files = list(coco_train_path.glob("*.jpg"))
            image_status["coco_train2017"]["exists"] = True
            image_status["coco_train2017"]["count"] = len(jpg_files)
            image_status["coco_train2017"]["size_gb"] = self.calculate_directory_size(coco_train_path)
            
        # Check COCO annotations
        annotations_path = self.data_root / "images" / "coco2017" / "annotations"
        if annotations_path.exists():
            annotation_files = list(annotations_path.glob("**/*.json"))
            image_status["coco_annotations"]["exists"] = len(annotation_files) > 0
            image_status["coco_annotations"]["files"] = [f.name for f in annotation_files]
        
        # Calculate totals
        image_status["total_image_files"] = (
            image_status["coco_val2017"]["count"] + 
            image_status["coco_train2017"]["count"]
        )
        image_status["ready_for_training"] = (
            image_status["coco_val2017"]["exists"] and 
            image_status["coco_annotations"]["exists"] and
            image_status["coco_val2017"]["count"] > 1000  # Minimum viable dataset
        )
        
        return image_status
        
    def validate_text_datasets(self) -> Dict:
        """Validate text datasets."""
        text_status = {
            "sample_files": {"exists": False, "count": 0},
            "generated_text": {"exists": False, "count": 0},
            "total_text_files": 0,
            "ready_for_training": False
        }
        
        # Check sample text files
        text_path = self.data_root / "text"
        if text_path.exists():
            text_files = list(text_path.glob("*.txt")) + list(text_path.glob("*.json")) + list(text_path.glob("*.jsonl"))
            text_status["sample_files"]["exists"] = len(text_files) > 0
            text_status["sample_files"]["count"] = len(text_files)
            
        text_status["total_text_files"] = text_status["sample_files"]["count"]
        text_status["ready_for_training"] = text_status["sample_files"]["count"] > 0
        
        return text_status
        
    def calculate_directory_size(self, directory: Path) -> float:
        """Calculate directory size in GB."""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = Path(dirpath) / filename
                    try:
                        total_size += filepath.stat().st_size
                    except (OSError, FileNotFoundError):
                        continue
            return round(total_size / (1024**3), 2)  # Convert to GB
        except Exception:
            return 0.0
            
    def generate_training_recommendations(self, validation_results: Dict) -> List[str]:
        """Generate training recommendations based on dataset status."""
        recommendations = []
        
        audio_ready = validation_results["audio"]["ready_for_training"]
        image_ready = validation_results["images"]["ready_for_training"]
        text_ready = validation_results["text"]["ready_for_training"]
        
        if audio_ready and image_ready:
            recommendations.append("🔥 FULL MULTIMODAL TRAINING READY - All datasets validated!")
            recommendations.append("✅ Immediate Action: Start multimodal training with audio + image fusion")
            recommendations.append("🎯 Recommended: Begin with validation datasets for faster iteration")
        elif audio_ready:
            recommendations.append("🎵 AUDIO TRAINING READY - LJSpeech dataset validated")
            recommendations.append("✅ Immediate Action: Start audio-only training (TTS/STT)")
            recommendations.append("⚠️ Note: COCO images needed for full multimodal training")
        elif image_ready:
            recommendations.append("🖼️ IMAGE TRAINING READY - COCO dataset validated")
            recommendations.append("✅ Immediate Action: Start image captioning training")
            recommendations.append("⚠️ Note: Audio datasets needed for full multimodal training")
        else:
            recommendations.append("⚠️ LIMITED TRAINING READY - Using sample datasets only")
            recommendations.append("🔧 Immediate Action: Download core datasets (LJSpeech + COCO val2017)")
            recommendations.append("📋 Fallback: Use sample datasets for architecture validation")
            
        # Always add these
        recommendations.append("🚀 Memory Target: Optimized for GTX 1050 Ti (4GB VRAM)")
        recommendations.append("📊 Training Strategy: Start with 20% incremental loading")
        
        return recommendations
        
    def create_dataset_summary_report(self, validation_results: Dict) -> str:
        """Create a comprehensive summary report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# Dataset Status Report - ImpressionCore MVP Sprint
**Generated:** {timestamp}
**Status:** {"🔥 CHAMPIONSHIP READY!" if validation_results.get("overall_ready") else "⚠️ NEEDS ATTENTION"}

## 📊 Dataset Validation Summary

### Audio Datasets
- **LJSpeech**: {"✅" if validation_results["audio"]["ljspeech"]["exists"] else "❌"} {validation_results["audio"]["ljspeech"]["count"]} files ({validation_results["audio"]["ljspeech"]["size_gb"]} GB)
- **LibriSpeech Alignments**: {"✅" if validation_results["audio"]["librispeech_alignments"]["exists"] else "❌"} {validation_results["audio"]["librispeech_alignments"]["count"]} directories ({validation_results["audio"]["librispeech_alignments"]["size_gb"]} GB)
- **Training Ready**: {"✅ YES" if validation_results["audio"]["ready_for_training"] else "❌ NO"}

### Image Datasets  
- **COCO Val2017**: {"✅" if validation_results["images"]["coco_val2017"]["exists"] else "❌"} {validation_results["images"]["coco_val2017"]["count"]} files ({validation_results["images"]["coco_val2017"]["size_gb"]} GB)
- **COCO Train2017**: {"✅" if validation_results["images"]["coco_train2017"]["exists"] else "❌"} {validation_results["images"]["coco_train2017"]["count"]} files ({validation_results["images"]["coco_train2017"]["size_gb"]} GB)
- **COCO Annotations**: {"✅" if validation_results["images"]["coco_annotations"]["exists"] else "❌"} {len(validation_results["images"]["coco_annotations"]["files"])} files
- **Training Ready**: {"✅ YES" if validation_results["images"]["ready_for_training"] else "❌ NO"}

### Text Datasets
- **Sample Files**: {"✅" if validation_results["text"]["sample_files"]["exists"] else "❌"} {validation_results["text"]["sample_files"]["count"]} files
- **Training Ready**: {"✅ YES" if validation_results["text"]["ready_for_training"] else "❌ NO"}

## 🎯 Training Recommendations
"""
        
        for rec in validation_results.get("recommendations", []):
            report += f"- {rec}\n"
            
        report += f"""
## 🚀 Next Steps for MVP Sprint

1. **Environment Validation**: Ensure Python 3.13 + CUDA PyTorch ready
2. **Memory Optimization**: Validate 4GB VRAM constraints with sample batches  
3. **Training Pipeline**: Test end-to-end training with available datasets
4. **Performance Monitoring**: Implement rich UI progress tracking
5. **MVP Core Features**: Focus on text generation + web UI polish

**Status**: {"🏆 READY FOR CHAMPIONSHIP SPRINT!" if validation_results.get("overall_ready") else "🔧 PREP WORK NEEDED"}
"""
        
        return report
        
    def print_results_table(self, validation_results: Dict):
        """Print results in a beautiful table format."""
        if not RICH_AVAILABLE:
            print("\n=== DATASET VALIDATION RESULTS ===")
            print(f"Audio Ready: {validation_results['audio']['ready_for_training']}")
            print(f"Images Ready: {validation_results['images']['ready_for_training']}")
            print(f"Text Ready: {validation_results['text']['ready_for_training']}")
            return
            
        # Create results table
        table = Table(title="🏆 Dataset Validation Results - Championship Status", show_header=True, header_style="bold cyan")
        table.add_column("Dataset Type", style="yellow", width=15)
        table.add_column("Status", style="green", width=10)
        table.add_column("Files/Dirs", style="blue", width=12)
        table.add_column("Size (GB)", style="magenta", width=10)
        table.add_column("Training Ready", style="red", width=15)
        
        # Audio datasets
        audio = validation_results["audio"]
        table.add_row(
            "🎵 LJSpeech",
            "✅ Found" if audio["ljspeech"]["exists"] else "❌ Missing",
            str(audio["ljspeech"]["count"]),
            str(audio["ljspeech"]["size_gb"]),
            "🔥 READY" if audio["ljspeech"]["count"] > 1000 else "⚠️ Limited"
        )
        
        table.add_row(
            "🎵 LibriSpeech",
            "✅ Found" if audio["librispeech_alignments"]["exists"] else "❌ Missing", 
            str(audio["librispeech_alignments"]["count"]),
            str(audio["librispeech_alignments"]["size_gb"]),
            "✅ Ready" if audio["librispeech_alignments"]["exists"] else "❌ Missing"
        )
        
        # Image datasets
        images = validation_results["images"]
        table.add_row(
            "🖼️ COCO Val2017",
            "✅ Found" if images["coco_val2017"]["exists"] else "❌ Missing",
            str(images["coco_val2017"]["count"]),
            str(images["coco_val2017"]["size_gb"]),
            "🔥 READY" if images["coco_val2017"]["count"] > 1000 else "⚠️ Limited"
        )
        
        table.add_row(
            "🖼️ COCO Train2017",
            "✅ Found" if images["coco_train2017"]["exists"] else "❌ Missing",
            str(images["coco_train2017"]["count"]),
            str(images["coco_train2017"]["size_gb"]),
            "✅ Bonus" if images["coco_train2017"]["exists"] else "⚠️ Missing"
        )
        
        # Text datasets
        text = validation_results["text"]
        table.add_row(
            "📝 Text Samples",
            "✅ Found" if text["sample_files"]["exists"] else "❌ Missing",
            str(text["sample_files"]["count"]),
            "< 0.1",
            "✅ Basic" if text["sample_files"]["exists"] else "❌ Missing"
        )
        
        console.print("\n")
        console.print(table)
        
    def run_validation(self) -> Dict:
        """Run complete dataset validation."""
        self.print_header()
        
        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                
                task1 = progress.add_task("[cyan]Validating audio datasets...", total=None)
                self.validation_results["audio"] = self.validate_audio_datasets()
                progress.update(task1, completed=True)
                
                task2 = progress.add_task("[cyan]Validating image datasets...", total=None)
                self.validation_results["images"] = self.validate_image_datasets()
                progress.update(task2, completed=True)
                
                task3 = progress.add_task("[cyan]Validating text datasets...", total=None)
                self.validation_results["text"] = self.validate_text_datasets()
                progress.update(task3, completed=True)
                
                task4 = progress.add_task("[cyan]Generating recommendations...", total=None)
                self.validation_results["recommendations"] = self.generate_training_recommendations(self.validation_results)
                progress.update(task4, completed=True)
        else:
            print("Validating audio datasets...")
            self.validation_results["audio"] = self.validate_audio_datasets()
            print("Validating image datasets...")
            self.validation_results["images"] = self.validate_image_datasets()
            print("Validating text datasets...")
            self.validation_results["text"] = self.validate_text_datasets()
            print("Generating recommendations...")
            self.validation_results["recommendations"] = self.generate_training_recommendations(self.validation_results)
        
        # Determine overall readiness
        self.validation_results["overall_ready"] = (
            self.validation_results["audio"]["ready_for_training"] or
            self.validation_results["images"]["ready_for_training"]
        )
        
        self.validation_results["status"] = "completed"
        
        return self.validation_results
        
    def save_results(self, validation_results: Dict):
        """Save validation results to memlog."""
        # Create report
        report = self.create_dataset_summary_report(validation_results)
        
        # Save to memlog
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        memlog_path = self.project_root / "src" / "memlog" / f"dataset_validation_report_{timestamp}.md"
        
        try:
            with open(memlog_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            if RICH_AVAILABLE:
                console.print(f"\n[green]✅ Report saved to: {memlog_path}[/green]")
            else:
                print(f"\n✅ Report saved to: {memlog_path}")
                
        except Exception as e:
            if RICH_AVAILABLE:
                console.print(f"\n[red]❌ Error saving report: {e}[/red]")
            else:
                print(f"\n❌ Error saving report: {e}")

def main():
    """Main execution function."""
    validator = DatasetStatusValidator()
    
    try:
        # Run validation
        results = validator.run_validation()
        
        # Print results
        validator.print_results_table(results)
        
        # Print recommendations
        if RICH_AVAILABLE:
            console.print("\n")
            console.print(Panel(
                "\n".join(results["recommendations"]),
                title="[bold yellow]🎯 Championship Training Recommendations[/bold yellow]",
                border_style="yellow"
            ))
        else:
            print("\n=== TRAINING RECOMMENDATIONS ===")
            for rec in results["recommendations"]:
                print(f"  {rec}")
        
        # Save results
        validator.save_results(results)
        
        # Final status
        if results["overall_ready"]:
            if RICH_AVAILABLE:
                console.print("\n[bold green]🏆 CHAMPIONSHIP STATUS: READY FOR MVP SPRINT! 🚀[/bold green]")
            else:
                print("\n🏆 CHAMPIONSHIP STATUS: READY FOR MVP SPRINT! 🚀")
        else:
            if RICH_AVAILABLE:
                console.print("\n[bold yellow]⚠️ PREP STATUS: SOME DATASETS NEED ATTENTION[/bold yellow]")
            else:
                print("\n⚠️ PREP STATUS: SOME DATASETS NEED ATTENTION")
                
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"\n[bold red]❌ VALIDATION ERROR: {e}[/bold red]")
        else:
            print(f"\n❌ VALIDATION ERROR: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
