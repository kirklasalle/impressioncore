"""KD Dataset Filtering Utilities (relocated)

Original location: `src/filters.py`.
Relocated on August 23, 2025 to `distillation/processing/filters.py` as part of
source tree consolidation. No functional changes.
"""
from __future__ import annotations

import re
import string
from collections import Counter
from collections.abc import Iterable

_WS_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Normalize text for comparison: strip, lowercase, collapse whitespace."""
    if text is None:
        return ""
    return _WS_RE.sub(" ", text.strip().lower())


def length_filter(text: str, *, min_chars: int = 1, max_chars: int | None = None) -> bool:
    """Return True if text length is within bounds."""
    n = len(text or "")
    if n < min_chars:
        return False
    return not (max_chars is not None and n > max_chars)


def toxicity_filter(_text: str) -> bool:
    """Placeholder non-toxicity filter. Always returns True for now.

    Replace with a tiny classifier or rule-set in Phase 4.
    """
    return True


def heuristic_score(text: str) -> float:
    """Compute a simple heuristic quality score.

    Features:
    - Reward moderate length (too short/too long penalized)
    - Penalize excessive punctuation ratio
    - Reward presence of letters/digits
    """
    if not text:
        return 0.0
    t = text.strip()
    n = len(t)
    # Length score: peak around 150–600 chars
    target_low, target_high = 150, 600
    if n < target_low:
        len_score = n / target_low
    elif n > target_high:
        len_score = max(0.0, 1.0 - (n - target_high) / max(1, target_high))
    else:
        len_score = 1.0

    punct = sum(ch in string.punctuation for ch in t)
    punct_ratio = punct / n
    punct_score = max(0.0, 1.0 - 2.5 * punct_ratio)

    alpha = sum(ch.isalpha() for ch in t)
    digit = sum(ch.isdigit() for ch in t)
    content_score = min(1.0, (alpha + 0.5 * digit) / max(1, n / 4))

    return 0.5 * len_score + 0.3 * punct_score + 0.2 * content_score


def pick_self_consistent_candidate(candidates: Iterable[str]) -> tuple[str | None, Counter]:
    """Pick the most self-consistent candidate by normalized majority vote.

    Returns (chosen_candidate, vote_counter). If tie, break by heuristic_score.
    """
    items: list[str] = [c for c in candidates if c]
    if not items:
        return None, Counter()
    norm_map = {c: normalize_text(c) for c in items}
    votes = Counter(norm_map.values())
    # Find the normalized winner(s)
    if not votes:
        return items[0], Counter()
    max_count = max(votes.values())
    winners = [norm for norm, cnt in votes.items() if cnt == max_count]

    def best_original_for(norm: str) -> str:
        originals = [orig for orig, nrm in norm_map.items() if nrm == norm]
        return max(originals, key=heuristic_score)

    if len(winners) == 1:
        return best_original_for(winners[0]), votes
    # Tie: evaluate heuristic on representatives and pick best
    best = max((best_original_for(w) for w in winners), key=heuristic_score)
    return best, votes

__all__ = [
    "heuristic_score",
    "length_filter",
    "normalize_text",
    "pick_self_consistent_candidate",
    "toxicity_filter",
]
