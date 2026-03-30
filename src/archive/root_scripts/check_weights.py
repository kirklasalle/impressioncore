import torch

path = r'F:\data\training\checkpoints\b3_pretraining\b3_interrupted_step_690_20260124_120335.pth'
checkpoint = torch.load(path)

nan_params = []
inf_params = []
stat_summary = []

state_dict = checkpoint.get('model_state_dict', checkpoint)

for name, param in state_dict.items():
    if 'expert_usage' in name:
        print(f"DEBUG: {name} = {param}")
    if torch.isnan(param).any():
        nan_params.append(name)
    if torch.isinf(param).any():
        inf_params.append(name)
    stat_summary.append(f"{name}: Max={param.abs().max().item():.4f}, Mean={param.mean().item():.4f}")

print(f"Total Parameters: {len(state_dict)}")
print(f"NaN Parameters: {len(nan_params)}")
if nan_params:
    print(f"First 10 NaN: {nan_params[:10]}")
print(f"Inf Parameters: {len(inf_params)}")
if inf_params:
    print(f"First 10 Inf: {inf_params[:10]}")

if not nan_params and not inf_params:
    print("Checkpoint is numerically valid (no NaN/Inf in weights).")
    print("\nSample Stats:")
    for s in stat_summary[:10]:
        print(s)
