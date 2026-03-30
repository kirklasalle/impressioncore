
import torch
import sys

def check_checkpoint(path):
    print(f"Checking {path}...")
    try:
        checkpoint = torch.load(path, map_location='cpu')
        state_dict = checkpoint.get('model_state_dict', {})

        has_nan = False
        nan_layers = []

        for name, param in state_dict.items():
            if torch.isnan(param).any():
                has_nan = True
                nan_layers.append(name)
                print(f"NaN found in: {name}")
            elif torch.isinf(param).any():
                print(f"Inf found in: {name}")

        if not has_nan:
            print("No NaNs found in model parameters.")
        else:
            print(f"Total layers with NaN: {len(nan_layers)}")

        print(f"Step: {checkpoint.get('global_step', 'Unknown')}")
        print(f"Epoch: {checkpoint.get('epoch', 'Unknown')}")
        print(f"Best Quality: {checkpoint.get('best_quality', 'Unknown')}")

    except Exception as e:
        print(f"Error loading checkpoint: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_checkpoint(sys.argv[1])
    else:
        # Default to the one it resumed from
        check_checkpoint("F:/data/training/checkpoints/b3_pretraining/b3_step_7499_20260123_185418.pth")
