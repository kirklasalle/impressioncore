#!/usr/bin/env python3
"""Small runner: quick real-data smoke using F:/data/datasets

Runs a tiny training loop (few steps) on real text files using the
existing SimpleTransformerModel + SimpleTokenizer. This keeps changes
local and avoids editing the main training script.
"""
import argparse
import sys
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, IterableDataset

# make repo importable
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
    from training.scripts.train_768_128k_scaffold import ScaffoldConfig, SimpleTransformerModel


class RealStreamingDataset(IterableDataset):
    def __init__(self, data_root: Path, tok: SimpleTokenizer, seq_len: int):
        self.data_root = Path(data_root)
        self.tok = tok
        self.seq_len = seq_len

    def __iter__(self):
        for p in self.data_root.rglob('*.txt'):
            try:
                with open(p, encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                    full = self.tok.encode(text, max_len=len(text))
                    for i in range(0, max(1, len(full)), self.seq_len):
                        chunk = full[i:i+self.seq_len]
                        if len(chunk) < self.seq_len:
                            chunk = chunk + [0] * (self.seq_len - len(chunk))
                        yield torch.tensor(chunk, dtype=torch.long)
            except Exception:
                continue


def run_real_smoke(args):
    device = 'cpu' if args.cpu else ('cuda' if torch.cuda.is_available() else 'cpu')
    tok = SimpleTokenizer(args.vocab_size)
    cfg = ScaffoldConfig()
    cfg.embed_dim = args.embed_dim
    cfg.num_layers = args.num_layers
    cfg.max_seq_length = args.max_seq_length
    cfg.attn_type = args.attn_type
    cfg.window_size = args.window_size
    cfg.vocab_size = args.vocab_size
    cfg.device = device

    model = SimpleTransformerModel(cfg).to(device)
    model.train()
    optim_ = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)

    dataset = RealStreamingDataset(Path(args.data_root), tok, args.seq_len)
    loader = DataLoader(dataset, batch_size=args.batch_size, collate_fn=lambda b: torch.stack(b), num_workers=0)

    scaler = torch.cuda.amp.GradScaler(enabled=(not args.cpu and torch.cuda.is_available()))
    global_step = 0
    for batch in loader:
        batch = batch.to(device)
        labels = batch.clone()
        with torch.cuda.amp.autocast(enabled=scaler.is_enabled()):
            logits = model(batch)
            loss = nn.functional.cross_entropy(logits.view(-1, cfg.vocab_size), labels.view(-1))
        scaler.scale(loss).backward()
        scaler.step(optim_)
        scaler.update()
        optim_.zero_grad()
        global_step += 1  # noqa: SIM113
        print(f"step={global_step} loss={loss.item():.4f} device={device}")
        if global_step >= args.steps:
            print("Real-data smoke complete")
            return

    print("Real-data smoke ended (dataset exhausted)")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--data-root', type=Path, default=Path('F:/data/datasets'))
    p.add_argument('--steps', type=int, default=4)
    p.add_argument('--batch-size', type=int, default=1)
    p.add_argument('--seq-len', dest='seq_len', type=int, default=256)
    p.add_argument('--embed-dim', type=int, default=768)
    p.add_argument('--num-layers', type=int, default=2)
    p.add_argument('--max-seq-length', type=int, default=128000)
    p.add_argument('--vocab-size', type=int, default=16384)
    p.add_argument('--attn-type', type=str, default='rope', choices=['rope','alibi','window'])
    p.add_argument('--window-size', type=int, default=512)
    p.add_argument('--lr', type=float, default=2e-4)
    p.add_argument('--cpu', action='store_true')
    args = p.parse_args()
    run_real_smoke(args)
