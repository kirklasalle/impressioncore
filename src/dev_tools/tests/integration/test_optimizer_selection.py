"""
Integration test for memory-efficient optimizer selection in ModelTrainer.
"""
import pytest
import torch
import torch.nn as nn
from src.training.trainer import ModelTrainer

def simple_model():
    return nn.Sequential(nn.Linear(8, 8), nn.ReLU(), nn.Linear(8, 2))

def test_adamw_selection():
    model = simple_model()
    trainer = ModelTrainer(model, train_dataloader=[], optimizer_name="adamw", optimizer_lr=1e-3)
    assert trainer.optimizer.__class__.__name__ == "AdamW"

def test_adam8bit_fallback(monkeypatch):
    model = simple_model()
    # Simulate bitsandbytes not installed
    def fake_get_memory_efficient_optimizer(*args, **kwargs):
        raise ImportError("bitsandbytes is required for 8-bit Adam. Please install bitsandbytes.")
    
    # Patch the function in the trainer module where it's imported
    import src.training.trainer as trainer_module
    monkeypatch.setattr(trainer_module, "get_memory_efficient_optimizer", fake_get_memory_efficient_optimizer)
    
    trainer = ModelTrainer(model, train_dataloader=[], optimizer_name="adam8bit", optimizer_lr=1e-3)
    assert trainer.optimizer.__class__.__name__ == "AdamW"
