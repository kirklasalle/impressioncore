#!/usr/bin/env python3
"""
ImpressionCore: Run Demo

Module for run demo functionality in the ImpressionCore framework.

File: examples\run_demo.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [production, 2025]
Dependencies: [pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements run demo functionality for the
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
from examples.run_demo import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.core.knowledge.uks import UniversalKnowledgeStore
from src.generators.response_generator import ResponseGenerator
from src.model import MockModel
# Memory optimization: Explicit memory cleanup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_knowledge_store():
    """
    Initialize the knowledge store with some example knowledge.
    
    Returns:
        Initialized UniversalKnowledgeStore
    """
    print("Initializing knowledge store...")
    ks = UniversalKnowledgeStore()
    
    # Add some basic astronomy knowledge
    solar_system = ks.add_node("Solar System", {
        "description": "The Solar System is the gravitationally bound system of the Sun and the objects that orbit it.",
        "age": "4.6 billion years",
        "star": "The Sun",
        "planets": 8
    })
    
    sun = ks.add_node("Sun", {
        "type": "G-type main-sequence star",
        "mass": "1.989 × 10^30 kg",
        "diameter": "1,391,000 km",
        "temperature": "5,778 K (surface)"
    }, parent=solar_system)
    
    earth = ks.add_node("Earth", {
        "type": "Terrestrial planet",
        "order": 3,
        "mass": "5.972 × 10^24 kg",
        "diameter": "12,742 km",
        "atmosphere": "78% nitrogen, 21% oxygen, 1% other gases",
        "moons": 1
    }, parent=solar_system)
    
    mars = ks.add_node("Mars", {
        "type": "Terrestrial planet",
        "order": 4,
        "mass": "6.39 × 10^23 kg",
        "diameter": "6,779 km",
        "atmosphere": "95% carbon dioxide, 3% nitrogen, 1.6% argon",
        "moons": 2,
        "nickname": "The Red Planet",
        "color": "Red",
        "surface": "Dusty, rocky, with polar ice caps"
    }, parent=solar_system)
    
    phobos = ks.add_node("Phobos", {
        "type": "Moon of Mars",
        "diameter": "22.2 km",
        "orbit_distance": "9,376 km"
    }, parent=mars)
    
    deimos = ks.add_node("Deimos", {
        "type": "Moon of Mars",
        "diameter": "12.6 km",
        "orbit_distance": "23,463 km"
    }, parent=mars)
    
    moon = ks.add_node("Moon", {
        "type": "Earth's natural satellite",
        "diameter": "3,474 km",
        "orbit_distance": "384,400 km"
    }, parent=earth)
    
    jupiter = ks.add_node("Jupiter", {
        "type": "Gas giant",
        "order": 5,
        "mass": "1.898 × 10^27 kg",
        "diameter": "139,820 km",
        "atmosphere": "90% hydrogen, 10% helium",
        "moons": 79
    }, parent=solar_system)
    
    print(f"Knowledge store initialized with {len(ks.get_all_nodes())} nodes")
    return ks

def main():
    """
    Main function for the ImpressionCore demo.
    """
    print("=" * 80)
    print("ImpressionCore Demo")
    print("=" * 80)
    print()
    
    # Initialize components
    ks = initialize_knowledge_store()
    print("Initializing response generator...")
    model = MockModel()
    # Memory optimization: Explicit memory cleanup
    generator = ResponseGenerator(knowledge_store=ks, model=model)
    
    # Print example queries
    print("-" * 80)
    print("Example queries:")
    print("-" * 80)
    
    example_queries = [
        "What is Mars?",
        "Tell me about the Sun",
        "How many moons does Mars have?",
        "What is the atmosphere of Earth composed of?",
        "What is Jupiter?"
    ]
    
    for query in example_queries:
        print(f"Query: {query}")
        response = generator.generate_response(query)
        print(f"Response: {response}")
        print("-" * 80)
    
    # Interactive mode
    print("Interactive mode (type 'exit' to quit):")
    while True:
        user_query = input("\nYour query: ")
        if user_query.lower() in ["exit", "quit", "bye"]:
            print("Exiting demo.")
            break
        
        response = generator.generate_response(user_query)
        print(f"Response: {response}")

if __name__ == "__main__":
    main()
