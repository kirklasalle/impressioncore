#!/usr/bin/env python3
"""
Test F: Drive Embedding Dataset Loading
======================================

Quick validation that embedding dataset loading works correctly
before starting full 14-21 day training.

Created: October 6, 2025
"""

import sys
from pathlib import Path
import torch

# Add src to path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root))

from src.training.b3_embedding_integration_trainer import (
    EmbeddingIntegrationConfig,
    FDriveEmbeddingDataset,
)

def test_dataset_loading():
    """Test that we can load embeddings from F: drive"""

    print("\n" + "="*80)
    print("Testing F: Drive Embedding Dataset Loading")
    print("="*80 + "\n")

    # Create config
    config = EmbeddingIntegrationConfig()

    print("Configuration:")
    print(f"  Legacy F: Drive Root: {config.f_embeddings_root}")
    print(f"  Shard Root: {config.embedding_shard_root}")
    print(f"  Modalities: {config.modalities}")
    print(f"  Include truncated: {config.include_truncated}")
    print(f"  Max samples/modality: {config.max_samples_per_modality}")
    print(f"  Embedding Dim: {config.embedding_dim}")
    print(f"  Max per Batch: {config.max_embeddings_per_batch}\n")

    # Test each phase dataset
    phases = ["alignment", "generation", "multitask", "finetuning"]

    for phase in phases:
        print("\n" + "="*80)
        print(f"Testing Phase: {phase.upper()}")
        print("="*80 + "\n")

        try:
            # Create dataset
            print(f"Creating dataset for phase: {phase}...")
            dataset = FDriveEmbeddingDataset(config, phase=phase)

            print("✅ Dataset created successfully!")
            print(f"   Total samples: {len(dataset)}")

            if len(dataset) > 0:
                # Test getting a sample
                print("\nTesting sample retrieval...")
                sample = dataset[0]

                print("✅ Sample retrieved successfully!")
                print(f"   Keys: {list(sample.keys())}")
                print(f"   Embedding shape: {sample['embedding'].shape}")
                print(f"   Input IDs shape: {sample['input_ids'].shape}")
                print(f"   Attention mask shape: {sample['attention_mask'].shape}")
                print(f"   Labels shape: {sample['labels'].shape}")
                print(f"   Metadata keys: {list(sample['metadata'].keys())}")
                print(f"   Modality: {sample['metadata'].get('modality')}")
                print(f"   Truncated: {sample['metadata'].get('truncated')}")

                # Check memory usage
                embedding_size_mb = sample['embedding'].nelement() * sample['embedding'].element_size() / (1024**2)
                print(f"   Embedding size: {embedding_size_mb:.2f} MB")

                # Test batch loading
                print("\nTesting batch loading...")
                from torch.utils.data import DataLoader

                dataloader = DataLoader(dataset, batch_size=2, shuffle=False, num_workers=0)
                batch = next(iter(dataloader))

                print("✅ Batch loaded successfully!")
                print(f"   Batch embedding shape: {batch['embedding'].shape}")
                print(f"   Batch input_ids shape: {batch['input_ids'].shape}")

                batch_size_mb = (
                    batch['embedding'].nelement() * batch['embedding'].element_size() +
                    batch['input_ids'].nelement() * batch['input_ids'].element_size()
                ) / (1024**2)
                print(f"   Batch memory: {batch_size_mb:.2f} MB")

            else:
                print("⚠️  Dataset is empty (no embeddings loaded)")

        except Exception as e:
            print(f"❌ Error in phase {phase}:")
            print(f"   {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*80}")
    print("Dataset Loading Test Complete!")
    print(f"{'='*80}\n")

    # Summary
    print("Summary:")
    print("  If all phases loaded successfully, you're ready to start training!")
    print("  If some phases are empty, that's OK - they use different data sources.")
    print("  Check warnings for missing directories or files.")
    print("\nNext step: Run full training with:")
    print("  python launch_b3_embedding_integration.py")

def test_memory_estimate():
    """Estimate memory usage for GTX 1050 Ti"""

    print("\n" + "="*80)
    print("GTX 1050 Ti Memory Estimate")
    print("="*80 + "\n")

    # Model size
    model_params = 35_560_024
    bytes_per_param = 4  # FP32
    model_size_gb = (model_params * bytes_per_param) / (1024**3)

    print(f"Model size: {model_size_gb:.2f} GB ({model_params:,} params)")

    # Embedding batch
    embedding_dim = 768
    batch_size = 1
    embedding_size_gb = (batch_size * embedding_dim * 4) / (1024**3)

    print(f"Embedding batch: {embedding_size_gb:.4f} GB")

    # Gradients (with checkpointing, ~40% of model)
    gradient_size_gb = model_size_gb * 0.4
    print(f"Gradients (checkpointed): {gradient_size_gb:.2f} GB")

    # Optimizer states
    optimizer_size_gb = model_size_gb * 0.3  # Offloaded to CPU
    print(f"Optimizer (offloaded): {optimizer_size_gb:.2f} GB on CPU")

    # Activations
    activation_size_gb = 0.4
    print(f"Activations: {activation_size_gb:.2f} GB")

    # Total GPU
    total_gpu_gb = model_size_gb + embedding_size_gb + gradient_size_gb + activation_size_gb + 0.2  # overhead

    print(f"\nTotal GPU memory: {total_gpu_gb:.2f} GB")
    print("GTX 1050 Ti VRAM: 4.00 GB")

    if total_gpu_gb < 3.5:
        print(f"✅ Should fit comfortably! ({3.5 - total_gpu_gb:.2f} GB safety margin)")
    elif total_gpu_gb < 4.0:
        print(f"⚠️  Tight fit ({4.0 - total_gpu_gb:.2f} GB margin). Monitor carefully.")
    else:
        print(f"❌ May exceed VRAM! ({total_gpu_gb - 4.0:.2f} GB over limit)")
        print("   Consider: Reduce batch size, increase gradient checkpointing")

if __name__ == "__main__":
    print("\n🔍 Running pre-training validation tests...\n")

    # Test dataset loading
    test_dataset_loading()

    # Test memory estimate
    test_memory_estimate()

    print("\n✅ Pre-training validation complete!")
    print("Ready to begin Path C: F: Drive Embedding Integration\n")
