#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #api #command_line #docs\scripts\tools\environment_documentation_generator.py #documentation #memory_management #python #source_code #testing #transformer #web_interface  
**Category:** Source Code  
**Status:** Active
"""









# !/usr/bin/env python3

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:27:00  
**Author:** ImpressionCore Team  
**Tags:** #api #command_line #docs\scripts\tools\environment_documentation_generator.py #documentation #memory_management #python #source_code #testing #transformer #web_interface  
**Category:** Source Code  
**Status:** Active

"""
Environment Documentation Generator for ImpressionCore IDS

This script generates comprehensive documentation for Python environment setups
and integrates them into the existing ImpressionCore Documentation System (IDS).
It complements existing IDS automation scripts rather than duplicating functionality.

Created: 2025-01-06
Author: ImpressionCore Development Team
IDS Tags: environment, python, documentation, automation, development_setup
"""

import os
import sys
import json
import yaml
import subprocess
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pkg_resources

# Add project root to path for IDS integration
PROJECT_ROOT = Path(__file__).parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

class EnvironmentDocumentationGenerator:
    """Generates and maintains documentation for Python environments in IDS."""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or PROJECT_ROOT
        self.docs_dir = self.project_root / "docs"
        self.memlog_dir = self.project_root / "src" / "memlog"
        
    def detect_environment_info(self) -> Dict:
        """Detect current Python environment information."""
        info = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "architecture": platform.architecture()[0],
            "machine": platform.machine(),
            "processor": platform.processor(),
        }
        
        # Detect virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            info["virtual_env"] = True
            info["virtual_env_path"] = sys.prefix
            
            # Try to detect environment type
            if "venv" in sys.prefix:
                info["env_type"] = "venv"
            elif "conda" in sys.prefix:
                info["env_type"] = "conda"
            elif "virtualenv" in sys.prefix:
                info["env_type"] = "virtualenv"
            else:
                info["env_type"] = "unknown"
        else:
            info["virtual_env"] = False
            info["env_type"] = "system"
        
        return info
    
    def get_installed_packages(self) -> List[Dict]:
        """Get list of installed packages with versions."""
        packages = []
        try:
            installed_packages = [d for d in pkg_resources.working_set]
            for package in sorted(installed_packages, key=lambda x: x.project_name.lower()):
                packages.append({
                    "name": package.project_name,
                    "version": package.version,
                    "location": package.location
                })
        except Exception as e:
            print(f"Warning: Could not enumerate packages: {e}")
        
        return packages
    
    def categorize_packages(self, packages: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize packages by type/purpose."""
        categories = {
            "core_ai_ml": [],
            "scientific_computing": [],
            "web_frameworks": [],
            "development_tools": [],
            "jupyter_notebooks": [],
            "specialized_libraries": [],
            "audio_processing": [],
            "system_monitoring": [],
            "other": []
        }
        
        # Define categorization rules
        ai_ml_packages = {"torch", "torchvision", "torchaudio", "transformers", "datasets", 
                         "accelerate", "bitsandbytes", "clip", "tiktoken", "sentence-transformers"}
        scientific_packages = {"numpy", "scipy", "pandas", "scikit-learn", "matplotlib", 
                              "seaborn", "plotly", "sympy"}
        web_packages = {"gradio", "flask", "fastapi", "django", "starlette", "uvicorn", 
                       "requests", "httpx", "aiohttp"}
        dev_packages = {"pytest", "black", "isort", "flake8", "ruff", "mypy", "pylint", 
                       "coverage", "tox"}
        jupyter_packages = {"jupyter", "jupyterlab", "ipython", "ipywidgets", "notebook"}
        audio_packages = {"soundfile", "pydub", "librosa", "pyaudio"}
        monitoring_packages = {"psutil", "nvidia-ml-py", "pynvml", "memory-profiler", 
                             "py-cpuinfo"}
        
        for package in packages:
            name_lower = package["name"].lower()
            
            if any(ai_pkg in name_lower for ai_pkg in ai_ml_packages):
                categories["core_ai_ml"].append(package)
            elif any(sci_pkg in name_lower for sci_pkg in scientific_packages):
                categories["scientific_computing"].append(package)
            elif any(web_pkg in name_lower for web_pkg in web_packages):
                categories["web_frameworks"].append(package)
            elif any(dev_pkg in name_lower for dev_pkg in dev_packages):
                categories["development_tools"].append(package)
            elif any(jup_pkg in name_lower for jup_pkg in jupyter_packages):
                categories["jupyter_notebooks"].append(package)
            elif any(aud_pkg in name_lower for aud_pkg in audio_packages):
                categories["audio_processing"].append(package)
            elif any(mon_pkg in name_lower for mon_pkg in monitoring_packages):
                categories["system_monitoring"].append(package)
            else:
                categories["other"].append(package)
        
        return categories
    
    def generate_environment_report(self) -> str:
        """Generate comprehensive environment documentation."""
        env_info = self.detect_environment_info()
        packages = self.get_installed_packages()
        categorized_packages = self.categorize_packages(packages)
        
        report = f"""# Python Environment Documentation

**Generated:** {env_info['timestamp']}  
**System:** {env_info['platform']}  
**Python:** {env_info['python_version']} ({env_info['python_implementation']})  
**Architecture:** {env_info['architecture']}  
**Environment Type:** {env_info['env_type']}  
**Virtual Environment:** {'Yes' if env_info['virtual_env'] else 'No'}  

## Environment Details

### System Information
- **Platform:** {env_info['platform']}
- **Machine:** {env_info['machine']}
- **Processor:** {env_info['processor']}
- **Architecture:** {env_info['architecture']}

### Python Environment
- **Version:** {env_info['python_version']}
- **Implementation:** {env_info['python_implementation']}
- **Environment Type:** {env_info['env_type']}
- **Virtual Environment:** {'Yes' if env_info['virtual_env'] else 'No'}
"""

        if env_info['virtual_env']:
            report += f"- **Environment Path:** {env_info['virtual_env_path']}\n"

        report += f"\n## Installed Packages ({len(packages)} total)\n\n"
        
        # Add categorized packages
        category_names = {
            "core_ai_ml": "Core AI/ML Stack",
            "scientific_computing": "Scientific Computing",
            "web_frameworks": "Web Frameworks & APIs",
            "development_tools": "Development Tools",
            "jupyter_notebooks": "Jupyter & Notebooks",
            "specialized_libraries": "Specialized Libraries",
            "audio_processing": "Audio Processing",
            "system_monitoring": "System Monitoring",
            "other": "Other Packages"
        }
        
        for category, packages_list in categorized_packages.items():
            if packages_list:
                report += f"### {category_names[category]}\n\n"
                for package in packages_list:
                    report += f"- **{package['name']}:** {package['version']}\n"
                report += "\n"
        
        # Add IDS tags
        report += """
## IDS Tags

- environment_documentation
- python_environment
- package_management
- development_setup
- system_configuration
- automated_documentation

---

*This documentation was automatically generated by the ImpressionCore Environment Documentation Generator.*
"""
        
        return report
    
    def save_environment_documentation(self) -> Tuple[str, bool]:
        """Save environment documentation to memlog with IDS integration."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            filename = f"environment_documentation_{timestamp}.md"
            filepath = self.memlog_dir / filename
            
            # Ensure memlog directory exists
            self.memlog_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate and save report
            report = self.generate_environment_report()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            
            return str(filepath), True
            
        except Exception as e:
            print(f"Error saving environment documentation: {e}")
            return "", False
    
    def update_ids_tags(self, filepath: str) -> bool:
        """Update IDS tags for the new documentation file."""
        try:
            # Try to run the IDS tag updater if available
            tag_script = self.project_root / "docs" / "scripts" / "automation" / "add_or_update_tags.py"
            
            if tag_script.exists():
                cmd = [
                    sys.executable, str(tag_script),
                    filepath,
                    "--tags", "environment_documentation,python_environment,package_management,development_setup,system_configuration,automated_documentation"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.returncode == 0
            else:
                print("IDS tag updater not found, skipping tag update")
                return True
                
        except Exception as e:
            print(f"Warning: Could not update IDS tags: {e}")
            return False
    
    def run_full_documentation(self) -> bool:
        """Run complete environment documentation generation."""
        print("🔧 ImpressionCore Environment Documentation Generator")
        print("=" * 60)
        
        print("📊 Analyzing current environment...")
        env_info = self.detect_environment_info()
        packages = self.get_installed_packages()
        
        print(f"✅ Detected Python {env_info['python_version']} ({env_info['env_type']})")
        print(f"✅ Found {len(packages)} installed packages")
        
        print("📝 Generating documentation...")
        filepath, success = self.save_environment_documentation()
        
        if success:
            print(f"✅ Documentation saved: {filepath}")
            
            print("🏷️  Updating IDS tags...")
            if self.update_ids_tags(filepath):
                print("✅ IDS tags updated successfully")
            else:
                print("⚠️  IDS tag update failed (continuing)")
            
            print("🎯 Environment documentation complete!")
            return True
        else:
            print("❌ Failed to save documentation")
            return False

def main():
    """Main entry point for environment documentation generator."""
    generator = EnvironmentDocumentationGenerator()
    success = generator.run_full_documentation()
    
    if success:
        print("\n🚀 Environment documentation successfully integrated into IDS!")
    else:
        print("\n❌ Environment documentation generation failed!")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
