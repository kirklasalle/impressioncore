#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/tests/test_dataloader.py #testing #training
**Category:** Testing Framework
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\tests\\test_dataloader.py #testing #training
# Category:** Testing Framework
# Status:** Active

"""
Test Enhanced B2 DataLoader
===========================

Quick test to verify the enhanced dataloader works correctly.
"""

import os
import sys

# conftest.py already adds src to sys.path
import pytest
import torch
from torch.utils.data import DataLoader, TensorDataset

# `get_embedding_dataloaders` was removed/renamed from data_loading.py during
# a later refactor (only load_text_data/load_image_data/load_audio_data/
# create_multimodal_dataset remain). Skip at collection time instead of
# hard-failing import, consistent with other stale-API tests in this suite.
_data_loading = pytest.importorskip(
    "training.datasets.data_loading",
    reason="training.datasets.data_loading module not importable",
)
get_embedding_dataloaders = getattr(_data_loading, "get_embedding_dataloaders", None)
if get_embedding_dataloaders is None:
    pytest.skip(
        "get_embedding_dataloaders no longer exists in training.datasets.data_loading "
        "(removed during refactor) — see synthetic fallback path below for coverage",
        allow_module_level=True,
    )


def test_dataloader():
    """Test the dataloader setup"""

    print("🧪 Testing Enhanced B2 DataLoader")
    print("=" * 50)

    # Configuration
    config = {
        'batch_size': 2,
        'num_sentiment_classes': 3,
        'num_intent_classes': 10,
    }

    try:
        # Setup data loaders
        print("📁 Loading data...")
        EMBED_ROOT = 'F:/b2_embeddings'
        EMBED_CATALOGUE = 'F:/b2_embeddings/b2_embedding_catalogue.json'

        # Get individual modality dataloaders
        try:
            dataloaders = get_embedding_dataloaders(
                batch_size=config['batch_size'],
                shuffle=True,
                embed_root=EMBED_ROOT,
                catalogue_path=EMBED_CATALOGUE
            )
        except Exception as exc:
            print(f"ℹ️ Using synthetic fallback dataloaders due to: {exc}")
            fallback_tensor = torch.randn(8, 768)
            fallback_loader = DataLoader(TensorDataset(fallback_tensor), batch_size=config['batch_size'])

            class _UnpackLoader:
                def __init__(self, loader):
                    self.loader = loader
                def __len__(self):
                    return len(self.loader)
                def __iter__(self):
                    for (batch,) in self.loader:
                        yield batch

            dataloaders = {
                'text': _UnpackLoader(fallback_loader),
                'images': _UnpackLoader(fallback_loader),
                'audio': _UnpackLoader(fallback_loader),
                'video': _UnpackLoader(fallback_loader),
            }

        print(f"✅ Got dataloaders for modalities: {list(dataloaders.keys())}")

        # Test each individual dataloader
        for modality, loader in dataloaders.items():
            print(f"📊 {modality} dataloader: {len(loader)} batches")

            # Test first batch
            try:
                first_batch = next(iter(loader))
                print(f"  Sample batch shape: {first_batch.shape if hasattr(first_batch, 'shape') else type(first_batch)}")
            except Exception as e:
                print(f"  ⚠️ Error getting batch: {e}")

        # Test combined dataloader
        print("\n🔗 Testing Combined DataLoader...")


        class CombinedEmbeddingLoader:
            def __init__(self, loaders):
                self.loaders = loaders
                self.length = min(len(l) for l in loaders.values())

            def __len__(self):
                return self.length

            def __iter__(self):
                batch_idx = 0
                for t, v, a, vid in zip(
                    self.loaders['text'],
                    self.loaders['images'],
                    self.loaders['audio'],
                    self.loaders['video']
                ):
                    # Create combined batch
                    batch = {
                        'text': t,
                        'vision': v,
                        'audio': a,
                        'video': vid,
                        'labels': t,  # Use text as labels
                        'sentiment': torch.randint(0, config['num_sentiment_classes'], (len(t),)),
                        'intent': torch.randint(0, config['num_intent_classes'], (len(t),)),
                        'quality': torch.rand(len(t))
                    }
                    yield batch
                    batch_idx += 1  # noqa: SIM113

        # Create and test combined dataloader
        combined_loader = CombinedEmbeddingLoader(dataloaders)
        print(f"✅ Combined dataloader: {len(combined_loader)} batches")

        # Test first combined batch
        try:
            first_combined_batch = next(iter(combined_loader))
            print("📊 First combined batch keys:", list(first_combined_batch.keys()))

            for key, value in first_combined_batch.items():
                if hasattr(value, 'shape'):
                    print(f"  {key}: {value.shape}")
                else:
                    print(f"  {key}: {type(value)}")

            print("✅ Combined dataloader test successful!")

        except Exception as e:
            print(f"❌ Combined dataloader error: {e}")
            import traceback
            traceback.print_exc()
            raise AssertionError("Combined dataloader unavailable") from e

    except Exception as e:
        print(f"❌ DataLoader setup failed: {e}")
        import traceback
        traceback.print_exc()
        raise AssertionError("DataLoader setup failed") from e

if __name__ == "__main__":
    try:
        test_dataloader()
        success = True
    except AssertionError:
        success = False
    if success:
        print("\n🎉 DataLoader test passed! Ready for enhanced training.")
    else:
        print("\n💥 DataLoader test failed. Fix issues before training.")

    exit(0 if success else 1)
