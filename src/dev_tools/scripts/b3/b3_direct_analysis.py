#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #attention_mechanism #cuda #inference #memory_management #python #source_code #src/scripts\b3\b3_direct_analysis.py #testing #training #transformer
**Category:** Source Code
**Status:** Active
"""



import json
import time
from datetime import datetime
from pathlib import Path

import torch


def analyze_b3_model():
    """Analyze the B3 best quality model directly"""

    model_path = "F:/models/checkpoints/b3/b3_best_quality_model_20250802_124801.pth"

    print("="*60)
    print("ImpressionCore B3 Model Analysis")
    print("="*60)
    print(f"Model: {Path(model_path).name}")
    print(f"Size: {Path(model_path).stat().st_size / (1024*1024):.2f} MB")
    print(f"Modified: {datetime.fromtimestamp(Path(model_path).stat().st_mtime)}")
    print("-"*60)

    try:
        print("Loading checkpoint...")
        checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
        print("Checkpoint loaded successfully!")

        print("\nCheckpoint structure:")
        if isinstance(checkpoint, dict):
            for key in checkpoint:
                value = checkpoint[key]
                if isinstance(value, torch.Tensor):
                    print(f"  {key}: Tensor {value.shape} [{value.dtype}]")
                elif isinstance(value, dict):
                    print(f"  {key}: Dict with {len(value)} items")
                elif isinstance(value, list):
                    print(f"  {key}: List with {len(value)} items")
                else:
                    print(f"  {key}: {type(value).__name__} - {value}")
        else:
            print(f"  Direct tensor: {type(checkpoint).__name__}")
            if hasattr(checkpoint, 'shape'):
                print(f"  Shape: {checkpoint.shape}")

        # Analyze model content
        print("\nDetailed Analysis:")

        if isinstance(checkpoint, dict):
            # Check for training metadata
            training_keys = ['epoch', 'step', 'loss', 'conversation_quality', 'teacher_model']
            print("Training Information:")
            for key in training_keys:
                if key in checkpoint:
                    print(f"  {key}: {checkpoint[key]}")
                else:
                    print(f"  {key}: Not found")

            # Check for model state
            if 'model_state_dict' in checkpoint:
                model_state = checkpoint['model_state_dict']
                print(f"\nModel State Dict: {len(model_state)} parameters")

                # Analyze parameter sizes
                total_params = 0
                for name, param in model_state.items():
                    if isinstance(param, torch.Tensor):
                        param_count = param.numel()
                        total_params += param_count
                        print(f"  {name}: {param.shape} ({param_count:,} params)")

                print(f"\nTotal Parameters: {total_params:,}")
                print(f"Estimated Model Size: {total_params * 4 / (1024*1024):.2f} MB (float32)")

            # Check for optimizer state
            if 'optimizer_state_dict' in checkpoint:
                print("\nOptimizer State: Present")

            # Check for custom metadata
            custom_keys = [k for k in checkpoint
                          if k not in ['model_state_dict', 'optimizer_state_dict', 'epoch', 'step']]
            if custom_keys:
                print("\nCustom Metadata:")
                for key in custom_keys:
                    value = checkpoint[key]
                    if isinstance(value, str | int | float | bool):
                        print(f"  {key}: {value}")
                    else:
                        print(f"  {key}: {type(value).__name__}")

        # Performance test
        print("\nPerformance Test:")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Device: {device}")

        # Measure loading time
        start_time = time.perf_counter()
        test_checkpoint = torch.load(model_path, map_location=device, weights_only=False)
        load_time = (time.perf_counter() - start_time) * 1000
        print(f"Loading Time: {load_time:.2f} ms")

        # Memory usage
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            initial_memory = torch.cuda.memory_allocated()
            _ = test_checkpoint  # Keep in memory
            final_memory = torch.cuda.memory_allocated()
            memory_usage = (final_memory - initial_memory) / (1024*1024)
            print(f"VRAM Usage: {memory_usage:.2f} MB")

            # GTX 1050 Ti compatibility check
            gtx1050ti_vram = 4096  # 4GB in MB
            estimated_inference_memory = memory_usage * 2  # Rough estimate for inference

            print("GTX 1050 Ti Compatibility:")
            print(f"  Available VRAM: {gtx1050ti_vram} MB")
            print(f"  Estimated Usage: {estimated_inference_memory:.2f} MB")
            print(f"  Compatible: {'Yes' if estimated_inference_memory < 3000 else 'Possibly' if estimated_inference_memory < 3500 else 'No'}")

        print("\nAnalysis completed successfully!")

        # Save analysis results
        results = {
            'model_path': model_path,
            'file_size_mb': Path(model_path).stat().st_size / (1024*1024),
            'modification_date': datetime.fromtimestamp(Path(model_path).stat().st_mtime).isoformat(),
            'checkpoint_type': type(checkpoint).__name__,
            'loading_time_ms': load_time,
            'analysis_timestamp': datetime.now().isoformat()
        }

        if isinstance(checkpoint, dict):
            results['checkpoint_keys'] = list(checkpoint.keys())
            for key in ['epoch', 'step', 'conversation_quality', 'teacher_model']:
                if key in checkpoint:
                    results[key] = checkpoint[key]

        if torch.cuda.is_available():
            results['vram_usage_mb'] = memory_usage
            results['gtx1050ti_compatible'] = estimated_inference_memory < 3000

        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"b3_model_analysis_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\nResults saved to: {results_file}")

        return results

    except Exception as e:
        print(f"Error during analysis: {e}")
        return None

def quick_inference_test():
    """Quick inference capability test"""

    print("\n" + "="*60)
    print("Quick Inference Test")
    print("="*60)

    model_path = "F:/models/checkpoints/b3/b3_best_quality_model_20250802_124801.pth"

    try:
        print("Loading model for inference test...")
        checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)

        # Check if this looks like a usable model
        if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
            print("Model state dict found - this appears to be a trained model")

            # Extract some information about the model architecture
            model_state = checkpoint['model_state_dict']

            # Look for common model components
            has_embeddings = any('embed' in key.lower() for key in model_state)
            has_transformer = any('transformer' in key.lower() or 'attention' in key.lower() for key in model_state)
            has_output = any('output' in key.lower() or 'head' in key.lower() for key in model_state)

            print("Model Components Detected:")
            print(f"  Embeddings: {'Yes' if has_embeddings else 'No'}")
            print(f"  Transformer/Attention: {'Yes' if has_transformer else 'No'}")
            print(f"  Output Layer: {'Yes' if has_output else 'No'}")

            # Get vocabulary size if available
            for key, param in model_state.items():
                if 'embed' in key.lower() and len(param.shape) >= 2:
                    vocab_size = param.shape[0]
                    embed_dim = param.shape[1]
                    print(f"  Vocabulary Size: {vocab_size:,}")
                    print(f"  Embedding Dimension: {embed_dim}")
                    break

            # Check for quality metrics
            if 'conversation_quality' in checkpoint:
                quality = checkpoint['conversation_quality']
                print(f"\nConversation Quality: {quality}")

                if quality > 8.0:
                    print("  Assessment: EXCELLENT quality!")
                elif quality > 6.0:
                    print("  Assessment: GOOD quality")
                elif quality > 4.0:
                    print("  Assessment: FAIR quality")
                else:
                    print("  Assessment: Needs improvement")

            print("\nInference Readiness: Model appears ready for inference")
            print("Note: Full inference requires model architecture reconstruction")

        else:
            print("This appears to be a raw model tensor")
            print("May require additional setup for inference")

        return True

    except Exception as e:
        print(f"Error during inference test: {e}")
        return False

if __name__ == "__main__":
    # Run analysis
    results = analyze_b3_model()

    # Run quick inference test
    quick_inference_test()

    print("\n" + "="*60)
    print("Analysis Complete!")
    print("="*60)
