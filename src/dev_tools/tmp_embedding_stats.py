import glob
import json
import os

import numpy as np

out_dir = r'F:\data\embeddings\b3_39m'
files = sorted(glob.glob(os.path.join(out_dir, '*.npy')))
print('found', len(files), 'files')

groups = {}
bad_files = []
for f in files:
    try:
        a = np.load(f)
        # normalize common cases: 1D -> (D,), 2D with shape (1,D) -> (D,)
        if a.ndim == 2 and a.shape[0] == 1:
            a = a.reshape(-1)
        shape = tuple(a.shape)
        groups.setdefault(shape, []).append({'file': f, 'arr': a.astype(np.float32)})
    except Exception as e:
        bad_files.append({'file': f, 'error': str(e)})

report = {'file_count': len(files), 'shapes_found': sorted([list(s) for s in groups]), 'bad_files': bad_files, 'groups': {}}

for shape, items in groups.items():
    arrs = np.stack([it['arr'] for it in items], axis=0)
    g = {}
    g['count'] = int(arrs.shape[0])
    if arrs.ndim == 1:
        # single vector per file -> treat as (N,) stack created a (N,) array; reshape
        arrs = arrs.reshape(arrs.shape[0], -1)
    g['dim'] = int(arrs.shape[1]) if arrs.ndim == 2 else None
    # per-dim sample
    if g['dim'] is not None:
        g['per_dim_mean_sample'] = [float(x) for x in np.round(arrs.mean(axis=0)[:10], 6).tolist()]
        g['per_dim_std_sample'] = [float(x) for x in np.round(arrs.std(axis=0)[:10], 6).tolist()]
    # norms
    try:
        norms = np.linalg.norm(arrs.reshape(arrs.shape[0], -1), axis=1)
        g['norm_mean'] = float(np.round(norms.mean(), 6))
        g['norm_std'] = float(np.round(norms.std(), 6))
        g['norm_min'] = float(np.round(norms.min(), 6))
        g['norm_max'] = float(np.round(norms.max(), 6))
    except Exception as e:
        g['norm_error'] = str(e)
    # nan/inf
    g['nan_count'] = int(np.isnan(arrs).sum())
    g['inf_count'] = int(np.isinf(arrs).sum())
    # duplicates
    try:
        uniq = np.unique(np.round(arrs, 6), axis=0)
        g['unique_embeddings'] = int(uniq.shape[0])
        g['duplicate_count'] = int(arrs.shape[0] - uniq.shape[0])
    except Exception as e:
        g['unique_embeddings'] = 'error:' + str(e)
        g['duplicate_count'] = 'error'
    # sample pairwise cosine (subset)
    try:
        m = min(200, arrs.shape[0])
        if m > 1 and g.get('dim'):
            sub = arrs[:m]
            norms_sub = np.linalg.norm(sub, axis=1, keepdims=True)
            norms_sub[norms_sub == 0] = 1.0
            subn = sub / norms_sub
            cos = (subn @ subn.T)
            s = (cos.sum() - m) / (m * (m - 1))
            g['sample_pairwise_cosine_mean'] = float(np.round(s, 6))
        else:
            g['sample_pairwise_cosine_mean'] = None
    except Exception as e:
        g['sample_pairwise_cosine_mean'] = 'error:' + str(e)

    # PCA hint
    try:
        from sklearn.decomposition import PCA
        pca = PCA(n_components=min(5, arrs.shape[1], arrs.shape[0]))
        pca.fit(arrs.reshape(arrs.shape[0], -1))
        g['pca_explained_variance_ratio'] = [float(x) for x in np.round(pca.explained_variance_ratio_.tolist(), 6)]
    except Exception as e:
        g['pca_explained_variance_ratio'] = 'sklearn_missing_or_error:' + str(e)

    # list sample files (first 5)
    g['sample_files'] = [it['file'] for it in items[:5]]
    report['groups'][str(shape)] = g

with open(os.path.join(out_dir, 'stats_report.json'), 'w') as fh:
    json.dump(report, fh, indent=2)

# print short summary
print('Report written to', os.path.join(out_dir, 'stats_report.json'))
for shape, g in report['groups'].items():
    print('Shape', shape, 'count', g['count'], 'dim', g.get('dim'), 'norm_mean', g.get('norm_mean'))
