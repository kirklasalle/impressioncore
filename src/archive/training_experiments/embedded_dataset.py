import json
from pathlib import Path
import numpy as np
from torch.utils.data import Dataset


class PrecomputedEmbeddingDataset(Dataset):
    """Loads a memory-mapped embeddings.npy and optional ids list.

    Returns (embedding, embedding) pairs by default (reconstruction task).
    If you have labels, supply a dict path mapping ids -> label and set label_key.
    """
    def __init__(self, multimodal_dir: str = r'F:/models/embeddings/b3_39m_128k/multimodal_batches', limit: int = None):
        self.dir = Path(multimodal_dir)
        self.emb_path = self.dir / 'embeddings.npy'
        self.ids_path = self.dir / 'ids.json'
        if not self.emb_path.exists():
            raise FileNotFoundError(f'Embeddings file not found: {self.emb_path}')
        self.emb = np.load(str(self.emb_path), mmap_mode='r')
        if self.ids_path.exists():
            with open(self.ids_path, 'r', encoding='utf-8') as f:
                self.ids = json.load(f)
        else:
            self.ids = None
        self.total = self.emb.shape[0]
        if limit is not None:
            self.total = min(self.total, int(limit))

    def __len__(self):
        return int(self.total)

    def __getitem__(self, idx):
        # return embedding as float32
        vec = self.emb[idx].astype('float32')
        # default supervised target is the vector itself (reconstruction)
        return vec, vec
