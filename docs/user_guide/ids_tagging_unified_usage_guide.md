# IDS + Tagging Unified Usage Guide

**Created:** June 04, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\user_guide\ids_tagging_unified_usage_guide.md #documentation #pytorch  
**Category:** User Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## Overview

This guide explains how to use the new unified ImpressionCore Documentation System (IDS) and tagging system for project-wide search, navigation, and cross-referencing.

## Features

- Unified search across all documentation and codebase files
- Tag-based, keyword, file type, and category search
- Cross-referencing between docs and code
- Rich UI with statistics, analytics, and index rebuilding

## How to Use

### 1. Launch the Enhanced IDS Interface

```bash
python docs/enhanced_ids.py
```

### 2. Main Menu Options

- **Search & Discovery**: Search by tag, keyword, file type, or category
- **View Statistics**: See project-wide stats and most common tags
- **Rebuild Indices**: Re-index all docs and code (use after major changes)
- **System Status**: View current system info

### 3. Search Examples

- **By Tag**: Find all files (docs or code) tagged with `MoE`, `pytorch`, etc.
- **By Keyword**: Search for any string in tags (e.g., `quantization`)
- **By File Type**: List all documentation or all source code files
- **By Category**: Filter by project area (e.g., `models`, `core`, `user`)

### 4. Cross-Referencing

- Results show both documentation and code files for any tag or keyword
- Use file details to see all tags and metadata for any file

### 5. Maintenance

- Use **Rebuild Indices** after adding, removing, or renaming files
- Indices are stored in `docs/unified_tags_index.yaml` and `docs/file_metadata.yaml`

## Best Practices

- Add meaningful tags to new documentation and code files
- Use consistent naming for categories and tags
- Rebuild indices regularly for best search results

## Troubleshooting

- If search results are missing, rebuild indices
- For errors, check that all dependencies (e.g., `rich`, `pyyaml`) are installed

---
**File**: `docs/user_guide/ids_tagging_unified_usage_guide.md`
