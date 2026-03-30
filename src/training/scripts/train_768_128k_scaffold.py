#!/usr/bin/env python3
"""Clean scaffold: supports RoPE, ALiBi, and Windowed attention for smoke testing.

Run with --smoke to execute a quick forward/backward pass.
"""
import argparse
import math
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.optim as optim

from training.rope.rope_utils import apply_rope, rescale_rope_cache_by_recompute


@dataclass
class ScaffoldConfig:
    embed_dim: int = 768
    num_layers: int = 2
    num_heads: int = 12
    ff_dim: int = 2048
    dropout: float = 0.1
    vocab_size: int = 16384
    max_seq_length: int = 128000
    device: str = 'cuda' if torch.cuda.is_available() else 'cpu'
    attn_type: str = 'rope'  # 'rope' | 'alibi' | 'window'
    window_size: int = 512


class ExtendablePositionalEmbedding(nn.Module):
    def __init__(self, max_len: int, dim: int):
        super().__init__()
        self.dim = dim
        self.max_len = max_len
        self.pos_emb = nn.Parameter(torch.randn(max_len, dim) * 0.02)

    def forward(self, seq_len: int):
        if seq_len <= self.max_len:
            return self.pos_emb[:seq_len]
        old = self.pos_emb.data
        new = nn.functional.interpolate(old.unsqueeze(0).permute(0,2,1), size=seq_len, mode='linear', align_corners=False)
        return new.squeeze(0).permute(1,0)


class RoPEBlock(nn.Module):
    def __init__(self, embed_dim: int, num_heads: int, ff_dim: int, dropout: float = 0.1, cfg: ScaffoldConfig | None=None):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        assert self.head_dim * num_heads == embed_dim
        self.q_proj = nn.Linear(embed_dim, embed_dim)
        self.k_proj = nn.Linear(embed_dim, embed_dim)
        self.v_proj = nn.Linear(embed_dim, embed_dim)
        self.out_proj = nn.Linear(embed_dim, embed_dim)
        self.ln1 = nn.LayerNorm(embed_dim)
        self.ln2 = nn.LayerNorm(embed_dim)
        self.ffn = nn.Sequential(nn.Linear(embed_dim, ff_dim), nn.GELU(), nn.Linear(ff_dim, embed_dim), nn.Dropout(dropout))
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor):
        B, S, D = x.shape
        q = self.q_proj(self.ln1(x)).view(B, S, self.num_heads, self.head_dim).permute(0,2,1,3)
        k = self.k_proj(self.ln1(x)).view(B, S, self.num_heads, self.head_dim).permute(0,2,1,3)
        v = self.v_proj(self.ln1(x)).view(B, S, self.num_heads, self.head_dim).permute(0,2,1,3)

        q = q.reshape(B * self.num_heads, S, self.head_dim)
        k = k.reshape(B * self.num_heads, S, self.head_dim)
        q = apply_rope(q, cos, sin)
        k = apply_rope(k, cos, sin)
        q = q.view(B, self.num_heads, S, self.head_dim)
        k = k.view(B, self.num_heads, S, self.head_dim)
        v = v.view(B, self.num_heads, S, self.head_dim)

        qk = torch.einsum('bhqd,bhkd->bhqk', q, k)
        scale = 1.0 / math.sqrt(self.head_dim)
        attn = torch.softmax(qk * scale, dim=-1)
        out = torch.einsum('bhqk,bhkd->bhqd', attn, v)
        out = out.permute(0,2,1,3).contiguous().view(B, S, D)
        out = self.out_proj(out)
        out = self.dropout(out)
        x = x + out
        x = x + self.ffn(self.ln2(x))
        return x


