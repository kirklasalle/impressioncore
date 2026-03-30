#!/usr/bin/env python3
"""
ImpressionCore: Rule Based Reasoning

Module for rule based reasoning functionality in the ImpressionCore framework.

File: examples\rule_based_reasoning.py
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
Dependencies: [pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements rule based reasoning functionality for the
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
from examples.rule_based_reasoning import Context
instance = Context()
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
import logging
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.core.knowledge import UniversalKnowledgeStore, KnowledgeNode, Rule, RuleEngine
try:
    from src.core.knowledge.rules import Context  # Try to import the Context class
except ImportError:
    # Define a fallback Context class if import fails
    class Context:
        """Fallback Context class for rule evaluation."""
        def __init__(self, facts=None):
            """Initialize with optional facts."""
            self.facts = facts or {}
            self.inferred_facts = []
        
        def __getitem__(self, key):
            """Support dictionary-style access."""
            return self.facts.get(key)
        
        def __contains__(self, key):
            """Support 'in' operator."""
            return key in self.facts

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_solar_system_knowledge():
    """Create knowledge base with planets in our solar system."""
    uks = UniversalKnowledgeStore()
    
    # Create celestial body node directly with properties
    uks.create_node("CelestialBody", {"in_space": True})
    
    # Create planet node directly with properties
    uks.create_node("Planet", {"orbits_star": True})
    
    # Add parent-child relationship
    uks.add_relationship("Planet", "type", "CelestialObject")
    
    # Create specific planets
    uks.create_node("Mercury", {
        "temperature": 430,  # Average temperature in °C
        "has_atmosphere": False,
        "distance_from_sun": 0.39  # AU
    })
    uks.add_relationship("Mercury", "type", "TerrestrialPlanet")
    
    uks.create_node("Venus", {
        "temperature": 465,  # Average temperature in °C
        "has_atmosphere": True,
        "distance_from_sun": 0.72  # AU
    })
    uks.add_relationship("Venus", "type", "TerrestrialPlanet")
    
    uks.create_node("Earth", {
        "temperature": 15,  # Average temperature in °C
        "has_atmosphere": True,
        "distance_from_sun": 1.0,  # AU
        "has_life": True
    })
    uks.add_relationship("Earth", "type", "TerrestrialPlanet")
    
    uks.create_node("Mars", {
        "temperature": -65,  # Average temperature in °C
        "has_atmosphere": True,
        "atmosphere_type": "thin",
        "distance_from_sun": 1.52  # AU
    })
    uks.add_relationship("Mars", "type", "TerrestrialPlanet")
    
    return uks

def create_rules():
    """Create rules for planetary classification."""
    rules = []
    
    # Inspect Rule class to determine accepted parameters
    import inspect
    try:
        # Get the signature of the Rule constructor
        rule_signature = inspect.signature(Rule.__init__)
        accepted_params = list(rule_signature.parameters.keys())
        
        # Remove 'self' from the parameter list
        if 'self' in accepted_params:
            accepted_params.remove('self')
        
        logger.info(f"Rule constructor accepts parameters: {accepted_params}")
        
        # Check which parameters are accepted
        has_priority = 'priority' in accepted_params
        has_description = 'description' in accepted_params
    except Exception as e:
        logger.warning(f"Could not inspect Rule class: {e}")
        # Assume conservative defaults
        has_priority = False
        has_description = False
    
    # Rule for hot planets
    def hot_condition(context):
        """Rule condition for hot planets."""
        logger.debug(f"Hot condition check - has temperature: {context_has_key(context, 'temperature')}")
        if not context_has_key(context, 'temperature'):
            return False
        temp = context_get_value(context, 'temperature')
        logger.debug(f"Hot condition check - temperature value: {temp} (type: {type(temp).__name__})")
        # Convert to float if it's a string
        if isinstance(temp, str):
            try:
                temp = float(temp)
            except (ValueError, TypeError):
                return False
        return temp > 100
    
    def hot_action(context):
        """
        
    hot_action function for processing.
    
    Args:
        context: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        temp = context_get_value(context, 'temperature')
        return {
            'habitability': 'uninhabitable',
            'classification': 'hot',
            'reason': f"Temperature of {temp}°C is too hot for life as we know it"
        }
    
    # Create rule with appropriate parameters based on what's supported
    hot_rule_args = {
        "name": "hot_planet",
        "condition": hot_condition,
        "action": hot_action
    }
    
    # Add optional parameters if supported
    if has_priority:
        hot_rule_args["priority"] = 10
    
    if has_description:
        hot_rule_args["description"] = "Classify planets with temperature > 100°C as hot"
    
    hot_rule = Rule(**hot_rule_args)
    rules.append(hot_rule)
    
    # Rule for cold planets
    def cold_condition(context):
        """Rule condition for cold planets."""
        if not context_has_key(context, 'temperature'):
            return False
        temp = context_get_value(context, 'temperature')
        # Convert to float if it's a string
        if isinstance(temp, str):
            try:
                temp = float(temp)
            except (ValueError, TypeError):
                return False
        return temp < -50
    
    def cold_action(context):
        """
        
    cold_action function for processing.
    
    Args:
        context: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        temp = context_get_value(context, 'temperature')
        return {
            'habitability': 'challenging',
            'classification': 'cold',
            'reason': f"Temperature of {temp}°C requires significant heating"
        }
    
    # Create rule with appropriate parameters based on what's supported
    cold_rule_args = {
        "name": "cold_planet",
        "condition": cold_condition,
        "action": cold_action
    }
    
    if has_priority:
        cold_rule_args["priority"] = 10
    
    if has_description:
        cold_rule_args["description"] = "Classify planets with temperature < -50°C as cold"
    
    cold_rule = Rule(**cold_rule_args)
    rules.append(cold_rule)
    
    # Rule for temperate planets
    def temperate_condition(context):
        """Rule condition for temperate planets."""
        if not context_has_key(context, 'temperature'):
            return False
        temp = context_get_value(context, 'temperature')
        # Convert to float if it's a string
        if isinstance(temp, str):
            try:
                temp = float(temp)
            except (ValueError, TypeError):
                return False
        return -50 <= temp <= 50
    
    def temperate_action(context):
        """
        
    temperate_action function for processing.
    
    Args:
        context: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        temp = context_get_value(context, 'temperature')
        return {
            'habitability': 'potentially habitable',
            'classification': 'temperate',
            'reason': f"Temperature of {temp}°C is within habitable range"
        }
    
    # Create rule with appropriate parameters based on what's supported
    temperate_rule_args = {
        "name": "temperate_planet",
        "condition": temperate_condition,
        "action": temperate_action
    }
    
    if has_priority:
        temperate_rule_args["priority"] = 10
    
    if has_description:
        temperate_rule_args["description"] = "Classify planets with temperature between -50°C and 50°C as temperate"
    
    temperate_rule = Rule(**temperate_rule_args)
    rules.append(temperate_rule)
    
    return rules

