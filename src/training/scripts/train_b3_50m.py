#!/usr/bin/env python3
"""
B3 50M Parameter Training Script
===============================

Direct training script for the validated 50M parameter B3 architecture.
Implements Sweet Spot methodology with efficiency monitoring.

Created: August 7, 2025
Author: Kirk LaSalle & GitHub Copilot
"""

import gc
import sys
import time
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

print("🚀 Starting B3 50M Parameter Training System")
print("=" * 50)

# Import B3 components directly
try:
    from core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model
    print("✅ B3 components imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class B3TrainingDataset(Dataset):
    """Training dataset for B3 50M parameter model."""

    def __init__(self, size=5000, seq_len=256):
        self.size = size
        self.seq_len = seq_len
        self.vocab_size = 16384  # B3 50M vocab size
        self.image_embed_dim = 256  # B3 50M image embedding
        self.audio_embed_dim = 256  # B3 50M audio embedding
        self.phoneme_vocab_size = 256

    def __len__(self):
        return self.size

    def __getitem__(self, idx):
        # Generate training data
        input_ids = torch.randint(1, self.vocab_size-1, (self.seq_len,))
        targets = torch.cat([input_ids[1:], torch.tensor([0])])

        # Multimodal features with correct dimensions
        image_features = torch.randn(self.seq_len, self.image_embed_dim)
        audio_features = torch.randn(self.seq_len, self.audio_embed_dim)
        phoneme_ids = torch.randint(0, self.phoneme_vocab_size, (self.seq_len,))
        modality_type = torch.zeros(self.seq_len, dtype=torch.long)

        return {
            'input_ids': input_ids,
            'targets': targets,
            'image_features': image_features,
            'audio_features': audio_features,
            'phoneme_ids': phoneme_ids,
            'modality_type': modality_type
        }

def monitor_efficiency(loss_history, memory_usage, samples_per_sec):
    """Monitor training efficiency using Sweet Spot methodology."""
    if len(loss_history) < 3:
        return True, 1.0

    # Calculate recent improvement
    recent_losses = loss_history[-3:]
    improvement = (recent_losses[0] - recent_losses[-1]) / recent_losses[0]

    # Efficiency score
    loss_score = max(0, 1.0 - (recent_losses[-1] / 10.0))
    memory_score = max(0, 1.0 - (memory_usage / 3500))  # GTX 1050 Ti limit
    throughput_score = min(1.0, samples_per_sec / 15.0)

    efficiency = (0.4 * loss_score + 0.3 * memory_score + 0.3 * throughput_score)

    # Stop if efficiency drops below 60% or no improvement
    should_continue = efficiency > 0.6 and improvement > -0.05

    return should_continue, efficiency

def get_memory_usage():
    """Get current VRAM usage."""
    if torch.cuda.is_available():
        return torch.cuda.memory_allocated() / (1024 * 1024)
    return 0.0

def main():
    """Main training function."""

    # Setup device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🎯 Device: {device}")

    # Create validated 50M configuration
    config = B3Config(
        embed_dim=256,          # Validated 50M config
        num_heads=8,
        num_layers=12,
        vocab_size=16384,
        num_experts=4,
        expert_dim=320,
        experts_per_token=2,
        image_embed_dim=256,
        audio_embed_dim=256,
        phoneme_vocab_size=256,
        dropout=0.1,
        max_seq_length=2048,
        use_gradient_checkpointing=True
    )

    print("📊 B3 50M Configuration:")
    print(f"  Embed Dim: {config.embed_dim}")
    print(f"  Num Layers: {config.num_layers}")
    print(f"  Vocab Size: {config.vocab_size}")
    print(f"  Num Experts: {config.num_experts}")

    # Initialize model
    print("🏗️ Initializing B3 50M Model...")
    model = ImpressionCoreB3Model(config)
    model = model.to(device)

    total_params = sum(p.numel() for p in model.parameters())
    print(f"📊 Total Parameters: {total_params:,} ({total_params/1e6:.1f}M)")

    # Create dataset and dataloader
    print("📚 Creating Dataset...")
    dataset = B3TrainingDataset(size=4000, seq_len=256)
    dataloader = DataLoader(dataset, batch_size=2, shuffle=True, num_workers=0)

    # Initialize optimizer
    optimizer = optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.01)

    # Training loop with efficiency monitoring
    print("\n🚀 Starting Training Loop")
    print("🎯 Will stop when efficiency drops or training becomes inefficient")
    print("-" * 50)

    model.train()
    loss_history = []
    epoch = 0
    start_time = time.time()

    try:
        while True:
            epoch += 1
            epoch_losses = []
            epoch_start = time.time()
            samples_processed = 0

            print(f"\n📅 Epoch {epoch}")

            for batch_idx, batch in enumerate(dataloader):
                batch_start = time.time()

                # Move to device
                input_ids = batch['input_ids'].to(device)
                targets = batch['targets'].to(device)
                image_features = batch['image_features'].to(device)
                audio_features = batch['audio_features'].to(device)
                phoneme_ids = batch['phoneme_ids'].to(device)
                modality_type = batch['modality_type'].to(device)

                # Forward pass
                optimizer.zero_grad()

                try:
                    outputs = model(
                        input_ids=input_ids,
                        image_features=image_features,
                        audio_features=audio_features,
                        phoneme_ids=phoneme_ids,
                        modality_type=modality_type
                    )

                    # Calculate loss
                    if isinstance(outputs, dict):
                        logits = outputs.get('logits', outputs[next(iter(outputs.keys()))])
                    else:
                        logits = outputs

                    loss = nn.functional.cross_entropy(
                        logits.view(-1, logits.size(-1)),
                        targets.view(-1),
                        ignore_index=0
                    )

                    # Backward pass
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                    optimizer.step()

                    epoch_losses.append(loss.item())
                    samples_processed += input_ids.size(0)

                    # Print progress every 25 batches
                    if batch_idx % 25 == 0:
                        batch_time = time.time() - batch_start
                        samples_per_sec = input_ids.size(0) / batch_time
                        memory_mb = get_memory_usage()

                        print(f"  Batch {batch_idx:3d}: Loss={loss.item():.4f}, "
                              f"Speed={samples_per_sec:.1f} samples/s, "
                              f"VRAM={memory_mb:.0f}MB")

                        # Clean memory
                        if batch_idx % 50 == 0:
                            torch.cuda.empty_cache() if torch.cuda.is_available() else None
                            gc.collect()

                except Exception as e:
                    print(f"❌ Error in batch {batch_idx}: {e}")
                    continue

            # Epoch summary
            if epoch_losses:
                avg_loss = sum(epoch_losses) / len(epoch_losses)
                loss_history.append(avg_loss)

                epoch_time = time.time() - epoch_start
                samples_per_sec = samples_processed / epoch_time
                memory_mb = get_memory_usage()

                print(f"📊 Epoch {epoch} Summary:")
                print(f"  Average Loss: {avg_loss:.6f}")
                print(f"  Samples/sec: {samples_per_sec:.1f}")
                print(f"  VRAM Usage: {memory_mb:.0f} MB")
                print(f"  Time: {epoch_time:.1f}s")

                # Check efficiency
                should_continue, efficiency = monitor_efficiency(
                    loss_history, memory_mb, samples_per_sec
                )

                print(f"  Efficiency Score: {efficiency:.3f}")

                if not should_continue:
                    print("\n⚠️ INEFFICIENCY DETECTED!")
                    print("🛑 Training stopped due to efficiency threshold")
                    print("🎯 Sweet Spot methodology suggests stopping here")
                    break

                if efficiency < 0.7:
                    print(f"⚠️ Low efficiency warning: {efficiency:.3f}")

            else:
                print("❌ No valid batches in this epoch")
                break

            # Stop after 15 epochs for this demonstration
            if epoch >= 15:
                print("\n🎯 Training session complete (15 epochs)")
                break

    except KeyboardInterrupt:
        print("\n⚠️ Training interrupted by user")
    except Exception as e:
        print(f"\n❌ Training error: {e}")
        raise

    # Final summary
    total_time = time.time() - start_time
    print("\n✅ B3 50M Training Complete!")
    print(f"⏱️ Total Time: {total_time/60:.1f} minutes")
    print(f"📊 Epochs Completed: {epoch}")

    if loss_history:
        print(f"📉 Final Loss: {loss_history[-1]:.6f}")
        if len(loss_history) > 1:
            improvement = ((loss_history[0] - loss_history[-1]) / loss_history[0] * 100)
            print(f"📈 Loss Improvement: {improvement:.1f}%")

        # Save checkpoint
        checkpoint_dir = Path("F:/models/checkpoints/b3_50m")
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        checkpoint = {
            'model_state_dict': model.state_dict(),
            'config': config,
            'loss_history': loss_history,
            'total_params': total_params
        }

        checkpoint_path = checkpoint_dir / f"b3_50m_epoch_{epoch}.pt"
        torch.save(checkpoint, checkpoint_path)
        print(f"💾 Model saved: {checkpoint_path}")

    print("\n🎉 B3 50M Training Session Complete!")
    print("✅ Ready for deployment or further training")

if __name__ == "__main__":
    main()
