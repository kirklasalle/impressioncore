# ImpressionCore KPI Registry

**Created:** August 22, 2025  
**Updated:** December 29, 2025  
**Author:** GitHub Copilot  
**Tags:** #kpi #metrics #rollout #guardian_stack #governance #ids  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

**Version:** 1.0.0  
**Author:** GitHub Copilot  
**Tags:** #kpi #metrics #rollout #guardian_stack #governance #ids  
**Category:** Reference  
**Status:** Active  
**IDS Integration:** Indexed (post-save)

---

## 1. Purpose

Central authoritative registry for quantitative metrics & thresholds governing series rollout gates, guardian stack performance, and platform governance. Harmonizes values referenced in `IMPRESSIONCORE_MODEL_LINEUP.md` (§12) and `GUARDIAN_STACK_SPECIFICATION.md` (§7/§8).

Versioning Policy:

- Patch (x.y.Z): typo / formatting / narrative clarifications (no numeric change).
- Minor (x.Y.z): additive metric (new row) or additional gate column context.
- Major (X.y.z): any redefinition of existing metric semantics or threshold shift affecting acceptance criteria.

---

## 2. Metric Classification

| Class | Scope | Examples |
|-------|-------|----------|
| Safety | Harmful content mitigation | Safety FN Rate, Safety FP Rate |
| Privacy | PII protection & leakage | Privacy Filter Recall, Redaction Leakage Rate |
| Performance | Latency & efficiency | Mean Policy Overhead, VRAM Footprint |
| Reliability | Stability & integrity | Ledger Write Failure Rate, Hot Reload Success Rate |
| Memory | Continuity & recall | Memory Retention Fidelity |
| Governance | Policy & compliance cohesion | Federated Policy Consistency |
| Drift | Behavioral regression | Drift Alert Precision |
| Persona | Avatar coherence | Avatar Consistency Score |
| Robotics | Deterministic control | Control Loop Jitter |
| Tooling | Mediation accuracy | Tool Mediation Denial Accuracy |

---

## 3. Canonical Metric Definitions

| Metric | Definition | Formula / Method | Primary Gate(s) | Source Layer |
|--------|------------|------------------|-----------------|--------------|
| Safety FN Rate | Harmful items passed | false_negatives / total_harmful | P4 | Output Auditor |
| Safety FP Rate | Benign items blocked | false_positives / total_benign | P2/P4 | Output Auditor |
| Privacy Filter Recall | Detected PII / total PII | detected_pii / ground_truth_pii | P2 | Identity+Redaction |
| Redaction Leakage Rate | Residual PII tokens proportion | residual_pii / ground_truth_pii | P4/P5 | Output Auditor |
| Mean Policy Overhead | Added median latency | median(policy_path_ms - baseline_ms) | P4 | Policy Engine |
| Param Efficiency | Quality vs param baseline | quality_score / baseline_score | P1 | Training Pipeline |
| VRAM Footprint | Peak VRAM usage | max(vram_samples) | P1 | Runtime Monitor |
| Training Stability | Stable epochs run | count(consecutive_stable_epochs) | P1 | Training Logs |
| Avatar Consistency Score | Persona style cohesion | classifier_mean(style_vectors) | P2 | AVT Evaluator |
| Tool Mediation Denial Accuracy | Correct denials ratio | correct_denials / total_denials | P3 | Tool Mediator |
| Control Loop Jitter | 95p latency variance | p95(\|latency_i - mean\|) | P3 | Robotics Harness |
| Ledger Integrity Fail Rate | Failed writes / total events | failed_writes / total_events | P3/P4 | Ledger Service |
| Conversation Quality | Composite human rating | median(human_scores) | P4 | Evaluation Panel |
| Memory Retention Fidelity | Episodic recall accuracy | recalled / expected | P4 | Memory Probe Suite |
| Federated Policy Consistency | Divergent decisions ratio | divergent / total_decisions | P5 | Policy Kernel |
| Hot Reload Success Rate | Successful swaps ratio | success_swaps / total_swaps | P5 | Kernel Events |
| Drift Alert Precision | True alerts proportion | true_alerts / total_alerts | P5 | Drift Monitor |
| Privacy Leakage Rate | Residual PII after full audit | residual_pii / total_pii | P5 | Federated Audit |

---

## 4. Target Threshold Table

| Metric | P1 | P2 | P3 | P4 | P5 |
|--------|----|----|----|----|----|
| Safety FN Rate | — | <0.7% | <0.7% | <0.5% | <0.2% |
| Safety FP Rate | — | <3.0% | <3.0% | <2.5% | <1.5% |
| Privacy Filter Recall | — | ≥99.5% | ≥99.5% | ≥99.7% | ≥99.9% |
| Redaction Leakage Rate | — | <0.5% | <0.4% | <0.3% | <0.1% |
| Mean Policy Overhead (ms) | — | — | <45 | <35 | <25 |
| Param Efficiency | ≥95% | maintain | maintain | maintain | maintain |
| VRAM Footprint (GB) | ≤3.6 | ≤3.6 | ≤3.6 | ≤3.6 | Elastic |
| Training Stability (epochs) | ≥10 | ≥10 | ≥10 | ≥15 | ≥15 |
| Avatar Consistency Score | — | ≥0.87 | ≥0.88 | ≥0.90 | ≥0.90 |
| Tool Denial Accuracy | — | — | ≥92% | ≥94% | ≥95% |
| Control Loop Jitter (ms 95p) | — | — | ≤12 | ≤10 | ≤8 |
| Ledger Fail Rate | — | — | <0.05% | <0.03% | <0.01% |
| Conversation Quality | — | — | — | 10/10 | 10/10 |
| Memory Retention Fidelity | — | — | — | ≥92% | ≥95% |
| Federated Policy Consistency | — | — | — | — | <0.3% |
| Hot Reload Success Rate | — | — | — | — | ≥98% |
| Drift Alert Precision | — | — | — | >90% | >95% |
| Privacy Leakage Rate | — | — | — | <0.3% | <0.1% |

---

## 5. Governance & Update Protocol

1. Any proposed threshold change requires: rationale, impact analysis, simulation or backtest evidence.
2. Changes logged in §7 Change Log and mirrored in lineup & guardian docs.
3. Guardian Stack runtime enforces live thresholds from signed config bundle.

---

## 6. Exception Handling

| Scenario | Temporary Action | Max Duration | Approval |
|----------|------------------|--------------|----------|
| Elevated FP due to new safety model | Relax FP limit by +0.5% | 7 days | Policy Lead |
| Drift monitor recalibration | Suspend drift alerts | 48 hours | Platform Lead |
| Emergency privacy patch | Tighten recall target +0.2% | 3 days | Security Lead |

---

## 7. Change Log

| Date | Change | Author |
|------|--------|--------|
| August 22, 2025 | Initial registry established | GitHub Copilot |
| August 22, 2025 | Added version 1.0.0 & versioning policy | GitHub Copilot |

---
End of Document