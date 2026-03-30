#!/usr/bin/env python3
"""Full training scaffold for 768-d model with 128k logical context support.

This script provides a streaming dataset loader (or synthetic smoke data),
AMP support, gradient accumulation, checkpointing, and a progressive curriculum flag.

Run smoke validation locally with:
  python train_full_768_128k.py --smoke

"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, IterableDataset

# Ensure repo src is importable
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))
try:
    from src.training.tokenizer.simple_tokenizer import SimpleTokenizer
except Exception:
    from training.tokenizer.simple_tokenizer import SimpleTokenizer

try:
    from src.training.scripts.train_768_128k_scaffold import ScaffoldConfig, SimpleTransformerModel
except Exception:
    # Fallback to relative import path
    from training.scripts.train_768_128k_scaffold import ScaffoldConfig, SimpleTransformerModel


DEFAULT_DATA_ROOT = Path('F:/data/datasets')
DEFAULT_CHECKPOINT_DIR = Path('F:/models/checkpoints/b3_39m_128k')


class SyntheticDataset(IterableDataset):
    def __init__(self, vocab_size, seq_len, total_samples=1000):
        self.vocab_size = vocab_size
        self.seq_len = seq_len
        self.total = total_samples

    def __iter__(self):
        for _ in range(self.total):
            yield torch.randint(0, self.vocab_size, (self.seq_len,), dtype=torch.long)


class StreamingTextDataset(IterableDataset):
    def __init__(self, data_root: Path, vocab_size: int, seq_len: int):
        self.data_root = Path(data_root)
        self.vocab_size = vocab_size
        self.seq_len = seq_len
        # tokenizer instance for deterministic tokenization
        self.tok = SimpleTokenizer(self.vocab_size)

    def __iter__(self):
        # Walk text files and yield sequences clipped/padded to seq_len
        for p in self.data_root.rglob('*.txt'):
            try:
                with open(p, encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                    # use simple tokenizer for deterministic tokenization
                    full = self.tok.encode(text, max_len=len(text))
                    for i in range(0, max(1, len(full)), self.seq_len):
                        chunk = full[i:i+self.seq_len]
                        if len(chunk) < self.seq_len:
                            chunk = chunk + [0] * (self.seq_len - len(chunk))
                        yield torch.tensor(chunk, dtype=torch.long)
            except Exception:
                continue


def save_checkpoint(state, out_dir: Path, step: int):
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    path = out_dir / f'ckpt_step_{step}_{ts}.pt'
    torch.save(state, path)
    return path


def estimate_resources(model: nn.Module, batch_size: int, seq_len: int):
    param_count = sum(p.numel() for p in model.parameters())
    # Very rough VRAM estimate: param storage + activations ~ param*4 bytes + batch*seq*embed*4
    embed = model.cfg.embed_dim
    est_bytes = param_count * 4 + batch_size * seq_len * embed * 4
    est_gb = est_bytes / (1024**3)
    return param_count, est_gb


def train(args):
    cfg = ScaffoldConfig()
    cfg.embed_dim = args.embed_dim
    cfg.num_layers = args.num_layers
    cfg.max_seq_length = args.max_seq_length
    cfg.attn_type = args.attn_type
    # window size and vocab size from args
    cfg.window_size = args.window_size
    cfg.vocab_size = args.vocab_size
    cfg.device = 'cpu' if args.cpu else ('cuda' if torch.cuda.is_available() else 'cpu')

    model = SimpleTransformerModel(cfg).to(cfg.device)

    # dataset
    if args.smoke:
        dataset = SyntheticDataset(cfg.vocab_size, args.seq_len, total_samples=10)
    else:
        dataset = StreamingTextDataset(args.data_root, cfg.vocab_size, args.seq_len)

    loader = DataLoader(dataset, batch_size=args.batch_size, collate_fn=lambda b: torch.stack(b), num_workers=0)

    optim = torch.optim.AdamW(model.parameters(), lr=args.lr)
    scaler = torch.cuda.amp.GradScaler(enabled=(not args.cpu and torch.cuda.is_available()))

    model.train()
    global_step = 0

    param_count, est_gb = estimate_resources(model, args.batch_size, args.seq_len)
    print(f"Model params: {param_count:,}; estimated memory per batch (approx): {est_gb:.2f} GB")

    for _epoch in range(args.epochs):
        for batch in loader:
            batch = batch.to(cfg.device)
            labels = batch.clone()
            with torch.cuda.amp.autocast(enabled=scaler.is_enabled()):
                logits = model(batch)
                loss = nn.functional.cross_entropy(logits.view(-1, cfg.vocab_size), labels.view(-1))

            scaler.scale(loss).backward()

            if (global_step + 1) % args.accumulate == 0:
                scaler.step(optim)
                scaler.update()
                optim.zero_grad()

            global_step += 1

            if global_step % args.save_every == 0:
                ckpt = {'step': global_step, 'model_state_dict': model.state_dict(), 'cfg': vars(cfg)}
                path = save_checkpoint(ckpt, args.checkpoint_dir, global_step)
                print(f"Saved checkpoint to {path}")

            if args.smoke and global_step >= 4:
                # short-circuit for smoke
                print(f"Smoke training complete at step {global_step}")
                return

    # final save
    ckpt = {'step': global_step, 'model_state_dict': model.state_dict(), 'cfg': vars(cfg)}
    path = save_checkpoint(ckpt, args.checkpoint_dir, global_step)
    print(f"Training complete. Final checkpoint: {path}")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--smoke', action='store_true', help='Run quick smoke training')
    p.add_argument('--cpu', action='store_true', help='Force CPU')
    p.add_argument('--data-root', type=Path, default=DEFAULT_DATA_ROOT)
    p.add_argument('--checkpoint-dir', type=Path, default=DEFAULT_CHECKPOINT_DIR)
    p.add_argument('--epochs', type=int, default=1)
    p.add_argument('--batch-size', type=int, default=1)
    p.add_argument('--seq-len', dest='seq_len', type=int, default=256)
    p.add_argument('--embed-dim', type=int, default=768)
    p.add_argument('--num-layers', type=int, default=4)
    p.add_argument('--max-seq-length', type=int, default=128000)
    p.add_argument('--vocab-size', type=int, default=16384)
    p.add_argument('--attn-type', type=str, default='rope', choices=['rope','alibi','window'], help='Attention backend to use')
    p.add_argument('--window-size', type=int, default=512, help='Window size for windowed attention')
    p.add_argument('--lr', type=float, default=2e-4)
    p.add_argument('--accumulate', type=int, default=1)
    p.add_argument('--save-every', type=int, default=50)
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    # ensure checkpoint dir
    args.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    train(args)
