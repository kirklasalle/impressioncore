"""Presets for ImpressionCore training.

Contains default presets optimized for NVIDIA GTX 1050 Ti (4GB VRAM) and CPU fallback.
"""
from copy import deepcopy
from typing import Dict, Any

# Canonical offering lineup used by Builder and Dashboard discovery.
OFFERING_PRESETS: Dict[str, Dict[str, Any]] = {
    "b1_39m": {
        "id": "b1_39m",
        "stage": "B1",
        "name": "B1 Hope 39M",
        "target_params_m": 39,
        "model": {
            "architecture": "transformer",
            "preset": "b1_39m",
            "layers": 8,
            "hiddenSize": 768,
            "heads": 12,
            "intermediateSize": 3072,
            "contextWindow": 4096,
            "vocabSize": 50257,
            "precision": "fp16",
            "activation": "gelu",
            "flashAttention": False,
            "rope": True,
        },
        "training": {
            "epochs": 3,
            "batchSize": 1,
            "learningRate": 5e-5,
            "warmupSteps": 100,
            "scheduler": "cosine",
            "precision": "fp16",
            "gradCheckpoint": True,
            "gradAccumSteps": 8,
            "maxSteps": 0,
            "checkpointDir": "F:\\models\\checkpoints",
        },
    },
    "b2_50m": {
        "id": "b2_50m",
        "stage": "B2",
        "name": "B2 Insight 50M",
        "target_params_m": 50,
        "model": {
            "architecture": "transformer",
            "preset": "b2_50m",
            "layers": 10,
            "hiddenSize": 832,
            "heads": 13,
            "intermediateSize": 3328,
            "contextWindow": 4096,
            "vocabSize": 50257,
            "precision": "fp16",
            "activation": "gelu",
            "flashAttention": False,
            "rope": True,
        },
        "training": {
            "epochs": 3,
            "batchSize": 1,
            "learningRate": 4e-5,
            "warmupSteps": 150,
            "scheduler": "cosine",
            "precision": "fp16",
            "gradCheckpoint": True,
            "gradAccumSteps": 10,
            "maxSteps": 0,
            "checkpointDir": "F:\\models\\checkpoints",
        },
    },
    "b3_504m": {
        "id": "b3_504m",
        "stage": "B3",
        "name": "B3 Apex 504M",
        "target_params_m": 504,
        "model": {
            "architecture": "transformer",
            "preset": "b3_504m",
            "layers": 24,
            "hiddenSize": 3072,
            "heads": 24,
            "intermediateSize": 12288,
            "contextWindow": 4096,
            "vocabSize": 50257,
            "precision": "fp16",
            "activation": "gelu",
            "flashAttention": True,
            "rope": True,
        },
        "training": {
            "epochs": 2,
            "batchSize": 1,
            "learningRate": 2e-5,
            "warmupSteps": 300,
            "scheduler": "cosine",
            "precision": "fp16",
            "gradCheckpoint": True,
            "gradAccumSteps": 16,
            "maxSteps": 0,
            "checkpointDir": "F:\\models\\checkpoints",
        },
    },
    "b3_3b": {
        "id": "b3_3b",
        "stage": "B3",
        "name": "B3 Ultra 3B MoE",
        "target_params_m": 3200,
        "model": {
            "architecture": "transformer",
            "preset": "b3_3b",
            "layers": 32,
            "hiddenSize": 4096,
            "heads": 32,
            "intermediateSize": 16384,
            "contextWindow": 8192,
            "vocabSize": 50257,
            "precision": "fp16",
            "activation": "gelu",
            "flashAttention": True,
            "rope": True,
        },
        "training": {
            "epochs": 2,
            "batchSize": 1,
            "learningRate": 1e-5,
            "warmupSteps": 500,
            "scheduler": "cosine",
            "precision": "fp16",
            "gradCheckpoint": True,
            "gradAccumSteps": 32,
            "maxSteps": 0,
            "checkpointDir": "F:\\models\\checkpoints",
        },
    },
}


def get_builder_offering_presets() -> Dict[str, Dict[str, Any]]:
    """Return a copy-safe map of canonical Builder offering presets."""
    return deepcopy(OFFERING_PRESETS)

PRESETS: Dict[str, Dict[str, Any]] = {
    "conversational_ai": {
        "model_architecture_config": "src/core/config/impressioncore_b1_arch.yaml",
        "dataset": {
            "type": "dummy_multimodal",
            "text_data_path": "data/dummy_text_corpus.txt",
            "image_data_path": "data/dummy_images/",
            "text_sequence_length": 512,
            "image_size": 224,
        },
        "training_params": {
            "optimizer": "AdamW",
            "learning_rate": 0.00005,
            "batch_size": 1,
            "num_epochs": 3,
            "gradient_accumulation_steps": 8,
            "weight_decay": 0.01,
            "lr_scheduler": "cosine",
            "warmup_steps": 100,
        },
        "checkpointing": {
            "checkpoint_dir": "models/impressioncore-b1-checkpoints/",
            "save_frequency_epochs": 1,
            "keep_last_n_checkpoints": 3,
        },
        "logging": {
            "log_frequency_steps": 10,
        },
        "device": "cuda",
        "system_oversight": {
            "enabled": True,
        },
        "seed": 42,
    },
    "smoke_test": {
        "model_architecture_config": "src/core/config/impressioncore_b1_arch.yaml",
        "dataset": {
            "type": "dummy_multimodal",
            "text_data_path": "data/dummy_text_corpus.txt",
            "image_data_path": "data/dummy_images/",
            "text_sequence_length": 64,
            "image_size": 224,
        },
        "training_params": {
            "optimizer": "AdamW",
            "learning_rate": 0.0001,
            "batch_size": 1,
            "num_epochs": 1,
            "gradient_accumulation_steps": 1,
            "weight_decay": 0.01,
            "lr_scheduler": "cosine",
            "warmup_steps": 5,
        },
        "checkpointing": {
            "checkpoint_dir": "models/impressioncore-b1-checkpoints/",
            "save_frequency_epochs": 1,
            "keep_last_n_checkpoints": 1,
        },
        "logging": {
            "log_frequency_steps": 1,
        },
        "device": "cpu",
        "system_oversight": {
            "enabled": True,
        },
        "seed": 42,
    },
    "distillation": {
        "model_architecture_config": "src/core/config/impressioncore_b1_arch.yaml",
        "dataset": {
            "type": "dummy_multimodal",
            "text_data_path": "data/dummy_text_corpus.txt",
            "image_data_path": "data/dummy_images/",
            "text_sequence_length": 256,
            "image_size": 224,
        },
        "training_params": {
            "optimizer": "AdamW",
            "learning_rate": 0.0001,
            "batch_size": 1,
            "num_epochs": 2,
            "gradient_accumulation_steps": 4,
            "weight_decay": 0.01,
            "lr_scheduler": "cosine",
            "warmup_steps": 50,
        },
        "checkpointing": {
            "checkpoint_dir": "models/impressioncore-b1-checkpoints/",
            "save_frequency_epochs": 1,
            "keep_last_n_checkpoints": 2,
        },
        "logging": {
            "log_frequency_steps": 5,
        },
        "device": "cuda",
        "system_oversight": {
            "enabled": True,
        },
        "seed": 42,
    }
}
