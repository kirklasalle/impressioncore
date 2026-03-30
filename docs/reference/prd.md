# ImpressionCore Product Requirements Document (PRD) – Canonical

**Created:** February 18, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\prd.md #api #documentation #gpu_optimization #memory_management #multimodal #performance #security #testing #tokenization #training #official #permanent  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## Executive Summary

ImpressionCore is a brain-inspired multimodal AI framework delivering enterprise capabilities on consumer hardware through the 39M Parameter Foundation and protection-first design. It achieves 10/10 conversation quality with <1GB VRAM on GTX 1050 Ti and preserves complete B3 architecture within constitutional constraints.

## Table of Contents

1. Product Overview
2. Breakthrough Achievements
3. Market Revolution
4. Target Audience
5. Core Product Features
6. Technical Architecture
7. Performance Requirements
8. Security and Protection
9. User Experience
10. Integration and Deployment
11. Scalability
12. Compliance and Regulatory
13. Development Phases and Roadmap
14. Success Metrics and KPIs
15. Risk Assessment and Mitigation
16. Resource Requirements
17. Quality Assurance
18. Documentation Requirements
19. Support and Maintenance
20. Future Considerations
21. Conclusion and Document Control

---

## Product Overview

ImpressionCore democratizes sophisticated AI by preserving complete B3 architecture within 39M parameters, optimizing for GTX 1050 Ti accessibility, and embedding protection-first capabilities (user avatar creation, digital identity security). It operates under constitutional authority:

- Permanent Architectural Framework — see docs/reference/IMPRESSIONCORE_PERMANENT_ARCHITECTURAL_FRAMEWORK.md
- Permanent Active Directives — see docs/reference/Permanent_Active_Directives.md
- ImpressionCore Standards Official — see docs/reference/IMPRESSIONCORE_STANDARDS_OFFICIAL.md

Success criteria (overview):

- Consumer hardware democracy: full operation on NVIDIA GTX 1050 Ti (4GB VRAM) with < 1GB VRAM inference target
- Constitutional compliance: preserve complete B3 architecture within 39M parameters without feature loss
- Protection-first design: identity security, local-first processing, and Fifth Law adherence
- Production discipline: single source of truth documentation, standards-compliant headers, and IDS discoverability

## Breakthrough Achievements

- <1GB VRAM inference, >20 samples/second on GTX 1050 Ti
- 10/10 conversation quality via concentrated intelligence
- Full B3 architecture preserved: Assembly of Experts, Multi-Head Latent Attention, multimodal support
- Protection-first: secure impression and avatar creation

## Market Revolution

Transforms AI accessibility by enabling enterprise-quality AI on consumer GPUs, expanding the addressable market by up to 40x, with privacy-by-design local processing.

## Target Audience

Primary: AI enthusiasts, independent developers, educational institutions, SMBs, researchers. Secondary: creators, privacy-conscious users, developing markets.

## Core Product Features

### B3 39M Parameter Foundation (Constitutional)

- Assembly of Experts (8 experts; 2 active per token)
- Multi-Head Latent Attention (optimized for VRAM)
- Brain-inspired layers; unified tokenizers

### Protection-First Design

- User avatar creation (visual, voice, behavioral)
- Deepfake detection, identity theft prevention, secure impression generation
- Local processing; quantum-resistant encryption

### Multimodal Engine

- Text: NLU, high-quality generation, multi-language
- Image: understanding, generation, VQA, style transfer
- Audio: ASR, TTS, voice cloning; real-time processing
- Cross-modal fusion and synchronized generation

## Technical Architecture

- Modular core with plugin extensions; REST/WebSocket APIs; SDKs
- Knowledge store (UKS) foundations for memory/knowledge
- Adaptive Memory Management: checkpointing, mixed precision, CPU offload
- Model Management: versions, optimization, training pipeline foundations

Detailed components and contracts:

- Text/Image/Audio encoders with unified tokenizer interfaces and cross-modal fusion
  - Text: DialoGPT-small compatible loader with secure safetensors handling
  - Image: CLIP ViT-B/32 extraction for visual embeddings
  - Audio: Wav2Vec2-base pipeline for ASR/voice features
