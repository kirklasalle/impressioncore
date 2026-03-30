"""
B3 + LCM End-to-End Pipeline Test

Created: October 11, 2025
Updated: October 11, 2025
Author: ImpressionCore Team
Tags: #b3 #lcm #integration_test #pipeline
Category: Testing
Status: Active

Purpose:
    Test complete B3 architecture with LCM image generation.
    Validates Decision #4 implementation.

Test Coverage:
    1. Simple prompts (concrete objects)
    2. Complex prompts (scenes with multiple elements)
    3. Creative prompts (imaginative concepts)
    4. VRAM monitoring (<3.5GB total)
    5. Latency measurement (<15s per image)

Success Criteria:
    - All images generate successfully
    - Quality: 512×512, coherent, detailed
    - VRAM: Peak usage <3.5GB
    - Latency: Average <15s per image
    - No OOM errors or crashes
"""

import torch
import logging
import time
from pathlib import Path
from PIL import Image

from src.core.models.lcm_diffusion import B3ImageGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_gpu_memory_stats():
    """Get GPU memory usage statistics."""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / (1024**3)
        reserved = torch.cuda.memory_reserved() / (1024**3)
        max_allocated = torch.cuda.max_memory_allocated() / (1024**3)
        return {
            "allocated_gb": allocated,
            "reserved_gb": reserved,
            "max_allocated_gb": max_allocated
        }
    return None


def test_case_simple():
    """Test Case 1: Simple concrete object."""
    return {
        "name": "Simple Object",
        "prompt": "a red apple on a wooden table",
        "description": "Testing simple object generation with clear subject"
    }


def test_case_complex():
    """Test Case 2: Complex scene with multiple elements."""
    return {
        "name": "Complex Scene",
        "prompt": "a serene mountain landscape at sunset with a lake reflecting golden light and pine trees",
        "description": "Testing complex scene composition with multiple elements"
    }


def test_case_creative():
    """Test Case 3: Creative imaginative concept."""
    return {
        "name": "Creative Concept",
        "prompt": "a futuristic city with flying cars at night, neon lights, cyberpunk aesthetic",
        "description": "Testing creative generation with imaginative elements"
    }


def test_case_artistic():
    """Test Case 4: Artistic style."""
    return {
        "name": "Artistic Style",
        "prompt": "a portrait of a wise old wizard with a long white beard, oil painting style, detailed",
        "description": "Testing artistic style and character generation"
    }


