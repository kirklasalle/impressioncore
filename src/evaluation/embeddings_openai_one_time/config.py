"""Configuration for one-time OpenAI vs local checkpoint embedding evaluation.
Created: August 17, 2025
Author: GitHub Copilot

This module centralizes paths and parameters so the harness scripts remain minimal.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

# NOTE: Adjust these if you relocate checkpoints.

@dataclass
class CheckpointConfig:
    label: str                 # Logical label (e.g., UNIFIED_SWEET_SPOT)
    path: str                  # Absolute file path to checkpoint (.pth/.pt/.safetensors)
    modality_scope: list[str]  # e.g., ["text"], future expansion
    embedding_dim: int | None = None  # Filled after model load if None
    precision: str = "fp16"    # fp16 by default per user guidance
    notes: str = ""

OPENAI_MODEL_SMALL = "text-embedding-3-small"
OPENAI_MODEL_LARGE = "text-embedding-3-large"  # Only used selectively
OPENAI_USE_LARGE_THRESHOLD = 0.07  # Trigger on >=7% uplift slices
OPENAI_MAX_COST_USD = 10.0
OPENAI_SOFT_STOP_USD = 9.0

# User-provided / confirmed paths
CHECKPOINTS: list[CheckpointConfig] = [
    CheckpointConfig(
        label="UNIFIED_SWEET_SPOT",
        path=r"F:\\models\\checkpoints\\unified_sweet_spot\\unified_final_step_0.pth",
        modality_scope=["text"],
        notes="Unified sweet spot current baseline"
    ),
    CheckpointConfig(
        label="SWEET_SPOT_RECOVERY_5000",
        path=r"F:\\models\\checkpoints\\sweet_spot_recovery\\recovery_step_5000.pth",
        modality_scope=["text"],
        notes="Recovery methodology 5000-step"
    ),
    CheckpointConfig(
        label="KD_SFT_PHASE2_FULLRUN",
        path=r"F:\\models\\checkpoints\\kd_sft_phase2_fullrun_20250815\\step_605.pt",
        modality_scope=["text"],
        notes="KD/SFT phase2 full run checkpoint (step_605)"
    ),
]

# Data slice configuration (query set manifests to be created)
SLICE_DEFINITIONS = [
    {"name": "short_queries", "target_size": 200},
    {"name": "multilingual", "target_size": 300},
    {"name": "rare_entities", "target_size": 200},
    {"name": "abstract_topics", "target_size": 150},
    {"name": "paraphrase_clusters", "target_size": 150},
    {"name": "conversation_memory", "target_size": 300},
]

# Directory where manifests and outputs will reside (F: drive enforced)
BASE_OUTPUT_DIR = r"F:/data/embeddings/openai_one_time"
MANIFEST_DIR = os.path.join(BASE_OUTPUT_DIR, "manifests")
VECTORS_DIR = os.path.join(BASE_OUTPUT_DIR, "vectors")
METRICS_PATH = os.path.join(BASE_OUTPUT_DIR, "metrics.json")
DELTA_TABLE_PATH = os.path.join(BASE_OUTPUT_DIR, "slice_delta_table.md")
COST_LOG_PATH = os.path.join(BASE_OUTPUT_DIR, "openai_cost_log.json")

# Query-only OpenAI usage (no doc-side embedding to reduce cost initially)
OPENAI_QUERY_ONLY = True

# Bootstrap settings
BOOTSTRAP_RESAMPLES = 1000
MIN_SIGNIFICANT_DELTA = 0.02  # Lower bound for CI significance

# Similarity settings
NORMALIZE_OUTPUT = True

# Batch sizes (tunable)
LOCAL_BATCH_SIZE = 16
OPENAI_BATCH_TOKENS_TARGET = 800  # approximate token budget per API batch

# Token cost estimation (fallback if API billing detail not accessible)
EST_TOKENS_PER_QUERY = 40
PRICE_PER_1K_SMALL = 0.00002
PRICE_PER_1K_LARGE = 0.00013

# Random seed for reproducibility
SEED = 42

"""Contract Summary:
- Scripts will import this config, ensure output directories exist, and proceed.
- A separate manifest builder will produce JSONL files listing queries and ground truth doc ids per slice.
- Embedding harness will: load checkpoints → compute doc embeddings for referenced docs → compute query embeddings per checkpoint & OpenAI → store vectors → compute metrics → write deltas.
"""
