# Checkpoint Manager

This small utility helps audit and prune PyTorch checkpoint files (.pth) under a checkpoints directory. It's conservative by default and will not delete/move files unless you pass `--apply`.

Examples (PowerShell):

## Audit and write a CSV of checkpoints

```powershell
python tools/ckpt_manager.py audit --dir F:/models/checkpoints --out ckpts.csv
```

## Quick report to see recent/large files

```powershell
python tools/ckpt_manager.py report --dir F:/models/checkpoints
```

## Dry-run prune (policy: keep_latest:3 — keep 3 newest files, list candidates)

```powershell
python tools/ckpt_manager.py prune --dir F:/models/checkpoints --policy keep_latest:3
```

## Apply prune and move candidates to archive directory

```powershell
python tools/ckpt_manager.py prune --dir F:/models/checkpoints --policy keep_latest:3 --archive F:/models/checkpoints/archive --apply
```

Policies supported:

- `keep_latest:N`
- `keep_best_per_prefix:N`
- `keep_total_size:GB`

Safety:

- Defaults to dry-run. Use `--apply` to actually move files to the archive directory.
- Skips files it cannot read.
