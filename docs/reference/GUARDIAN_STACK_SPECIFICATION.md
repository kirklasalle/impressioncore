# Guardian Stack Specification

**Created:** August 22, 2025  
**Updated:** December 29, 2025  
**Author:** GitHub Copilot  
**Tags:** #guardian_stack #protection #policy #compliance #identity #audit #risk #security #kernel #ids  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

**Version:** 1.0.0  
**Author:** GitHub Copilot  
**Tags:** #guardian_stack #protection #policy #compliance #identity #audit #risk #security #kernel #ids  
**Category:** Reference  
**Status:** Active  
**IDS Integration:** Indexed (post-save)  

---

## 1. Purpose & Scope

The Guardian Stack is ImpressionCore's layered real‑time protection, governance, and compliance framework that envelopes model inference, tool execution, memory access, and outbound responses. It ensures: (1) safety (no harmful output / actions), (2) identity & consent integrity, (3) privacy preservation, (4) regulatory & covenant compliance, (5) deterministic auditability, and (6) adaptive risk‑aware mediation of capabilities.

Applicable Series Progression:

- B: Minimal baseline (sanitization + basic output filter + logging)
- AVT: Adds identity / consent envelope + persona memory scoping
- IDC: Industrial compliance, deterministic actuation safety & audit schema
- IU1: Full adaptive guardian stack (risk scoring + escalation automation)
- IS1: System-wide policy kernel with multi-model federated governance

---

## 2. Design Principles

| Principle | Description | Enforcement Mechanism |
|-----------|-------------|------------------------|
| Least Exposure | Only minimum necessary context/memory exposed per request | Context slicer + memory policy resolver |
| Defense in Depth | Independent layered gates; single failure not catastrophic | Sequential gating pipeline & fallback logic |
| Deterministic Replay | Every decision reproducible from signed ledger | Immutable event ledger + hash chained records |
| Adaptive Tightening | Dynamic policy strictness based on risk score | Risk bands + rule set modulation |
| Separation of Duties | Policy evaluation isolated from model generation | External policy engine microservice |
| Privacy First | PII detection + selective redaction before model view | Redaction filters + classification stage |
| Fail Safe | On uncertainty → degrade (deny / partial / human review) | Escalation handler + policy thresholds |
| Continuous Improvement | Feedback loops refine filters & scoring | Blocked / allowed exemplar harvesting to shadow distillation |

---

## 3. Layer Architecture (Inner → Outer)

| # | Layer | Core Functions | Key Artifacts | Series Activation |
|---|-------|----------------|---------------|------------------|
| 1 | Input Gate & Sanitizer | Schema validation, size limits, MIME/type normalization, rate shaping | Input policy manifest | B+ |
| 2 | Identity & Consent Envelope | Verify session, avatar identity, consent scope, capability claims | Identity tokens, consent ledger | AVT+ |
| 3 | Context & Memory Guard | Memory slice selection, purpose scoping, TTL enforcement, redaction | Memory policy map, redaction rules | AVT+ (expanded IU1/IS1) |
| 4 | Policy Engine & Risk Scorer | Rule evaluation (safety, covenant, compliance), dynamic risk scoring | Policy rule DSL, risk profile vector | IDC+ (full in IU1) |
| 5 | Tool / Action Mediator | Validates tool/actuator intents, sandbox or dry‑run, concurrency limits | Tool capability registry | IDC+ |
| 6 | Output Auditor & Redactor | Toxicity/PII/leakage scan, transformation, partial block | Output classifier ensemble | B (basic) → full IU1 |
| 7 | Event Ledger & Trace Fabric | Immutable hashed event chain, signature, correlation IDs | Ledger store, hash chain | IDC+ → federated IS1 |
| 8 | Escalation & Intervention | Human review queue, auto‑deny, secondary model cross-check | Escalation workflow config | IU1+ |
| 9 | Anomaly & Drift Monitor | Baseline divergence detection, temporal drift, latency spikes | Drift profiles, metric buffers | IU1+ |
| 10 | Continuous Learning Feedback Loop | Curates exemplars for shadow distillation & policy refinement | Feedback dataset, labeling schema | IU1+ / IS1 system-wide |

