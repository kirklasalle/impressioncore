#!/usr/bin/env python3
"""
ImpressionCore: Enhanced Rule Reasoning

Module for enhanced rule reasoning functionality in the ImpressionCore framework.

File: examples\enhanced_rule_reasoning.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [production, object-oriented, 2025]
Dependencies: [rich, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements enhanced rule reasoning functionality for the
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
from examples.enhanced_rule_reasoning import ExplainableRule
instance = ExplainableRule()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

# Import the base rule-based reasoning implementation
import sys
import os
import logging
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path
import rich
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

# Initialize rich console
console = Console()

# Update logging to use rich for better formatting
from rich.logging import RichHandler

# Configure rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, show_time=True, show_path=False)]
)
logger = logging.getLogger("rich_logger")

# Add progress bar for long-running tasks
def run_with_progress(task_name, task_function, *args, **kwargs):
    """
    Run a task with a progress bar.

    Args:
        task_name (str): Name of the task to display.
        task_function (callable): The function to execute.
        *args: Positional arguments for the task function.
        **kwargs: Keyword arguments for the task function.

    Returns:
        Any: The result of the task function.
    """
    with Progress(
        SpinnerColumn(),
        BarColumn(),
        TextColumn("{task.description}"),
        console=console
    ) as progress:
        task_id = progress.add_task(task_name, total=None)
        result = task_function(*args, **kwargs)
        progress.update(task_id, completed=1)
    return result

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import from the original rule-based reasoning example
from examples.rule_based_reasoning import (
    UniversalKnowledgeStore, Rule, RuleEngine,
    context_has_key, context_get_value, create_context_from_dict
)
from src.core.brainsim_adapter import BrainSimAdapter

def create_detailed_solar_system():
    """Create an enhanced knowledge base with detailed planet information."""
    uks = UniversalKnowledgeStore()
    adsim_adapter = BrainSimAdapter(uks)
    
    # Create base classification nodes
    celestial_body_id = adsim_adapter.add_node("CelestialBody", {"in_space": True})
    planet_id = adsim_adapter.add_node("Planet", {"orbits_star": True})
    adsim_adapter.add_relationship(planet_id, celestial_body_id, "type")
    
    # Define planet types
    terrestrial_planet_id = adsim_adapter.add_node("TerrestrialPlanet", {"has_solid_surface": True})
    gas_giant_id = adsim_adapter.add_node("GasGiant", {"has_solid_surface": False, "has_gas_atmosphere": True})
    ice_giant_id = adsim_adapter.add_node("IceGiant", {"has_solid_surface": False, "has_ice_composition": True})

    adsim_adapter.add_relationship(terrestrial_planet_id, planet_id, "type")
    adsim_adapter.add_relationship(gas_giant_id, planet_id, "type")
    adsim_adapter.add_relationship(ice_giant_id, planet_id, "type")
    
    # Mercury
    mercury_id = adsim_adapter.add_node("Mercury", {
        "temperature": 430,  # Average temperature in °C
        "has_atmosphere": False,
        "distance_from_sun": 0.39,  # AU
        "gravity": 0.38,  # Earth = 1
        "has_water": False,
        "has_magnetic_field": True,
        "magnetic_field_strength": 0.01,  # Earth = 1
        "moon_count": 0
    })
    adsim_adapter.add_relationship(mercury_id, terrestrial_planet_id, "type")
    
    # Venus
    venus_id = adsim_adapter.add_node("Venus", {
        "temperature": 465,  # Average temperature in °C
        "has_atmosphere": True,
        "atmosphere_composition": "CO2",
        "atmospheric_pressure": 92,  # Earth = 1
        "distance_from_sun": 0.72,  # AU
        "gravity": 0.91,  # Earth = 1
        "has_water": False,
        "has_magnetic_field": False,
        "moon_count": 0
    })
    adsim_adapter.add_relationship(venus_id, terrestrial_planet_id, "type")
    
    # Earth
    earth_id = adsim_adapter.add_node("Earth", {
        "temperature": 15,  # Average temperature in °C
        "has_atmosphere": True,
        "atmosphere_composition": "Nitrogen, Oxygen",
        "atmospheric_pressure": 1.0,  # Earth = 1
        "distance_from_sun": 1.0,  # AU
        "gravity": 1.0,  # Earth = 1
        "has_water": True,
        "water_state": "liquid, solid, gas",
        "has_magnetic_field": True,
        "magnetic_field_strength": 1.0,  # Earth = 1
        "has_life": True,
        "moon_count": 1
    })
    adsim_adapter.add_relationship(earth_id, terrestrial_planet_id, "type")
    
    # Mars
    mars_id = adsim_adapter.add_node("Mars", {
        "temperature": -65,  # Average temperature in °C
        "has_atmosphere": True,
        "atmosphere_composition": "CO2",
        "atmospheric_pressure": 0.01,  # Earth = 1
        "distance_from_sun": 1.52,  # AU
        "gravity": 0.38,  # Earth = 1
        "has_water": True,
        "water_state": "ice, trace gas",
        "has_magnetic_field": False,
        "moon_count": 2
    })
    adsim_adapter.add_relationship(mars_id, terrestrial_planet_id, "type")
    
    # Jupiter
    jupiter_id = adsim_adapter.add_node("Jupiter", {
        "temperature": -145,  # Average temperature in °C
        "has_atmosphere": True,
        "atmosphere_composition": "Hydrogen, Helium",
        "distance_from_sun": 5.20,  # AU
        "gravity": 2.53,  # Earth = 1
        "has_water": True,
        "water_state": "ice, gas",
        "has_magnetic_field": True,
        "magnetic_field_strength": 14.0,  # Earth = 1
        "moon_count": 79
    })
    adsim_adapter.add_relationship(jupiter_id, gas_giant_id, "type")
    
    # Saturn
    saturn_id = adsim_adapter.add_node("Saturn", {
        "temperature": -178,  # Average temperature in °C
        "has_atmosphere": True,
        "atmosphere_composition": "Hydrogen, Helium",
        "distance_from_sun": 9.54,  # AU
        "gravity": 1.07,  # Earth = 1
        "has_water": True,
        "water_state": "ice",
        "has_magnetic_field": True,
        "magnetic_field_strength": 0.63,  # Earth = 1
        "moon_count": 82
    })
    adsim_adapter.add_relationship(saturn_id, gas_giant_id, "type")
    
    # Uranus
    uranus_id = adsim_adapter.add_node("Uranus", {
        "temperature": -224,  # Average temperature in °C
        "has_atmosphere": True,
        "atmosphere_composition": "Hydrogen, Helium, Methane",
        "distance_from_sun": 19.19,  # AU
        "gravity": 0.92,  # Earth = 1
        "has_water": True,
        "water_state": "ice",
        "has_magnetic_field": True,
        "magnetic_field_strength": 0.23,  # Earth = 1
        "moon_count": 27
    })
    adsim_adapter.add_relationship(uranus_id, ice_giant_id, "type")
    
    # Neptune
    neptune_id = adsim_adapter.add_node("Neptune", {
        "temperature": -214,  # Average temperature in °C
        "has_atmosphere": True,
        "atmosphere_composition": "Hydrogen, Helium, Methane",
        "distance_from_sun": 30.07,  # AU
        "gravity": 1.12,  # Earth = 1
        "has_water": True,
        "water_state": "ice",
        "has_magnetic_field": True,
        "magnetic_field_strength": 0.14,  # Earth = 1
        "moon_count": 14
    })
    adsim_adapter.add_relationship(neptune_id, ice_giant_id, "type")
    
    return uks

class ExplainableRule(Rule):
    """An extension of the Rule class that includes explanation capabilities."""
    
    def __init__(self, name, condition, action, explanation_func=None, priority=0, description=""):
        """
        Initialize an explainable rule.
        
        Args:
            name: Rule name
            condition: Condition function that returns True/False
            action: Action function to execute when condition is True
            explanation_func: Function that explains why the rule fired
            priority: Rule priority (higher numbers = higher priority)
            description: Human-readable description of the rule
        """
        super().__init__(name, conditions=[condition], actions=[action], description=description)
        self.explanation_func = explanation_func or self._default_explanation
        self.priority = priority
    
    def _default_explanation(self, context, result):
        """Default explanation if none provided."""
        condition_name = self.condition.__name__ if hasattr(self.condition, "__name__") else "condition"
        return f"Rule '{self.name}' applied because {condition_name} returned True."
    
    def explain(self, context, result):
        """Generate an explanation for why this rule fired."""
        return self.explanation_func(context, result)

def create_enhanced_rules():
    """Create an enhanced set of rules with interdependencies and explanations."""
    rules = []
    
    # Basic temperature classification rules (similar to original)
    def hot_condition(context):
        """Rule condition for hot planets."""
        if not context_has_key(context, 'temperature'):
            return False
        temp = context_get_value(context, 'temperature')
        if isinstance(temp, str):
            try:
                temp = float(temp)
            except (ValueError, TypeError):
                return False
        return temp > 100
    
    def hot_explanation(context, result):
        """
        
    hot_explanation function for processing.
    
    Args:
        context, result: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        temp = context_get_value(context, 'temperature')
        name = context_get_value(context, 'name') or "This planet"
        return f"{name} is classified as HOT because its temperature is {temp}°C, which exceeds 100°C. " \
               f"Such high temperatures make it {result['habitability']}."
    
    hot_rule = ExplainableRule(
        name="hot_planet",
        condition=hot_condition,
        action=lambda context: {
            'habitability': 'uninhabitable',
            'classification': 'hot',
            'reason': f"Temperature of {context_get_value(context, 'temperature')}°C is too hot for life as we know it"
        },
        explanation_func=hot_explanation,
        priority=10,
        description="Classify planets with temperature > 100°C as hot"
    )
    rules.append(hot_rule)
    
    # Cold planets
    def cold_condition(context):
        """Rule condition for cold planets."""
        if not context_has_key(context, 'temperature'):
            return False
        temp = context_get_value(context, 'temperature')
        if isinstance(temp, str):
            try:
                temp = float(temp)
            except (ValueError, TypeError):
                return False
        return temp < -50
    
    def cold_explanation(context, result):
        """
        
    cold_explanation function for processing.
    
    Args:
        context, result: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        temp = context_get_value(context, 'temperature')
        name = context_get_value(context, 'name') or "This planet"
        return f"{name} is classified as COLD because its temperature is {temp}°C, which is below -50°C. " \
               f"Such cold temperatures make it {result['habitability']}."
    
    cold_rule = ExplainableRule(
        name="cold_planet",
        condition=cold_condition,
        action=lambda context: {
            'habitability': 'challenging',
            'classification': 'cold',
            'reason': f"Temperature of {context_get_value(context, 'temperature')}°C requires significant heating"
        },
        explanation_func=cold_explanation,
        priority=10,
        description="Classify planets with temperature < -50°C as cold"
    )
    rules.append(cold_rule)
    
    # Temperate planets
    def temperate_condition(context):
        """Rule condition for temperate planets."""
        if not context_has_key(context, 'temperature'):
            return False
        temp = context_get_value(context, 'temperature')
        if isinstance(temp, str):
            try:
                temp = float(temp)
            except (ValueError, TypeError):
                return False
        return -50 <= temp <= 50
    
    def temperate_explanation(context, result):
        """
        
    temperate_explanation function for processing.
    
    Args:
        context, result: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        temp = context_get_value(context, 'temperature')
        name = context_get_value(context, 'name') or "This planet"
        return f"{name} is classified as TEMPERATE because its temperature is {temp}°C, which is between -50°C and 50°C. " \
               f"This moderate temperature range makes it {result['habitability']}."
    
    temperate_rule = ExplainableRule(
        name="temperate_planet",
        condition=temperate_condition,
        action=lambda context: {
            'habitability': 'potentially habitable',
            'classification': 'temperate',
            'reason': f"Temperature of {context_get_value(context, 'temperature')}°C is within habitable range"
        },
        explanation_func=temperate_explanation,
        priority=10,
        description="Classify planets with temperature between -50°C and 50°C as temperate"
    )
    rules.append(temperate_rule)
    
    # New: Habitable Zone rule (depends on distance from sun)
    def habitable_zone_condition(context):
        """Rule condition for habitable zone planets."""
        if not context_has_key(context, 'distance_from_sun'):
            return False
        distance = context_get_value(context, 'distance_from_sun')
        if isinstance(distance, str):
            try:
                distance = float(distance)
            except (ValueError, TypeError):
                return False
        # Simplified habitable zone is between 0.9 and 1.7 AU
        return 0.9 <= distance <= 1.7
    
    def habitable_zone_explanation(context, result):
        """
        
    habitable_zone_explanation function for processing.
    
    Args:
        context, result: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        distance = context_get_value(context, 'distance_from_sun')
        name = context_get_value(context, 'name') or "This planet"
        return f"{name} is in the HABITABLE ZONE because its distance from the Sun is {distance} AU, " \
               f"which falls within the range of 0.9-1.7 AU where liquid water could potentially exist."
    
    habitable_zone_rule = ExplainableRule(
        name="habitable_zone",
        condition=habitable_zone_condition,
        action=lambda context: {
            'zone_classification': 'habitable_zone',
            'zone_reason': f"Distance of {context_get_value(context, 'distance_from_sun')} AU is within habitable range"
        },
        explanation_func=habitable_zone_explanation,
        priority=15,
        description="Identify planets in the habitable zone (0.9-1.7 AU from star)"
    )
    rules.append(habitable_zone_rule)
    
    # New: Life potential rule (depends on temperature, water, and atmosphere)
    def life_potential_condition(context):
        """Rule condition for planets with potential for life."""
        # Need temperate conditions
        if not temperate_condition(context):
            return False
        
        # Need water
        has_water = context_get_value(context, 'has_water')
        if not has_water:
            return False
        
        # Need atmosphere
        has_atmosphere = context_get_value(context, 'has_atmosphere')
        return has_atmosphere
    
    def life_potential_explanation(context, result):
        """
        
    life_potential_explanation function for processing.
    
    Args:
        context, result: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        name = context_get_value(context, 'name') or "This planet"
        temp = context_get_value(context, 'temperature')
        composition = context_get_value(context, 'atmosphere_composition', "unknown composition")
        
        return f"{name} has {result['life_potential']} because it:\n" \
               f"1. Has a temperature of {temp}°C (within habitable range)\n" \
               f"2. Has water present\n" \
               f"3. Has an atmosphere of {composition}\n" \
               f"These factors are essential prerequisites for life as we know it on Earth."
    
    life_potential_rule = ExplainableRule(
        name="life_potential",
        condition=life_potential_condition,
        action=lambda context: {
            'life_potential': 'high potential for life',
            'potential_reason': "Has temperate climate, water, and atmosphere"
        },
        explanation_func=life_potential_explanation,
        priority=20,
        description="Identify planets with key conditions for life"
    )
    rules.append(life_potential_rule)
    
    # New: Colonization candidate (depends on temperature, gravity, and magnetic field)
    def colonization_condition(context):
        """Rule condition for planets suitable for colonization."""
        # Need acceptable temperature
        if not context_has_key(context, 'temperature'):
            return False
        temp = context_get_value(context, 'temperature')
        if isinstance(temp, str):
            try:
                temp = float(temp)
            except (ValueError, TypeError):
                return False
        temp_suitable = -80 <= temp <= 60  # Wider range than temperate
        
        # Need acceptable gravity
        if not context_has_key(context, 'gravity'):
            return False
        gravity = context_get_value(context, 'gravity')
        if isinstance(gravity, str):
            try:
                gravity = float(gravity)
            except (ValueError, TypeError):
                return False
        gravity_suitable = 0.3 <= gravity <= 1.5  # Range humans could adapt to
        
        return temp_suitable and gravity_suitable
    
    def colonization_explanation(context, result):
        """
        
    colonization_explanation function for processing.
    
    Args:
        context, result: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        name = context_get_value(context, 'name') or "This planet"
        temp = context_get_value(context, 'temperature')
        gravity = context_get_value(context, 'gravity')
        magnetic_field = "present" if context_get_value(context, 'has_magnetic_field') else "absent"
        
        return f"{name} is rated as {result['colonization_suitability']} because:\n" \
               f"1. Its temperature of {temp}°C is within manageable range for human habitation with technology\n" \
               f"2. Its gravity of {gravity}g is within adaptation range for humans\n" \
               f"3. Magnetic field is {magnetic_field} - {result.get('protection_needed', '')}"
    
    colonization_rule = ExplainableRule(
        name="colonization_candidate",
        condition=colonization_condition,
        action=lambda context: {
            'colonization_suitability': 'suitable for colonization' if context_get_value(context, 'has_magnetic_field') else 'requires additional radiation protection',
            'protection_needed': '' if context_get_value(context, 'has_magnetic_field') else 'radiation shielding would be needed'
        },
        explanation_func=colonization_explanation,
        priority=25,
        description="Identify planets suitable for human colonization"
    )
    rules.append(colonization_rule)
    
    # New: Gas giant identification
    def gas_giant_condition(context):
        """Rule condition for gas giants."""
        if context_has_key(context, 'name'):
            name = context_get_value(context, 'name')
            # Check for direct relationship
            node_type = context_get_value(context, 'type')
            if node_type and "GasGiant" in node_type:
                return True
        
        # Or check by properties
        return context_get_value(context, 'has_solid_surface') is False and \
               context_get_value(context, 'has_gas_atmosphere') is True
    
    gas_giant_rule = ExplainableRule(
        name="gas_giant",
        condition=gas_giant_condition,
        action=lambda context: {
            'planet_type': 'gas giant',
            'research_value': 'atmospheric studies'
        },
        explanation_func=lambda context, result: f"{context_get_value(context, 'name')} is a gas giant with no solid surface but extensive gas atmosphere.",
        priority=5
    )
    rules.append(gas_giant_rule)
    
    # New: Asteroid impact risk (depends on magnetic field and moon count)
    def asteroid_risk_condition(context):
        """Rule condition for asteroid impact risk."""
        # Only apply to terrestrial planets
        moon_count = context_get_value(context, 'moon_count')
        if moon_count is None:
            return False
            
        # Consider both moon count and magnetic field
        has_magnetic_field = context_get_value(context, 'has_magnetic_field')
        return True  # This rule applies to all planets, with different results
    
    def asteroid_risk_action(context):
        """Determine asteroid impact risk level."""
        moon_count = context_get_value(context, 'moon_count')
        has_magnetic_field = context_get_value(context, 'has_magnetic_field')
        
        # More moons can provide some protection by capturing impactors
        if moon_count >= 2:
            risk = "lower"
            reason = f"Has {moon_count} moons that can capture potential impactors"
        elif moon_count == 1:
            risk = "moderate"
            reason = "Has 1 moon providing limited protection"
        else:
            risk = "higher"
            reason = "Has no moons to capture potential impactors"
            
        return {
            'asteroid_impact_risk': risk,
            'impact_risk_reason': reason
        }
    
    def asteroid_risk_explanation(context, result):
        """
        
    asteroid_risk_explanation function for processing.
    
    Args:
        context, result: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        name = context_get_value(context, 'name') or "This planet"
        moon_count = context_get_value(context, 'moon_count')
        
        explanation = f"{name} has {result['asteroid_impact_risk']} risk of asteroid impacts because it has {moon_count} moon(s). "
        explanation += result['impact_risk_reason']
        
        return explanation
    
    asteroid_risk_rule = ExplainableRule(
        name="asteroid_impact_risk",
        condition=asteroid_risk_condition,
        action=asteroid_risk_action,
        explanation_func=asteroid_risk_explanation,
        priority=15
    )
    rules.append(asteroid_risk_rule)
    
    return rules

