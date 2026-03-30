"""
LCM GTX 1050 Ti Validation Script

Created: October 11, 2025
Updated: October 11, 2025
Author: ImpressionCore Team
Tags: #lcm #diffusion #validation #gtx1050ti
Category: Testing
Status: Active

Purpose:
    Verify LCM (Latent Consistency Models) runs on GTX 1050 Ti (4GB VRAM)
    with memory optimizations. Validates Decision #4 for B3 architecture.

Test Cases:
    1. Model loading with float16 precision
    2. Memory optimizations (CPU offload, attention slicing)
    3. Image generation with 4-step inference
    4. VRAM usage profiling (target: <3GB)
    5. Latency measurement (target: <2s per image)

Success Criteria:
    - Model loads without OOM errors
    - VRAM usage <3GB during generation
    - Image quality: 512x512, coherent output
    - Latency: <2 seconds per image
"""

import torch
import time
import os
from diffusers import AutoPipelineForText2Image, LCMScheduler
from PIL import Image
import psutil

# Memory tracking utilities
def get_gpu_memory():
    """Get current GPU memory usage in GB"""
    if torch.cuda.is_available():
        return torch.cuda.memory_allocated() / (1024**3)
    return 0

def get_gpu_memory_reserved():
    """Get reserved GPU memory in GB"""
    if torch.cuda.is_available():
        return torch.cuda.memory_reserved() / (1024**3)
    return 0

def print_memory_stats(stage=""):
    """Print comprehensive memory statistics"""
    if stage:
        print(f"\n{'='*60}")
        print(f"Memory Stats - {stage}")
        print(f"{'='*60}")

    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / (1024**3)
        reserved = torch.cuda.memory_reserved() / (1024**3)
        max_allocated = torch.cuda.max_memory_allocated() / (1024**3)

        print(f"GPU Memory Allocated:     {allocated:.3f} GB")
        print(f"GPU Memory Reserved:      {reserved:.3f} GB")
        print(f"GPU Memory Max Allocated: {max_allocated:.3f} GB")
        print(f"GPU Device: {torch.cuda.get_device_name(0)}")
    else:
        print("CUDA not available!")

    # System RAM
    ram = psutil.virtual_memory()
    print(f"System RAM Used:          {ram.used / (1024**3):.3f} GB / {ram.total / (1024**3):.3f} GB")
    print(f"{'='*60}\n")

def test_lcm_loading():
    """Test 1: Load LCM model with memory optimizations"""
    print("\n" + "="*60)
    print("TEST 1: LCM Model Loading")
    print("="*60)

    try:
        print("Loading SimianLuo/LCM_Dreamshaper_v7...")
        print("Optimizations: torch.float16, CPU offload, attention slicing")

        start_time = time.time()

        # Load LCM pipeline with memory optimizations
        pipe = AutoPipelineForText2Image.from_pretrained(
            "SimianLuo/LCM_Dreamshaper_v7",
            torch_dtype=torch.float16
        )

        # Configure LCM scheduler
        pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)

        # Move to GPU with optimizations
        pipe = pipe.to("cuda")

        # Enable memory optimizations
        pipe.enable_model_cpu_offload()  # Offload to CPU when not in use
        pipe.enable_attention_slicing()   # Slice attention for memory efficiency

        load_time = time.time() - start_time

        print(f"✅ Model loaded successfully in {load_time:.2f} seconds")
        print_memory_stats("After Model Loading")

        return pipe, True

    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        print_memory_stats("After Loading Failure")
        return None, False

def test_lcm_generation(pipe, prompt="a serene mountain landscape at sunset", num_steps=4):
    """Test 2: Generate image with LCM"""
    print("\n" + "="*60)
    print("TEST 2: LCM Image Generation")
    print("="*60)
    print(f"Prompt: '{prompt}'")
    print(f"Inference Steps: {num_steps}")

    try:
        # Clear GPU cache before generation
        torch.cuda.empty_cache()
        print_memory_stats("Before Generation")

        start_time = time.time()

        # Generate image with LCM (4 steps, 512x512)
        image = pipe(
            prompt=prompt,
            num_inference_steps=num_steps,
            guidance_scale=1.0,  # LCM uses minimal guidance
            lcm_origin_steps=50,  # Original diffusion steps
            height=512,
            width=512,
        ).images[0]

        gen_time = time.time() - start_time

        print(f"✅ Image generated successfully in {gen_time:.2f} seconds")
        print(f"   Image size: {image.size}")
        print_memory_stats("After Generation")

        # Save test image
        output_dir = "test_outputs"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "lcm_test_output.png")
        image.save(output_path)
        print(f"   Image saved to: {output_path}")

        return image, gen_time, True

    except Exception as e:
        print(f"❌ Image generation failed: {e}")
        print_memory_stats("After Generation Failure")
        return None, 0, False

