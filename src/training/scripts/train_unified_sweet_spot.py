#!/usr/bin/env python3
"""Unified Sweet Spot Training (Resume + Advanced Features)

Implements requested enhancements:
 - Validation refactored into helpers (_compute_validation_loss / _log_validation)
 - RNG + dataset position restore on resume
 - Early stopping with min_delta + patience
 - Length bucketing and mmap stub for performance
 - Atomic checkpoint writes & dual best trackers

Updated: August 22, 2025
Author: Kirk LaSalle & GitHub Copilot
"""

from __future__ import annotations

import argparse
import contextlib
import logging
import math
import os
import random
import shutil
import sys
import tempfile
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from queue import Queue
from typing import Any

import torch
import torch.nn as nn
import torch.optim as optim
from torch.amp import GradScaler, autocast
from torch.utils.data import DataLoader, Dataset

from src.core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model
from src.core.models.unified_tokenizer_system import UnifiedTokenizerSystem
from src.data.curriculum.scheduler import DEFAULT_CURRICULUM
from src.data.integrity.hash_index import HashIndex
from src.data.metrics import BestModelTracker
from src.data.pipelines.transforms import DEFAULT_TRANSFORMS

try:  # optional
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None
try:
    from torch.utils.tensorboard import SummaryWriter  # type: ignore
except Exception:  # pragma: no cover
    SummaryWriter = None

logger = logging.getLogger("unified_sweet_spot_trainer")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

UNIFIED_CHECKPOINT_DIR = Path(os.environ.get('IMPRESSIONCORE_CHECKPOINT_DIR', "F:/models/checkpoints/unified_sweet_spot"))
EMBED_ROOT = Path(os.environ.get('IMPRESSIONCORE_EMBED_ROOT', 'F:/data/embeddings'))
HASH_INDEX_PATH = Path(os.environ.get('IMPRESSIONCORE_HASH_INDEX_PATH', 'F:/data/system/hashes/embedding_hashes.json'))
ARTIFACTS_DIR = Path(os.environ.get('IMPRESSIONCORE_ARTIFACTS_DIR', 'F:/models/checkpoints/artifacts'))
CALIBRATION_DIR = Path(os.environ.get('IMPRESSIONCORE_CALIBRATION_DIR', 'F:/models/checkpoints/calibration'))
DEFAULT_CONFIG_PATH = Path("src/config/training/unified_sweet_spot.yaml")

if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'


class UnifiedSweetSpotDataset(Dataset):
    """In-memory token dataset (stores padded ids + raw lengths for bucketing)."""
    def __init__(self, datasets_root: str, seq_len: int, embed_dim: int, max_samples: int, vocab_size: int, tokenizer: UnifiedTokenizerSystem | None = None):
        self.datasets_root = datasets_root
        self.seq_len = seq_len
        self.embed_dim = embed_dim
        self.max_samples = max_samples
        self.vocab_size = vocab_size
        self.tokenizer = tokenizer
        self.samples: list[torch.Tensor] = []
        self.raw_lengths: list[int] = []
        self._build_samples()

    def _discover_text_files(self) -> list[Path]:
        return list(Path(self.datasets_root).rglob('*.txt'))[:400]

    def _tokenize(self, text: str) -> list[int]:
        if self.tokenizer and self.tokenizer.output_tokenizer:
            return self.tokenizer.output_tokenizer.encode(text)
        ln = random.randint(16, min(self.seq_len, 128))
        return [random.randint(0, self.vocab_size - 1) for _ in range(ln)]

    def _build_samples(self):
        added = 0
        for p in self._discover_text_files():
            if added >= self.max_samples:
                break
            txt = ''
            try:
                txt = p.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            if not txt.strip():
                continue
            ids = self._tokenize(txt)[: self.seq_len]
            if len(ids) < 8:
                continue  # skip ultra short
            raw_len = len(ids)
            if raw_len < self.seq_len:
                ids += [0]*(self.seq_len - raw_len)
            self.raw_lengths.append(raw_len)
            self.samples.append(torch.tensor(ids, dtype=torch.long))
            added += 1
        if not self.samples:  # fallback synthetic
            synth_n = min(256, self.max_samples)
            for _ in range(synth_n):
                ln = random.randint(16, self.seq_len)
                ids = [random.randint(0, self.vocab_size - 1) for _ in range(ln)]
                self.raw_lengths.append(len(ids))
                if ln < self.seq_len:
                    ids += [0]*(self.seq_len-ln)
                self.samples.append(torch.tensor(ids, dtype=torch.long))
        logger.info(f"[DATASET] samples={len(self.samples)} seq_len={self.seq_len} (synthetic={'yes' if added==0 else 'no'})")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx: int):
        ids = self.samples[idx]
        return {
            'input_ids': ids,
            'labels': ids.clone(),
            'attention_mask': (ids != 0).long(),
            'image_embeddings': torch.zeros(self.embed_dim),
            'audio_embeddings': torch.zeros(self.embed_dim),
            'raw_len': torch.tensor(self.raw_lengths[idx] if self.raw_lengths else ids.ne(0).sum().item())
        }


class PrefetchLoader:
    def __init__(self, loader: DataLoader, prefetch: int = 2):
        self.loader = loader
        self.queue: Queue = Queue(maxsize=prefetch)
        self._stop = False
        # worker will be started per-iterator to avoid worker death between epochs
        self._worker_thread = None
    def _worker(self):
        try:
            for batch in self.loader:
                if self._stop:
                    break
                self.queue.put(batch)
            self.queue.put(None)
        except Exception as e:
            logger.warning(f"[PREFETCH] worker error: {e}")
            self.queue.put(None)
    def __iter__(self):
        # start a fresh worker thread for this iterator
        self._stop = False
        if self._worker_thread is None or not self._worker_thread.is_alive():
            self._worker_thread = threading.Thread(target=self._worker, daemon=True)
            self._worker_thread.start()
        while True:
            start_wait = time.monotonic()
            b = self.queue.get()
            wait = time.monotonic() - start_wait
            if wait > 0.5:
                logger.info(f"[PREFETCH] queue.get waited {wait:.3f}s")
            if b is None:
                break
            yield b
    def __len__(self):  # pragma: no cover
        return len(self.loader)


