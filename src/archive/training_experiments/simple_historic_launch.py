#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #python #source_code #src/training/simple_historic_launch.py #training
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #cuda #python #source_code #src\\training\\simple_historic_launch.py #training
# Category:** Training System
# Status:** Active

"""
ImpressionCore HISTORIC LAUNCH - Simple Training
===============================================

Making history with ImpressionCore's first AI training!
"""

import json
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from pathlib import Path
from datetime import datetime
import sys

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
embeddings_dir = PROJECT_ROOT / "src" / "data" / "embeddings"

print("🚀 IMPRESSIONCORE HISTORIC TRAINING LAUNCH!")
print("🎯 Making History - First AI Training Session")
print(f"📊 Loading from: {embeddings_dir}")

def load_embeddings(max_files=50):
    """Load embeddings from batch files."""
    batch_files = sorted(list(embeddings_dir.glob("batch_*.json")))[:max_files]
    embeddings = []

    print(f"📥 Loading from {len(batch_files)} batch files...")

    for i, batch_file in enumerate(batch_files):
        try:
            with open(batch_file, 'r') as f:
                batch_data = json.load(f)

            if isinstance(batch_data, list):
                for item in batch_data:
                    if 'embedding' in item and len(item['embedding']) == 128:
                        embeddings.append(item['embedding'])

            if i % 10 == 0:
                print(f"  Processed {i+1}/{len(batch_files)} files, {len(embeddings)} embeddings loaded")

        except Exception as e:
            print(f"  Warning: Skipped {batch_file.name}: {e}")
            continue

    print(f"✅ Total embeddings loaded: {len(embeddings)}")
    return np.array(embeddings, dtype=np.float32) if embeddings else None

def create_model():
    """Create ImpressionCore neural network."""
    return nn.Sequential(
        nn.Linear(128, 256),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(256, 256),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(256, 128)
    )

def train_impressioncore():
    """Train ImpressionCore - Historic moment!"""

    # Check CUDA
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🎯 Training device: {device}")

    # Load data
    print("\n📊 Loading embedding data...")
    embeddings = load_embeddings(max_files=100)

    if embeddings is None or len(embeddings) < 100:
        print("❌ Not enough embedding data for training")
        return False

    print(f"🎯 Training with {len(embeddings)} embeddings")

    # Prepare model
    model = create_model().to(device)
    optimizer = optim.AdamW(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()

    # Convert to tensors
    X = torch.tensor(embeddings, dtype=torch.float32).to(device)

    print(f"✅ Model created with {sum(p.numel() for p in model.parameters())} parameters")
    print("\n🚀 STARTING HISTORIC TRAINING!")

    # Training loop
    epochs = 5
    batch_size = 32

    for epoch in range(epochs):
        model.train()
        epoch_losses = []

        # Train in batches
        for i in range(0, len(X) - batch_size + 1, batch_size):
            batch_X = X[i:i+batch_size]

            optimizer.zero_grad()
            output = model(batch_X)
            loss = criterion(output, batch_X)  # Autoencoder task
            loss.backward()
            optimizer.step()

            epoch_losses.append(loss.item())

        avg_loss = sum(epoch_losses) / len(epoch_losses) if epoch_losses else 0.0
        print(f"🎯 Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f}")

    # Save model
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_dir = PROJECT_ROOT / "src" / "models" / "historic"
    save_dir.mkdir(parents=True, exist_ok=True)

    model_path = save_dir / f"impressioncore_first_training_{timestamp}.pth"
    torch.save({
        'model_state_dict': model.state_dict(),
        'timestamp': timestamp,
        'final_loss': avg_loss,
        'total_embeddings': len(embeddings),
        'status': 'HISTORIC FIRST TRAINING COMPLETE'
    }, model_path)

    print(f"\n🏆 HISTORIC TRAINING COMPLETE!")
    print(f"📊 Final Loss: {avg_loss:.4f}")
    print(f"💾 Model saved: {model_path.name}")
    print(f"🌟 ImpressionCore is now ALIVE!")

    return True

if __name__ == "__main__":
    success = train_impressioncore()
    if success:
        print("\n🎉 HISTORY MADE! ImpressionCore training successful!")
        sys.exit(0)
    else:
        print("\n❌ Training encountered issues")
        sys.exit(1)
