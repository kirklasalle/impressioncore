"""
openai_embeddings.py

Created: August 20, 2025
Author: GitHub Copilot
Purpose: Secure, memory-optimized OpenAI embedding utilities for ImpressionCore.
"""

import os
import hashlib
from pathlib import Path
from typing import List, Optional, Tuple, Dict
import openai
import numpy as np
from dotenv import load_dotenv, find_dotenv
# ImpressionCore logging and status animation modules
from .rich_logging import log_info, log_error, log_warning, log_success
from .rich_status_animation import status_animation
from contextlib import suppress
from math import ceil

# ---------------- Internal helpers to reduce cognitive complexity ---------------- #

def _init_openai_client(key: str):
    """Return (client, legacy_mode_flag). If new style client not present, use legacy mode."""
    if hasattr(openai, "OpenAI"):
        try:
            return openai.OpenAI(api_key=key), False
        except Exception as e:
            log_warning(f"Falling back to legacy OpenAI client: {e}")
    openai.api_key = key
    return None, True


def _resolve_legacy_create_fn():
    """Find the legacy embedding create function in the openai module."""
    for attr in ["embeddings", "Embedding"]:
        with suppress(Exception):
            candidate = getattr(openai, attr)
            if hasattr(candidate, "create"):
                return candidate.create
    # final fallback
    return getattr(getattr(openai, "embeddings"), "create", None)


def _extract_vectors_from_response(response) -> Optional[np.ndarray]:
    data = getattr(response, 'data', None)
    if data is None and isinstance(response, dict):
        data = response.get('data')
    if not data:
        return None
    vectors = []
    for item in data:
        emb = getattr(item, 'embedding', None) or (item.get('embedding') if isinstance(item, dict) else None)
        if emb is not None:
            vectors.append(emb)
    if not vectors:
        return None
    return np.asarray(vectors, dtype=np.float32)

# ---------------------------------------------------------------------------
# Environment loading strategy
# 1. Prefer project src/.env (two levels up from this file)
# 2. Fallback to src/core/.env (legacy earlier incorrect path)
# 3. Finally rely on any globally discoverable .env via find_dotenv
# ---------------------------------------------------------------------------
_UTILS_DIR = os.path.dirname(__file__)
_SRC_DIR = os.path.abspath(os.path.join(_UTILS_DIR, '..', '..'))          # .../src
_LEGACY_CORE_DIR = os.path.abspath(os.path.join(_UTILS_DIR, '..'))        # .../src/core

_PRIMARY_ENV = os.path.join(_SRC_DIR, '.env')
_LEGACY_ENV = os.path.join(_LEGACY_CORE_DIR, '.env')

loaded_any = False
for candidate in (_PRIMARY_ENV, _LEGACY_ENV):
    if os.path.isfile(candidate):
        load_dotenv(candidate, override=False)
        loaded_any = True

if not loaded_any:
    # Last resort: search upward
    auto = find_dotenv()
    if auto:
        load_dotenv(auto, override=False)


def _read_key_from_file(path: str) -> Optional[str]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    k, v = line.split('=', 1)
                    if k.strip() == 'OPENAI_API_KEY' and v.strip():
                        return v.strip()
                else:
                    if line.startswith('sk-') and len(line) > 40:
                        return line
    except Exception:
        return None
    return None


def _infer_api_key() -> Optional[str]:
    for candidate in (_PRIMARY_ENV, _LEGACY_ENV):
        if candidate and os.path.isfile(candidate):
            key = _read_key_from_file(candidate)
            if key:
                log_warning("Inferred OPENAI_API_KEY from raw .env entry (please normalize format).")
                return key
    return None


def get_openai_api_key() -> str:
    """Return OpenAI API key or raise EnvironmentError if missing."""
    api_key = os.getenv("OPENAI_API_KEY") or _infer_api_key()
    if not api_key:
        log_error("OPENAI_API_KEY not set. Create src/.env with OPENAI_API_KEY=your_key.")
        raise EnvironmentError("OPENAI_API_KEY not set.")
    return api_key

def _cache_dir(default_dir: Optional[str] = None) -> Path:
    """Determine cache directory (configurable via env OPENAI_EMBED_CACHE)."""
    base = (
        default_dir
        or os.getenv("OPENAI_EMBED_CACHE")
        or os.path.join("F:/data/embeddings", "openai_cache")
    )
    p = Path(base)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _hash_text(model: str, text: str) -> str:
    return hashlib.sha256(f"{model}||{text}".encode("utf-8")).hexdigest()


def _split_cached(texts: List[str], model: str, cache_root: Path) -> Tuple[List[str], Dict[int, np.ndarray]]:
    """Return missing_texts, cached_vectors_map(index->vector)."""
    missing: List[str] = []
    cached: Dict[int, np.ndarray] = {}
    for idx, t in enumerate(texts):
        h = _hash_text(model, t)
        f = cache_root / f"{h[:32]}.npy"
        if f.is_file():
            try:
                vec = np.load(f)
                cached[idx] = vec
            except Exception:
                missing.append(t)
        else:
            missing.append(t)
    return missing, cached


