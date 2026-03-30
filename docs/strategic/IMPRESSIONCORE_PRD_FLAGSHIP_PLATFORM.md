# ImpressionCore Product Requirements Document (Flagship Platform)

**Created:** August 22, 2025  
**Updated:** December 29, 2025  
**Author:** GitHub Copilot  
**Tags:** #prd #requirements #iu1 #is1 #guardian_stack #rollout #kpi #ids  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

**Version:** 1.0.0-draft  
**Author:** GitHub Copilot  
**Tags:** #prd #requirements #iu1 #is1 #guardian_stack #rollout #kpi #ids  
**Category:** Strategic  
**Status:** Draft  
**IDS Integration:** Indexed (post-save)

---

## 1. Vision Alignment

The Product consolidates constitutional principles (Concentrated Intelligence, 39M Parameter Foundation, Consumer Hardware Democracy, Protection-First, Data Condensation, True Purpose Architecture) into a coherent flagship deployment (IU1) and system orchestration layer (IS1).

Cross References:

- Model Lineup & Rollout Strategy (core series scope)
- Guardian Stack Specification (safety & governance blueprint)
- KPI Registry (quantitative success criteria)
- Permanent Architectural Framework (constitutional principles)

---

## 2. Product Goals

| Goal | Description | Success Signal |
|------|-------------|----------------|
| G1 | Deliver IU1 flagship achieving sustained 10/10 conversation quality within protection-first constraints | Human eval + guardian metrics green |
| G2 | Enable persona-secure AVT → IU1 maturation via shadow distillation with zero data leakage | Distillation logs + privacy recall ≥99.7% |
| G3 | Achieve deterministic robotics/compliance (IDC) integration pathway feeding IS1 orchestration | Control jitter ≤12 ms & audit chain integrity |
| G4 | Launch IS1 kernel orchestrating multi-model + policy kernel with federated ledger | Federated policy consistency <0.3% divergence |
| G5 | Maintain consumer GPU accessibility through optimization & module elasticity | Peak VRAM ≤3.6 GB (baseline path) |

---

## 3. In-Scope Features

| Feature | Description | Series | Ref |
|---------|-------------|--------|-----|
| Guardian Stack Adaptive Pipeline | Layered protection gating (10 layers) | IU1/IS1 | Guardian Spec §3/§8 |
| Shadow Distillation Lifecycle | Progressive avatar → flagship maturation | AVT→IU1 | Lineup §3 |
| Policy Kernel Federation | Unified policy evaluation across nodes | IS1 | Guardian Spec §9/§10 |
| Persona Identity Envelope | Consent + capability claims mediation | AVT/IU1 | Guardian Spec §3 Layer 2 |
| Memory Stratification Hierarchy | Episodic + semantic + systemic fabric | IU1/IS1 | Lineup Pillars |
| Tool / Actuation Mediator | Risk-scored tool gating & sandbox | IDC/IU1 | Guardian Spec Layer 5 |
| KPI Telemetry Bus | Real-time metric aggregation & threshold enforcement | All | KPI Registry |

---

## 4. Out of Scope (Phase IU1)

| Item | Rationale |
|------|-----------|
| Multi-agent arbitration layer (IS2 concept) | Future extension (§11 Guardian Spec) |
| Zero-knowledge redaction proofs | Deferred until regulated deployment demand |
| Full on-device edge guardian mode | Post initial IS1 stabilization |

---

## 5. User Personas

| Persona | Primary Needs | Feature Mapping |
|---------|---------------|-----------------|
| End User (Avatar) | Safe, consistent personal assistant with privacy | Guardian Layers 1–3, Persona Memory |
| Developer | Extensible APIs, deterministic safety envelope | Policy Engine API, Tool Mediator |
| Compliance Officer | Audit trail & policy evidence | Ledger + Policy Kernel |
| Robotics Integrator | Low-latency deterministic control surface | Tool Mediator + IDC adapters |
| Platform Operator | Central governance & drift oversight | Federated Kernel + KPI Bus |

---

## 6. Functional Requirements (Selected)

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-1 | Input Gate enforces schema, size, rate | >99.9% invalid blocked; no valid false blocks >0.2% |
| FR-2 | Identity envelope validates consent & capability claims | 100% of privileged tool calls carry validated capability token |
| FR-3 | Memory guard applies redaction + TTL scoping | Privacy recall ≥99.7%; leakage rate <0.3% (IU1) |
| FR-4 | Policy engine produces composite risk & band decision | Decisions reproducible from ledger payload |
| FR-5 | Output auditor transforms or blocks unsafe output | Safety FN <0.5%; FP ≤2.5% (IU1) |
| FR-6 | Escalation auto-triggers on ORANGE/RED bands | ≥98% of RED events escalated within 150 ms |
| FR-7 | Ledger writes hashed, chain continuity intact | Chain integrity verification pass 100% daily |
| FR-8 | Drift monitor flags semantic deviation | Drift alert precision >90% |
| FR-9 | Shadow distillation replay stable | Replay stability index within ±5% window |
| FR-10 | KPI thresholds enforced dynamically | Violations trigger alert within 5s |

---

## 7. Non-Functional Requirements

| Category | Requirement | Metric |
|----------|------------|--------|
| Performance | Added guardian latency | <35 ms IU1 median |
| Reliability | Ledger availability | 99.95% monthly |
| Scalability | Policy rule load scalability | Linear up to 5× current rules |
| Security | PII residual after audit | <0.3% IU1 / <0.1% IS1 |
| Maintainability | Config hot reload success | ≥98% |
| Observability | Metric coverage | 100% KPIs emitted |

