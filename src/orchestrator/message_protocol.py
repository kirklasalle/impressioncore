#!/usr/bin/env python3
"""Lightweight message objects for tri-architecture orchestration."""

from __future__ import annotations

import base64
import json
import uuid
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

_DEFAULT_VECTOR_DIM = 256


def _encode_vector(values: Iterable[float]) -> str:
    payload = json.dumps(list(values)).encode("utf-8")
    return base64.b64encode(payload).decode("ascii")


def _decode_vector(data: str) -> list[float]:
    raw = base64.b64decode(data.encode("ascii"))
    return list(json.loads(raw.decode("utf-8")))


@dataclass
class TriMessage:
    provenance: str
    modality: str
    structured_msg: Mapping[str, Any]
    summary_vector: Iterable[float] = field(default_factory=list)
    confidence: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    identifier: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self, include_vector: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": self.identifier,
            "provenance": self.provenance,
            "modality": self.modality,
            "structured_msg": json.dumps(self.structured_msg, separators=(",", ":")),
            "confidence": float(self.confidence),
            "timestamp": self.timestamp,
        }
        if include_vector:
            data["summary_vector"] = _encode_vector(self.summary_vector)
        return data

    def serialize(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def deserialize(cls, payload: str) -> TriMessage:
        data = json.loads(payload)
        vector_blob = data.get("summary_vector")
        vector = _decode_vector(vector_blob) if vector_blob else []
        structured_msg = json.loads(data["structured_msg"])
        return cls(
            provenance=data["provenance"],
            modality=data["modality"],
            structured_msg=structured_msg,
            summary_vector=vector,
            confidence=float(data.get("confidence", 0.0)),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            identifier=data.get("id", str(uuid.uuid4())),
        )

    @classmethod
    def blank(cls, provenance: str, modality: str, vector_dim: int = _DEFAULT_VECTOR_DIM) -> TriMessage:
        vector = [0.0] * vector_dim
        return cls(provenance=provenance, modality=modality, structured_msg={}, summary_vector=vector)


def pack_message(provenance: str, modality: str, structured: Mapping[str, Any], vector: Iterable[float], confidence: float) -> TriMessage:
    return TriMessage(
        provenance=provenance,
        modality=modality,
        structured_msg=structured,
        summary_vector=vector,
        confidence=confidence,
    )


def unpack_message(message: TriMessage) -> dict[str, Any]:
    return {
        "id": message.identifier,
        "provenance": message.provenance,
        "modality": message.modality,
        "structured_msg": message.structured_msg,
        "summary_vector": list(message.summary_vector),
        "confidence": message.confidence,
        "timestamp": message.timestamp,
    }
