# ImpressionCore Model Lineup & Rollout Strategy

**Created:** August 22, 2025  
**Updated:** December 29, 2025  
**Author:** GitHub Copilot  
**Tags:** #models #rollout #B_series #AVT #IDC #IU1 #IS1 #lineup #ids  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

**Version:** 1.0.0  
**Author:** GitHub Copilot  
**Tags:** #models #rollout #B_series #AVT #IDC #IU1 #IS1 #lineup #ids  
**Category:** Strategic  
**Status:** Active

---

## 1. Canonical Series Overview

| Series | Name Expansion | License / Availability | Primary Purpose | Core Differentiators ( concise ) |
|--------|----------------|------------------------|-----------------|-------------------------------|
| B Series | ImpressionCore B (B1→B2→B3) | Open Source | Foundational concentrated intelligence baseline | 39M parameter efficiency baseline; consumer GPU (GTX 1050 Ti) accessibility; full multimodal encode path (text / audio / image / video* / phoneme). |
| AVT Series | Avatar Series (ImpressionCore-AVT) | Freeware (non‑commercial) | Personal avatar & protected digital identity layer | Persona synthesis + safety / privacy envelope; feeds IU1 via shadow model distillation (see §4); integrates RAG + UKS + BrainSim3 wrapper. |
| IDC Series | ImpressionCore-IDC | Commercial (licensed) | Robotics / industrial / regulated automation | Deterministic control adapters (ROS2 / edge I/O), extended safety & compliance tracing, hardened deployment surface. |
| IU1 | ImpressionCore-IU1 (Flagship) | Flagship (commercial hybrid) | Canonical full multimodal flagship architecture | Multi‑expert routing, advanced memory substrate, protection-first Guardian Stack (see Guardian Stack Specification), curriculum + shadow maturation pipeline. |
| IS1 | ImpressionCore Intelligent System One (IS1) | Intelligence Platform Distribution | System-level orchestration of models + capabilities | Runtime kernel + liaison framework (see kernel docs), modular service bus, secure capability graph, lifecycle & policy governance; hardware adaptability tiering. |

Multimodal NOTE: Core generative responsibility focuses on model comprehension + response composition; external specialized generators may be invoked for heavy media synthesis per protection-first design.

---

## 2. Intent & Evolution

1. **B Series**: Establish constitutional architecture + parameter efficiency; broaden modality coverage each increment while retaining consumer hardware viability.
2. **AVT Series**: Distributable avatar / identity companion; safe instantiation + consent / privacy filters; produces shadow training streams for IU1.
3. **IDC Series**: Reliability + controllability tier; real‑time tolerant scheduling, robotics middleware, compliance traceability (see Sacred_Covenant_Compliance_Framework).
4. **IU1**: Convergence layer (multi‑expert attention, latent fusion, adaptive memory, curriculum distillation, shadow maturation merge).
5. **IS1**: Intelligence System platform: orchestrated subsystems (memory, planning, policy, capability routing) via kernel + liaison framework; persistent governance.

## 3. Shadow Model Distillation Lifecycle (Extract)

Reference: `docs/reference/SHADOW_MODEL_DISTILLATION.md` + distillation pipeline documents.

| Stage | Source → Target | Trigger | Mechanism | Promotion Criterion |
|-------|-----------------|---------|-----------|--------------------|
| Shadow Init | AVT snapshot → Shadow | Avatar maturity checkpoint | Lightweight distill (curriculum subset) | Baseline loss delta within threshold vs parent |
| Progressive Alignment | Shadow → IU1 candidate | Performance plateau | Mixed curriculum (core + avatar contexts) | Cross-entropy + safety parity |
| Maturation Merge | IU1 candidate → IU1 main | Stability window achieved | Weighted parameter merge + replay | Retains ≥ target coherence & safety metrics |
| Refresh Cycle | IU1 main → New shadow | Scheduled or drift detection | Snapshot + differential distill | Drift < threshold over eval suite |

KPIs (initial placeholders – quantify in follow-up): loss delta %, safety violation rate, semantic retention score, replay stability index.

---

## 4. Feature Layering Matrix

