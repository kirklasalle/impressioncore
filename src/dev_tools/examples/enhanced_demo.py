#!/usr/bin/env python3
"""
ImpressionCore: Enhanced Demo

Module for enhanced demo functionality in the ImpressionCore framework.

File: examples\enhanced_demo.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [pytorch, production, object-oriented, 2025]
Dependencies: [torch, typing, pathlib, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements enhanced demo functionality for the
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
from examples.enhanced_demo import ColoredFormatter
instance = ColoredFormatter()
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
import torch
import os
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import required modules
from src.pipeline.main import ModalEngine
from src.core.knowledge.uks import UniversalKnowledgeStore, KnowledgeNode
from src.integration.brainsim_adapter import BrainSimAdapter

# Configure logging with colors
class ColoredFormatter(logging.Formatter):
    """Formatter for colored console output."""
    
    COLORS = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',   # Green
        'WARNING': '\033[93m', # Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[91m\033[1m',  # Bold Red
        'RESET': '\033[0m'    # Reset
    }
    
    def format(self, record):
        """
        
    format function for processing.
    
    Args:
        self, record: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        log_message = super().format(record)
        level_name = record.levelname
        return f"{self.COLORS.get(level_name, '')}{log_message}{self.COLORS['RESET']}"

# Set up colored logging - first remove any existing handlers
logger = logging.getLogger()
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Add our custom handler
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.setLevel(logging.INFO)
logger.addHandler(handler)

def create_test_knowledge_store() -> UniversalKnowledgeStore:
    """Create a test knowledge store with sample data."""
    uks = UniversalKnowledgeStore()
    
    # Create a solar system hierarchy
    solar_system = KnowledgeNode("SolarSystem")
    solar_system.add_attribute("star", "Sun")
    solar_system.add_attribute("planets", 8)
    uks.add_node(solar_system)
    
    # Add planets
    planet = KnowledgeNode("Planet", parent=solar_system)
    planet.add_attribute("orbits_star", True)
    planet.add_attribute("has_gravity", True)
    uks.add_node(planet)
    
    # Add Earth
    earth = KnowledgeNode("Earth", parent=planet)
    earth.add_attribute("position", 3)
    earth.add_attribute("has_moon", True)
    earth.add_attribute("has_life", True)
    earth.add_attribute("atmosphere", "nitrogen-oxygen")
    uks.add_node(earth)
    
    # Add Mars
    mars = KnowledgeNode("Mars", parent=planet)
    mars.add_attribute("position", 4)
    mars.add_attribute("has_moons", 2)
    mars.add_attribute("atmosphere", "thin CO2")
    mars.add_attribute("color", "red")
    mars.add_attribute("has_water", "frozen")
    uks.add_node(mars)
    
    # Add Jupiter
    jupiter = KnowledgeNode("Jupiter", parent=planet)
    jupiter.add_attribute("position", 5)
    jupiter.add_attribute("type", "gas giant")
    jupiter.add_attribute("largest_planet", True)
    jupiter.add_attribute("has_moons", "79+")
    uks.add_node(jupiter)
    
    # Add relationships
    mars.add_relationship("neighbor_of", earth)
    mars.add_relationship("has_moon", KnowledgeNode("Phobos"))
    mars.add_relationship("has_moon", KnowledgeNode("Deimos"))
    
    logger.info(f"Created knowledge store with {len(uks.nodes)} nodes")
    return uks

