#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #memory_management #python #source_code #src/core/utils/scan_f_drive_for_labels.py
**Category:** Core Implementation
**Status:** Active
"""









# Scan F Drive For Labels

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #memory_management #python #source_code #src\\core\\utils\\scan_f_drive_for_labels.py
# Category:** Core Implementation
# Status:** Active

"""
scan_f_drive_for_labels.py
Efficiently scans the F: drive for embedding files and attempts to map them to sentiment/intent labels.
Outputs a CSV mapping: embedding_path,sentiment_label,intent_label

- Recursively scans F:/ for .npy embedding files
- Attempts to find labels by:
    * Matching sidecar files (same name, .csv/.json/.txt)
    * Checking for label info in parent directory or filename
    * If no label found, marks as 'unlabeled'
- Writes results incrementally to avoid memory issues
- Summarizes results at the end

Usage: python scan_f_drive_for_labels.py
"""
import csv
import json
import os
import re
from pathlib import Path

F_ROOT = Path('F:/')
OUTPUT_CSV = Path('F:/embedding_label_mapping.csv')
EMBEDDING_EXT = '.npy'
LABEL_EXTS = ['.csv', '.json', '.txt']

# Heuristic: look for label in filename or parent dir (e.g., .../positive/..., ..._intent3.npy)
SENTIMENT_KEYWORDS = ['positive', 'neutral', 'negative']
INTENT_PATTERN = re.compile(r'intent(\d+)')


def find_label_for_embedding(embedding_path):
    """Try to find sentiment/intent label for an embedding file."""
    parent = embedding_path.parent
    fname = embedding_path.stem.lower()
    sentiment = 'unlabeled'
    intent = 'unlabeled'

    # 1. Check parent directory for sentiment
    for kw in SENTIMENT_KEYWORDS:
        if kw in parent.parts:
            sentiment = kw
            break
    # 2. Check filename for sentiment
    if sentiment == 'unlabeled':
        for kw in SENTIMENT_KEYWORDS:
            if kw in fname:
                sentiment = kw
                break
    # 3. Check filename for intent
    m = INTENT_PATTERN.search(fname)
    if m:
        intent = m.group(1)
    # 4. Check for sidecar label files
    for ext in LABEL_EXTS:
        sidecar = embedding_path.with_suffix(ext)
        if sidecar.exists():
            try:
                if ext == '.csv':
                    with open(sidecar, encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if 'sentiment' in row:
                                sentiment = row['sentiment']
                            if 'intent' in row:
                                intent = row['intent']
                            break
                elif ext == '.json':
                    with open(sidecar, encoding='utf-8') as f:
                        data = json.load(f)
                        sentiment = data.get('sentiment', sentiment)
                        intent = data.get('intent', intent)
                elif ext == '.txt':
                    with open(sidecar, encoding='utf-8') as f:
                        for line in f:
                            if 'sentiment' in line:
                                sentiment = line.split(':')[-1].strip()
                            if 'intent' in line:
                                intent = line.split(':')[-1].strip()
            except Exception:
                pass
    return sentiment, intent

def main():
    print(f"Scanning {F_ROOT} for embedding files...")
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as out_f:
        writer = csv.writer(out_f)
        writer.writerow(['embedding_path', 'sentiment_label', 'intent_label'])
        count = 0
        labeled = 0
        for root, _dirs, files in os.walk(F_ROOT):
            for fname in files:
                if fname.endswith(EMBEDDING_EXT):
                    fpath = Path(root) / fname
                    sentiment, intent = find_label_for_embedding(fpath)
                    writer.writerow([str(fpath), sentiment, intent])
                    count += 1
                    if sentiment != 'unlabeled' or intent != 'unlabeled':
                        labeled += 1
                    if count % 1000 == 0:
                        print(f"Processed {count} files...")
        print(f"Scan complete. {count} embeddings found. {labeled} labeled. Output: {OUTPUT_CSV}")

if __name__ == '__main__':
    main()
