import json
from pathlib import Path

import torch


def make_json_safe(obj, _depth=0):
    # convert common simple types
    try:
        if obj is None:
            return None
        if isinstance(obj, bool | int | float | str):
            return obj
        if isinstance(obj, list | tuple):
            return [make_json_safe(x, _depth+1) for x in obj]
        if isinstance(obj, dict):
            out = {}
            for k, v in obj.items():
                try:
                    out[str(k)] = make_json_safe(v, _depth+1)
                except Exception:
                    out[str(k)] = repr(v)[:200]
            return out
        # tensors -> shape
        import torch as _torch
        if isinstance(obj, _torch.Tensor):
            return {'__tensor_shape__': list(obj.shape), 'dtype': str(obj.dtype)}
        # objects: try to extract attributes
        if _depth > 4:
            return repr(obj)[:400]
        attrs = {}
        for name in dir(obj):
            if name.startswith('_'):
                continue
            try:
                val = getattr(obj, name)
            except Exception:
                continue
            if callable(val):
                continue
            try:
                attrs[name] = make_json_safe(val, _depth+1)
            except Exception:
                attrs[name] = repr(val)[:400]
        if attrs:
            return attrs
        return repr(obj)[:400]
    except Exception:
        return repr(obj)[:400]


def main():
    scan_path = Path(r'F:\data\embeddings\b3_39m\ckpt_scan.json')
    out_dir = Path(r'F:\data\embeddings\b3_39m\config_dumps')
    out_dir.mkdir(parents=True, exist_ok=True)

    if not scan_path.exists():
        print('Missing scan file at', scan_path)
        return

    entries = json.loads(scan_path.read_text(encoding='utf-8'))
    candidates = [e['path'] for e in entries if e.get('embed_dim_reported') == 768]
    if not candidates:
        print('No 768-d checkpoints found in scan.')
        return

    index = []
    for p in candidates:
        p = Path(p)
        print('Processing', p)
        try:
            ck = torch.load(str(p), map_location='cpu')
        except Exception as e:
            print(' load error', e)
            index.append({'path': str(p), 'error': repr(e)})
            continue

        cfg = None
        if isinstance(ck, dict):
            cfg = ck.get('config')
        dump = None
        if cfg is None:
            # try to infer from state_dict keys
            dump = {'note': 'no config saved', 'top_keys': list(ck.keys()) if isinstance(ck, dict) else []}
        else:
            dump = make_json_safe(cfg)

        out_file = out_dir / (p.stem + '_config.json')
        try:
            with open(out_file, 'w', encoding='utf-8') as fh:
                json.dump({'path': str(p), 'config_dump': dump}, fh, indent=2)
            index.append({'path': str(p), 'dump_file': str(out_file)})
        except Exception as e:
            index.append({'path': str(p), 'error': repr(e)})

    # write index
    idx_file = out_dir / 'index.json'
    with open(idx_file, 'w', encoding='utf-8') as fh:
        json.dump(index, fh, indent=2)
    print('Wrote', idx_file)


if __name__ == '__main__':
    main()