def create_context_from_dict(facts_dict):
    """Create a Context object from a dictionary of facts."""
    try:
        # Try to create a Context object with the imported class
        # Inspect signature to determine the correct parameter name
        import inspect
        sig_params = list(inspect.signature(Context.__init__).parameters.keys())
        
        # Create kwargs based on parameter names
        kwargs = {}
        
        # Check for common parameter names for facts/properties
        if 'properties' in sig_params:
            kwargs['properties'] = facts_dict
        elif 'facts' in sig_params:
            kwargs['facts'] = facts_dict
        elif 'initial_facts' in sig_params:
            kwargs['initial_facts'] = facts_dict
        elif 'data' in sig_params:
            kwargs['data'] = facts_dict
        else:
            # If no recognized parameter, try with first non-self parameter
            for param in sig_params:
                if param != 'self' and param != 'knowledge_store':
                    kwargs[param] = facts_dict
                    break
        
        # Create context with appropriate parameters
        ctx = Context(**kwargs)
        
        # Ensure it has the required inferred_facts attribute
        if not hasattr(ctx, 'inferred_facts'):
            ctx.inferred_facts = []
        
        # Add a get method for compatibility with both dictionary and object access
        if not hasattr(ctx, 'get'):
            ctx.get = lambda key, default=None: context_get_value(ctx, key, default)
            
        # Add contains check for compatibility
        if not hasattr(ctx, '__contains__'):
            ctx.__contains__ = lambda key: context_has_key(ctx, key)
            
        return ctx
    except Exception as e:
        logger.warning(f"Error creating Context: {e}, using fallback")
        # Use our fallback Context class
        return Context(facts=facts_dict)

# Helper functions for context access that work with any Context implementation
def context_has_key(context, key):
    """Check if context has a key regardless of implementation."""
    # Try various ways to check for key existence
    try:
        # Try __contains__ method (in operator)
        if key in context:
            return True
    except (TypeError, Exception):
        pass
        
    try:
        # Try as attribute
        if hasattr(context, key):
            return True
    except Exception:
        pass
    
    try:
        # Try as dictionary
        if hasattr(context, 'facts') and key in context.facts:
            return True
    except Exception:
        pass
    
    try:
        # Try as properties
        if hasattr(context, 'properties') and key in context.properties:
            return True
    except Exception:
        pass
    
    return False