- Assembly of Experts (MoE): 8 experts, top-2 per token, 2048 expert dims; router with load balancing and dropout safety
- Multi-Head Latent Attention: VRAM-aware heads with gradient checkpointing on long contexts
- TurboQuant KV Cache Compression (arXiv:2504.19874, ICLR 2026): Two-stage vector quantization (PolarQuant + QJL) compressing KV cache to 3.5 bits/channel with zero accuracy loss. Training-free, pure PyTorch, saves ~59MB at 4K tokens and ~960MB at 64K tokens.
- Brain Simulation Adapter: memory consolidation, attention modulation hooks
- Unified Knowledge Store (UKS): pluggable vector index; CPU memory mapped cache with spillover
- F:/models Management Integration (mandatory)
  - All model lifecycle operations MUST use manage_f_models.py
  - Canonical locations: F:/models/checkpoints, F:/models/training, F:/models/distillation, F:/models/deployment
  - Registry and provenance: models managed with registry.json and training_sessions/ metadata
  - Failure policy: if F:/models is missing, training/inference MUST fail fast with actionable guidance

API surface (minimum):

- Inference: POST /v1/infer (text|image|audio|multimodal); WS /v1/stream
- Embeddings: POST /v1/embeddings
- Models: GET /v1/models; POST /v1/models/switch
- UKS: POST /v1/uks/query; POST /v1/uks/upsert
- Admin: GET /v1/health; GET /v1/metrics; POST /v1/snapshots

Acceptance criteria:

- Architecture compiles and runs on Windows with Python 3.10; Pylance shows no critical errors
- Inference/startup succeeds when F:/models exists and indicates corrective action when missing
- MoE routing activates exactly 2 experts/token with <5% variance across batches (load balance)
- Tokenizers share a unified vocabulary contract; regression tests cover round-trip encode/decode

## Performance Requirements

- Text throughput 10k+ tokens/s; image 30+/min; audio <50ms latency (targets)
- GPU memory <90% peak; system RAM <75%; zero memory leaks
- API latency <100ms simple; <5s complex; WebSocket <50ms updates

Target hardware and constraints:

- GPU: NVIDIA GTX 1050 Ti (4GB VRAM)
- CPU: Intel Core i5 4460 @ 3.20GHz; RAM: 32GB DDR3

Performance acceptance tests:

- Inference VRAM: < 1.0 GB peak on GTX 1050 Ti for standard chat prompts (TurboQuant KV cache compression saves ~59MB at 4K context, ~960MB at 64K context)
- Sustained conversation: 10/10 subjective quality on curated benchmark across 50 turns
- Latency: p95 < 150ms for simple text prompts; p99 < 5s for complex multimodal tasks
- Memory safety: no increasing RSS trend over 30 minutes under mixed workloads
- Training pipeline: gradient checkpointing enabled; stable AMP with no NaN explosions over 10k steps

## Security and Protection

- MFA/SSO; RBAC/ABAC; least privilege
- AES-256 at rest; TLS 1.3 in transit; HSM-backed keys
- Anonymization, masking, retention policies, encrypted backups
- Network isolation, IDS/IPS, VPN support; OWASP compliance

Constitutional protections:

- Fifth Law enforcement (no legal authority, no adjudication by AI) — see docs/reference/Permanent_Active_Directives.md
- Protection-first design for digital identity and avatar generation — see docs/reference/PROTECTION_FIRST_DESIGN_SPECIFICATION.md

Security acceptance criteria:

- Secrets never stored in plaintext in repo; .env and secret stores required
- Encryption at rest applied to model artifacts and UKS indexes; keys rotated per policy
- Endpoints hardened against OWASP Top 10; automated DAST/SAST integrated into CI
- Privacy: PII handling with data minimization, masking, and opt-in retention

## User Experience

- WCAG 2.1 AA; screen reader/keyboard support; color-blind safe
- Onboarding, in-context help, clear errors, progress indicators
- Mobile-responsive UI; offline core functions

UX acceptance criteria:

- Color palette adheres to diagram/style standards — see docs/reference/IMPRESSIONCORE_STANDARDS_OFFICIAL.md
- Error dialogs include actionable remediation suggestions
- Progress indicators for long-running tasks, including training/distillation workflows

## Integration and Deployment

- OpenAPI 3; webhooks (signed); rate limits; pagination/filtering
- SDKs: Python/JS; CI/CD; monitoring (Prometheus/Grafana)
- DBs: Postgres/MySQL/SQLite/MongoDB; vector DBs; cloud optional

Operational integration requirements:

- F:/models is the single source of truth for model artifacts; all packaging uses manage_f_models.py
- IDS Documentation System integrated for discoverability; canonical docs linked from UI where applicable
- MCP Servers available for automation and validation:
  - .mcp/impressioncore-ids (documentation search/indexing)
  - .mcp/impressioncore-vrgc (system assessment, training monitor, covenant guardian)

Deployment acceptance criteria:

- Production package emits to F:/models/deployment/production with versioned manifest
- Health endpoints expose build version, git commit, and model checksum
- Rollback tested: prior production model can be restored from F:/models/deployment/backup

## Scalability

- Horizontal: LB, discovery, health checks, auto-scaling
- Vertical: dynamic allocation; GPU utilization; caching
- Global: CDN, multi-region, compliance zones; multi-tenant isolation

Scale acceptance criteria:

- Stateless service scale-out verified to 3 instances with shared UKS backend without consistency errors
- Caching hit rate >= 80% on hot paths under synthetic load

## Compliance

- GDPR, CCPA; ISO 27001, SOC 2; NIST alignment
- Sector: HIPAA, PCI DSS; FedRAMP/FISMA readiness (enterprise)

Compliance acceptance criteria:

- DPIA templates completed for core flows; data maps documented
- Audit logs retained per policy; tamper-evident storage for security logs

## Development Phases and Roadmap

- Phase 1: Foundation (infra, memory optimization, CLI)
- Phase 2: Multimodal engines (text/image/audio, cross-modal)
- Phase 3: Sweet Spot optimization (161M→39M with validation)
- Phase 4: Web UI, UKS, training framework, API/SDKs
- Phase 5: Security/compliance
- Phase 6: Performance/scalability

Milestone exit criteria (per phase):

- Phase 1: F:/models initialized; core inference passes minimal acceptance; IDS index up-to-date
- Phase 2: Cross-modal generation demo; UKS read/write API available
- Phase 3: Verified 39M parameter preservation of B3 features with regression tests
- Phase 4: Stable web UI with accessibility checks; SDKs published with examples
- Phase 5: Security baseline validated by automated scans and manual penetration test
- Phase 6: p95 latency and throughput targets achieved in CI performance suite

## Success Metrics and KPIs

- Technical: throughput/latency/memory utilization; uptime; scalability
- Business: adoption/retention/satisfaction; market share; revenue
- Security: zero critical vulns; compliance certifications; incident rate

Metrics instrumentation:

- Prometheus counters for requests, latency, errors; GPU/VRAM gauges
- Quality scoring harness for 10/10 conversational benchmarks

## Risk Assessment and Mitigation

- Technical: hardware compatibility, performance regressions, security
- Business: competitive pressure, market adoption
- Regulatory: evolving privacy/AI rules

Mitigations:

- Hardware: CI smoke tests on CPU-only and simulated low-VRAM configurations
- Performance: perf budget alerts and rollback on regressions
- Security: periodic red team exercises; dependency pinning and SBOM

## Resource Requirements

- Team composition across dev/ML/devops/QA/security/product/design/support
- Infra for dev/test/prod; budget outlines

Artifacts and environments:

- Python 3.10 environment; requirements.txt managed and pinned
- Windows primary dev target; Linux CI runners for cross-validation

## Quality Assurance

- Automated unit/integration/perf/security tests; manual UAT/accessibility
- Continuous QA: code review, static analysis, dependency scans

Test matrix (minimum):

- Unit: tokenization round-trip; MoE routing selection; memory utils
- Integration: F:/models lifecycle (init/status/package), inference endpoints, UKS queries
- Performance: latency and throughput with synthetic workloads
- Security: SAST/DAST; secret scanning; dependency vulnerability scans
- Accessibility: WCAG checks on web UI flows

