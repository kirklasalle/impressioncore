# B3 Training Implementation Plan (Step-by-Step)

**Created:** August 12, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\training\B3_Training_Implementation_Plan.md #documentation #training #distillation #multimodal #plan #official  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

This plan operationalizes “Most Effective Training Method — Verbatim Response” for ImpressionCore B3 (39M params, 4GB VRAM), aligning with Concentrated Intelligence, data condensation, and consumer hardware democracy.

## Success gates (high level)

- 10/10 conversation quality on weekly 100-prompt battery (qualitative gate)
- Perplexity reduction ≥15% on held-out KD dev set vs initial student
- Multimodal alignment: image/text and audio/text retrieval R@10 ↑ by ≥10 points from baseline
- Stable VRAM usage ≤ 4GB with micro-batch 1–2 and accumulation achieving effective batch ≥32

## Phase 0 — Data condensation and curriculum setup

Deliverables:

- Condensed, stratified datasets with curriculum bands (short → medium → complex) per modality
- Multi-teacher distilled pairs with self-consistency filtering; rationale subset (10–20%)

Actions:

1) Teacher discovery and selection

   - Use `openrouter_model_discovery.py` and `openrouter_free_models_quick_reference.json` to pick 2–3 reliable remote teachers.
   - Confirm 1 local teacher (Ollama) pipeline via `b3_real_ollama_distillation_system.py`.

2) Generate multi-sample teacher outputs (N=3–5)

   - Remote: `b3_top5_remote_distillation_system.py` (or `b3_real_ollama_distillation_system.py` against remote APIs if supported)
   - Local: `b3_real_ollama_distillation_system.py`
   - Sampling defaults: temperature 0.7–1.0; top-p 0.9

3) Self-consistency + heuristic selection

   - Majority vote or heuristic scoring (length bounds, simple factuality heuristics, toxicity filter)
   - Persist final answer; include rationale in 10–20% of samples

4) Curriculum bucketing

   - Bucket by length/complexity and modality
   - Store manifests with splits (train/val/test) and tags
   - Generate the Phase 1 dialog corpora via `src/training/data/tools/generate_phase1_dialog_corpora.py`, then validate manifests with `src/training/data/tools/validate_phase1_manifest.py` before moving to alignment steps.

Notes:

- Keep datasets small and dense. Deduplicate aggressively. Track provenance.

## Phase 1 — Multimodal alignment pretraining (low-cost, high ROI)

Deliverables:

- Aligned text–image and text–audio latent spaces using contrastive losses

Actions:

1) Prepare paired datasets (t,i) and (t,a) from F:/data if available; otherwise synthesize small pairs from existing assets.
2) Implement alignment finetune module (planned code location): `src/training/pipelines/multimodal_alignment.py`

   - Projection heads from encoders to shared latent; freeze heavy encoders if needed
   - Loss: InfoNCE (NT-Xent) with temperature schedule
   - Config: micro-batch 1–2; grad checkpointing; fp16 if stable; CPU offload

Completion gate:

- R@10 improved ≥10 points on a small retrieval validation set

## Phase 2 — KD + SFT (quality backbone)

Deliverables:

- Student trained with token-level CE + KL distillation on curriculum KD data; rationale subset 10–20%

Actions:

1) Unify KD datasets into a single loader with curriculum sampling

   - Planned code: `src/training/pipelines/kd_sft_curriculum.py`
   - Loss: CE + KL(p_teacher^T || p_student), T≈2.0, λ_kl ramp 0→0.3 over first 30% steps

2) Orchestrate training

   - Start with short/clean band → medium → complex
   - Optimizer: 8-bit Adam via bitsandbytes
   - Accumulation to achieve global batch ≥32, micro-batch 1–2
   - Grad checkpointing, CPU offload for optimizer states
   - LR 2e-4, cosine decay, warmup 500–1k steps

3) Integration with existing scripts

   - Reference: `train_b3_39m_constitutional.py`, `train_unified_sweet_spot.py`, `launch_unified_training.py`
   - Option: call existing distillation systems (`b3_real_ollama_distillation_system.py`, `b3_top5_remote_distillation_system.py`) during data build, not during train loop

Completion gate:

- ≥15% PPL reduction on dev KD set and accuracy improvements across curriculum bands

## Phase 3 — Offline preference optimization (DPO/ORPO)

Deliverables:

- Student aligned on helpfulness/refusals without on-policy RL

Actions:

1) Build preference pairs

   - From multiple teacher candidates (ranked) or teacher-vs-student pairs (teacher preferred)
   - Small human set for critical safety prompts if available

2) Train with DPO/ORPO

   - Planned code: `src/training/pipelines/offline_pref_opt.py`
   - 1–2 epochs max, LR 5e-5, batch as per Phase 2 memory envelope

Completion gate:

- Style/helpfulness gains on eval prompts without increased verbosity; safety pass rate ↑

