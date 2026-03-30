import logging

logger = logging.getLogger(__name__)

# Suppress SWIG warnings from Faiss if possible, or usually handled by logger config
HAS_FAISS = False
try:
    import faiss
    HAS_FAISS = True
except ImportError:
    pass

def get_faiss_index(dimension: int, use_gpu: bool = False, metric="l2"):
    """
    Safely returns a Faiss index, handling GPU/CPU fallbacks and warnings.
    """
    if not HAS_FAISS:
        raise ImportError("faiss module not found. Install faiss-cpu or faiss-gpu.")

    # Optimized CPU Index (Exact Search)
    if metric == "l2":
        index = faiss.IndexFlatL2(dimension)
    elif metric == "ip":
        index = faiss.IndexFlatIP(dimension)
    else:
        raise ValueError(f"Unknown metric: {metric}")

    if use_gpu:
        # Attempt to transfer to GPU
        try:
            # Check for Standard GPU Faiss Support
            if hasattr(faiss, "StandardGpuResources"):
                res = faiss.StandardGpuResources()
                index = faiss.index_cpu_to_gpu(res, 0, index)
            else:
                logger.warning("GPU Faiss requested but StandardGpuResources not found. Using CPU.")
        except Exception as e:
            logger.warning(f"Failed to move Faiss index to GPU: {e}. Falling back to CPU.")
            # Fallback is just the original CPU index
            pass

    return index
