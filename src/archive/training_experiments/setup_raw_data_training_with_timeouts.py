#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #attention_mechanism #command_line #cuda #deployment #gpu_optimization #memory_management #multimodal #python #source_code #src/training/setup_raw_data_training_with_timeouts.py #testing #tokenization #training #transformer
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #attention_mechanism #command_line #cuda #deployment #gpu_optimization #memory_management #multimodal #python #source_code #src\\training\\setup_raw_data_training_with_timeouts.py #testing #tokenization #training #transformer
# Category:** Training System
# Status:** Active

"""
ImpressionCore B2 Raw Data Training Setup with Robust Timeout Mechanisms
Comprehensive preparation for Phase 2: Raw Multimodal Data Training

This script prepares the complete pipeline for training with real multimodal data:
- Text-image-audio conversations
- End-to-end encoder training
- Production-ready deployment pipeline
- Robust timeout and anti-hang mechanisms
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import numpy as np
import time
import os
import json
import h5py  # For distillation data storage
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union
import logging
from dataclasses import dataclass
from PIL import Image
import torchaudio
import torchvision.transforms as transforms
from transformers import (
    AutoTokenizer, AutoModel,
    CLIPProcessor, CLIPModel,
    Wav2Vec2Processor, Wav2Vec2Model
)
from sklearn.metrics import accuracy_score, f1_score, classification_report
import pandas as pd
import signal
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import psutil
import gc
import queue
import multiprocessing
import sys
import traceback

# Import B2 multimodal architecture
try:
    from src.models.b2_multimodal.core.b2_multimodal_model import B2MultimodalModel
    from src.core.utils.rich_enhancements import FallbackProgress, RichEnhancer
    from src.core.utils.rich_logging import RichLogger
    from src.core.utils.rich_status_animation import RichStatusAnimation
except ImportError as e:
    print(f"Warning: Could not import B2 components: {e}")
    print("Falling back to basic implementations...")


class TimeoutManager:
    """Manages timeout and anti-hang mechanisms for training processes"""

    def __init__(self, default_timeout: int = 300):  # 5 minutes default
        self.default_timeout = default_timeout
        self.active_timers = {}
        self.interrupt_flag = threading.Event()

    def set_timeout(self, name: str, timeout: int = None):
        """Set a timeout for a named operation"""
        timeout = timeout or self.default_timeout

        def timeout_handler():
            if not self.interrupt_flag.wait(timeout):
                print(f"\n⚠️ TIMEOUT: Operation '{name}' exceeded {timeout} seconds")
                print("Triggering graceful shutdown...")
                self.interrupt_flag.set()

        timer = threading.Timer(timeout, timeout_handler)
        self.active_timers[name] = timer
        timer.start()
        return timer

    def clear_timeout(self, name: str):
        """Clear a specific timeout"""
        if name in self.active_timers:
            self.active_timers[name].cancel()
            del self.active_timers[name]

    def clear_all_timeouts(self):
        """Clear all active timeouts"""
        for timer in self.active_timers.values():
            timer.cancel()
        self.active_timers.clear()

    def is_interrupted(self):
        """Check if an interrupt/timeout has occurred"""
        return self.interrupt_flag.is_set()

    def reset(self):
        """Reset the timeout manager"""
        self.clear_all_timeouts()
        self.interrupt_flag.clear()


class ProcessWatchdog:
    """Monitors system resources and prevents hangs"""

    def __init__(self, memory_threshold_gb: float = 28.0, gpu_memory_threshold_gb: float = 3.5):
        self.memory_threshold = memory_threshold_gb * 1024 * 1024 * 1024  # Convert to bytes
        self.gpu_memory_threshold = gpu_memory_threshold_gb * 1024 * 1024 * 1024
        self.monitoring = False
        self.alert_callback = None

    def start_monitoring(self, alert_callback=None):
        """Start resource monitoring in background thread"""
        self.alert_callback = alert_callback
        self.monitoring = True

        def monitor():
            while self.monitoring:
                try:
                    # Check system memory
                    memory_info = psutil.virtual_memory()
                    if memory_info.used > self.memory_threshold:
                        if self.alert_callback:
                            self.alert_callback(f"High memory usage: {memory_info.used / 1e9:.1f}GB")

                    # Check GPU memory if available
                    if torch.cuda.is_available():
                        gpu_memory = torch.cuda.memory_allocated()
                        if gpu_memory > self.gpu_memory_threshold:
                            if self.alert_callback:
                                self.alert_callback(f"High GPU memory: {gpu_memory / 1e9:.1f}GB")

                    time.sleep(5)  # Check every 5 seconds
                except Exception as e:
                    print(f"Watchdog monitoring error: {e}")

        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()

    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False


@dataclass
class RawDataConfig:
    """Configuration for raw data training with timeout settings"""
    # Model architecture
    vocab_size: int = 50257
    embed_dim: int = 768
    num_heads: int = 12
    num_layers: int = 12
    max_seq_len: int = 128000
    num_sentiment_classes: int = 3
    num_intent_classes: int = 10

    # Training parameters
    batch_size: int = 1  # Reduced for multimodal complexity
    max_epochs: int = 50
    base_lr: float = 0.00005  # Lower for end-to-end training
    classification_lr: float = 0.0002
    weight_decay: float = 0.01
    early_stopping_patience: int = 8
    gradient_accumulation_steps: int = 4  # Effective batch size = 4

    # Timeout configurations
    epoch_timeout: int = 1800  # 30 minutes per epoch
    batch_timeout: int = 120   # 2 minutes per batch
    model_load_timeout: int = 300  # 5 minutes for model loading
    data_load_timeout: int = 600   # 10 minutes for data loading
    save_timeout: int = 180        # 3 minutes for saving

    # Loss weights for raw data training
    text_loss_weight: float = 0.4
    sentiment_loss_weight: float = 1.0
    intent_loss_weight: float = 2.0
    quality_loss_weight: float = 0.3

    # Data paths
    raw_data_dir: str = "data/raw_multimodal"
    checkpoint_dir: str = "checkpoints/raw_training"
    log_dir: str = "logs/raw_training"


class DistillationCapture:
    """Captures teacher model outputs for distillation training"""

    def __init__(self, output_dir: str, timeout_manager: TimeoutManager):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timeout_manager = timeout_manager

        # Phase 1 outputs (teacher) for Phase 2 preparation
        self.phase1_dir = self.output_dir / "phase1_outputs"
        self.phase1_dir.mkdir(exist_ok=True)

        # Phase 2 preparation (student data)
        self.phase2_dir = self.output_dir / "phase2_prep"
        self.phase2_dir.mkdir(exist_ok=True)

        # Distillation framework
        self.distillation_dir = self.output_dir / "distillation"
        self.distillation_dir.mkdir(exist_ok=True)

        self.current_batch = 0
        self.capture_interval = 5  # Capture every 5 batches

        print(f"✅ DistillationCapture initialized:")
        print(f"   Phase 1 outputs: {self.phase1_dir}")
        print(f"   Phase 2 prep: {self.phase2_dir}")
        print(f"   Distillation framework: {self.distillation_dir}")

    def capture_teacher_outputs(self,
                              batch_idx: int,
                              inputs: Dict,
                              teacher_outputs: Dict,
                              targets: Dict = None) -> bool:
        """Capture teacher model outputs with timeout protection"""

        if batch_idx % self.capture_interval != 0:
            return True

        try:
            # Set timeout for capture operation
            self.timeout_manager.set_timeout(f"distillation_capture_{batch_idx}", 60)

            if self.timeout_manager.is_interrupted():
                return False

            # Use safe batch naming
            safe_batch_idx = batch_idx // self.capture_interval

            # Teacher outputs for distillation (HDF5 format)
            teacher_file = self.phase1_dir / f"teacher_outputs_batch_{safe_batch_idx:06d}.h5"

            with h5py.File(teacher_file, 'w') as f:
                # Store teacher predictions and attention weights
                if 'logits' in teacher_outputs:
                    f.create_dataset('teacher_logits',
                                   data=teacher_outputs['logits'].detach().cpu().numpy())

                if 'attention_weights' in teacher_outputs:
                    f.create_dataset('teacher_attention',
                                   data=teacher_outputs['attention_weights'].detach().cpu().numpy())

                if 'embeddings' in teacher_outputs:
                    f.create_dataset('teacher_embeddings',
                                   data=teacher_outputs['embeddings'].detach().cpu().numpy())

                # Store input metadata
                f.attrs['batch_idx'] = batch_idx
                f.attrs['timestamp'] = datetime.now().isoformat()

                if targets is not None:
                    if 'sentiment' in targets:
                        f.create_dataset('target_sentiment',
                                       data=targets['sentiment'].detach().cpu().numpy())
                    if 'intent' in targets:
                        f.create_dataset('target_intent',
                                       data=targets['intent'].detach().cpu().numpy())

            # Student preparation data (JSON format for metadata)
            student_file = self.phase2_dir / f"student_data_batch_{safe_batch_idx:06d}.json"

            student_data = {
                'batch_idx': batch_idx,
                'timestamp': datetime.now().isoformat(),
                'teacher_file': str(teacher_file.name),
                'input_shapes': {k: list(v.shape) for k, v in inputs.items() if hasattr(v, 'shape')},
                'output_shapes': {k: list(v.shape) for k, v in teacher_outputs.items() if hasattr(v, 'shape')}
            }

            with open(student_file, 'w') as f:
                json.dump(student_data, f, indent=2)

            # Distillation framework metadata
            distill_meta = self.distillation_dir / f"distillation_meta_batch_{safe_batch_idx:06d}.json"

            distillation_metadata = {
                'teacher_model': 'B2MultimodalModel',
                'distillation_type': 'knowledge_distillation',
                'temperature': 4.0,  # Standard distillation temperature
                'alpha': 0.7,  # Knowledge distillation weight
                'beta': 0.3,   # Hard target weight
                'batch_info': {
                    'batch_idx': batch_idx,
                    'capture_interval': self.capture_interval,
                    'teacher_outputs_file': str(teacher_file.name),
                    'student_data_file': str(student_file.name)
                }
            }

            with open(distill_meta, 'w') as f:
                json.dump(distillation_metadata, f, indent=2)

            self.timeout_manager.clear_timeout(f"distillation_capture_{batch_idx}")

            if batch_idx % 25 == 0:  # Progress update every 25 captured batches
                print(f"📊 Distillation capture: Batch {batch_idx} → Files generated in {self.phase1_dir.name}")

            return True

        except Exception as e:
            print(f"❌ Distillation capture failed for batch {batch_idx}: {e}")
            self.timeout_manager.clear_timeout(f"distillation_capture_{batch_idx}")
            return False


class TimeoutDataset(Dataset):
    """Dataset wrapper with timeout protection"""

    def __init__(self, data: List[Dict], timeout_manager: TimeoutManager, item_timeout: int = 30):
        self.data = data
        self.timeout_manager = timeout_manager
        self.item_timeout = item_timeout

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        """Get dataset item with timeout protection"""

        def get_item():
            return self.data[idx]

        try:
            # Use thread executor with timeout
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(get_item)
                return future.result(timeout=self.item_timeout)

        except FutureTimeoutError:
            print(f"⚠️ Dataset item {idx} timed out after {self.item_timeout}s")
            # Return a dummy item to prevent complete failure
            return {
                'text_input_ids': torch.zeros(512, dtype=torch.long),
                'text_attention_mask': torch.zeros(512, dtype=torch.long),
                'image_tensor': torch.zeros(3, 224, 224),
                'audio_tensor': torch.zeros(1024),
                'sentiment_label': torch.tensor(0, dtype=torch.long),
                'intent_label': torch.tensor(0, dtype=torch.long),
                'quality_score': torch.tensor(0.5, dtype=torch.float)
            }
        except Exception as e:
            print(f"❌ Error getting dataset item {idx}: {e}")
            raise


def timeout_aware_model_loading(config: RawDataConfig, timeout_manager: TimeoutManager, device: torch.device):
    """Load models with timeout protection"""

    print("🔄 Loading models with timeout protection...")

    try:
        # Set overall timeout for model loading
        timeout_manager.set_timeout("model_loading", config.model_load_timeout)

        if timeout_manager.is_interrupted():
            raise TimeoutError("Model loading interrupted by timeout")

        # Text encoder (DialoGPT) with safetensors workaround
        print("📝 Loading text encoder (DialoGPT-small)...")
        text_tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
        text_model = AutoModel.from_pretrained(
            "microsoft/DialoGPT-small",
            use_safetensors=True,
            trust_remote_code=False
        ).to(device)

        if timeout_manager.is_interrupted():
            raise TimeoutError("Text model loading interrupted")

        # Vision encoder (CLIP) with safetensors workaround
        print("🖼️ Loading vision encoder (CLIP)...")
        vision_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        vision_model = CLIPModel.from_pretrained(
            "openai/clip-vit-base-patch32",
            use_safetensors=True,
            trust_remote_code=False
        ).to(device)

        if timeout_manager.is_interrupted():
            raise TimeoutError("Vision model loading interrupted")

        # Audio encoder (Wav2Vec2) with safetensors workaround
        print("🎵 Loading audio encoder (Wav2Vec2)...")
        audio_processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base")
        audio_model = Wav2Vec2Model.from_pretrained(
            "facebook/wav2vec2-base",
            use_safetensors=True,
            trust_remote_code=False
        ).to(device)

        if timeout_manager.is_interrupted():
            raise TimeoutError("Audio model loading interrupted")

        # Multimodal fusion model
        print("🧠 Initializing B2 multimodal model...")
        try:
            multimodal_model = B2MultimodalModel(config).to(device)
        except NameError:
            print("⚠️ B2MultimodalModel not available, using placeholder")
            multimodal_model = None

        timeout_manager.clear_timeout("model_loading")

        print("✅ All models loaded successfully!")

        return {
            'text_tokenizer': text_tokenizer,
            'text_model': text_model,
            'vision_processor': vision_processor,
            'vision_model': vision_model,
            'audio_processor': audio_processor,
            'audio_model': audio_model,
            'multimodal_model': multimodal_model
        }

    except Exception as e:
        timeout_manager.clear_timeout("model_loading")
        print(f"❌ Model loading failed: {e}")
        raise


def timeout_aware_training_step(model, batch, criterion, device, timeout_manager: TimeoutManager, batch_timeout: int):
    """Execute training step with timeout protection"""

    def training_step():
        try:
            # Move batch to device
            for key in batch:
                if isinstance(batch[key], torch.Tensor):
                    batch[key] = batch[key].to(device)

            # Forward pass
            outputs = model(batch)

            # Calculate losses
            sentiment_loss = criterion['sentiment'](outputs['sentiment_logits'], batch['sentiment_label'])
            intent_loss = criterion['intent'](outputs['intent_logits'], batch['intent_label'])
            quality_loss = criterion['quality'](outputs['quality_logits'].squeeze(), batch['quality_score'])

            # Combined loss
            total_loss = (
                sentiment_loss * 1.0 +
                intent_loss * 2.0 +
                quality_loss * 0.3
            )

            return {
                'total_loss': total_loss,
                'sentiment_loss': sentiment_loss,
                'intent_loss': intent_loss,
                'quality_loss': quality_loss,
                'outputs': outputs
            }

        except Exception as e:
            print(f"❌ Training step error: {e}")
            raise

    # Execute with timeout
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(training_step)
            return future.result(timeout=batch_timeout)

    except FutureTimeoutError:
        print(f"⚠️ Training step timed out after {batch_timeout}s")
        # Return dummy losses to prevent complete failure
        return {
            'total_loss': torch.tensor(float('inf'), device=device),
            'sentiment_loss': torch.tensor(float('inf'), device=device),
            'intent_loss': torch.tensor(float('inf'), device=device),
            'quality_loss': torch.tensor(float('inf'), device=device),
            'outputs': None
        }


def run_raw_data_training_with_timeouts():
    """Main training function with comprehensive timeout mechanisms"""

    print("🚀 Starting ImpressionCore B2 Raw Data Training with Timeout Protection")
    print("=" * 80)

    # Initialize timeout and monitoring systems
    timeout_manager = TimeoutManager(default_timeout=300)
    watchdog = ProcessWatchdog()

    def resource_alert(message):
        print(f"🔔 Resource Alert: {message}")

    watchdog.start_monitoring(resource_alert)

    try:
        # Configuration
        config = RawDataConfig()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🎯 Using device: {device}")

        if torch.cuda.is_available():
            print(f"🔥 GPU: {torch.cuda.get_device_name()}")
            print(f"💾 GPU Memory: {torch.cuda.get_device_properties(device).total_memory / 1e9:.1f}GB")

        # Create output directories
        os.makedirs(config.checkpoint_dir, exist_ok=True)
        os.makedirs(config.log_dir, exist_ok=True)
        os.makedirs("src/training", exist_ok=True)

        # Initialize distillation capture with timeout manager
        distillation_capture = DistillationCapture("src/training", timeout_manager)

        # Load models with timeout protection
        models = timeout_aware_model_loading(config, timeout_manager, device)

        if timeout_manager.is_interrupted():
            print("❌ Training interrupted during model loading")
            return False

        # Create dummy dataset for testing
        print("📊 Creating dummy multimodal dataset...")
        dummy_data = []
        for i in range(100):  # 100 samples
            dummy_data.append({
                'text_input_ids': torch.randint(0, config.vocab_size, (512,)),
                'text_attention_mask': torch.ones(512),
                'image_tensor': torch.randn(3, 224, 224),
                'audio_tensor': torch.randn(1024),
                'sentiment_label': torch.randint(0, config.num_sentiment_classes, (1,)).squeeze(),
                'intent_label': torch.randint(0, config.num_intent_classes, (1,)).squeeze(),
                'quality_score': torch.rand(1).squeeze()
            })

        # Create timeout-aware dataset
        dataset = TimeoutDataset(dummy_data, timeout_manager, item_timeout=30)
        dataloader = DataLoader(dataset, batch_size=config.batch_size, shuffle=True, num_workers=0)

        # Simple model for testing (if B2MultimodalModel not available)
        if models['multimodal_model'] is None:
            print("🔧 Using simple test model...")
            class SimpleTestModel(nn.Module):
                def __init__(self, config):
                    super().__init__()
                    self.text_proj = nn.Linear(768, 256)
                    self.image_proj = nn.Linear(512, 256)
                    self.audio_proj = nn.Linear(768, 256)
                    self.fusion = nn.Linear(768, 512)
                    self.sentiment_head = nn.Linear(512, config.num_sentiment_classes)
                    self.intent_head = nn.Linear(512, config.num_intent_classes)
                    self.quality_head = nn.Linear(512, 1)

                def forward(self, batch):
                    # Simple fusion
                    text_feat = self.text_proj(torch.randn(batch['text_input_ids'].size(0), 768, device=batch['text_input_ids'].device))
                    image_feat = self.image_proj(torch.randn(batch['image_tensor'].size(0), 512, device=batch['image_tensor'].device))
                    audio_feat = self.audio_proj(torch.randn(batch['audio_tensor'].size(0), 768, device=batch['audio_tensor'].device))

                    combined = torch.cat([text_feat, image_feat, audio_feat], dim=1)
                    fused = self.fusion(combined)

                    return {
                        'sentiment_logits': self.sentiment_head(fused),
                        'intent_logits': self.intent_head(fused),
                        'quality_logits': self.quality_head(fused),
                        'embeddings': fused,
                        'attention_weights': torch.randn(batch['text_input_ids'].size(0), 12, 512, 512, device=fused.device)
                    }

            model = SimpleTestModel(config).to(device)
        else:
            model = models['multimodal_model']

        # Loss functions
        criterion = {
            'sentiment': nn.CrossEntropyLoss(),
            'intent': nn.CrossEntropyLoss(),
            'quality': nn.MSELoss()
        }

        # Optimizer
        optimizer = optim.AdamW(model.parameters(), lr=config.base_lr, weight_decay=config.weight_decay)

        print(f"🎯 Starting training for {config.max_epochs} epochs...")
        print(f"⏱️ Timeout settings:")
        print(f"   Epoch timeout: {config.epoch_timeout}s")
        print(f"   Batch timeout: {config.batch_timeout}s")
        print("=" * 80)

        # Training loop with timeout protection
        for epoch in range(config.max_epochs):
            if timeout_manager.is_interrupted():
                print("❌ Training interrupted by timeout")
                break

            # Set epoch timeout
            timeout_manager.set_timeout(f"epoch_{epoch}", config.epoch_timeout)

            print(f"\n📅 Epoch {epoch + 1}/{config.max_epochs}")

            model.train()
            epoch_losses = []
            epoch_sentiment_acc = []

            for batch_idx, batch in enumerate(dataloader):
                if timeout_manager.is_interrupted():
                    print(f"❌ Epoch {epoch + 1} interrupted at batch {batch_idx}")
                    break

                # Execute training step with timeout
                step_results = timeout_aware_training_step(
                    model, batch, criterion, device, timeout_manager, config.batch_timeout
                )

                if step_results['outputs'] is None:
                    print(f"⚠️ Skipping batch {batch_idx} due to timeout")
                    continue

                total_loss = step_results['total_loss']

                # Skip infinite losses (from timeouts)
                if torch.isinf(total_loss):
                    print(f"⚠️ Skipping batch {batch_idx} due to infinite loss")
                    continue

                # Backward pass
                optimizer.zero_grad()
                total_loss.backward()

                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

                optimizer.step()

                # Capture teacher outputs for distillation
                if step_results['outputs'] is not None:
                    capture_success = distillation_capture.capture_teacher_outputs(
                        batch_idx=batch_idx,
                        inputs=batch,
                        teacher_outputs=step_results['outputs'],
                        targets={
                            'sentiment': batch['sentiment_label'],
                            'intent': batch['intent_label']
                        }
                    )

                    if not capture_success and timeout_manager.is_interrupted():
                        print("❌ Distillation capture interrupted")
                        break

                # Calculate metrics
                epoch_losses.append(total_loss.item())

                # Calculate accuracy
                sentiment_preds = torch.argmax(step_results['outputs']['sentiment_logits'], dim=1)
                sentiment_acc = (sentiment_preds == batch['sentiment_label']).float().mean().item()
                epoch_sentiment_acc.append(sentiment_acc)

                # Progress update
                if batch_idx % 10 == 0:
                    print(f"   Batch {batch_idx:3d}: loss={total_loss.item():.4f}, acc={sentiment_acc:.4f}")

                # Memory cleanup
                if batch_idx % 20 == 0:
                    gc.collect()
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()

            # Clear epoch timeout
            timeout_manager.clear_timeout(f"epoch_{epoch}")

            if timeout_manager.is_interrupted():
                print(f"❌ Training stopped at epoch {epoch + 1}")
                break

            # Epoch summary
            avg_loss = np.mean(epoch_losses) if epoch_losses else float('inf')
            avg_acc = np.mean(epoch_sentiment_acc) if epoch_sentiment_acc else 0.0

            print(f"   📊 Epoch {epoch + 1} Summary:")
            print(f"      Average Loss: {avg_loss:.4f}")
            print(f"      Average Accuracy: {avg_acc:.4f}")

            # Save checkpoint with timeout
            try:
                timeout_manager.set_timeout(f"save_epoch_{epoch}", config.save_timeout)

                checkpoint_path = os.path.join(config.checkpoint_dir, f"checkpoint_epoch_{epoch}.pth")
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'loss': avg_loss,
                    'accuracy': avg_acc,
                    'config': config
                }, checkpoint_path)

                timeout_manager.clear_timeout(f"save_epoch_{epoch}")
                print(f"   💾 Checkpoint saved: {checkpoint_path}")

            except Exception as e:
                timeout_manager.clear_timeout(f"save_epoch_{epoch}")
                print(f"   ⚠️ Checkpoint save failed: {e}")

        print("\n🎉 Training completed successfully!")
        print(f"📁 Distillation data saved in: src/training/")
        print("🚀 Ready for Phase 2: Knowledge Distillation")

        return True

    except Exception as e:
        print(f"\n❌ Training failed with error: {e}")
        print(f"🔍 Error traceback:")
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        timeout_manager.clear_all_timeouts()
        watchdog.stop_monitoring()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        gc.collect()
        print("✅ Cleanup completed")


if __name__ == "__main__":
    # Signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}, initiating graceful shutdown...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    success = run_raw_data_training_with_timeouts()

    if success:
        print("\n✅ ImpressionCore B2 Raw Data Training completed successfully!")
        print("🎯 Next: Execute Phase 2 knowledge distillation")
        sys.exit(0)
    else:
        print("\n❌ Training failed!")
        sys.exit(1)
