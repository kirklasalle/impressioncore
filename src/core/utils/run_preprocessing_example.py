#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/core/utils/run_preprocessing_example.py #training
**Category:** Core Implementation
**Status:** Active
"""









# Run Preprocessing Example

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\core\\utils\\run_preprocessing_example.py #training
# Category:** Core Implementation
# Status:** Active

"""
Example script to preprocess audio transcript files for ImpressionCore-B1 conversational training.
- Loads transcript files
- Cleans and standardizes turns
- Chunks for model context
- Saves processed output
"""
import os
from pathlib import Path

from .core.utils.preprocess_transcripts import chunk_conversation, normalize_text, preprocess_transcript

INPUT_DIR = Path("F:/impressioncore-b1-embeddings-062125/")  # Adjust as needed
OUTPUT_DIR = Path("F:/impressioncore-b1-processed-transcripts/")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TRANSCRIPT_EXTS = [".txt", ".transcript", ".log"]

def is_transcript_file(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in TRANSCRIPT_EXTS)

def process_all_transcripts():
    for root, _, files in os.walk(INPUT_DIR):
        for fname in files:
            if is_transcript_file(fname):
                in_path = Path(root) / fname
                with open(in_path, encoding="utf-8", errors="ignore") as f:
                    raw = f.read()
                turns = preprocess_transcript(raw)
                turns = [normalize_text(t) for t in turns]
                chunks = chunk_conversation(turns, max_length=512)
                # Save each chunk as a separate file
                for i, chunk in enumerate(chunks):
                    out_path = OUTPUT_DIR / f"{in_path.stem}_chunk{i+1}.txt"
                    with open(out_path, "w", encoding="utf-8") as out_f:
                        out_f.write("\n".join(chunk))
                print(f"Processed {in_path} -> {len(chunks)} chunks.")

if __name__ == "__main__":
    process_all_transcripts()