def run_test_suite():
    """Run complete B3 + LCM test suite."""
    print("="*80)
    print(" B3 + LCM END-TO-END INTEGRATION TEST SUITE")
    print("="*80)
    print()

    # Initialize generator
    logger.info("Initializing B3 Image Generator...")
    generator = B3ImageGenerator()

    if not generator.load():
        logger.error("❌ Failed to load LCM model. Aborting tests.")
        return False

    logger.info("✅ B3 Image Generator loaded successfully")
    print()

    # Test cases
    test_cases = [
        test_case_simple(),
        test_case_complex(),
        test_case_creative(),
        test_case_artistic(),
    ]

    # Create output directory
    output_dir = Path("test_outputs/b3_lcm_pipeline")
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {output_dir}")
    print()

    # Run tests
    results = []
    total_time = 0
    peak_vram = 0

    for i, test_case in enumerate(test_cases, 1):
        print("-"*80)
        print(f"TEST CASE {i}/{len(test_cases)}: {test_case['name']}")
        print("-"*80)
        print(f"Description: {test_case['description']}")
        print(f"Prompt: '{test_case['prompt']}'")
        print()

        # Clear GPU cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()

        # Generate image
        start_time = time.time()

        image = generator.generate_from_b3_output(
            test_case['prompt'],
            enhance_prompt=True
        )

        gen_time = time.time() - start_time
        total_time += gen_time

        # Get memory stats
        mem_stats = get_gpu_memory_stats()
        if mem_stats:
            peak_vram = max(peak_vram, mem_stats['max_allocated_gb'])

        # Save image
        if image:
            filename = f"test_{i}_{test_case['name'].lower().replace(' ', '_')}.png"
            output_path = output_dir / filename
            image.save(output_path)

            result = {
                "test_case": test_case['name'],
                "success": True,
                "generation_time": gen_time,
                "output_path": str(output_path),
                "vram_gb": mem_stats['max_allocated_gb'] if mem_stats else None
            }

            logger.info(f"✅ SUCCESS - Generated in {gen_time:.2f}s")
            logger.info(f"   Saved to: {output_path}")
            if mem_stats:
                logger.info(f"   Peak VRAM: {mem_stats['max_allocated_gb']:.3f} GB")
        else:
            result = {
                "test_case": test_case['name'],
                "success": False,
                "generation_time": gen_time,
                "output_path": None,
                "vram_gb": None
            }
            logger.error(f"❌ FAILED - Generation unsuccessful")

        results.append(result)
        print()

    # Print summary
    print("="*80)
    print(" TEST SUITE SUMMARY")
    print("="*80)
    print()

    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    avg_time = total_time / len(results)

    print(f"Total Tests: {len(results)}")
    print(f"Successful:  {successful} ✅")
    print(f"Failed:      {failed} ❌")
    print()
    print(f"Performance Metrics:")
    print(f"  Total Generation Time:   {total_time:.2f}s")
    print(f"  Average Generation Time: {avg_time:.2f}s")
    print(f"  Peak VRAM Usage:         {peak_vram:.3f} GB")
    print()

    # Detailed results
    print("Detailed Results:")
    print("-"*80)
    for i, result in enumerate(results, 1):
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{i}. {result['test_case']}: {status}")
        print(f"   Time: {result['generation_time']:.2f}s")
        if result['vram_gb']:
            print(f"   VRAM: {result['vram_gb']:.3f} GB")
        if result['output_path']:
            print(f"   Output: {result['output_path']}")
        print()

    # Performance targets
    print("="*80)
    print(" PERFORMANCE TARGET VALIDATION")
    print("="*80)
    print()

    vram_pass = peak_vram < 3.5
    latency_pass = avg_time < 15.0
    success_pass = successful == len(results)

    print(f"VRAM Target (<3.5GB):        {peak_vram:.3f} GB - {'✅ PASS' if vram_pass else '❌ FAIL'}")
    print(f"Latency Target (<15s avg):   {avg_time:.2f}s - {'✅ PASS' if latency_pass else '❌ FAIL'}")
    print(f"Success Rate (100%):         {successful}/{len(results)} - {'✅ PASS' if success_pass else '❌ FAIL'}")
    print()

    # Final verdict
    all_pass = vram_pass and latency_pass and success_pass

    if all_pass:
        print("="*80)
        print(" ✅ ✅ ✅ ALL TESTS PASSED ✅ ✅ ✅")
        print("="*80)
        print()
        print("B3 + LCM integration is READY FOR PRODUCTION!")
        print("Decision #4 implementation: VALIDATED ✅")
    else:
        print("="*80)
        print(" ⚠️  SOME TARGETS NOT MET ⚠️")
        print("="*80)
        print()
        if not vram_pass:
            print("⚠️  VRAM usage exceeded 3.5GB target")
        if not latency_pass:
            print("⚠️  Average latency exceeded 15s target")
        if not success_pass:
            print("⚠️  Some test cases failed")
        print()
        print("Integration works but may need optimization.")

    # Get final stats
    gen_stats = generator.get_stats()
    print()
    print("Generator Statistics:")
    print(f"  Model: {gen_stats['model_id']}")
    print(f"  Device: {gen_stats['device']}")
    print(f"  Load Time: {gen_stats['load_time']:.2f}s")
    print(f"  Total Generations: {gen_stats['generation_count']}")
    print(f"  Average Time: {gen_stats['average_generation_time']:.2f}s")

    # Cleanup
    generator.unload()
    logger.info("Generator unloaded, GPU memory cleared")

    return all_pass


if __name__ == "__main__":
    success = run_test_suite()
    exit(0 if success else 1)
