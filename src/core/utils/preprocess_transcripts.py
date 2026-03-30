#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/core/utils/preprocess_transcripts.py #training
**Category:** Core Implementation
**Status:** Active
"""









# Preprocess Transcripts

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\core\\utils\\preprocess_transcripts.py #training
# Category:** Core Implementation
# Status:** Active

"""
Preprocessing utilities for audio transcript text data for ImpressionCore-B1 conversational training.
- Removes timestamps, speaker labels, and noise markers
- Standardizes conversational turns
- Normalizes text
- Splits long transcripts into manageable segments
"""
import re


def clean_transcript_line(line: str) -> str:
    """
    Cleans a single line of transcript by removing timestamps, speaker labels, and noise markers.
    Args:
        line: Raw transcript line.
    Returns:
        Cleaned line with only dialogue text.
    """
    # Remove timestamps [00:00:00] or (00:00:00)
    line = re.sub(r"[\[(]?\d{1,2}:\d{2}:\d{2}[)\]]?", "", line)
    # Remove speaker labels (e.g., 'Speaker 1:', 'User:', 'Assistant:')
    line = re.sub(r"^[A-Za-z0-9_\- ]{1,30}:\s*", "", line)
    # Remove noise markers (e.g., [laughter], [inaudible])
    line = re.sub(r"\[[^\]]+\]", "", line)
    # Remove extra whitespace
    line = line.strip()
    return line

def preprocess_transcript(transcript: str, user_token: str = "<USER>", assistant_token: str = "<ASSISTANT>") -> list[str]:
    """
    Processes a full transcript into standardized conversational turns.
    Args:
        transcript: Raw transcript text.
        user_token: Token to mark user turns.
        assistant_token: Token to mark assistant turns.
    Returns:
        List of cleaned, tokenized conversation turns.
    """
    lines = transcript.splitlines()
    turns = []
    for line in lines:
        clean = clean_transcript_line(line)
        if not clean:
            continue
        # Heuristic: assign tokens based on speaker label if present
        if line.lower().startswith(("user:", "speaker 1:")):
            turns.append(f"{user_token} {clean}")
        elif line.lower().startswith(("assistant:", "speaker 2:")):
            turns.append(f"{assistant_token} {clean}")
        else:
            turns.append(clean)
    return turns

def chunk_conversation(turns: list[str], max_length: int = 512) -> list[list[str]]:
    """
    Splits conversation turns into chunks that fit within a model's context window.
    Args:
        turns: List of conversation turns.
        max_length: Maximum number of tokens/words per chunk.
    Returns:
        List of conversation chunks (each a list of turns).
    """
    chunks = []
    current = []
    current_len = 0
    for turn in turns:
        turn_len = len(turn.split())
        if current_len + turn_len > max_length and current:
            chunks.append(current)
            current = []
            current_len = 0
        current.append(turn)
        current_len += turn_len
    if current:
        chunks.append(current)
    return chunks

def normalize_text(text: str) -> str:
    """
    Normalizes text for conversational training (lowercase, punctuation, contractions).
    Args:
        text: Input text.
    Returns:
        Normalized text.
    """
    text = text.lower()
    # Optionally, expand contractions or fix punctuation here
    text = re.sub(r"\s+", " ", text)
    return text.strip()