---

## 4. Data Flow (Conceptual)

```text
[Client / Sensor Input]
        |
        v
[1 Input Gate] -> sanitized_batch
        |
        v
[2 Identity/Consent] -> authorized_context
        |
        v
[3 Memory Guard] --(policy memory slice)--> enriched_context
        |
        v
[4 Policy+Risk] -> (risk_score, allowed_capabilities)
        |
        +--> if risk > band_threshold => [8 Escalation]
        |
        v
[Model Inference / Tool Mediation (5)]
        |
        v
[6 Output Auditor]
        |
        v
[7 Ledger Write] -- hash(previous_hash + event_payload)
        |
        v
[9 Drift Monitor + 10 Feedback]
        |
        v
[Final Response]
```

---

## 5. Policy Engine & Rule Semantics

Policy expressed as layered rule bundles:

- Core Safety: disallowed content categories, self-harm, violence, manipulation.
- Identity / Consent: persona scope, capability whitelist, session expiration.
- Privacy: PII classification (regex + ML), redaction transform mapping.
- Compliance: jurisdictional & industrial (IDC) modules; modular plugin approach.
- Covenant & Constitutional: Fifth Law enforcement, protection-first directives.

Rule Evaluation Order:

1. Structural (format / size)
2. Identity / Consent
3. Privacy pre-filter
4. Core safety
5. Compliance overlays
6. Adaptive heuristics (risk adjustments)
7. Final allow / transform / deny decision

Risk Score Vector (example components):

- content_risk (toxicity / leakage probability)
- action_risk (tool / actuator privilege level)
- privacy_risk (PII density)
- anomaly_risk (deviation from typical embedding pattern)
- compliance_risk (regulated domain tag)

Composite risk = weighted_sum + dynamic adjustments (time of day, escalation history, drift signals).

Bands: GREEN (auto proceed), YELLOW (enhanced auditing / partial context), ORANGE (sandbox / cross‑model validation), RED (deny or escalate).

---

## 6. Event Ledger & Trace Fabric

Event Record (logical fields):

```json
{
  "event_id": "uuid",
  "timestamp": "August 22, 2025 04:15:00 PM",
  "session_id": "uuid",
  "layer": "output_auditor",
  "input_hash": "sha3-256",
  "decision": "allow|transform|deny|escalate",
  "risk": {"composite": 0.42, "components": {"content":0.12,"privacy":0.05,"action":0.25} },
  "policies_triggered": ["safety.v1.block_low_confidence_tool"],
  "redactions": [ {"type": "pii_email", "count": 2} ],
  "capabilities_granted": ["tool.search"],
  "hash_prev": "...",
  "hash_self": "..."
}
```

Retention & Integrity:

- Hash chaining (hash_self = H(prev_hash || serialized_event))
- Optional external notarization (future) for IDC regulated environments
- Selective field encryption (PII redaction metadata)

---

## 7. Metrics & KPIs (Initial Targets – To Calibrate)

| Metric | Definition | Target (Phase IU1) | Target (Phase IS1) |
|--------|------------|--------------------|--------------------|
| Safety FN Rate | Harmful content passed undetected | < 0.5% | < 0.2% |
| Safety FP Rate | Benign content incorrectly blocked | < 2.5% | < 1.5% |
| Mean Policy Overhead | Added latency (ms) per request | < 35 ms | < 25 ms |
| Redaction Leakage Rate | Residual PII tokens / total PII tokens | < 0.3% | < 0.1% |
| Intervention Latency | Detection → mitigation | < 150 ms | < 100 ms |
| Drift Alert Precision | True drift alerts / total alerts | > 90% | > 95% |
| Ledger Write Failure Rate | Failed writes / total events | < 0.05% | < 0.01% |

---

