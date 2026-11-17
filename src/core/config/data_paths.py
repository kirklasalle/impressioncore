#!/usr/bin/env python3
"""
ImpressionCore: Centralized Data & Model Path Configuration

Provides a single source of truth for all F:\ drive paths used across the project.
All modules should import paths from here instead of hardcoding F:\ references.

File: core/config/data_paths.py
Project: ImpressionCore
Created: 2026-07-01
Version: 1.0.0

Authors:
    - Kirk LaSalle <kirk@impressioncore.ai>
    - Antigravity AI Agent

Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Root Paths — Override via environment variables for cross-machine portability
# ─────────────────────────────────────────────────────────────────────────────

# Primary data drive (F:\ on Kirk's workstation)
DATA_DRIVE = Path(os.environ.get("IMPRESSIONCORE_DATA_DRIVE", "F:/"))

# Project root (D:\Projects\impressioncore on Kirk's workstation)
PROJECT_ROOT = Path(os.environ.get(
    "IMPRESSIONCORE_PROJECT_ROOT",
    str(Path(__file__).resolve().parent.parent.parent.parent)
))

# ─────────────────────────────────────────────────────────────────────────────
# Model Paths
# ─────────────────────────────────────────────────────────────────────────────

MODELS_ROOT = DATA_DRIVE / "models"

# Base models (teachers / encoders)
BASE_MODELS = MODELS_ROOT / "base"
BASE_GPT2_SMALL = BASE_MODELS / "gpt2_small"
BASE_CLIP_VIT = BASE_MODELS / "clip-vit-base-patch32"

# Production models (validated, ready to serve)
PRODUCTION_MODELS = MODELS_ROOT / "production"
B3_HOPE_V1_DIR = PRODUCTION_MODELS / "b3_hope_v1"
B3_HOPE_V1_WEIGHTS = B3_HOPE_V1_DIR / "impressioncore_b3_hope.pt"
B3_HOPE_V1_CONFIG = B3_HOPE_V1_DIR / "config.json"
B3_HOPE_V1_METADATA = B3_HOPE_V1_DIR / "metadata.json"
PRODUCTION_CANDIDATES = PRODUCTION_MODELS / "candidates"
PRODUCTION_VALIDATED = PRODUCTION_MODELS / "validated"
PRODUCTION_CURRENT = PRODUCTION_MODELS / "current"

# Checkpoint paths
CHECKPOINTS_ROOT = MODELS_ROOT / "checkpoints"
CHECKPOINT_B3_FULL = CHECKPOINTS_ROOT / "b3_full_training"
CHECKPOINT_B3_CONV = CHECKPOINTS_ROOT / "b3_conversational"
CHECKPOINT_B3_SANITY = CHECKPOINTS_ROOT / "b3_sanity_slim32m"
CHECKPOINT_B3_STRESS = CHECKPOINTS_ROOT / "b3_stress1b_dryrun"
CHECKPOINT_RLM = CHECKPOINTS_ROOT / "rlm"
CHECKPOINT_DISTILLATION = CHECKPOINTS_ROOT / "distillation"
CHECKPOINT_KD_SFT_PHASE2 = CHECKPOINTS_ROOT / "kd_sft_phase2"
CHECKPOINT_DPO_PHASE3 = CHECKPOINTS_ROOT / "dpo_phase3"
CHECKPOINT_DIVERSE_CURRICULUM = CHECKPOINTS_ROOT / "diverse_curriculum"
CHECKPOINT_GRAMMAR = CHECKPOINTS_ROOT / "grammar_specialized"
CHECKPOINT_BUILDER_CLIENT = CHECKPOINTS_ROOT / "builder_client"
CHECKPOINT_DATA_TRAINING = CHECKPOINTS_ROOT / "data_training_checkpoints"
CHECKPOINT_RAW_TRAINING = CHECKPOINTS_ROOT / "raw_training"

# RLM policy checkpoints
RLM_POLICY_BEST = CHECKPOINT_RLM / "policy_best.pth"
RLM_POLICY_FINAL = CHECKPOINT_RLM / "policy_final.pth"
RLM_LOGS = CHECKPOINT_RLM / "logs"

# Training models directory
TRAINING_MODELS = MODELS_ROOT / "training"
TRAINING_ACTIVE = TRAINING_MODELS / "active"
TRAINING_COMPLETED = TRAINING_MODELS / "completed"
TRAINING_CONFIGS = TRAINING_MODELS / "configs"
TRAINING_LOGS = TRAINING_MODELS / "logs"

# Experiments and management
EXPERIMENTS = MODELS_ROOT / "experiments"
MODEL_MANAGEMENT = MODELS_ROOT / "management"
TEACHER_MODELS = MODELS_ROOT / "teachers"
DEPLOYMENT_MODELS = MODELS_ROOT / "deployment"
DISTILLATION_MODELS = MODELS_ROOT / "distillation"

# ─────────────────────────────────────────────────────────────────────────────
# Data Paths
# ─────────────────────────────────────────────────────────────────────────────

DATA_ROOT = DATA_DRIVE / "data"

# Data catalog
DATA_CATALOG_CSV = DATA_ROOT / "data_catalog.csv"

# Dataset categories
DATASETS_ROOT = DATA_ROOT / "datasets"
DATASETS_RAW = DATASETS_ROOT / "raw"
DATASETS_PROCESSED = DATASETS_ROOT / "processed"
DATASETS_AUDIO = DATASETS_ROOT / "audio"
DATASETS_VIDEO = DATASETS_ROOT / "video"
DATASETS_VISION = DATASETS_ROOT / "vision"
DATASETS_ACADEMIC = DATASETS_ROOT / "academic"
DATASETS_EDUCATIONAL = DATASETS_ROOT / "educational"
DATASETS_ENGLISH_GRAMMAR = DATASETS_ROOT / "english-grammar"
DATASETS_EXPERIMENTAL = DATASETS_ROOT / "experimental"
DATASETS_STRUCTURED = DATASETS_ROOT / "structured"
DATASETS_TABULAR = DATASETS_ROOT / "tabular"
DATASETS_TRANSCRIPTS = DATASETS_ROOT / "transcripts"
DATASETS_WEB = DATASETS_ROOT / "web"
DATASETS_KINETICS400 = DATASETS_ROOT / "kinetics400"
DATASETS_SPLITS = DATASETS_ROOT / "splits"
DATASETS_METADATA = DATASETS_ROOT / "metadata"

# Embeddings
EMBEDDINGS_ROOT = DATA_ROOT / "embeddings"
EMBEDDINGS_B3 = EMBEDDINGS_ROOT / "b3"
EMBEDDINGS_B3_39M = EMBEDDINGS_ROOT / "b3_39m"
EMBEDDINGS_B3_128K = EMBEDDINGS_ROOT / "b3_39m_128k"
EMBEDDINGS_B3_TRAINING = EMBEDDINGS_ROOT / "b3_training"
EMBEDDINGS_B3_INTEGRATION = EMBEDDINGS_ROOT / "b3_integration"
EMBEDDINGS_FAISS = EMBEDDINGS_ROOT / "faiss_indices"
EMBEDDINGS_SENTENCE_TX = EMBEDDINGS_ROOT / "sentence_transformers"
EMBEDDINGS_CACHE = EMBEDDINGS_ROOT / "cache"

# Processed data
PROCESSED_ROOT = DATA_ROOT / "processed"

# Raw data
RAW_ROOT = DATA_ROOT / "raw"

# Training data
TRAINING_DATA_ROOT = DATA_ROOT / "training"
TRAINING_DATA_LOGS = TRAINING_DATA_ROOT / "logs"

# HuggingFace cache
HF_CACHE = DATA_ROOT / "huggingface_cache"

# Reports and catalogs
DATA_REPORTS = DATA_ROOT / "reports"
DATA_CATALOGS = DATA_ROOT / "catalogs"

# System data
SYSTEM_DATA = DATA_ROOT / "system"

# ─────────────────────────────────────────────────────────────────────────────
# RLM Training Paths (from RLM_TRAINING_INTEGRATION_PLAN.md)
# ─────────────────────────────────────────────────────────────────────────────

RLM_BASE_MODEL = CHECKPOINTS_ROOT / "b3" / "b3_best_quality_model.pth"
RLM_TRAINING_OUTPUT = CHECKPOINT_RLM
RLM_TRAINING_LOGS = MODELS_ROOT / "logs" / "rlm_training"
RLM_LONG_CONTEXT_QA = DATASETS_ROOT / "text" / "long_context_qa"
RLM_BABILONG_BENCHMARK = DATASETS_ROOT / "text" / "babilong_benchmark"
RLM_GUITAR_QA = DATASETS_ROOT / "text" / "guitar_lesson_qa"
RLM_MUSIC_THEORY = DATASETS_ROOT / "text" / "music_theory_context"


# ─────────────────────────────────────────────────────────────────────────────
# Utility Functions
# ─────────────────────────────────────────────────────────────────────────────

def verify_data_drive() -> bool:
    """Check if the external data drive is available and accessible."""
    if not DATA_DRIVE.is_dir():
        logger.warning(f"Data drive not found or not a directory: {DATA_DRIVE}")
        return False

    required = [MODELS_ROOT, DATA_ROOT]
    for path in required:
        if not path.is_dir():
            logger.warning(f"Required directory missing or not a directory: {path}")
            return False

    logger.info(f"Data drive verified: {DATA_DRIVE}")
    return True


def enforce_data_drive() -> None:
    """Enforce that the external data drive is available, raising RuntimeError if not."""
    if not verify_data_drive():
        msg = (
            f"Critical Failure: Data drive ({DATA_DRIVE}) or required directories "
            f"are missing. Boot aborted. Reconnect the external drive and verify "
            f"that {MODELS_ROOT} and {DATA_ROOT} are accessible directories. "
            "If storage was intentionally moved, set IMPRESSIONCORE_DATA_DRIVE "
            "to the root containing both models and data before launching. "
            "Do not create empty folders as a substitute for missing storage."
        )
        logger.critical(msg)
        raise RuntimeError(msg)


def get_best_b3_checkpoint() -> Optional[Path]:
    """Return the path to the best available B3 model checkpoint.

    Priority order:
    1. Production B3 Hope v1
    2. B3 full training (latest epoch)
    3. B3 sanity slim 32M
    4. B3 conversational (final epoch)
    """
    candidates = [
        B3_HOPE_V1_WEIGHTS,
        CHECKPOINT_B3_FULL / "checkpoint_epoch_14.pth",
        CHECKPOINT_B3_SANITY / "checkpoint_epoch_0.pth",
        CHECKPOINT_B3_CONV / "b3_conv_epoch_final.pt",
    ]
    for path in candidates:
        if path.exists():
            logger.info(f"Best B3 checkpoint: {path}")
            return path

    logger.warning("No B3 checkpoint found on data drive")
    return None


def get_b3_hope_config() -> Optional[Dict[str, Any]]:
    """Load and return the B3 Hope v1 model configuration."""
    import json
    if B3_HOPE_V1_CONFIG.exists():
        with open(B3_HOPE_V1_CONFIG, 'r') as f:
            return json.load(f)
    return None


def get_checkpoint_inventory() -> Dict[str, list]:
    """Return an inventory of all available checkpoints on the data drive."""
    inventory = {}
    if not CHECKPOINTS_ROOT.exists():
        return inventory

    for subdir in CHECKPOINTS_ROOT.iterdir():
        if subdir.is_dir():
            files = [f.name for f in subdir.rglob("*.pt")] + \
                    [f.name for f in subdir.rglob("*.pth")]
            if files:
                inventory[subdir.name] = files

    return inventory


def get_data_drive_summary() -> Dict[str, Any]:
    """Return a summary of the data drive status for diagnostics."""
    summary = {
        "drive_available": DATA_DRIVE.exists(),
        "drive_path": str(DATA_DRIVE),
        "models_available": MODELS_ROOT.exists(),
        "data_available": DATA_ROOT.exists(),
        "b3_hope_v1_available": B3_HOPE_V1_WEIGHTS.exists(),
        "rlm_policy_available": RLM_POLICY_BEST.exists(),
        "checkpoint_count": 0,
        "dataset_categories": 0,
    }

    if CHECKPOINTS_ROOT.exists():
        summary["checkpoint_count"] = sum(
            1 for _ in CHECKPOINTS_ROOT.rglob("*.pt")
        ) + sum(
            1 for _ in CHECKPOINTS_ROOT.rglob("*.pth")
        )

    if DATASETS_ROOT.exists():
        summary["dataset_categories"] = sum(
            1 for d in DATASETS_ROOT.iterdir() if d.is_dir()
        )

    return summary


if __name__ == "__main__":
    try:
        enforce_data_drive()
    except RuntimeError as error:
        raise SystemExit(str(error))
