"""OpenAI embedding client helper.
Created: August 17, 2025
Author: GitHub Copilot
"""
from __future__ import annotations

import json
import os
import time

from .config import (
    COST_LOG_PATH,
    EST_TOKENS_PER_QUERY,
    OPENAI_MAX_COST_USD,
    OPENAI_MODEL_LARGE,
    OPENAI_MODEL_SMALL,
    OPENAI_SOFT_STOP_USD,
    PRICE_PER_1K_LARGE,
    PRICE_PER_1K_SMALL,
)

try:
    from openai import OpenAI  # openai>=1.0.0
except ImportError:  # Fallback or deferred install
    OpenAI = None

_client = None
_cost_state = {"estimated_cost_usd": 0.0, "batches": []}


def get_client():
    global _client
    if _client is None:
        if OpenAI is None:
            raise RuntimeError("openai package not installed. Install via requirements.txt.")
        _client = OpenAI()
    return _client


def _estimate_batch_cost(n_texts: int, model: str) -> float:
    # Approximate tokens
    tokens = n_texts * EST_TOKENS_PER_QUERY
    price = PRICE_PER_1K_LARGE if model == OPENAI_MODEL_LARGE else PRICE_PER_1K_SMALL
    return (tokens / 1000.0) * price


def _log_cost(model: str, n_texts: int, est_cost: float):
    entry = {"ts": time.time(), "model": model, "n_texts": n_texts, "est_cost": est_cost}
    _cost_state["batches"].append(entry)
    _cost_state["estimated_cost_usd"] += est_cost
    os.makedirs(os.path.dirname(COST_LOG_PATH), exist_ok=True)
    with open(COST_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(_cost_state, f, indent=2)


def fetch_embeddings(texts: list[str], model: str = OPENAI_MODEL_SMALL) -> list[list[float]]:
    client = get_client()
    est_cost = _estimate_batch_cost(len(texts), model)
    if _cost_state["estimated_cost_usd"] + est_cost > OPENAI_MAX_COST_USD:
        raise RuntimeError("Cost limit exceeded; aborting further OpenAI calls.")
    if _cost_state["estimated_cost_usd"] + est_cost > OPENAI_SOFT_STOP_USD:
        print("[WARN] Approaching budget limit; consider stopping soon.")
    _log_cost(model, len(texts), est_cost)

    resp = client.embeddings.create(model=model, input=texts)
    return [d.embedding for d in resp.data]


def selective_large_escalation(candidate_queries: list[str]) -> list[list[float]]:
    if not candidate_queries:
        return []
    return fetch_embeddings(candidate_queries, model=OPENAI_MODEL_LARGE)