class ExplainableRuleEngine(RuleEngine):
    """An extension of RuleEngine that provides explanations."""
    
    def __init__(self, knowledge_store):
        """
        Initialize the explainable rule engine.

        Args:
            knowledge_store: The knowledge store instance to use.
        """
        super().__init__(knowledge_store)
        self.explanations = {}
        self.rule_history = {}
    
    def add_rule(self, rule):
        """Add a rule to the engine."""
        super().add_rule(rule)
    
    def run(self, context):
        """Run all rules and store explanations."""
        self.rule_history[id(context)] = []
        results = []
        
        for rule in self.rules:
            try:
                # Only evaluate if rule condition passes
                if rule.condition(context):
                    # Apply the rule action
                    result = rule.action(context)
                    
                    # Store which rule fired and its result
                    self.rule_history[id(context)].append({
                        'rule_name': rule.name,
                        'rule_description': getattr(rule, 'description', ''),
                        'result': result
                    })
                    
                    # If rule is explainable, get explanation
                    if hasattr(rule, 'explain'):
                        explanation = rule.explain(context, result)
                        
                        # Store explanation
                        if id(context) not in self.explanations:
                            self.explanations[id(context)] = []
                        
                        self.explanations[id(context)].append({
                            'rule_name': rule.name,
                            'explanation': explanation
                        })
                    
                    results.append(result)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {e}")
        
        return results
    
    def get_explanations(self, context):
        """Get explanations for a specific context."""
        context_id = id(context)
        if context_id in self.explanations:
            return self.explanations[context_id]
        return []
    
    def get_rule_history(self, context):
        """Get rule history for a specific context."""
        context_id = id(context)
        if context_id in self.rule_history:
            return self.rule_history[context_id]
        return []

