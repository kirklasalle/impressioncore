import json
from pathlib import Path

import faiss
import numpy as np
import torch

from src.inference.embedder import UnifiedEmbedder
from src.inference.embedding_head_loader import load_best_head


class ProductionIndex:
    """Loads Faiss index + ids + (optional) raw embeddings and a query pipeline.

    Optionally applies the production reconstruction head (v1) to query vectors
    before search. This can slightly align distribution if the index was built
    on transformed embeddings.
    """
    def __init__(self,
                 multimodal_dir: str = r'F:/data/embeddings/b3_39m_128k/multimodal_batches',
                 ckpt_path: str = r'F:/models/checkpoints/b3_39m_128k/ckpt_step_3500_20250903_124926.pt',
                 device: str | None = None,
                 recon_head_dir: str | None = r'F:/models/production/embedding_head_v1',
                 apply_reconstruction: bool = True):
        self.dir = Path(multimodal_dir)
        self.emb_path = self.dir / 'embeddings.npy'
        self.ids_path = self.dir / 'ids.json'
        self.faiss_path = self.dir / 'embeddings.faiss'

        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.device = device

        # load ids list
        with open(self.ids_path, encoding='utf-8') as f:
            self.ids = json.load(f)

        # load embeddings memmap for optional exact scoring
        if self.emb_path.exists():
            self.embeddings = np.load(str(self.emb_path), mmap_mode='r')
        else:
            self.embeddings = None

        # load faiss
        if self.faiss_path.exists():
            self.index = faiss.read_index(str(self.faiss_path))
        else:
            raise FileNotFoundError(f'Faiss index not found at {self.faiss_path}')

        # loader/encoder for queries
        self.embedder = UnifiedEmbedder(ckpt_path=ckpt_path, device=self.device)

        # Optional reconstruction head
        self.recon = None
        if apply_reconstruction and recon_head_dir:
            try:
                self.recon = load_best_head(recon_head_dir, map_location='cpu').to(self.device).eval()
            except Exception as e:
                print(f"[WARN] Failed to load reconstruction head from {recon_head_dir}: {e}")
                self.recon = None

    def _maybe_transform(self, v: torch.Tensor | np.ndarray):
        if self.recon is None:
            return v
        t = torch.from_numpy(v).to(self.device) if isinstance(v, np.ndarray) else v.to(self.device)
        with torch.no_grad():
            out = self.recon(t)
        return out.detach().cpu().numpy() if not isinstance(v, torch.Tensor) else out

    def query_text(self, text: str, k: int = 10):
        vec = self.embedder.embed_text_long(text, seq_len=512)
        vec = self._maybe_transform(vec)
        q = np.asarray(vec, dtype='float32').reshape(1, -1)
        D, I = self.index.search(q, k)
        results = []
        for dist, idx in zip(D[0], I[0]):
            if idx < 0 or idx >= len(self.ids):
                results.append({'id': None, 'dist': float(dist)})
            else:
                results.append({'id': self.ids[idx], 'dist': float(dist)})
        return results

    def query_unified(self, text=None, img_path=None, audio_waveform=None, k: int = 10):
        vec = self.embedder.embed_unified(text=text, img_path=img_path, audio_waveform=audio_waveform)
        vec = self._maybe_transform(vec)
        q = np.asarray(vec, dtype='float32').reshape(1, -1)
        D, I = self.index.search(q, k)
        results = [{'id': (None if i<0 or i>=len(self.ids) else self.ids[i]), 'dist': float(d)} for d,i in zip(D[0], I[0])]
        return results
