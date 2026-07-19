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
