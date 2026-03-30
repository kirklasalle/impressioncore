#!/usr/bin/env python3
"""
Quick Training Data Size Calculator
Estimates storage requirements for various AI model training scenarios

Usage: python training_data_calculator.py [model_type] [dataset_size_gb]
"""

import argparse
import sys
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class TrainingEstimate:
    """Training data size estimate"""
    model_type: str
    dataset_size_gb: float
    processed_multiplier: float
    checkpoint_size_gb: float
    temp_cache_gb: float
    total_estimated_gb: float

def calculate_training_requirements(model_type: str, dataset_size_gb: float) -> TrainingEstimate:
    """Calculate training storage requirements based on model type and dataset size"""
    
    # Processing multipliers (how much processed data vs raw data)
    processing_multipliers = {
        "small_llm": 0.5,           # 50% of raw data size
        "medium_llm": 0.6,          # 60% of raw data size  
        "large_llm": 0.7,           # 70% of raw data size
        "multimodal": 0.8,          # 80% of raw data size (tokenization + vision preprocessing)
        "specialized": 0.4,         # 40% of raw data size (domain-specific, less preprocessing)
    }
    
    # Checkpoint sizes (approximate model size during training)
    checkpoint_sizes = {
        "small_llm": 8.0,           # 1-3B parameters
        "medium_llm": 30.0,         # 7-13B parameters
        "large_llm": 80.0,          # 30-70B parameters
        "multimodal": 45.0,         # Multimodal model with vision
        "specialized": 15.0,        # Domain-specific model
    }
    
    # Temporary cache requirements
    temp_cache_requirements = {
        "small_llm": 10.0,
        "medium_llm": 25.0,
        "large_llm": 50.0,
        "multimodal": 35.0,
        "specialized": 15.0,
    }
    
    # Calculate components
    processed_size = dataset_size_gb * processing_multipliers.get(model_type, 0.6)
    checkpoint_size = checkpoint_sizes.get(model_type, 30.0)
    temp_cache = temp_cache_requirements.get(model_type, 25.0)
    
    # Total: raw data + processed data + checkpoints + temp cache + 20% buffer
    total = (dataset_size_gb + processed_size + checkpoint_size + temp_cache) * 1.2
    
    return TrainingEstimate(
        model_type=model_type,
        dataset_size_gb=dataset_size_gb,
        processed_multiplier=processing_multipliers.get(model_type, 0.6),
        checkpoint_size_gb=checkpoint_size,
        temp_cache_gb=temp_cache,
        total_estimated_gb=total
    )

def print_estimate(estimate: TrainingEstimate):
    """Print formatted training estimate"""
    print(f"\n🤖 Training Storage Estimate - {estimate.model_type.upper()}")
    print("=" * 50)
    print(f"Raw Dataset Size:        {estimate.dataset_size_gb:>8.1f} GB")
    print(f"Processed Data:          {estimate.dataset_size_gb * estimate.processed_multiplier:>8.1f} GB")
    print(f"Model Checkpoints:       {estimate.checkpoint_size_gb:>8.1f} GB")
    print(f"Temporary Cache:         {estimate.temp_cache_gb:>8.1f} GB")
    print("-" * 50)
    print(f"TOTAL ESTIMATED:         {estimate.total_estimated_gb:>8.1f} GB")
    print(f"(includes 20% safety buffer)")
    
    # Check if it fits on ImpressionCore drive
    available_space = 476.8  # GB
    if estimate.total_estimated_gb <= available_space:
        remaining = available_space - estimate.total_estimated_gb
        print(f"\n✅ FITS on ImpressionCore drive!")
        print(f"   Remaining space: {remaining:.1f} GB")
        
        # How many more projects could fit
        additional_projects = int(remaining / estimate.total_estimated_gb)
        if additional_projects > 0:
            print(f"   Could fit {additional_projects} more similar projects")
    else:
        overflow = estimate.total_estimated_gb - available_space
        print(f"\n❌ EXCEEDS ImpressionCore drive capacity!")
        print(f"   Overflow: {overflow:.1f} GB")
        print(f"   Consider: Reduce dataset size or use external storage")

def main():
    """Main function with CLI interface"""
    parser = argparse.ArgumentParser(description="Calculate training storage requirements")
    parser.add_argument("model_type", nargs="?", default="multimodal",
                       choices=["small_llm", "medium_llm", "large_llm", "multimodal", "specialized"],
                       help="Type of model to train")
    parser.add_argument("dataset_size", nargs="?", type=float, default=50.0,
                       help="Dataset size in GB")
    
    args = parser.parse_args()
    
    # Interactive mode if no arguments
    if len(sys.argv) == 1:
        print("🚀 ImpressionCore Training Storage Calculator")
        print("=" * 50)
        print("Available model types:")
        print("1. small_llm    - 1-3B parameters")
        print("2. medium_llm   - 7-13B parameters") 
        print("3. large_llm    - 30-70B parameters")
        print("4. multimodal   - Text + Vision model")
        print("5. specialized  - Domain-specific model")
        
        model_choice = input("\nSelect model type (1-5): ").strip()
        model_map = {"1": "small_llm", "2": "medium_llm", "3": "large_llm", 
                    "4": "multimodal", "5": "specialized"}
        model_type = model_map.get(model_choice, "multimodal")
        
        dataset_size = float(input("Enter dataset size in GB: ") or "50.0")
    else:
        model_type = args.model_type
        dataset_size = args.dataset_size
    
    # Calculate and display estimate
    estimate = calculate_training_requirements(model_type, dataset_size)
    print_estimate(estimate)
    
    # Show some example scenarios
    print(f"\n📊 Example Scenarios for {model_type}:")
    print("-" * 30)
    test_sizes = [10, 25, 50, 100, 200]
    for size in test_sizes:
        test_estimate = calculate_training_requirements(model_type, size)
        status = "✅" if test_estimate.total_estimated_gb <= 476.8 else "❌"
        print(f"{size:>3}GB dataset → {test_estimate.total_estimated_gb:>6.1f}GB total {status}")

if __name__ == "__main__":
    main()
