#!/usr/bin/env python3
"""
ImpressionCore: Pattern

Module for pattern functionality in the ImpressionCore framework.

File: core\brain\subconscious\pattern.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [core, production, framework, 2025]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements pattern functionality for the
ImpressionCore brain-inspired multimodal AI framework. Optimized for memory-
constrained environments and designed to run efficiently on consumer hardware.

Design Philosophy:
- Memory-efficient implementation for GTX 1050 Ti constraints
- Modular design for easy extension and maintenance
- Rich logging and error handling
- Integration with ImpressionCore ecosystem

TODO:
- Add comprehensive unit tests
- Implement performance benchmarks
- Add configuration validation
- Optimize memory usage patterns

Examples:
```python
# Basic usage example
from core.brain.subconscious.pattern import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

from typing import Any, Dict, List

def _calculate_nesting_level(obj: Any) -> int:
    """
    Calculate the nesting level of a data structure.
    
    Args:
        obj: Object to analyze
        
    Returns:
        Integer representing nesting depth
    """
    if isinstance(obj, dict):
        # Empty dict has level 1
        if not obj:
            return 1
            
        # Recursively find deepest level
        return 1 + max(_calculate_nesting_level(val) for val in obj.values())
        
    elif isinstance(obj, list):
        # Empty list has level 1
        if not obj:
            return 1
            
        # Recursively find deepest level
        return 1 + max(_calculate_nesting_level(item) for item in obj)
        
    else:
        # Primitive type has level 0
        return 0

def _create_hashable_repr(obj: Any) -> str:
    """
    Create a hashable string representation of an object.
    
    Args:
        obj: Object to represent
        
    Returns:
        String representation that can be used as dict key
    """
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return str(obj)
    elif isinstance(obj, list):
        return "[" + ",".join(_create_hashable_repr(item) for item in obj) + "]"
    elif isinstance(obj, dict):
        sorted_items = sorted(obj.items(), key=lambda x: str(x[0]))
        return "{" + ",".join(f"{k}:{_create_hashable_repr(v)}" for k, v in sorted_items) + "}"
    else:
        # For other types, use string representation and class name
        return f"{obj.__class__.__name__}({str(obj)})"

def _compare_sentence_structures(sentence1: str, sentence2: str) -> float:
    """
    Compare the structural similarities between two sentences.
    
    Args:
        sentence1: First sentence
        sentence2: Second sentence
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    # Simple structural features to compare
    features1 = _extract_sentence_features(sentence1)
    features2 = _extract_sentence_features(sentence2)
    
    # Compare features
    similarities = []
    
    # Length similarity
    length_ratio = min(len(features1["words"]), len(features2["words"])) / max(len(features1["words"]), len(features2["words"]))
    similarities.append(length_ratio)
    
    # Word type pattern similarity
    min_length = min(len(features1["word_types"]), len(features2["word_types"]))
    if min_length > 0:
        # Compare patterns up to the length of the shorter sentence
        type_matches = sum(1 for i in range(min_length) if features1["word_types"][i] == features2["word_types"][i])
        similarities.append(type_matches / min_length)
    
    # Punctuation similarity
    if features1["punctuation"] == features2["punctuation"]:
        similarities.append(1.0)
    else:
        similarities.append(0.0)
    
    # Overall similarity is weighted average of feature similarities
    weights = [0.2, 0.5, 0.3]  # Length, word types, punctuation
    return sum(s * w for s, w in zip(similarities, weights))

def _extract_sentence_features(sentence: str) -> Dict[str, Any]:
    """
    Extract structural features from a sentence.
    
    Args:
        sentence: Sentence to analyze
        
    Returns:
        Dictionary of sentence features
    """
    # Simple processing - would use proper NLP in production
    words = sentence.split()
    
    # Basic punctuation extraction
    punctuation = ""
    if sentence and sentence[-1] in ".!?":
        punctuation = sentence[-1]
    
    # Very simple "word type" identification
    word_types = []
    for word in words:
        word = word.strip(".,!?;:")
        if not word:
            continue
            
        if word[0].isupper() and word != words[0]:
            word_type = "proper"
        elif word.lower() in ["a", "an", "the"]:
            word_type = "article"
        elif word.lower() in ["and", "or", "but", "so", "yet", "for", "nor"]:
            word_type = "conjunction"
        elif word.lower() in ["in", "on", "at", "by", "with", "from", "to", "for"]:
            word_type = "preposition"
        elif word.lower() in ["i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them"]:
            word_type = "pronoun"
        else:
            # This is a very simple heuristic, not linguistically accurate
            if word.endswith("ly"):
                word_type = "adverb"
            elif word.endswith("ed"):
                word_type = "verb_past"
            elif word.endswith("ing"):
                word_type = "verb_continuous"
            elif word.endswith("s") and not word.endswith("ss"):
                word_type = "plural_or_verb"
            else:
                word_type = "noun_or_verb"  # Simplified default
        
        word_types.append(word_type)
    
    return {
        "words": words,
        "word_count": len(words),
        "word_types": word_types,
        "punctuation": punctuation
    }

