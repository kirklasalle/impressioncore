#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #deployment #python #source_code #src/training/distillation/launch_b3_remote_distillation.py
**Category:** Training System
**Status:** Active
"""



from b3_remote_config import create_default_config, setup_environment

# Import our remote distillation components
from b3_remote_distillation_system import B3RemoteDistillationSystem
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table


def main():
    """Main launcher function"""
    console = Console()

    # Welcome header
    console.print(Panel.fit(
        "🌐 ImpressionCore B3 Remote Distillation Launcher\n"
        "OpenRouter + Moonshotai/Kimi-K2 Enhanced Learning Pipeline\n\n"
        "🎯 Ready to enhance B3 with remote teacher expertise!",
        style="bold magenta"
    ))

    # Check for existing API key
    api_key = setup_environment()

    if not api_key:
        console.print("\n🔐 OpenRouter API Key Required")
        console.print("You can obtain a free API key from: https://openrouter.ai/")

        if Confirm.ask("Do you have an OpenRouter API key ready?"):
            api_key = Prompt.ask("Enter your OpenRouter API key", password=True)

            if Confirm.ask("Save this API key to environment config?"):
                try:
                    config = create_default_config()
                    config.openrouter.api_key = api_key
                    config.save_to_file("remote_distillation_config.json")
                    console.print("✅ API key saved to configuration file")
                except Exception as e:
                    console.print(f"⚠️ Could not save config: {e}")
        else:
            console.print("Please visit https://openrouter.ai/ to get your free API key")
            return

    if not api_key or not api_key.strip():
        console.print("❌ Valid API key is required to proceed")
        return

    # Display configuration summary
    config_table = Table(title="🔧 Remote Distillation Configuration")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")

    config_table.add_row("Teacher Model", "moonshotai/kimi-k2:free")
    config_table.add_row("API Endpoint", "https://openrouter.ai/api/v1")
    config_table.add_row("Curriculum Stages", "4 Progressive Stages")
    config_table.add_row("Enhancement Type", "Remote Teacher Distillation")
    config_table.add_row("Hardware Target", "GTX 1050 Ti Optimized")

    console.print(config_table)

    # Confirm execution
    if not Confirm.ask("\n🚀 Start remote distillation pipeline?"):
        console.print("Operation cancelled")
        return

    console.print("\n🌐 Initializing B3 Remote Distillation System...")

    try:
        # Create and run the remote distillation system
        remote_system = B3RemoteDistillationSystem(api_key)
        results = remote_system.run_complete_remote_pipeline()

        # Display final summary
        if results.get("status") != "failed":
            console.print(Panel.fit(
                "✅ Remote Distillation Completed Successfully!\n\n"
                f"🎯 Stages Completed: {len(results.get('stages_completed', []))}\n"
                f"📊 Performance Improvement: +{results.get('final_metrics', {}).get('overall_improvement', 0):.1%}\n"
                f"🌐 API Success Rate: {results.get('final_metrics', {}).get('api_success_rate', 0):.1%}\n"
                f"⏱️ Total Time: {results.get('total_pipeline_time', 0):.1f}s\n\n"
                "🌟 B3 model enhanced with remote teacher knowledge!",
                style="bold green"
            ))

            if results.get("deployment_assessment", {}).get("deployment_ready"):
                console.print("🚀 Enhanced B3 model is ready for production deployment!")
            else:
                console.print("📈 B3 model shows significant improvement from remote distillation!")

        else:
            console.print(Panel.fit(
                f"❌ Remote Distillation Failed\n\n"
                f"Error: {results.get('error', 'Unknown error')}\n\n"
                "Please check your API key and connection",
                style="bold red"
            ))

    except KeyboardInterrupt:
        console.print("\n⏹️ Remote distillation interrupted by user")
    except Exception as e:
        console.print(f"\n❌ Unexpected error: {e}")
        console.print("Please check logs for detailed error information")

if __name__ == "__main__":
    main()
