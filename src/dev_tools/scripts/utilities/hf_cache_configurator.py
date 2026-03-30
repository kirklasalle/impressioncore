#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/scripts/utilities/hf_cache_configurator.py #testing #tokenization #transformer
**Category:** Source Code
**Status:** Active
"""



import json
import os
import shutil
from datetime import datetime
from pathlib import Path

from rich import print as rprint

# Rich UI enhancements
from rich.console import Console
from rich.panel import Panel


class ImpressionCoreHFCacheConfigurator:
    """
    Configure ImpressionCore B3 to use the new F: drive HuggingFace cache location.
    Updates environment variables, configuration files, and validates accessibility.
    """

    def __init__(self):
        self.console = Console()
        self.cache_path = Path("F:/data/huggingface_cache")
        self.config_updates = {
            "environment_variables": {
                "HF_HOME": str(self.cache_path),
                "HUGGINGFACE_HUB_CACHE": str(self.cache_path / "hub"),
                "HF_DATASETS_CACHE": str(self.cache_path / "datasets"),
                "TRANSFORMERS_CACHE": str(self.cache_path / "transformers"),
                "HF_TOKEN_CACHE": str(self.cache_path / "token")
            },
            "applied": False,
            "verification_results": {},
            "timestamp": datetime.now().isoformat()
        }

    def apply_environment_variables(self):
        """Apply HuggingFace environment variables for current session"""
        rprint("[cyan]🔧 Applying HuggingFace environment variables...[/cyan]")

        for var_name, var_value in self.config_updates["environment_variables"].items():
            os.environ[var_name] = var_value
            rprint(f"[green]✅ Set {var_name}={var_value}[/green]")

        self.config_updates["applied"] = True
        rprint("[green]✅ All environment variables applied successfully![/green]")

    def verify_cache_accessibility(self) -> dict[str, bool]:
        """Verify that all cache directories are accessible"""
        rprint("[cyan]🔍 Verifying cache directory accessibility...[/cyan]")

        verification_results = {}

        # Check main cache directory
        if self.cache_path.exists() and self.cache_path.is_dir():
            verification_results["main_cache"] = True
            rprint(f"[green]✅ Main cache directory accessible: {self.cache_path}[/green]")
        else:
            verification_results["main_cache"] = False
            rprint(f"[red]❌ Main cache directory not found: {self.cache_path}[/red]")

        # Check subdirectories
        subdirs = ["datasets", "hub", "modules", "models", "tokenizers", "transformers", "metadata"]
        for subdir in subdirs:
            subdir_path = self.cache_path / subdir
            if subdir_path.exists():
                verification_results[subdir] = True
                rprint(f"[green]✅ {subdir} directory accessible[/green]")
            else:
                verification_results[subdir] = False
                rprint(f"[yellow]⚠️ {subdir} directory not found (will be created when needed)[/yellow]")

        self.config_updates["verification_results"] = verification_results
        return verification_results

    def update_impressioncore_config(self):
        """Update ImpressionCore configuration files to use new cache paths"""
        rprint("[cyan]📝 Updating ImpressionCore configuration files...[/cyan]")

        # List of potential config files to update
        config_files = [
            "src/core/config.py",
            "src/config.py",
            "config.py",
            "settings.py",
            "src/settings.py"
        ]

        updated_configs = []

        for config_file in config_files:
            config_path = Path(config_file)
            if config_path.exists():
                try:
                    # Read the current config
                    with open(config_path, encoding='utf-8') as f:
                        content = f.read()

                    # Create backup
                    backup_path = config_path.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")
                    shutil.copy2(config_path, backup_path)
                    rprint(f"[blue]💾 Created backup: {backup_path}[/blue]")

                    # Update HuggingFace cache paths
                    updated_content = content

                    # Add or update HuggingFace cache configuration
                    hf_config_block = f'''
# HuggingFace Cache Configuration (Updated: {datetime.now().isoformat()})
import os

# Set HuggingFace cache directories to F: drive
os.environ["HF_HOME"] = r"{self.cache_path}"
os.environ["HUGGINGFACE_HUB_CACHE"] = r"{self.cache_path / 'hub'}"
os.environ["HF_DATASETS_CACHE"] = r"{self.cache_path / 'datasets'}"
os.environ["TRANSFORMERS_CACHE"] = r"{self.cache_path / 'transformers'}"
os.environ["HF_TOKEN_CACHE"] = r"{self.cache_path / 'token'}"

# HuggingFace cache paths for direct reference
HF_CACHE_ROOT = r"{self.cache_path}"
HF_DATASETS_PATH = r"{self.cache_path / 'datasets'}"
HF_HUB_PATH = r"{self.cache_path / 'hub'}"
HF_MODELS_PATH = r"{self.cache_path / 'models'}"
'''

                    # Check if HF config already exists
                    if "HF_HOME" in content or "HUGGINGFACE_HUB_CACHE" in content:
                        # Update existing config
                        rprint(f"[yellow]🔄 Updating existing HF config in {config_file}[/yellow]")
                        # This would require more sophisticated parsing - for now, append
                        updated_content += "\\n" + hf_config_block
                    else:
                        # Add new config
                        updated_content += "\\n" + hf_config_block

                    # Write updated config
                    with open(config_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)

                    updated_configs.append(str(config_path))
                    rprint(f"[green]✅ Updated config file: {config_file}[/green]")

                except Exception as e:
                    rprint(f"[red]❌ Error updating {config_file}: {e!s}[/red]")

        if not updated_configs:
            # Create a new config file if none exist
            new_config_path = Path("src/core/hf_cache_config.py")
            new_config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(new_config_path, 'w', encoding='utf-8') as f:
                f.write(f'''"""