---

## 8. KPI Mapping

Every functional & non-functional requirement bound to registry metric identifier. See KPI Registry §3/§4. Violations propagate to: alert → escalation (if safety/privacy) → gating (if rollout phase gating).

---

## 9. Dependencies

| Dependency | Justification | Status |
|------------|--------------|--------|
| Guardian Stack Implementation | Core safety/governance path | In Progress |
| Shadow Distillation Pipelines | Avatar → flagship maturation | Operational (baseline) |
| Kernel / Liaison Framework | Orchestration & capability bus | Planned integration |
| Metrics Telemetry Service | Real-time KPI aggregation | Design phase |

---

## 10. Rollout Plan Alignment

Maps directly to lineup gates P1–P5 with explicit gate KPIs (Lineup §12; KPI Registry §4). Exit reviews require signed metric pack + ledger integrity attestation.

Version Synchronization:

- Model Lineup v1.0.0 (this PRD tracks lineup taxonomy; changes to series or gate KPIs require PRD version bump).
- Guardian Stack Spec current active version establishes safety metrics authoritative semantics.
- KPI Registry authoritative thresholds are ingested by telemetry (see guardian metrics implementation) and referenced here; deviations trigger change control (§14).

---

## 11. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|-----------|
| Over-tight safety thresholds inflate FP | User frustration / reduced utility | Medium | Adaptive tuning & exemplar feedback loop |
| Ledger latency spikes | Throughput degradation | Low | Async write buffer + backpressure strategy |
| Drift false positives | Noise & alert fatigue | Medium | Calibrate with shadow replay baseline |
| Tool mediator bottleneck | Execution backlog | Medium | Capability graph parallel routing |
| Memory over-retention | Privacy risk | Low | TTL enforcement & periodic purge audits |

---

## 12. Open Questions

| Topic | Question | Owner |
|-------|----------|-------|
| Escalation UX | Human review interface requirements | TBD |
| Ledger External Notarization | When to introduce third-party anchoring? | TBD |
| Robotics Abstraction | Standard contract for mixed actuator classes | TBD |

---

## 13. Acceptance & Success Metrics

Success = All G1–G5 goals achieved within KPI thresholds for 30 consecutive days, zero critical safety incident, ledger integrity 100%, conversation quality 10/10 median, federated consistency target achieved at IS1 launch.

---

## 14. Change Control

All modifications require PRD delta appendix + KPI registry sync + guardian spec cross-ref update.

---

## 15. Change Log

| Date | Change | Author |
|------|--------|--------|
| August 22, 2025 | Initial PRD scaffold created | GitHub Copilot |
| August 22, 2025 | Added lineup integration (v1.0.0), version sync table, guardian + KPI cross-refs | GitHub Copilot |
| January 19, 2026 | Added NEXUS-RLM v1.2 feature scope (Recursive Language Model integration) | Antigravity Agent |

---

## 16. NEXUS-RLM v1.2-1.4 Feature Addendum (January 2026)

### Overview

The NEXUS language extensions (v1.2-1.4) enable ImpressionCore's Brain-Triad architecture to process arbitrarily large contexts (10M+ tokens) through RLM-inspired inference patterns, while maintaining RLM itself as a distinct model architecture research topic.

### Phase 1 Components (Implemented)

| Version | Component | Description | Status |
|---------|-----------|-------------|--------|
| v1.2 | `LLM-QUERY` Command | Recursive sub-LLM calls to L/R/Colossus | ✅ Implemented |
| v1.2 | `CONTEXT-LOAD/SEARCH/CHUNK` | External context management | ✅ Implemented |
| v1.2 | `nexus_context_manager.py` | Singleton context storage with recursion tracking | ✅ Implemented |
| v1.3 | `ASYNC/AWAIT/PARALLEL` | Thread-based parallel execution | ✅ Implemented |
| v1.4 | `PIPELINE` | Sequential execution with result chaining | ✅ Implemented |
| v1.4 | Arithmetic | `+`, `-`, `*`, `/` operators | ✅ Implemented |
| v1.4 | Utilities | `CONCAT`, `LIST`, `MAP` | ✅ Implemented |

### Integration Points

- **NEXUS Language**: Extended with 19 new commands (v1.1-v1.4)
- **Brain-Triad**: LLM-QUERY routes to Left/Right/Colossus hemispheres
- **MHC Ultra Training**: Compatible with MHC-stabilized model weights

### Success Criteria

| Metric | Target | Current |
|--------|--------|---------|
| Context Length | 100K+ tokens | 50MB max per context |
| Recursion Depth | 20 max | ✅ Implemented |
| Memory Overhead | <100MB | ~50MB estimated |
| Command Coverage | 19 commands | ✅ 19 implemented |

### Phase 2: RLM Training (Planned)

> **📋 Reference:** [RLM Training Integration Plan](strategic/b3/RLM_TRAINING_INTEGRATION_PLAN.md)

| Component | Description | Status |
|-----------|-------------|--------|
| Policy Network | RL controller for action selection | Planned (Week 1-2) |
| Reward Functions | Multi-objective training signals | Planned (Week 1-2) |
| PPO Training | Reinforcement learning pipeline | Planned (Week 3-4) |
| Benchmarks | Long-context evaluation suite | Planned (Week 5-6) |

### RLM Research Context

RLM (Recursive Language Model) is an **inference scaffolding paradigm** (not a model architecture) that enables unbounded context processing via:
- Python REPL for action execution
- Sub-LLM calls for delegation
- Context folding for compression

See [RLM Research Report](../reports/rlm_research_report.md) for theoretical background.

---
End of Document