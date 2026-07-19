# Documentation Canonicalization Plan (July 18, 2026)

Created: July 18, 2026  
Updated: July 18, 2026  
Owner: ImpressionCore Documentation Governance

## Purpose

Define a single source of truth for high-impact documents and classify all related copies as mirror or archive.

## Canonical Mapping

1. PRD
   - Canonical: docs/reference/prd.md
   - Mirror: docs/prd.md

2. User Guide
   - Canonical: docs/user/user_guide.md
   - Mirrors: docs/user_guide.md, docs/user_guide/user_guide.md

3. Development Roadmap
   - Canonical: docs/process/development_roadmap.md
   - Mirror: docs/development_roadmap.md

4. Next Steps
   - Canonical: docs/process/next_steps.md
   - Mirror: docs/next_steps.md

5. Changelog
   - Canonical: docs/reference/CHANGELOG.md
   - Mirror: docs/CHANGELOG.md

## Operational Rules

1. Edit canonical files first.
2. Mirror files must include a source-of-truth notice and sync date.
3. After major updates, refresh docs/DOCUMENTATION_INDEX.md.
4. Validate discoverability via IDS MCP server docs and search flow.

## Sync Workflow

1. Update canonical file.
2. Propagate to mirrors.
3. Record sync note with date and scope.
4. Run IDS index/update checks.

## Mirror Sync Checklist

Use this operator checklist for each sprint and release:

- docs/process/MIRROR_SYNC_CHECKLIST_20260718.md

Required completion rule:

1. Each canonical update must include a checklist row update.
2. Any mirror still carrying full body content must be explicitly marked as transitional.
3. Pointer-only mirrors must keep canonical link, status, and last-validated date.

## Cleanup Guidance (Non-Destructive)

1. Do not delete mirrors until all consumers are confirmed migrated.
2. Replace stale mirror bodies with concise pointers when safe.
3. Move retired variants to docs/archive with timestamped note.

## Mirror Modes

1. Transitional mirror: source-of-truth notice + retained legacy body content.
2. Pointer-only mirror: concise pointer to canonical doc + sync metadata.
3. Archive mirror: migrated to docs/archive with historical note.
