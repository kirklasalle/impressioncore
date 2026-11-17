# Mirror Sync Checklist (2026-07-18)

Created: July 18, 2026  
Updated: July 18, 2026  
Owner: ImpressionCore Documentation Governance

## Purpose

Provide a single operational checklist to keep canonical and mirror documentation synchronized.

## Canonical-Mirror Pairs

1. PRD
   - Canonical: docs/reference/prd.md
   - Mirror: docs/prd.md
2. Development Roadmap
   - Canonical: docs/process/development_roadmap.md
   - Mirror: docs/development_roadmap.md
3. Next Steps
   - Canonical: docs/process/next_steps.md
   - Mirror: docs/next_steps.md
4. Changelog
   - Canonical: docs/reference/CHANGELOG.md
   - Mirror: docs/CHANGELOG.md
5. User Guide
   - Canonical: docs/user/user_guide.md
   - Mirrors: docs/user_guide.md, docs/user_guide/user_guide.md

## Checklist Per Update Cycle

1. Confirm scope and target canonical document(s).
2. Apply canonical updates only.
3. Run focused review on canonical sections changed.
4. Update each affected mirror:
   - Add or refresh source-of-truth notice.
   - Set mirror mode (transitional or pointer-only).
   - Set last-validated date.
5. Update docs/DOCUMENTATION_INDEX.md control section when the doc set changes.
6. Validate IDS MCP discoverability paths:
   - .mcp/ids-mcp/README.md
   - docs/reference/mcp_server/IDS_MCP_USER_GUIDE.md
7. Record completion in changelog canonical source:
   - docs/reference/CHANGELOG.md

## Mirror Mode Flags

- Transitional: legacy body retained below source-of-truth notice.
- Pointer-only: only summary metadata and canonical links retained.

## Current Status Snapshot (2026-07-18)

- PRD mirror mode: pointer-only
- Development roadmap mirror mode: pointer-only
- Next-steps mirror mode: pointer-only
- Changelog mirror mode: transitional
- User guide mirror mode (docs/user_guide.md): transitional
- User guide mirror mode (docs/user_guide/user_guide.md): pointer-only

## November 2, 2026 status-notice cycle

### Subsequent implementation synchronization

- Updated canonical operator guide and full-body maintained mirror with the
  repaired supervisor/gateway, explicit Kinect lifecycle, optional speech
  setup and exact remaining limits. Refreshed pointer-only canonical links and
  target-validation metadata; no historical bodies were purged.
- Updated root/documentation entries, index, administration, PRD, roadmap,
  next steps, execution appendix and four public HTML status notices.
- Appended a repair addendum to the audit rather than rewriting the original
  pre-repair evidence. Added the dated repair report and sanitized runtime
  counters/status evidence; no service keys, camera frames or recordings.
- Added canonical changelog entry. Existing historical model/market/training
  qualifications still apply; their linked audit now opens with current repairs.
- IDS rebuild/search validation remains unperformed, not implicitly certified.

### Original audit-only update

- Canonical current-evidence notices added to `docs/user/user_guide.md`, `docs/process/next_steps.md`, `docs/process/development_roadmap.md`, `docs/process/EXECUTION_APPENDIX_2026_2027.md`, and `docs/reference/prd.md`.
- Maintained full-body user-guide mirror `docs/user_guide.md` received the same notice with location-correct links. Existing pointer-only guides, PRD, roadmap, and next-step mirrors remain unchanged; the historical July metadata above is not a new validation claim.
- Root README, docs README, documentation index, administration troubleshooting, four public HTML entry pages, and the active 2026 model/market documents received scoped evidence qualifications. Historical bodies and archives were preserved.
- Current evidence and acceptance gates: [platform audit](../analysis_reports/BUILDER_PLATFORM_AUDIT_20261102.md). No runtime fixes, driver/model/capture changes, or production certification are implied by this documentation cycle.
- IDS rebuild/search validation and canonical changelog synchronization are not performed by this bounded documentation update; do not interpret this record as completion of those operational checks.
