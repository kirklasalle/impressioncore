import torch
import torch.nn as nn
from src.core.models.impressioncore_b3_architecture import AssemblyOfExperts, B3Config
from src.training.b3_unified_training_pipeline import TrainingConfig
import numpy as np

def debug_aoe():
    t_config = TrainingConfig()
    model = AssemblyOfExperts(
        t_config.embed_dim,
        t_config.num_experts,
        t_config.expert_dim,
        t_config.experts_per_token,
        num_heads=t_config.num_heads
    ).cuda()

    # Load weights from checkpoint to reproduce failure
    ckpt_path = r'F:\data\training\checkpoints\b3_pretraining\b3_interrupted_step_690_20260124_120335.pth'
    checkpoint = torch.load(ckpt_path)

    sd = checkpoint.get('model_state_dict', checkpoint)
    block_sd = {k.replace('b3_model.layers.0.aoe.', ''): v for k, v in sd.items() if 'b3_model.layers.0.aoe.' in k}
    if block_sd:
        model.load_state_dict(block_sd, strict=True)
        print("Loaded weights for Layer 0 AoE")

    # Dummy batch
    x = torch.randn(1, 128, t_config.embed_dim).cuda()

    # Hook to check magnitudes
    def hook_fn(module, input, output):
        if isinstance(output, tuple):
            out = output[0]
        else:
            out = output
        max_val = out.abs().max().item()
        print(f"Layer: {module.__class__.__name__}, Max: {max_val:.4f}, HasNaN: {torch.isnan(out).any().item()}, NearNF: {max_val > 65000}")

    # Register hooks on interesting parts
    model.router.register_forward_hook(hook_fn)
    model.output_norm.register_forward_hook(hook_fn)
    for i, expert in enumerate(model.experts):
        expert.register_forward_hook(hook_fn)

    print("--- Forward Pass ---")
    out, loss = model(x)
    print(f"Final Out Max: {out.abs().max().item()}, Loss: {loss.item()}")

    print("\n--- Backward Pass ---")
    loss_sum = out.sum() + loss
    loss_sum.backward()

    for name, param in model.named_parameters():
        if param.grad is not None:
            print(f"Param: {name}, Grad Max: {param.grad.abs().max().item()}, HasNaN: {torch.isnan(param.grad).any().item()}")

if __name__ == "__main__":
    debug_aoe()
