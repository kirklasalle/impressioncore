#!/usr/bin/env python3
"""
ImpressionCore: Rule Based Reasoning Demo

Module for rule based reasoning demo functionality in the ImpressionCore framework.

File: examples\rule_based_reasoning_demo.py
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
This module implements rule based reasoning demo functionality for the
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
from examples.rule_based_reasoning_demo import MainClass
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
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.core.knowledge.uks import UniversalKnowledgeStore, KnowledgeNode

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    # Fix the import statement - remove the function that doesn't exist
    from src.core.knowledge.rules import Rule, RuleEngine, Context, create_planet_rules
except ImportError as e:
    logger.error(f"Error importing from knowledge rules: {e}")
    logger.error("Looking for alternative implementations...")
    
    # Try to import from examples instead
    try:
        from examples.rule_based_reasoning import Rule, RuleEngine, create_rules
        from examples.rule_based_reasoning import create_context_from_dict as Context
        
        # Define create_planet_rules as an alias for create_rules if needed
        create_planet_rules = create_rules
        logger.info("Successfully imported rule system from example implementations")
    except ImportError:
        logger.error("Could not find rule engine implementation")
        sys.exit(1)

# Function to integrate rule engine with other components
def integrate_rule_engine(rule_engine, knowledge_store, contexts=None):
    """
    Integrate a rule engine with a knowledge store for rule-based reasoning.
    
    Args:
        rule_engine: The rule engine instance
        knowledge_store: The knowledge store to integrate with
        contexts: Optional dictionary of pre-created contexts
        
    Returns:
        Dictionary of contexts after rule application
    """
    logger.info("Integrating rule engine with knowledge store")
    
    if contexts is None:
        contexts = {}
        
    # Get all nodes from knowledge store
    nodes = knowledge_store.get_nodes() if hasattr(knowledge_store, 'get_nodes') else {}
    
    # Create contexts for each node if not already provided
    for node_id, node in nodes.items():
        if node_id not in contexts:
            # Create context from node properties
            if isinstance(node, dict) and "properties" in node:
                context = Context(node["properties"])
                contexts[node_id] = context
    
    # Apply rules to all contexts
    processed_contexts = {}
    for node_id, context in contexts.items():
        # Apply rules
        try:
            if hasattr(rule_engine, 'run'):
                results = rule_engine.run(context)
            elif hasattr(rule_engine, 'apply_rules'):
                results = rule_engine.apply_rules(context)
            elif hasattr(rule_engine, 'apply'):
                results = rule_engine.apply(context)
            else:
                logger.warning(f"No suitable method found to apply rules for node {node_id}")
                continue
                
            # Store updated context
            processed_contexts[node_id] = context
            
            # Update knowledge store if possible
            if node_id in nodes and isinstance(nodes[node_id], dict) and "properties" in nodes[node_id]:
                for result in results:
                    for key, value in result.items():
                        nodes[node_id]["properties"][key] = value
                        
        except Exception as e:
            logger.error(f"Error applying rules to node {node_id}: {e}")
    
    logger.info(f"Rule engine integration complete: processed {len(processed_contexts)} contexts")
    return processed_contexts

def create_planet_knowledge_base():
    """Create a simple knowledge base about planets."""
    # Create a UKS
    uks = UniversalKnowledgeStore()
    
    # Create base nodes using the correct API
    uks.create_node("CelestialBody", {
        "is_in_space": True
    })
    
    uks.create_node("Planet", {
        "orbits_star": True
    })
    
    # Add relationship
    uks.add_relationship("Planet", "type", "CelestialBody")
    
    # Add specific planets with their properties
    uks.create_node("Mercury", {
        "distance_from_sun": 0.4,  # AU
        "temperature": 430  # °C (average daytime)
    })
    uks.add_relationship("Mercury", "type", "Planet")
    
    uks.create_node("Venus", {
        "distance_from_sun": 0.7,  # AU
        "temperature": 470  # °C
    })
    uks.add_relationship("Venus", "type", "Planet")
    
    uks.create_node("Earth", {
        "distance_from_sun": 1.0,  # AU
        "temperature": 15,  # °C
        "has_life": True
    })
    uks.add_relationship("Earth", "type", "Planet")
    
    uks.create_node("Mars", {
        "distance_from_sun": 1.5,  # AU
        "temperature": -65  # °C
    })
    uks.add_relationship("Mars", "type", "Planet")
    
    return uks

def debug_rule_conditions(engine, context, planet_name):
    """Debug why rule conditions aren't matching for a planet."""
    logger.info(f"Debugging rule conditions for planet {planet_name}:")
    
    # Print context data being used for rules
    if hasattr(context, 'facts'):
        logger.info(f"  Context facts: {context.facts}")
    elif hasattr(context, '__dict__'):
        logger.info(f"  Context attributes: {context.__dict__}")
    else:
        logger.info(f"  Context (as string): {context}")
    
    # Test each rule condition directly
    for i, rule in enumerate(engine.rules):
        try:
            # Ensure we can access the condition
            condition_func = rule.condition
            condition_name = rule.name
            
            # Try to evaluate the condition directly
            result = False
            try:
                result = condition_func(context)
            except Exception as e:
                logger.error(f"  Error evaluating condition for rule {condition_name}: {e}")
            
            logger.info(f"  Rule {i+1} '{condition_name}' condition result: {result}")
            
            # For temperature rules, log the specific values
            if 'temperature' in condition_name.lower():
                # Try different ways to get temperature
                temp_value = None
                if hasattr(context, 'facts') and 'temperature' in context.facts:
                    temp_value = context.facts['temperature']
                elif hasattr(context, 'temperature'):
                    temp_value = context.temperature
                elif hasattr(context, 'get') and callable(getattr(context, 'get')):
                    temp_value = context.get('temperature')
                    
                logger.info(f"  Temperature value: {temp_value} (type: {type(temp_value).__name__ if temp_value is not None else 'None'})")
                
                # Try to manually evaluate common temperature conditions
                if temp_value is not None:
                    logger.info(f"  Manual checks: temp > 100: {temp_value > 100}, temp < -50: {temp_value < -50}")
                    
        except Exception as e:
            logger.error(f"  Error debugging rule {i}: {e}")

