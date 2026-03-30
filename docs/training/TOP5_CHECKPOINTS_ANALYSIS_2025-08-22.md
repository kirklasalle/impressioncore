# Top 5 Checkpoints Analysis

**Created:** August 22, 2025  
**Updated:** December 29, 2025  
**Author:** GitHub Copilot  
**Tags:** #training #checkpoints #analysis #ranking #unified_sweet_spot #ollama_enhanced  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

**Date:** August 22, 2025  
**Author:** GitHub Copilot  
**Category:** Training / Evaluation  
**Status:** Active  
**Tags:** #training #checkpoints #analysis #ranking #unified_sweet_spot #ollama_enhanced

---

## 1. Overview

This document records the methodology, selection criteria, and deep analysis of the current top five checkpoints discovered under `F:/models` as of the full recursive inventory (122 checkpoint-like files).

## 2. Selection Method Summary

1. Inventory script enumerated all files with extensions: `.pth, .pt, .safetensors, .ckpt, .bin`.
2. Each checkpoint loaded (full pickle, fallback weights_only if supported). Extracted metrics:
   - `val_best` (if present)
   - `best_loss`
   - `loss_history` 10-step tail average
3. Primary score = first available among `val_best`, `best_loss`, `hist_tail`; else sentinel (1e12).
4. Ranked by (ascending): primary score → descending steps → descending size → descending timestamp.
5. Excluded sentinel-only entries unless needed to fill remaining slots.
6. Result: Four `unified_sweet_spot` early-step checkpoints (steps 5–25) plus one `b3_ollama_enhanced` stage file (different loss scale).

## 3. Top 5 Checkpoints (Order)

| Rank | Filename | Path (relative) | Primary (best_loss) | Steps | Size (MB) | Notes |
|------|----------|-----------------|---------------------|-------|-----------|-------|
| 1 | unified_final_step_25.pth | checkpoints/unified_sweet_spot | 10.8215 | 25 | 4490.49 | Lowest loss, includes optimizer/state (larger size) |
| 2 | unified_final_step_20.pth | checkpoints/unified_sweet_spot | 10.9380 | 20 | 1930.69 | Stable descent, lighter save |
| 3 | unified_final_step_8.pth  | checkpoints/unified_sweet_spot | 11.0014 | 8  | 1930.69 | Early plateau snapshot |
| 4 | unified_final_step_5.pth  | checkpoints/unified_sweet_spot | 11.2773 | 5  | 1930.69 | Earliest tracked metric baseline |
| 5 | b3_ollama_enhanced_stage_2_step_5500.pth | checkpoints/b3_ollama_enhanced | 4570.5485 | 5500 | 4454.44 | Different loss scale (outlier) |

## 4. Deep Metrics Summary

All four unified checkpoints share identical parameter element counts (≈506M) across 755 tensors; parameter-heavy layers: token embeddings & lm_head (~7.627% each), multiple large 3D conv blocks (~3.147% each). Bits-per-parameter for step_25 inflated (~74.4) due to presence of optimizer / auxiliary states; 1.93GB variants nearer expected raw weight footprint mixture.

The Ollama enhanced checkpoint exhibits incompatible metric scale (loss >> 100), flagged as `loss_scale_outlier` and not comparable for direct ordering within unified series.

## 5. Anomaly Flags

- `low_step_count`: All unified checkpoints (training extremely early — only 5–25 steps captured).
- `high_bits_per_param`: Step 25 only (oversized file suggests optimizer & scaler states bundled).
- `loss_scale_outlier`: Ollama stage_2 file only.

## 6. Recommendations (Current Session)

1. Proceed with deeper validation only for unified steps 8, 20, 25 (top 3) – they form a micro learning curve.
2. Run synthetic probe perplexity to confirm internal consistency of reported loss ordering.
3. Produce normalized (weights-only) export variants for these 3 to standardize size & enable fair comparison.
4. Capture a structured summary JSON for these 3 (`top3_report.json`) with: param_elems, best_loss, tail, steps, probe_loss, file_size_mb(normalized), save_mode.
5. Introduce scale-partitioned ranking (exclude incompatible loss regimes from unified ordering) — deferred until more mixed regimes appear.

## 7. Implementation Plan (Executed Next)

- Add `top3_deep_probe.py` script: loads models, runs small synthetic batch forward to compute probe cross-entropy; saves updated report.
- Add `export_weights_only.py`: strips optimizer / non-model keys, saves `*_weights_only.pth` for first three.
- Generate consolidated `inventory_reports/top3_report.json` containing:
  - original metrics
  - probe_loss
  - weights_only size & bits/param
  - anomaly notes

## 8. Future Enhancements (Not Executed Now)

- Unified validation dataset probe for real perplexity.
- Automatic resume selection logic integrated into trainer.
- Loss scale normalization across regimes.
- Integrity scan to quarantine partially corrupted archives.

## 9. Integrity & Traceability

Artifacts written under `inventory_reports/` with timestamped JSON ensure reproducibility. Original checkpoints remain untouched; weights-only exports use suffix `_weights_only.pth`.

---

End of Report