class ALiBiBlock(nn.Module):
    def __init__(self, embed_dim: int, num_heads: int, ff_dim: int, dropout: float = 0.1, cfg: ScaffoldConfig | None=None):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        assert self.head_dim * num_heads == embed_dim
        self.q_proj = nn.Linear(embed_dim, embed_dim)
        self.k_proj = nn.Linear(embed_dim, embed_dim)
        self.v_proj = nn.Linear(embed_dim, embed_dim)
        self.out_proj = nn.Linear(embed_dim, embed_dim)
        self.ln1 = nn.LayerNorm(embed_dim)
        self.ln2 = nn.LayerNorm(embed_dim)
        self.ffn = nn.Sequential(nn.Linear(embed_dim, ff_dim), nn.GELU(), nn.Linear(ff_dim, embed_dim), nn.Dropout(dropout))
        self.dropout = nn.Dropout(dropout)

    def _alibi_bias(self, seq_len: int, device: torch.device):
        """Return ALiBi bias tensor with shape [H, S, S].

        Each attention head uses a different linear slope applied to relative
        distances. This implementation follows a common heuristic for slopes.
        """
        # Per-head slopes (heuristic). Compute on device.
        ar = torch.arange(self.num_heads, device=device, dtype=torch.float32)
        slopes = 1.0 / (2.0 ** (ar / float(self.num_heads)))
        pos = torch.arange(seq_len, device=device, dtype=torch.float32)
        # relative distance = i - j, shape [S, S]
        rel = pos.view(1, -1) - pos.view(-1, 1)
        # per-head scaling -> [H, S, S]
        bias = slopes.view(self.num_heads, 1, 1) * rel.unsqueeze(0)
        return bias

    def forward(self, x: torch.Tensor, seq_len: int | None = None):
        B, S, D = x.shape
        if seq_len is None:
            seq_len = S

        q = self.q_proj(self.ln1(x)).view(B, S, self.num_heads, self.head_dim).permute(0,2,1,3)
        k = self.k_proj(self.ln1(x)).view(B, S, self.num_heads, self.head_dim).permute(0,2,1,3)
        v = self.v_proj(self.ln1(x)).view(B, S, self.num_heads, self.head_dim).permute(0,2,1,3)

        qk = torch.einsum('bhqd,bhkd->bhqk', q, k)
        bias = self._alibi_bias(seq_len, x.device)  # [H, S, S]
        bias = bias.unsqueeze(0)  # [1, H, S, S]
        scale = 1.0 / math.sqrt(self.head_dim)
        qk = qk * scale + bias

        mask = torch.triu(torch.ones((S, S), dtype=torch.bool, device=x.device), diagonal=1)
        qk = qk.masked_fill(mask.unsqueeze(0).unsqueeze(0), float('-inf'))
        attn = torch.softmax(qk, dim=-1)

        out = torch.einsum('bhqk,bhkd->bhqd', attn, v)
        out = out.permute(0,2,1,3).contiguous().view(B, S, D)
        out = self.out_proj(out)
        out = self.dropout(out)
        x = x + out
        x = x + self.ffn(self.ln2(x))
        return x


