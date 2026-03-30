# Manual Tag Manifest (Interim)

**Created:** August 24, 2025  
**Updated:** December 29, 2025  
**Author:** GitHub Copilot  
**Tags:** #documentation #ids #tag_manifest #checkpoint_governance #canonical_checkpoint_set  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

Purpose: Provide a resilient, human-auditable manifest of newly introduced or critical tags pending full restoration of the original documentation indexer.

## Newly Introduced Tags (Aug 24, 2025)

| Tag | Origin File | Description |
|-----|-------------|-------------|
| checkpoint_governance | CHECKPOINT_GOVERNANCE_POLICY.md | Checkpoint lifecycle policy & statuses |
| canonical_checkpoint_set | CANONICAL_CHECKPOINT_SET.md | Canonical force-keep anchors & audit baseline |

## Usage Guidance

1. Keep this manifest updated when adding governance or canonical-related documents.
2. After updating tags, run lightweight indexer: `python src/dev_tools/documentation_indexer.py`.
3. Once the full historical indexer is restored, integrate these tags into automated extraction and retire this file.

## Retirement Criteria

- Full indexer restored + new tags confirmed discoverable via IDS search.
- Tag presence validated in two consecutive system validations.

---
*Interim safeguard for discoverability and search consistency.*