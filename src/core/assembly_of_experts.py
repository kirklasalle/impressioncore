#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** July-29-2025
**Author:** ImpressionCore Team
**Tags:** #command_line #python #pytorch #source_code #src/models/assembly_of_experts.py
**Category:** Source Code
**Status:** Active
"""







# Assembly Of Experts

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** ImpressionCore Team
# Tags:** #command_line #python #pytorch #source_code #src\\models\\assembly_of_experts.py
# Category:** Source Code
# Status:** Active

"""
Assembly of Experts (AoE) module for ImpressionCore B2

Provides utilities to assemble (interpolate) multiple expert checkpoints into a single expert for use in MoE or other architectures.

- Supports weighted interpolation of expert parameters.
- Can be used to initialize MoE experts with AoE-assembled weights.
- Designed for extensibility and integration with B2 config/CLI.

Author: GitHub Copilot
Date: 2025-07-06
"""
import copy
import logging

import torch

logger = logging.getLogger(__name__)


class AssemblyOfExperts:
    """
    Assembly of Experts (AoE): Interpolates parameters from multiple expert checkpoints.
    Args:
        expert_state_dicts (List[Dict]): List of PyTorch state_dicts for each expert.
        weights (List[float]): Interpolation weights (should sum to 1.0).
    """
    def __init__(self, expert_state_dicts: list[dict], weights: list[float]):
        assert len(expert_state_dicts) == len(weights), "Number of experts and weights must match."
        assert abs(sum(weights) - 1.0) < 1e-5, "Weights must sum to 1.0."
        self.expert_state_dicts = expert_state_dicts
        self.weights = weights

    def assemble(self) -> dict:
        """
        Returns a new state_dict with parameters interpolated from all experts.
        Handles device/dtype consistency for robust model loading.
        """
        base = copy.deepcopy(self.expert_state_dicts[0])
        for key in base:
            # Only interpolate if all experts have this key and it is a tensor
            if all(key in expert for expert in self.expert_state_dicts) and torch.is_tensor(base[key]):
                tensors = [expert[key].to(base[key].device).to(base[key].dtype) for expert in self.expert_state_dicts]
                base[key] = sum(w * t for w, t in zip(self.weights, tensors))
            # Otherwise, keep the value from the first expert
        return base
    @staticmethod
    def cli_help():
        """
        Prints CLI/config usage for AoE integration in B2.
        """
        logger.info(
            "To use Assembly of Experts (AoE) in B2, add the following to your config or CLI:\n"
            "  aoe_expert_paths:\n"
            "    - path/to/expert1.pt\n"
            "    - path/to/expert2.pt\n"
            "  aoe_expert_weights: [0.6, 0.4]\n"
            "  Weights must sum to 1.0. The model will assemble experts at initialization."
        )

    @staticmethod
    def from_checkpoints(paths: list[str], weights: list[float], map_location: str | torch.device = 'cpu'):
        """
        Loads expert checkpoints from file paths and returns an AoE instance.
        """
        state_dicts = [torch.load(p, map_location=map_location) for p in paths]
        return AssemblyOfExperts(state_dicts, weights)

# Example usage (in model init):
# aoe = AssemblyOfExperts.from_checkpoints(["expert1.pt", "expert2.pt"], [0.6, 0.4])
# assembled_state_dict = aoe.assemble()
# expert.load_state_dict(assembled_state_dict)
