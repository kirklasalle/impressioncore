import json
import os

import numpy as np

try:
    import torch
    from torch.utils.data import Dataset
except Exception:
    torch = None
    Dataset = object


class ShardDataset(Dataset):
    """Dataset that reads vectors from numpy shard files created by the extraction step.

    Expects shard index NDJSON at `index_path` with lines: {"dataset": <id>, "shard": <int>, "offset": <int>}.
    Shards are numpy .npy files named `shard_{i:03d}.npy` in shard_dir.
    """

    def __init__(self, index_path: str = "src/memlog/shards/index.jsonl", shard_dir: str = "src/memlog/shards"):
        if torch is None:
            raise RuntimeError("torch not available in this environment; install PyTorch in the .venv310")
        self.index_path = index_path
        self.shard_dir = shard_dir
        self.entries: list[tuple[str, int, int]] = []  # (dataset, shard, offset)
        with open(index_path, encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                self.entries.append((rec["dataset"], int(rec["shard"]), int(rec["offset"])))

        # lazy load memmaps
        self._shards = {}

    def _load_shard(self, shard: int):
        if shard in self._shards:
            return self._shards[shard]
        path = os.path.join(self.shard_dir, f"shard_{shard:03d}.npy")
        arr = np.load(path, mmap_mode="r")
        # keep as numpy memmap-like array
        self._shards[shard] = arr
        return arr

    def __len__(self) -> int:
        return len(self.entries)

    def __getitem__(self, idx: int):
        ds, shard, offset = self.entries[idx]
        arr = self._load_shard(shard)
        vec = arr[offset]
        # convert to torch tensor
        return torch.from_numpy(np.asarray(vec, dtype=np.float32)), ds


def collate_fn(batch):
    # batch is list of (tensor, dataset_id)
    xs = [b[0].unsqueeze(0) for b in batch]
    ids = [b[1] for b in batch]
    x = torch.cat(xs, dim=0)
    return x, ids