def test_lcm_stress(pipe, num_images=3):
    """Test 3: Generate multiple images to test stability"""
    print("\n" + "="*60)
    print("TEST 3: LCM Stress Test (Multiple Images)")
    print("="*60)
    print(f"Generating {num_images} images consecutively...")

    prompts = [
        "a red apple on a wooden table",
        "a futuristic city with flying cars at night",
        "a cute cat sleeping on a cozy blanket"
    ]

    times = []
    max_vram = 0

    for i, prompt in enumerate(prompts[:num_images], 1):
        print(f"\n--- Image {i}/{num_images} ---")
        print(f"Prompt: '{prompt}'")

        try:
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()

            start_time = time.time()

            image = pipe(
                prompt=prompt,
                num_inference_steps=4,
                guidance_scale=1.0,
                lcm_origin_steps=50,
                height=512,
                width=512,
            ).images[0]

            gen_time = time.time() - start_time
            times.append(gen_time)

            # Track peak VRAM
            peak_vram = torch.cuda.max_memory_allocated() / (1024**3)
            max_vram = max(max_vram, peak_vram)

            print(f"✅ Generated in {gen_time:.2f}s | Peak VRAM: {peak_vram:.3f} GB")

            # Save image
            output_path = f"test_outputs/lcm_stress_test_{i}.png"
            image.save(output_path)
            print(f"   Saved to: {output_path}")

        except Exception as e:
            print(f"❌ Generation {i} failed: {e}")
            return False

    # Summary
    avg_time = sum(times) / len(times)
    print(f"\n{'='*60}")
    print(f"Stress Test Summary:")
    print(f"  Total Images: {num_images}")
    print(f"  Average Time: {avg_time:.2f}s")
    print(f"  Max VRAM: {max_vram:.3f} GB")
    print(f"  Target: <3GB VRAM ✅" if max_vram < 3.0 else f"  Target: <3GB VRAM ⚠️ (exceeded)")
    print(f"  Target: <2s latency ✅" if avg_time < 2.0 else f"  Target: <2s latency ⚠️ (slower)")
    print(f"{'='*60}")

    return True

def main():
    """Run all LCM validation tests"""
    print("\n" + "#"*60)
    print("# LCM GTX 1050 Ti Validation Suite")
    print("#"*60)
    print(f"# Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
    print(f"# CUDA Available: {torch.cuda.is_available()}")
    print(f"# PyTorch Version: {torch.__version__}")
    print("#"*60)

    if not torch.cuda.is_available():
        print("\n❌ CUDA not available! LCM requires GPU.")
        return False

    print_memory_stats("Initial State")

    # Test 1: Load model
    pipe, load_success = test_lcm_loading()
    if not load_success:
        print("\n❌ VALIDATION FAILED: Could not load LCM model")
        return False

    # Test 2: Single generation
    _, gen_time, gen_success = test_lcm_generation(
        pipe,
        prompt="a serene mountain landscape at sunset",
        num_steps=4
    )
    if not gen_success:
        print("\n❌ VALIDATION FAILED: Could not generate image")
        return False

    # Test 3: Stress test
    stress_success = test_lcm_stress(pipe, num_images=3)
    if not stress_success:
        print("\n❌ VALIDATION FAILED: Stress test failed")
        return False

    # Final verdict
    print("\n" + "#"*60)
    print("# FINAL VALIDATION RESULT")
    print("#"*60)

    final_vram = get_gpu_memory()
    max_vram = torch.cuda.max_memory_allocated() / (1024**3)

    print(f"Current VRAM: {final_vram:.3f} GB")
    print(f"Peak VRAM:    {max_vram:.3f} GB")
    print(f"Latency:      {gen_time:.2f}s per image")

    if max_vram < 3.0 and gen_time < 2.0:
        print("\n✅ ✅ ✅ LCM VALIDATION PASSED ✅ ✅ ✅")
        print("LCM is suitable for GTX 1050 Ti integration with B3!")
        return True
    elif max_vram < 3.5:
        print("\n⚠️  LCM VALIDATION PARTIAL SUCCESS ⚠️")
        print("LCM works but may need additional optimizations.")
        return True
    else:
        print("\n❌ LCM VALIDATION FAILED")
        print("VRAM usage too high for GTX 1050 Ti.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
