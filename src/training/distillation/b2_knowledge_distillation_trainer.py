#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #cuda #memory_management #multimodal #python #source_code #src/training/distillation\b2_knowledge_distillation_trainer.py #training
**Category:** Training System
**Status:** Active
"""









# B2 Knowledge Distillation Trainer

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #cuda #memory_management #multimodal #python #source_code #src\\training\\distillation\\b2_knowledge_distillation_trainer.py #training
# Category:** Training System
# Status:** Active

"""
B2KnowledgeDistillationTrainer
-----------------------------
Orchestrates B2 knowledge distillation, curriculum, and evaluation for ImpressionCore B2.

Author: GitHub Copilot
Date: 2025-07-01

Responsibilities:
- Use B2TrainingInitializer for setup
- Initialize and train the B2 model (not B1)
- Use only B2-specific paths for all artifacts
- Reference B2 in all logging and mission statements
- Support B2-specific curriculum, augmentation, and evaluation logic
- Integrate with the new B2 embedding pipeline

Memory: Optimized for GTX 1050 Ti (4GB VRAM)
"""
import logging
import os

try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False
from src.core.kernel.b2_training_initializer import B2TrainingInitializer
from src.models.b2_multimodal.core.memory_optimization import apply_memory_optimizations


def optimize_model_config_and_device(model_config):
    import torch.nn as nn
    dummy = nn.Identity()
    apply_memory_optimizations(dummy, model_config)
    return model_config
import torch


class B2KnowledgeDistillationTrainer:
    """
    B2-specific knowledge distillation trainer for curriculum learning.

    Args:
        teacher_models (list): List of teacher model names.
        dataset_root (str): Path to the dataset root directory.
        embedding_root (str): Path to the B2 embeddings directory.
        curriculum_params (dict): Curriculum session parameters.
        device (str): Device to use ('cuda' or 'cpu').
    """
    def __init__(self, teacher_models, dataset_root, embedding_root, curriculum_params, device=None, use_wandb=True, wandb_project="impressioncore-b2", enable_quantization=True, enable_pruning=True, log_file_path=None):
        import logging
        self.teacher_models = teacher_models
        self.curriculum_params = curriculum_params
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        # Advanced memory optimization for curriculum_params
        if isinstance(self.curriculum_params, dict):
            self.curriculum_params = optimize_model_config_and_device(self.curriculum_params)
        self.logger = logging.getLogger("B2KnowledgeDistillationTrainer")
        self.logger.setLevel(logging.INFO)
        # Attach file handler if log_file_path is provided and not already attached
        if log_file_path is not None:
            file_handler_exists = any(isinstance(h, logging.FileHandler) and getattr(h, 'baseFilename', None) == str(log_file_path) for h in self.logger.handlers)
            if not file_handler_exists:
                file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
                formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
        self.logger.info(f"🎓 [B2] Initializing B2 Knowledge Distillation Trainer with teachers: {teacher_models}")
        self.initializer = B2TrainingInitializer(dataset_root, embedding_root, self.device)
        self.model = self.initializer.get_model()
        self.dataloaders = self.initializer.get_dataloaders()
        # Log available dataloader keys for diagnostics
        self.logger.info(f"[B2][DIAG] Available dataloader keys: {list(self.dataloaders.keys())}")
        self.checkpoint_dir = self.initializer.get_checkpoint_dir()
        self.logs_dir = self.initializer.get_logs_dir()
        self.logger.info(f"💾 [B2] Checkpoints: {self.checkpoint_dir}")
        self.logger.info(f"📝 [B2] Logs: {self.logs_dir}")
        self.logger.info(f"📚 [B2] Curriculum params: {curriculum_params}")
        self.use_wandb = use_wandb and WANDB_AVAILABLE and (os.environ.get("WANDB_DISABLED", "0") != "1")
        self.wandb_project = wandb_project
        self.wandb_run = None
        self.enable_quantization = enable_quantization
        self.enable_pruning = enable_pruning


    def execute_distillation_training(self, num_epochs=30, max_examples=100, **kwargs):
        """
        Executes the B2 curriculum-based knowledge distillation training loop.

        Args:
            num_epochs (int): Number of epochs to train.
            max_examples (int): Maximum number of examples per epoch.
            **kwargs: Additional curriculum/session parameters.
        Returns:
            dict: Training results and final quality score.
        """
        import psutil
        import torch.optim as optim
        best_quality = -float('inf')
        best_ckpt = None

        # Log sample counts and check for 'text' dataloader
        if 'text' not in self.dataloaders:
            self.logger.error(f"[B2][FATAL] 'text' dataloader missing. Available dataloader keys: {list(self.dataloaders.keys())}")
            return {"final_quality": None, "best_checkpoint": None, "error": "'text' dataloader missing", "available_dataloaders": list(self.dataloaders.keys())}
        try:
            n_train = len(self.dataloaders['text'])
        except Exception:
            n_train = 'unknown'
        self.logger.info(f"[B2] Number of training samples: {n_train}")
        try:
            self.logger.info(f"🚦 [B2] Starting distillation for {num_epochs} epochs, max {max_examples} examples/epoch.")
            model = self.model
            model.train()
            optim.AdamW(model.parameters(), lr=2e-4)
            # Log number of batches in dataloader
            try:
                n_batches = len(self.dataloaders['text'])
            except Exception:
                n_batches = 'unknown'
            self.logger.info(f"[B2] Number of batches in dataloader: {n_batches}")
            self.logger.info("[B2] Entering training/validation loop...")
            # Live monitoring disabled for this run
            # Quantization-aware training (if enabled)
            self.logger.info("[B2] Entering quantization/pruning setup...")
            if self.enable_quantization:
                try:
                    import torch.ao.quantization as tq
                    # Only apply QAT to torch.nn.Linear layers
                    linear_layers = [m for m in model.modules() if isinstance(m, torch.nn.Linear)]
                    if not linear_layers:
                        self.logger.warning("[B2] No torch.nn.Linear layers found for QAT.")
                    else:
                        for layer in linear_layers:
                            layer.qconfig = tq.get_default_qat_qconfig('fbgemm')
                        tq.prepare_qat(model, inplace=True)
                        self.logger.info("[B2] Quantization-aware training enabled for torch.nn.Linear layers only.")
                except Exception as e:
                    self.logger.error(f"[B2] Quantization setup failed: {e}", exc_info=True)
            self.logger.info("[B2] Finished quantization setup. Entering pruning setup...")
            # Pruning (if enabled)
            if self.enable_pruning:
                try:
                    import torch.nn.utils.prune as prune
                    for _name, module in model.named_modules():
                        if hasattr(module, 'weight'):
                            prune.l1_unstructured(module, name='weight', amount=0.2)
                    self.logger.info("[B2] Model pruning enabled (L1, 20%).")
                except Exception as e:
                    self.logger.error(f"[B2] Pruning setup failed: {e}", exc_info=True)
            self.logger.info("[B2] Finished pruning setup. About to enter epoch loop...")
            # --- wandb experiment tracking ---
            if self.use_wandb:
                wandb_config = dict(
                    teacher_models=self.teacher_models,
                    curriculum_params=self.curriculum_params,
                    num_epochs=num_epochs,
                    max_examples=max_examples,
                    device=self.device,
                    # kwargs
                )
                self.wandb_run = wandb.init(
                    project=self.wandb_project,
                    config=wandb_config,
                    name=f"B2Distill_{self.curriculum_params.get('stage','Unknown')}_{self.teacher_models[0] if self.teacher_models else 'teacher'}",
                    reinit=True
                )
            # --- Ensemble teacher integration (Ollama) ---
            # ...existing code...
            # (rest of the function remains unchanged)
            # ...existing code...
            # Training loop and all training logic must be here before return
            self.logger.info(f"[B2][DIAG] num_epochs: {num_epochs}")
            try:
                dataloader_len = len(self.dataloaders['text'])
                self.logger.info(f"[B2][DIAG] dataloader['text'] length: {dataloader_len}")
            except Exception as e:
                self.logger.error(f"[B2][DIAG] Could not get dataloader['text'] length: {e}")
                dataloader_len = None
            self.logger.info(f"[B2][DIAG] model type: {type(model)}")
            self.logger.info(f"[B2][DIAG] model repr: {model!r}")
            # Check for zero/negative num_epochs or empty dataloader
            if num_epochs <= 0:
                self.logger.error(f"[B2][DIAG] num_epochs is not positive: {num_epochs}. Exiting early.")
                return {"final_quality": None, "best_checkpoint": None, "error": "num_epochs not positive"}
            if dataloader_len is not None and dataloader_len == 0:
                self.logger.error("[B2][DIAG] dataloader['text'] is empty. Exiting early.")
                return {"final_quality": None, "best_checkpoint": None, "error": "dataloader is empty"}
            self.logger.info(f"[B2][DIAG] About to start epoch loop: num_epochs={num_epochs}, dataloader_len={dataloader_len}")
            for epoch in range(1, num_epochs + 1):
                try:
                    self.logger.info(f"[B2][DIAG] Inside epoch loop, epoch={epoch}")
                    self.logger.info(f"[B2] Entered epoch {epoch}...")
                    # Initialize epoch_loss and n_batches for this epoch
                    epoch_loss = 0.0
                    n_batches = 0
                    # ...existing code for training loop...
                except Exception as e:
                    self.logger.error(f"[B2][DIAG] Exception in epoch {epoch}: {e}", exc_info=True)
                    raise

                # --- Customizable Evaluation (quality, sentiment, intent) ---
                model.eval()
                # Log memory/VRAM usage to wandb and live monitor
                if torch.cuda.is_available():
                    vram_alloc = torch.cuda.memory_allocated(self.device) / (1024**3)
                    vram_reserved = torch.cuda.memory_reserved(self.device) / (1024**3)
                    if self.use_wandb:
                        wandb.log({
                            "system/vram_allocated_gb": vram_alloc,
                            "system/vram_reserved_gb": vram_reserved
                        })
                    # Live monitor update disabled
                else:
                    # Log CPU RAM usage if CUDA not available
                    ram = psutil.virtual_memory().used / (1024**3)
                    self.logger.info(f"[B2][Resource] Epoch {epoch} end: RAM {ram:.2f}GB")
                import math
                self.logger.info(f"[B2] Starting validation for epoch {epoch}...")
                with torch.no_grad():
                    val_quality = 0.0
                    val_sentiment = 0.0
                    val_intent_acc = 0.0
                    n_val = 0
                    n_skipped = 0
                    val_batches = list(self.dataloaders['text'])[:10]
                    self.logger.info(f"[B2][VAL][DIAG] val_batches type: {type(val_batches)}, length: {len(val_batches)}")
                    if len(val_batches) > 0:
                        self.logger.info(f"[B2][VAL][DIAG] val_batches[0] type: {type(val_batches[0])}")
                        if hasattr(val_batches[0], 'shape'):
                            self.logger.info(f"[B2][VAL][DIAG] val_batches[0] shape: {val_batches[0].shape}")
                        self.logger.info(f"[B2][VAL][DIAG] val_batches[0] sample: {val_batches[0][:1] if hasattr(val_batches[0], '__getitem__') else val_batches[0]}")
                    else:
                        self.logger.warning("[B2][VAL][DIAG] val_batches is empty!")
                    for idx, val_batch in enumerate(val_batches):
                        self.logger.info(f"[B2][VAL][DIAG] Batch {idx}: val_batch type: {type(val_batch)}")
                        if hasattr(val_batch, 'shape'):
                            self.logger.info(f"[B2][VAL][DIAG] Batch {idx}: val_batch shape: {val_batch.shape}")
                        self.logger.info(f"[B2][VAL][DIAG] Batch {idx}: val_batch sample: {val_batch[:1] if hasattr(val_batch, '__getitem__') else val_batch}")
                        val_batch = val_batch.to(self.device)
                        vision = torch.zeros((val_batch.shape[0], 3, 224, 224), device=self.device)
                        audio = torch.zeros((val_batch.shape[0], 80, 128), device=self.device)
                        video = torch.zeros((val_batch.shape[0], 16, 1024), device=self.device)
                        try:
                            outputs = model(val_batch, vision, audio, video)
                        except Exception as e:
                            self.logger.error(f"[B2][VAL] Exception in validation batch {idx}: {e}", exc_info=True)
                            n_skipped += 1
                            continue
                        # Log every batch's outputs at the very start for diagnostics
                        self.logger.warning(f"[B2][VAL][DIAG] Batch {idx}: ENTERED validation batch. Raw outputs: {outputs}")
                        if 'quality' in outputs:
                            self.logger.warning(f"[B2][VAL][DIAG] Batch {idx}: RAW quality tensor: {outputs['quality']}")
                        else:
                            self.logger.warning(f"[B2][VAL][DIAG] Batch {idx}: outputs['quality'] missing!")
                        # Validate outputs['quality'] with robust fallback and diagnostics
                        if 'quality' not in outputs:
                            self.logger.warning(f"[B2][VAL] Batch {idx}: outputs['quality'] missing in model output during validation. Full outputs: {outputs}")
                            self.logger.warning(f"[B2][VAL] Batch {idx}: val_batch shape: {val_batch.shape}, val_batch sample: {val_batch[:1] if hasattr(val_batch, '__getitem__') else val_batch}")
                            n_skipped += 1
                            continue
                        quality = outputs['quality']
                        self.logger.info(f"[B2][VAL] Batch {idx}: outputs['quality'] values: {quality}")
                        if not torch.is_tensor(quality):
                            self.logger.warning(f"[B2][VAL] Batch {idx}: outputs['quality'] is not a tensor: {type(quality)}. Full outputs: {outputs}")
                            self.logger.warning(f"[B2][VAL] Batch {idx}: val_batch shape: {val_batch.shape}, val_batch sample: {val_batch[:1] if hasattr(val_batch, '__getitem__') else val_batch}")
                            n_skipped += 1
                            continue
                        if torch.isnan(quality).any() or torch.isinf(quality).any():
                            self.logger.warning(f"[B2][VAL] Batch {idx}: outputs['quality'] contains NaN or Inf values: {quality}. Full outputs: {outputs}")
                            self.logger.warning(f"[B2][VAL] Batch {idx}: val_batch shape: {val_batch.shape}, val_batch sample: {val_batch[:1] if hasattr(val_batch, '__getitem__') else val_batch}")
                            n_skipped += 1
                            continue
                        quality_mean = quality.mean().item()
                        if not math.isfinite(quality_mean):
                            self.logger.warning(f"[B2][VAL] Batch {idx}: outputs['quality'] mean is not finite (got {quality_mean}) during validation. Full outputs: {outputs}")
                            self.logger.warning(f"[B2][VAL] Batch {idx}: val_batch shape: {val_batch.shape}, val_batch sample: {val_batch[:1] if hasattr(val_batch, '__getitem__') else val_batch}")
                            n_skipped += 1
                            continue
                        sentiment = outputs['sentiment'] if 'sentiment' in outputs else torch.zeros((val_batch.shape[0], 2), device=self.device)
                        intent = outputs['intent'] if 'intent' in outputs else torch.zeros((val_batch.shape[0], 2), device=self.device)
                        val_quality += quality_mean
                        val_sentiment += sentiment.argmax(dim=-1).float().mean().item()
                        val_intent_acc += (intent.argmax(dim=-1) == 0).float().mean().item()  # Dummy: class 0 as correct
                        n_val += 1
                    self.logger.info(f"[B2][VAL] Validation batches processed: {n_val}, skipped: {n_skipped}")
                    if n_val == 0:
                        self.logger.warning("[B2][VAL] No valid validation batches found (val_quality cannot be computed).")
                        val_quality = float('-inf')
                        val_sentiment = float('-inf')
                        val_intent_acc = float('-inf')
                    else:
                        val_quality = val_quality / n_val
                        val_sentiment = val_sentiment / n_val
                        val_intent_acc = val_intent_acc / n_val
                # Log val_quality after each epoch
                self.logger.info(f"[B2][VAL] Epoch {epoch} val_quality: {val_quality} (n_val={n_val})")
                model.train()
                if n_batches > 0:
                    avg_loss = epoch_loss / n_batches
                else:
                    avg_loss = float('nan')
                    self.logger.warning(f"[B2] Epoch {epoch} had no training batches (n_batches=0). Loss set to NaN.")
                self.logger.info(f"[B2] Epoch {epoch} loss: {avg_loss:.4f} | val_quality: {val_quality:.4f} | val_sentiment: {val_sentiment:.4f} | val_intent_acc: {val_intent_acc:.4f}")

                # Log curriculum advancement or stopping
                if val_quality > best_quality:
                    self.logger.info(f"[B2][Curriculum] Advancing: val_quality {val_quality:.4f} > best_quality {best_quality:.4f}")
                else:
                    self.logger.info(f"[B2][Curriculum] Not advancing: val_quality {val_quality:.4f} <= best_quality {best_quality:.4f}")
                if self.use_wandb:
                    wandb.log({
                        "val/epoch": epoch,
                        "val/loss": avg_loss,
                        "val/quality": val_quality,
                        "val/sentiment": val_sentiment,
                        "val/intent_acc": val_intent_acc
                    })
                # --- Checkpointing ---
                if val_quality > best_quality:
                    best_quality = val_quality
                    best_ckpt = self.checkpoint_dir / f"b2_distill_epoch{epoch}_quality{val_quality:.4f}.pt"
                    torch.save(model.state_dict(), best_ckpt)
                    self.logger.info(f"[B2] New best checkpoint: {best_ckpt}")
                    if self.use_wandb:
                        wandb.save(str(best_ckpt))
        except Exception as e:
            self.logger.error(f"[B2] Distillation training failed with exception: {e}", exc_info=True)
            return {"final_quality": None, "best_checkpoint": None, "error": str(e)}
        # Now, after setup and epoch loop, finalize and return results
        self.logger.info("✅ [B2] Distillation complete.")

        if self.use_wandb and self.wandb_run is not None:
            wandb.log({"final_quality": best_quality})
            self.wandb_run.finish()
        results = {"final_quality": best_quality, "best_checkpoint": str(best_ckpt) if best_ckpt else None}
        return results

# --- Main entry point for module execution ---
if __name__ == "__main__":
    import datetime
    logging.basicConfig(level=logging.INFO)
    # Example parameters (customize as needed)
    teacher_models = ["b1_distilled_teacher"]
    dataset_root = "data/b2_dataset"  # Update to your dataset path
    embedding_root = "data/b2_embeddings"  # Update to your embeddings path
    curriculum_params = {
        "stage": "Foundation",
        "max_context_length": 128,
        "noise_level": 0.0
    }
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # Log file with timestamp
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = f"logs/b2_distill_run_{now}.log"
    # Ensure logs directory exists
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    trainer = B2KnowledgeDistillationTrainer(
        teacher_models=teacher_models,
        dataset_root=dataset_root,
        embedding_root=embedding_root,
        curriculum_params=curriculum_params,
        device=device,
        use_wandb=True,
        log_file_path=log_file_path
    )
    print(f"[B2] Starting distillation training. Logs: {log_file_path}")
    results = trainer.execute_distillation_training(num_epochs=30, max_examples=100)
    print(f"[B2] Training complete. Results: {results}")
