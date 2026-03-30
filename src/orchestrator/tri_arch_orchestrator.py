#!/usr/bin/env python3
"""Coordinator for analytical, creative, and integrator B3 instances."""

from __future__ import annotations

import logging
import os
import threading
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch

from src.core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model
from src.integrator.colossus_model import Colossus, ColossusConfig
from src.orchestrator.message_protocol import TriMessage, pack_message

try:
    from transformers import AutoTokenizer
except ImportError:  # pragma: no cover - graceful degradation when transformers is absent
    AutoTokenizer = None


logger = logging.getLogger(__name__)


@dataclass
class RoleConfig:
    name: str
    d_model: int
    num_heads: int
    num_layers: int
    num_experts: int
    experts_per_token: int
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


@dataclass
class TriOrchestratorConfig:
    role_a: RoleConfig
    role_b: RoleConfig
    colossus: ColossusConfig


class RoleModel:
    _tokenizer_cache: dict[str, AutoTokenizer | None] = {}

    def __init__(self, cfg: RoleConfig):
        base_cfg = B3Config(
            embed_dim=cfg.d_model,
            num_heads=cfg.num_heads,
            num_layers=cfg.num_layers,
            num_experts=cfg.num_experts,
            experts_per_token=cfg.experts_per_token,
        )
        self.model = ImpressionCoreB3Model(base_cfg)
        self.cfg = cfg
        self.model.to(cfg.device)
        self.model.eval()
        self.tokenizer = self._load_tokenizer()

    def _load_tokenizer(self):
        if AutoTokenizer is None:
            return None
        cached = RoleModel._tokenizer_cache.get(self.cfg.name)
        if cached is not None:
            return cached
        try:
            tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
            if getattr(tokenizer, "pad_token", None) is None:
                tokenizer.pad_token = tokenizer.eos_token
            RoleModel._tokenizer_cache[self.cfg.name] = tokenizer
            return tokenizer
        except Exception as exc:  # pragma: no cover - dependency/runtime specific
            logger.warning("Tokenizer load failed for %s: %s", self.cfg.name, exc)
            RoleModel._tokenizer_cache[self.cfg.name] = None
            return None

    def _prepare_inputs(self, multimodal_input: Mapping[str, Any]) -> dict[str, Any]:
        allowed_keys = {
            "input_ids",
            "image_features",
            "audio_features",
            "phoneme_ids",
            "modality_type",
            "mask",
        }
        prepared: dict[str, Any] = {}
        for key in allowed_keys:
            if key not in multimodal_input:
                continue
            value = multimodal_input[key]
            if isinstance(value, torch.Tensor):
                prepared[key] = value.to(self.cfg.device)
            else:
                prepared[key] = value
        return prepared

    def _summarize_embedding(self, embedding: torch.Tensor | None) -> Iterable[float]:
        if embedding is None:
            return [0.0] * min(self.cfg.d_model, 256)
        with torch.no_grad():
            pooled = embedding.detach().mean(dim=1, keepdim=False).to("cpu", dtype=torch.float32)
        flat = pooled.flatten()
        if flat.numel() > 256:
            flat = flat[:256]
        return flat.tolist()

    def _decode_tokens(self, token_ids: torch.Tensor) -> str:
        if token_ids.ndim > 1:
            token_ids = token_ids[0]
        token_ids = token_ids.detach().to("cpu")
        token_ids = token_ids.tolist()
        if not token_ids:
            return ""
        if self.tokenizer is not None:
            try:
                return self.tokenizer.decode(token_ids, skip_special_tokens=True)
            except Exception as exc:  # pragma: no cover - decoding edge cases
                logger.debug("Tokenizer decode failed for %s: %s", self.cfg.name, exc)
        # Fallback: provide token ids when decoding unavailable
        tail = token_ids[-8:]
        return f"Tokens {tail}"

    def _extract_top_tokens(self, logits: torch.Tensor, k: int = 5) -> Iterable[dict[str, Any]] | None:
        if logits is None:
            return None
        if logits.ndim < 3:
            return None
        last_step = logits[0, -1]
        values, indices = torch.topk(last_step, k=min(k, last_step.numel()))
        results = []
        for score, idx in zip(values.detach().cpu().tolist(), indices.detach().cpu().tolist()):
            token_text = None
            if self.tokenizer is not None:
                try:
                    token_text = self.tokenizer.decode([idx], skip_special_tokens=True).strip() or None
                except Exception:  # pragma: no cover - decoding edge cases
                    token_text = None
            results.append({"token_id": int(idx), "token": token_text, "logit": float(score)})
        return results

    def encode(self, multimodal_input: dict[str, torch.Tensor]) -> torch.Tensor:
        prepared = self._prepare_inputs(multimodal_input)
        with torch.no_grad():
            embedding = self.model.embeddings(
                input_ids=prepared.get("input_ids"),
                image_features=prepared.get("image_features"),
                audio_features=prepared.get("audio_features"),
                phoneme_ids=prepared.get("phoneme_ids"),
                modality_type=None,
            )
        return embedding

    def process(self, multimodal_input: Mapping[str, Any], base_embedding: torch.Tensor | None) -> TriMessage:
        summary_vector = self._summarize_embedding(base_embedding)
        try:
            prepared = self._prepare_inputs(multimodal_input)
            with torch.no_grad():
                outputs = self.model(**prepared)
        except Exception as exc:  # pragma: no cover - inference safety net
            logger.error("Role %s inference failed: %s", self.cfg.name, exc)
            fallback = TriMessage.blank(self.cfg.name, "text", vector_dim=len(summary_vector))
            fallback.structured_msg = {"role": self.cfg.name, "error": str(exc)}
            fallback.confidence = 0.0
            return fallback

        logits: torch.Tensor | None = outputs.get("logits") if isinstance(outputs, dict) else None
        quality_tensor: torch.Tensor | None = outputs.get("quality_score") if isinstance(outputs, dict) else None

        generated_text = self._decode_tokens(torch.argmax(logits, dim=-1)) if logits is not None else ""
        quality_value = float(quality_tensor.mean().item()) if quality_tensor is not None else 0.0
        quality_value = max(0.0, min(1.0, quality_value))

        structured: dict[str, Any] = {
            "role": self.cfg.name,
            "text": generated_text,
            "quality": quality_value,
        }

        top_tokens = self._extract_top_tokens(logits)
        if top_tokens:
            structured["top_tokens"] = top_tokens

        if logits is not None:
            structured["sequence_length"] = int(logits.size(1))

        return pack_message(self.cfg.name, "text", structured, summary_vector, confidence=quality_value)


