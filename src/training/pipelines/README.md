# DPO Alignment Pipeline

This pipeline implements Direct Preference Optimization (DPO) for aligning the ImpressionCore B3 model.
It is optimized for consumer hardware (GTX 1050 Ti, 4GB VRAM).

## Prerequisites

- Phase 2 SFT Checkpoint (e.g., `F:\models\checkpoints\kd_sft_phase2\step_5000.pt`)
- Phase 1 Manifest (`src/training/configs/datasets/dialog_phase1_manifest.json`)

## Steps

### 1. Generate DPO Dataset

This step generates "rejected" responses using the current model and pre-computes reference log-probs to save memory during training.

```bash
python -m src.training.data.tools.generate_dpo_pairs
```

Output: `src/training/data/datasets/dpo_phase3_dataset_with_logprobs.jsonl`

### 2. Run DPO Training

This step fine-tunes the model using the generated dataset.

```bash
python -m src.training.pipelines.dpo_alignment
```

Output: `F:\models\checkpoints\dpo_phase3\dpo_final.pt`

### 3. Evaluate

Compare the DPO model against the SFT baseline.

```bash
python -m src.training.verification.compare_dpo_vs_sft
```

## Configuration

Edit `src/training/pipelines/dpo_alignment.py` to adjust:

- `learning_rate` (Default: 1e-6)
- `beta` (Default: 0.1)
- `max_steps`
- `batch_size`
