#!/usr/bin/env python3
"""Estimate parameter counts for ImpressionCore B3 configurations.

This utility instantiates the ImpressionCore B3 architecture with user-provided
hyperparameters and reports total parameters, memory footprint, and a
component-level breakdown. Use it to explore downsized variants before editing
core model definitions.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

import torch

sys.path.append(str(Path(__file__).resolve().parents[2] / "core" / "models"))

from impressioncore_b3_architecture import (
    B3Config,
    ImpressionCoreB3Model,
    memory_profile,
)


def _parameter_breakdown(model: ImpressionCoreB3Model) -> list[dict[str, float]]:
    counts: dict[str, int] = {}
    for name, param in model.named_parameters():
        component = name.split(".", 1)[0]
        counts[component] = counts.get(component, 0) + param.numel()

    total = sum(counts.values()) or 1
    breakdown: list[dict[str, float]] = []
    for component, num_params in sorted(counts.items(), key=lambda item: item[1], reverse=True):
        memory_mb = num_params * 4 / 1024**2
        percent = (num_params / total) * 100
        breakdown.append(
            {
                "component": component,
                "parameters": float(num_params),
                "memory_mb": memory_mb,
                "percent": percent,
            }
        )
    return breakdown


def estimate_parameters(args: argparse.Namespace) -> None:
    base_config = B3Config()
    config = replace(
        base_config,
        embed_dim=args.embed_dim,
        num_layers=args.num_layers,
        num_heads=args.num_heads,
        num_experts=args.num_experts,
        expert_dim=args.expert_dim,
        experts_per_token=args.experts_per_token,
        vocab_size=args.vocab_size,
    )

    with torch.no_grad():
        model = ImpressionCoreB3Model(config)

    profile = memory_profile(model)
    breakdown = _parameter_breakdown(model)

    print("\nImpressionCore B3 Parameter Estimate")
    print("====================================")
    print(f"embed_dim           : {config.embed_dim}")
    print(f"num_layers          : {config.num_layers}")
    print(f"num_heads           : {config.num_heads}")
    print(f"num_experts         : {config.num_experts}")
    print(f"expert_dim          : {config.expert_dim}")
    print(f"experts_per_token   : {config.experts_per_token}")
    print(f"vocab_size          : {config.vocab_size}")

    print("\nTotals")
    print("------")
    print(f"Total parameters    : {profile['total_params']:,}")
    print(f"Trainable parameters: {profile['trainable_params']:,}")
    print(f"Model memory (MB)   : {profile['memory_mb']:.2f}")
    print(f"Total memory (MB)   : {profile['total_memory_mb']:.2f}")

    print("\nComponent breakdown")
    print("-------------------")
    for entry in breakdown:
        name = entry['component']
        params = int(entry['parameters'])
        memory_mb = entry['memory_mb']
        percent = entry['percent']
        print(f"{name:>12}: {params:>12,} params | {memory_mb:7.2f} MB | {percent:5.2f}%")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Estimate ImpressionCore B3 parameter counts")
    parser.add_argument("--embed-dim", type=int, required=True)
    parser.add_argument("--num-layers", type=int, required=True)
    parser.add_argument("--num-heads", type=int, required=True)
    parser.add_argument("--num-experts", type=int, required=True)
    parser.add_argument("--expert-dim", type=int, required=True)
    parser.add_argument("--experts-per-token", type=int, required=True)
    parser.add_argument("--vocab-size", type=int, default=28000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    estimate_parameters(args)


if __name__ == "__main__":
    main()