def visualize_planets_and_rules(uks, explanations_by_planet, rule_history_by_planet):
    """Create a visual representation of planets and applied rules."""
    plt.figure(figsize=(15, 10))
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add planet nodes
    planets = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
    planet_types = {}
    
    for planet_name in planets:
        planet = uks.get_node(planet_name)
        if not planet:
            continue
        
        # Add planet to graph
        G.add_node(planet_name)
        
        # Add planet type if available
        if "properties" in planet and "classification" in planet["properties"]:
            classification = planet["properties"]["classification"]
            planet_types[planet_name] = classification
            
            # Add classification node and edge
            G.add_node(classification)
            G.add_edge(planet_name, classification)
        
        # Add other significant properties as nodes
        significant_properties = ["habitability", "zone_classification", "life_potential", "colonization_suitability"]
        for prop in significant_properties:
            if "properties" in planet and prop in planet["properties"]:
                prop_value = planet["properties"][prop]
                node_name = f"{prop}: {prop_value}"
                G.add_node(node_name)
                G.add_edge(planet_name, node_name)
    
    # Set positions
    pos = nx.spring_layout(G, seed=42)
    
    # Draw the graph
    planet_nodes = [n for n in G.nodes() if n in planets]
    classification_nodes = [n for n in G.nodes() if n not in planets and not n.startswith("habitability:") and 
                           not n.startswith("zone_classification:") and not n.startswith("life_potential:") and 
                           not n.startswith("colonization_suitability:")]
    property_nodes = [n for n in G.nodes() if n not in planets and n not in classification_nodes]
    
    nx.draw_networkx_nodes(G, pos, nodelist=planet_nodes, node_color='skyblue', node_size=1000, alpha=0.8)
    nx.draw_networkx_nodes(G, pos, nodelist=classification_nodes, node_color='lightgreen', node_size=800, alpha=0.8)
    nx.draw_networkx_nodes(G, pos, nodelist=property_nodes, node_color='salmon', node_size=600, alpha=0.7)
    
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, edge_color='gray')
    nx.draw_networkx_labels(G, pos, font_size=8)
    
    plt.title('Solar System Knowledge Graph with Inferred Properties')
    plt.axis('off')
    
    # Save the graph image
    plt.tight_layout()
    plt.savefig('solar_system_knowledge_graph.png')
    logger.info("Knowledge graph visualization saved as 'solar_system_knowledge_graph.png'")
    
    # Generate text explanations
    explanation_file = 'planet_rule_explanations.txt'
    with open(explanation_file, 'w') as f:
        f.write("# Solar System Analysis: Rule-Based Reasoning Explanations\n\n")
        
        for planet_name in sorted(explanations_by_planet.keys()):
            f.write(f"## {planet_name}\n\n")
            
            # Summarize rules that fired for this planet
            if planet_name in rule_history_by_planet:
                rule_names = [rule['rule_name'] for rule in rule_history_by_planet[planet_name]]
                f.write(f"Rules applied: {', '.join(rule_names)}\n\n")
            
            # Write detailed explanations
            for explanation in explanations_by_planet[planet_name]:
                f.write(f"### Rule: {explanation['rule_name']}\n")
                f.write(f"{explanation['explanation']}\n\n")
            
            f.write("---\n\n")
    
    logger.info(f"Rule explanations saved to '{explanation_file}'")

