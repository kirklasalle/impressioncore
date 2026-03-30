#!/usr/bin/env python3
"""Simple diagnostic to run a forward+backward on a synthetic batch and detect NaN/Inf.

Usage: python tools/diagnose_nan.py --checkpoint <path> [--fp16]
"""
import argparse
import os
from pathlib import Path

import torch
import torch.nn as nn

from src.core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model


def make_synthetic_batch(batch_size=4, seq_len=512, vocab_size=50257, embed_dim=768, device='cpu'):
    input_ids = torch.randint(0, vocab_size, (batch_size, seq_len), dtype=torch.long, device=device)
    labels = input_ids.clone()
    attention_mask = (input_ids != 0).long()
    image_embeddings = torch.zeros(batch_size, embed_dim, device=device)
    audio_embeddings = torch.zeros(batch_size, embed_dim, device=device)
    return {
        'input_ids': input_ids,
        'labels': labels,
        'attention_mask': attention_mask,
        'image_embeddings': image_embeddings,
        'audio_embeddings': audio_embeddings,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', required=True)
    parser.add_argument('--fp16', action='store_true')
    parser.add_argument('--batch-size', type=int, default=4)
    parser.add_argument('--seq-len', type=int, default=512)
    args = parser.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('Device:', device)

    cfg = B3Config(embed_dim=768, num_heads=12, num_layers=8, vocab_size=50257, num_experts=8, expert_dim=2048, experts_per_token=2, max_seq_length=512)
    model = ImpressionCoreB3Model(cfg).to(device)

    ckpt = torch.load(args.checkpoint, map_location=device)
    state = ckpt.get('model_state_dict', ckpt)
    try:
        model.load_state_dict(state)
        print('Loaded model state')
    except Exception as e:
        print('Model load_state_dict failed:', e)

    # create optimizer
    opt = torch.optim.AdamW(model.parameters(), lr=1e-4)

    scaler = None
    if args.fp16:
        scaler = torch.cuda.amp.GradScaler()

    batch = make_synthetic_batch(batch_size=args.batch_size, seq_len=args.seq_len, vocab_size=cfg.vocab_size, embed_dim=cfg.embed_dim, device=device)

    # forward
    model.train()
    try:
        if args.fp16:
            with torch.cuda.amp.autocast(device_type='cuda'):
                out = model(input_ids=batch['input_ids'], image_features=batch['image_embeddings'], audio_features=batch['audio_embeddings'], mask=batch['attention_mask'])
                logits = out['logits']
                loss = nn.CrossEntropyLoss()(logits.view(-1, cfg.vocab_size), batch['labels'].view(-1))
                loss_value = float(loss.item())
        else:
            out = model(input_ids=batch['input_ids'], image_features=batch['image_embeddings'], audio_features=batch['audio_embeddings'], mask=batch['attention_mask'])
            logits = out['logits']
            loss = nn.CrossEntropyLoss()(logits.view(-1, cfg.vocab_size), batch['labels'].view(-1))
            loss_value = float(loss.item())
    except Exception as e:
        print('Forward failed:', e)
        return

    print('Loss:', loss_value)
    ART = Path(os.environ.get('IMPRESSIONCORE_ARTIFACTS_DIR', 'F:/models/checkpoints/artifacts'))
    if (torch.isnan(torch.tensor(loss_value)) or torch.isinf(torch.tensor(loss_value))):
        print('Loss is NaN/Inf  dumping batch')
        ART.mkdir(parents=True, exist_ok=True)
        torch.save({'meta': {'loss': loss_value}, 'batch': {k: (v[:4].cpu() if torch.is_tensor(v) else v) for k, v in batch.items()}}, str(ART / 'bad_batch_diag.pt'))
        print(f'Saved {ART / "bad_batch_diag.pt"}')
        return

    # backward
    try:
        opt.zero_grad()
        if args.fp16 and scaler is not None:
            scaler.scale(loss).backward()
            scaler.unscale_(opt)
            # check grads
            found = False
            for p in model.parameters():
                if p.grad is not None and (torch.isnan(p.grad).any() or torch.isinf(p.grad).any()):
                    found = True
                    break
            if found:
                print('Detected NaN/Inf in grads during fp16 backward — dumping')
                ART.mkdir(parents=True, exist_ok=True)
                torch.save({'meta': {'stage': 'backward_fp16'}, 'batch': {k: (v[:4].cpu() if torch.is_tensor(v) else v) for k, v in batch.items()}}, str(ART / 'bad_batch_diag.pt'))
                return
            scaler.step(opt)
            scaler.update()
        else:
            loss.backward()
            # check grads
            found = False
            for p in model.parameters():
                if p.grad is not None and (torch.isnan(p.grad).any() or torch.isinf(p.grad).any()):
                    found = True
                    break
            if found:
                print('Detected NaN/Inf in grads during backward — dumping')
                ART.mkdir(parents=True, exist_ok=True)
                torch.save({'meta': {'stage': 'backward_fp32'}, 'batch': {k: (v[:4].cpu() if torch.is_tensor(v) else v) for k, v in batch.items()}}, str(ART / 'bad_batch_diag.pt'))
                return
            opt.step()
    except Exception as e:
        print('Backward/step failed:', e)
        ART.mkdir(parents=True, exist_ok=True)
        torch.save({'meta': {'exception': str(e)}, 'batch': {k: (v[:4].cpu() if torch.is_tensor(v) else v) for k, v in batch.items()}}, str(ART / 'bad_batch_diag.pt'))
        print(f'Saved dump due to exception -> {ART / "bad_batch_diag.pt"}')
        return

    print('Forward+backward completed without NaN/Inf')


if __name__ == '__main__':
    main()