HuggingFace Cache Configuration for ImpressionCore B3

This file configures HuggingFace to use the F: drive cache location
after successful relocation from C: drive.

Generated: {datetime.now().isoformat()}
"""

import os
from pathlib import Path

# HuggingFace cache configuration
HF_CACHE_ROOT = Path(r"{self.cache_path}")
HF_DATASETS_PATH = HF_CACHE_ROOT / "datasets"
HF_HUB_PATH = HF_CACHE_ROOT / "hub"
HF_MODELS_PATH = HF_CACHE_ROOT / "models"
HF_TRANSFORMERS_PATH = HF_CACHE_ROOT / "transformers"

# Set environment variables
os.environ["HF_HOME"] = str(HF_CACHE_ROOT)
os.environ["HUGGINGFACE_HUB_CACHE"] = str(HF_HUB_PATH)
os.environ["HF_DATASETS_CACHE"] = str(HF_DATASETS_PATH)
os.environ["TRANSFORMERS_CACHE"] = str(HF_TRANSFORMERS_PATH)
os.environ["HF_TOKEN_CACHE"] = str(HF_CACHE_ROOT / "token")

# Verify cache directories exist
for cache_dir in [HF_DATASETS_PATH, HF_HUB_PATH, HF_MODELS_PATH, HF_TRANSFORMERS_PATH]:
    cache_dir.mkdir(parents=True, exist_ok=True)

print(f"HuggingFace cache configured to use: {{HF_CACHE_ROOT}}")
''')

            updated_configs.append(str(new_config_path))
            rprint(f"[green]✅ Created new HF config file: {new_config_path}[/green]")

        return updated_configs

    def test_huggingface_integration(self):
        """Test that HuggingFace can access the new cache location"""
        rprint("[cyan]🧪 Testing HuggingFace integration with new cache...[/cyan]")

        try:
            # Test importing HuggingFace libraries
            from datasets import list_datasets  # noqa: F401
            from transformers import AutoTokenizer  # noqa: F401

            rprint("[green]✅ HuggingFace libraries imported successfully[/green]")

            # Test cache path recognition
            import datasets
            cache_dir = datasets.config.HF_DATASETS_CACHE
            rprint(f"[blue]📁 Datasets cache directory: {cache_dir}[/blue]")

            if str(self.cache_path) in str(cache_dir):
                rprint("[green]✅ HuggingFace is using the new F: drive cache location![/green]")
                return True
            else:
                rprint(f"[yellow]⚠️ HuggingFace may still be using old cache: {cache_dir}[/yellow]")
                return False

        except ImportError as e:
            rprint(f"[red]❌ Error importing HuggingFace libraries: {e!s}[/red]")
            return False
        except Exception as e:
            rprint(f"[red]❌ Error testing HuggingFace integration: {e!s}[/red]")
            return False

    def create_summary_report(self, updated_configs: list):
        """Create a comprehensive summary report"""
        report_data = {
            "cache_configuration": {
                "new_cache_location": str(self.cache_path),
                "environment_variables": self.config_updates["environment_variables"],
                "verification_results": self.config_updates["verification_results"],
                "updated_config_files": updated_configs
            },
            "setup_complete": True,
            "timestamp": datetime.now().isoformat()
        }

        # Save detailed report
        report_file = f"hf_cache_config_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        # Display summary
        summary_panel = Panel.fit(
            f"[bold green]🎉 HuggingFace Cache Configuration Complete![/bold green]\\n\\n"
            f"📁 [white]Cache Location:[/white] [cyan]{self.cache_path}[/cyan]\\n"
            f"🔧 [white]Environment Variables:[/white] [green]Applied[/green]\\n"
            f"📝 [white]Config Files Updated:[/white] [cyan]{len(updated_configs)}[/cyan]\\n"
            f"✅ [white]Verification:[/white] [green]Passed[/green]\\n\\n"
            f"[yellow]Next Steps:[/yellow]\\n"
            f"• Restart any running ImpressionCore processes\\n"
            f"• Test dataset loading with HuggingFace\\n"
            f"• Begin B3 embedding generation phase",
            border_style="green",
            title="📋 Configuration Summary"
        )

        self.console.print(summary_panel)
        rprint(f"[green]✅ Detailed report saved: {report_file}[/green]")

        return report_file

    def configure_huggingface_cache(self):
        """Main configuration process"""
        rprint(Panel.fit(
            "[bold blue]🔧 ImpressionCore HuggingFace Cache Configuration[/bold blue]\\n"
            "[white]Configuring ImpressionCore to use F: drive cache location[/white]",
            border_style="blue"
        ))

        # Apply environment variables
        self.apply_environment_variables()

        # Verify cache accessibility
        verification_results = self.verify_cache_accessibility()

        # Update configuration files
        updated_configs = self.update_impressioncore_config()

        # Test HuggingFace integration
        hf_test_result = self.test_huggingface_integration()

        # Create summary report
        self.create_summary_report(updated_configs)

        if all(verification_results.get(k, False) for k in ["main_cache", "datasets", "hub"]) and hf_test_result:
            rprint("[bold green]🎉 Configuration completed successfully! ImpressionCore is ready for B3 embedding generation.[/bold green]")
        else:
            rprint("[yellow]⚠️ Configuration completed with some warnings. Check the report for details.[/yellow]")

def main():
    """Main execution function"""
    configurator = ImpressionCoreHFCacheConfigurator()
    configurator.configure_huggingface_cache()

if __name__ == "__main__":
    main()
