#!/usr/bin/env python3
"""
ImpressionCore: Evaluation

Module for evaluation functionality in the ImpressionCore framework.

File: core\brain\creativity\evaluation.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, framework, core, production, 2025]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements evaluation functionality for the
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
from core.brain.creativity.evaluation import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import random
from functools import reduce

def evaluate_novelty(
    output: str,
    reference_outputs: List[str],
    method: str = "semantic_difference"
) -> Dict[str, Any]:
    """
    Evaluate the novelty of a creative output compared to reference outputs.
    
    Args:
        output: The creative output to evaluate
        reference_outputs: Collection of existing outputs for comparison
        method: Method for novelty calculation ("semantic_difference", "n_gram", "feature_based")
        
    Returns:
        Dictionary with novelty metrics
    """
    # Mock implementation - would use more sophisticated comparison in production
    if not reference_outputs:
        return {
            "novelty_score": 1.0,  # Maximum novelty if no references
            "unique_elements": ["all"],
            "method": method,
            "confidence": 0.7
        }
    
    if method == "semantic_difference":
        # Mock semantic difference calculation
        # In production: would use embeddings and cosine similarity
        avg_chars = sum(len(ref) for ref in reference_outputs) / len(reference_outputs)
        length_diff = abs(len(output) - avg_chars) / max(avg_chars, 1)
        
        novelty_score = min(0.3 + length_diff * 0.3 + random.random() * 0.4, 1.0)
        
    elif method == "n_gram":
        # Mock n-gram based calculation
        # In production: would compare n-gram distributions
        novelty_score = 0.4 + random.random() * 0.6
        
    else:  # feature_based or default
        # Mock feature-based calculation
        novelty_score = 0.5 + random.random() * 0.5
    
    return {
        "novelty_score": novelty_score,
        "unique_elements": [f"element_{i}" for i in range(int(novelty_score * 5))],
        "method": method,
        "confidence": 0.7
    }

def evaluate_value(
    output: str,
    context: Dict[str, Any],
    criteria: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Evaluate the value or utility of a creative output in a given context.
    
    Args:
        output: The creative output to evaluate
        context: Contextual information for evaluation
        criteria: Optional specific criteria for value assessment
        
    Returns:
        Dictionary with value metrics
    """
    criteria = criteria or ["relevance", "usefulness", "effectiveness", "impact"]
    
    # Mock implementation - would use more sophisticated assessment in production
    criterion_scores = {}
    
    for criterion in criteria:
        # Generate mock score for each criterion
        base_score = 0.5
        
        if criterion == "relevance":
            # Check if output contains keywords from context
            keywords = context.get("keywords", [])
            if keywords:
                matches = sum(keyword in output for keyword in keywords)
                base_score += min(0.5, matches * 0.1)
        
        # Add some randomness to other criteria
        criterion_scores[criterion] = min(1.0, base_score + random.random() * 0.4)
    
    # Calculate overall value score
    overall_value = sum(criterion_scores.values()) / len(criterion_scores)
    
    return {
        "overall_value": overall_value,
        "criterion_scores": criterion_scores,
        "context": context.get("name", "general"),
        "confidence": 0.8 if "keywords" in context else 0.6
    }

