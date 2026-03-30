# Regulator Backbone + Remediation Blend Plan

**Created:** October 25, 2025
**Author:** GitHub Copilot

- **Objective:** Preserve the regulator-focused backbone while reintroducing the three regression prompts at a lower frequency (3:1 regulator-to-remediation ratio) so confidence gains stay anchored on compliance scenarios.
- **Prompt source files:**
  - Baseline regulator corpus: `ollama_combined_teacher_20251025_regulator.json`
  - Regression prompts: `teacher_regression_remediation_prompts_20251025.jsonl`
- **Blend manifest:** `teacher_regulator_remediation_blend_prompts_20251025.jsonl`
  - 12 total prompts (9 regulator, 3 remediation).
  - Ordering interleaves three regulator prompts followed by one remediation prompt to preserve the desired ratio across batches.
- **Generation plan:**
  1. Run dual-teacher generation (phi3.5 mini + llama3.2 3B) on the blend manifest with 4096 ctx / 256 predict windows.
  2. Consolidate the two runs into `ollama_combined_teacher_20251025_regulator_remediation_blend.json` while retaining the 3:1 prompt ordering.
- **Status:**
  - Completed phi3.5 run → `ollama_phi3.5_regulator_remediation_blend_20251025.json` (12 prompts after retry merge).
  - Completed llama3.2 run → `ollama_llama32_regulator_remediation_blend_20251025.json`.
  - Dual-teacher merge → `ollama_combined_teacher_20251025_regulator_remediation_blend.json` (12 prompts, 3:1 ratio preserved).
  - Distilled blend dataset → `F:/models/management/training_sessions/colossus/20251026_083544_colossus_distilled.pt` (vector 0.001759 | confidence 0.174392 | total 0.045357).
  - Evaluation vs `20251025_174538_colossus_distilled.pt` showed regression (avg L2 0.2856 | avg confidence delta −0.1401), so pointer remains on `20251025_174538`.
  - Transcript review (`colossus_transcripts_20251026_083544_colossus_distilled.jsonl`) shows the distilled responses collapsing into generic facilitation tips, missing the regulators' escalation scaffolds and evidence-weight arbitration specifics that the teachers supply, explaining the confidence drop.
- **Upcoming experiment sketch:**
  - Distillation: 8 epochs, batch size 32, gradient accumulation 2.
  - Scheduler: cosine (lr `1e-3` → `1e-4`).
  - Vector dim: 256.
  - Compare checkpoints against `20251025_174538_colossus_distilled.pt` focusing on the three regression prompts plus war-room governance drills.
- **Suggested command:**

  ```powershell
  . .\.venv310\Scripts\Activate.ps1
  python -m src.training.colossus_distillation \
    --teacher-data src/training/distillation/kd_inputs/generated/ollama_combined_teacher_20251025_regulator_remediation_blend.json \
    --epochs 8 --batch-size 32 --gradient-accumulation 2 \
    --scheduler cosine --learning-rate 1e-3 --lr-min 1e-4
  ```

## October 26, 2025 – Regulator Backbone Shortlist Refresh

- **Purpose:** Extract a wider regulator spine (18 prompts) that explicitly reinstates evidence-weight arbitration, escalation switching logic, and psychological safety cooldown drills before re-blending with remediation items.
- **Source:** `ollama_combined_teacher_20251025_regulator.json` → indices `[5, 11, 18, 19, 22, 26, 31, 32, 33, 34, 35, 36, 39, 42, 45, 49, 61, 87]`.
- **Artifacts:**
  - Prompt manifest → `teacher_regulator_backbone_shortlist_prompts_20251026.jsonl` (feeds dual-teacher regeneration if we need fresher completions).
  - Dual-teacher merge (current) → `ollama_combined_teacher_20251026_regulator_backbone_shortlist.json` (18 prompts, both teachers preserved from the 2025-10-25 regulator run).
- **Coverage audit:**
  - **Evidence arbitration:** storyboard + matrix prompts (`26, 32, 33, 35, 36, 39`).
  - **Escalation governance:** rotation + signal matrix + compliance close-out (`31, 34, 42, 45, 49, 61`).
  - **Psychological safety:** cooldown + narrative reconciliation prompts (`19, 87`).
  - **Cross-cultural alignment:** remote interpretation + contingency drills (`5, 11, 18, 22`).
- **Next steps:** Blend this 18-prompt backbone with a refreshed remediation set (maintain 3:1 ratio) before regenerating teachers to avoid stale completions, then rerun the 8-epoch distillation for checkpoint comparison against `20251025_174538`.

### Remediation Backbone & New Blend Assembly

- **Remediation shortlist:** Pulled from `ollama_combined_teacher_20251025_branching.json` → indices `[16, 17, 79, 83, 85, 86]` to emphasize branch recovery, psychological safety resets, and mediator overload detection.
- **Artifacts:**
  - Prompt manifest → `teacher_remediation_backbone_shortlist_prompts_20251026.jsonl` (6 prompts).
  - Combined blend manifest → `teacher_regulator_remediation_blend_prompts_20251026.jsonl` (24 prompts total; 18 regulator + 6 remediation, ordered to preserve the 3:1 cadence).
- **Upcoming actions:**
  1. Regenerate teachers on the new blend manifest (phi3.5 mini + llama3.2 3B, 4096 ctx / 256 predict, retry on truncations).
  2. Merge outputs into `ollama_combined_teacher_20251026_regulator_remediation_blend.json` once both runs finish.
  3. Launch 8-epoch distillation against the refreshed dataset and compare to checkpoint `20251025_174538_colossus_distilled.pt` with the regulator governance suite as primary probes.
