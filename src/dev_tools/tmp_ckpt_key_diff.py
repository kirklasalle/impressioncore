import json
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
src_root = repo_root / 'src'
sys.path.insert(0, str(src_root))
sys.path.insert(0, str(repo_root))

import torch


def make_b3config(cfg_obj):
    """Try to convert checkpoint config (dict or object) into local B3Config-compatible dict."""
    if cfg_obj is None:
        return None
    if isinstance(cfg_obj, dict):
        return cfg_obj
    # object with attributes
    try:
        return {k: getattr(cfg_obj, k) for k in dir(cfg_obj) if not k.startswith('_') and not callable(getattr(cfg_obj, k))}
    except Exception:
        return None


def main():
    ckpt_path = Path(r'F:\models\checkpoints\b3_39m\b3_39m_epoch_3.pt')
    out_json = Path(r'F:\data\embeddings\b3_39m\ckpt_model_key_diff.json')
    out_json.parent.mkdir(parents=True, exist_ok=True)

    print('Loading checkpoint:', ckpt_path)
    ckpt = torch.load(str(ckpt_path), map_location='cpu')

    # extract state_dict
    state_dict = None
    for k in ('model_state_dict', 'state_dict', 'model'):
        if k in ckpt:
            state_dict = ckpt[k]
            break
    if state_dict is None and isinstance(ckpt, dict):
        # maybe the dict itself is a state dict
        state_dict = ckpt

    if state_dict is None:
        print('Could not find a state_dict in checkpoint. Aborting.')
        return

    ckpt_config = ckpt.get('config', None)
    cfg_dict = make_b3config(ckpt_config)

    # import model classes
    try:
        from core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model
    except Exception as e:
        print('Failed to import model from core.models.impressioncore_b3_architecture:', e)
        print('Attempting alternative imports...')
        try:
            from core.models import impressioncore_b3_architecture as impmod
            B3Config = impmod.B3Config
            ImpressionCoreB3Model = impmod.ImpressionCoreB3Model
        except Exception as e2:
            print('Alternative import failed:', e2)
            print('Cannot instantiate local model for diagnostics. Exiting.')
            return

    # instantiate model with checkpoint config where possible
    model_cfg = None
    try:
        if cfg_dict is not None:
            # Filter keys that B3Config accepts
            try:
                model_cfg = B3Config(**{k: v for k, v in cfg_dict.items() if k in B3Config.__init__.__code__.co_varnames})
            except Exception:
                # fallback to passing dict directly if B3Config can accept it
                try:
                    model_cfg = B3Config(**cfg_dict)
                except Exception:
                    model_cfg = None
        if model_cfg is None:
            print('Warning: could not create B3Config from checkpoint config; instantiating with default B3Config()')
            model_cfg = B3Config()
    except Exception as e:
        print('Error while preparing B3Config:', e)
        model_cfg = B3Config()

    print('Instantiating local model...')
    model = ImpressionCoreB3Model(model_cfg)

    local_sd = model.state_dict()
    ckpt_keys = set(state_dict.keys())
    local_keys = set(local_sd.keys())

    shared = ckpt_keys & local_keys
    only_in_ckpt = sorted(list(ckpt_keys - local_keys))
    only_in_local = sorted(list(local_keys - ckpt_keys))

    # shape mismatches
    mismatches = []
    for k in sorted(shared):
        ck_shape = tuple(state_dict[k].shape) if hasattr(state_dict[k], 'shape') else None
        local_shape = tuple(local_sd[k].shape) if hasattr(local_sd[k], 'shape') else None
        if ck_shape != local_shape:
            mismatches.append({'key': k, 'ckpt_shape': ck_shape, 'local_shape': local_shape})

    # attempt to load with strict=False to capture missing/unexpected keys
    print('Running load_state_dict(strict=False) to collect missing/unexpected keys...')
    res = model.load_state_dict(state_dict, strict=False)
    missing = list(res.missing_keys) if hasattr(res, 'missing_keys') else []
    unexpected = list(res.unexpected_keys) if hasattr(res, 'unexpected_keys') else []

    report = {
        'checkpoint_path': str(ckpt_path),
        'num_ckpt_keys': len(ckpt_keys),
        'num_local_keys': len(local_keys),
        'only_in_checkpoint_count': len(only_in_ckpt),
        'only_in_local_count': len(only_in_local),
        'only_in_checkpoint': only_in_ckpt,
        'only_in_local': only_in_local,
        'num_shared_keys': len(shared),
        'shape_mismatches': mismatches,
        'missing_keys_from_load': missing,
        'unexpected_keys_from_load': unexpected,
    }

    with open(out_json, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, indent=2)

    print('Diagnostics written to', out_json)
    print('Summary: ckpt_keys=%d local_keys=%d shared=%d only_in_ckpt=%d only_in_local=%d mismatches=%d missing=%d unexpected=%d' % (  # noqa: UP031
        len(ckpt_keys), len(local_keys), len(shared), len(only_in_ckpt), len(only_in_local), len(mismatches), len(missing), len(unexpected)
    ))


if __name__ == '__main__':
    main()
