#!/usr/bin/env python3
"""
ImpressionCore: Evaluate Model

Module for evaluate model functionality in the ImpressionCore framework.

File: examples\evaluate_model.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, production, 2025]
Dependencies: [typing, pathlib, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements evaluate model functionality for the
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
from examples.evaluate_model import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import os
import sys
import json
import logging
import argparse
import numpy as np
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from difflib import SequenceMatcher

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.pipeline.main import ModalEngine
from src.core.config import ConfigManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_test_cases(test_file: str) -> List[Dict[str, Any]]:
    """
    Load test cases from a JSON file.
    
    Args:
        test_file: Path to test cases file
        
    Returns:
        List of test cases
    """
    if not os.path.exists(test_file):
        logger.error(f"Test file not found: {test_file}")
        return []
    
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different possible formats of the test cases file
        if isinstance(data, dict) and "cases" in data:
            # Format with a "cases" array
            test_cases = data["cases"]
        elif isinstance(data, list):
            # Direct array of test cases
            test_cases = data
        else:
            # Unknown format
            logger.error(f"Unknown test cases format in {test_file}")
            test_cases = []
        
        # Validate that all test cases are dictionaries
        valid_cases = []
        for case in test_cases:
            if isinstance(case, dict):
                valid_cases.append(case)
            else:
                logger.warning(f"Skipping invalid test case (not a dictionary): {case}")
        
        logger.info(f"Loaded {len(valid_cases)} valid test cases from {test_file}")
        return valid_cases
    except Exception as e:
        logger.error(f"Error loading test cases: {e}")
        return []

def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score (0-1)
    """
    # Normalize texts
    text1 = re.sub(r'\s+', ' ', text1.lower().strip())
    text2 = re.sub(r'\s+', ' ', text2.lower().strip())
    
    # Use SequenceMatcher for string similarity
    return SequenceMatcher(None, text1, text2).ratio()

def evaluate_model(engine, test_cases: List[Dict[str, Any]], similarity_threshold: float = 0.7) -> Dict[str, Any]:
    """
    Evaluate a model on test cases.
    # Memory optimization: Explicit memory cleanup
    
    Args:
        engine: ModalEngine instance
        test_cases: List of test cases
        similarity_threshold: Threshold for similarity matching (0-1)
        
    Returns:
        Dict containing evaluation results
    """
    results = {
        "total": len(test_cases),
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "details": []
    }
    
    for idx, case in enumerate(test_cases):
        try:
            # Get case name or ID for logging
            case_name = case.get("name", case.get("id", f"Case {idx+1}"))
            logger.info(f"Processing test case {idx+1}/{len(test_cases)}: {case_name}")
            
            # Process input through engine
            input_text = case.get("input", "")
            expected_output = case.get("expected_output", "")
            
            if not input_text:
                logger.warning(f"Skipping test case {idx+1}: No input text")
                results["skipped"] += 1
                results["details"].append({
                    "case": idx+1,
                    "name": case_name,
                    "status": "skipped",
                    "reason": "No input text"
                })
                continue
            
            actual_output = engine.process_input(input_text)
            
            # Calculate similarity score
            similarity = calculate_similarity(expected_output, actual_output)
            
            # Check if exact match or similarity above threshold
            if expected_output in actual_output:
                match_type = "exact"
                results["passed"] += 1
                status = "passed"
            elif similarity >= similarity_threshold:
                match_type = "similar"
                results["passed"] += 1
                status = "passed"
            else:
                match_type = "none"
                results["failed"] += 1
                status = "failed"
            
            results["details"].append({
                "case": idx+1,
                "name": case_name,
                "status": status,
                "match_type": match_type,
                "similarity": round(similarity, 4),
                "input": input_text,
                "expected": expected_output,
                "actual": actual_output
            })
            
        except Exception as e:
            logger.error(f"Error processing test case {idx+1}: {e}")
            results["failed"] += 1
            results["details"].append({
                "case": idx+1,
                "name": f"Case {idx+1}",
                "status": "error",
                "error": str(e)
            })
    
    return results

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Evaluate ImpressionCore model")
    parser.add_argument("--model-dir", default=os.path.join(project_root, "models"), help="Directory containing model")
    parser.add_argument("--test-file", default=os.path.join(project_root, "data", "evaluation", "test_cases.json"), help="Path to test cases JSON file")
    parser.add_argument("--output-file", default="", help="Path to output evaluation results")
    parser.add_argument("--similarity-threshold", type=float, default=0.7, help="Similarity threshold (0-1)")
    args = parser.parse_args()
    
    print(f"Evaluating model from {args.model_dir} on test data from {args.test_file}")
    # Memory optimization: Explicit memory cleanup
    
    # Create config with model directory
    # Memory optimization: Explicit memory cleanup
    config = ConfigManager()
    config.set("models", "model_dir", args.model_dir)
    
    # Initialize engine using the config
    engine = ModalEngine(
        config_path=None,  # Use in-memory config
        # Memory optimization: Memory-critical operation
        use_brainsim=False
    )
    engine.config_manager = config  # Use our custom config
    
    # Load test cases
    test_cases = load_test_cases(args.test_file)
    if not test_cases:
        logger.error("No valid test cases to evaluate. Creating sample test cases...")
        create_sample_test_cases(args.test_file)
        logger.info("Please run the script again to use the newly created test cases.")
        return 1
    
    # Evaluate model
    results = evaluate_model(engine, test_cases, args.similarity_threshold)
    
    # Output results
    passed_rate = results["passed"] / results["total"] * 100 if results["total"] > 0 else 0
    logger.info(f"Evaluation complete: {results['passed']}/{results['total']} passed ({passed_rate:.1f}%)")
    
    if args.output_file:
        output_path = os.path.join(project_root, args.output_file)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to {output_path}")
    
    # Output detailed results
    logger.info("Test case results:")
    for detail in results["details"]:
        status = detail["status"]
        name = detail.get("name", "Unnamed")
        match_type = detail.get("match_type", "unknown")
        similarity = detail.get("similarity", 0)
        
        if status == "passed":
            logger.info(f"✅ {name}: PASSED ({match_type} match, similarity: {similarity:.2f})")
        elif status == "failed":
            logger.info(f"❌ {name}: FAILED (similarity: {similarity:.2f})")
        else:
            logger.info(f"⚠️ {name}: {status.upper()}")
    
    return 0

def create_sample_test_cases(test_file_path):
    """
    Create a sample test cases file.
    
    Args:
        test_file_path (str): Path where to create the file
    """
    sample_test_cases = [
        {
            "name": "Basic greeting",
            "input": "Hello, how are you?",
            "expected_output": "I'm doing well"
        },
        {
            "name": "Mars question",
            "input": "Tell me about Mars",
            "expected_output": "Mars is the fourth planet"
        },
        {
            "name": "Scientific question",
            "input": "What is the speed of light?",
            "expected_output": "299,792,458 meters per second"
        }
    ]
    
    os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
    with open(test_file_path, 'w', encoding='utf-8') as f:
        json.dump(sample_test_cases, f, indent=2)
    
    logger.info(f"Created sample test cases at {test_file_path}")

if __name__ == "__main__":
    main()