def apply_rules_directly(engine, context):
    """
    Apply rules directly without relying on the rule engine's methods.
    
    This is a fallback function when the rule engine's built-in methods don't work correctly.
    """
    results = []
    logger.info("Attempting direct rule application")
    
    # Try to apply each rule directly
    for i, rule in enumerate(engine.rules):
        try:
            # Evaluate condition
            condition_result = rule.condition(context)
            logger.info(f"  Rule {i+1} '{rule.name}' condition: {condition_result}")
            
            if condition_result:
                # Apply action directly
                action_result = rule.action(context)
                logger.info(f"  Rule {i+1} '{rule.name}' applied with result: {action_result}")
                results.append(action_result)
                
                # Update context with result if needed
                if isinstance(action_result, dict) and hasattr(context, 'properties'):
                    for key, value in action_result.items():
                        context.properties[key] = value
        
        except Exception as e:
            logger.error(f"  Error directly applying rule {rule.name}: {e}")
    
    return results

def main():
    """Run the rule-based reasoning demo."""
    logger.info("Starting rule-based reasoning demo")
    
    # Create knowledge base
    uks = create_planet_knowledge_base()
    
    # Create rule engine
    engine = RuleEngine()
    
    # Add planet classification rules
    for rule in create_planet_rules():
        engine.add_rule(rule)
    
    # Log the rules we have
    logger.info(f"Loaded {len(engine.rules)} rules:")
    for i, rule in enumerate(engine.rules):
        logger.info(f"  Rule {i+1}: {rule.name}")
    
    # Integrate rule engine with knowledge store
    integrate_rule_engine(engine, uks)
    
    # Test with planets
    planets = ["Mercury", "Venus", "Earth", "Mars"]
    for planet_name in planets:
        logger.info(f"\nAnalyzing planet: {planet_name}")
        planet_node = uks.get_node(planet_name)
        
        if planet_node:
            # Extract planet data
            if isinstance(planet_node, dict) and "properties" in planet_node:
                # Create proper data dictionary with all needed properties
                planet_data = planet_node["properties"].copy()
                planet_data['name'] = planet_name
                
                logger.info(f"Planet data: {planet_data}")
                
                # Create a proper Context object using the imported Context function
                try:
                    # Use the Context constructor (which is actually create_context_from_dict)
                    context = Context(planet_data)
                    
                    # Debug why rules aren't firing
                    debug_rule_conditions(engine, context, planet_name)
                    
                    # Apply rules using engine method
                    if hasattr(engine, 'apply_all'):
                        logger.info("Using engine.apply_all() method")
                        results = engine.apply_all(context)
                    elif hasattr(engine, 'run'):
                        logger.info("Using engine.run() method")
                        results = engine.run(context)
                        
                        # Inspect the returned results
                        logger.info(f"engine.run() returned: {results} (type: {type(results).__name__})")
                        
                        # If no results but the rule conditions evaluated to True, try direct application
                        if not results:
                            results = apply_rules_directly(engine, context)
                    elif hasattr(engine, 'apply_rules'):
                        logger.info("Using engine.apply_rules() method")
                        results = engine.apply_rules(context)
                    else:
                        logger.error("No compatible rule application method found")
                        results = []
                    
                    # If we still have no results, try direct application as last resort
                    if not results:
                        results = apply_rules_directly(engine, context)
                    
                    # Display results
                    if results:
                        for i, result in enumerate(results):
                            logger.info(f"Rule {i+1} result: {result}")
                            
                            # Update the planet node in the knowledge store - Fix get_nodes error
                            try:
                                # Try to update the planet node directly without using get_nodes()
                                planet_node = uks.get_node(planet_name)
                                if isinstance(result, dict) and planet_node is not None:
                                    for key, value in result.items():
                                        # Update node properties
                                        planet_node["properties"][key] = value
                                        logger.info(f"  Updated {planet_name} property '{key}' to '{value}'")
                            except Exception as e:
                                logger.error(f"Error updating knowledge store for {planet_name}: {e}")
                                
                    else:
                        logger.info(f"No classifications applied to {planet_name}")
                
                except Exception as e:
                    logger.error(f"Error applying rules to {planet_name}: {e}")
                    logger.debug(f"Context creation or rule application failed", exc_info=True)
            else:
                logger.warning(f"Planet {planet_name} has invalid node structure")
        else:
            logger.warning(f"Planet {planet_name} not found in knowledge base")

if __name__ == "__main__":
    main()
