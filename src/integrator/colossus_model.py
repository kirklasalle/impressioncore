#!/usr/bin/env python3
"""Local Colossus integrator model wrapper."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

import torch
from torch import nn

from src.core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model
from src.orchestrator.message_protocol import TriMessage, pack_message, unpack_message


@dataclass
class ColossusConfig:
    d_model: int = 128
    num_heads: int = 4
    num_layers: int = 4
    num_experts: int = 2
    experts_per_token: int = 1
    vector_dim: int = 256
    checkpoint_path: Path | None = None
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


class Colossus(nn.Module):
    def __init__(self, cfg: ColossusConfig):
        super().__init__()
        base_cfg = B3Config(
            embed_dim=cfg.d_model,
            num_heads=cfg.num_heads,
            num_layers=cfg.num_layers,
            num_experts=cfg.num_experts,
            experts_per_token=cfg.experts_per_token,
        )
        self.model = ImpressionCoreB3Model(base_cfg)
        self.cfg = cfg
        self.model.requires_grad_(False)
        self.use_learned_heads = False
        self.learned_mix_ratio = 0.5

        feature_dim = cfg.vector_dim * 2 + 2
        if feature_dim <= 2:
            raise ValueError("vector_dim must be large enough to construct feature tensors.")

        self.vector_projector = nn.Sequential(
            nn.Linear(feature_dim, cfg.vector_dim),
            nn.GELU(),
            nn.Linear(cfg.vector_dim, cfg.vector_dim),
        )
        hidden_conf = max(cfg.vector_dim // 2, 4)
        self.confidence_head = nn.Sequential(
            nn.Linear(feature_dim, hidden_conf),
            nn.ReLU(),
            nn.Linear(hidden_conf, 1),
            nn.Sigmoid(),
        )

        self.to(cfg.device)

    @classmethod
    def load(cls, cfg: ColossusConfig) -> Colossus:
        instance = cls(cfg)
        if cfg.checkpoint_path and Path(cfg.checkpoint_path).is_file():
            load_kwargs = {"map_location": cfg.device}
            try:
                load_kwargs["weights_only"] = True  # type: ignore[arg-type]
                state = torch.load(str(cfg.checkpoint_path), **load_kwargs)
            except TypeError:  # pragma: no cover - older torch versions
                load_kwargs.pop("weights_only", None)
                state = torch.load(str(cfg.checkpoint_path), **load_kwargs)

            weight_key = "model_state_dict" if isinstance(state, Mapping) else None
            payload = state.get(weight_key, {}) if weight_key and weight_key in state else state

            if isinstance(payload, Mapping):
                model_state = payload.get("model", payload)
                if isinstance(model_state, Mapping):
                    instance.model.load_state_dict(model_state, strict=False)
                head_state = payload.get("vector_head")
                if isinstance(head_state, Mapping):
                    instance.vector_projector.load_state_dict(head_state, strict=False)
                conf_state = payload.get("confidence_head")
                if isinstance(conf_state, Mapping):
                    instance.confidence_head.load_state_dict(conf_state, strict=False)
                    instance.use_learned_heads = True
                meta_state = payload.get("meta")
                if isinstance(meta_state, Mapping):
                    instance.use_learned_heads = bool(meta_state.get("use_learned_heads", instance.use_learned_heads))
                    if "learned_mix_ratio" in meta_state:
                        instance.learned_mix_ratio = float(meta_state["learned_mix_ratio"])
            else:
                instance.load_state_dict(payload, strict=False)
        instance.eval()
        return instance

    def forward(self, *args, **kwargs):
        raise NotImplementedError("Colossus forward path is orchestrated via integrate().")

    def integrate(self, message_a: TriMessage, message_b: TriMessage, extra_context: Iterable[float] | None = None) -> Mapping[str, object]:
        merged: dict[str, object] = {
            "inputs": [unpack_message(message_a), unpack_message(message_b)],
            "notes": {},
        }
        if extra_context:
            merged["context_vector"] = list(extra_context)

        baseline_vector = self._blend_vectors(message_a.summary_vector, message_b.summary_vector)
        baseline_conf = self._blend_conf(message_a.confidence, message_b.confidence)

        if self.use_learned_heads:
            features = self._build_feature_tensor(message_a, message_b)
            with torch.no_grad():
                projected_vector = self.vector_projector(features)[0]
                blended_conf = self.confidence_head(features).squeeze(-1)
            learned_vector = projected_vector.cpu().tolist()
            summary_vector = self._interpolate_vectors(baseline_vector, learned_vector, self.learned_mix_ratio)
            confidence = float((1.0 - self.learned_mix_ratio) * baseline_conf + self.learned_mix_ratio * blended_conf.cpu().item())
        else:
            summary_vector = baseline_vector
            confidence = baseline_conf

        structured = {
            "decision": "integrate",
            "details": merged,
        }
        response = pack_message("model_colossus", "text", structured, summary_vector, confidence=confidence)
        return unpack_message(response)

    def save_heads(self, destination: Path) -> None:
        state = {
            "vector_head": self.vector_projector.state_dict(),
            "confidence_head": self.confidence_head.state_dict(),
            "meta": {
                "use_learned_heads": True,
                "learned_mix_ratio": self.learned_mix_ratio,
            },
        }
        self.use_learned_heads = True
        torch.save(state, str(destination))

    @staticmethod
    def _blend_vectors(vec_a: Iterable[float], vec_b: Iterable[float]) -> Iterable[float]:
        list_a = list(vec_a)
        list_b = list(vec_b)
        if not list_a and not list_b:
            return []
        if len(list_a) != len(list_b):
            return list_a or list_b
        return [(a + b) / 2.0 for a, b in zip(list_a, list_b)]

    @staticmethod
    def _blend_conf(conf_a: float, conf_b: float) -> float:
        return max(min((conf_a + conf_b) / 2.0, 1.0), 0.0)

    def _prepare_vector(self, vector: Iterable[float]) -> torch.Tensor:
        values = list(vector)
        if len(values) >= self.cfg.vector_dim:
            values = values[: self.cfg.vector_dim]
        else:
            values = values + [0.0] * (self.cfg.vector_dim - len(values))
        return torch.tensor(values, dtype=torch.float32, device=self.cfg.device)

    def _build_feature_tensor(self, message_a: TriMessage, message_b: TriMessage) -> torch.Tensor:
        vec_a = self._prepare_vector(message_a.summary_vector)
        vec_b = self._prepare_vector(message_b.summary_vector)
        confidences = torch.tensor([message_a.confidence, message_b.confidence], dtype=torch.float32, device=self.cfg.device)
        features = torch.cat([vec_a, vec_b, confidences], dim=0)
        return features.unsqueeze(0)

    @staticmethod
    def _interpolate_vectors(base: Iterable[float], learned: Iterable[float], mix: float) -> Iterable[float]:
        base_list = list(base)
        learned_list = list(learned)
        if not base_list:
            return learned_list
        if len(base_list) != len(learned_list):
            length = min(len(base_list), len(learned_list))
            base_list = base_list[:length]
            learned_list = learned_list[:length]
        mix = max(0.0, min(1.0, mix))
        return [(1.0 - mix) * b + mix * l for b, l in zip(base_list, learned_list)]
