# Colossus Dataset Benchmark Packages — October 25, 2025

**Created:** October 25, 2025  
**Updated:** December 29, 2025  
**Author:** GitHub Copilot  
**Tags:** #training #colossus #datasets #metrics  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## Aggregate Overview

| Dataset Path | Prompt Count | Checkpoint(s) | Metrics File | Transcript Bundle |
| --- | --- | --- | --- | --- |
| `src/training/distillation/kd_inputs/generated/ollama_combined_teacher_20251025_conflict_lab.json` | 165 | `F:/models/management/training_sessions/colossus/20251025_133455_colossus_distilled.pt` | `src/training/distillation/eval_outputs/colossus_metrics_20251025_133455_colossus_distilled.json` | `src/training/distillation/eval_outputs/colossus_transcripts_20251025_133455_colossus_distilled.jsonl` |
| `src/training/distillation/kd_inputs/generated/ollama_combined_teacher_20251025_compliance.json` | 185 | `F:/models/management/training_sessions/colossus/20251025_153030_colossus_distilled.pt` | `src/training/distillation/eval_outputs/colossus_metrics_20251025_153030_colossus_distilled.json` | `src/training/distillation/eval_outputs/colossus_transcripts_20251025_153030_colossus_distilled.jsonl` |
| `src/training/distillation/kd_inputs/generated/ollama_combined_teacher_20251025_regulator.json` | 203 | `F:/models/management/training_sessions/colossus/20251025_163709_colossus_distilled.pt`<br>`F:/models/management/training_sessions/colossus/20251025_174538_colossus_distilled.pt` | `src/training/distillation/eval_outputs/colossus_metrics_20251025_163709_colossus_distilled.json`<br>`src/training/distillation/eval_outputs/colossus_metrics_20251025_174538_colossus_distilled.json` | `src/training/distillation/eval_outputs/colossus_transcripts_20251025_163709_colossus_distilled.jsonl`<br>`src/training/distillation/eval_outputs/colossus_transcripts_20251025_174538_colossus_distilled.jsonl` |

## Response Length Metrics

| Dataset | Llama3.2 min / avg chars | Phi3.5 min / avg chars |
| --- | --- | --- |
| 165-pair (`...conflict_lab.json`) | 767 / 1,443.0 | 622 / 1,191.3 |
| 185-pair (`...compliance.json`) | 767 / 1,424.9 | 622 / 1,181.1 |
| 203-pair (`...regulator.json`) | 767 / 1,416.8 | 622 / 1,182.0 |

Focused prompts now exceed 800 characters per teacher, eliminating the previously flagged short responses.

## Usage Notes

- Each dataset retains dual-teacher coverage (`phi3.5:3.8b-mini-instruct-q4_K_M`, `llama3.2:3b`) with clean prompt de-duplication.
- The benchmark table anchors regression comparisons across successive dataset expansions while maintaining VRAM headroom (<4 GB).
- When running downstream evaluations, pair each aggregate with its associated metrics and transcript artifacts to track qualitative deltas.
- For the 203-pair aggregate, compare the 8-epoch and 12-epoch checkpoints to gauge the impact of cosine annealing and accumulation (avg L2 dropped from 0.5760 to 0.5590).