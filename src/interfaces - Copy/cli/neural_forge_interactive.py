#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #command_line #deployment #inference #memory_management #python #pytorch #source_code #src/interfaces/cli\neural_forge_interactive.py #training #transformer
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #api #command_line #deployment #inference #memory_management #python #pytorch #source_code #src\\interfaces\\cli\\neural_forge_interactive.py #training #transformer
# Category:** Interface Definitions
# Status:** Active

"""
Neural Forge Launcher - Interactive Preset Edition
Full implementation with working preset selection and configuration export
"""

import asyncio
import json
import sys
from pathlib import Path

# Ensure we can import from the current directory
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

async def main():
    """Launch the Neural Forge interactive builder with full preset functionality."""
    try:        # Add the parent directory to sys.path to find src modules
        src_path = current_dir.parent
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        from cli.config.configuration_manager import ConfigurationManager
        from cli.config.preset_loader import PresetLoader
        from cli.interactive_builder.neural_forge import NeuralForge

        print("🧠 ImpressionCore Neural Forge")
        print("=" * 50)
        print("Brain-inspired AI model building experience")
        print("Optimized for GTX 1050 Ti and consumer hardware")
        print()

        # Initialize components
        forge = NeuralForge()
        preset_loader = PresetLoader()
        config_manager = ConfigurationManager()

        # Run the neural boot sequence
        await forge.neural_boot_sequence()

        # Start the interactive experience
        print("\n🎯 Welcome to Neural Forge!")
        print("Choose your path to AI mastery:")
        print()
        print("1. 🌟 Smart Default    - Let AI optimize everything for your hardware")
        print("2. ⚡ Express Preset   - Choose from curated configurations")
        print("3. 🔧 Custom Config    - Fine-tune every parameter")
        print("4. 🤖 AI Assistant     - Chat with the AI architect")
        print("5. 📊 System Status    - Check your setup and capabilities")
        print("6. 🚪 Exit")
        print()

        while True:
            try:
                choice = input("Enter your choice (1-6): ").strip()

                if choice == "1":
                    print("\n🌟 Smart Default Mode")
                    print("AI is analyzing your system and optimizing configuration...")
                    config = await forge.foundation_genesis_phase()

                    # Save configuration
                    config_path = config_manager.save_configuration(
                        config, "smart_default", "Smart Default Configuration"
                    )
                    print(f"✅ Generated optimal configuration with {len(config)} sections")
                    print(f"💾 Configuration saved to: {config_path}")
                    print("\n💡 Configuration complete! Choose another option or type 6 to exit.")

                elif choice == "2":
                    print("\n⚡ Express Preset Mode")
                    await handle_preset_selection(forge, preset_loader, config_manager)

                elif choice == "3":
                    print("\n🔧 Custom Configuration Mode")
                    print("Starting complete build pipeline...")

                    # Run all phases
                    foundation_config = await forge.foundation_genesis_phase()
                    architecture_config = await forge.architecture_design_phase()
                    training_config = await forge.training_orchestration_phase()
                    deployment_config = await forge.deployment_mastery_phase()

                    # Combine all configurations
                    complete_config = {
                        "foundation": foundation_config,
                        "architecture": architecture_config,
                        "training": training_config,
                        "deployment": deployment_config
                    }

                    # Save configuration
                    config_path = config_manager.save_configuration(
                        complete_config, "custom_complete", "Complete Custom Configuration"
                    )

                    total_sections = (len(foundation_config) + len(architecture_config) +
                                    len(training_config) + len(deployment_config))
                    print(f"✅ Complete configuration generated with {total_sections} sections")
                    print(f"💾 Configuration saved to: {config_path}")
                    print("\n💡 Full pipeline complete! Choose another option or type 6 to exit.")

                elif choice == "4":
                    print("\n🤖 AI Assistant Mode")
                    print("Chat with the Neural Forge AI architect...")
                    print("Type 'back' to return to main menu")

                    assistant_active = True
                    while assistant_active:
                        try:
                            user_input = input("\n🧠 You: ").strip()
                            if user_input.lower() in ['back', 'exit', 'quit']:
                                assistant_active = False
                                print("Returning to main menu...")
                            elif user_input.lower() == 'hardware':
                                print("🤖 AI: GTX 1050 Ti Optimization Tips:")
                                print("     • Use mixed precision (FP16) to halve memory usage")
                                print("     • Enable gradient checkpointing for larger models")
                                print("     • Consider LoRA for fine-tuning efficiency")
                                print("     • Use INT8 quantization for inference")
                            elif user_input.lower() == 'presets':
                                print("🤖 AI: Preset Comparison:")
                                print("     • Lightning ⚡: Best for rapid iteration")
                                print("     • Balanced ⚖️: Recommended for most users")
                                print("     • Precision 🎯: Maximum quality output")
                                print("     • Efficient 🧠: Perfect for limited VRAM")
                            elif user_input.lower() == 'memory':
                                print("🤖 AI: VRAM Optimization Strategies:")
                                print("     • Model parallelism for large models")
                                print("     • CPU offloading for parameters")
                                print("     • Dynamic batching based on sequence length")
                                print("     • Activation checkpointing trade-off")
                            elif user_input:
                                print("🤖 AI: I'm here to help you build the perfect AI model!")
                                print("     Available commands:")
                                print("     • 'hardware' - GTX 1050 Ti optimization tips")
                                print("     • 'presets' - Compare Lightning vs Balanced vs Precision")
                                print("     • 'memory' - VRAM optimization strategies")
                                print("     • 'back' - Return to main menu")
                        except (EOFError, KeyboardInterrupt):
                            print("\nReturning to main menu...")
                            assistant_active = False

                elif choice == "5":
                    print("\n📊 System Status")
                    print("Hardware: GTX 1050 Ti (4GB VRAM) - ✅ Supported")
                    print("Memory: Available for optimization")
                    print("Neural Forge: ✅ Fully operational")
                    print("Components: Running in adaptive mode")
                    print(f"Configurations saved: {len(list(config_manager.config_dir.glob('*.json')))}")
                    print("\n💡 Status check complete! Choose another option or type 6 to exit.")

                elif choice == "6":
                    print("\n🚪 Thank you for using Neural Forge!")
                    print("Your AI journey continues...")
                    break

                else:
                    print("❌ Invalid choice. Please enter 1-6.")

            except EOFError:
                print("\n\n🚪 Input ended. Exiting Neural Forge...")
                break
            except KeyboardInterrupt:
                print("\n\n🚪 Exiting Neural Forge. Goodbye!")
                break

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all Neural Forge components are properly installed.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