def _store_new_embeddings(texts: List[str], model: str, vectors: np.ndarray, cache_root: Path) -> None:
    for t, v in zip(texts, vectors):
        try:
            h = _hash_text(model, t)
            np.save(cache_root / f"{h[:32]}.npy", v.astype(np.float32))
        except Exception as e:
            log_warning(f"Failed to store cached embedding: {e}")


def _call_openai_embeddings(texts: List[str], model: str, api_key: Optional[str]) -> Optional[np.ndarray]:
    """Low-level raw API call without caching (kept small to reduce complexity)."""
    if not texts:
        return np.zeros((0, 0), dtype=np.float32)
    key = api_key or get_openai_api_key()
    client, legacy = _init_openai_client(key)
    if legacy:
        create_fn = _resolve_legacy_create_fn()
        if not create_fn:
            log_error("Could not resolve legacy OpenAI embeddings create function.")
            return None
    try:
        if not legacy:
            response = client.embeddings.create(input=texts, model=model)  # type: ignore
        else:
            response = create_fn(input=texts, model=model)  # type: ignore
        embeddings = _extract_vectors_from_response(response)
        if embeddings is None:
            log_error("Failed to parse embeddings from OpenAI response.")
            return None
        return embeddings
    except Exception as e:
        log_error(f"Embedding generation failed: {e}")
        return None


def generate_openai_embeddings(
    texts: List[str],
    model: str = "text-embedding-3-small",
    api_key: Optional[str] = None,
    use_cache: bool = True,
    cache_dir: Optional[str] = None,
) -> Optional[np.ndarray]:
    """Generate embeddings with optional on-disk caching.

    Caching Strategy:
      - Each text hashed with sha256(model||text) first 32 hex chars used as filename
      - Individual .npy files (float32) allow partial reuse without single large index file
      - Missing texts are batched in a single request (caller's batching handles larger sets)

    Args:
        texts: Input texts (order preserved)
        model: Embedding model name
        api_key: Optional override key
        use_cache: Enable / disable local cache lookup and persistence
        cache_dir: Optional explicit cache directory path

    Returns:
        ndarray shape (N, D) or None if API call failed
    """
    if not texts:
        log_warning("No texts provided for embedding generation.")
        return np.zeros((0, 0), dtype=np.float32)

    cache_root = _cache_dir(cache_dir) if use_cache else None
    missing: List[str]
    cached_map: Dict[int, np.ndarray]
    if use_cache:
        missing, cached_map = _split_cached(texts, model, cache_root)
        if cached_map and not missing:
            # All cached: stack in order
            ordered = [cached_map[i] for i in range(len(texts))]
            mat = np.vstack(ordered).astype(np.float32)
            log_info(f"All {len(texts)} embeddings served from cache (model={model}).")
            return mat
    else:
        missing, cached_map = texts[:], {}

    with status_animation("Generating OpenAI embeddings"):
        fresh = _call_openai_embeddings(missing, model, api_key)
    if fresh is None:
        return None
    if use_cache:
        _store_new_embeddings(missing, model, fresh, cache_root)
        log_success(f"Cached {len(missing)} new embeddings (model={model}).")
    # Reconstruct in original order
    result_rows: List[np.ndarray] = []
    fresh_iter = iter(fresh)
    for idx in range(len(texts)):
        if idx in cached_map:
            result_rows.append(cached_map[idx])
        else:
            result_rows.append(next(fresh_iter))
    mat = np.vstack(result_rows).astype(np.float32)
    log_info(f"Generated embeddings shape={mat.shape} model={model} (cache_hits={len(cached_map)})")
    return mat


def generate_openai_embeddings_batched(
    texts: List[str],
    model: str = "text-embedding-3-small",
    api_key: Optional[str] = None,
    batch_size: int = 64,
    use_cache: bool = True,
    cache_dir: Optional[str] = None,
) -> Optional[np.ndarray]:
    """Batch wrapper around generate_openai_embeddings with caching passthrough."""
    if batch_size <= 0:
        batch_size = 64
    if len(texts) <= batch_size:
        return generate_openai_embeddings(texts, model=model, api_key=api_key, use_cache=use_cache, cache_dir=cache_dir)
    all_vecs: List[np.ndarray] = []
    total = len(texts)
    n_batches = ceil(total / batch_size)
    for i in range(n_batches):
        start = i * batch_size
        chunk = texts[start:start + batch_size]
        log_info(f"Batch {i+1}/{n_batches} (size={len(chunk)})")
        vecs = generate_openai_embeddings(chunk, model=model, api_key=api_key, use_cache=use_cache, cache_dir=cache_dir)
        if vecs is None:
            log_warning(f"Batch {i+1} failed; aborting batched generation.")
            return None
        all_vecs.append(vecs)
    if not all_vecs:
        return None
    return np.vstack(all_vecs)

def save_embeddings_npy(
    embeddings: np.ndarray,
    out_path: str
) -> None:
    """
    Save embeddings to a .npy file.

    Args:
        embeddings (np.ndarray): Embedding matrix.
        out_path (str): Output file path.

    Returns:
        None
    """
    try:
        np.save(out_path, embeddings)
        log_info(f"Embeddings saved to {out_path}")
    except Exception as e:
        log_error(f"Failed to save embeddings: {e}")
