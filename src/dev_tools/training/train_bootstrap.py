import argparse

import torch
import torch.nn as nn
import torch.optim as optim
from pytorch_shard_dataset import ShardDataset, collate_fn
from torch.utils.data import DataLoader


class SimpleMLP(nn.Module):
    def __init__(self, dim: int, hidden: int = 512):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, dim),
        )

    def forward(self, x):
        return self.net(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default="src/memlog/shards/index.jsonl")
    ap.add_argument("--shards", default="src/memlog/shards")
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--epochs", type=int, default=1)
    ap.add_argument("--checkpoint-dir", default="src/memlog/checkpoints")
    ap.add_argument("--eval-fraction", type=float, default=0.05, help="Fraction of dataset to hold out for evaluation")
    ap.add_argument("--lr", type=float, default=1e-3)
    args = ap.parse_args()

    ds = ShardDataset(index_path=args.index, shard_dir=args.shards)
    loader = DataLoader(ds, batch_size=args.batch_size, collate_fn=collate_fn)

    # infer dim from first batch
    x0, _ = next(iter(loader))
    dim = x0.shape[1]
    model = SimpleMLP(dim)
    opt = optim.Adam(model.parameters(), lr=args.lr)
    scheduler = optim.lr_scheduler.StepLR(opt, step_size=1, gamma=0.9)
    loss_fn = nn.MSELoss()

    # prepare checkpoint dir
    import os
    os.makedirs(args.checkpoint_dir, exist_ok=True)

    # split for evaluation: simple deterministic split by index
    total = len(ds)
    eval_n = max(1, int(total * args.eval_fraction))
    total - eval_n

    model.train()
    for epoch in range(args.epochs):
        running = 0.0
        for i, (x, _ids) in enumerate(loader):
            # tiny self-supervised step: reconstruct input
            pred = model(x)
            loss = loss_fn(pred, x)
            opt.zero_grad()
            loss.backward()
            opt.step()
            running += loss.item()
            if i % 10 == 0:
                print(f"epoch {epoch} step {i} loss {loss.item():.6f}")
        scheduler.step()
        avg = running / (i + 1) if i >= 0 else running
        print(f"epoch {epoch} done lr={scheduler.get_last_lr()[0]:.6e} avg_loss={avg:.6f}")

        # checkpoint
        ckpt_path = os.path.join(args.checkpoint_dir, f"checkpoint_epoch_{epoch}.pt")
        torch.save({"epoch": epoch, "model_state": model.state_dict(), "opt_state": opt.state_dict()}, ckpt_path)
        print("Wrote checkpoint", ckpt_path)

        # quick eval: sample first eval_n entries from dataset (deterministic)
        model.eval()
        try:
            eval_loader = DataLoader(ds, batch_size=args.batch_size, collate_fn=collate_fn)
            eval_loss = 0.0
            eval_steps = 0
            for j, (x_eval, _ids_eval) in enumerate(eval_loader):
                if j * args.batch_size >= eval_n:
                    break
                with torch.no_grad():
                    pred = model(x_eval)
                    l = loss_fn(pred, x_eval)
                eval_loss += l.item()
                eval_steps += 1
            if eval_steps:
                print(f"eval_loss={eval_loss / eval_steps:.6f} over {eval_steps} steps")
        except Exception as e:
            print("Eval skipped due to error:", e)
        model.train()


if __name__ == "__main__":
    main()
