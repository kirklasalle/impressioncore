"""KD + SFT Curriculum Training (Phase 2)
=================================================

Implements combined Supervised Fine Tuning (SFT) with self-distillation style
Knowledge Distillation (KD) using an EMA (Exponential Moving Average) teacher.

Data Assumptions:
  - JSONL manifest produced by build_kd_dataset.py with fields:
      prompt, target, rationale (optional), modality, bucket

Training Objective:
  loss = CE(masked) + beta(step) * KL(student_T || teacher_T)
  where beta linearly warms from 0 → kl_final_weight over kl_warmup_ratio * total_steps

Memory Constraints (GTX 1050 Ti 4GB):
  - Gradient accumulation (micro_batch * accum_steps = effective batch)
  - Mixed precision (amp) when CUDA available
  - Optional gradient checkpointing already supported inside model

Self-Distillation Rationale:
  Since external teacher logits not persisted, we maintain an EMA copy of the
  student as a slowly moving teacher to stabilize early training while still
  permitting improvement (student learns from newer gradients).

Notes:
  - Only CE part applies to tokens of the target segment (prompt tokens masked)
  - KL computed on the same tokens where labels != -100 to limit compute
  - Handles short datasets via multiple epochs until max_steps reached
  - Safe loading of base checkpoint; if absent, initializes fresh model
  - Tokenization uses tiktoken GPT-2 encoding (50257) with robust fallback
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from pathlib import Path as _Path

# Ensure project root (parent of 'src') on sys.path for "src." imports
_file_path = _Path(__file__).resolve()
_parents = _file_path.parents
_PROJECT_ROOT = _parents[3] if len(_parents) > 3 else _parents[-1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import contextlib

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

try:  # tokenizer dependency
    import tiktoken  # type: ignore
except Exception:  # pragma: no cover
    tiktoken = None  # fallback handled later

# Import model components with robust fallbacks avoiding training __init__ side-effects
_arch_import_error = None

# ------------------------------------------------------------------
# Implementation Version Identifier (bump when logic meaningfully changes)
# ------------------------------------------------------------------
TRAIN_IMPL_VERSION = "KD_SFT_V2_explicit_ce_curriculum_2025-08-14"
TIMESTAMP_FMT = "%B %d, %Y %I:%M:%S %p"

def now_ts() -> str:
    return datetime.now().strftime(TIMESTAMP_FMT)

# ---------------------------------------------------------------
# Dynamic helper loader (avoids importing entire training package)
# ---------------------------------------------------------------
_HEEL_HELPERS = None
def _load_heel_helpers():  # lazy load to bypass package side-effects
    global _HEEL_HELPERS
    if _HEEL_HELPERS is not None:
        return _HEEL_HELPERS
    from importlib.machinery import SourceFileLoader
    heel_path = _PROJECT_ROOT / 'src' / 'training' / 'utils' / 'heel_logic.py'
    try:
        mod = SourceFileLoader('heel_logic_local', str(heel_path)).load_module()
        _HEEL_HELPERS = mod
    except Exception as e:  # fallback minimal inline implementation
        class HeelConfigViewFallback:
            def __init__(self, heel_min_windows, heel_min_eff_floor, heel_eff_ratio, heel_curvature_tol, heel_var_ratio_max, heel_peak_decay, heel_hold_consec):
                self.heel_min_windows = heel_min_windows
                self.heel_min_eff_floor = heel_min_eff_floor
                self.heel_eff_ratio = heel_eff_ratio
                self.heel_curvature_tol = heel_curvature_tol
                self.heel_var_ratio_max = heel_var_ratio_max
                self.heel_peak_decay = heel_peak_decay
                self.heel_hold_consec = heel_hold_consec
        from collections import deque as _dq
        def init_heel_state():
            return {
                "last_raw_ce": None,
                "eff_ema": 0.0,
                "eff_peak": 0.0,
                "eff_prev": _dq(maxlen=3),
                "raw_ce_history": _dq(maxlen=16),
                "windows": 0,
                "heel_consec": 0,
                "heel_reported": False,
                "heel_stopped": False,
                "last_token_eff": None,
            }
        def update_heel_metrics(state, cfg, *, pre_reset_raw_ce: float, supervised_tok: int):
            state['windows'] += 1
            delta_ce = 0.0
            if state['last_raw_ce'] is not None:
                delta_ce = max(0.0, state['last_raw_ce'] - pre_reset_raw_ce)
            token_eff = delta_ce / max(1, supervised_tok)
            state['eff_ema'] = 0.9*state['eff_ema'] + 0.1*token_eff
            state['eff_peak'] = max(state['eff_peak']*cfg.heel_peak_decay, state['eff_ema'])
            state['eff_prev'].append(state['eff_ema'])
            curvature=0.0
            if len(state['eff_prev'])==3:
                a, b, c = state['eff_prev'][0], state['eff_prev'][1], state['eff_prev'][2]
                curvature = c - 2 * b + a
            state['raw_ce_history'].append(pre_reset_raw_ce)
            var_ratio=0.0
            if len(state['raw_ce_history'])>4:
                vals = list(state['raw_ce_history'])
                mean_v = sum(vals) / len(vals)
                if mean_v > 0:
                    var = sum((x - mean_v) ** 2 for x in vals) / len(vals)
                    std = var ** 0.5
                    var_ratio = std / mean_v
            eff_ratio = (token_eff/(state['eff_peak']+1e-12)) if state['eff_peak']>0 else 0.0
            cand_reasons={
                'enough_windows': state['windows']>=cfg.heel_min_windows,
                'above_eff_floor': token_eff>=cfg.heel_min_eff_floor,
                'eff_ratio_ok': eff_ratio<=cfg.heel_eff_ratio,
                'curvature_ok': curvature>-cfg.heel_curvature_tol,
                'var_ok': var_ratio<cfg.heel_var_ratio_max,
            }
            heel_cand = all(cand_reasons.values()) and state['eff_peak']>0
            if heel_cand:
                state['heel_consec'] += 1
            else:
                state['heel_consec'] = 0
            state['last_token_eff'] = token_eff
            state['last_raw_ce'] = pre_reset_raw_ce
            return {
                "token_eff": token_eff,
                "eff_ratio": eff_ratio,
                "curvature": curvature,
                "var_ratio": var_ratio,
                "heel_cand": heel_cand,
                "cand_reasons": cand_reasons,
            }
        _HEEL_HELPERS = type('HeelHelpers', (), {
            'init_heel_state': init_heel_state,
            'update_heel_metrics': update_heel_metrics,
            'HeelConfigView': HeelConfigViewFallback,
            '__error__': e,
        })
    return _HEEL_HELPERS
try:
    from src.core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model
except Exception as e:
    _arch_import_error = e
    try:
        # Try relative path import by direct exec of file
        arch_path = _PROJECT_ROOT / 'src' / 'core' / 'models' / 'impressioncore_b3_architecture.py'
        spec = {'__name__': 'impressioncore_b3_architecture_temp'}
        with open(arch_path, encoding='utf-8') as f:
            code = compile(f.read(), str(arch_path), 'exec')
        exec(code, spec)
        ImpressionCoreB3Model = spec['ImpressionCoreB3Model']
        B3Config = spec['B3Config']
        _arch_import_error = None
    except Exception as e2:  # pragma: no cover
        raise RuntimeError(f"Failed to import B3 architecture (primary: {_arch_import_error}) (fallback: {e2})") from e


# ----------------------
# Configuration
# ----------------------
@dataclass
class KDConfig:
    manifest_path: str = "src/training/configs/datasets/dialog_phase1_manifest.json"
    base_checkpoint: str = "F:/models/checkpoints/b3_phase1/checkpoint_epoch_19.pth"
    output_dir: str = "F:/models/checkpoints/kd_sft_phase2"
    lr: float = 2e-4
    weight_decay: float = 0.01
    micro_batch: int = 1
    accum_steps: int = 32
    max_steps: int = 5000  # Phase 2 target
    epochs: int = 10  # Approximate epochs
    kl_temperature: float = 2.0
    kl_final_weight: float = 0.3
    kl_warmup_ratio: float = 0.3  # portion of total steps for linear ramp
    ema_decay: float = 0.995
    warmup_steps: int = 50
    log_every: int = 10
    eval_every: int = 100
    save_every: int = 300
    max_seq_length: int = 2048  # truncate combined prompt+target
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    fp16: bool = True
    seed: int = 42
    mask_prompt_loss: bool = True  # mask prompt portion from CE
    expert_loss_scale: float = 0.01  # scale factor applied to expert/aux losses to keep LM loss interpretable
    # Dynamic sequence length curriculum: use short_seq_len for first short_seq_steps steps
    short_seq_len: int = 768
    short_seq_steps: int = 9999  # freeze short seq to isolate heel detection dynamics
    # EMA update interval (every n optimizer steps)
    ema_update_interval: int = 1
    # Safety / stability
    spike_ratio_threshold: float = 4.0  # if raw CE > threshold * running avg -> LR backoff
    lr_backoff_factor: float = 0.5  # multiply LR by this on spike
    min_lr: float = 5e-7  # floor to avoid zeroing
    # Heel stop (sweet spot) configuration
    enable_heel_stop: bool = True
    heel_min_windows: int = 4          # need at least this many windows before considering stop
    heel_hold_consec: int = 2           # consecutive heel_cand windows to confirm
    heel_eff_ratio: float = 0.40        # token_eff <= eff_peak * ratio triggers candidate
    heel_curvature_tol: float = 1e-6    # curvature > -tol (i.e., flattening)
    heel_var_ratio_max: float = 0.08    # variance ratio ceiling for stable detection
    heel_min_eff_floor: float = 1e-6    # require token_eff >= this to consider heel
    heel_peak_decay: float = 1.0        # decay factor applied to eff_peak each window (1.0 = no decay)
    # --- Phase 2 (post-heel adaptive refinement) ---
    enable_phase2_after_heel: bool = False  # if True, do NOT terminate at heel; instead adapt schedule
    phase2_extra_steps: int = 20            # number of additional refinement steps after heel detection
    phase2_lr_scale: float = 0.3            # multiply base LR by this factor during phase2
    phase2_kl_taper_steps: int = 10         # steps over which to linearly decay KL (if disabling)
    phase2_disable_kl: bool = True          # if True, KL weight tapers to 0 across taper steps
    phase2_expert_scale: float = 0.5        # multiply expert_loss_scale by this during phase2 (stabilization)
    # Runtime adaptive controls
    runtime_override_path: str | None = None  # JSON file polled for mid-run parameter overrides
    status_snapshot_every: int = 0  # if >0, write periodic status snapshot JSON
    # --- Runtime adaptive control & snapshots ---
    runtime_override_path: str = "runtime_overrides.json"  # looked up relative to output_dir if not absolute
    snapshot_windows_interval: int = 0  # every N instrumentation windows, write snapshot (0=disabled)
    # --- Enhanced metrics & auto comparison controls ---
    enable_throughput_metric: bool = True          # append tok/s column to metrics CSV
    rolling_ce_improve_window: int = 30            # window size for CE improvement (%); 0 disables
    auto_compare_min_windows: int = 0              # require at least this many windows before auto-compare
    auto_compare_min_phase2_steps: int = 0         # require at least this many steps into phase2
    # --- Data condensation & modality mix instrumentation ---
    log_modality_mix: bool = True                  # log modality distribution each logging window
    modality_balance_enable: bool = False          # if True, attempt simple uniform reweight (future hook)
    modality_imbalance_warn_ratio: float = 4.0     # warn if (max_count/min_count) exceeds
    # --- Adaptive KL schedule calibration ---
    kl_adapt_enable: bool = False                  # enable dynamic warmup compression
    kl_adapt_window: int = 5                       # require at least this many logging windows
    kl_adapt_improve_threshold: float = 0.5        # (%) required CE improvement over first window to keep schedule
    kl_adapt_min_ramp_reduction: float = 0.5       # fraction to shrink remaining warmup when under-performing
    # --- Phase2 marginal gain auto-stop ---
    phase2_auto_stop_enable: bool = False
    phase2_auto_stop_patience: int = 3             # consecutive windows below improvement threshold
    phase2_auto_stop_min_improve: float = 0.25     # (%) relative CE improvement vs phase2 baseline required
    # --- Gradient checkpointing auto suggestion ---
    auto_enable_checkpointing: bool = False        # attempt enabling mid-run if utilization high
    checkpointing_utilization_threshold: float = 0.92  # GPU mem alloc / total > threshold triggers


# ----------------------
# Tokenizer Utilities
# ----------------------
class GPT2LikeTokenizer:
    """Wrapper for tiktoken gpt2 with fallback naive tokenizer.

    Exposes encode(text)->List[int] and decode(ids)->str.
    """

    def __init__(self, vocab_size: int = 50257):
        self.vocab_size = vocab_size
        self._use_tiktoken = False
        if tiktoken is not None:
            try:
                self.enc = tiktoken.get_encoding("gpt2")
                self._use_tiktoken = True
            except Exception:
                self._use_tiktoken = False
        if not self._use_tiktoken:
            # Simple reversible whitespace/token fallback
            self.basic_vocab: dict[str, int] = {"<pad>": 0, "<eos>": 50256}
            self.next_id = 1

    def encode(self, text: str) -> list[int]:
        if self._use_tiktoken:
            return self.enc.encode(text)
        ids = []
        for tok in text.split():
            if tok not in self.basic_vocab:
                if self.next_id >= self.vocab_size - 1:
                    tok = "<unk>"
                else:
                    self.basic_vocab[tok] = self.next_id
                    self.next_id += 1
            ids.append(self.basic_vocab.get(tok, 0))
        ids.append(self.basic_vocab["<eos>"])
        return ids

    def decode(self, ids: list[int]) -> str:  # pragma: no cover simple
        if self._use_tiktoken:
            return self.enc.decode(ids)
        inv = {v: k for k, v in self.basic_vocab.items()}
        return " ".join(inv.get(i, "<unk>") for i in ids)


# ----------------------
# KD Dataset
# ----------------------
class KDJsonlDataset(Dataset):
    """Dataset for KD/SFT that loads from a manifest or direct path.

    Supports 'messages' format: [{"role": "human", ...}, {"role": "assistant", ...}]
    """

    def __init__(self, path: str, tokenizer: GPT2LikeTokenizer, max_seq: int, mask_prompt: bool = True):
        self.path = Path(path)
        self.tokenizer = tokenizer
        self.max_seq = max_seq
        self.mask_prompt = mask_prompt
        self.samples: list[dict] = []

        # Check if path is a manifest (json) or a direct dataset (jsonl)
        if self.path.suffix == '.json':
            self._load_from_manifest()
        else:
            self._load_jsonl(self.path)

    def _load_from_manifest(self):
        try:
            manifest = json.loads(self.path.read_text(encoding='utf-8'))
            splits = manifest.get("splits", {})
            # Load train split
            for entry in splits.get("train", []):
                file_path = Path(entry.get("path", ""))
                if file_path.exists():
                    self._load_jsonl(file_path)
                else:
                    print(f"Warning: Dataset file not found: {file_path}")
        except Exception as e:
            print(f"Error loading manifest {self.path}: {e}")

    def _load_jsonl(self, path: Path):
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    self.samples.append(obj)
                except json.JSONDecodeError:
                    continue

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        ex = self.samples[idx]

        # Handle 'messages' format
        if "messages" in ex:
            messages = ex["messages"]
            prompt = ""
            target = ""
            for msg in messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "human":
                    prompt += f"Human: {content}\n"
                elif role == "assistant":
                    target += f"Assistant: {content}\n"
            if not target:
                target = " "
        else:
            # Fallback to old format
            prompt = ex.get("prompt", "")
            target = ex.get("target", "")

        modality = ex.get("modality", "unknown")

        # Tokenize
        prompt_ids = self.tokenizer.encode(prompt)
        target_ids = self.tokenizer.encode(target)

        # Truncate prompt if needed to fit at least some target
        # Reserve space for target (at least 1 token)
        max_prompt_len = self.max_seq - len(target_ids)
        if max_prompt_len < 0:
             # Target is too long, truncate target
             target_ids = target_ids[:self.max_seq]
             prompt_ids = []
        elif len(prompt_ids) > max_prompt_len:
             # Truncate prompt from left (keep recent)
             prompt_ids = prompt_ids[-max_prompt_len:]

        input_ids = prompt_ids + target_ids

        labels = [-100] * len(prompt_ids) + target_ids if self.mask_prompt else prompt_ids + target_ids

        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "labels": torch.tensor(labels, dtype=torch.long),
            "modality": modality,
        }


def _collate(batch: list[dict]) -> dict[str, torch.Tensor]:
    max_len = max(len(x["input_ids"]) for x in batch)
    input_ids_list = []
    labels_list = []
    modalities: list[str] = []
    for ex in batch:
        pad_len = max_len - len(ex["input_ids"])
        input_ids_list.append(F.pad(ex["input_ids"], (0, pad_len), value=0))
        labels_list.append(F.pad(ex["labels"], (0, pad_len), value=-100))
        if 'modality' in ex:
            modalities.append(ex['modality'])
    return {
        "input_ids": torch.stack(input_ids_list, dim=0),
        "labels": torch.stack(labels_list, dim=0),
        "modalities": modalities,
    }


# ----------------------
# EMA Teacher Utilities
# ----------------------
def create_ema_teacher(model: nn.Module, device: str) -> nn.Module:
    ema = type(model)(model.config)  # fresh instance
    ema.load_state_dict(model.state_dict())
    ema = ema.to(device)
    for p in ema.parameters():
        p.requires_grad_(False)
    ema.eval()
    return ema


@torch.no_grad()
def update_ema(ema: nn.Module, student: nn.Module, decay: float):
    for (_n1, p_ema), (_, p_stu) in zip(ema.named_parameters(), student.named_parameters()):
        if p_ema.data.shape != p_stu.data.shape:
            continue
        p_ema.data.mul_(decay).add_(p_stu.data, alpha=1 - decay)


# ----------------------
# Scheduler Helpers
# ----------------------
def linear_warmup_cosine_decay(step: int, total: int, warmup: int, min_lr_scale: float = 0.1) -> float:
    if step < warmup:
        return step / max(1, warmup)
    progress = (step - warmup) / max(1, total - warmup)
    return min_lr_scale + 0.5 * (1 + math.cos(math.pi * progress)) * (1 - min_lr_scale)


def kl_weight(step: int, total: int, final_w: float, warmup_ratio: float) -> float:
    ramp_steps = int(total * warmup_ratio)
    if ramp_steps == 0:
        return final_w
    return final_w * min(1.0, step / ramp_steps)


# ----------------------
# Main Training Entry
# ----------------------
def run_kd_sft(config: KDConfig) -> None:
    """Run KD + SFT adaptive training.

    Refactored to delegate discrete concerns to helper functions for reduced
    cognitive complexity while preserving exact prior behavior.
    """
    # ---------------- Inner Helpers (pure / side-effect isolated) -----------------
    def _apply_env_overrides(cfg: KDConfig) -> dict:
        env_map = {  # (same mapping as previous inline logic)
            "IC_MAX_STEPS": ("max_steps", int),
            "IC_LOG_EVERY": ("log_every", int),
            "IC_SAVE_EVERY": ("save_every", int),
            "IC_EVAL_EVERY": ("eval_every", int),
            "IC_ACCUM_STEPS": ("accum_steps", int),
            "IC_LR": ("lr", float),
            "IC_WARMUP_STEPS": ("warmup_steps", int),
            "IC_SEQ_LEN": ("max_seq_length", int),
            "IC_SHORT_SEQ_LEN": ("short_seq_len", int),
            "IC_SHORT_SEQ_STEPS": ("short_seq_steps", int),
            "IC_KL_FINAL": ("kl_final_weight", float),
            "IC_KL_WARMUP_RATIO": ("kl_warmup_ratio", float),
            "IC_EMA_DECAY": ("ema_decay", float),
            "IC_HEEL_EFF_RATIO": ("heel_eff_ratio", float),
            "IC_HEEL_MIN_WINDOWS": ("heel_min_windows", int),
            "IC_HEEL_HOLD_CONSEC": ("heel_hold_consec", int),
            "IC_HEEL_CURV_TOL": ("heel_curvature_tol", float),
            "IC_HEEL_VAR_RATIO_MAX": ("heel_var_ratio_max", float),
            "IC_HEEL_MIN_EFF_FLOOR": ("heel_min_eff_floor", float),
            "IC_HEEL_PEAK_DECAY": ("heel_peak_decay", float),
            "IC_ENABLE_HEEL_STOP": ("enable_heel_stop", lambda v: v.lower() in ("1","true","yes")),
            "IC_PHASE2_AFTER_HEEL": ("enable_phase2_after_heel", lambda v: v.lower() in ("1","true","yes")),
            "IC_PHASE2_EXTRA_STEPS": ("phase2_extra_steps", int),
            "IC_PHASE2_LR_SCALE": ("phase2_lr_scale", float),
            "IC_PHASE2_KL_TAPER_STEPS": ("phase2_kl_taper_steps", int),
            "IC_PHASE2_DISABLE_KL": ("phase2_disable_kl", lambda v: v.lower() in ("1","true","yes")),
            "IC_PHASE2_EXPERT_SCALE": ("phase2_expert_scale", float),
            "IC_RUNTIME_OVERRIDES_PATH": ("runtime_override_path", str),
            "IC_STATUS_SNAPSHOT_EVERY": ("status_snapshot_every", int),
            # Newly added: allow changing output directory via environment for clearer separation of runs
            "IC_OUTPUT_DIR": ("output_dir", str),
            # New optimization & instrumentation flags
            "IC_LOG_MODALITY_MIX": ("log_modality_mix", lambda v: v.lower() in ("1","true","yes")),
            "IC_MODALITY_BALANCE_ENABLE": ("modality_balance_enable", lambda v: v.lower() in ("1","true","yes")),
            "IC_MODALITY_IMBALANCE_WARN_RATIO": ("modality_imbalance_warn_ratio", float),
            "IC_KL_ADAPT_ENABLE": ("kl_adapt_enable", lambda v: v.lower() in ("1","true","yes")),
            "IC_KL_ADAPT_WINDOW": ("kl_adapt_window", int),
            "IC_KL_ADAPT_IMPROVE_THRESHOLD": ("kl_adapt_improve_threshold", float),
            "IC_KL_ADAPT_MIN_RAMP_REDUCTION": ("kl_adapt_min_ramp_reduction", float),
            "IC_PHASE2_AUTO_STOP_ENABLE": ("phase2_auto_stop_enable", lambda v: v.lower() in ("1","true","yes")),
            "IC_PHASE2_AUTO_STOP_PATIENCE": ("phase2_auto_stop_patience", int),
            "IC_PHASE2_AUTO_STOP_MIN_IMPROVE": ("phase2_auto_stop_min_improve", float),
            "IC_AUTO_ENABLE_CHECKPOINTING": ("auto_enable_checkpointing", lambda v: v.lower() in ("1","true","yes")),
            "IC_CHECKPOINTING_UTIL_THRESHOLD": ("checkpointing_utilization_threshold", float),
        }
        applied = {}
        for env_key, (attr, cast_fn) in env_map.items():
            if env_key in os.environ and os.environ[env_key].strip():
                try:
                    old_val = getattr(cfg, attr)
                    new_val = cast_fn(os.environ[env_key])
                    setattr(cfg, attr, new_val)
                    applied[attr] = (old_val, new_val)
                except Exception as e:  # pragma: no cover
                    print(f"[KD][EnvOverride][WARN] Failed to apply {env_key}: {e}")
        return applied

    def _prepare_data(cfg: KDConfig):
        tokenizer = GPT2LikeTokenizer()
        dataset = KDJsonlDataset(cfg.manifest_path, tokenizer, cfg.max_seq_length, mask_prompt=cfg.mask_prompt_loss)
        dataloader = DataLoader(dataset, batch_size=cfg.micro_batch, shuffle=True, drop_last=False, collate_fn=_collate, num_workers=0)
        return tokenizer, dataset, dataloader

    def _build_model(cfg: KDConfig):
        model_cfg = B3Config()
        if os.environ.get("IC_SMOKE_MODEL", "0") == "1":
            model_cfg.embed_dim = 384
            model_cfg.num_heads = 6
            model_cfg.num_layers = min(4, model_cfg.num_layers)
            model_cfg.num_experts = min(2, model_cfg.num_experts)
            model_cfg.expert_dim = min(512, model_cfg.expert_dim)
            model_cfg.experts_per_token = 1
            model_cfg.use_gradient_checkpointing = False
            print("[KD][SmokeModel] Activated reduced model configuration (embed_dim=384,layers=4,experts=2,expert_dim=512,heads=6,checkpointing=OFF).")
        model = ImpressionCoreB3Model(model_cfg).to(cfg.device)
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        print(f"[KD] Model: ImpressionCoreB3 | total_params={total_params/1e6:.2f}M trainable={trainable_params/1e6:.2f}M layers={len(model.layers)} vocab={model_cfg.vocab_size}")
        print(f"[KD] ModelConfig: embed_dim={model_cfg.embed_dim} heads={model_cfg.num_heads} experts={model_cfg.num_experts} exp_per_tok={model_cfg.experts_per_token} seq_max={cfg.max_seq_length}")
        return model, model_cfg

    def _load_base_checkpoint(model, cfg: KDConfig):
        if os.environ.get("IC_SMOKE_MODEL", "0") == "1":
            print("[KD] Skipping base checkpoint load in smoke model mode.")
            return
        p = Path(cfg.base_checkpoint)
        if not p.exists():
            print("[KD] Base checkpoint not found; training from scratch initialization.")
            return
        try:
            try:
                ckpt = torch.load(str(p), map_location="cpu", weights_only=True)
            except TypeError:
                ckpt = torch.load(str(p), map_location="cpu")
            state_dict = ckpt.get("model_state_dict", ckpt)
            missing, unexpected = model.load_state_dict(state_dict, strict=False)
            print(f"[KD] Loaded base checkpoint. Missing={len(missing)} Unexpected={len(unexpected)}")
        except Exception as e:
            print(f"[KD] Warning: failed to load checkpoint ({e}); proceeding with fresh init.")

    def _create_optimizer_scaler(model, cfg: KDConfig):
        use_bnb = False
        try:
            import bitsandbytes as bnb
            use_bnb = True
        except ImportError:
            pass

        if use_bnb:
            print("[KD] Using bitsandbytes 8-bit AdamW optimizer.")
            optimizer = bnb.optim.AdamW8bit(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
        else:
            print("[KD] Using standard torch.optim.AdamW.")
            optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)

        try:
            scaler = torch.amp.GradScaler(enabled=cfg.fp16 and torch.cuda.is_available())
        except AttributeError:
            scaler = torch.cuda.amp.GradScaler(enabled=cfg.fp16 and torch.cuda.is_available())
        return optimizer, scaler

    def _maybe_create_ema(model, cfg: KDConfig):
        if cfg.ema_decay <= 0:
            return None
        return create_ema_teacher(model, cfg.device)

    def _init_metrics_csv(cfg: KDConfig):
        path = Path(cfg.output_dir) / "training_metrics.csv"
        write_header = not path.exists()
        try:
            fh = open(path, 'a', encoding='utf-8')
            if write_header:
                # Added memory + optional throughput + rolling CE improvement columns
                fh.write("step,total,raw_ce,kl,beta,kl_ratio,exp_ratio,eff_ema,eff_peak,token_eff,eff_ratio,curvature,var_ratio,heel_cand,lr,seq_len,cuda_alloc_MB,cuda_reserved_MB,cuda_max_alloc_MB,tok_per_sec,ce_improve_pct\n")
            return fh
        except Exception as e:
            print(f"[KD][Metrics][WARN] Cannot open metrics CSV: {e}")
            return None

    def apply_runtime_overrides(cfg: KDConfig, last_mtime: float) -> float:
        """Public helper (unit-testable) to apply runtime overrides file if modified.
        Returns new mtime (or original if unchanged)."""
        if not cfg.runtime_override_path:
            return last_mtime
        try:
            ov_path = Path(cfg.runtime_override_path)
            if not ov_path.is_absolute():
                ov_path = Path(cfg.output_dir) / cfg.runtime_override_path
            if ov_path.exists():
                mtime = ov_path.stat().st_mtime
                if mtime > last_mtime:
                    with ov_path.open('r', encoding='utf-8') as f:
                        data = json.load(f)
                    applied = []
                    for k, v in data.items():
                        if hasattr(cfg, k):
                            try:
                                oldv = getattr(cfg, k)
                                setattr(cfg, k, v)
                                applied.append((k, oldv, v))
                            except Exception:
                                pass
                    if applied:
                        print(f"[KD][RuntimeOverride] Applied overrides: {applied}")
                    return mtime
        except Exception as e:
            print(f"[KD][RuntimeOverride][WARN] {e}")
        return last_mtime

    # ------------------- Original Top-Level Logic (simplified) --------------------
    random.seed(config.seed)
    torch.manual_seed(config.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(config.seed)
    applied_overrides = _apply_env_overrides(config)

    banner_time = now_ts()
    print("=" * 88)
    print(f"[KD] ImpressionCore KD+SFT Training | Version: {TRAIN_IMPL_VERSION} | Start: {banner_time}")
    print("=" * 88)
    print("[KD] Starting KD+SFT Phase with config:")
    print(json.dumps(asdict(config), indent=2))
    if applied_overrides:
        for k, (ov, nv) in applied_overrides.items():
            print(f"[KD][EnvOverride] {k}: {ov} -> {nv}")

    # Optional fast debug overrides (lowest friction to confirm loop progress)
    if os.environ.get("IC_FAST_DEBUG", "0") == "1":
        print("[KD][FastDebug] Activating fast debug overrides: seq_len=256, max_steps=2, accum_steps=1, disable KL+EMA", flush=True)
        config.max_seq_length = min(256, config.max_seq_length)
        config.short_seq_len = min(256, config.short_seq_len)
        config.short_seq_steps = config.max_steps  # keep short for entire run
        config.max_steps = min(2, config.max_steps)
        config.accum_steps = 1
        config.kl_final_weight = 0.0
        config.ema_decay = 0.0  # signals to skip EMA updates
        config.enable_heel_stop = False

    if not Path(config.manifest_path).exists():
        print(f"[KD][FATAL] Manifest missing: {config.manifest_path}")
        return

    # Prepare tokenizer & dataset
    tokenizer, dataset, dataloader = _prepare_data(config)
    # Modality distribution baseline summary (data condensation diagnostics)
    if config.log_modality_mix:
        modality_counts = {}
        for s in dataset.samples:  # lightweight single pass
            m = s.get('modality', 'unknown')
            modality_counts[m] = modality_counts.get(m, 0) + 1
        total_samples = sum(modality_counts.values()) or 1
        print("[KD][ModalityBaseline] distribution=" + ", ".join(f"{k}:{v}({v/total_samples*100:.1f}%)" for k,v in sorted(modality_counts.items())))
        if len(modality_counts) > 1:
            max_c = max(modality_counts.values())
            min_c = min(modality_counts.values())
            if min_c > 0 and (max_c / min_c) > config.modality_imbalance_warn_ratio:
                print(f"[KD][ModalityBaseline][WARN] Imbalance ratio {(max_c/min_c):.2f} exceeds {config.modality_imbalance_warn_ratio}. Consider targeted condensation or upsampling.")

    # Model config: align with architecture default (39M base assumptions)
    model, model_cfg = _build_model(config)
    model_param_millions = sum(p.numel() for p in model.parameters()) / 1e6
    print(f"[KD] Dataset size: {len(dataset)} records | Micro batch {config.micro_batch} * Accum {config.accum_steps} => Effective batch {config.micro_batch * config.accum_steps}")
    print(f"[KD] Device: {config.device} | FP16: {config.fp16 and torch.cuda.is_available()} | Max steps: {config.max_steps}")
    print(f"[KD] Model: ImpressionCoreB3Model | Params: {model_param_millions:.2f}M | Gradient Checkpointing: {model_cfg.use_gradient_checkpointing}")

    # Attempt checkpoint load
    _load_base_checkpoint(model, config)

    # EMA teacher
    ema_teacher = _maybe_create_ema(model, config)
    optimizer, scaler = _create_optimizer_scaler(model, config)

    total_steps = config.max_steps
    global_step = 0
    # Phase2 runtime state
    phase2_active = False
    phase2_start_step = None
    phase2_end_step = None
    running_loss = 0.0
    running_kl = 0.0
    running_ce = 0.0
    start_time = time.time()

    Path(config.output_dir).mkdir(parents=True, exist_ok=True)

    # Resume support: if IC_RESUME_CKPT is set, load model/ema/global_step
    resume_ckpt = os.environ.get("IC_RESUME_CKPT")
    if resume_ckpt and Path(resume_ckpt).exists():
        try:
            ckpt = torch.load(resume_ckpt, map_location="cpu")
            model.load_state_dict(ckpt["model_state_dict"], strict=False)
            if ckpt.get("ema_teacher_state_dict") and config.ema_decay > 0:
                if ema_teacher is None:
                    ema_teacher = create_ema_teacher(model, config.device)
                ema_teacher.load_state_dict(ckpt["ema_teacher_state_dict"], strict=False)
            if "global_step" in ckpt:
                global_step = int(ckpt["global_step"])
            print(f"[KD][Resume] Loaded checkpoint {resume_ckpt} starting at step {global_step}.")
        except Exception as e:
            print(f"[KD][Resume][WARN] Failed to resume from {resume_ckpt}: {e}")

    # Metrics CSV
    metrics_csv = _init_metrics_csv(config)

    model.train()

    def evaluate(sample_batches: int = 4):  # light eval with explicit CE + KL
        model.eval()
        ce_acc = 0.0
        kl_acc = 0.0
        tok_count = 0
        with torch.no_grad():
            for i, batch in enumerate(dataloader):
                if i >= sample_batches:
                    break
                input_ids = batch["input_ids"].to(config.device)
                labels = batch["labels"].to(config.device)
                # Truncate dynamically same as training first steps conceptually (use max_seq_length here for eval consistency)
                cur_max = min(config.max_seq_length, input_ids.size(1))
                input_ids = input_ids[:, :cur_max]
                labels = labels[:, :cur_max]
                out = model(input_ids=input_ids, labels=None)
                logits = out["logits"]
                expert_loss_raw = out.get("expert_loss", torch.tensor(0.0, device=config.device))
                if not isinstance(expert_loss_raw, torch.Tensor):
                    expert_loss_raw = torch.tensor(float(expert_loss_raw), device=config.device)
                # Shift
                if logits.size(1) < 2:
                    continue
                shift_logits = logits[:, :-1, :].contiguous()
                shift_labels = labels[:, 1:].contiguous()
                # CE with ignore_index
                raw_ce = F.cross_entropy(
                    shift_logits.view(-1, shift_logits.size(-1)),
                    shift_labels.view(-1),
                    ignore_index=-100,
                    reduction='sum'
                )
                # Distillation KL on supervised positions
                mask = shift_labels != -100
                if mask.any() and ema_teacher is not None and config.kl_final_weight > 0:
                    student_logits_masked = shift_logits[mask]
                    with torch.no_grad():
                        teacher_out = ema_teacher(input_ids=input_ids, labels=None)
                        teacher_logits = teacher_out["logits"][:, :-1, :].contiguous()[mask]
                    T = config.kl_temperature
                    student_logp = F.log_softmax(student_logits_masked / T, dim=-1)
                    teacher_p = F.softmax(teacher_logits / T, dim=-1)
                    sample_kl = F.kl_div(student_logp, teacher_p, reduction="batchmean") * (T * T)
                else:
                    sample_kl = torch.tensor(0.0, device=config.device)
                ce_acc += raw_ce.item()
                kl_acc += sample_kl.item()
                tok_count += mask.sum().item()
        model.train()
        if tok_count == 0:
            print("[KD][Eval] No supervised tokens in eval sample.")
            return
        avg_ce = ce_acc / tok_count
        try:
            ppl = math.exp(avg_ce) if avg_ce < 20 else float('inf')
        except OverflowError:
            ppl = float('inf')
        ppl_str = 'inf' if ppl == float('inf') else f"{ppl:.2f}"
        print(f"[KD][Eval] ce={avg_ce:.4f} kl={kl_acc/max(1,sample_batches):.4f} ppl={ppl_str} supervised_tok={tok_count}")

    # Training Loop
    dataloader_iter = iter(dataloader)
    optimizer.zero_grad()
    accum_counter = 0
    # Aggregate supervised tokens across micro-batches before an optimizer step
    supervised_tokens_micro_total = 0
    # Aggregate supervised tokens across steps within a logging window
    supervised_tok_window = 0

    early_stop_triggered = False
    last_override_mtime: float = 0.0
    # Instrumentation state for modality and adaptive KL
    modality_window_counts: dict[str,int] = {}
    first_window_ce: float | None = None
    kl_adapt_applied = False
    # Phase2 marginal gain tracking
    phase2_baseline_ce: float | None = None
    phase2_non_improve_streak = 0
    while global_step < total_steps:
        try:
            batch = next(dataloader_iter)
        except StopIteration:
            dataloader_iter = iter(dataloader)
            batch = next(dataloader_iter)

        input_ids = batch["input_ids"].to(config.device, non_blocking=True)
        labels = batch["labels"].to(config.device, non_blocking=True)
        batch_modalities = batch.get("modalities", [])

        # Dynamic sequence curriculum
        current_max_len = config.short_seq_len if global_step < config.short_seq_steps else config.max_seq_length
        if input_ids.size(1) > current_max_len:
            input_ids = input_ids[:, :current_max_len]
            labels = labels[:, :current_max_len]

        try:
            autocast_ctx = torch.amp.autocast('cuda', enabled=config.fp16 and torch.cuda.is_available())
        except TypeError:
            # Fallback older API
            autocast_ctx = torch.cuda.amp.autocast(enabled=config.fp16 and torch.cuda.is_available())
        with autocast_ctx:
            if global_step == 0 and accum_counter == 0:
                print("[KD][Debug] Entering first forward pass...", flush=True)
            outputs = model(input_ids=input_ids, labels=None)  # avoid internal loss, get logits + expert_loss
            logits = outputs["logits"]
            expert_loss_raw = outputs.get("expert_loss", torch.tensor(0.0, device=config.device))
            if not isinstance(expert_loss_raw, torch.Tensor):
                expert_loss_raw = torch.tensor(float(expert_loss_raw), device=config.device)

            # Shift for autoregressive CE
            if logits.size(1) < 2:
                continue  # skip extremely short
            shift_logits = logits[:, :-1, :].contiguous()
            shift_labels = labels[:, 1:].contiguous()
            raw_ce = F.cross_entropy(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1),
                ignore_index=-100,
                reduction='mean'
            )
            scaled_expert = expert_loss_raw * config.expert_loss_scale
            ce_loss = raw_ce + scaled_expert

            # Distillation (EMA teacher)
            if ema_teacher is not None:
                with torch.no_grad():
                    teacher_out = ema_teacher(input_ids=input_ids, labels=None)
                    teacher_logits = teacher_out["logits"].detach()
            else:
                teacher_logits = logits.detach()  # self reference (KL weight likely 0 in fast debug)

            # Mask positions where labels == -100 to reduce compute
            mask = shift_labels != -100
            if mask.any():
                student_logits = shift_logits[mask]
                teacher_logits_masked = teacher_logits[:, :-1, :].contiguous()[mask]
                T = config.kl_temperature
                student_logp = F.log_softmax(student_logits / T, dim=-1)
                teacher_p = F.softmax(teacher_logits_masked / T, dim=-1)
                kl = F.kl_div(student_logp, teacher_p, reduction="batchmean") * (T * T)
            else:
                kl = torch.tensor(0.0, device=config.device)

            # Compute KL weight with possible Phase2 taper override
            base_beta = kl_weight(global_step + 1, total_steps, config.kl_final_weight, config.kl_warmup_ratio)
            if phase2_active and config.phase2_disable_kl and phase2_start_step is not None:
                # linearly decay from base_beta at phase2 start to 0 across taper steps
                delta = global_step - phase2_start_step
                if delta <= config.phase2_kl_taper_steps:
                    decay_factor = max(0.0, 1.0 - (delta / max(1, config.phase2_kl_taper_steps)))
                    beta = base_beta * decay_factor
                else:
                    beta = 0.0
            else:
                beta = base_beta
            loss = ce_loss + beta * kl

        if not torch.isfinite(loss):
            print(f"[KD][FATAL] Non-finite loss encountered (loss={loss.item()}, ce={ce_loss.item()}, kl={kl.item()}); aborting.")
            break
        # ---------------- BACKWARD & OPTIMIZATION (moved inside loop) ----------------
        # Debug: memory + timing around backward
        if torch.cuda.is_available():
            alloc_before = torch.cuda.memory_allocated()/1024**2
        t_bw_start = time.time()
        scaler.scale(loss / config.accum_steps).backward()
        t_bw = time.time() - t_bw_start
        if torch.cuda.is_available():
            alloc_after = torch.cuda.memory_allocated()/1024**2
            print(f"[KD][Debug] Micro-batch backward done (accum_index={accum_counter+1}/{config.accum_steps}) time={t_bw:.2f}s mem {alloc_before:.0f}MB→{alloc_after:.0f}MB", flush=True)
        accum_counter += 1
        running_loss += loss.item()
        running_kl += kl.item()
        running_ce += raw_ce.item()
        supervised_tokens_micro_total += (shift_labels != -100).sum().item()

        if accum_counter >= config.accum_steps:
            # LR schedule
            lr_scale = linear_warmup_cosine_decay(global_step, total_steps, config.warmup_steps)
            lr_base = config.lr * lr_scale
            if phase2_active:
                lr_base *= config.phase2_lr_scale
            for pg in optimizer.param_groups:
                pg["lr"] = lr_base

            # Debug: pre-step grad norm / memory
            if torch.cuda.is_available():
                print(f"[KD][Debug] Optimizer step start mem={torch.cuda.memory_allocated()/1024**2:.0f}MB", flush=True)
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad(set_to_none=True)
            accum_counter = 0
            if torch.cuda.is_available():
                torch.cuda.synchronize()
                print(f"[KD][Debug] Optimizer step complete mem={torch.cuda.memory_allocated()/1024**2:.0f}MB", flush=True)

            # EMA update after optimizer
            if ema_teacher is not None and (global_step % config.ema_update_interval) == 0:
                update_ema(ema_teacher, model, decay=config.ema_decay)

            # Finalize step token stats
            supervised_tok_window += supervised_tokens_micro_total
            supervised_tokens_micro_total = 0

            global_step += 1

            if global_step % config.log_every == 0:
                elapsed = time.time() - start_time
                supervised_tok = supervised_tok_window
                mem_mb = torch.cuda.memory_allocated()/1024**2 if torch.cuda.is_available() else 0.0
                pre_reset_total = running_loss / config.log_every
                pre_reset_raw_ce = running_ce / config.log_every
                pre_reset_kl = running_kl / config.log_every
                kl_ratio = pre_reset_kl / (pre_reset_raw_ce + 1e-8)
                expert_ratio = scaled_expert.item() / (raw_ce.item() + 1e-8) if 'scaled_expert' in locals() else 0.0
                print(
                    f"[KD][Step {global_step}/{total_steps}] total={pre_reset_total:.4f} "
                    f"raw_ce={pre_reset_raw_ce:.4f} kl={pre_reset_kl:.4f} "
                    f"beta={beta:.3f} lr={optimizer.param_groups[0]['lr']:.2e} kl_ratio={kl_ratio:.3f} exp_ratio={expert_ratio:.3f} "
                    f"tok/s={supervised_tok/elapsed:.1f} mem={mem_mb:.0f}MB seq_len={current_max_len}"
                )
                # Window CE baseline capture for adaptive KL schedule
                if first_window_ce is None:
                    first_window_ce = pre_reset_raw_ce
                # Track modality mix for this window
                if config.log_modality_mix and batch_modalities:
                    for m in batch_modalities:
                        modality_window_counts[m] = modality_window_counts.get(m,0)+1
                # Print modality mix at window boundary
                if config.log_modality_mix and modality_window_counts:
                    total_mw = sum(modality_window_counts.values()) or 1
                    mix_str = " ".join(f"{k}:{v/total_mw*100:.1f}%" for k,v in sorted(modality_window_counts.items()))
                    print(f"[KD][ModalityWindow] {mix_str}")
                    modality_window_counts.clear()

                # ---------------- Instrumentation (refactored heel logic - dynamic load) ----------------
                heel_mod = _load_heel_helpers()
                if not hasattr(run_kd_sft, "_instr"):
                    run_kd_sft._instr = heel_mod.init_heel_state()
                instr = run_kd_sft._instr
                heel_cfg_view = heel_mod.HeelConfigView(
                    heel_min_windows=config.heel_min_windows,
                    heel_min_eff_floor=config.heel_min_eff_floor,
                    heel_eff_ratio=config.heel_eff_ratio,
                    heel_curvature_tol=config.heel_curvature_tol,
                    heel_var_ratio_max=config.heel_var_ratio_max,
                    heel_peak_decay=config.heel_peak_decay,
                    heel_hold_consec=config.heel_hold_consec,
                )
                metrics = heel_mod.update_heel_metrics(
                    instr,
                    heel_cfg_view,
                    pre_reset_raw_ce=pre_reset_raw_ce,
                    supervised_tok=supervised_tok,
                )
                token_eff = metrics["token_eff"]
                eff_ratio = metrics["eff_ratio"]
                curvature = metrics["curvature"]
                var_ratio = metrics["var_ratio"]
                heel_cand = metrics["heel_cand"]
                cand_reasons = metrics["cand_reasons"]
                print(
                    f"[KD][Instr] win={instr['windows']} token_eff={token_eff:.6f} eff_ema={instr['eff_ema']:.6f} "
                    f"eff_peak={instr['eff_peak']:.6f} eff_ratio={eff_ratio:.3f} curvature={curvature:.2e} var_ratio={var_ratio:.3f} heel_cand={int(heel_cand)}"
                )
                if os.environ.get("IC_HEEL_VERBOSE", "0") == "1":
                    print(f"[KD][HeelDbg] supervised_tok={supervised_tok} cand_reasons={cand_reasons}")
                if metrics_csv is not None:
                    try:
                        # Capture CUDA memory stats (graceful fallback if unavailable)
                        cuda_alloc = cuda_reserved = cuda_max = 0.0
                        try:
                            if torch.cuda.is_available():
                                cuda_alloc = torch.cuda.memory_allocated() / (1024**2)
                                cuda_reserved = torch.cuda.memory_reserved() / (1024**2)
                                cuda_max = torch.cuda.max_memory_allocated() / (1024**2)
                        except Exception:
                            pass
                        # Throughput (tokens/sec) for last logging interval (already computed earlier as supervised_tok/elapsed)
                        tok_per_sec = 0.0
                        try:
                            if 'elapsed' in locals() and elapsed > 0:
                                tok_per_sec = supervised_tok / elapsed
                        except Exception:
                            pass
                        # Rolling CE improvement percentage vs window-average baseline
                        ce_improve_pct = ''
                        if config.rolling_ce_improve_window > 0:
                            if not hasattr(run_kd_sft, '_ce_hist'):
                                run_kd_sft._ce_hist = []  # type: ignore[attr-defined]
                            hist = run_kd_sft._ce_hist  # type: ignore[attr-defined]
                            hist.append(pre_reset_raw_ce)
                            if len(hist) > config.rolling_ce_improve_window:
                                del hist[0:len(hist)-config.rolling_ce_improve_window]
                            if len(hist) == config.rolling_ce_improve_window:
                                first = hist[0]
                                if first > 0:
                                    ce_improve_pct = f"{(first - pre_reset_raw_ce)/first*100:.2f}"
                        metrics_csv.write(
                            f"{global_step},{pre_reset_total:.6f},{pre_reset_raw_ce:.6f},{pre_reset_kl:.6f},{beta:.6f},{kl_ratio:.6f},{expert_ratio:.6f},"
                            f"{instr['eff_ema']:.6f},{instr['eff_peak']:.6f},{token_eff:.6f},{eff_ratio:.6f},{curvature:.6e},{var_ratio:.6f},{int(heel_cand)},{optimizer.param_groups[0]['lr']:.6e},{current_max_len},{cuda_alloc:.1f},{cuda_reserved:.1f},{cuda_max:.1f},{tok_per_sec:.2f},{ce_improve_pct}\n"
                        )
                        # Optional periodic auto-comparison (lightweight):
                        # Controlled via env vars:
                        #   IC_AUTO_COMPARE_EVERY = N (windows) and IC_COMPARE_BASE=path_to_baseline_run
                        # Executes only after window update and on window boundaries to limit overhead.
                        try:
                            auto_every = int(os.environ.get("IC_AUTO_COMPARE_EVERY", "0"))
                        except ValueError:
                            auto_every = 0
                        windows_ok = instr.get('windows',0) >= max(config.auto_compare_min_windows, 1)
                        phase2_steps_ok = True
                        if phase2_active and config.auto_compare_min_phase2_steps > 0:
                            heel_step_ref = getattr(run_kd_sft, '_heel_stop_step', None)
                            if heel_step_ref is not None:
                                phase2_steps_ok = (global_step - heel_step_ref) >= config.auto_compare_min_phase2_steps
                            else:
                                phase2_steps_ok = False
                        if auto_every > 0 and windows_ok and (instr.get('windows',0) % auto_every == 0) and phase2_steps_ok:
                            base_run = os.environ.get("IC_COMPARE_BASE")
                            if base_run:
                                try:
                                    import subprocess
                                    import sys
                                    compare_last_n = os.environ.get("IC_COMPARE_LAST_N", "25")
                                    out_path = Path(cfg.output_dir)/f"auto_compare_windows_{instr['windows']}.json"
                                    cmd = [sys.executable, '-m', 'src.training.analysis.compare_heel_runs', '--run-a', base_run, '--run-b', cfg.output_dir, '--last-n', compare_last_n, '--out', str(out_path)]
                                    # Use subprocess without check to avoid raising inside training loop
                                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                    print(f"[KD][AutoCompare] Generated {out_path.name} (windows={instr['windows']})")
                                except Exception as _e:
                                    print(f"[KD][AutoCompare][WARN] {_e}")
                    except Exception:
                        pass
                if (not instr["heel_reported"]) and instr["heel_consec"] >= config.heel_hold_consec:
                    eff_ratio = (token_eff / (instr["eff_peak"] + 1e-12)) if instr["eff_peak"] > 0 else 0.0
                    print(
                        f"[KD][Heel DRY-RUN] WOULD STOP at step {global_step} | eff_ratio={eff_ratio:.3f} "
                        f"token_eff={token_eff:.6f} peak={instr['eff_peak']:.6f} curvature={curvature:.2e} var_ratio={var_ratio:.3f}"
                    )
                    instr["heel_reported"] = True
                # --- Runtime override polling (lightweight) ---
                last_override_mtime = apply_runtime_overrides(config, last_override_mtime)

                # --- Periodic status snapshot ---
                if config.status_snapshot_every > 0 and (global_step % config.status_snapshot_every == 0):
                    try:
                        snap = {
                            'timestamp': now_ts(),
                            'impl_version': TRAIN_IMPL_VERSION,
                            'step': global_step,
                            'total_planned': total_steps,
                            'phase2_active': phase2_active,
                            'phase2_end_step': phase2_end_step,
                            'lr': optimizer.param_groups[0]['lr'],
                            'raw_ce_avg': pre_reset_raw_ce,
                            'kl_avg': pre_reset_kl,
                            'beta': beta,
                            'eff_ema': instr['eff_ema'],
                            'eff_peak': instr['eff_peak'],
                            'heel_cand': bool('heel_consec' in instr and instr.get('heel_consec',0)>0),
                            'config_dyn': {
                                'heel_eff_ratio': config.heel_eff_ratio,
                                'heel_min_windows': config.heel_min_windows,
                                'heel_peak_decay': config.heel_peak_decay,
                                'phase2_extra_steps': config.phase2_extra_steps,
                                'phase2_lr_scale': config.phase2_lr_scale,
                            }
                        }
                        snap_path = Path(config.output_dir)/'status_snapshot_latest.json'
                        with open(snap_path,'w',encoding='utf-8') as sf:
                            json.dump(snap, sf, indent=2)
                        # Optional rolled snapshot
                        rolled = Path(config.output_dir)/f'status_snapshot_step_{global_step}.json'
                        with open(rolled,'w',encoding='utf-8') as rf:
                            json.dump(snap, rf, indent=2)
                    except Exception as e:
                        print(f"[KD][Snapshot][WARN] Failed to write snapshot: {e}")

                if (config.enable_heel_stop and
                    instr.get("heel_reported", False) and
                    not instr.get("heel_stopped", False)):
                    eff_ratio = (token_eff / (instr["eff_peak"] + 1e-12)) if instr["eff_peak"] > 0 else 0.0
                    if eff_ratio <= config.heel_eff_ratio:
                        # Heel confirmed
                        if config.enable_phase2_after_heel and not phase2_active:
                            # Activate Phase2 (continue training)
                            phase2_active = True
                            phase2_start_step = global_step
                            phase2_end_step = global_step + config.phase2_extra_steps
                            phase2_baseline_ce = pre_reset_raw_ce  # baseline for marginal gain tracking
                            print(f"[KD][Phase2] Activating Phase2 refinement at step {global_step} → extra {config.phase2_extra_steps} steps (end @ {phase2_end_step}). KL taper={config.phase2_disable_kl} expert_scale*={config.phase2_expert_scale}")
                            config.expert_loss_scale *= config.phase2_expert_scale
                            total_steps = max(total_steps, phase2_end_step)
                            report = {
                                "timestamp": now_ts(),
                                "impl_version": TRAIN_IMPL_VERSION,
                                "step": global_step,
                                "phase2_activated": True,
                                "phase2_end_step": phase2_end_step,
                                "eff_ratio": eff_ratio,
                                "token_eff": token_eff,
                            }
                            report_path = Path(config.output_dir) / f"heel_phase2_transition_step_{global_step}.json"
                            try:
                                with open(report_path, 'w', encoding='utf-8') as rf:
                                    json.dump(report, rf, indent=2)
                                print(f"[KD][Phase2] Logged transition report → {report_path}")
                            except Exception as e:
                                print(f"[KD][Phase2][WARN] Failed to log transition report: {e}")
                            instr['heel_stopped'] = True  # prevent re-trigger
                        else:
                            # True early stop path
                            report = {
                                "timestamp": now_ts(),
                                "impl_version": TRAIN_IMPL_VERSION,
                                "step": global_step,
                                "windows": instr["windows"],
                                "token_eff": token_eff,
                                "eff_peak": instr["eff_peak"],
                                "eff_ratio": eff_ratio,
                                "curvature": curvature,
                                "var_ratio": var_ratio,
                                "heel_consec": instr["heel_consec"],
                                "criteria": {
                                    "heel_eff_ratio": config.heel_eff_ratio,
                                    "heel_curvature_tol": config.heel_curvature_tol,
                                    "heel_var_ratio_max": config.heel_var_ratio_max,
                                    "heel_min_windows": config.heel_min_windows,
                                    "heel_hold_consec": config.heel_hold_consec,
                                }
                            }
                            report_path = Path(config.output_dir) / f"heel_report_step_{global_step}.json"
                            try:
                                with open(report_path, 'w', encoding='utf-8') as rf:
                                    json.dump(report, rf, indent=2)
                                print(f"[KD][Heel STOP] Saved heel report → {report_path}")
                                # Record heel stop step for downstream logic (auto comparison gating)
                                run_kd_sft._heel_stop_step = global_step
                            except Exception as e:
                                print(f"[KD][Heel STOP][WARN] Failed to write heel report: {e}")
                            ckpt_path = Path(config.output_dir) / f"heel_stop_step_{global_step}.pt"
                            to_save = {
                                "model_state_dict": model.state_dict(),
                                "ema_teacher_state_dict": ema_teacher.state_dict() if ema_teacher is not None else None,
                                "config": asdict(config),
                                "global_step": global_step,
                                "heel_report_path": str(report_path)
                            }
                            try:
                                torch.save(to_save, ckpt_path)
                                print(f"[KD][Heel STOP] Saved heel checkpoint → {ckpt_path}")
                            except Exception as e:
                                print(f"[KD][Heel STOP][WARN] Failed to save heel checkpoint: {e}")
                            print("[KD][Heel STOP] Early stopping at heel sweet spot.")
                            instr["heel_stopped"] = True
                            early_stop_triggered = True
                    else:
                        # Not yet plateau; reset candidate tracking
                        instr["heel_reported"] = False
                        instr["heel_consec"] = 0
                        print(f"[KD][Heel] Eff ratio {eff_ratio:.3f} above threshold (needs <= {config.heel_eff_ratio:.3f}); continuing.")
                instr["last_raw_ce"] = pre_reset_raw_ce
                # --- Runtime adaptive snapshots & overrides ---
                if config.snapshot_windows_interval > 0 and (instr["windows"] % config.snapshot_windows_interval == 0):
                    snap = {
                        "timestamp": now_ts(),
                        "impl_version": TRAIN_IMPL_VERSION,
                        "step": global_step,
                        "windows": instr["windows"],
                        "eff_peak": instr["eff_peak"],
                        "eff_ema": instr["eff_ema"],
                        "last_token_eff": instr.get("last_token_eff"),
                        "lr": optimizer.param_groups[0]['lr'],
                        "phase2_active": phase2_active,
                        "phase2_end_step": phase2_end_step,
                    }
                    try:
                        snap_path = Path(config.output_dir) / f"snapshot_win_{instr['windows']}.json"
                        with open(snap_path, 'w', encoding='utf-8') as sf:
                            json.dump(snap, sf, indent=2)
                        print(f"[KD][Snapshot] Wrote {snap_path}")
                    except Exception as e:
                        print(f"[KD][Snapshot][WARN] Failed snapshot write: {e}")
                # Apply runtime overrides if file present
                try:
                    override_file = Path(config.runtime_override_path)
                    if not override_file.is_absolute():
                        override_file = Path(config.output_dir) / config.runtime_override_path
                    if override_file.exists():
                        with open(override_file, encoding='utf-8') as rf:
                            ov = json.load(rf)
                        applied = []
                        if 'heel_eff_ratio' in ov:
                            old = config.heel_eff_ratio
                            config.heel_eff_ratio = float(ov['heel_eff_ratio'])
                            applied.append(f"heel_eff_ratio {old}->{config.heel_eff_ratio}")
                        if 'phase2_extra_steps' in ov and phase2_active and phase2_end_step is not None:
                            new_extra = int(ov['phase2_extra_steps'])
                            if global_step + new_extra > phase2_end_step:
                                phase2_end_step = global_step + new_extra
                                total_steps = max(total_steps, phase2_end_step)
                                applied.append(f"phase2_end_step extended->{phase2_end_step}")
                        if applied:
                            print(f"[KD][RuntimeOverride] Applied: {applied}")
                except Exception as e:
                    print(f"[KD][RuntimeOverride][WARN] {e}")

                if not hasattr(run_kd_sft, "_ce_avg"):
                    run_kd_sft._ce_avg = pre_reset_raw_ce + 1e-8
                else:
                    avg_prev = run_kd_sft._ce_avg
                    current_avg = pre_reset_raw_ce
                    if avg_prev > 0 and current_avg > config.spike_ratio_threshold * avg_prev:
                        for pg in optimizer.param_groups:
                            new_lr = max(config.min_lr, pg['lr'] * config.lr_backoff_factor)
                            pg['lr'] = new_lr
                        print(f"[KD][Safety] Loss spike detected (raw_ce={current_avg:.4f} > {config.spike_ratio_threshold}x prev_avg={avg_prev:.4f}). LR backoff applied.")
                    run_kd_sft._ce_avg = 0.9 * avg_prev + 0.1 * current_avg

                # --- Adaptive KL warmup compression ---
                if (config.kl_adapt_enable and not kl_adapt_applied and first_window_ce is not None and
                    instr.get('windows',0) >= config.kl_adapt_window and config.kl_warmup_ratio > 0):
                    try:
                        improvement_pct = (first_window_ce - pre_reset_raw_ce)/first_window_ce*100 if first_window_ce>0 else 0.0
                        if improvement_pct < config.kl_adapt_improve_threshold:
                            # Compress remaining ramp
                            original_ratio = config.kl_warmup_ratio
                            remaining_frac = max(0.0, (config.kl_warmup_ratio*total_steps - global_step)/max(1,total_steps))
                            new_remaining = remaining_frac * config.kl_adapt_min_ramp_reduction
                            config.kl_warmup_ratio = min(1.0, (global_step/total_steps) + new_remaining)
                            kl_adapt_applied = True
                            print(f"[KD][KLAdapt] Applied warmup compression: ratio {original_ratio:.3f} -> {config.kl_warmup_ratio:.3f} (improve={improvement_pct:.2f}% < {config.kl_adapt_improve_threshold}%).")
                    except Exception as _e:
                        print(f"[KD][KLAdapt][WARN] {_e}")

                # --- Phase2 marginal gain auto-stop ---
                if phase2_active and config.phase2_auto_stop_enable and phase2_baseline_ce is not None and not early_stop_triggered:
                    try:
                        improvement_vs_base = (phase2_baseline_ce - pre_reset_raw_ce)/phase2_baseline_ce*100 if phase2_baseline_ce>0 else 0.0
                        if improvement_vs_base < config.phase2_auto_stop_min_improve:
                            phase2_non_improve_streak += 1
                        else:
                            phase2_non_improve_streak = 0
                        if phase2_non_improve_streak >= config.phase2_auto_stop_patience:
                            # schedule end next step
                            if phase2_end_step is not None and global_step < phase2_end_step:
                                print(f"[KD][Phase2AutoStop] Insufficient marginal gains (improve={improvement_vs_base:.2f}% < {config.phase2_auto_stop_min_improve}%) for {phase2_non_improve_streak} windows. Scheduling early Phase2 end.")
                                phase2_end_step = global_step + 1
                                total_steps = max(total_steps, phase2_end_step)
                    except Exception as _e:
                        print(f"[KD][Phase2AutoStop][WARN] {_e}")

                # --- Gradient checkpointing auto enable / suggestion ---
                if config.auto_enable_checkpointing and torch.cuda.is_available():
                    try:
                        props = torch.cuda.get_device_properties(0)
                        total_mem = props.total_memory
                        alloc = torch.cuda.memory_allocated()
                        util = alloc / max(1,total_mem)
                        if util > config.checkpointing_utilization_threshold and not getattr(model.config,'use_gradient_checkpointing', False):
                            # Attempt to enable if method exists
                            enabled = False
                            if hasattr(model, 'enable_gradient_checkpointing'):
                                try:
                                    model.enable_gradient_checkpointing()
                                    model.config.use_gradient_checkpointing = True
                                    enabled = True
                                except Exception:
                                    pass
                            if enabled:
                                print(f"[KD][Checkpointing] Enabled gradient checkpointing at utilization {util*100:.1f}%.")
                            else:
                                print(f"[KD][Checkpointing][SUGGEST] Utilization {util*100:.1f}% > threshold {config.checkpointing_utilization_threshold*100:.1f}%. Consider enabling gradient checkpointing.")
                    except Exception as _e:
                        print(f"[KD][Checkpointing][WARN] {_e}")

                running_loss = running_ce = running_kl = 0.0
                supervised_tok_window = 0
                start_time = time.time()

            if early_stop_triggered:
                break
            if global_step % config.eval_every == 0 or global_step == 1:
                evaluate()

            # Phase2 completion condition: extend saving at end
            if early_stop_triggered:
                break
            if global_step % config.save_every == 0 or global_step == total_steps or (phase2_active and global_step == phase2_end_step):
                ckpt_path = Path(config.output_dir) / f"step_{global_step}.pt"
                to_save = {
                    "model_state_dict": model.state_dict(),
                    "ema_teacher_state_dict": ema_teacher.state_dict() if ema_teacher is not None else None,
                    "config": asdict(config),
                    "global_step": global_step,
                }
                torch.save(to_save, ckpt_path)
                print(f"[KD] Saved checkpoint → {ckpt_path}")
                if phase2_active and global_step == phase2_end_step:
                    print(f"[KD][Phase2] Reached scheduled Phase2 end step {phase2_end_step}.")
                    break

    # --- Final Summary Report (Phase2 end or heel early stop) ---
    try:
        instr = getattr(run_kd_sft, '_instr', None)
        event_type = None
        if 'early_stop_triggered' in locals() and early_stop_triggered:
            event_type = 'heel_early_stop'
        elif phase2_active and phase2_end_step is not None and global_step >= phase2_end_step:
            event_type = 'phase2_end'
        if event_type and instr:
            eff_peak = instr.get('eff_peak')
            eff_ema = instr.get('eff_ema')
            last_token_eff = instr.get('last_token_eff')
            last_eff_ratio = 0.0
            if eff_peak and eff_peak > 0 and last_token_eff is not None:
                last_eff_ratio = last_token_eff / (eff_peak + 1e-12)
            summary = {
                'timestamp': now_ts(),
                'impl_version': TRAIN_IMPL_VERSION,
                'event': event_type,
                'global_step': global_step,
                'total_steps_initial': config.max_steps,
                'phase2_active': phase2_active,
                'phase2_end_step': phase2_end_step,
                'eff_peak': eff_peak,
                'eff_ema': eff_ema,
                'last_token_eff': last_token_eff,
                'last_eff_ratio': last_eff_ratio,
                'heel_params': {
                    'heel_eff_ratio': config.heel_eff_ratio,
                    'heel_min_windows': config.heel_min_windows,
                    'heel_hold_consec': config.heel_hold_consec,
                },
                'phase2_params': {
                    'enabled': config.enable_phase2_after_heel,
                    'extra_steps': config.phase2_extra_steps,
                    'lr_scale': config.phase2_lr_scale,
                    'kl_taper_steps': config.phase2_kl_taper_steps,
                    'disable_kl': config.phase2_disable_kl,
                    'expert_scale': config.phase2_expert_scale,
                }
            }
            suffix = 'phase2_end' if event_type == 'phase2_end' else 'heel_early_stop'
            summary_path = Path(config.output_dir) / f"final_training_summary_{suffix}_step_{global_step}.json"
            with open(summary_path, 'w', encoding='utf-8') as sf:
                json.dump(summary, sf, indent=2)
            print(f"[KD][Summary] Wrote final summary report → {summary_path}")
    except Exception as e:
        print(f"[KD][Summary][WARN] Failed to write final summary: {e}")

    print("[KD] Training complete.")
    if 'metrics_csv' in locals() and metrics_csv:
        with contextlib.suppress(Exception):
            metrics_csv.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="Run smoke test")
    args = parser.parse_args()

    if args.smoke:
        print("[KD] Running smoke test...")
        cfg = KDConfig(max_steps=5, log_every=1, eval_every=5, save_every=5, accum_steps=2, short_seq_steps=3)
    else:
        print("[KD] Running full Phase 2 training...")
        cfg = KDConfig() # Use defaults

    run_kd_sft(cfg)
