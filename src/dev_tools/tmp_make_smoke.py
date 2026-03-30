import json
from pathlib import Path

import numpy as np

p = Path('src/memlog')
p.mkdir(parents=True, exist_ok=True)
# deterministic rng
rng = np.random.default_rng(12345)
N = 64
D = 128
emb = rng.standard_normal(size=(N, D)).astype('float32')
np_path = p / 'smoke_embeddings.npy'
np.save(np_path, emb)
# create manifest pointing to the file (relative path)
manifest_path = p / 'sample_manifest.ndjson'
with open(manifest_path, 'w', encoding='utf-8') as f:
    for i in range(N):
        obj = {'id': f'sample_{i}', 'path': str(np_path), 'text': f'sample document {i}', 'embedding_dim': D}
        f.write(json.dumps(obj) + "\n")
print('wrote', np_path, 'and', manifest_path)
