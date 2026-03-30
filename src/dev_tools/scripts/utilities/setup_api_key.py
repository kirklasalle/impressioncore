#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #python #source_code #src/scripts/utilities/setup_api_key.py
**Category:** Source Code
**Status:** Active
"""



import os
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

# Import our config classes
from b3_remote_config import RemoteDistillationConfig, create_default_config


class APIKeySetup:
    """Interactive API key setup"""

    def __init__(self):
        self.console = Console()
        self.config_file = "remote_distillation_config.json"

    def show_welcome(self):
        """Show welcome message"""
        self.console.print(Panel.fit(
            "🔑 B3 Remote Distillation API Setup\n"
            "Configure OpenRouter credentials for remote teacher models",
            style="bold blue"
        ))

    def show_instructions(self):
        """Show setup instructions"""
        self.console.print("\n📋 To get your OpenRouter API key:")
        self.console.print("  1. Visit: https://openrouter.ai/")
        self.console.print("  2. Sign up or log in to your account")
        self.console.print("  3. Navigate to the 'Keys' section")
        self.console.print("  4. Create a new API key")
        self.console.print("  5. Copy the generated key")
        self.console.print("  6. Return here to configure\n")

    def get_api_key(self) -> str:
        """Get API key from user"""
        api_key = Prompt.ask("🔑 Enter your OpenRouter API key", password=True)

        if not api_key:
            self.console.print("❌ No API key provided")
            return ""

        if not api_key.startswith("sk-or-"):
            self.console.print("⚠️  Warning: OpenRouter API keys typically start with 'sk-or-'")
            if not Confirm.ask("Continue anyway?"):
                return ""

        return api_key

    def configure_settings(self) -> dict:
        """Configure additional settings"""
        self.console.print("\n⚙️  Configure additional settings:")

        # Model selection
        available_models = [
            "moonshotai/kimi-k2:free",
            "anthropic/claude-3-haiku",
            "meta-llama/llama-3.1-8b-instruct:free",
            "microsoft/wizardlm-2-8x22b:nitro"
        ]

        model_table = Table(title="Available Models")
        model_table.add_column("Index", style="cyan")
        model_table.add_column("Model", style="green")
        model_table.add_column("Cost", style="yellow")

        for i, model in enumerate(available_models):
            cost = "Free" if "free" in model else "Paid"
            model_table.add_row(str(i + 1), model, cost)

        self.console.print(model_table)

        model_choice = Prompt.ask("Select model (1-4)", default="1")
        try:
            model_index = int(model_choice) - 1
            selected_model = available_models[model_index]
        except (ValueError, IndexError):
            selected_model = available_models[0]

        # Other settings
        max_tokens = Prompt.ask("Max tokens per response", default="2048")
        temperature = Prompt.ask("Temperature (0.0-2.0)", default="0.7")
        timeout = Prompt.ask("API timeout (seconds)", default="30")

        return {
            "model": selected_model,
            "max_tokens": int(max_tokens),
            "temperature": float(temperature),
            "timeout": int(timeout)
        }

    def save_configuration(self, api_key: str, settings: dict):
        """Save configuration to file"""
        try:
            # Create configuration
            config = create_default_config()

            # Update with user settings
            config.openrouter.api_key = api_key
            config.teacher_model.model_id = settings["model"]
            config.teacher_model.max_tokens = settings["max_tokens"]
            config.teacher_model.temperature = settings["temperature"]
            config.teacher_model.timeout = settings["timeout"]

            # Save to file
            config.save_to_file(self.config_file)

            # Also set environment variable for current session
            os.environ['OPENROUTER_API_KEY'] = api_key

            self.console.print(f"✅ Configuration saved to {self.config_file}")
            self.console.print("✅ API key set for current session")

            return True

        except Exception as e:
            self.console.print(f"❌ Failed to save configuration: {e}")
            return False

    def show_configuration_summary(self, api_key: str, settings: dict):
        """Show configuration summary"""
        summary_table = Table(title="Configuration Summary")
        summary_table.add_column("Setting", style="cyan")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("API Key", f"{api_key[:15]}..." if api_key else "Not set")
        summary_table.add_row("Model", settings["model"])
        summary_table.add_row("Max Tokens", str(settings["max_tokens"]))
        summary_table.add_row("Temperature", str(settings["temperature"]))
        summary_table.add_row("Timeout", f"{settings['timeout']}s")
        summary_table.add_row("Config File", self.config_file)

        self.console.print(summary_table)

    def check_existing_config(self) -> bool:
        """Check if configuration already exists"""
        if Path(self.config_file).exists():
            self.console.print(f"📁 Found existing configuration: {self.config_file}")

            try:
                config = RemoteDistillationConfig.load_from_file(self.config_file)
                if config.openrouter.api_key:
                    self.console.print("✅ API key already configured")

                    if not Confirm.ask("Reconfigure API settings?"):
                        return False
            except Exception:
                self.console.print("⚠️  Existing config file appears corrupted")

        return True

    def run_setup(self):
        """Run the complete setup process"""
        self.show_welcome()

        # Check for existing configuration
        if not self.check_existing_config():
            self.console.print("👋 Setup cancelled. Existing configuration retained.")
            return

        self.show_instructions()

        # Get API key
        api_key = self.get_api_key()
        if not api_key:
            self.console.print("❌ Setup cancelled. No API key provided.")
            return

        # Configure settings
        settings = self.configure_settings()

        # Show summary
        self.console.print()
        self.show_configuration_summary(api_key, settings)

        # Confirm and save
        if Confirm.ask("\n💾 Save this configuration?"):
            if self.save_configuration(api_key, settings):
                self.console.print("\n🚀 Setup complete! You can now run remote distillation.")
                self.console.print("Run: python b3_remote_distillation_launcher.py")
            else:
                self.console.print("\n❌ Setup failed. Please try again.")
        else:
            self.console.print("\n👋 Setup cancelled.")

def main():
    """Main execution function"""
    setup = APIKeySetup()
    setup.run_setup()

if __name__ == "__main__":
    main()