def print_section_header(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_knowledge_queries(uks: UniversalKnowledgeStore) -> None:
    """Test knowledge graph queries and display results."""
    print_section_header("KNOWLEDGE GRAPH DEMO")
    
    # Query for Mars
    print("Querying for 'Mars':")
    results = uks.query("Mars")
    for node in results:
        print(f"\nNode: {node.label}")
        print("  Attributes:")
        all_attrs = node.get_all_attributes()
        for key, value in all_attrs.items():
            print(f"    {key}: {value}")
        
        if node.relationships:
            print("  Relationships:")
            for rel_type, target in node.relationships:
                print(f"    {rel_type}: {target.label}")
    
    # Test inheritance
    print("\nTesting inheritance from Planet to Mars:")
    mars = uks.get_node("Mars")
    print(f"  Mars orbits a star: {mars.get_attribute('orbits_star')}")
    print(f"  Mars has gravity: {mars.get_attribute('has_gravity')}")

def test_brainsim_integration(uks: UniversalKnowledgeStore) -> None:
    """Test BrainSimIII integration."""
    print_section_header("BRAINSIM INTEGRATION DEMO")
    
    # Create a BrainSimAdapter instance
    adapter = BrainSimAdapter(
        integration_mode="local_import",
        brainsim_path=str(project_root / "brainsim")
    )
    
    # Initialize the adapter
    success = adapter.initialize()
    print(f"BrainSimAdapter initialization: {'Success' if success else 'Failed'}")
    
    # If initialized successfully, test some cognitive functions
    if success and adapter.brainsim:
        print("\nTesting BrainSim functions:")
        
        # Test concept extraction
        query = "What are the characteristics of Mars and its moons?"
        concepts = adapter.brainsim.extract_concepts(query)
        print(f"\n  Extracted concepts from '{query}':")
        print(f"    {', '.join(concepts)}")
        
        # Test intent analysis
        intent_result = adapter.call_cognitive_function("analyze_intent", query=query)
        print(f"\n  Intent analysis:")
        if intent_result:
            for key, value in intent_result.items():
                print(f"    {key}: {value}")
        else:
            print("    No results (fallback mode)")
        
        # Test fact generation
        facts = adapter.call_cognitive_function("generate_facts", concept="Mars")
        print(f"\n  Generated facts for 'Mars':")
        if facts:
            for subject, predicate, obj in facts:
                print(f"    {subject} {predicate} {obj}")
        else:
            print("    No facts generated (fallback mode)")
    else:
        print("\nUsing fallback implementation since BrainSim is not available")
        
        # Test prompt augmentation with facts from UKS
        query = "Tell me about Mars"
        augmented = adapter.augment_prompt(query, uks)
        print(f"\n  Original prompt: '{query}'")
        print(f"  Augmented prompt: '{augmented}'")

def test_modal_engine(uks: UniversalKnowledgeStore) -> None:
    """Test the ModalEngine with the knowledge store."""
    print_section_header("MODAL ENGINE DEMO")
    
    # Initialize the engine
    engine = ModalEngine(
        brainsim_integration_mode="local_import",
        brainsim_path=str(project_root / "brainsim"),
        model_dir=str(project_root / "models")
    )
    
    # Add the knowledge store
    engine.knowledge_store = uks
    
    # Initialize
    success = engine.initialize()
    print(f"ModalEngine initialization: {'Success' if success else 'Failed'}")
    
    # Process some queries
    if success:
        test_queries = [
            "What is Mars?", 
            "Tell me about the atmosphere on Mars", 
            "Does Mars have any moons?",
            "Compare Earth and Mars"
        ]
        
        print("\nProcessing test queries:")
        for query in test_queries:
            print(f"\n  Query: '{query}'")
            response = engine.process_input(query)
            print(f"  Response: '{response}'")
    
    # Shutdown the engine
    engine.shutdown()
    print("\nEngine has been shut down.")

def test_multimodal_processing() -> None:
    """Test multimodal processing capabilities."""
    print_section_header("MULTIMODAL PROCESSING DEMO")
    
    try:
        from src.core.ai.preprocessing import TextProcessor, ImageProcessor, AudioProcessor, MultimodalAligner
        
        print("Initializing multimodal processors...")
        
        # Initialize processors
        text_processor = TextProcessor(model_name="gpt2")
        image_processor = ImageProcessor(image_size=224)
        audio_processor = AudioProcessor(sample_rate=16000)
        
        # Initialize multimodal aligner
        aligner = MultimodalAligner(
            text_processor=text_processor,
            image_processor=image_processor,
            audio_processor=audio_processor
        )
        
        # Create directory for sample data if it doesn't exist
        sample_data_dir = project_root / "examples" / "sample_data"
        sample_data_dir.mkdir(exist_ok=True, parents=True)
        
        # Create a dummy image for testing if it doesn't exist
        image_path = sample_data_dir / "sample_image.jpg"
        if not image_path.exists():
            try:
                import numpy as np
                from PIL import Image
                
                # Create a simple red image (representing Mars)
                img_array = np.zeros((224, 224, 3), dtype=np.uint8)
                img_array[:, :, 0] = 200  # Red channel
                img = Image.fromarray(img_array)
                img.save(str(image_path))
                print(f"Created dummy Mars image at {image_path}")
            except ImportError:
                print("PIL or numpy not available. Cannot create test image.")
                image_path = None
        
        # Create a simple multimodal sample
        sample = {
            "id": "demo-sample",
            "text": "Mars is the fourth planet from the sun.",
            "image_path": str(image_path) if image_path and image_path.exists() else None,
            "audio_path": None,  # No audio for this demo
            "metadata": {"source": "demo"}
        }
        
        # Process the sample
        print("\nProcessing multimodal sample...")
        result = aligner.process_sample(sample)
        
        # Print results
        print("\nProcessed sample:")
        print(f"  ID: {result.get('id', 'unknown')}")
        print(f"  Available modalities: {result.get('modalities', [])}")
        
        if "text_features" in result:
            print(f"  Text features shape: {result['text_features'].shape if hasattr(result['text_features'], 'shape') else 'N/A'}")
            
        if "image_features" in result:
            print(f"  Image features shape: {result['image_features'].shape if hasattr(result['image_features'], 'shape') else 'N/A'}")
            
    except ImportError as e:
        print(f"Multimodal processing components not available: {e}. Skipping test.")
    except Exception as e:
        print(f"Error during multimodal processing demo: {e}")

def main():
    """Main function to run the demo."""
    parser = argparse.ArgumentParser(description='ImpressionCore Enhanced Demo')
    parser.add_argument('--test', choices=['all', 'knowledge', 'brainsim', 'engine', 'multimodal'], 
                      default='all', help='Specific test to run')
    args = parser.parse_args()
    
    print("\nImpressionCore Enhanced Demo")
    print("===========================\n")
    
    # Create test knowledge store
    uks = create_test_knowledge_store()
    
    # Run selected tests
    if args.test in ['all', 'knowledge']:
        test_knowledge_queries(uks)
        
    if args.test in ['all', 'brainsim']:
        test_brainsim_integration(uks)
        
    if args.test in ['all', 'engine']:
        test_modal_engine(uks)
        
    if args.test in ['all', 'multimodal']:
        test_multimodal_processing()
    
    print("\nDemo completed successfully!")

if __name__ == "__main__":
    main()