| Capability Domain | B Series | AVT | IDC | IU1 | IS1 |
|-------------------|---------|-----|-----|-----|-----|
| Core Multi modal Encoding | B3 scope | Subset (persona-focused) | Full (industrial tuned) | Full + enhanced latent routing | Full + dynamic module hot‑swap |
| Parameter Efficiency | Primary goal | Maintained | Adjusted for control stability | Balanced vs capability | Elastic module scaling |
| Avatar / Persona Layer | Basic hooks | Primary feature set | Optional | Advanced adaptive personas | System-tier dynamic identity graph |
| Protection / Identity Security | Baseline | Elevated (privacy + consent) | Hardened (industrial policies) | Unified guardian stack | System policy engine + audit fabric |
| Real-Time / Robotics IO | Minimal | Not focus | Core | Extended (multi-device) | Orchestrated multi-agent scheduling |
| Memory & Continuity | Lightweight cache | Scoped persona memory | Deterministic logs | Hierarchical episodic + semantic memory | System-wide long-horizon cognitive fabric |
| Tool / Plugin Integration | Minimal | Limited | Industrial adapters | Comprehensive | Kernel-level capability graph |
| Governance / Policy | Foundational directives | Avatar safety emphasis | Compliance & safety logs | Adaptive policy tuning | Full intelligence system governance |

---

## 5. Licensing & Distribution Positioning

- **Open Source (B Series):** Public repository; encourages community experimentation & downstream specialization.
- **Freeware (AVT):** Binary / model weights distribution for avatar usage (person, place, or thing); restricted commercial exploitation. Intended for market, research, education. Avatars of plants, animals, geographical locations for study, and human teachable skills
- **Commercial (IDC):** Licensed deployments with SLA, certification pathways, safety audit bundles. Intended for FULL Commercial Compliance, regulatory and Federal, State, and local County, legal compliance.
- **Flagship Commercial (IU1):** Core runtime with selective proprietary enhancement modules; commercial AVT plugin surface retained.
- **Intelligence System (IS1):** Platform distribution (installer / container ensemble) providing orchestration kernel + pluggable intelligence services.

---

## 6. Rollout Sequencing & Readiness Gates

| Phase | Target | Gate Criteria | Exit Metrics |
|-------|--------|---------------|--------------|
| P1 | B3 Consolidation | Stable 39M+ efficient baseline; reproducible training | Sustained loss improvement on constrained GPU; zero integrity failures |
| P2 | AVT Release | Persona synthesis stable; privacy filters validated | Safety audit pass, latency ≤ target, avatar consistency score |
| P3 | IDC Alpha | Robotics IO harness + deterministic control | Loop jitter within bounds, fault recovery tests pass |
| P4 | IU1 Flagship | Full multimodal & memory integration | 10/10 conversation quality benchmark retained, protection tests green |
| P5 | IS1 System Launch | Kernel orchestration + lifecycle management | Hot reload success rate, policy engine compliance, persistent memory retention fidelity |

---

## 7. Differentiating Technical Pillars

| Pillar | Layered Progression | Cross-Reference |
|--------|---------------------|-----------------|
| Protection / Identity | Baseline (B) → Avatar consent + privacy (AVT) → Industrial compliance (IDC) → Guardian stack (IU1) → Policy kernel (IS1) | Protection-First Design Spec, Sacred_Covenant_Compliance_Framework |
| Memory Stratification | Ephemeral (B) → Persona scoped (AVT) → Deterministic ops logs (IDC) → Hierarchical episodic + semantic (IU1) → Long-horizon systemic fabric (IS1) | B2_MEMORY_OPTIMIZATION, enhanced_rag_memory_system_guide |
| Distillation & Maturation | Classic distill (B/AVT) → Shadow progressive (AVT → IU1) → Merge & replay (IU1) → Systemic multi-agent sync (IS1 future) | SHADOW_MODEL_DISTILLATION + distillation pipeline docs |
| Kernel & Orchestration | Minimal runtime (B) → Wrapper services (AVT) → Control adapters (IDC) → Cognitive orchestration (IU1) → Full kernel + liaison (IS1) | impressioncore_kernel_and_liaison_framework |
| Compliance & Audit | Baseline logging (B) → Persona consent ledger (AVT) → Industrial audit fabric (IDC) → Guardian policy enforcement (IU1) → System governance fabric (IS1) | code-audit-plan, Sacred_Covenant_Compliance_Framework |
| Modality Fusion | Incremental encoders (B) → Persona-optimized subset (AVT) → Deterministic sensor IO (IDC) → Enhanced latent routing (IU1) → Dynamic module hot-swap (IS1) | B3 architecture docs |

Guardian Stack: See [Guardian Stack Specification](../reference/GUARDIAN_STACK_SPECIFICATION.md) for enforcement layers, escalation flows, risk bands, metrics, and activation matrix. This lineup document (v1.0.0) aligns with Guardian Spec current active version (refer to that document header) and KPI Registry canonical thresholds. Cross-referenced in PRD §10 and Market Change Kernel Liaison notice.

