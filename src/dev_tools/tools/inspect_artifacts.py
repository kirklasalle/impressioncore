import torch

files = [r'F:/models/checkpoints/artifacts/bad_batch_grad_norm_step_487.pt', r'F:/models/checkpoints/artifacts/bad_batch_grad_norm_step_483.pt']
for f in files:
    try:
        d = torch.load(f, map_location='cpu')
        print('FILE', f)
        print('META', d.get('meta'))
        for k in ('input_ids', 'attention_mask', 'labels'):
            v = d.get(k)
            if v is None:
                print('  ', k, '= None')
            else:
                print('  ', k, 'shape', getattr(v, 'shape', None), 'dtype', getattr(v, 'dtype', None))
    except Exception as e:
        print('LOAD ERROR', f, e)