class WindowedBlock(nn.Module):
    def __init__(self, embed_dim: int, num_heads: int, ff_dim: int, dropout: float = 0.1, cfg: ScaffoldConfig | None=None):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        assert self.head_dim * num_heads == embed_dim
        self.window_size = cfg.window_size if cfg is not None else 512
        self.q_proj = nn.Linear(embed_dim, embed_dim)
        self.k_proj = nn.Linear(embed_dim, embed_dim)
        self.v_proj = nn.Linear(embed_dim, embed_dim)
        self.out_proj = nn.Linear(embed_dim, embed_dim)
        self.ln1 = nn.LayerNorm(embed_dim)
        self.ln2 = nn.LayerNorm(embed_dim)
        self.ffn = nn.Sequential(nn.Linear(embed_dim, ff_dim), nn.GELU(), nn.Linear(ff_dim, embed_dim), nn.Dropout(dropout))
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, seq_len: int | None = None):
        B, S, D = x.shape
        if seq_len is None:
            seq_len = S
        q = self.q_proj(self.ln1(x)).view(B, S, self.num_heads, self.head_dim).permute(0,2,1,3)
        k = self.k_proj(self.ln1(x)).view(B, S, self.num_heads, self.head_dim).permute(0,2,1,3)
        v = self.v_proj(self.ln1(x)).view(B, S, self.num_heads, self.head_dim).permute(0,2,1,3)
        # accumulate outputs into a buffer and average overlapping contributions
        out_buf = x.new_zeros((B, self.num_heads, S, self.head_dim))
        count_buf = x.new_zeros((1, 1, S, 1))
        # use overlapping windows to reduce boundary artifacts
        step = max(1, self.window_size // 2)
        for start in range(0, S, step):
            end = min(S, start + self.window_size)
            q_slice = q[:, :, start:end, :]
            k_slice = k[:, :, start:end, :]
            v_slice = v[:, :, start:end, :]
            qk = torch.einsum('bhqd,bhkd->bhqk', q_slice, k_slice)
            scale = 1.0 / math.sqrt(self.head_dim)
            # apply causal mask within window
            local_s = q_slice.size(2)
            mask = torch.triu(torch.ones((local_s, local_s), dtype=torch.bool, device=x.device), diagonal=1)
            qk = qk * scale
            qk = qk.masked_fill(mask.unsqueeze(0).unsqueeze(0), float('-inf'))
            attn = torch.softmax(qk, dim=-1)
            out = torch.einsum('bhqk,bhkd->bhqd', attn, v_slice)
            # write into buffer
            out_buf[:, :, start:end, :] += out
            count_buf[:, :, start:end, :] += 1.0
        # avoid divide-by-zero
        count_buf = count_buf.clamp(min=1.0)
        out = out_buf / count_buf
        out = out.permute(0,2,1,3).contiguous().view(B, S, D)
        out = self.out_proj(out)
        out = self.dropout(out)
        x = x + out
        x = x + self.ffn(self.ln2(x))
        return x


class SimpleTransformerModel(nn.Module):
    def __init__(self, cfg: ScaffoldConfig):
        super().__init__()
        self.cfg = cfg
        self.token_emb = nn.Embedding(cfg.vocab_size, cfg.embed_dim)
        self.pos_emb = ExtendablePositionalEmbedding(cfg.max_seq_length, cfg.embed_dim)
        if cfg.attn_type == 'rope':
            Block = RoPEBlock
        elif cfg.attn_type == 'alibi':
            Block = ALiBiBlock
        elif cfg.attn_type == 'window':
            Block = WindowedBlock
        else:
            raise ValueError('unknown attn_type')
        self.blocks = nn.ModuleList([Block(cfg.embed_dim, cfg.num_heads, cfg.ff_dim, cfg.dropout, cfg) for _ in range(cfg.num_layers)])
        self.ln = nn.LayerNorm(cfg.embed_dim)
        self.head = nn.Linear(cfg.embed_dim, cfg.vocab_size)

    def forward(self, input_ids):
        _, s = input_ids.shape
        x = self.token_emb(input_ids)
        pos = self.pos_emb(s).unsqueeze(0)
        x = x + pos
        if self.cfg.attn_type == 'rope':
            head_dim = self.cfg.embed_dim // self.cfg.num_heads
            cos, sin = rescale_rope_cache_by_recompute(head_dim, s, device=x.device)
            for blk in self.blocks:
                x = blk(x, cos, sin)
        elif self.cfg.attn_type == 'alibi' or self.cfg.attn_type == 'window':
            for blk in self.blocks:
                x = blk(x, seq_len=s)
        x = self.ln(x)
        logits = self.head(x)
        return logits


def smoke_run(args):
    cfg = ScaffoldConfig()
    cfg.num_layers = 2
    cfg.max_seq_length = 2048
    cfg.device = 'cpu' if args.cpu else cfg.device
    model = SimpleTransformerModel(cfg).to(cfg.device)
    model.train()
    batch = 2
    seq_len = 256
    input_ids = torch.randint(0, cfg.vocab_size, (batch, seq_len), dtype=torch.long, device=cfg.device)
    labels = input_ids.clone()
    optimizer = optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.01)
    logits = model(input_ids)
    loss = nn.functional.cross_entropy(logits.view(-1, cfg.vocab_size), labels.view(-1))
    loss.backward()
    optimizer.step()
    print(f"Smoke run complete — loss: {loss.item():.4f} device={cfg.device} seq_len={seq_len} model_param_count={sum(p.numel() for p in model.parameters()):,}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--smoke', action='store_true')
    p.add_argument('--cpu', action='store_true')
    args = p.parse_args()
    if args.smoke:
        smoke_run(args)
    else:
        print('Run with --smoke to validate quickly')


if __name__ == '__main__':
    main()
