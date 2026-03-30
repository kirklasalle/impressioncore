#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Sweet Spot Training - Embeddings + Datasets (Resume Capable)
===================================================================

Purpose:
  Continue training from an existing "sweet spot" (best quality / recovery / unified) checkpoint
  using the unified tokenizer system (GPT-2 + Microsoft/Diablo integration) while fusing
  embeddings + raw datasets for concentrated intelligence under consumer hardware constraints.

Key Principles (Constitutional Framework Alignment):
  - 39M Parameter Foundation (sweet spot B3 architecture preserved)
  - Consumer Hardware Democracy (GTX 1050 Ti optimization: tiny batch + accumulation + fp16)
  - Concentrated Intelligence (high information density inputs)
  - Protection-First Design (safe checkpoint handling + resume integrity)
  - Data Condensation Methodology (embeddings + datasets unified)

Updated: August 22, 2025 (Added stable resume + auto-detect logic)
Author: Kirk LaSalle & GitHub Copilot
"""

from __future__ import annotations

import sys
import os
import argparse
import logging
from pathlib import Path
from glob import glob
from datetime import datetime
from typing import Optional, Dict, Any, List
import json
import gc
import random
from collections import deque
import threading
from queue import Queue, Empty

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from torch.cuda.amp import autocast, GradScaler

# ----------------------------------------------------------------------------------
# Environment / Encoding (Windows safe)
# ----------------------------------------------------------------------------------
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# ----------------------------------------------------------------------------------
# External project imports (assumed existing in repository)
# ----------------------------------------------------------------------------------
try:
    from b3_working_multimodal_strategy import B3Config, ImpressionCoreB3Model, UnifiedTokenizerSystem  # adjust if path differs
except Exception:
    # Fallback import strategy (if modules relocated). Adjust as needed.
    from b3_working_multimodal_strategy import B3Config, ImpressionCoreB3Model, UnifiedTokenizerSystem  # noqa

# Enhanced data & training utilities (new modules)
from src.data.pipelines.transforms import DEFAULT_TRANSFORMS
from src.data.integrity.hash_index import HashIndex
from src.data.curriculum.scheduler import DEFAULT_CURRICULUM
from src.data.metrics import BestModelTracker

# ----------------------------------------------------------------------------------
# Logging Setup
# ----------------------------------------------------------------------------------
LOG_FILE = 'unified_sweet_spot_training.log'
logger = logging.getLogger("unified_sweet_spot")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(LOG_FILE, encoding='utf-8')
    sh = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(fmt)
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)

# Central checkpoint directory for unified continuation saves
UNIFIED_CHECKPOINT_DIR = Path("F:/models/checkpoints/unified_sweet_spot")

# ----------------------------------------------------------------------------------
# Minimal Unified Dataset (placeholder logic – safe, deterministic-ish)
# ----------------------------------------------------------------------------------
class UnifiedSweetSpotDataset(Dataset):
    """Unified dataset combining (placeholder) embeddings + raw sequences.

    This minimal implementation avoids complex external I/O to ensure the
    training script is restored to a runnable state. It can be enhanced later
    to load real multimodal embeddings & tokenized corpora.
    """

    def __init__(
            self,
            embeddings_root: str,
            datasets_root: str,
            seq_len: int = 512,
            embed_dim: int = 768,
            max_samples: int = 5000,
            vocab_size: int = 50257,
            tokenizer: Optional[Any] = None,
        ) -> None:
        # Core configuration
        self.embeddings_root = Path(embeddings_root)
        self.datasets_root = Path(datasets_root)
        self.seq_len = seq_len
        self.embed_dim = embed_dim
        self.max_samples = max_samples
        self.vocab_size = vocab_size
        self.tokenizer = tokenizer

        # Embedding discovery (lightweight)
        self.image_files = sorted(glob(str(self.embeddings_root / '**' / '*image*.npy'), recursive=True))[:100]
        self.audio_files = sorted(glob(str(self.embeddings_root / '**' / '*audio*.npy'), recursive=True))[:100]
        if not self.image_files:
            self.image_files = []
        if not self.audio_files:
            self.audio_files = []

        # Deterministic synthetic fallback seeds
        random.seed(42)
        np.random.seed(42)
        torch.manual_seed(42)

        # Real text segments container (Category 1)
        self.real_segments = []  # list[Tensor]
        if self.tokenizer is not None:
            try:
                self._build_real_segments()
            except Exception as e:
                print(f"[DATA][WARN] Real text integration failed, using synthetic fallback: {e}")

    def _discover_text_files(self) -> List[Path]:
        processed = self.datasets_root / 'processed' / 'text_tokenized'
        raw_txt = self.datasets_root / 'raw' / 'text'
        files: List[Path] = []
        if processed.exists():
            files.extend(list(processed.rglob('*.txt')))
            files.extend(list(processed.rglob('*.jsonl')))
        if not files and raw_txt.exists():
            files.extend(list(raw_txt.rglob('*.txt')))
        return files[:50]

    def _build_real_segments(self):
        files = self._discover_text_files()
        if not files:
            return
        segs: List[torch.Tensor] = []
        for fp in files:
            if len(segs) >= self.max_samples:
                break
            try:
                text = fp.read_text(encoding='utf-8', errors='ignore')
                if not text.strip():
                    continue
                if hasattr(self.tokenizer, 'encode'):
                    token_ids = self.tokenizer.encode(text)
                else:
                    enc = self.tokenizer(text, add_special_tokens=False)
                    token_ids = enc['input_ids'] if isinstance(enc, dict) else enc
                for i in range(0, len(token_ids), self.seq_len):
                    if len(segs) >= self.max_samples:
                        break
                    seg = token_ids[i:i+self.seq_len]
                    if len(seg) < self.seq_len:
                        seg = seg + [0]*(self.seq_len - len(seg))
                    segs.append(torch.tensor(seg, dtype=torch.long))
            except Exception:
                continue
        if segs:
            self.real_segments = segs
            print(f"[DATA] Real segments integrated: {len(self.real_segments)}")

    def __len__(self) -> int:
        return len(self.real_segments) if self.real_segments else self.max_samples

    def _load_or_random(self, file_list: List[str], shape: tuple[int, ...]) -> torch.Tensor:
        if not file_list:
            return torch.randn(*shape, dtype=torch.float32)
        path = random.choice(file_list)
        try:
            arr = np.load(path)
            t = torch.from_numpy(arr)
            if t.ndim == 1:
                t = t.unsqueeze(0)
            # Resize/pad to shape
            if t.shape[-1] != shape[-1]:
                if t.shape[-1] > shape[-1]:
                    t = t[..., :shape[-1]]
                else:
                    pad = shape[-1] - t.shape[-1]
                    t = torch.nn.functional.pad(t, (0, pad))
            if t.shape[0] != shape[0]:
                if t.shape[0] > shape[0]:
                    t = t[:shape[0]]
                else:
                    reps = shape[0] // t.shape[0] + 1
                    t = t.repeat(reps, 1)[:shape[0]]
            return t.to(torch.float32)
        except Exception:
            return torch.randn(*shape, dtype=torch.float32)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        if self.real_segments:
            input_ids = self.real_segments[idx % len(self.real_segments)]
        else:
            input_ids = torch.randint(0, self.vocab_size, (self.seq_len,), dtype=torch.long)
        labels = input_ids.clone()
        attention_mask = torch.ones(self.seq_len, dtype=torch.long)
        image_embeddings = self._load_or_random(self.image_files, (8, self.embed_dim)).mean(dim=0)
        audio_embeddings = self._load_or_random(self.audio_files, (8, self.embed_dim)).mean(dim=0)
        return {
            'input_ids': input_ids,
            'labels': labels,
            'attention_mask': attention_mask,
            'image_embeddings': image_embeddings,
            'audio_embeddings': audio_embeddings,
        }


# ----------------------------------------------------------------------------------
# Category 2: Simple Prefetch DataLoader Wrapper (single-background-thread)
# ----------------------------------------------------------------------------------
class PrefetchLoader:
    def __init__(self, loader: DataLoader, prefetch: int = 2):
        self.loader = loader
        self.prefetch = max(1, prefetch)
        self.queue: Queue = Queue(maxsize=self.prefetch)
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._worker, daemon=True)

    def _worker(self):
        try:
            for batch in self.loader:
                if self._stop.is_set():
                    break
                self.queue.put(batch)
            # Sentinel
            self.queue.put(None)
        except Exception as e:
            # Propagate exception via sentinel tuple
            self.queue.put((e,))

    def __iter__(self):
        if not self._thread.is_alive():
            # Drain queue if reused
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                except Empty:
                    break
            self._thread = threading.Thread(target=self._worker, daemon=True)
            self._thread.start()
        while True:
            item = self.queue.get()
            if item is None:
                break
            if isinstance(item, tuple) and len(item) == 1 and isinstance(item[0], Exception):
                raise item[0]
            yield item

    def __len__(self):
        return len(self.loader)

    def shutdown(self):
        self._stop.set()
        try:
            self.queue.put(None)
        except Exception:
            pass

# ----------------------------------------------------------------------------------
# Unified Sweet Spot Trainer (resume capable)
# ----------------------------------------------------------------------------------
class UnifiedSweetSpotTrainer:
    """Trainer for unified sweet spot continuation.

    'Unified' strictly refers to the unified tokenizer system (GPT-2 + Microsoft Diablo) already
    present in the project; we do NOT alter tokenizer semantics here—only integrate resume logic.
    """

    def __init__(self, resume: Optional[str] = None, total_steps: Optional[int] = None, auto_resume: bool = False):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.resume_arg = resume
        self.auto_resume = auto_resume or (resume and resume.lower() == 'auto')
        self.user_total_steps = total_steps

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info(f"[GPU] {torch.cuda.get_device_name(0)} | VRAM {torch.cuda.get_device_properties(0).total_memory/1024**3:.1f}GB")

        # Core configs & state
        self._setup_configs()
        self.global_step = 0
        self.best_loss = float('inf')
        self.loss_history = []
        # Category hooks
        self.transforms = DEFAULT_TRANSFORMS  # (Category 5)
        self.best_tracker = BestModelTracker(UNIFIED_CHECKPOINT_DIR / 'best')
        self.best_val_tracker = BestModelTracker(UNIFIED_CHECKPOINT_DIR / 'best_val')
        self.integrity_index = None
        self.curriculum = DEFAULT_CURRICULUM
        self.validation_cache = deque(maxlen=256)


    # ----------------------------- CONFIG ---------------------------------
    def _setup_configs(self):
        self.config = B3Config(
            vocab_size=50257,
            embed_dim=768,
            num_heads=12,
            num_layers=8,
            expert_dim=2048,
            num_experts=8,
            experts_per_token=2,
            dropout=0.1,
            max_seq_length=512,
            use_gradient_checkpointing=True,
        )
        self.training_config: Dict[str, Any] = {
            'batch_size': 2,
            'learning_rate': 5e-5,
            'weight_decay': 0.01,
            'warmup_steps': 100,
            'max_steps': 10000,
            'save_every': 500,
            'log_every': 10,
            'gradient_accumulation_steps': 4,
            'max_grad_norm': 1.0,
            'fp16': True,
            'validate_every': 500,
            'validation_batches': 8,
            'prefetch': 2,
            'use_prefetch': True,
        }
        if self.user_total_steps and self.user_total_steps > 0:
            self.training_config['max_steps'] = self.user_total_steps
        logger.info("[SETUP] Configuration ready | target steps=%d", self.training_config['max_steps'])

    # --------------------------- MODEL SETUP ------------------------------
    def setup_model_and_optimizer(self):
        logger.info("[SETUP] Initializing B3 model (sweet spot configuration)...")
        self.model = ImpressionCoreB3Model(self.config).to(self.device)
        total_params = sum(p.numel() for p in self.model.parameters())
        logger.info(f"[STATS] Total Params: {total_params:,}")
        if 35e6 <= total_params <= 45e6:
            logger.info("TARGET: 39M Parameter Foundation VALIDATED")

        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=self.training_config['learning_rate'],
            weight_decay=self.training_config['weight_decay'],
            betas=(0.9, 0.95),
            eps=1e-8,
        )
        self.scaler = GradScaler() if self.training_config['fp16'] else None

        # Unified tokenizer system (unchanged semantics)
        self.tokenizer_system = UnifiedTokenizerSystem(config_path=None)

        self._resume_if_requested()

    def _candidate_checkpoint_paths(self) -> List[Path]:
        dirs = [
            UNIFIED_CHECKPOINT_DIR,
            Path("F:/models/checkpoints/sweet_spot_recovery"),
            Path("F:/models/checkpoints/best_quality"),
        ]
        files: List[Path] = []
        for d in dirs:
            if d.exists():
                files.extend([Path(p) for p in glob(str(d / '*.pth'))])
        return files

    def _auto_latest_checkpoint(self) -> Optional[Path]:
        files = self._candidate_checkpoint_paths()
        if not files:
            return None
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return files[0]

    def _select_resume_checkpoint(self) -> Optional[Path]:
        """Determine which checkpoint (if any) should be used for resume."""
        if self.resume_arg and self.resume_arg.lower() != 'auto':
            p = Path(self.resume_arg)
            if p.exists():
                return p
            logger.warning(f"[RESUME] Specified checkpoint not found: {p}")
            return None
        if self.auto_resume:
            cp = self._auto_latest_checkpoint()
            if cp:
                logger.info(f"[RESUME] Auto-detected latest checkpoint: {cp}")
            return cp
        # default fallback
        default_cp = Path("F:/models/checkpoints/best_quality/b3_best_quality_model_20250802_124801.pth")
        if default_cp.exists():
            logger.info(f"[LOAD] Default checkpoint: {default_cp}")
            return default_cp
        return None

    def _load_checkpoint(self, chosen: Path):
        """Load model/optimizer/scaler + progress from a checkpoint path."""
        ckpt = torch.load(chosen, map_location=self.device, weights_only=False)
        model_state = None
        if isinstance(ckpt, dict):
            for k in ['model_state_dict', 'state_dict', 'model', 'weights']:
                if k in ckpt:
                    model_state = ckpt[k]
                    break
            if model_state is None and ckpt and all('.' in key for key in list(ckpt.keys())[:10]):
                model_state = ckpt
        else:
            model_state = ckpt
        if model_state is not None:
            self.model.load_state_dict(model_state, strict=False)
            logger.info(f"[RESUME] Loaded weights from {chosen}")
        if isinstance(ckpt, dict):
            self._restore_optimizer_scaler(ckpt)
            self._restore_training_progress(ckpt)

    def _restore_optimizer_scaler(self, ckpt: Dict[str, Any]):
        if 'optimizer_state_dict' in ckpt:
            try:
                self.optimizer.load_state_dict(ckpt['optimizer_state_dict'])
                logger.info("[RESUME] Optimizer restored")
            except Exception as e:
                logger.warning(f"[RESUME] Optimizer restore failed: {e}")
        if 'scaler_state_dict' in ckpt and self.scaler:
            try:
                self.scaler.load_state_dict(ckpt['scaler_state_dict'])
                logger.info("[RESUME] GradScaler restored")
            except Exception as e:
                logger.warning(f"[RESUME] Scaler restore failed: {e}")

    def _restore_training_progress(self, ckpt: Dict[str, Any]):
        self.global_step = int(ckpt.get('global_step', self.global_step))
        self.best_loss = float(ckpt.get('best_loss', self.best_loss))
        if isinstance(ckpt.get('loss_history'), list):
            self.loss_history = ckpt['loss_history']
        if self.global_step >= self.training_config['max_steps']:
            self.training_config['max_steps'] = self.global_step + 1000
        logger.info(
            f"[RESUME] Resuming at step {self.global_step} (target {self.training_config['max_steps']}) best_loss={self.best_loss:.6f}"
        )

    def _resume_if_requested(self):
        chosen = self._select_resume_checkpoint()
        if not chosen or not chosen.exists():
            logger.info("[RESUME] No checkpoint loaded (fresh start)")
            return
        try:
            self._load_checkpoint(chosen)
        except Exception as e:
            logger.warning(f"[RESUME] Failed to load checkpoint {chosen}: {e}")

    # ---------------------------- DATA LOADER -----------------------------
    def setup_data_loader(self):
        logger.info("[DATA] Preparing unified dataset ...")
        self.dataset = UnifiedSweetSpotDataset(
            embeddings_root="F:/data/embeddings",
            datasets_root="F:/data/datasets",
            seq_len=512,
            embed_dim=self.config.embed_dim,
            max_samples=5000,
            vocab_size=self.config.vocab_size,
            tokenizer=self.tokenizer_system,
        )
        def collate_fn(batch: List[Dict[str, torch.Tensor]]):
            return {
                'input_ids': torch.stack([b['input_ids'] for b in batch], dim=0),
                'labels': torch.stack([b['labels'] for b in batch], dim=0),
                'attention_mask': torch.stack([b['attention_mask'] for b in batch], dim=0),
                'image_embeddings': torch.stack([b['image_embeddings'] for b in batch], dim=0),
                'audio_embeddings': torch.stack([b['audio_embeddings'] for b in batch], dim=0),
            }
        self.data_loader = DataLoader(
            self.dataset,
            batch_size=self.training_config['batch_size'],
            shuffle=True,
            num_workers=0,
            pin_memory=True,
            drop_last=True,
            collate_fn=collate_fn,
        )
        # Validation split (Category 7)
        if len(self.dataset) > 20:
            val_indices = list(range(0, min(200, len(self.dataset)//20)))  # ~5% or capped
            from torch.utils.data import Subset
            val_subset = Subset(self.dataset, val_indices)
            self.val_loader = DataLoader(
                val_subset,
                batch_size=self.training_config['batch_size'],
                shuffle=False,
                num_workers=0,
                pin_memory=True,
                drop_last=False,
                collate_fn=collate_fn,
            )
        else:
            self.val_loader = None

        # Optional prefetch wrapper (Category 2)
        if self.training_config.get('use_prefetch'):
            try:
                self.data_loader = PrefetchLoader(self.data_loader, prefetch=self.training_config.get('prefetch', 2))
                if self.val_loader is not None:
                    self.val_loader = PrefetchLoader(self.val_loader, prefetch=1)
                logger.info(f"[PERF] Prefetch enabled (train={self.training_config.get('prefetch',2)})")
            except Exception as e:
                logger.warning(f"[PERF] Prefetch disabled: {e}")
        logger.info(f"[DATA] Size: {len(self.dataset)} | Batches/Epoch: {len(self.data_loader)}")
        # Build / verify integrity hash index (Category 3)
        try:
            self.integrity_index = HashIndex(Path('F:/data/embeddings'), Path('F:/data/system/hashes/embedding_hashes.json'))
            updated, total = self.integrity_index.build_or_update(limit=50)
            logger.info(f"[INTEGRITY] Hash index updated: {updated} / {total} files (sampled)")
        except Exception as e:
            logger.warning(f"[INTEGRITY] Hash indexing skipped: {e}")

    # ----------------------------- TRAIN STEP -----------------------------
    def train_step(self, batch: Dict[str, torch.Tensor]) -> float:
        # Apply curriculum adjustments (Category 4) (placeholder call)
        _ = self.curriculum.current(self.global_step)
        # (Optional future: adjust seq_len dynamically)
        batch = {k: v.to(self.device) if torch.is_tensor(v) else v for k, v in batch.items()}
        # Apply transforms (Category 5)
        for t in self.transforms:
            try:
                batch = t(batch)
            except Exception:
                continue
        if self.training_config['fp16']:
            with autocast():
                out = self.model(
                    input_ids=batch['input_ids'],
                    image_features=batch['image_embeddings'],
                    audio_features=batch['audio_embeddings'],
                    mask=batch['attention_mask'],
                )
                logits = out['logits']
                loss = nn.CrossEntropyLoss()(logits.view(-1, self.config.vocab_size), batch['labels'].view(-1))
        else:
            out = self.model(
                input_ids=batch['input_ids'],
                image_features=batch['image_embeddings'],
                audio_features=batch['audio_embeddings'],
                mask=batch['attention_mask'],
            )
            logits = out['logits']
            loss = nn.CrossEntropyLoss()(logits.view(-1, self.config.vocab_size), batch['labels'].view(-1))
        if self.training_config['fp16']:
            self.scaler.scale(loss).backward()
        else:
            loss.backward()
        return float(loss.item())

    # --------------------------- TRAIN LOOP -------------------------------
    def train(self):
        logger.info("[START] Unified Sweet Spot Training (resume capable)")
        self.setup_model_and_optimizer()
        self.setup_data_loader()
        accumulation = 0.0
        steps_accum = 0
        save_dir = UNIFIED_CHECKPOINT_DIR
        save_dir.mkdir(parents=True, exist_ok=True)
        try:
            while self.global_step < self.training_config['max_steps']:
                for batch in self.data_loader:
                    if self.global_step >= self.training_config['max_steps']:
                        break
                    loss_val = self.train_step(batch)
                    accumulation, steps_accum = self._after_step(loss_val, accumulation, steps_accum)
        except KeyboardInterrupt:
            logger.info("[INTERRUPT] Training interrupted by user")
        finally:
            self._finalize_training(save_dir)

    def _after_step(self, loss_val: float, accumulation: float, steps_accum: int):
        accumulation += loss_val
        steps_accum += 1
        self._maybe_optimize()
    accumulation, steps_accum = self._maybe_log(accumulation, steps_accum)
    self._maybe_validate()
    self._maybe_save()
    self.global_step += 1
    return accumulation, steps_accum

    def _maybe_optimize(self):
        if (self.global_step + 1) % self.training_config['gradient_accumulation_steps'] != 0:
            return
        if self.training_config['fp16']:
            self.scaler.unscale_(self.optimizer)
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.training_config['max_grad_norm'])
            self.scaler.step(self.optimizer)
            self.scaler.update()
        else:
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.training_config['max_grad_norm'])
            self.optimizer.step()
        self.optimizer.zero_grad()

    def _maybe_log(self, accumulation: float, steps_accum: int):
        if self.global_step % self.training_config['log_every'] != 0:
            return accumulation, steps_accum
        avg_loss = accumulation / max(1, steps_accum)
        if torch.cuda.is_available():
            used = torch.cuda.memory_allocated()/1024**2
            resv = torch.cuda.memory_reserved()/1024**2
        else:
            used = resv = 0
        logger.info(f"[PROGRESS] Step {self.global_step:5d} | Loss {avg_loss:.6f} | VRAM {used:.0f}MB/{resv:.0f}MB")
        if avg_loss < self.best_loss:
            self.best_loss = avg_loss
            logger.info(f"[BEST] New best loss {self.best_loss:.6f}")
            # Save best-loss checkpoint (user requirement)
            try:
                self.best_tracker.update(avg_loss, self.global_step, self.model, self.optimizer, self.scaler, {
                    'loss_history_len': len(self.loss_history),
                })
            except Exception as e:
                logger.warning(f"[BEST] Tracker save failed: {e}")
        self.loss_history.append(avg_loss)
        return 0.0, 0

    # --------------------------- VALIDATION ------------------------------
    def _maybe_validate(self):
        cfg = self.training_config
        if not self.val_loader:
            return
        if self.global_step == 0 or self.global_step % cfg['validate_every'] != 0:
            return
        self.model.eval()
        losses = []
        with torch.no_grad():
            for i, batch in enumerate(self.val_loader):
                if i >= cfg['validation_batches']:
                    break
                batch = {k: v.to(self.device) if torch.is_tensor(v) else v for k, v in batch.items()}
                out = self.model(
                    input_ids=batch['input_ids'],
                    image_features=batch['image_embeddings'],
                    audio_features=batch['audio_embeddings'],
                    mask=batch['attention_mask'],
                )
                logits = out['logits']
                loss = nn.CrossEntropyLoss()(logits.view(-1, self.config.vocab_size), batch['labels'].view(-1))
                losses.append(float(loss.item()))
        if losses:
            val_loss = sum(losses)/len(losses)
            logger.info(f"[VAL] Step {self.global_step} | ValLoss {val_loss:.6f} | Batches {len(losses)}")
            # Track best validation
            if val_loss < self.best_val_tracker.best_loss:
                try:
                    self.best_val_tracker.update(val_loss, self.global_step, self.model, self.optimizer, self.scaler, {
                        'context': 'validation',
                        'batches': len(losses),
                    })
                    logger.info(f"[VAL][BEST] Improved validation loss {val_loss:.6f}")
                except Exception as e:
                    logger.warning(f"[VAL][BEST] Save failed: {e}")
        self.model.train()

    def _maybe_save(self):
        if self.global_step % self.training_config['save_every'] != 0 or self.global_step == 0:
            return
        save_dir = UNIFIED_CHECKPOINT_DIR
        cp = save_dir / f"unified_step_{self.global_step}.pth"
        self.save_checkpoint(cp)
        logger.info(f"[SAVE] {cp}")

    def _finalize_training(self, save_dir: Path):
        # Save a final checkpoint at the end (or after interruption)
        final_cp = save_dir / f"unified_final_step_{self.global_step}.pth"
        self.save_checkpoint(final_cp)
        logger.info(f"[FINAL] Final checkpoint saved: {final_cp} | Total steps: {self.global_step}")

    # ----------------------------- CHECKPOINT -----------------------------
    def save_checkpoint(self, path: Path):
        ckpt = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'config': self.config,
            'global_step': self.global_step,
            'best_loss': self.best_loss,
            'loss_history': self.loss_history,
            'training_config': self.training_config,
            'timestamp': datetime.now().isoformat(),
            'total_params': sum(p.numel() for p in self.model.parameters()),
        }
        if self.scaler:
            ckpt['scaler_state_dict'] = self.scaler.state_dict()
        torch.save(ckpt, path)


# ----------------------------------------------------------------------------------
# Entry Point
# ----------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Unified Sweet Spot Training (resume capable)")
    parser.add_argument('--resume', type=str, default=None, help="Path to checkpoint to resume from or 'auto'")
    parser.add_argument('--total_steps', type=int, default=None, help="Override total max steps for this run")
    parser.add_argument('--auto-resume', action='store_true', help="Auto-detect latest checkpoint (alias of --resume auto)")
    args = parser.parse_args()

    print("UNIFIED SWEET SPOT TRAINING")
    print("Constitutional Framework Active: 39M Parameter Foundation | Consumer Hardware Democracy | Resume Support")

    try:
        # Normalize resume argument
        resume_arg = args.resume
        if not resume_arg and args.auto_resume:
            resume_arg = 'auto'
        auto_flag = args.auto_resume or (resume_arg is not None and resume_arg.lower() == 'auto')
        trainer = UnifiedSweetSpotTrainer(resume=resume_arg, total_steps=args.total_steps, auto_resume=auto_flag)
        trainer.train()
        print("Training complete. Final checkpoint saved in unified_sweet_spot directory.")
    except Exception as e:
        logger.error(f"Training failed: {e}")
        print(f"ERROR: Training failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