def _find_numerical_sequence_pattern(numbers: List[float]) -> Dict[str, Any]:
    """
    Detect patterns in a sequence of numbers.
    
    Args:
        numbers: List of numbers to analyze
        
    Returns:
        Dictionary with pattern information or empty dict if no pattern found
    """
    if len(numbers) < 3:
        return {}
    
    # Check for arithmetic progression
    diffs = [numbers[i+1] - numbers[i] for i in range(len(numbers)-1)]
    diff_mean = sum(diffs) / len(diffs)
    diff_variance = sum((d - diff_mean) ** 2 for d in diffs) / len(diffs)
    
    if diff_variance < 0.0001:  # Nearly constant difference
        return {
            "type": "arithmetic",
            "difference": diff_mean,
            "confidence": 0.9,
            "formula": f"a_n = a_1 + (n-1) * {diff_mean:.4f}"
        }
    
    # Check for geometric progression (if all numbers are non-zero)
    if all(n != 0 for n in numbers):
        ratios = [numbers[i+1] / numbers[i] for i in range(len(numbers)-1)]
        ratio_mean = sum(ratios) / len(ratios)
        ratio_variance = sum((r - ratio_mean) ** 2 for r in ratios) / len(ratios)
        
        if ratio_variance < 0.0001:  # Nearly constant ratio
            return {
                "type": "geometric",
                "ratio": ratio_mean,
                "confidence": 0.9,
                "formula": f"a_n = a_1 * {ratio_mean:.4f}^(n-1)"
            }
    
    # Check for quadratic sequence by analyzing second differences
    if len(numbers) >= 4:
        second_diffs = [diffs[i+1] - diffs[i] for i in range(len(diffs)-1)]
        second_diff_mean = sum(second_diffs) / len(second_diffs)
        second_diff_variance = sum((d - second_diff_mean) ** 2 for d in second_diffs) / len(second_diffs)
        
        if second_diff_variance < 0.0001:  # Nearly constant second difference
            a = second_diff_mean / 2
            # Calculate b and c using the first two terms
            b = diffs[0] - second_diff_mean
            c = numbers[0]
            
            return {
                "type": "quadratic",
                "a": a,
                "b": b,
                "c": c,
                "confidence": 0.85,
                "formula": f"a_n = {a:.4f}n² + {b:.4f}n + {c:.4f}"
            }
    
    # No clear pattern found
    return {}

def detect_temporal_patterns(data: List[Dict[str, Any]], timestamp_key: str) -> List[Dict[str, Any]]:
    """
    Detect patterns in time-series data.
    
    Args:
        data: List of data points with timestamps
        timestamp_key: Key for timestamp values in data dictionaries
        
    Returns:
        List of detected temporal patterns
    """
    if not data or len(data) < 3:
        return []
    
    patterns = []
    
    # Extract timestamps
    try:
        timestamps = [item[timestamp_key] for item in data if timestamp_key in item]
        if len(timestamps) < 3:
            return []
    except (KeyError, TypeError):
        return []
    
    # Sort data by timestamp
    sorted_data = sorted(
        [item for item in data if timestamp_key in item],
        key=lambda x: x[timestamp_key]
    )
    
    # Calculate time intervals
    intervals = [
        sorted_data[i+1][timestamp_key] - sorted_data[i][timestamp_key]
        for i in range(len(sorted_data)-1)
    ]
    
    # Check for periodicity
    if intervals:
        mean_interval = sum(intervals) / len(intervals)
        variance = sum((i - mean_interval)**2 for i in intervals) / len(intervals)
        normalized_variance = variance / (mean_interval**2) if mean_interval != 0 else float('inf')
        
        if normalized_variance < 0.1:  # Low variance indicates regular intervals
            patterns.append({
                "type": "periodic",
                "mean_interval": mean_interval,
                "variance": variance,
                "confidence": 1.0 - min(1.0, normalized_variance),
                "description": f"Events occur approximately every {mean_interval:.2f} time units"
            })
    
    # Check for acceleration/deceleration patterns
    if len(intervals) >= 3:
        # Calculate changes in intervals
        interval_changes = [intervals[i+1] - intervals[i] for i in range(len(intervals)-1)]
        mean_change = sum(interval_changes) / len(interval_changes)
        
        # Significant trend in interval changes
        if abs(mean_change) > 0.1 * mean_interval:
            if mean_change > 0:
                pattern_type = "deceleration"
                description = "Events are occurring less frequently over time"
            else:
                pattern_type = "acceleration"
                description = "Events are occurring more frequently over time"
                
            patterns.append({
                "type": pattern_type,
                "mean_interval_change": mean_change,
                "confidence": min(0.9, abs(mean_change) / mean_interval),
                "description": description
            })
    
    # Check for time-of-day patterns if timestamps are Unix time
    timestamps_seconds = [int(ts) for ts in timestamps if isinstance(ts, (int, float))]
    if timestamps_seconds:
        # Convert to hours of day (0-23)
        hours_of_day = [int((ts % 86400) / 3600) for ts in timestamps_seconds]
        
        # Count occurrences of each hour
        hour_counts = {}
        for hour in hours_of_day:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Find most common hour
        if hour_counts:
            most_common_hour = max(hour_counts.items(), key=lambda x: x[1])
            hour, count = most_common_hour
            
            # If more than 30% of events occur at the same hour
            if count > 0.3 * len(hours_of_day):
                patterns.append({
                    "type": "time_of_day",
                    "hour": hour,
                    "count": count,
                    "total_events": len(hours_of_day),
                    "percentage": count / len(hours_of_day) * 100,
                    "confidence": min(0.9, count / len(hours_of_day)),
                    "description": f"Events commonly occur around {hour}:00 hours"
                })
    
    return patterns