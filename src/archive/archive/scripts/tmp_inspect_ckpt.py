import torch, json
ck='F:/models/checkpoints/b3_39m/b3_39m_epoch_3.pt'
ckdata=torch.load(ck,map_location='cpu')
print('TOP_KEYS:', list(ckdata.keys())[:20])
if 'config' in ckdata:
    cfg=ckdata['config']
    print('CONFIG TYPE:', type(cfg))
    try:
        if isinstance(cfg, dict):
            print(json.dumps(cfg, indent=2))
        else:
            # dataclass or object
            d=getattr(cfg,'__dict__',str(cfg))
            print('CONFIG __dict__:', d)
    except Exception as e:
        print('CONFIG PRINT ERROR:', e)

if 'model_state_dict' in ckdata:
    sd=ckdata['model_state_dict']
else:
    # maybe keys at top are state_dict
    sd={k:v for k,v in ckdata.items() if isinstance(v, torch.Tensor)}

print('STATE_DICT sample keys:', list(sd.keys())[:40])
# try to find some important shapes
shapes={}
for k,v in sd.items():
    shapes[k]=tuple(v.shape)
# print a few known keys if present
for key in ['lm_head.weight','token_embedding.weight','layers.0.mla.q_proj.weight','layers.0.aoe.experts.0.0.weight']:
    for k in shapes:
        if key in k:
            print(k, shapes[k])
# gather unique first-dim sizes
first_dims=set()
for k,s in shapes.items():
    if len(s)>=1:
        first_dims.add(s[0])
print('unique first-dim sizes (sample):', sorted(list(first_dims))[:30])
# print lm_head if present
for k,s in shapes.items():
    if 'lm_head.weight' in k:
        print('lm_head.weight shape:', s)
        break
print('Done')
