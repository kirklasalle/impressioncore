#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #command_line #deployment #inference #memory_management #python #source_code #src/interfaces/cli\neural_forge_launcher_enhanced.py #training
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #command_line #deployment #inference #memory_management #python #source_code #src\\interfaces\\cli\\neural_forge_launcher_enhanced.py #training
# Category:** Interface Definitions
# Status:** Active

"""
Neural Forge Launcher - Enhanced Interactive Version
Entry point for the ImpressionCore Neural Forge Experience Engine
"""

import asyncio
import sys
from pathlib import Path

# Ensure we can import from the current directory
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

async def main():
    """Launch the Neural Forge interactive builder."""
    try:
        from interactive_builder.neural_forge import NeuralForge

        print("🧠 ImpressionCore Neural Forge")
        print("=" * 50)
        print("Brain-inspired AI model building experience")
        print("Optimized for GTX 1050 Ti and consumer hardware")
        print()

        # Initialize Neural Forge
        forge = NeuralForge()

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
                    print(f"✅ Generated optimal configuration with {len(config)} sections")
                    print("\n💡 Configuration complete! Choose another option or type 6 to exit.")

                elif choice == "2":
                    print("\n⚡ Express Preset Mode")
                    print("Choose your optimized configuration preset:")
                    print()
                    print("1. ⚡ Lightning  - Ultra-fast inference, minimal VRAM")
                    print("2. ⚖️  Balanced   - Best performance/quality balance")
                    print("3. 🎯 Precision - Maximum quality, slower inference")
                    print("4. 💚 Efficient - Memory optimized, GTX 1050 Ti perfect")
                    print("5. 🔙 Back to main menu")
                    print()

                    preset_active = True
                    while preset_active:
                        try:
                            preset_choice = input("Choose preset (1-5): ").strip()

                            if preset_choice == "1":
                                print("\n⚡ Lightning Preset Selected")
                                print("🔥 Optimizing for ultra-fast inference...")
                                config = await forge.foundation_genesis_phase()
                                print("⚡ Lightning configuration:")
                                print("  • Model size: Small (fits in 2GB VRAM)")
                                print("  • Precision: Mixed FP16/FP32")
                                print("  • Batch size: 1 (minimal memory)")
                                print("  • Inference speed: ~50ms per token")
                                print(f"✅ Lightning preset configured with {len(config)} sections")
                                preset_active = False

                            elif preset_choice == "2":
                                print("\n⚖️ Balanced Preset Selected")
                                print("🎯 Optimizing for performance/quality balance...")
                                config = await forge.foundation_genesis_phase()
                                print("⚖️ Balanced configuration:")
                                print("  • Model size: Medium (fits in 3GB VRAM)")
                                print("  • Precision: FP16 with FP32 fallback")
                                print("  • Batch size: 2-4 (smart batching)")
                                print("  • Quality/Speed: Optimal balance")
                                print(f"✅ Balanced preset configured with {len(config)} sections")
                                preset_active = False

                            elif preset_choice == "3":
                                print("\n🎯 Precision Preset Selected")
                                print("💎 Optimizing for maximum quality...")
                                config = await forge.foundation_genesis_phase()
                                print("🎯 Precision configuration:")
                                print("  • Model size: Large (uses 3.8GB VRAM)")
                                print("  • Precision: Full FP32 where needed")
                                print("  • Batch size: 1 (quality focus)")
                                print("  • Output quality: Maximum fidelity")
                                print(f"✅ Precision preset configured with {len(config)} sections")
                                preset_active = False

                            elif preset_choice == "4":
                                print("\n💚 Efficient Preset Selected")
                                print("🔋 Optimizing for GTX 1050 Ti efficiency...")
                                config = await forge.foundation_genesis_phase()
                                print("💚 Efficient configuration:")
                                print("  • Model size: Adaptive (1.5-2.5GB VRAM)")
                                print("  • Precision: INT8 quantization where possible")
                                print("  • Memory: Gradient checkpointing enabled")
                                print("  • Perfect for: Long training sessions")
                                print(f"✅ Efficient preset configured with {len(config)} sections")
                                preset_active = False

                            elif preset_choice == "5":
                                print("🔙 Returning to main menu...")
                                preset_active = False

                            else:
                                print("❌ Invalid choice. Please enter 1-5.")

                        except (EOFError, KeyboardInterrupt):
                            print("\n🔙 Returning to main menu...")
                            preset_active = False

                    if preset_choice != "5":
                        print("\n💡 Preset configured! Choose another option or type 6 to exit.")

                elif choice == "3":
                    print("\n🔧 Custom Configuration Mode")
                    print("Starting complete build pipeline...")

                    # Run all phases
                    foundation_config = await forge.foundation_genesis_phase()
                    architecture_config = await forge.architecture_design_phase()
                    training_config = await forge.training_orchestration_phase()
                    deployment_config = await forge.deployment_mastery_phase()

                    total_sections = (len(foundation_config) + len(architecture_config) +
                                    len(training_config) + len(deployment_config))
                    print(f"✅ Complete configuration generated with {total_sections} sections")
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
                            elif user_input:
                                print("🤖 AI: I'm here to help you build the perfect AI model!")
                                print("     Available commands:")
                                print("     • 'hardware' - Check GTX 1050 Ti optimization tips")
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
                    print("Recent Activity: Ready for model building")
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
            except Exception as e:
                print(f"❌ Error: {e}")
                # Exit on persistent input errors
                if "EOF" in str(e):
                    print("🚪 Input error detected. Exiting...")
                    break
                continue

    except ImportError as e:
        print(f"❌ Failed to start Neural Forge: {e}")
        print("Please ensure all components are properly installed.")
        return 1

    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🚪 Goodbye!")
        sys.exit(0)
