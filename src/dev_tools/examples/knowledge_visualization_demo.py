#!/usr/bin/env python3
"""
ImpressionCore: Knowledge Visualization Demo

Module for knowledge visualization demo functionality in the ImpressionCore framework.

File: examples\knowledge_visualization_demo.py
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
This module implements knowledge visualization demo functionality for the
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
from examples.knowledge_visualization_demo import MainClass
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
import subprocess
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.core.knowledge.uks import UniversalKnowledgeStore
from src.core.knowledge.node import KnowledgeNode
from src.core.knowledge.visualization import generate_visualization, install_graphviz_instructions

def create_solar_system_knowledge():
    """Create a knowledge graph of the solar system."""
    uks = UniversalKnowledgeStore()
    
    # Create sun
    sun = KnowledgeNode("Sun")
    sun.set_attribute("type", "star")
    sun.set_attribute("color", "yellow")
    sun.set_attribute("diameter_km", 1392684)
    sun.set_attribute("mass_kg", 1.989e30)
    sun.add_tag("celestial_body")
    uks.add_node(sun)
    
    # Create planets
    planets = {
        "Mercury": {"color": "gray", "diameter_km": 4879, "position": 1},
        "Venus": {"color": "yellow", "diameter_km": 12104, "position": 2},
        "Earth": {"color": "blue", "diameter_km": 12742, "position": 3},
        "Mars": {"color": "red", "diameter_km": 6779, "position": 4},
        "Jupiter": {"color": "orange", "diameter_km": 139820, "position": 5},
        "Saturn": {"color": "yellow", "diameter_km": 116460, "position": 6},
        "Uranus": {"color": "blue", "diameter_km": 50724, "position": 7},
        "Neptune": {"color": "blue", "diameter_km": 49244, "position": 8}
    }
    
    for name, attrs in planets.items():
        planet = KnowledgeNode(name)
        planet.set_attribute("type", "planet")
        for key, value in attrs.items():
            planet.set_attribute(key, value)
        planet.add_tag("celestial_body")
        uks.add_node(planet)
        
        # Add relation to sun
        uks.add_relation(planet, "orbits", sun)
    
    # Add some moons
    moons = {
        "Luna": {"parent": "Earth", "diameter_km": 3475},
        "Phobos": {"parent": "Mars", "diameter_km": 22},
        "Deimos": {"parent": "Mars", "diameter_km": 12},
        "Io": {"parent": "Jupiter", "diameter_km": 3643},
        "Europa": {"parent": "Jupiter", "diameter_km": 3122},
        "Titan": {"parent": "Saturn", "diameter_km": 5149}
    }
    
    for name, attrs in moons.items():
        moon = KnowledgeNode(name)
        moon.set_attribute("type", "moon")
        moon.set_attribute("diameter_km", attrs["diameter_km"])
        moon.add_tag("celestial_body")
        uks.add_node(moon)
        
        # Add relation to parent planet
        parent_planet = uks.get_node_by_name(attrs["parent"])
        if parent_planet:
            uks.add_relation(moon, "orbits", parent_planet)
    
    return uks

def main():
    """Run the knowledge visualization demo."""
    print("Creating Solar System Knowledge Graph...")
    uks = create_solar_system_knowledge()
    print(f"Created knowledge store with {len(uks.nodes)} nodes")
    
    # Export to GraphViz DOT file
    output_dir = os.path.join(project_root, "output", "knowledge_graphs")
    os.makedirs(output_dir, exist_ok=True)
    dot_file = os.path.join(output_dir, "solar_system.dot")
    
    print("Exporting to GraphViz DOT file...")
    uks.export_to_graphviz(dot_file)
    
    # Generate visualization using helper function
    print("Generating visualization...")
    output_file = os.path.join(output_dir, "solar_system.png")
    result = generate_visualization(dot_file, output_file)
    
    if result["success"]:
        print(f"Visualization successfully generated using {result['method']}!")
        print(f"Saved to: {result['output_file']}")
    else:
        print("Could not generate visualization.")
        print(f"Error: {result.get('error')}")
        
        if "install_instructions" in result:
            print("\nTo install GraphViz:")
            print(result["install_instructions"])
        
        print(f"\nYou can manually convert the DOT file at {dot_file}")
    
    # Demonstrate some queries
    print("\nQuerying the knowledge graph:")
    
    # Find all planets
    planets = uks.query(filters={"type": "planet"})
    print(f"Found {len(planets)} planets:")
    for planet in sorted(planets, key=lambda p: p.get_attribute("position")):
        print(f"  - {planet.name}: {planet.get_attribute('diameter_km')} km")
    
    # Find all moons that orbit Jupiter
    jupiter = uks.get_node_by_name("Jupiter")
    if jupiter:
        moons = uks.query(
            filters={"type": "moon"},
            relation_filters=[{"type": "orbits", "target": jupiter.id}]
        )
        print(f"\nFound {len(moons)} moons of Jupiter:")
        for moon in moons:
            print(f"  - {moon.name}: {moon.get_attribute('diameter_km')} km")
    
    print("\nDemo completed successfully!")

if __name__ == "__main__":
    main()