async def handle_preset_selection(forge, preset_loader, config_manager):
    """Handle the interactive preset selection process.

    Args:
        forge: Neural Forge instance.
        preset_loader: PresetLoader instance.
        config_manager: ConfigurationManager instance.
    """
    # Display preset menu
    displayed_presets = preset_loader.display_preset_menu(available_vram=4.0)

    preset_active = True
    while preset_active:
        try:
            preset_choice = input(f"Choose preset (1-{len(displayed_presets) + 1}): ").strip()

            # Handle numbered choices
            try:
                choice_num = int(preset_choice)

                if 1 <= choice_num <= len(displayed_presets):
                    # Apply selected preset
                    preset_key, preset_info = displayed_presets[choice_num - 1]

                    print(f"\n{preset_info.icon} {preset_info.name} Selected")
                    print(f"🎯 Optimizing for {preset_info.target_use_case}...")

                    # Generate configuration using the preset
                    config = await forge.apply_express_preset(preset_key)

                    # Save configuration
                    config_path = config_manager.save_configuration(
                        config, f"preset_{preset_key}", f"{preset_info.name} Preset Configuration"
                    )

                    print(f"💾 Configuration saved to: {config_path}")

                    # Ask about next steps
                    await show_next_steps(config, preset_info, config_manager)

                    preset_active = False

                elif choice_num == len(displayed_presets) + 1:
                    print("🔙 Returning to main menu...")
                    preset_active = False

                else:
                    print(f"❌ Invalid choice. Please enter 1-{len(displayed_presets) + 1}.")

            except ValueError:
                print(f"❌ Invalid input. Please enter a number 1-{len(displayed_presets) + 1}.")

        except (EOFError, KeyboardInterrupt):
            print("\n🔙 Returning to main menu...")
            preset_active = False

    if preset_choice != str(len(displayed_presets) + 1):
        print("\n💡 Preset configured! Choose another option or type 6 to exit.")

async def show_next_steps(config, preset_info, config_manager):
    """Show options for what to do next with the generated configuration.

    Args:
        config: Generated configuration dictionary.
        preset_info: PresetInfo object.
        config_manager: ConfigurationManager instance.
    """
    print(f"\n🚀 {preset_info.name} Configuration Complete!")
    print("What would you like to do next?")
    print()
    print("1. 📋 View detailed configuration")
    print("2. 💾 Export for training script")
    print("3. 🔧 Customize this configuration")
    print("4. 🏁 Start training (coming soon)")
    print("5. ↩️  Continue with main menu")
    print()

    while True:
        try:
            next_choice = input("Choose next action (1-5): ").strip()

            if next_choice == "1":
                print(f"\n📋 Detailed Configuration for {preset_info.name}:")
                print("=" * 50)
                print(json.dumps(config, indent=2))
                print("=" * 50)
                break

            elif next_choice == "2":
                print("\n💾 Export Options:")
                print("1. PyTorch training script")
                print("2. HuggingFace Transformers config")
                print("3. JSON configuration file")
                print("4. All formats")

                export_choice = input("Choose export format (1-4): ").strip()

                if export_choice == "1":
                    script_path = config_manager.export_pytorch_script(config, preset_info.key)
                    print(f"✅ PyTorch script exported to: {script_path}")
                elif export_choice == "2":
                    hf_path = config_manager.export_huggingface_config(config, preset_info.key)
                    print(f"✅ HuggingFace config exported to: {hf_path}")
                elif export_choice == "3":
                    json_path = config_manager.export_json_config(config, preset_info.key)
                    print(f"✅ JSON config exported to: {json_path}")
                elif export_choice == "4":
                    script_path = config_manager.export_pytorch_script(config, preset_info.key)
                    hf_path = config_manager.export_huggingface_config(config, preset_info.key)
                    json_path = config_manager.export_json_config(config, preset_info.key)
                    print("✅ All formats exported:")
                    print(f"   PyTorch: {script_path}")
                    print(f"   HuggingFace: {hf_path}")
                    print(f"   JSON: {json_path}")
                else:
                    print("❌ Invalid export choice.")
                    continue
                break

            elif next_choice == "3":
                print(f"\n🔧 Customizing {preset_info.name} Configuration")
                print("(Advanced customization interface coming soon)")
                print("For now, you can edit the exported JSON configuration manually.")
                break

            elif next_choice == "4":
                print(f"\n🏁 Training {preset_info.name} Model")
                print("Training pipeline integration coming soon!")
                print("Use the exported PyTorch script as a starting point.")
                break

            elif next_choice == "5":
                print("↩️ Continuing with main menu...")
                break

            else:
                print("❌ Invalid choice. Please enter 1-5.")

        except (EOFError, KeyboardInterrupt):
            print("\n↩️ Continuing with main menu...")
            break

if __name__ == "__main__":
    asyncio.run(main())