---

## 8. Naming Conventions & Future Reserved Codes

| Code | Reserved Meaning | Status |
|------|------------------|--------|
| IU2 | Next flagship optimization cycle | Reserved |
| IS2 | Next intelligence system federation | Reserved |
| AVT-L | Lightweight / mobile avatar variant | Concept |
| IDC-RT | Real-time certified branch | Concept |

---

## 9. Documentation & Indexing Actions

- Added explicit identifiers (B3, b3, AVT, IDC, IU1, IS1) to ensure IDS search discoverability.
- Future: cross-reference in `Architectural_Definitions_B3.md` and update DOCUMENTATION_INDEX.md in next indexing pass.

---

## 10. Next Immediate Steps

1. Cross-link this lineup from DOCUMENTATION_INDEX.
2. Add minimal placeholder specs for IU1 & IS1 modules breakdown.
3. Define quantitative KPIs per readiness gate (latency, memory footprint, safety test suite thresholds).

---

## 11. Source Integrity Note

---

## 12. Gate KPI Definitions (Initial Targets)

| Gate | Metric | Definition | Target Threshold (Entry) | Exit Verification Method |
|------|--------|------------|--------------------------|---------------------------|
| P1 B3 Consolidation | Param Efficiency | Effective params achieving target perplexity vs baseline | ≥ 95% retention of baseline quality at 39M | Eval suite perplexity & loss trend |
| P1 B3 Consolidation | Training Stability | Consecutive epochs without divergence / NaN | ≥ 10 epochs stable | Training logs scan |
| P1 B3 Consolidation | VRAM Footprint | Peak VRAM during standard batch | ≤ 3.6 GB (GTX 1050 Ti headroom) | nvidia-smi sampling |
| P2 AVT Release | Avatar Consistency Score | Persona response style cohesion metric | ≥ 0.87 | Style classifier score |
| P2 AVT Release | Privacy Filter Recall | Detected PII tokens / total PII tokens | ≥ 99.5% | Redaction audit sample |
| P2 AVT Release | Safety FP Rate | Benign prompts blocked | ≤ 3% | Prompt panel test |
| P3 IDC Alpha | Control Loop Jitter | 95th percentile actuator latency variance | ≤ 12 ms | Robotics harness log |
| P3 IDC Alpha | Tool Mediation Denial Accuracy | Correct denials / total denials | ≥ 92% | Labeled action set |
| P3 IDC Alpha | Ledger Integrity Fail Rate | Failed writes / total events | < 0.05% | Ledger monitor |
| P4 IU1 Flagship | Conversation Quality | Human eval composite (coherence, safety, helpfulness) | 10/10 median | Human panel & rubric |
| P4 IU1 Flagship | Safety FN Rate | Harmful content passed undetected | < 0.5% | Guardian metrics |
| P4 IU1 Flagship | Mean Policy Overhead | Added latency per request | < 35 ms | Timing instrumentation |
| P4 IU1 Flagship | Memory Retention Fidelity | Recall accuracy over episodic window | ≥ 92% | Memory probe tests |
| P5 IS1 System Launch | Federated Policy Consistency | Divergent decisions across nodes / total | < 0.3% | Cross-node diff audit |
| P5 IS1 System Launch | Hot Reload Success Rate | Successful module swaps / total swaps | ≥ 98% | Kernel event log |
| P5 IS1 System Launch | Drift Alert Precision | True drift alerts / total alerts | > 90% | Labeled drift scenarios |
| P5 IS1 System Launch | Privacy Leakage Rate | Residual PII after system-level audit | < 0.1% | Federated audit batch |

Notes:

1. Targets sourced / harmonized with Guardian Stack metrics where applicable (see specification §7 & §8).
2. Thresholds marked as initial; KPI Registry centralizes authoritative values.
3. All dates & logs use Month Day, Year format per permanent standard.

---

## 13. Versioning & Cross-Reference Summary

| Artifact | Current Version | Reference Section |
|----------|-----------------|------------------|
| Model Lineup & Rollout (this doc) | 1.0.0 | All |
| Guardian Stack Specification | (see spec header) | Protection / Identity Pillar, §7 metrics |
| KPI Registry | (see registry header) | Gate KPI Definitions §12 |
| Flagship Platform PRD | 1.0.x (draft evolves) | PRD §10 Rollout Alignment |
| Market Change Kernel Liaison | Active (dated) | Pillar: Kernel & Orchestration |

Change Control: Increment minor version for additive clarifications; increment patch for typo / formatting; increment major only if series taxonomy or gate KPI set materially changes.

---
End of Document