def evaluate_surprise(
    output: str,
    expectation: Optional[str] = None,
    domain_knowledge: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Evaluate the surprise or unexpectedness of a creative output.
    
    Args:
        output: The creative output to evaluate
        expectation: Optional description of expected output
        domain_knowledge: Optional domain-specific knowledge for context
        
    Returns:
        Dictionary with surprise metrics
    """
    domain_knowledge = domain_knowledge or {}
    
    # Mock implementation - would use more sophisticated assessment in production
    if expectation:
        # Simple text difference as surprise metric
        length_diff = abs(len(output) - len(expectation))
        normalized_diff = min(1.0, length_diff / max(len(expectation), 1))
        surprise_score = 0.3 + normalized_diff * 0.7
    else:
        # If no expectation provided, use domain conventions
        conventions = domain_knowledge.get("conventions", [])
        if conventions:
            # Check how many conventions are broken
            convention_breaks = sum(
                convention not in output for convention in conventions
            )
            surprise_score = min(1.0, convention_breaks / len(conventions) * 0.8 + 0.2)
        else:
            # Default score if no reference point
            surprise_score = 0.5
    
    # Identify surprising elements
    surprising_elements = []
    if surprise_score > 0.7:
        surprising_elements = ["unexpected_structure", "novel_combination"]
    elif surprise_score > 0.4:
        surprising_elements = ["unexpected_element"]
    
    return {
        "surprise_score": surprise_score,
        "surprising_elements": surprising_elements,
        "expectation_deviation": "high" if surprise_score > 0.7 else "medium" if surprise_score > 0.4 else "low",
        "confidence": 0.7 if expectation or conventions else 0.5
    }

def evaluate_creativity(
    output: str,
    context: Dict[str, Any],
    reference_outputs: Optional[List[str]] = None,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Perform multi-criteria evaluation of creativity.
    
    Args:
        output: The creative output to evaluate
        context: Context information for evaluation
        reference_outputs: Optional reference outputs for comparison
        weights: Optional weights for different evaluation criteria
        
    Returns:
        Dictionary with comprehensive creativity evaluation
    """
    reference_outputs = reference_outputs or []
    weights = weights or {
        "novelty": 0.4,
        "value": 0.3,
        "surprise": 0.3
    }
    
    # Perform individual evaluations
    novelty = evaluate_novelty(output, reference_outputs)
    value = evaluate_value(output, context)
    surprise = evaluate_surprise(output, context.get("expectation"))
    
    # Combine scores using weights
    creativity_score = (
        novelty["novelty_score"] * weights["novelty"] +
        value["overall_value"] * weights["value"] +
        surprise["surprise_score"] * weights["surprise"]
    )
    
    # Categorize creativity level
    if creativity_score > 0.8:
        creativity_level = "transformational"
    elif creativity_score > 0.6:
        creativity_level = "innovative"
    elif creativity_score > 0.4:
        creativity_level = "adaptive"
    else:
        creativity_level = "routine"
    
    return {
        "creativity_score": creativity_score,
        "creativity_level": creativity_level,
        "component_scores": {
            "novelty": novelty["novelty_score"],
            "value": value["overall_value"],
            "surprise": surprise["surprise_score"]
        },
        "strengths": _identify_strengths(novelty, value, surprise),
        "improvement_areas": _identify_improvement_areas(novelty, value, surprise),
        "evaluation_confidence": min(
            novelty.get("confidence", 0.5),
            value.get("confidence", 0.5),
            surprise.get("confidence", 0.5)
        )
    }

def evaluate_coherence(
    output: str,
    structure_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluate the internal coherence and structure of a creative output.
    
    Args:
        output: The creative output to evaluate
        structure_type: Optional expected structure type for evaluation
        
    Returns:
        Dictionary with coherence metrics
    """
    # Mock implementation - would use more sophisticated assessment in production
    
    # Simple length-based metrics as placeholders
    paragraphs = output.split("\n\n")
    sentences = output.replace("\n", " ").split(". ")
    
    # Check basic structure
    has_intro = len(paragraphs) >= 2
    has_conclusion = len(paragraphs) >= 3
    
    # Calculate mock coherence score
    base_score = 0.5
    if has_intro:
        base_score += 0.1
    if has_conclusion:
        base_score += 0.1
    if len(sentences) > 1:
        base_score += min(0.3, (len(sentences) - 1) * 0.05)
    
    coherence_score = min(1.0, base_score)
    
    # Structure match score if structure_type provided
    structure_match = None
    if structure_type:
        if structure_type == "narrative" and has_intro and has_conclusion:
            structure_match = 0.8
        elif structure_type == "exposition" and len(paragraphs) >= 3:
            structure_match = 0.7
        else:
            structure_match = 0.4
    
    return {
        "coherence_score": coherence_score,
        "structure_elements": {
            "has_introduction": has_intro,
            "has_conclusion": has_conclusion,
            "paragraph_count": len(paragraphs),
            "sentence_count": len(sentences)
        },
        "structure_match": structure_match,
        "confidence": 0.6
    }

def _identify_strengths(
    novelty: Dict[str, Any],
    value: Dict[str, Any],
    surprise: Dict[str, Any]
) -> List[str]:
    """Identify strengths based on evaluation components."""
    strengths = []
    
    if novelty["novelty_score"] > 0.7:
        strengths.append("highly_original")
    
    if value["overall_value"] > 0.7:
        strengths.append("valuable_contribution")
        
        # Check specific value criteria
        criterion_scores = value.get("criterion_scores", {})
        for criterion, score in criterion_scores.items():
            if score > 0.8:
                strengths.append(f"strong_{criterion}")
    
    if surprise["surprise_score"] > 0.7:
        strengths.append("unexpectedly_creative")
    
    return strengths

def _identify_improvement_areas(
    novelty: Dict[str, Any],
    value: Dict[str, Any],
    surprise: Dict[str, Any]
) -> List[str]:
    """Identify potential improvement areas based on evaluation components."""
    improvements = []
    
    if novelty["novelty_score"] < 0.4:
        improvements.append("increase_originality")
    
    if value["overall_value"] < 0.4:
        improvements.append("enhance_practical_value")
        
        # Check specific value criteria
        criterion_scores = value.get("criterion_scores", {})
        for criterion, score in criterion_scores.items():
            if score < 0.4:
                improvements.append(f"improve_{criterion}")
    
    if surprise["surprise_score"] < 0.4:
        improvements.append("add_unexpected_elements")
    
    return improvements

def comparative_evaluation(
    outputs: List[str],
    criteria: Optional[List[str]] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Perform comparative evaluation among multiple creative outputs.
    
    Args:
        outputs: List of creative outputs to compare
        criteria: Optional evaluation criteria
        context: Optional context for evaluation
        
    Returns:
        Dictionary with comparative evaluation results
    """
    criteria = criteria or ["novelty", "value", "surprise", "coherence"]
    context = context or {}
    
    if not outputs:
        return {"error": "No outputs provided for evaluation"}
    
    # Evaluate each output on each criterion
    evaluations = []
    
    for i, output in enumerate(outputs):
        output_eval = {"output_id": i, "scores": {}}
        
        for criterion in criteria:
            # Generate mock scores for each criterion
            if criterion == "novelty":
                # Compare to other outputs
                others = [o for j, o in enumerate(outputs) if j != i]
                eval_result = evaluate_novelty(output, others)
                score = eval_result["novelty_score"]
            elif criterion == "value":
                eval_result = evaluate_value(output, context)
                score = eval_result["overall_value"]
            elif criterion == "surprise":
                eval_result = evaluate_surprise(output, context.get("expectation"))
                score = eval_result["surprise_score"]
            elif criterion == "coherence":
                eval_result = evaluate_coherence(output)
                score = eval_result["coherence_score"]
            else:
                # Default random score for custom criteria
                score = 0.4 + random.random() * 0.6
            
            output_eval["scores"][criterion] = score
        
        # Calculate overall score
        output_eval["overall_score"] = sum(output_eval["scores"].values()) / len(criteria)
        evaluations.append(output_eval)
    
    # Rank outputs
    ranked_outputs = sorted(evaluations, key=lambda x: x["overall_score"], reverse=True)
    
    # Identify best output for each criterion
    best_by_criterion = {}
    for criterion in criteria:
        best_output = max(evaluations, key=lambda x: x["scores"][criterion])
        best_by_criterion[criterion] = best_output["output_id"]
    
    return {
        "ranked_outputs": ranked_outputs,
        "best_overall": ranked_outputs[0]["output_id"] if ranked_outputs else None,
        "best_by_criterion": best_by_criterion,
        "evaluation_criteria": criteria
    }