## 8. Series-Specific Activation Matrix

| Layer | B | AVT | IDC | IU1 | IS1 |
|-------|---|-----|-----|-----|-----|
| Input Gate | Basic | Enhanced | Enhanced | Adaptive | Federated |
| Identity / Consent | Basic session | Avatar envelope | Audit-grade | Adaptive persona | Federated multi-tenant |
| Memory Guard | Size clipped | Persona-sliced | Deterministic logs | Hierarchical gating | Global fabric policy |
| Policy Engine | Static core | + Consent rules | + Industrial modules | + Adaptive scoring | Unified policy kernel |
| Tool Mediator | Minimal | Minimal | Deterministic gating | Dynamic gating | Capability graph orchestration |
| Output Auditor | Basic filter | Persona-tuned | Compliance augmented | Multi-model ensemble | Federated audit mesh |
| Ledger | Minimal logs | Extended session | Immutable chain | Signed chain | Cross-node aggregation |
| Escalation | Manual fallback | Manual + templated | Tiered | Automated multi-path | Federated arbitration |
| Drift Monitor | None | Light stats | Basic thresholds | Full semantic + latency | Cross-model correlation |
| Feedback Loop | Manual curation | Persona exemplars | Safety reinforcement | Shadow pipeline integration | Systemic multi-agent |

---

## 9. Implementation Phases

| Phase | Focus | Deliverables |
|-------|-------|-------------|
| GS-P1 | Baseline (B/early AVT) | Sanitizer, basic output audit, minimal ledger |
| GS-P2 | AVT Identity Integration | Consent envelope, persona memory scoping, redaction v1 |
| GS-P3 | IDC Compliance Core | Deterministic tool gating, industrial policy modules, hashed ledger |
| GS-P4 | IU1 Adaptive Guardian | Risk scoring engine, escalation automation, drift monitor, feedback loop |
| GS-P5 | IS1 Federated Kernel | Policy kernel unification, cross-model governance, federated ledger & orchestration |

---

## 10. Integration Points

| Component | Hook Style | Purpose |
|----------|-----------|---------|
| Kernel / Liaison | Pre & post inference interceptors | Central policy adjudication & capability routing |
| Memory Subsystem | Policy-mediated accessor | Scoped retrieval & redaction |
| Tool Registry | Capability descriptor ingestion | Risk classification & gating |
| Training Pipeline | Feedback dataset export | Reinforcement & distillation tuning |
| Logging / Metrics | Structured event emission | Observability & SLA compliance |

---

## 11. Future Extensions

- Adaptive cryptographic ledger anchoring (external trust provider)
- Zero-knowledge redaction proofs for regulated industries
- Multi-agent arbitration layer (IS2 concept)
- Formal verification of high-risk policy rules
- On-device compact guardian mode for edge deployments

---

## 12. Glossary

| Term | Definition |
|------|------------|
| Guardian Stack | Layered safety & governance framework wrapping model operations |
| Risk Band | Categorical threshold (GREEN/YELLOW/ORANGE/RED) guiding mediation |
| Escalation | Transition to higher scrutiny path (human, secondary model, deny) |
| Drift | Statistically significant behavioral shift vs baseline profile |
| Shadow Distillation | Progressive alignment of subordinate model instance feeding maturation |
| Capability Graph | Structured mapping of tools/actions with dependency & risk metadata |

---

## 13. Cross References

- Protection-First Design Specification
- Sacred_Covenant_Compliance_Framework.md
- SHADOW_MODEL_DISTILLATION.md
- impressioncore_kernel_and_liaison_framework.md
- code-audit-plan.md
- B2_MEMORY_OPTIMIZATION.md / enhanced_rag_memory_system_guide

---

## 14. Change Log

| Date | Change | Author |
|------|--------|--------|
| August 22, 2025 | Initial specification created | GitHub Copilot |
| August 22, 2025 | Added version 1.0.0 & lineup v1.0.0 cross-ref | GitHub Copilot |

---
End of Document