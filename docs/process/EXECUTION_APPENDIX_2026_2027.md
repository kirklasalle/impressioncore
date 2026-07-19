# ImpressionCore Execution Appendix (2026-2027)

Created: July 18, 2026  
Updated: July 18, 2026  
Owner: ImpressionCore Core Team

## Purpose

This appendix is the canonical execution backlog for the next delivery cycle. It aligns with:

- docs/development_roadmap.md
- docs/process/development_roadmap.md
- docs/prd.md
- docs/reference/prd.md
- docs/strategic/IMPRESSIONCORE_MODEL_LINEUP.md
- docs/architecture/IMPRESSIONCORE_C_BRAIN_TRIAD_ARCHITECTURE.md
- docs/analysis_reports/B_SERIES_BUILDER_DASHBOARD_SECOND_DRAFT_20260718_191233.md

## Workstreams and Deliverables

## WS1 - B-Series Productization (B1 39M, B2 50M, B3 504M)

### WS1 Objectives

- Make B-series offerings first-class across Builder, Runtime, and documentation.
- Eliminate metadata drift between declared model stage and discovered artifacts.

### WS1 Delivery Tasks

1. Replace path-heuristic offering mapping with explicit metadata manifests per artifact.
2. Add offering manifest schema validation in startup checks.
3. Add offering registry endpoint consumed by dashboard/runtime clients.
4. Add regression tests for offering preset application and persisted configs.
5. Add migration script for older model directories missing offering manifests.

### WS1 Exit Criteria

- Builder, Runtime, and Dashboard all resolve offering from manifest (not path string matching).
- Passing tests for preset loading and model discovery schema.

## WS2 - Brain-Triad C1 Integration (Governed)

### WS2 Objectives

- Operationalize C1 Colossus as a controlled integration path after B-series stabilization.

### WS2 Delivery Tasks

1. Define triad runtime contract for left/right/colossus request lifecycle.
2. Implement confidence-weighted synthesis API contract and trace logging.
3. Add neutral baseline model selection policy for colossus arbiter.
4. Add triad observability metrics: per-hemisphere latency, confidence, and mix ratios.
5. Build staged toggles: Off -> Observe -> Assist -> Enforce.

### WS2 Exit Criteria

- Colossus integration path can run in observe mode without impacting existing runtime paths.
- Full audit trace for triad blend decisions is recorded.

## WS3 - Builder System Hardening

### WS3 Objectives

- Convert current mixed simulation/live surfaces into consistent API-backed behavior.

### WS3 Delivery Tasks

1. Remove/retire training simulation paths in unified builder UI.
2. Bind start/pause/stop/checkpoint actions to live Builder API responses only.
3. Add full checkpoint browser with offering labels and integrity hashes.
4. Add form-side and server-side schema validation parity.
5. Add smoke tests for all Builder routes under low-VRAM profile.

### WS3 Exit Criteria

- Unified Builder no longer diverges between simulation and live training state.
- All key Builder routes have passing contract tests.

## WS4 - Runtime Native B3 Path

### WS4 Objectives

- Reduce full dependency on external runtime providers for core B-series inference.

### WS4 Delivery Tasks

1. Add native B-series model load path into runtime routing layer.
2. Preserve existing fallback routing to external providers.
3. Add runtime model-source policy: native-first, fallback-on-fail.
4. Add streaming output and token telemetry for native inference.
5. Add comparative benchmark scripts (native vs fallback).

### WS4 Exit Criteria

- Runtime can process request end-to-end with local B-series weights.
- Fallback remains available and policy-controlled.

## WS5 - Repository and Quality Cleanup

### WS5 Objectives

- Reduce technical debt that blocks scale, contributors, and release confidence.

### WS5 Delivery Tasks

1. Remove/relocate oversized tracked binaries and enforce artifact policy.
2. Archive or delete empty/stub files in active paths.
3. Consolidate entrypoint ambiguity and retire placeholder paths.
4. Split large monolith modules into route/domain packages.
5. Raise automated test coverage gate in phases (1.5% -> 10% -> 20%).

### WS5 Exit Criteria

- Repository health baseline passes policy checks.
- CI quality gate enforced on pull requests.

## WS6 - Security and Compliance Stabilization

### WS6 Objectives

- Close high-severity security and operational governance gaps.

### WS6 Delivery Tasks

1. Enforce constant-time API key comparisons.
2. Add secret scanning and environment hygiene checks.
3. Remove hardcoded absolute paths from runtime and service layers.
4. Add log rotation and retention defaults.
5. Add security regression tests for auth and input validation.

### WS6 Exit Criteria

- Security checks pass in CI and preflight scripts.
- Runtime hardcoded-path policy violations are zero.

## WS7 - Docs, DX, and Onboarding Consistency

### WS7 Objectives

- Keep all user/dev/strategic docs synchronized to one execution truth.

### WS7 Delivery Tasks

1. Keep roadmap, PRD, README, user guide, developer guide, and changelog in sync each sprint.
2. Enforce canonical-vs-mirror governance using docs/process/DOCUMENTATION_CANONICALIZATION_PLAN_20260718.md.
3. Maintain docs/process/MIRROR_SYNC_CHECKLIST_20260718.md for each canonical-change cycle.
4. Convert high-duplication mirrors to pointer-only mode as consumer dependencies are validated.
5. Add doc freshness checks using IDS indexes and doc timestamps.
6. Add release-note template for model lineup and architecture impacts.
7. Add explicit support matrix by hardware tier and operating system.
8. Add user runbooks for backup, recovery, and model integrity checks.

### WS7 Exit Criteria

- All top-level guides cross-reference this appendix and latest sprint state.
- IDS index updates performed after doc updates.

## Milestone Plan

## Milestone M1 (0-30 days)

1. Replace offering heuristics with explicit manifests.
2. Builder API and UI parity for live training operations.
3. Security quick wins (auth compare, path cleanup start, log rotation).
4. Coverage gate raised to 10% for key packages.

## Milestone M2 (31-60 days)

1. Runtime native B-series inference path (beta).
2. Triad C1 observe mode integrated with telemetry.
3. Repository debt cleanup pass complete for active paths.
4. Full Builder checkpoint and integrity UX.

## Milestone M3 (61-90 days)

1. Triad C1 assist mode pilot.
2. Native-vs-fallback benchmark publication.
3. Coverage gate raised to 20% with contract-test suite expansion.
4. Release candidate doc and runbook finalization.

## Dependencies and Risks

1. Artifact metadata migration may expose legacy model inconsistencies.
2. Runtime native path requires careful memory profile control on 4GB VRAM targets.
3. Triad C1 integration requires strict governance and staged rollout controls.
4. Monolith decomposition may temporarily increase integration complexity.

## Governance

1. This appendix is the active backlog source for 2026-2027 execution.
2. Roadmap and PRD remain normative product documents; this file carries sprint-level action detail.
3. Update cadence: weekly progress update, monthly baseline refresh.
