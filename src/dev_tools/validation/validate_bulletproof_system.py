#!/usr/bin/env python3
"""
ImpressionCore-B1 System Validation & Status Report
==================================================

Comprehensive validation of the bulletproof training system.
Generates detailed status report for production readiness.

Author: ImpressionCore Team
Date: 2025-06-11
Version: 1.0.0 - Production Validation
"""

import os
import sys
import json
import time
import torch
import psutil
import subprocess
from pathlib import Path
from datetime import datetime
import importlib.util

# Rich imports for beautiful output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress
    from rich.text import Text
    from rich.align import Align
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

def create_console():
    """Create Rich console or fallback"""
    if RICH_AVAILABLE:
        return Console()
    else:
        class FallbackConsole:
            def print(self, *args, **kwargs):
                print(*args)
        return FallbackConsole()

def check_file_exists(filepath):
    """Check if file exists and return status"""
    path = Path(filepath)
    return path.exists(), path.stat().st_size if path.exists() else 0

def check_import(module_name, file_path=None):
    """Check if module can be imported"""
    try:
        if file_path:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        else:
            __import__(module_name)
        return True, "OK"
    except Exception as e:
        return False, str(e)

def check_cuda_status():
    """Check CUDA availability and GPU info"""
    try:
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            return True, {
                "available": True,
                "gpu_name": gpu_name,
                "gpu_memory_gb": round(gpu_memory, 1),
                "device_count": torch.cuda.device_count()
            }
        else:
            return False, {"available": False, "reason": "CUDA not available"}
    except Exception as e:
        return False, {"available": False, "error": str(e)}

def check_datasets():
    """Check dataset availability"""
    base_path = Path("src/data/minimal_datasets")
    
    datasets = {
        "text": {"path": base_path / "text_samples", "expected": 5},
        "images": {"path": base_path / "images", "expected": 10},
        "audio": {"path": base_path / "audio", "expected": 20}
    }
    
    results = {}
    for name, info in datasets.items():
        if info["path"].exists():
            files = list(info["path"].glob("*"))
            # Filter out metadata files
            if name == "images":
                files = [f for f in files if f.suffix.lower() in ['.jpg', '.jpeg', '.png']]
            elif name == "audio":
                files = [f for f in files if f.suffix.lower() == '.wav']
            elif name == "text":
                files = [f for f in files if f.suffix.lower() == '.txt']
            
            results[name] = {
                "exists": True,
                "count": len(files),
                "expected": info["expected"],
                "status": "OK" if len(files) >= info["expected"] else "INSUFFICIENT"
            }
        else:
            results[name] = {
                "exists": False,
                "count": 0,
                "expected": info["expected"],
                "status": "MISSING"
            }
    
    return results

