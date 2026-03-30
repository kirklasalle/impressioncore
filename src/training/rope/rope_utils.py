"""RoPE utilities: compute inv_freq, build cos/sin caches, apply rotary, and rescale caches."""

import torch
import torch.nn.functional as F


def compute_inv_freq(dim: int, base: float = 10000.0) -> torch.Tensor:
    """Compute inverse frequencies for RoPE (half-dim). Returns shape (dim/2,)."""
    assert dim % 2 == 0, "RoPE dim must be even"
    half = dim // 2
    inv_freq = 1.0 / (base ** (torch.arange(0, half, dtype=torch.float32) / half))
    return inv_freq


def build_rope_cache(seq_len: int, dim: int, base: float = 10000.0, device=None) -> tuple[torch.Tensor, torch.Tensor]:
    """Build cos and sin caches for positions [0..seq_len-1].

    Returns cos, sin of shape (seq_len, dim//2)
    """
    inv_freq = compute_inv_freq(dim, base=base)
    if device is not None:
        inv_freq = inv_freq.to(device)
    positions = torch.arange(seq_len, dtype=torch.float32, device=inv_freq.device).unsqueeze(1)
    angles = positions * inv_freq.unsqueeze(0)
    cos = torch.cos(angles)
    sin = torch.sin(angles)
    return cos, sin


def apply_rope(x: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor) -> torch.Tensor:
    """Apply RoPE to tensor x with shape [batch, seq, dim].

    cos/sin expected shape: (seq, dim//2)
    """
    # x: [B, S, D]
    B, S, D = x.shape
    assert D % 2 == 0
    half = D // 2
    # reshape to [B, S, half, 2]
    x_pair = x.view(B, S, half, 2)
    # cos/sin -> [S, half] -> expand
    cos_e = cos.unsqueeze(0)  # [1, S, half]
    sin_e = sin.unsqueeze(0)
    x0 = x_pair[..., 0]
    x1 = x_pair[..., 1]
    x_rot0 = x0 * cos_e - x1 * sin_e
    x_rot1 = x1 * cos_e + x0 * sin_e
    x_rot = torch.stack([x_rot0, x_rot1], dim=-1)
    return x_rot.view(B, S, D)


def rescale_rope_cache_by_recompute(old_dim: int, new_seq_len: int, base: float = 10000.0, device=None) -> tuple[torch.Tensor, torch.Tensor]:
    """Recompute cos/sin for a new sequence length (preferred, numerically stable).

    This uses the same inv_freq computed from 'old_dim' to produce caches for new_seq_len.
    """
    inv_freq = compute_inv_freq(old_dim, base=base)
    if device is not None:
        inv_freq = inv_freq.to(device)
    positions = torch.arange(new_seq_len, dtype=torch.float32, device=inv_freq.device).unsqueeze(1)
    angles = positions * inv_freq.unsqueeze(0)
    return torch.cos(angles), torch.sin(angles)


def rescale_rope_cache_by_interp(old_cos: torch.Tensor, old_sin: torch.Tensor, new_seq_len: int) -> tuple[torch.Tensor, torch.Tensor]:
    """Linearly interpolate existing cos/sin caches along the sequence axis to new_seq_len.

    old_cos/sin shape: [old_seq, half]
    returns new cos/sin shape: [new_seq_len, half]
    """
    old_seq, _ = old_cos.shape
    # perform interpolation per-frequency using 1D linear interpolation
    # reshape for interpolation
    old_cos_t = old_cos.t().unsqueeze(0)  # [1, half, old_seq]
    old_sin_t = old_sin.t().unsqueeze(0)
    new_cos = F.interpolate(old_cos_t, size=new_seq_len, mode='linear', align_corners=False)
    new_sin = F.interpolate(old_sin_t, size=new_seq_len, mode='linear', align_corners=False)
    # back to [new_seq, half]
    new_cos = new_cos.squeeze(0).t()
    new_sin = new_sin.squeeze(0).t()
    return new_cos, new_sin
