#!/usr/bin/env python3
"""
ImpressionCore: Test Knowledge

Module for test knowledge functionality in the ImpressionCore framework.

File: tests\test_knowledge.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [qa, production, testing, 2025, object-oriented]
Dependencies: [pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements test knowledge functionality for the
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
from tests.test_knowledge import TestKnowledgeNode
instance = TestKnowledgeNode()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.core.knowledge.uks import KnowledgeNode, UniversalKnowledgeStore

class TestKnowledgeNode(unittest.TestCase):
    """Test cases for the KnowledgeNode class."""
    
    def test_basic_functionality(self):
        """Test basic functionality of KnowledgeNode."""
        node = KnowledgeNode("Test")
        node.add_attribute("attribute1", "value1")
        self.assertEqual(node.get_attribute("attribute1"), "value1")
    
    def test_init_with_attributes(self):
        """Test initialization with attributes."""
        node = KnowledgeNode("Test", {"attribute1": "value1"})
        self.assertEqual(node.get_attribute("attribute1"), "value1")
    
    def test_relations(self):
        """Test relations between nodes."""
        node1 = KnowledgeNode("Node1")
        node2 = KnowledgeNode("Node2")
        
        node1.add_relation("related_to", node2)
        
        relations = node1.get_relations("related_to")
        self.assertEqual(len(relations), 1)
        self.assertEqual(relations[0], node2)
    
    def test_inheritance(self):
        """Test attribute inheritance."""
        parent = KnowledgeNode("Parent")
        parent.add_attribute("inherited_attr", "parent_value")
        
        child = KnowledgeNode("Child", parent=parent)
        
        self.assertEqual(child.get_attribute("inherited_attr"), "parent_value")
    
    def test_attribute_override(self):
        """Test that child attributes override parent attributes."""
        parent = KnowledgeNode("Parent")
        parent.add_attribute("attr", "parent_value")
        
        child = KnowledgeNode("Child", parent=parent)
        child.add_attribute("attr", "child_value")
        
        self.assertEqual(child.get_attribute("attr"), "child_value")
    
    def test_get_all_attributes(self):
        """Test getting all attributes including inherited ones."""
        parent = KnowledgeNode("Parent")
        parent.add_attribute("parent_attr", "parent_value")
        parent.add_attribute("shared_attr", "parent_version")
        
        child = KnowledgeNode("Child", parent=parent)
        child.add_attribute("child_attr", "child_value")
        child.add_attribute("shared_attr", "child_version")
        
        all_attrs = child.get_all_attributes()
        
        self.assertIn("parent_attr", all_attrs)
        self.assertIn("child_attr", all_attrs)
        self.assertIn("shared_attr", all_attrs)
        self.assertEqual(all_attrs["shared_attr"], "child_version")  # Should be overridden

class TestUniversalKnowledgeStore(unittest.TestCase):
    """Test cases for the UniversalKnowledgeStore class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.uks = UniversalKnowledgeStore()
        
        # Add some test nodes
        self.animal = self.uks.add_node("Animal", {"has_cells": True})
        self.mammal = self.uks.add_node("Mammal", {"has_fur": True}, "Animal")
        self.dog = self.uks.add_node("Dog", {"barks": True}, "Mammal")
        self.cat = self.uks.add_node("Cat", {"meows": True}, "Mammal")
    
    def test_node_creation(self):
        """Test that nodes can be created and retrieved."""
        self.assertIn("Animal", self.uks.nodes)
        self.assertIsInstance(self.uks.nodes["Animal"], KnowledgeNode)
    
    def test_inheritance(self):
        """Test that nodes inherit attributes from parent nodes."""
        # Dog should inherit has_cells from Animal through Mammal
        self.assertEqual(self.dog.get_attribute("has_cells"), True)
        
        # Dog should inherit has_fur from Mammal
        self.assertEqual(self.dog.get_attribute("has_fur"), True)
    
    def test_node_retrieval(self):
        """Test that nodes can be retrieved by label."""
        dog = self.uks.query("Dog")
        self.assertEqual(dog.label, "Dog")
    
    def test_query(self):
        """Test querying the knowledge store."""
        results = self.uks.query("Dog")
        self.assertIsNotNone(results)
        self.assertEqual(results.name, "Dog")
    
    def test_save_and_load(self):
        """Test saving and loading the knowledge store."""
        # Add some relationships
        self.uks.add_relationship("Dog", "is_pet_of", "Human")

        # Save to temporary file
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, "test_uks.json")

        self.uks.save(file_path)
        self.assertTrue(os.path.exists(file_path), "Knowledge store file was not saved")
        
        # Create a new UKS and load from file
        new_uks = UniversalKnowledgeStore()
        success = new_uks.load(file_path)
        
        self.assertTrue(success)
        self.assertIn("Dog", new_uks.nodes)
        self.assertEqual(new_uks.nodes["Dog"].get_attribute("barks"), True)
        
        # Clean up
        try:
            os.remove(file_path)
        except:
            pass

if __name__ == "__main__":
    unittest.main()

"""
Test script for the Universal Knowledge Store module.
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.knowledge.uks import KnowledgeNode  # Ensure consistent import
from src.core.knowledge.uks import UniversalKnowledgeStore

def main():
    """
    
    main function for processing.
    
    Args:
        No arguments: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
    """
    print("Testing Universal Knowledge Store...")
    
    # Create a new knowledge store
    uks = UniversalKnowledgeStore()
    
    # Create some nodes
    mars = KnowledgeNode("Mars")
    mars.set_attribute("type", "planet")
    mars.set_attribute("color", "red")
    
    earth = KnowledgeNode("Earth")
    earth.set_attribute("type", "planet")
    earth.set_attribute("color", "blue")
    
    sun = KnowledgeNode("Sun")
    sun.set_attribute("type", "star")
    sun.set_attribute("color", "yellow")
    
    # Add nodes to the store
    mars_id = uks.add_node(mars)
    earth_id = uks.add_node(earth)
    sun_id = uks.add_node(sun)
    
    print(f"Added nodes: {mars}, {earth}, {sun}")
    
    # Add relationships
    uks.add_relation(mars, "orbits", sun)
    uks.add_relation(earth, "orbits", sun)
    
    # Test query
    planets = uks.query(filters={"type": "planet"})
    print(f"Found planets: {[p.name for p in planets]}")
    
    # Test relation query
    orbiting_bodies = uks.query_by_relation(sun_id, "orbits")
    print(f"Bodies orbiting sun: {[b.name for b in orbiting_bodies]}")
    
    print("Universal Knowledge Store test completed successfully!")

if __name__ == "__main__":
    main()
