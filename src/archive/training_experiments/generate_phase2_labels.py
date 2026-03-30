#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/training/generate_phase2_labels.py #training
**Category:** Training System
**Status:** Active
"""









# Generate Phase2 Labels

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\training\\generate_phase2_labels.py #training
# Category:** Training System
# Status:** Active

"""
ImpressionCore Phase 2 Raw Data Label Generator
Automatically generates labels for raw data lacking a smart/correct label.

- Scans f:/datasets/raw/ for all files
- Checks/updates manifests in f:/b2_datasets/
- Generates placeholder or rule-based labels for missing/invalid entries
- Outputs updated manifest and summary log

Usage:
    python src/training/generate_phase2_labels.py
"""

import os
import json
from pathlib import Path
from datetime import datetime

RAW_DATA_DIR = Path('f:/datasets/raw/')
MANIFEST_DIR = Path('f:/b2_datasets/')
EMBEDDING_DIR = Path('f:/b2_embeddings/')

LABEL_FIELDS = ['sentiment', 'intent']
SENTIMENT_CLASSES = ['negative', 'neutral', 'positive']
INTENT_CLASSES = [f'intent_{i}' for i in range(10)]

MANIFEST_OUT = MANIFEST_DIR / f'phase2_manifest_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
LOG_PATH = MANIFEST_DIR / f'phase2_labelgen_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

def load_existing_manifest():
    manifests = []
    print(f"[DEBUG] Scanning manifest dir: {MANIFEST_DIR}")
    for file in MANIFEST_DIR.glob('*.json'):
        print(f"[DEBUG] Found manifest file: {file}")
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    manifests.extend(data)
        except Exception as e:
            print(f"[DEBUG] Error reading {file}: {e}")
            continue
    print(f"[DEBUG] Loaded {len(manifests)} manifest entries.")
    return {entry['id']: entry for entry in manifests if 'id' in entry}

                needs_update = True
    print(f"[DEBUG] RAW_DATA_DIR: {RAW_DATA_DIR}")
    print(f"[DEBUG] MANIFEST_DIR: {MANIFEST_DIR}")
    print(f"[DEBUG] EMBEDDING_DIR: {EMBEDDING_DIR}")
    print(f"[DEBUG] Checking if directories exist...")
    print(f"[DEBUG] RAW_DATA_DIR exists: {RAW_DATA_DIR.exists()}")
    print(f"[DEBUG] MANIFEST_DIR exists: {MANIFEST_DIR.exists()}")
    print(f"[DEBUG] EMBEDDING_DIR exists: {EMBEDDING_DIR.exists()}")
    log_lines = []
    existing = load_existing_manifest()
    updated_manifest = []
    seen_ids = set()
    sample_files = list(RAW_DATA_DIR.glob('*'))
    print(f"[DEBUG] Found {len(sample_files)} files in RAW_DATA_DIR.")
    for sample_path in sample_files:
        if not sample_path.is_file():
            print(f"[DEBUG] Skipping non-file: {sample_path}")
            continue
        sample_id = sample_path.stem
        entry = existing.get(sample_id, {'id': sample_id, 'path': str(sample_path)})
        needs_update = False
        for field in LABEL_FIELDS:
            if field not in entry or entry[field] not in (SENTIMENT_CLASSES if field=='sentiment' else INTENT_CLASSES):
                label = generate_label_for_sample(sample_path)[field]
                entry[field] = label
                needs_update = True
        if needs_update:
            log_lines.append(f"[AUTO-LABEL] {sample_id}: {entry}")
            print(f"[DEBUG] Auto-labeled {sample_id}: {entry}")
        updated_manifest.append(entry)
        seen_ids.add(sample_id)
    # Add any existing entries not in raw dir
    for sample_id, entry in existing.items():
        if sample_id not in seen_ids:
            updated_manifest.append(entry)
    # Write manifest
    print(f"[DEBUG] Writing manifest to {MANIFEST_OUT}")
    with open(MANIFEST_OUT, 'w', encoding='utf-8') as f:
        json.dump(updated_manifest, f, indent=2)
    # Write log
    print(f"[DEBUG] Writing log to {LOG_PATH}")
    with open(LOG_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines))
    print(f"Phase 2 manifest written to: {MANIFEST_OUT}")
    print(f"Label generation log written to: {LOG_PATH}")
        if needs_update:
            log_lines.append(f"[AUTO-LABEL] {sample_id}: {entry}")
        updated_manifest.append(entry)
        seen_ids.add(sample_id)
    # Add any existing entries not in raw dir
    for sample_id, entry in existing.items():
        if sample_id not in seen_ids:
            updated_manifest.append(entry)
    # Write manifest
    with open(MANIFEST_OUT, 'w', encoding='utf-8') as f:
        json.dump(updated_manifest, f, indent=2)
    # Write log
    with open(LOG_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines))
    print(f"Phase 2 manifest written to: {MANIFEST_OUT}")
    print(f"Label generation log written to: {LOG_PATH}")

if __name__ == '__main__':
    main()