## Phase 4 — Safety, calibration, short refinement (ReST-style)

Deliverables:

- A refined micro-split using rejection sampling; safety patterns distilled

Actions:

1) Generate k candidates per prompt; select via rules/compact judge; fine-tune 0.5–1 epoch
2) Add refusal/guardrail patterns as small SFT set

Completion gate:

- Safety benchmarks and regression suite pass; minimal CE loss drift

## Phase 5 — Continual learning with replay

Deliverables:

- Replay buffer (5–10%) and EWC/freeze strategy to avoid forgetting

Actions:

1) Maintain replay manifests and mix into any later finetunes
2) Freeze lower layers or apply small EWC penalty when doing targeted updates

Completion gate:

- No regression on core eval battery across subsequent updates

## Efficiency and stability envelope (1050 Ti, 4GB)

- Micro-batch 1–2; accumulate to 32–64
- fp16 if stable; otherwise fp32 with 8-bit optimizer
- Grad checkpointing; activation recompute; sequence length warmup (1k→2k)
- CPU offload for optimizer states; pin memory; num_workers 2–4
- Avoid FlashAttention; use memory-efficient attention when available

## Engineering tasks backlog (incremental)

1) Data build utilities

   - `src/data/build_kd_dataset.py`: merge multi-teacher samples, self-consistency filter, rationale tagging, curriculum manifests
   - `src/data/filters.py`: length, toxicity, heuristic scorer

2) Training pipelines (as above)

   - `multimodal_alignment.py`, `kd_sft_curriculum.py`, `offline_pref_opt.py`

3) Orchestrator

   - `src/training/orchestrate_b3_pipeline.py`: CLI to run Phase 0→5 with saved checkpoints to F:/models via `manage_f_models.py`

4) Evaluation

   - `src/eval/b3_eval_suite.py`: PPL, instruction accuracy, R@K, safety checks, weekly 100-prompt harness

5) Configs and logging

   - `src/config/b3_training.yaml` with phase toggles; use rich logging/status modules from `src/core/utils/`

6) Model management

   - Route checkpoint saves via `manage_f_models.py` (F:/models). Enforce naming and registry updates.

## Timeline (indicative)

- Week 1: Phase 0 (data) + implement alignment module skeleton
- Week 2: Phase 1 run + start KD/SFT pipeline
- Week 3: Phase 2 completion and eval; checkpoint to F:/models/production candidate
- Week 4: Phase 3–4 polish; establish replay and long-run evals (Phase 5)

## Risk controls

- Overfitting to one teacher → multi-teacher + self-consistency
- Verbosity from CoT → limit to 10–20%; always supervise final answers
- VRAM spikes → sequence warmup, micro-batch 1, checkpointing, CPU offload
- Forgetting → replay buffer + light regularization/freeze

## November 2, 2025 Stability Update

- **Adaptive LR Floor:** Training stack now enforces a minimum learning rate equal to 50% of the configured base LR to prevent catastrophic scheduler collapse during sanity runs.
- **Validation Instrumentation:** `b3_full_embedding_training.py` captures full diagnostic artifacts whenever validation loss becomes NaN/∞. Artifacts land in `src/memlog/b3_training/validation_failures/` with tensors saved for post-mortem.
- **F:/ Data Enforcement:** `EmbeddingDataset` stops execution if no `.npy` embeddings are discovered on F:, and the slim sanity config sets `max_embedding_files=0` to consume the full drive (add optional extras via `additional_embedding_roots`). Supplemental text dirs currently point at `F:/data/english-grammar` until additional corpora are mirrored onto the drive.
- **Operator Guidance:** Before running Phase 1+ jobs, confirm the F: drive is mounted and run a quick sanity epoch; if a validation artifact triggers, review the saved batch and adjust data hygiene before longer runs.

## Next actions (immediate)

- Finalize teacher set and start Phase 0 data generation
- Implement `src/data/build_kd_dataset.py` and manifests
- Draft `kd_sft_curriculum.py` training loop using existing training utilities
- Execute the instrumented sanity pass with full F:/ embeddings mounted; if diagnostics trigger, analyze artifacts in `validation_failures/` prior to scale-up.
- Capture training anomalies: `training_failures/` now mirrors validation diagnostics; NaN/∞ losses force-save the offending batch for later triage.
- Latest sanity run (November 2, 2025) completed in ~62 minutes with best validation loss 8.5320 using 97k embeddings; oscillation detector still clamps LR almost every step—retune window/patience before multi-epoch expansion (retune pushed November 3; awaiting fresh confirmation run).
- Scheduler retune (November 3, 2025): adaptive controller now uses configurable `scheduler_*` fields (longer oscillation window, relative delta floor, cooldown) to prevent constant LR clamps while plateau detection remains available with a reduced std threshold.
- Training metrics sanitization ensures non-finite losses never corrupt averages or reports; sanity runs now record finite-only loss history to eliminate NaN `avg_loss` artifacts in generated reports.