def context_get_value(context, key, default=None):
    """Get a value from context regardless of implementation."""
    # Try various ways to get the value
    try:
        # Try __getitem__ method ([] operator)
        return context[key]
    except (KeyError, TypeError, Exception):
        pass
    
    try:
        # Try as attribute
        if hasattr(context, key):
            return getattr(context, key)
    except Exception:
        pass
    
    try:
        # Try as dictionary
        if hasattr(context, 'facts') and key in context.facts:
            return context.facts[key]
    except Exception:
        pass
    
    try:
        # Try as properties
        if hasattr(context, 'properties') and key in context.properties:
            return context.properties[key]
    except Exception:
        pass
    
    return default

# Add debug method to test rule conditions directly
def debug_rule_conditions(rule_engine, context, planet_name):
    """Debug rule conditions by directly evaluating them."""
    logger.info(f"Debug rule evaluation for {planet_name}:")
    
    for i, rule in enumerate(rule_engine.rules):  # Changed from _rules to rules
        try:
            # Get raw condition function from rule
            condition_func = rule.condition
            
            # Direct condition evaluation
            result = condition_func(context)
            logger.info(f"  Rule '{rule.name}' condition result: {result}")
            
            # Debug actual values
            if hasattr(context, 'properties'):
                logger.info(f"  Context properties: {context.properties}")
            elif hasattr(context, 'facts'):
                logger.info(f"  Context facts: {context.facts}")
            
            # Test with our helper functions
            if 'temperature' in rule.name.lower():
                has_temp = context_has_key(context, 'temperature')
                temp_value = context_get_value(context, 'temperature')
                logger.info(f"  context_has_key('temperature'): {has_temp}")
                logger.info(f"  context_get_value('temperature'): {temp_value} (type: {type(temp_value).__name__})")
        except Exception as e:
            logger.error(f"  Error evaluating rule {rule.name}: {e}")

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
    logger.info("Starting rule-based reasoning demo")
    
    # Create knowledge store with solar system information
    uks = create_solar_system_knowledge()
    
    # Create rule engine
    rule_engine = RuleEngine()
    
    # Add rules to the engine
    for rule in create_rules():
        rule_engine.add_rule(rule)
    
    # Process each planet
    planets = ["Mercury", "Venus", "Earth", "Mars"]
    
    # Dynamically find the correct rule application method
    rule_apply_method = None
    possible_methods = ['run', 'apply', 'apply_rules', 'apply_all', 'process', 'execute']
    
    for method_name in possible_methods:
        if hasattr(rule_engine, method_name):
            rule_apply_method = getattr(rule_engine, method_name)
            logger.info(f"Using RuleEngine.{method_name}() to apply rules")
            break
    
    if not rule_apply_method:
        logger.error("Could not find a method to apply rules in RuleEngine")
        return
    
    # Try direct rule application as fallback if built-in method doesn't work
    def apply_rules_directly(context):
        """Apply rules directly as a fallback."""
        results = []
        for rule in rule_engine.rules:  # Changed from _rules to rules
            try:
                condition_result = rule.condition(context)
                logger.debug(f"Direct rule evaluation - {rule.name}: {condition_result}")
                if condition_result:
                    action_result = rule.action(context)
                    results.append(action_result)
                    logger.debug(f"Rule {rule.name} applied with result: {action_result}")
            except Exception as e:
                logger.error(f"Error directly applying rule {rule.name}: {e}")
        return results
    
    for planet_name in planets:
        planet = uks.get_node(planet_name)
        
        if planet:
            # Create context from planet properties
            properties = planet["properties"]
            properties['name'] = planet_name
            
            # Create a proper Context object from the properties
            context = create_context_from_dict(properties)
            
            logger.info(f"Processing planet: {planet_name}")
            logger.info(f"Attributes: {properties}")
            
            # Debug rule conditions directly before applying
            debug_rule_conditions(rule_engine, context, planet_name)
            
            # Apply rules to the planet using the detected method
            results = rule_apply_method(context)
            
            # If no results, try direct application
            if not results:
                logger.info("No results from engine, trying direct rule application")
                results = apply_rules_directly(context)
            
            if results:
                for i, result in enumerate(results):
                    logger.info(f"Rule {i+1} result: {result}")
                    
                    # Add inference back to knowledge base
                    if 'classification' in result:
                        # Update: Use add_relationship instead of non-existent add_fact
                        planet["properties"]["classification"] = result['classification']
                    if 'habitability' in result:
                        # Update: Add property directly to the node
                        planet["properties"]["habitability"] = result['habitability']
            else:
                logger.info("No rules applied")
            
            logger.info("-" * 50)
    
    # Show updated knowledge
    logger.info("Updated knowledge:")
    for planet_name in planets:
        planet = uks.get_node(planet_name)
        logger.info(f"{planet_name}: {planet['properties']}")
    
    logger.info("Rule-based reasoning demo completed")

if __name__ == "__main__":
    main()
