"""OpenAI embedding utility (streamlined for test environment).

Features:
- Loads OPENAI_API_KEY from environment or root `.env` if present.
- Uses real OpenAI API if client available & key present.
- Deterministic offline fallback (hash-based) if API unavailable.
- Optional simple on-disk caching.

This is a condensed, test-friendly implementation replacing archived
version to remove heavy transitive imports during refactor.
"""
from __future__ import annotations

import contextlib
import hashlib
import os
from pathlib import Path

import numpy as np

try:  # optional dependency
    import openai  # type: ignore
except Exception:  # pragma: no cover
    openai = None  # type: ignore

EMBED_DIM_DEFAULT = 1536  # matches text-embedding-3-small


def _load_root_env() -> None:
    """Load root .env manually (minimal parser) if present."""
    if os.getenv("OPENAI_API_KEY"):
        return
    root_env = Path(".env")
    if not root_env.is_file():
        return
    try:
        for line in root_env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('OPENAI_API_KEY='):
                os.environ['OPENAI_API_KEY'] = line.split('=',1)[1].strip()
                return
            if line.startswith('sk-') and len(line) > 40 and 'OPENAI_API_KEY' not in os.environ:
                os.environ['OPENAI_API_KEY'] = line.strip()
                return
    except Exception:
        pass


def get_openai_api_key() -> str:
    _load_root_env()
    key = os.getenv('OPENAI_API_KEY', '')
    return key


def _hash_vector(text: str, dim: int) -> np.ndarray:
    """Deterministic pseudo-embedding using SHA256 expansion."""
    h = hashlib.sha256(text.encode('utf-8')).digest()
    needed = dim * 4  # float32 bytes
    buf = bytearray()
    while len(buf) < needed:
        h = hashlib.sha256(h).digest()
        buf.extend(h)
    arr = np.frombuffer(bytes(buf[:needed]), dtype=np.uint8).astype(np.float32)
    # Normalize & reshape
    arr = arr.reshape(-1, 4).mean(axis=1)
    arr = arr[:dim]
    arr /= (np.linalg.norm(arr) + 1e-9)
    return arr.astype(np.float32)


def _cache_dir(base: str | None) -> Path:
    p = Path(base or "F:/data/embeddings/openai_cache")
    p.mkdir(parents=True, exist_ok=True)
    return p


def _try_real_api(texts: list[str], model: str, api_key: str) -> np.ndarray | None:  # pragma: no cover - network path
    if not openai or not api_key:
        return None
    try:
        if hasattr(openai, 'OpenAI'):
            client = openai.OpenAI(api_key=api_key)  # type: ignore[attr-defined]
            resp = client.embeddings.create(model=model, input=texts)
            data = getattr(resp, 'data', None)
            if not data:
                return None
            vectors = [d.embedding for d in data if hasattr(d, 'embedding')]
            if vectors:
                return np.asarray(vectors, dtype=np.float32)
            return None
        # legacy style
        openai.api_key = api_key  # type: ignore[attr-defined]
        resp = openai.Embedding.create(model=model, input=texts)  # type: ignore[attr-defined]
        data = resp.get('data') if isinstance(resp, dict) else getattr(resp, 'data', None)
        if not data:
            return None
        vectors = []
        for item in data:
            emb = item.get('embedding') if isinstance(item, dict) else getattr(item, 'embedding', None)
            if emb is not None:
                vectors.append(emb)
        if vectors:
            return np.asarray(vectors, dtype=np.float32)
    except Exception:
        return None
    return None


def generate_openai_embeddings(
    texts: list[str],
    model: str = "text-embedding-3-small",
    api_key: str | None = None,
    use_cache: bool = True,
    cache_dir: str | None = None,
) -> np.ndarray | None:
    """Return embeddings for texts.

    Falls back to deterministic pseudo-embeddings if OpenAI unavailable.
    """
    if not texts:
        return np.zeros((0, EMBED_DIM_DEFAULT), dtype=np.float32)
    key = api_key or get_openai_api_key()

    # Cache handling
    cache_root = _cache_dir(cache_dir) if use_cache else None
    cached_vectors = {}
    missing_indices = list(range(len(texts)))
    if cache_root:
        for idx, t in enumerate(texts):
            fp = cache_root / f"{hashlib.sha256((model+'||'+t).encode()).hexdigest()[:32]}.npy"
            if fp.is_file():
                with contextlib.suppress(Exception):
                    cached_vectors[idx] = np.load(fp)
        missing_indices = [i for i in range(len(texts)) if i not in cached_vectors]

    new_vectors = None
    if missing_indices:
        missing_texts = [texts[i] for i in missing_indices]
        real = _try_real_api(missing_texts, model, key)
        if real is not None and real.shape[0] == len(missing_texts):
            new_vectors = real.astype(np.float32)
        else:
            # offline fallback
            dim = EMBED_DIM_DEFAULT
            new_vectors = np.vstack([_hash_vector(t, dim) for t in missing_texts])
        if cache_root:
            for idx, vec in zip(missing_indices, new_vectors):
                fp = cache_root / f"{hashlib.sha256((model+'||'+texts[idx]).encode()).hexdigest()[:32]}.npy"
                with contextlib.suppress(Exception):
                    np.save(fp, vec)

    # Assemble final array
    dim = (next(iter(cached_vectors.values())).shape[0] if cached_vectors else EMBED_DIM_DEFAULT)
    out = np.zeros((len(texts), dim), dtype=np.float32)
    for idx, vec in cached_vectors.items():
        out[idx] = vec
    if missing_indices and new_vectors is not None:
        for pos, idx in enumerate(missing_indices):
            out[idx] = new_vectors[pos]
    return out


def generate_openai_embeddings_batched(
    texts: list[str],
    batch_size: int = 32,
    model: str = "text-embedding-3-small",
    api_key: str | None = None,
    use_cache: bool = True,
    cache_dir: str | None = None,
) -> np.ndarray:
    """Generate embeddings in batches to mirror legacy helper functionality."""

    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    if not texts:
        return np.zeros((0, EMBED_DIM_DEFAULT), dtype=np.float32)

    batches = [texts[i : i + batch_size] for i in range(0, len(texts), batch_size)]
    outputs = []
    for batch in batches:
        embeddings = generate_openai_embeddings(
            batch,
            model=model,
            api_key=api_key,
            use_cache=use_cache,
            cache_dir=cache_dir,
        )
        if embeddings is None:
            return np.zeros((0, EMBED_DIM_DEFAULT), dtype=np.float32)
        outputs.append(embeddings)

    return np.vstack(outputs) if outputs else np.zeros((0, EMBED_DIM_DEFAULT), dtype=np.float32)


__all__ = [
    "generate_openai_embeddings",
    "generate_openai_embeddings_batched",
    "get_openai_api_key",
]