class TriOrchestrator:
    def __init__(self, cfg: TriOrchestratorConfig):
        self.cfg = cfg
        resolved_checkpoint = self._resolve_colossus_checkpoint(cfg.colossus)
        if resolved_checkpoint is not None:
            cfg.colossus.checkpoint_path = resolved_checkpoint
            logger.info("Resolved Colossus checkpoint at %s", resolved_checkpoint)
        self.model_a = RoleModel(cfg.role_a)
        self.model_b = RoleModel(cfg.role_b)
        self.colossus = Colossus.load(cfg.colossus)

    @staticmethod
    def _latest_checkpoint(directory: Path) -> Path | None:
        if not directory.exists():
            return None
        candidates = sorted(
            (path for path in directory.glob("*.pt") if path.is_file()),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )
        return candidates[0] if candidates else None

    @staticmethod
    def _read_pointer(path: Path) -> Path | None:
        try:
            if not path.is_file():
                return None
            target = path.read_text(encoding="utf-8").strip()
            if not target:
                return None
            candidate = Path(target).expanduser()
            if candidate.is_file():
                return candidate
            logger.warning("Colossus pointer %s points to missing file %s", path, candidate)
        except OSError as exc:  # pragma: no cover - filesystem edge cases
            logger.debug("Unable to read Colossus pointer %s: %s", path, exc)
        return None

    def _resolve_colossus_checkpoint(self, config: ColossusConfig) -> Path | None:
        env_path = os.environ.get("TRI_COLOSSUS_CHECKPOINT") or os.environ.get("COLOSSUS_CHECKPOINT_PATH")
        if env_path:
            candidate = Path(env_path).expanduser()
            if candidate.is_file():
                return candidate
            logger.warning("Configured Colossus checkpoint %s was not found", candidate)

        pointer_locations = []
        pointer_env = os.environ.get("TRI_COLOSSUS_POINTER") or os.environ.get("COLOSSUS_CHECKPOINT_POINTER")
        if pointer_env:
            pointer_locations.append(Path(pointer_env).expanduser())

        src_root = Path(__file__).resolve().parents[1]
        pointer_locations.append(src_root / "core" / "config" / "colossus_checkpoint.pointer")
        for pointer in pointer_locations:
            resolved = self._read_pointer(pointer)
            if resolved is not None:
                return resolved

        if config.checkpoint_path and Path(config.checkpoint_path).is_file():
            return Path(config.checkpoint_path)

        env_dir = os.environ.get("TRI_COLOSSUS_DIR") or os.environ.get("COLOSSUS_CHECKPOINT_DIR")
        search_dirs = []
        if env_dir:
            search_dirs.append(Path(env_dir).expanduser())

        default_dir = Path("F:/models/management/training_sessions/colossus")
        if default_dir not in search_dirs:
            search_dirs.append(default_dir)

        for directory in search_dirs:
            latest = self._latest_checkpoint(directory)
            if latest is not None:
                return latest
        return None

    def _run_role(
        self,
        role: RoleModel,
        multimodal_input: Mapping[str, Any],
        base_embedding: torch.Tensor | None,
        storage: dict[str, TriMessage],
    ) -> None:
        try:
            storage[role.cfg.name] = role.process(multimodal_input, base_embedding)
        except Exception as exc:  # pragma: no cover - defensive programming for threads
            logger.exception("Unhandled error while running role %s: %s", role.cfg.name, exc)
            fallback = TriMessage.blank(role.cfg.name, "text")
            fallback.structured_msg = {"role": role.cfg.name, "error": str(exc)}
            storage[role.cfg.name] = fallback

    def infer(self, multimodal_input: dict[str, torch.Tensor], extra_context: Iterable[float] | None = None) -> dict[str, object]:
        embedding_a = self.model_a.encode(multimodal_input)
        embedding_b = self.model_b.encode(multimodal_input)

        outputs: dict[str, TriMessage] = {}
        thread_a = threading.Thread(
            target=self._run_role,
            args=(self.model_a, multimodal_input, embedding_a, outputs),
            daemon=True,
        )
        thread_b = threading.Thread(
            target=self._run_role,
            args=(self.model_b, multimodal_input, embedding_b, outputs),
            daemon=True,
        )
        thread_a.start()
        thread_b.start()
        thread_a.join()
        thread_b.join()
        message_a = outputs.get(self.cfg.role_a.name)
        message_b = outputs.get(self.cfg.role_b.name)
        if not message_a or not message_b:
            raise RuntimeError("Role processing failed to produce outputs.")
        combined = self.colossus.integrate(message_a, message_b, extra_context=extra_context)
        combined["intermediate"] = {
            "role_a": message_a.to_dict(),
            "role_b": message_b.to_dict(),
        }
        combined.setdefault("details", combined.get("structured_msg", {}))
        return combined