# Add a function to display planet properties in a table
def display_planet_properties(planet_name, properties):
    """
    Display planet properties in a formatted table.

    Args:
        planet_name (str): Name of the planet.
        properties (dict): Dictionary of planet properties.
    """
    table = Table(title=f"Properties of {planet_name}", show_header=True, header_style="bold magenta")
    table.add_column("Property", style="dim", width=30)
    table.add_column("Value", style="bold")

    for key, value in properties.items():
        table.add_row(key, str(value))

    console.print(table)

def main():
    """Run the enhanced rule-based reasoning demo."""
    logger.info("\n[bold green]Starting enhanced rule-based reasoning demo[/bold green]")

    # Create enhanced knowledge store with solar system information
    uks = run_with_progress("[cyan]Creating Solar System Knowledge Base[/cyan]", create_detailed_solar_system)

    # Create explainable rule engine and add enhanced rules
    rule_engine = ExplainableRuleEngine(uks)

    for rule in run_with_progress("[cyan]Creating Enhanced Rules[/cyan]", create_enhanced_rules):
        rule_engine.add_rule(rule)

    # Process all planets
    planets = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]

    explanations_by_planet = {}
    rule_history_by_planet = {}

    for planet_name in planets:
        planet = uks.get_node(planet_name)

        if planet:
            properties = planet["properties"]
            properties['name'] = planet_name

            # Display planet properties in a table
            display_planet_properties(planet_name, properties)

            # Create context for this planet
            context = create_context_from_dict(properties)

            console.rule(f"[bold green]Processing Planet: {planet_name}[/bold green]")

            # Apply rules with progress
            results = run_with_progress(f"[cyan]Applying Rules to {planet_name}[/cyan]", rule_engine.run, context)

            if results:
                for i, result in enumerate(results):
                    console.print(Panel.fit(f"[bold green]Rule {i+1} result:[/bold green]\n{result}", title=f"[bold cyan]Result for {planet_name}[/bold cyan]"))

                    # Update knowledge store with inferred facts
                    for key, value in result.items():
                        planet["properties"][key] = value
            else:
                console.print(Panel.fit("[yellow]No rules applied[/yellow]", title=f"[bold red]No Results for {planet_name}[/bold red]"))

            # Get explanations for this planet
            explanations = rule_engine.get_explanations(context)
            rule_history = rule_engine.get_rule_history(context)

            if explanations:
                explanations_by_planet[planet_name] = explanations

            if rule_history:
                rule_history_by_planet[planet_name] = rule_history

            console.print(f"[bold cyan]Rules applied to {planet_name}:[/bold cyan] {len(rule_history)}")
            if explanations:
                console.print("[bold magenta]Explanations:[/bold magenta]")
                for explanation in explanations:
                    console.print(f"  - [bold]{explanation['rule_name']}[/bold]: {explanation['explanation'][:60]}...")

            console.rule("-" * 50, style="dim")

    # Show updated knowledge
    console.rule("[bold blue]Updated Knowledge with Inferred Properties[/bold blue]")
    for planet_name in planets:
        planet = uks.get_node(planet_name)
        if planet:
            interesting_props = {k: v for k, v in planet["properties"].items() 
                                if k in ["classification", "habitability", "zone_classification", 
                                        "life_potential", "colonization_suitability", 
                                        "asteroid_impact_risk", "planet_type"]}

            display_planet_properties(planet_name, interesting_props)

    # Create visualization of the results
    try:
        console.rule("[bold yellow]Generating Visualizations[/bold yellow]")
        run_with_progress("[cyan]Generating Visualizations[/cyan]", visualize_planets_and_rules, uks, explanations_by_planet, rule_history_by_planet)
        console.print(Panel.fit(f"[bold green]Visualizations complete![/bold green]\nSaved to: [cyan]{os.path.abspath('solar_system_knowledge_graph.png')}[/cyan]", title="[bold green]Visualization Saved[/bold green]"))
    except Exception as e:
        console.print(Panel.fit(f"[bold red]Error generating visualizations:[/bold red] {e}", title="[bold red]Visualization Error[/bold red]"))

    console.rule("[bold green]Enhanced Rule-Based Reasoning Demo Completed[/bold green]")

if __name__ == "__main__":
    main()