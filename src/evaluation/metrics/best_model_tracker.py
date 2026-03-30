"""Best Model Tracking Utilities (migrated)

Originally in `src/metrics.py`.
No functional changes; path only.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import torch


class BestModelTracker:
    def __init__(self, save_dir: Path, metric: str = 'loss'):
        self.save_dir = save_dir
        self.metric = metric
        self.best_value = float('inf')
        self.metadata: dict[str, Any] = {}

    def update(self, value: float, global_step: int, model, optimizer, scaler, extra: dict[str, Any]):
        if value < self.best_value:
            self.best_value = value
            self.metadata = {
                'best_value': value,
                'global_step': global_step,
                'metric': self.metric,
                # extra,
            }
            self._save(model, optimizer, scaler, global_step)
            return True
        return False

    def _save(self, model, optimizer, scaler, step: int):
        # Perform save in background thread to avoid blocking training loop
        def _do_save():
            try:
                self.save_dir.mkdir(parents=True, exist_ok=True)
                path = self.save_dir / f"best_{self.metric}_step_{step}.pth"
                ckpt = {
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'scaler_state_dict': scaler.state_dict() if scaler else None,
                    'metadata': self.metadata,
                }
                torch.save(ckpt, path)
            except Exception as e:
                # log to stdout as logger may not be configured in background thread
                try:
                    import logging
                    logging.getLogger('best_model_tracker').warning(f"[BEST-SAVE] failed: {e}")
                except Exception:
                    pass

        threading = __import__('threading')
        t = threading.Thread(target=_do_save, daemon=True)
        t.start()

    def info(self):
        return self.metadata
