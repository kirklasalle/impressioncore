# ImpressionCore B3 Phase 3: Advanced Alignment Strategy (DPO)

**Created:** November 26, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team  
**Tags:** #docs\B3_PHASE3_ALIGNMENT_PLAN.md #documentation  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

**Target Hardware:** GTX 1050 Ti (4GB VRAM)

## Executive Summary

Following the successful completion of Phase 2 (Knowledge Distillation + SFT), the model has learned *how* to speak. Phase 3 focuses on aligning the model's responses with human preferences—teaching it *what* is better to say.

We will utilize **Direct Preference Optimization (DPO)** instead of traditional RLHF (PPO). DPO is mathematically equivalent to RLHF but eliminates the need for a separate reward model and complex reinforcement learning loop, making it significantly more memory-efficient and stable—perfect for our GTX 1050 Ti constraints.

## Objectives

1. **Alignment:** Fine-tune the Phase 2 model to prefer helpful, harmless, and concise responses.
2. **Stability:** Maintain the 10/10 conversation quality achieved in Phase 2.
3. **Efficiency:** Execute alignment training within the 4GB VRAM budget.

## Methodology: Direct Preference Optimization (DPO)

DPO optimizes the policy (model) directly using a dataset of `(prompt, chosen, rejected)` triples.

### 1. Dataset Preparation

We need a dataset where for a given prompt, we have two responses:

* **Chosen:** The better response (e.g., from a high-quality teacher or human).
* **Rejected:** A worse response (e.g., hallucinated, toxic, or overly verbose).

**Source:** We can construct a synthetic DPO dataset using our existing SFT data:

* **Chosen:** The "Assistant" response from our high-quality Phase 2 dataset.
* **Rejected:** A generated response from an earlier/weaker version of the model, or a perturbed version of the chosen response.

### 2. Training Pipeline (`src/training/pipelines/dpo_alignment.py`)

* **Base Model:** The checkpoint from Phase 2 (`F:\models\checkpoints\kd_sft_phase2\step_5000.pt`).
* **Reference Model:** A frozen copy of the Base Model (required for DPO to calculate KL divergence).
* **Optimization:**
  * **QLoRA / 8-bit Optimization:** Essential to fit both Base and Reference models (or share weights efficiently) in 4GB VRAM.
  * **Gradient Checkpointing:** Enabled.
  * **Gradient Accumulation:** To simulate larger batch sizes.

## 4. Implementation Status (Updated)

### ✅ Proof of Concept Success

* **Date:** Current

* **Achievement:** Successfully implemented and verified the DPO pipeline on GTX 1050 Ti.
* **Key Optimizations:**
  * **Pre-computed Reference Log-Probs:** Eliminated the need to load the Reference Model during training, saving ~50% VRAM.
  * **8-bit AdamW:** Reduced optimizer state memory.
  * **Gradient Accumulation:** Enabled effective batch size of 32 with physical batch size of 1.
* **Verification:**
  * Dataset generation tool (`src/training/data/tools/generate_dpo_pairs.py`) runs successfully.
  * Training pipeline (`src/training/pipelines/dpo_alignment.py`) runs without OOM.
  * Model loads and generates text (identical to SFT for now due to short training).

### ✅ Phase 3 Execution (November 26, 2025)

- **Status:** Pipeline Operational & Verified.
* **Data:** Processed full Phase 1 dataset (91 samples).
* **Training:**
  * Run for 3 epochs (66 steps).
  * No OOM errors (Max VRAM usage stable).
  * Loss converged from ~1.08 to ~0.70.
* **Evaluation:**
  * Model stability confirmed (no degradation).
  * Outputs currently identical to SFT baseline due to small dataset size and conservative learning rate (1e-6).
* **Recommendation:**
  * Increase dataset size (Phase 2 data?) or increase epochs/LR for stronger alignment signal.
  * The pipeline is ready for scale.

### Next Steps

1. **Scale Data Generation:** Run `generate_dpo_pairs.py` on the full Phase 1 dataset (or a larger subset).
2. **Full Training Run:** Execute `dpo_alignment.py` for at least 1 full epoch.
3. **Evaluation:** Use `compare_dpo_vs_sft.py` to monitor qualitative improvements.

## Hardware Feasibility Analysis (GTX 1050 Ti)

* **Model Weights (39M params):** ~0.16 GB (fp32) / ~0.08 GB (fp16).
* **Reference Model:** ~0.08 GB (frozen, fp16).
* **Gradients & Optimizer:** Minimal impact due to small model size.
* **Activations:** The main bottleneck.
* **Conclusion:** Highly feasible. The 39M parameter size is our superpower here. We can likely fit full DPO training without extreme quantization, but we will stick to 8-bit optimizers for safety.

---
**Next Steps:**

1. Approve this plan.
2. Generate the DPO dataset.
3. Launch DPO training.