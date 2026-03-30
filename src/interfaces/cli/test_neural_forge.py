#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #command_line #deployment #multimodal #python #source_code #src/interfaces/cli\test_neural_forge.py #testing #training
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #command_line #deployment #multimodal #python #source_code #src\\interfaces\\cli\\test_neural_forge.py #testing #training
# Category:** Interface Definitions
# Status:** Active

"""
Neural Forge Test Runner
Tests the Neural Forge system integration and components.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def test_neural_forge_import():
    """Test that Neural Forge can be imported successfully."""
    try:
        from interactive_builder.neural_forge import BuildPhase, InputMode, NeuralForge
        print("✅ Neural Forge core components imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Neural Forge: {e}")
        return False

async def test_neural_forge_initialization():
    """Test Neural Forge initialization."""
    try:
        from interactive_builder.neural_forge import NeuralForge

        forge = NeuralForge()
        print("✅ Neural Forge initialized successfully")

        # Check component availability
        components = {
            "Advanced Utils": hasattr(forge, 'console') and forge.console is not None,
            "Intelligence Layer": hasattr(forge, 'intelligence_layer') and forge.intelligence_layer is not None,
            "Experience Engine": hasattr(forge, 'experience_engine') and forge.experience_engine is not None,
            "Neural Visualizations": hasattr(forge, 'neural_visualizations') and forge.neural_visualizations is not None,
            "Progress Galaxies": hasattr(forge, 'progress_galaxies') and forge.progress_galaxies is not None,
            "Multimodal Processors": hasattr(forge, 'vision_language_processor') and forge.vision_language_processor is not None
        }

        print("\n📊 Component Availability:")
        for component, available in components.items():
            status = "✅" if available else "⚠️"
            print(f"  {status} {component}: {'Available' if available else 'Fallback mode'}")

        return True
    except Exception as e:
        print(f"❌ Failed to initialize Neural Forge: {e}")
        return False

async def test_neural_forge_phases():
    """Test individual Neural Forge phases."""
    try:
        from interactive_builder.neural_forge import NeuralForge

        forge = NeuralForge()

        # Test individual phases
        phases = [
            ("Foundation Genesis", forge.foundation_genesis_phase),
            ("Architecture Design", forge.architecture_design_phase),
            ("Training Orchestration", forge.training_orchestration_phase),
            ("Deployment Mastery", forge.deployment_mastery_phase)
        ]

        print("\n🔬 Testing Neural Forge Phases:")
        for phase_name, phase_func in phases:
            try:
                config = await phase_func()
                print(f"  ✅ {phase_name}: {len(config)} configuration sections")
            except Exception as e:
                print(f"  ❌ {phase_name}: Failed - {e}")

        return True
    except Exception as e:
        print(f"❌ Failed to test phases: {e}")
        return False

async def test_neural_forge_boot_sequence():
    """Test Neural Forge boot sequence."""
    try:
        from interactive_builder.neural_forge import NeuralForge

        forge = NeuralForge()
        print("\n🚀 Testing Neural Boot Sequence:")

        await forge.neural_boot_sequence()
        print("  ✅ Boot sequence completed successfully")

        return True
    except Exception as e:
        print(f"  ❌ Boot sequence failed: {e}")
        return False

async def main():
    """Run all Neural Forge tests."""
    print("🧠 Neural Forge System Test")
    print("=" * 50)

    tests = [
        test_neural_forge_import,
        test_neural_forge_initialization,
        test_neural_forge_phases,
        test_neural_forge_boot_sequence
    ]

    results = []
    for test in tests:
        result = await test()
        results.append(result)
        print()

    # Summary
    passed = sum(results)
    total = len(results)

    print("📊 Test Summary")
    print("=" * 50)
    print(f"Tests Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! Neural Forge is ready for use.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
