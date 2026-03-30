# RLM Training Infrastructure
# src/training/rlm/__init__.py

"""
RLM (Recursive Language Model) Training Infrastructure for ImpressionCore.

This package provides reinforcement learning training for optimal NEXUS
command generation, enabling B3 to learn context folding policies.

Components:
    - policy_network: RL policy with PEFT/LoRA for action selection
    - state_encoder: Context state representation for policy input
    - reward_functions: Multi-objective rewards with anti-hacking measures
    - rlm_trainer: PPO training loop with adaptive KL control
    - experience_buffer: Rollout storage for policy updates

Usage:
    from src.training.rlm import RLMTrainer, RLMPolicyNetwork

    trainer = RLMTrainer(config_path="src/core/src/core/config/rlm_training_config.yaml")
    trainer.train()

Prime Directive Compliance: ✅ Verified
IDS Status: Indexed
"""

from .experience_buffer import ExperienceBuffer
from .policy_network import RLMPolicyNetwork
from .reward_functions import RLMRewardFunction
from .rlm_trainer import RLMTrainer
from .state_encoder import RLMStateEncoder

__all__ = [
    "ExperienceBuffer",
    "RLMPolicyNetwork",
    "RLMRewardFunction",
    "RLMStateEncoder",
    "RLMTrainer",
]

__version__ = "1.0.0"
__author__ = "Kirk LaSalle; Antigravity Agent"