## Documentation Requirements

- Developer API/architecture/integration/deployment
- User guides, quick starts, troubleshooting
- Admin/security/monitoring/backup-recovery; process docs

Documentation governance:

- Follow canonical standards — see docs/reference/IMPRESSIONCORE_STANDARDS_OFFICIAL.md
- Permanent date format: Month Day, Year (e.g., August 11, 2025)
- Single canonical PRD (this file); prior PRDs archived with clear pointers
- IDS index rebuild after significant doc changes

## Support and Maintenance

- Support tiers; channels; SLAs and metrics
- Maintenance windows; emergency procedures; LTS policy

Operational runbooks:

- Terminal Sanctity Principle: never run commands in terminals with active long-running jobs; open a new terminal for probes
- Backup cadence: periodic archives of src/, docs/, requirements.txt, manage_f_models.py to backups/ with timestamp
- Environment activation: always activate .venv310 before running scripts in new terminals

## Future Considerations

- Tech evolution (quantum, neuromorphic, edge)
- Market trends (democratization, privacy, edge AI)
- Partnerships (hardware/cloud/academia)

Explorations:

- Progressive distillation pipelines (Ollama/remote API) integrated with F:/models/distillation
- Edge deployment options for ultra-low VRAM devices

## Conclusion and Document Control

ImpressionCore delivers constitutional B3 capability on consumer hardware with protection-first design. This PRD governs development, integration, and deployment, and will be reviewed monthly.

Document Control:

- Version: 4.0.0
- Status: Approved
- Next Review: September 10, 2025
- Approval Authority: Product Management
- Distribution: Engineering, Product, Executive

Related Documents:

- Permanent Architectural Framework — docs/reference/IMPRESSIONCORE_PERMANENT_ARCHITECTURAL_FRAMEWORK.md
- Permanent Active Directives — docs/reference/Permanent_Active_Directives.md
- ImpressionCore Standards Official — docs/reference/IMPRESSIONCORE_STANDARDS_OFFICIAL.md

---

## Appendices

### Appendix A: Historical PRD (b1 Milestone Summary)

Key achievements (from docs/prd.md): stable multimodal architecture; adaptive memory management; brain simulation adapter; full MoE; comprehensive interfaces and APIs; performance and reliability verified on GTX 1050 Ti. Use cases UC-B1-001..006 validated; success criteria achieved.

### Appendix B: Prior App Overview (Reference)

Name: ImpressionCore – Lifelong Digital Assistant / Personal AI ID
Tagline: One chance for a first Permanent Digital Companion and Secure Digital Identity for Life.
Core goals: lifelong assistant, secure Digital ID, unified platform, privacy-first, robust and trustworthy.

### Appendix C: F:/Models Management System (Normative)

Summary:

- Centralized, mandatory model lifecycle management under F:/models
- Launcher: manage_f_models.py (project root); Manager: src/core/models/management/f_models_manager.py
- Reference (archived overview): docs/archive/archive/reference/f_models_management_system.md

Requirements:

- Initialize and maintain canonical directory structure: checkpoints/, training/, distillation/, deployment/
- Registry for model provenance: F:/models/management/registry.json; training_sessions/ with metadata
- All training, distillation, and packaging steps MUST write into F:/models; legacy locations are read-only

Acceptance tests:

- Running manage_f_models.py --status reports inventory without error
- Packaging emits versioned artifacts under F:/models/deployment/* with manifests

### Appendix D: IDS and MCP Server Integration (Normative)

IDS (ImpressionCore Documentation System):

- Canonical index lives in docs/DOCUMENTATION_INDEX.md; rebuild index on PRD updates
- Tagging system used for discoverability; headers standardized per standards doc

MCP Servers:

- impressioncore-ids: documentation search, index rebuild, tag discovery, system status
- impressioncore-vrgc: hardware assessment, training monitor, Sacred Covenant verification

Operational notes:

- After major documentation or configuration changes, run IDS index rebuild and system validation
- Maintain header compliance across 2,400+ files; track compliance rate as a KPI