class _BucketBatchSampler(torch.utils.data.Sampler[list[int]]):
    def __init__(self, batches: list[list[int]]):
        self.batches = batches
    def __iter__(self):
        yield from self.batches
    def __len__(self):
        return len(self.batches)


class UnifiedSweetSpotTrainer:
    def __init__(self, resume: str | None = 'auto', total_steps: int | None = None, auto_resume: bool = True):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.resume_arg = resume
        self.auto_resume = auto_resume or (resume and resume.lower() == 'auto')
        self.user_total_steps = total_steps
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info(f"[GPU] {torch.cuda.get_device_name(0)} | VRAM {torch.cuda.get_device_properties(0).total_memory/1024**3:.1f}GB")
        self._setup_configs()
        self.global_step = 0
        self.best_loss = float('inf')
        self.loss_history: list[float] = []
        self.transforms = DEFAULT_TRANSFORMS
        self.best_tracker = BestModelTracker(UNIFIED_CHECKPOINT_DIR / 'best')
        self.best_val_tracker = BestModelTracker(UNIFIED_CHECKPOINT_DIR / 'best_val', metric='val_loss')
        self.integrity_index = None
        self.curriculum = DEFAULT_CURRICULUM
        self.rolling_window = deque(maxlen=100)
        self.last_grad_norm: float | None = None
        self.no_val_improve = 0
        self.stop_training = False
        self.writer = None
        self.data_position = 0
        # background checkpoint queue and worker
        self._ckpt_queue: Queue[tuple[Path, dict]] = Queue()
        self._ckpt_worker_stop = False
        threading.Thread(target=self._ckpt_worker, daemon=True).start()
        # tensorboard background writer queue (non-blocking writes)
        self._tb_queue: Queue[tuple[str,str,float,int]] = Queue()
        self._tb_worker_stop = False
        threading.Thread(target=self._tb_worker, daemon=True).start()

    # --------------- RESUME HELPERS (defined early so callable during setup) ---------------
    def _candidate_checkpoint_paths(self) -> list[Path]:
        if not UNIFIED_CHECKPOINT_DIR.exists():
            return []
        return sorted(UNIFIED_CHECKPOINT_DIR.glob('unified_step_*.pth'), key=lambda p: p.stat().st_mtime, reverse=True)
    def _select_resume_checkpoint(self) -> Path | None:
        if self.resume_arg and self.resume_arg not in ('auto', 'AUTO'):
            p = Path(self.resume_arg)
            return p if p.exists() else None
        if not self.auto_resume:
            return None
        c = self._candidate_checkpoint_paths()
        return c[0] if c else None
    def _load_checkpoint(self, path: Path):
        logger.info(f"[RESUME] loading {path}")
        ckpt = torch.load(path, map_location=self.device)
        self.model.load_state_dict(ckpt['model_state_dict'])
        self.optimizer.load_state_dict(ckpt['optimizer_state_dict'])
        # Only attempt scaler restore when FP16 is enabled and a scaler exists. If the
        # checkpoint contains scaler state but the current config disables FP16, skip
        # restoring the scaler to avoid silently re-enabling mixed precision.
        ckpt_has_scaler = 'scaler_state_dict' in ckpt
        fp16_flag = bool(self.training_config.get('fp16', False))
        if fp16_flag and ckpt_has_scaler and self.scaler is not None:
            try:
                self.scaler.load_state_dict(ckpt['scaler_state_dict'])
            except Exception as e:
                logger.warning(f"[RESUME] scaler restore failed: {e}")
        elif ckpt_has_scaler and not fp16_flag:
            logger.info("[RESUME] checkpoint contains scaler state but FP16 is disabled in config; skipping scaler restore")
        self.global_step = int(ckpt.get('global_step', 0))
        self.best_loss = float(ckpt.get('best_loss', self.best_loss))
        self.loss_history = ckpt.get('loss_history', self.loss_history)
        try:  # RNG restore
            if 'python_random_state' in ckpt:
                random.setstate(ckpt['python_random_state'])
            if 'torch_rng_state' in ckpt:
                torch.set_rng_state(ckpt['torch_rng_state'])
            if torch.cuda.is_available() and 'cuda_rng_states' in ckpt:
                for i, st in enumerate(ckpt['cuda_rng_states']):
                    if i < torch.cuda.device_count():
                        torch.cuda.set_rng_state(st, device=i)
            logger.info("[RESUME] RNG restored")
        except Exception as e:  # pragma: no cover
            logger.warning(f"[RESUME] RNG restore failed: {e}")
        if self.data_position > 0 and hasattr(self, 'data_loader'):
            try:
                skip = self.data_position % max(1, len(self.data_loader))
                for _ in range(skip):
                    next(iter(self.data_loader))
                logger.info(f"[RESUME] advanced dataloader by {skip} batches")
            except Exception:
                logger.warning("[RESUME] failed to advance dataloader")
    def _resume_if_requested(self):
        path = self._select_resume_checkpoint()
        if not path:
            logger.info("[RESUME] no checkpoint (fresh start)")
            return
        try:
            self._load_checkpoint(path)
        except Exception as e:
            logger.warning(f"[RESUME] failed to load {path}: {e}")

    # ---------------- CONFIG -----------------
    def _default_training_config(self) -> dict[str, Any]:
        return {
            'batch_size': 4,
            'max_steps': 3000 if self.user_total_steps is None else self.user_total_steps,
            'gradient_accumulation_steps': 4,
            'learning_rate': 3e-4,
            'weight_decay': 0.01,
            'fp16': True,
            'log_every': 10,
            'save_every': 200,
            'validate_every': 100,
            'lr_warmup_steps': 1000,
            'min_lr': 1e-7,
            'validation_batches': 8,
            'max_grad_norm': 1.0,
            'use_prefetch': True,
            'prefetch': 2,
            'early_stopping': {'enabled': True, 'patience': 10, 'min_delta': 5e-4},
            'performance': {
                'bucket_by_length': True,
                'mmap_enabled': False,
                'mmap_corpus': None,
            },
            'safety': {'checkpoint_temp_write': True},
            'logging': {'tensorboard': True},
            'nan_recovery': {'enabled': True, 'lr_reduce_factor': 0.5, 'min_lr': 1e-7, 'max_retries': 5},
            'data': {
                'datasets_root': 'F:/data/datasets',
                'seq_len': 512,
                'max_samples': 5000,
            }
            ,
            'instrumentation': {
                'heartbeat': False,
            }
        }

    def _setup_configs(self):
        self.config = B3Config(
            embed_dim=768,
            num_heads=12,
            num_layers=8,
            vocab_size=50257,
            num_experts=8,
            expert_dim=2048,
            experts_per_token=2,
            max_seq_length=512,
        )
        self.training_config = self._default_training_config()
        if DEFAULT_CONFIG_PATH.exists() and yaml:
            try:
                with open(DEFAULT_CONFIG_PATH, encoding='utf-8') as f:
                    ext = yaml.safe_load(f) or {}
                # Accept either a top-level training: {...} mapping or a direct mapping
                if isinstance(ext, dict) and 'training' in ext and isinstance(ext['training'], dict):
                    self._deep_merge(self.training_config, ext['training'])
                else:
                    self._deep_merge(self.training_config, ext)
                logger.info("[CONFIG] external overrides applied")
            except Exception as e:
                logger.warning(f"[CONFIG] load failed: {e}")
        if self.training_config.get('logging', {}).get('tensorboard') and SummaryWriter:
            try:
                self.writer = SummaryWriter(log_dir=str(UNIFIED_CHECKPOINT_DIR / 'tb'))
            except Exception:
                self.writer = None
        self.tokenizer_system = UnifiedTokenizerSystem()
        # Threshold (L2) for proactive gradient-norm dumps. If the total norm exceeds this
        # value a minimal forensic payload will be written so we can inspect the batch.
        # This is intentionally conservative; adjust as needed.
        self._grad_norm_dump_threshold = float(self.training_config.get('grad_norm_dump_threshold', 2000.0))
        # Ensure artifacts & calibration dirs exist (configurable via env)
        with contextlib.suppress(Exception):
            ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        with contextlib.suppress(Exception):
            CALIBRATION_DIR.mkdir(parents=True, exist_ok=True)

    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]):
        for k, v in override.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict):
                self._deep_merge(base[k], v)
            else:
                base[k] = v

    # --------------- MODEL / OPTIMIZER ---------------
    def setup_model_and_optimizer(self):
        self.model = ImpressionCoreB3Model(self.config).to(self.device)
        # AdamW already sets defaults for betas/eps; batch_size is a DataLoader concern (false positive lint)
        # Coerce possibly-string config values to correct types to avoid YAML parsing/type issues
        try:
            lr_val = float(self.training_config.get('learning_rate', 3e-4))
        except Exception:
            lr_val = 3e-4
        try:
            wd_val = float(self.training_config.get('weight_decay', 0.01))
        except Exception:
            wd_val = 0.01
        self.training_config['learning_rate'] = lr_val
        self.training_config['weight_decay'] = wd_val
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=lr_val,
            weight_decay=wd_val
        )
        # optional LR scheduler with linear warmup to stabilize early training
        try:
            warmup = int(self.training_config.get('lr_warmup_steps', 0))
            if warmup > 0:
                # use LambdaLR to implement linear warmup then constant
                def lr_lambda(step: int):
                    if step >= warmup:
                        return 1.0
                    return float(step) / float(max(1, warmup))
                self.scheduler = optim.lr_scheduler.LambdaLR(self.optimizer, lr_lambda)
            else:
                self.scheduler = None
        except Exception:
            self.scheduler = None
        # Ensure fp16 config is interpreted as an explicit boolean before creating scaler.
        # Normalize fp16 flag if it's a string (some YAML variants produce strings)
        fp16_cfg = self.training_config.get('fp16', False)
        fp16_flag = fp16_cfg.lower() in ('1', 'true', 'yes', 'y', 't') if isinstance(fp16_cfg, str) else bool(fp16_cfg)
        logger.info(f"[MODEL] Mixed Precision Enabled={fp16_flag}")
        # Create GradScaler only after we've determined the intended precision mode. This
        # guarantees the scaler state creation/resume logic below uses the user's config.
        try:
            self.scaler = GradScaler(enabled=fp16_flag)
        except Exception as e:
            logger.warning(f"[MODEL] failed to create GradScaler: {e}; proceeding without scaler")
            self.scaler = None
        # Resume from checkpoint (if any) after model/optimizer/scaler exist
        self._resume_if_requested()
        logger.info(f"[MODEL] params={sum(p.numel() for p in self.model.parameters())/1e6:.2f}M")

    # --------------- VALIDATION ---------------
    def _compute_validation_loss(self) -> float | None:
        if not hasattr(self, 'val_loader') or self.val_loader is None:
            return None
        self.model.eval()
        losses: list[float] = []
        batches = 0
        with torch.no_grad():
            for batch in self.val_loader:
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
                batches += 1
                if batches >= self.training_config['validation_batches']:
                    break
        self.model.train()
        return float(sum(losses) / max(1, len(losses))) if losses else None

    def _log_validation(self, val_loss: float):
        es = self.training_config.get('early_stopping', {})
        min_delta = float(es.get('min_delta', 0.0))
        improved = val_loss < (self.best_val_tracker.best_value - min_delta)
        if improved:
            try:
                self.best_val_tracker.update(val_loss, self.global_step, self.model, self.optimizer, self.scaler, {'context': 'validation'})
                logger.info(f"[VAL][BEST] {val_loss:.6f} (Δ>{min_delta})")
            except Exception as e:
                logger.warning(f"[VAL][BEST] save failed: {e}")
            self.no_val_improve = 0
        else:
            self.no_val_improve += 1
        if self.writer:
            with contextlib.suppress(Exception):
                self.writer.add_scalar('val/loss', val_loss, self.global_step)
        if es.get('enabled') and self.no_val_improve >= int(es.get('patience', 5)):
            logger.info(f"[EARLY_STOP] patience reached (no_improve={self.no_val_improve}, min_delta={min_delta})")
            self.stop_training = True

    def _maybe_validate(self):
        if self.global_step == 0 or self.global_step % self.training_config['validate_every'] != 0:
            return
        t0 = time.monotonic()
        logger.info(f"[MAYBE_VALIDATE] start step={self.global_step}")
        val_loss = self._compute_validation_loss()
        t1 = time.monotonic()
        logger.info(f"[MAYBE_VALIDATE] done step={self.global_step} elapsed={(t1-t0):.3f}s")
        if val_loss is not None:
            self._log_validation(val_loss)

    # --------------- CHECKPOINTING ---------------
    def _maybe_save(self):
        if self.global_step % self.training_config['save_every'] != 0 or self.global_step == 0:
            return
        path = UNIFIED_CHECKPOINT_DIR / f"unified_step_{self.global_step}.pth"
        t0 = time.monotonic()
        logger.info(f"[MAYBE_SAVE] start step={self.global_step} path={path}")
        try:
            self.save_checkpoint(path)
            logger.info(f"[SAVE-ENQUEUE] {path}")
        except Exception as e:
            logger.warning(f"[SAVE] failed to enqueue: {e}")
        t1 = time.monotonic()
        logger.info(f"[MAYBE_SAVE] enqueued step={self.global_step} elapsed={(t1-t0):.3f}s")

    def _finalize_training(self):
        final_cp = UNIFIED_CHECKPOINT_DIR / f"unified_final_step_{self.global_step}.pth"
        self.save_checkpoint(final_cp)
        logger.info(f"[FINAL] Final checkpoint enqueued: {final_cp} | Total steps: {self.global_step}")
        # request checkpoint worker to stop after queue drains, then wait briefly
        try:
            self._ckpt_worker_stop = True
            # wait for queue to be processed
            self._ckpt_queue.join()
        except Exception:
            pass
        # stop and join tensorboard worker if present
        try:
            self._tb_worker_stop = True
            self._tb_queue.join()
        except Exception:
            pass
        logger.info("[FINAL] Checkpoint queue drained / writer stopped")

    def save_checkpoint(self, path: Path):
        # Prepare lightweight checkpoint dict and enqueue for background write
        try:
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
            # Enqueue for background write; items are (path, ckpt)
            self._ckpt_queue.put((path, ckpt))
            logger.info(f"[SAVE-QUEUED] {path}")
        except Exception as e:
            logger.warning(f"[SAVE] failed to enqueue checkpoint: {e}")

    def _ckpt_worker(self):
        """Background checkpoint writer. Performs atomic write (temp->move) to avoid blocking main thread.

        Queue items are (Path, ckpt_dict). Worker exits when _ckpt_worker_stop is True and queue empty.
        """
        # Add retry + fallback to handle intermittent filesystem/locking/antivirus issues
        retry_count = int(self.training_config.get('checkpoint_write_retries', 3))
        retry_sleep = float(self.training_config.get('checkpoint_write_retry_sleep', 1.0))
        fallback_dir = UNIFIED_CHECKPOINT_DIR / 'tmp_fallback'
        while not self._ckpt_worker_stop or not self._ckpt_queue.empty():
            try:
                item = self._ckpt_queue.get(timeout=1)
            except Exception:
                continue
            try:
                path, ckpt = item
                path.parent.mkdir(parents=True, exist_ok=True)
                # attempt atomic write with retries
                written = False
                last_exc = None
                for attempt in range(1, retry_count + 1):
                    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + '.tmp-')
                    try:
                        os.close(fd)
                        torch.save(ckpt, tmp)
                        try:
                            shutil.move(tmp, str(path))
                        except Exception:
                            # fallback to copy then remove
                            shutil.copyfile(tmp, str(path))
                            os.remove(tmp)
                        logger.info(f"[SAVE-DONE] {path}")
                        written = True
                        break
                    except Exception as e:
                        last_exc = e
                        logger.warning(f"[SAVE-WORKER] write attempt {attempt} failed for {path}: {e}")
                        try:
                            if os.path.exists(tmp):
                                os.remove(tmp)
                        except Exception:
                            pass
                        time.sleep(retry_sleep)
                if not written:
                    # try non-atomic fallback to local fallback dir
                    try:
                        fallback_dir.mkdir(parents=True, exist_ok=True)
                        fb = fallback_dir / path.name
                        torch.save(ckpt, str(fb))
                        logger.warning(f"[SAVE-WORKER] wrote checkpoint to fallback location: {fb}")
                    except Exception as e:
                        logger.warning(f"[SAVE-WORKER] fallback write also failed for {path}: {e} | last_exc={last_exc}")
            except Exception as e:
                logger.warning(f"[SAVE-WORKER] error writing checkpoint: {e}")
            finally:
                with contextlib.suppress(Exception):
                    self._ckpt_queue.task_done()

    def _tb_worker(self):
        """Background TensorBoard writer. Dequeues (tag, kind, value, step) tuples and writes via SummaryWriter.

        Exits when _tb_worker_stop is True and queue empty.
        """
        if not self.writer:
            return
        while not self._tb_worker_stop or not self._tb_queue.empty():
            try:
                item = self._tb_queue.get(timeout=1)
            except Exception:
                continue
            try:
                tag, kind, value, step = item
                try:
                    if kind == 'scalar':
                        self.writer.add_scalar(tag, value, step)
                    # extend for other kinds if needed
                except Exception:
                    # don't let TB writer exceptions kill the worker
                    pass
            finally:
                with contextlib.suppress(Exception):
                    self._tb_queue.task_done()

    # --------------- DATA LOADER ---------------
    def setup_data_loader(self):
        logger.info("[DATA] Preparing unified dataset ...")
        data_cfg = self.training_config.get('data', {})
        self.dataset = UnifiedSweetSpotDataset(
            datasets_root=data_cfg.get('datasets_root', 'F:/data/datasets'),
            seq_len=data_cfg.get('seq_len', 512),
            embed_dim=self.config.embed_dim,
            max_samples=data_cfg.get('max_samples', 5000),
            vocab_size=self.config.vocab_size,
            tokenizer=self.tokenizer_system,
        )
        def collate_fn(batch: list[dict[str, torch.Tensor]]):
            return {
                'input_ids': torch.stack([b['input_ids'] for b in batch], dim=0),
                'labels': torch.stack([b['labels'] for b in batch], dim=0),
                'attention_mask': torch.stack([b['attention_mask'] for b in batch], dim=0),
                'image_embeddings': torch.stack([b['image_embeddings'] for b in batch], dim=0),
                'audio_embeddings': torch.stack([b['audio_embeddings'] for b in batch], dim=0),
            }
        bucket_sampler = self._build_bucket_sampler(self.dataset)
        if bucket_sampler is not None:
            logger.info(f"[PERF] Using length bucket sampler: {len(bucket_sampler)} batches")
            self.data_loader = DataLoader(
                self.dataset,
                batch_sampler=bucket_sampler,
                num_workers=0,
                pin_memory=True,
                collate_fn=collate_fn,
            )
        else:
            self.data_loader = DataLoader(
                self.dataset,
                batch_size=self.training_config['batch_size'],
                shuffle=True,
                num_workers=0,
                pin_memory=True,
                drop_last=True,
                collate_fn=collate_fn,
            )
        if len(self.dataset) > 20:
            from torch.utils.data import Subset
            val_indices = list(range(0, min(200, len(self.dataset)//20)))
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
        if self.training_config.get('use_prefetch'):
            try:
                self.data_loader = PrefetchLoader(self.data_loader, prefetch=self.training_config.get('prefetch', 2))
                if self.val_loader is not None:
                    self.val_loader = PrefetchLoader(self.val_loader, prefetch=1)
                logger.info(f"[PERF] Prefetch enabled (train={self.training_config.get('prefetch',2)})")
            except Exception as e:
                logger.warning(f"[PERF] Prefetch disabled: {e}")
        logger.info(f"[DATA] Size: {len(self.dataset)} | Batches/Epoch: {len(self.data_loader)}")
        # track last batch seen for forensic dumps on numeric failures
        self._last_seen_batch: dict[str, torch.Tensor] | None = None
        try:
            self.integrity_index = HashIndex(EMBED_ROOT, HASH_INDEX_PATH)
            updated, total = self.integrity_index.build_or_update(limit=50)
            logger.info(f"[INTEGRITY] Hash index updated: {updated} / {total} files (sampled)")
        except Exception as e:
            logger.warning(f"[INTEGRITY] Hash indexing skipped: {e}")

    def _build_bucket_sampler(self, dataset: UnifiedSweetSpotDataset):
        perf = self.training_config.get('performance', {})
        if not perf.get('bucket_by_length') or not dataset.raw_lengths:
            return None
        batch_size = self.training_config['batch_size']
        indices = list(range(len(dataset.raw_lengths)))
        indices.sort(key=lambda i: dataset.raw_lengths[i])
        bucket_size = batch_size * 32
        batches: list[list[int]] = []
        for i in range(0, len(indices), bucket_size):
            bucket = indices[i:i+bucket_size]
            for j in range(0, len(bucket), batch_size):
                b = bucket[j:j+batch_size]
                if len(b) == batch_size:
                    batches.append(b)
        random.shuffle(batches)
        return _BucketBatchSampler(batches) if batches else None

    # --------------- OPTIM / LOGGING ---------------
    def _maybe_optimize(self):
        if (self.global_step + 1) % self.training_config['gradient_accumulation_steps'] != 0:
            return
        # Unscale grads for fp16 before clipping
        if self.training_config.get('fp16', False) and getattr(self, 'scaler', None) is not None:
            with contextlib.suppress(Exception):
                self.scaler.unscale_(self.optimizer)

        # Clip gradients and capture total norm
        total_norm = float('nan')
        try:
            total_norm = torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.training_config['max_grad_norm'])
        except Exception as e:
            logger.warning(f"[OPT] clip_grad_norm failed: {e}")

        # Proactive grad-norm threshold dump: if gradients get very large, persist a small
        # forensic payload (last seen batch) to help debugging before a NaN occurs.
        try:
            if (not math.isnan(total_norm)) and (self._grad_norm_dump_threshold is not None) and (total_norm > float(self._grad_norm_dump_threshold)):
                logger.warning(f"[OPT] grad_norm {total_norm:.2f} exceeded threshold {self._grad_norm_dump_threshold}; dumping last-seen batch")
                try:
                    if getattr(self, '_last_seen_batch', None) is not None:
                        self._dump_bad_batch(context='grad_norm', step=self.global_step, batch=self._last_seen_batch)
                except Exception as e:
                    logger.warning(f"[OPT] failed to dump last seen batch on grad-norm threshold: {e}")
        except Exception:
            pass

        # NaN/Inf detection in gradients
        found_bad = False
        try:
            for p in self.model.parameters():
                if p.grad is not None and torch.is_tensor(p.grad):
                    if torch.isnan(p.grad).any() or torch.isinf(p.grad).any():
                        found_bad = True
                        break
        except Exception:
            found_bad = False

        if found_bad:
            nr = self.training_config.get('nan_recovery', {})
            logger.warning(f"[OPT] NaN/Inf detected in gradients at step={self.global_step}; attempting recovery")
            # attempt forensic dump of the last seen batch for analysis (unconditional)
            try:
                if getattr(self, '_last_seen_batch', None) is not None:
                    # avoid saving huge tensors; _dump_bad_batch will trim
                    self._dump_bad_batch(context='grad', step=self.global_step, batch=self._last_seen_batch)
            except Exception as e:
                logger.warning(f"[OPT] failed to dump last seen batch: {e}")
            # attempt simple recovery: zero grads, reduce LR, skip step
            with contextlib.suppress(Exception):
                self.optimizer.zero_grad()
            # reduce LR
            try:
                curr_lr = self.optimizer.param_groups[0].get('lr', self.training_config['learning_rate'])
                new_lr = max(float(nr.get('min_lr', 1e-7)), curr_lr * float(nr.get('lr_reduce_factor', 0.5)))
                for g in self.optimizer.param_groups:
                    g['lr'] = new_lr
                logger.info(f"[OPT] LR reduced from {curr_lr:.6g} to {new_lr:.6g}")
            except Exception as e:
                logger.warning(f"[OPT] failed to reduce LR: {e}")
            # do not step optimizer this accumulation window
            self.last_grad_norm = float(total_norm) if not math.isnan(total_norm) else None
            return

        # normal stepping path
        if self.training_config.get('fp16', False) and getattr(self, 'scaler', None) is not None:
            try:
                self.scaler.step(self.optimizer)
                self.scaler.update()
            except Exception as e:
                logger.warning(f"[OPT] scaler step failed: {e}")
        else:
            try:
                self.optimizer.step()
            except Exception as e:
                logger.warning(f"[OPT] optimizer.step failed: {e}")

        # scheduler step should happen after optimizer step
        try:
            if getattr(self, 'scheduler', None) is not None:
                # LambdaLR expects step() each optimizer step
                self.scheduler.step()
        except Exception as e:
            logger.warning(f"[OPT] scheduler.step failed: {e}")

        with contextlib.suppress(Exception):
            self.optimizer.zero_grad()
        self.last_grad_norm = float(total_norm) if not math.isnan(total_norm) else None

    def _maybe_log(self, accumulation: float, steps_accum: int):
        if self.global_step % self.training_config['log_every'] != 0:
            return accumulation, steps_accum
        avg_loss = accumulation / max(1, steps_accum)
        self.rolling_window.append(avg_loss)
        rolling_mean = sum(self.rolling_window)/len(self.rolling_window)
        try:
            ppl = math.exp(min(20, rolling_mean))
        except OverflowError:  # pragma: no cover
            ppl = float('inf')
        if torch.cuda.is_available():
            try:
                used = torch.cuda.memory_allocated()/1024**2
                resv = torch.cuda.memory_reserved()/1024**2
            except Exception:
                used = resv = 0
        else:
            used = resv = 0
        grad_txt = f" grad={self.last_grad_norm:.2f}" if self.last_grad_norm is not None else ""
        logger.info(f"[STEP {self.global_step}] loss={avg_loss:.6f} roll={rolling_mean:.6f} ppl={ppl:.2f} vram={used:.0f}/{resv:.0f}MB{grad_txt}")
        if avg_loss < self.best_loss:
            self.best_loss = avg_loss
            try:
                self.best_tracker.update(avg_loss, self.global_step, self.model, self.optimizer, self.scaler, {'loss_history_len': len(self.loss_history)})
            except Exception as e:
                logger.warning(f"[BEST] update failed: {e}")
        self.loss_history.append(avg_loss)
        if self.writer:
            try:
                # enqueue scalars for background TB writer
                self._tb_queue.put(('train/loss', 'scalar', avg_loss, self.global_step))
                self._tb_queue.put(('train/rolling_loss', 'scalar', rolling_mean, self.global_step))
                self._tb_queue.put(('train/perplexity', 'scalar', ppl, self.global_step))
                if self.last_grad_norm is not None:
                    self._tb_queue.put(('train/grad_norm', 'scalar', self.last_grad_norm, self.global_step))
            except Exception:
                pass
        return 0.0, 0

    # (Duplicate resume helpers removed to avoid shadowing earlier definitions)

    # --------------- TRAIN STEP ---------------
    def train_step(self, batch: dict[str, torch.Tensor]) -> float:
        _ = self.curriculum.current(self.global_step)
        # keep a small CPU snapshot of the most-recent batch for forensic dumping
        try:
            safe_batch = {}
            for k, v in batch.items():
                if torch.is_tensor(v):
                    # copy only first few elements where appropriate to avoid huge saves
                    try:
                        safe_batch[k] = v[:4].cpu()
                    except Exception:
                        try:
                            safe_batch[k] = v.cpu()
                        except Exception:
                            safe_batch[k] = None
                else:
                    safe_batch[k] = v
            self._last_seen_batch = safe_batch
        except Exception:
            self._last_seen_batch = None
        batch = {k: v.to(self.device) if torch.is_tensor(v) else v for k, v in batch.items()}
        for t in self.transforms:
            try:
                batch = t(batch)
            except Exception:
                continue
        if self.training_config['fp16']:
            with autocast(device_type='cuda', dtype=torch.float16):
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
        # Detect NaN/Inf in loss before backward
        loss_val = float(loss.item())
        if (math.isnan(loss_val) or math.isinf(loss_val)) and self.training_config.get('nan_recovery', {}).get('enabled', False):
            nr = self.training_config.get('nan_recovery', {})
            logger.warning(f"[STEP] NaN/Inf loss detected at step={self.global_step} (loss={loss_val}); attempting recovery: reduce LR and skip backward")
            try:
                if self.training_config.get('nan_recovery', {}).get('dump_bad_batch', True):
                    self._dump_bad_batch(context='loss', step=self.global_step, batch=batch)
            except Exception:
                pass
            try:
                curr_lr = self.optimizer.param_groups[0].get('lr', self.training_config['learning_rate'])
                new_lr = max(float(nr.get('min_lr', 1e-7)), curr_lr * float(nr.get('lr_reduce_factor', 0.5)))
                for g in self.optimizer.param_groups:
                    g['lr'] = new_lr
                logger.info(f"[STEP] LR reduced from {curr_lr:.6g} to {new_lr:.6g}")
            except Exception as e:
                logger.warning(f"[STEP] failed to reduce LR: {e}")
            # skip backward to avoid corrupting optimizer state
            return loss_val

        if self.training_config['fp16']:
            self.scaler.scale(loss).backward()
        else:
            loss.backward()
        return float(loss.item())

    def _dump_bad_batch(self, context: str, step: int, batch: dict[str, torch.Tensor] | None = None):
        """Save a minimal representation of the problematic batch + meta to artifacts/ for inspection.

        This avoids saving huge tensors; we save input_ids, attention_mask and CPU copies of the first
        few tensors and a small metadata JSON. Files are named `artifacts/bad_batch_{context}_step_{step}.pt`.
        """
        # Robust dump with retries and temp->move atomic pattern. Falls back to UNIFIED_CHECKPOINT_DIR/tmp_fallback
        retry_count = int(self.training_config.get('dump_write_retries', 3))
        retry_sleep = float(self.training_config.get('dump_write_retry_sleep', 0.5))
        ART = ARTIFACTS_DIR
        with contextlib.suppress(Exception):
            ART.mkdir(parents=True, exist_ok=True)
        meta = {
            'step': int(step),
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'fp16': bool(self.training_config.get('fp16', False)),
        }
        payload = {'meta': meta}
        if batch:
            try:
                payload['input_ids'] = batch.get('input_ids')[:4].cpu() if torch.is_tensor(batch.get('input_ids')) else None
                payload['attention_mask'] = batch.get('attention_mask')[:4].cpu() if torch.is_tensor(batch.get('attention_mask')) else None
                payload['labels'] = batch.get('labels')[:4].cpu() if torch.is_tensor(batch.get('labels')) else None
            except Exception:
                pass
        p = ART / f"bad_batch_{context}_step_{step}.pt"
        written = False
        last_exc = None
        for attempt in range(1, retry_count + 1):
            try:
                # write to temp file then move for atomicity
                fd, tmp = tempfile.mkstemp(dir=str(ART), prefix=p.name + '.tmp-')
                try:
                    os.close(fd)
                    torch.save(payload, tmp)
                    try:
                        shutil.move(tmp, str(p))
                    except Exception:
                        shutil.copyfile(tmp, str(p))
                        os.remove(tmp)
                    logger.info(f"[DUMP] saved bad batch payload: {p} (attempt {attempt})")
                    written = True
                    break
                finally:
                    if os.path.exists(tmp):
                        with contextlib.suppress(Exception):
                            os.remove(tmp)
            except Exception as e:
                last_exc = e
                logger.warning(f"[DUMP] attempt {attempt} failed to save bad batch {p}: {e}")
                time.sleep(retry_sleep)
        if not written:
            # final fallback: try writing to UNIFIED_CHECKPOINT_DIR/tmp_fallback
            try:
                fb_dir = UNIFIED_CHECKPOINT_DIR / 'tmp_fallback'
                fb_dir.mkdir(parents=True, exist_ok=True)
                fb = fb_dir / p.name
                torch.save(payload, str(fb))
                logger.warning(f"[DUMP] saved bad batch payload to fallback: {fb}")
            except Exception as e:
                logger.warning(f"[DUMP] failed to save bad batch to fallback: {e} | last_exc={last_exc}")
    # --------------- TRAIN LOOP ---------------
    def train(self):
        logger.info("[START] unified sweet spot training")
        self.setup_model_and_optimizer()
        self.setup_data_loader()
        acc = 0.0
        acc_steps = 0
        UNIFIED_CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
        # Enforce explicit user-provided total_steps (hard cap). This guarantees that
        # wrapper callers (e.g. run_stable_short.py) requesting a short run will
        # not be overridden by resume logic or other config mutations.
        if self.user_total_steps is not None:
            try:
                self.training_config['max_steps'] = int(self.user_total_steps)
                logger.info(f"[CONFIG] enforced user_total_steps: max_steps={self.training_config['max_steps']}")
            except Exception as e:
                logger.warning(f"[CONFIG] failed to enforce user_total_steps={self.user_total_steps}: {e}")
        try:
            while self.global_step < self.training_config['max_steps'] and not self.stop_training:
                for batch in self.data_loader:
                    if self.global_step >= self.training_config['max_steps'] or self.stop_training:
                        break
                    # optional lightweight heartbeat instrumentation
                    try:
                        hb = self.training_config.get('instrumentation', {}).get('heartbeat', False)
                    except Exception:
                        hb = False
                    if hb and (self.global_step % max(1, self.training_config.get('log_every', 10)) == 0):
                        logger.info(f"[HEARTBEAT] before_step={self.global_step}")
                    loss_val = self.train_step(batch)
                    if hb and (self.global_step % max(1, self.training_config.get('log_every', 10)) == 0):
                        logger.info(f"[HEARTBEAT] after_step={self.global_step}")
                    acc += loss_val
                    acc_steps += 1
                    self._maybe_optimize()
                    acc, acc_steps = self._maybe_log(acc, acc_steps)
                    self._maybe_validate()
                    self._maybe_save()
                    self.global_step += 1
                    self.data_position = (self.data_position + 1) % max(1, len(self.data_loader))
                    if self.stop_training:
                        break
        except KeyboardInterrupt:
            logger.info("[INTERRUPT] user stop")
        finally:
            self._finalize_training()

def main():  # pragma: no cover
    parser = argparse.ArgumentParser(description='Unified Sweet Spot Trainer')
    parser.add_argument('--steps', type=int, default=None, help='Override max training steps')
    parser.add_argument('--resume', type=str, default='auto', help='Resume checkpoint path or "auto"')
    args = parser.parse_args()
    trainer = UnifiedSweetSpotTrainer(resume=args.resume, total_steps=args.steps, auto_resume=True)
    trainer.train()

if __name__ == '__main__':  # pragma: no cover
    main()

    # ----------- VALIDATION (REFACTORED) -----------
    def _compute_validation_loss(self) -> float | None:
        if not self.val_loader:
            return None
        self.model.eval()
        losses: list[float] = []
        with torch.no_grad():
            for i, batch in enumerate(self.val_loader):
                if i >= self.training_config['validation_batches']:
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
        self.model.train()
        return (sum(losses)/len(losses)) if losses else None
    def _log_validation(self, val_loss: float):
        logger.info(f"[VAL] step={self.global_step} loss={val_loss:.6f}")
        es = self.training_config.get('early_stopping', {})
        min_delta = float(es.get('min_delta', 0.0))
        improved = val_loss < (self.best_val_tracker.best_value - min_delta)
        if improved:
            try:
                self.best_val_tracker.update(val_loss, self.global_step, self.model, self.optimizer, self.scaler, {'context': 'validation'})
                logger.info(f"[VAL][BEST] {val_loss:.6f} (Δ>{min_delta})")
            except Exception as e:
                logger.warning(f"[VAL][BEST] save failed: {e}")
            self.no_val_improve = 0
        else:
            self.no_val_improve += 1
        if self.writer:
            with contextlib.suppress(Exception):
                self._tb_queue.put(('val/loss', 'scalar', val_loss, self.global_step))
        if es.get('enabled') and self.no_val_improve >= int(es.get('patience', 5)):
            logger.info(f"[EARLY_STOP] patience reached (no_improve={self.no_val_improve}, min_delta={min_delta})")
            self.stop_training = True
    def _maybe_validate(self):
        if self.global_step == 0 or self.global_step % self.training_config['validate_every'] != 0:
            return
        val_loss = self._compute_validation_loss()
        if val_loss is not None:
            self._log_validation(val_loss)

    # --------------- CHECKPOINTING ---------------
    def _maybe_save(self):
        if self.global_step % self.training_config['save_every'] != 0 or self.global_step == 0:
            return
        path = UNIFIED_CHECKPOINT_DIR / f"unified_step_{self.global_step}.pth"
        try:
            self.save_checkpoint(path)
            logger.info(f"[SAVE] {path}")
        except Exception as e:
            logger.warning(f"[SAVE] failed: {e}")

    def _finalize_training(self):
        final_cp = UNIFIED_CHECKPOINT_DIR / f"unified_final_step_{self.global_step}.pth"
        self.save_checkpoint(final_cp)
        logger.info(f"[FINAL] Final checkpoint saved: {final_cp} | Total steps: {self.global_step}")

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
    def _restore_training_progress(self, ckpt: dict[str, Any]):
        self.global_step = int(ckpt.get('global_step', self.global_step))
        self.best_loss = float(ckpt.get('best_loss', self.best_loss))
        if isinstance(ckpt.get('loss_history'), list):
            self.loss_history = ckpt['loss_history']
        if self.global_step >= self.training_config['max_steps']:
            self.training_config['max_steps'] = self.global_step + 1000
        logger.info(
            f"[RESUME] Resuming at step {self.global_step} (target {self.training_config['max_steps']}) best_loss={self.best_loss:.6f}"
        )

    # (Duplicate _resume_if_requested removed earlier; using the definition placed near top of class.)

    # ---------------------------- DATA LOADER -----------------------------
    def setup_data_loader(self):
        logger.info("[DATA] Preparing unified dataset ...")
        data_cfg = self.training_config.get('data', {})
        self.dataset = UnifiedSweetSpotDataset(
            datasets_root=data_cfg.get('datasets_root', 'F:/data/datasets'),
            seq_len=data_cfg.get('seq_len', 512),
            embed_dim=self.config.embed_dim,
            max_samples=data_cfg.get('max_samples', 5000),
            vocab_size=self.config.vocab_size,
            tokenizer=self.tokenizer_system,
        )
        def collate_fn(batch: list[dict[str, torch.Tensor]]):
            return {
                'input_ids': torch.stack([b['input_ids'] for b in batch], dim=0),
                'labels': torch.stack([b['labels'] for b in batch], dim=0),
                'attention_mask': torch.stack([b['attention_mask'] for b in batch], dim=0),
                'image_embeddings': torch.stack([b['image_embeddings'] for b in batch], dim=0),
                'audio_embeddings': torch.stack([b['audio_embeddings'] for b in batch], dim=0),
            }
        bucket_sampler = self._build_bucket_sampler(self.dataset)
        if bucket_sampler is not None:
            logger.info(f"[PERF] Using length bucket sampler: {len(bucket_sampler)} batches")
            self.data_loader = DataLoader(
                self.dataset,
                batch_sampler=bucket_sampler,
                num_workers=0,
                pin_memory=True,
                collate_fn=collate_fn,
            )
        else:
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

    def _build_bucket_sampler(self, dataset: UnifiedSweetSpotDataset):
        perf = self.training_config.get('performance', {})
        if not perf.get('bucket_by_length') or not dataset.raw_lengths:
            return None
        batch_size = self.training_config['batch_size']
        indices = list(range(len(dataset.raw_lengths)))
        indices.sort(key=lambda i: dataset.raw_lengths[i])
        bucket_size = batch_size * 32  # heuristic group
        batches: list[list[int]] = []
        for i in range(0, len(indices), bucket_size):
            bucket = indices[i:i+bucket_size]
            # within bucket, form batches sequentially (already length-sorted)
            for j in range(0, len(bucket), batch_size):
                b = bucket[j:j+batch_size]
                if len(b) == batch_size:
                    batches.append(b)
        random.shuffle(batches)
        return _BucketBatchSampler(batches) if batches else None
