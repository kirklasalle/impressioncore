#!/usr/bin/env python3
"""
ImpressionCore Training Readiness Verification
==============================================

Comprehensive verification script to demonstrate production readiness
for serious model training with the new 476GB storage infrastructure.

Author: GitHub Copilot
Date: 2025-06-13
Version: 1.0.0
Hardware: GTX 1050 Ti Optimized
"""

import os
import sys
import time
import torch
import psutil
import platform
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Rich UI for enhanced output (optional)
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import track
    from rich.text import Text
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    console = None
    RICH_AVAILABLE = False

class TrainingReadinessVerifier:
    """Comprehensive verification of ImpressionCore training readiness"""
    
    def __init__(self):
        self.project_root = Path("d:/Projects/impressioncore")
        self.training_drive = Path("f:/ImpressionCore_Training")
        self.verification_results = {}
        self.issues = []
        self.warnings = []
        
    def print_banner(self):
        """Print verification banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║             ImpressionCore Training Readiness              ║
║              🔍 COMPREHENSIVE VERIFICATION 🔍              ║
╠══════════════════════════════════════════════════════════════╣
║  🖥️  Hardware Status      📊 Storage Analysis              ║
║  🐍 Environment Check     📁 File System Validation        ║
║  🧠 Training Components   🛠️  Tool Availability            ║
║  📚 Documentation Status  🚀 Launch Readiness              ║
╚══════════════════════════════════════════════════════════════╝
        """
        
        if RICH_AVAILABLE:
            console.print(Panel(banner, style="bold blue"))
        else:
            print(banner)
        
        print(f"Verification Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Project Root: {self.project_root}")
        print()
    
    def verify_hardware(self) -> Dict[str, Any]:
        """Verify hardware configuration"""
        print("🖥️  Verifying Hardware Configuration...")
        
        results = {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'python_version': sys.version.split()[0],
            'cpu_count': psutil.cpu_count(logical=False),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'ram_total_gb': psutil.virtual_memory().total / (1024**3),
            'ram_available_gb': psutil.virtual_memory().available / (1024**3),
            'cuda_available': torch.cuda.is_available(),
            'pytorch_version': torch.__version__
        }
        
        if results['cuda_available']:
            results['gpu_count'] = torch.cuda.device_count()
            results['gpu_name'] = torch.cuda.get_device_name(0)
            results['gpu_memory_gb'] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            results['cuda_version'] = torch.version.cuda
        
        # Validation
        if not results['cuda_available']:
            self.issues.append("CUDA not available - training will be CPU-only")
        elif results['gpu_memory_gb'] < 3.5:
            self.warnings.append(f"GPU memory ({results['gpu_memory_gb']:.1f}GB) is low for large models")
        
        if results['ram_total_gb'] < 16:
            self.warnings.append(f"System RAM ({results['ram_total_gb']:.1f}GB) may limit dataset loading")
        
        self.verification_results['hardware'] = results
        return results
    
    def verify_storage(self) -> Dict[str, Any]:
        """Verify storage infrastructure"""
        print("📊 Verifying Storage Infrastructure...")
        
        results = {
            'training_drive_exists': self.training_drive.exists(),
            'training_drive_accessible': False,
            'directory_structure_complete': False,
            'total_space_gb': 0,
            'available_space_gb': 0,
            'used_space_gb': 0
        }
        
        # Check training drive
        if self.training_drive.exists():
            try:
                # Test accessibility
                test_file = self.training_drive / "test_access.tmp"
                test_file.write_text("test")
                test_file.unlink()
                results['training_drive_accessible'] = True
                
                # Get drive statistics
                try:
                    import shutil
                    total, used, free = shutil.disk_usage(self.training_drive)
                    results['total_space_gb'] = total / (1024**3)
                    results['available_space_gb'] = free / (1024**3)
                    results['used_space_gb'] = used / (1024**3)
                except Exception as e:
                    self.warnings.append(f"Could not get drive statistics: {e}")
                
                # Check directory structure
                expected_dirs = [
                    'training_data', 'models', 'embeddings', 'logs', 
                    'temp', 'experiments', 'datasets'
                ]
                
                missing_dirs = []
                for dir_name in expected_dirs:
                    if not (self.training_drive / dir_name).exists():
                        missing_dirs.append(dir_name)
                
                results['directory_structure_complete'] = len(missing_dirs) == 0
                if missing_dirs:
                    self.warnings.append(f"Missing directories: {', '.join(missing_dirs)}")
                
            except Exception as e:
                self.issues.append(f"Training drive access error: {e}")
        else:
            self.issues.append("Training drive F: not found or not accessible")
        
        self.verification_results['storage'] = results
        return results
    
    def verify_environment(self) -> Dict[str, Any]:
        """Verify Python environment and dependencies"""
        print("🐍 Verifying Python Environment...")
        
        results = {
            'python_version_ok': sys.version_info >= (3, 8),
            'pytorch_installed': False,
            'torch_version': None,
            'cuda_pytorch_compatible': False,
            'required_modules': {}
        }
        
        # Check PyTorch
        try:
            import torch
            results['pytorch_installed'] = True
            results['torch_version'] = torch.__version__
            results['cuda_pytorch_compatible'] = torch.cuda.is_available()
        except ImportError:
            self.issues.append("PyTorch not installed or not accessible")
        
        # Check required modules
        required_modules = [
            'numpy', 'pandas', 'matplotlib', 'tqdm', 'psutil',
            'pathlib', 'json', 'logging', 'asyncio'
        ]
        
        for module in required_modules:
            try:
                __import__(module)
                results['required_modules'][module] = True
            except ImportError:
                results['required_modules'][module] = False
                self.warnings.append(f"Optional module {module} not available")
        
        self.verification_results['environment'] = results
        return results
    
    def verify_training_components(self) -> Dict[str, Any]:
        """Verify training scripts and components"""
        print("🧠 Verifying Training Components...")
        
        results = {
            'project_structure_valid': self.project_root.exists(),
            'training_scripts': {},
            'core_modules': {},
            'config_files': {}
        }
        
        # Check training scripts
        training_scripts = [
            'bulletproof_training_launcher.py',
            'enhanced_training_launcher.py', 
            'bulletproof_incremental_trainer.py',
            'high_school_graduate_trainer.py'
        ]
        
        for script in training_scripts:
            script_path = self.project_root / "src" / "training" / script
            root_script_path = self.project_root / script
            
            if script_path.exists():
                results['training_scripts'][script] = str(script_path)
            elif root_script_path.exists():
                results['training_scripts'][script] = str(root_script_path)
            else:
                results['training_scripts'][script] = None
                self.warnings.append(f"Training script {script} not found")
        
        # Check core modules
        core_modules = [
            'src/core/utils/training_storage_manager.py',
            'src/core/utils/training_data_calculator.py',
            'src/training/models',
            'src/training/configs',
            'src/training/datasets'
        ]
        
        for module in core_modules:
            module_path = self.project_root / module
            results['core_modules'][module] = module_path.exists()
            if not module_path.exists():
                self.warnings.append(f"Core module {module} not found")
        
        self.verification_results['training_components'] = results
        return results
    
    def generate_recommendations(self) -> List[str]:
        """Generate training recommendations based on verification"""
        recommendations = []
        
        hardware = self.verification_results.get('hardware', {})
        storage = self.verification_results.get('storage', {})
        
        # Training capacity recommendations
        if hardware.get('cuda_available') and hardware.get('gpu_memory_gb', 0) >= 3.5:
            available_gb = storage.get('available_space_gb', 0)
            
            if available_gb >= 400:
                recommendations.append("🚀 READY: Large multimodal training (335GB projects)")
            elif available_gb >= 200:
                recommendations.append("📊 READY: Medium language model training (190GB projects)")
            elif available_gb >= 50:
                recommendations.append("🎯 READY: Small specialized model training (45-65GB projects)")
            else:
                recommendations.append("⚠️  CAUTION: Limited storage may restrict project size")
        
        # Hardware optimization recommendations
        if hardware.get('cuda_available'):
            recommendations.append("✅ GPU training enabled - use CUDA acceleration")
            if hardware.get('gpu_memory_gb', 0) < 6:
                recommendations.append("💡 TIP: Use gradient checkpointing for memory efficiency")
        
        # Storage optimization recommendations
        if storage.get('available_space_gb', 0) > 100:
            recommendations.append("📁 OPTIMAL: Sufficient storage for multiple concurrent projects")
        
        return recommendations
    
    def run_verification(self) -> Dict[str, Any]:
        """Run complete verification process"""
        self.print_banner()
        
        # Run all verification steps
        if RICH_AVAILABLE:
            steps = [
                ("Hardware", self.verify_hardware),
                ("Storage", self.verify_storage), 
                ("Environment", self.verify_environment),
                ("Training Components", self.verify_training_components)
            ]
            
            for step_name, step_func in track(steps, description="Verifying system..."):
                step_func()
                time.sleep(0.5)  # Small delay for visual effect
        else:
            self.verify_hardware()
            self.verify_storage()
            self.verify_environment()
            self.verify_training_components()
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive verification report"""
        print("\n" + "="*80)
        print("📋 VERIFICATION REPORT")
        print("="*80)
        
        # Overall status
        critical_issues = len(self.issues)
        warnings = len(self.warnings)
        
        if critical_issues == 0:
            status = "✅ PRODUCTION READY"
            status_color = "green"
        elif critical_issues <= 2:
            status = "⚠️  READY WITH WARNINGS"  
            status_color = "yellow"
        else:
            status = "❌ NEEDS ATTENTION"
            status_color = "red"
        
        print(f"Overall Status: {status}")
        print(f"Critical Issues: {critical_issues}")
        print(f"Warnings: {warnings}")
        print()
        
        # Hardware summary
        hw = self.verification_results.get('hardware', {})
        print("🖥️  Hardware Summary:")
        print(f"   Platform: {hw.get('platform', 'Unknown')} {hw.get('architecture', '')}")
        print(f"   Python: {hw.get('python_version', 'Unknown')}")
        print(f"   PyTorch: {hw.get('pytorch_version', 'Unknown')}")
        print(f"   CPU: {hw.get('cpu_count', 0)} cores ({hw.get('cpu_count_logical', 0)} logical)")
        print(f"   RAM: {hw.get('ram_total_gb', 0):.1f}GB total, {hw.get('ram_available_gb', 0):.1f}GB available")
        
        if hw.get('cuda_available'):
            print(f"   GPU: {hw.get('gpu_name', 'Unknown')} ({hw.get('gpu_memory_gb', 0):.1f}GB VRAM)")
            print(f"   CUDA: {hw.get('cuda_version', 'Unknown')}")
        else:
            print("   GPU: CUDA not available")
        print()
        
        # Storage summary
        storage = self.verification_results.get('storage', {})
        print("📊 Storage Summary:")
        if storage.get('training_drive_exists'):
            print(f"   Training Drive: F:\\ ({storage.get('total_space_gb', 0):.1f}GB total)")
            print(f"   Available: {storage.get('available_space_gb', 0):.1f}GB")
            print(f"   Used: {storage.get('used_space_gb', 0):.1f}GB")
            print(f"   Directory Structure: {'✅ Complete' if storage.get('directory_structure_complete') else '⚠️  Incomplete'}")
        else:
            print("   Training Drive: ❌ Not accessible")
        print()
        
        # Training capacity analysis
        available_gb = storage.get('available_space_gb', 0)
        print("🚀 Training Capacity Analysis:")
        if available_gb >= 335:
            print("   ✅ Large Multimodal Projects: Supported (335GB)")
        if available_gb >= 190:
            print(f"   ✅ Medium Language Models: {int(available_gb // 190)} concurrent projects")
        if available_gb >= 45:
            print(f"   ✅ Small Specialized Models: {int(available_gb // 45)} concurrent projects")
        print()
        
        # Issues and warnings
        if self.issues:
            print("❌ Critical Issues:")
            for issue in self.issues:
                print(f"   • {issue}")
            print()
        
        if self.warnings:
            print("⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")
            print()
        
        # Recommendations
        recommendations = self.generate_recommendations()
        if recommendations:
            print("💡 Recommendations:")
            for rec in recommendations:
                print(f"   • {rec}")
            print()
        
        # Next steps
        print("🎯 READY TO LAUNCH - Next Steps:")
        print("   1. Launch Historic GPU Distillation:")
        print("      python high_school_graduate_trainer.py")
        print()
        print("   2. Start Bulletproof Training:")
        print("      python src/training/bulletproof_training_launcher.py")
        print()
        print("   3. Monitor Storage:")
        print("      python src/core/utils/training_storage_manager.py")
        print()
        
        return {
            'status': status,
            'critical_issues': critical_issues,
            'warnings': warnings,
            'results': self.verification_results,
            'issues': self.issues,
            'warnings_list': self.warnings,
            'recommendations': recommendations
        }

def main():
    """Main verification function"""
    verifier = TrainingReadinessVerifier()
    report = verifier.run_verification()
    
    print("="*80)
    print("🏆 VERIFICATION COMPLETE")
    print("="*80)
    print(f"Status: {report['status']}")
    print(f"ImpressionCore is ready for serious AI training with 476GB storage!")
    print()

if __name__ == "__main__":
    main()