def run_system_validation():
    """Run comprehensive system validation"""
    console = create_console()
    
    # Header
    if RICH_AVAILABLE:
        console.print(Panel(
            Align.center(
                Text("🚀 ImpressionCore-B1 System Validation\n\n" +
                     "Bulletproof Training System Status Report\n" +
                     f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                     style="bold white")
            ),
            title="System Validation",
            border_style="cyan"
        ))
    else:
        console.print("=== ImpressionCore-B1 System Validation ===")
        console.print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    validation_results = {}
    
    # 1. Check Core Files
    console.print("\n🔍 Checking Core System Files...")
    core_files = {
        "Training Launcher": "bulletproof_training_launcher.py",
        "Incremental Trainer": "src/training/bulletproof_incremental_trainer.py",
        "Dataset Loaders": "src/training/multimodal_dataset_loaders.py",
        "Memory Tracker": "src/training/memory_tracker.py",
        "B1 Model": "src/training/models/architectures/b1/impressioncore_b1.py",
        "CLI Interface": "src/interfaces/cli/impressioncore_b1_cuda_cli.py"
    }
    
    file_results = {}
    for name, filepath in core_files.items():
        exists, size = check_file_exists(filepath)
        file_results[name] = {
            "exists": exists,
            "size_kb": round(size / 1024, 1) if exists else 0,
            "path": filepath
        }
    
    validation_results["core_files"] = file_results
    
    # 2. Check Python Dependencies
    console.print("\n📦 Checking Python Dependencies...")
    dependencies = [
        "torch", "torchvision", "numpy", "PIL", "librosa", 
        "psutil", "rich", "asyncio"
    ]
    
    dep_results = {}
    for dep in dependencies:
        success, message = check_import(dep)
        dep_results[dep] = {"available": success, "message": message}
    
    validation_results["dependencies"] = dep_results
    
    # 3. Check CUDA Status
    console.print("\n🎮 Checking CUDA & GPU Status...")
    cuda_success, cuda_info = check_cuda_status()
    validation_results["cuda"] = cuda_info
    
    # 4. Check Datasets
    console.print("\n📊 Checking Training Datasets...")
    dataset_results = check_datasets()
    validation_results["datasets"] = dataset_results
    
    # 5. Check System Resources
    console.print("\n💻 Checking System Resources...")
    system_info = {
        "cpu_count": psutil.cpu_count(),
        "memory_gb": round(psutil.virtual_memory().total / (1024**3), 1),
        "disk_free_gb": round(psutil.disk_usage('.').free / (1024**3), 1),
        "python_version": sys.version.split()[0],
        "platform": sys.platform
    }
    validation_results["system"] = system_info
    
    # 6. Generate Report
    console.print("\n📋 Generating Validation Report...")
    
    if RICH_AVAILABLE:
        # Create status table
        table = Table(title="System Validation Results")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Details", style="dim")
        
        # Core Files Status
        all_files_ok = all(info["exists"] for info in file_results.values())
        table.add_row(
            "Core Files", 
            "✅ PASS" if all_files_ok else "❌ FAIL",
            f"{sum(1 for info in file_results.values() if info['exists'])}/{len(file_results)} files found"
        )
        
        # Dependencies Status
        all_deps_ok = all(info["available"] for info in dep_results.values())
        table.add_row(
            "Dependencies",
            "✅ PASS" if all_deps_ok else "❌ FAIL", 
            f"{sum(1 for info in dep_results.values() if info['available'])}/{len(dep_results)} modules available"
        )
        
        # CUDA Status
        table.add_row(
            "CUDA Support",
            "✅ PASS" if cuda_success else "❌ FAIL",
            cuda_info.get("gpu_name", "Not available") if cuda_success else "CUDA not detected"
        )
        
        # Dataset Status
        all_datasets_ok = all(info["status"] == "OK" for info in dataset_results.values())
        table.add_row(
            "Training Data",
            "✅ PASS" if all_datasets_ok else "⚠️  WARN",
            f"Text: {dataset_results['text']['count']}, Images: {dataset_results['images']['count']}, Audio: {dataset_results['audio']['count']}"
        )
        
        # System Resources
        memory_sufficient = system_info["memory_gb"] >= 8
        disk_sufficient = system_info["disk_free_gb"] >= 10
        table.add_row(
            "System Resources",
            "✅ PASS" if memory_sufficient and disk_sufficient else "⚠️  WARN",
            f"RAM: {system_info['memory_gb']}GB, Disk: {system_info['disk_free_gb']}GB"
        )
        
        console.print(table)
    else:
        # Fallback text report
        console.print("\n=== VALIDATION RESULTS ===")
        console.print(f"Core Files: {sum(1 for info in file_results.values() if info['exists'])}/{len(file_results)} OK")
        console.print(f"Dependencies: {sum(1 for info in dep_results.values() if info['available'])}/{len(dep_results)} OK")
        console.print(f"CUDA: {'OK' if cuda_success else 'FAIL'}")
        console.print(f"Datasets: {sum(1 for info in dataset_results.values() if info['status'] == 'OK')}/3 OK")
    
    # 7. Overall Status
    overall_status = (
        all(info["exists"] for info in file_results.values()) and
        all(info["available"] for info in dep_results.values()) and
        cuda_success and
        all(info["status"] in ["OK", "INSUFFICIENT"] for info in dataset_results.values())
    )
    
    validation_results["overall_status"] = overall_status
    validation_results["timestamp"] = datetime.now().isoformat()
    
    # Final status message
    if RICH_AVAILABLE:
        status_color = "green" if overall_status else "red"
        status_text = "🚀 PRODUCTION READY" if overall_status else "❌ ISSUES DETECTED"
        console.print(f"\n[{status_color}]{status_text}[/{status_color}]")
        
        if overall_status:
            console.print(Panel(
                "✅ System validation completed successfully!\n\n" +
                "Your ImpressionCore-B1 system is ready for production training.\n" +
                "Run: python bulletproof_training_launcher.py",
                title="Ready for Training",
                border_style="green"
            ))
        else:
            console.print(Panel(
                "❌ System validation found issues!\n\n" +
                "Please resolve the issues above before training.\n" +
                "Check the documentation for troubleshooting steps.",
                title="Issues Detected",
                border_style="red"
            ))
    else:
        status_text = "PRODUCTION READY" if overall_status else "ISSUES DETECTED"
        console.print(f"\n=== {status_text} ===")
    
    # Save validation report
    report_path = f"src/memlog/system_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(validation_results, f, indent=2)
    
    console.print(f"\n📁 Validation report saved: {report_path}")
    
    return overall_status

if __name__ == "__main__":
    success = run_system_validation()
    sys.exit(0 if success else 1)
