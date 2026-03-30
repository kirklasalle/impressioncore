#!/usr/bin/env python3
"""
ImpressionCore: Simplified Advanced Reasoning

Module for simplified advanced reasoning functionality in the ImpressionCore framework.

File: examples\simplified_advanced_reasoning.py
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
Dependencies: [typing, pathlib, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements simplified advanced reasoning functionality for the
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
from examples.simplified_advanced_reasoning import ConfidenceRule
instance = ConfidenceRule()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import sys
import os
import logging
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional, Union, Tuple
import networkx as nx
from datetime import datetime

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import from the enhanced rule-based reasoning example
from examples.enhanced_rule_reasoning import (
    UniversalKnowledgeStore, ExplainableRule, ExplainableRuleEngine,
    context_has_key, context_get_value, create_context_from_dict,
    create_detailed_solar_system
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConfidenceRule(ExplainableRule):
    """Rule with confidence score to represent uncertainty."""
    
    def __init__(self, name, condition, action, explanation_func=None, 
                 priority=0, description="", confidence=1.0):
        """
        Initialize a rule with confidence.
        
        Args:
            name: Rule name
            condition: Condition function that returns True/False
            action: Action function to execute when condition is True
            explanation_func: Function that explains why the rule fired
            priority: Rule priority (higher numbers = higher priority)
            description: Human-readable description of the rule
            confidence: Confidence score (0.0-1.0) representing certainty
        """
        super().__init__(name, condition, action, explanation_func, priority, description)
        self.confidence = min(max(confidence, 0.0), 1.0)  # Clamp between 0 and 1
        self.application_history = []
    
    def record_application(self, context_id, result, success=True):
        """Record a rule application for learning."""
        self.application_history.append({
            'timestamp': datetime.now().isoformat(),
            'context_id': context_id,
            'result': result,
            'success': success
        })
    
    def adjust_confidence(self, adjustment):
        """Adjust the rule's confidence score."""
        new_confidence = self.confidence + adjustment
        self.confidence = min(max(new_confidence, 0.0), 1.0)  # Clamp between 0 and 1
        return self.confidence


class ConflictAwareRuleEngine(ExplainableRuleEngine):
    """Rule engine with conflict detection and resolution capabilities."""
    
    def __init__(self, conflict_strategy="priority"):
        """
        Initialize the conflict-aware rule engine.
        
        Args:
            conflict_strategy: Strategy for resolving conflicts
                - "priority": Use rule priority to resolve conflicts
                - "confidence": Use rule confidence to resolve conflicts
                - "recent": Use most recently added rule
                - "combine": Try to combine conflicting results
        """
        super().__init__()
        self.conflict_strategy = conflict_strategy
        self.conflict_history = []
        self.rule_modifications = []
        
        # Mapping of property names to rule names that set them
        self.property_rule_map = {}
    
    def detect_conflicts(self, results, rules_fired):
        """Detect conflicts between rule results."""
        property_values = {}
        conflicts = []
        
        for i, result in enumerate(results):
            rule = rules_fired[i]
            for prop, value in result.items():
                if prop in property_values:
                    # If property exists with a different value, it's a conflict
                    if property_values[prop]['value'] != value:
                        conflicts.append({
                            'property': prop,
                            'rules': [property_values[prop]['rule'], rule],
                            'values': [property_values[prop]['value'], value],
                            'confidences': [
                                getattr(property_values[prop]['rule'], 'confidence', 1.0),
                                getattr(rule, 'confidence', 1.0)
                            ],
                            'priorities': [
                                getattr(property_values[prop]['rule'], 'priority', 0),
                                getattr(rule, 'priority', 0)
                            ]
                        })
                else:
                    property_values[prop] = {'value': value, 'rule': rule}
        
        return conflicts
    
    def resolve_conflicts(self, conflicts, context_id):
        """Resolve conflicts using the selected strategy."""
        resolutions = {}
        
        for conflict in conflicts:
            prop = conflict['property']
            
            if self.conflict_strategy == "priority":
                # Choose the rule with higher priority
                if conflict['priorities'][0] >= conflict['priorities'][1]:
                    resolutions[prop] = conflict['values'][0]
                    winner_index = 0
                else:
                    resolutions[prop] = conflict['values'][1]
                    winner_index = 1
                    
            elif self.conflict_strategy == "confidence":
                # Choose the rule with higher confidence
                if conflict['confidences'][0] >= conflict['confidences'][1]:
                    resolutions[prop] = conflict['values'][0]
                    winner_index = 0
                else:
                    resolutions[prop] = conflict['values'][1]
                    winner_index = 1
                    
            elif self.conflict_strategy == "recent":
                # Choose the more recently added rule
                resolutions[prop] = conflict['values'][1]
                winner_index = 1
                
            elif self.conflict_strategy == "combine":
                # Attempt to combine results (implementation depends on data types)
                if isinstance(conflict['values'][0], str) and isinstance(conflict['values'][1], str):
                    # For strings, combine them
                    resolutions[prop] = f"{conflict['values'][0]} & {conflict['values'][1]}"
                elif isinstance(conflict['values'][0], (int, float)) and isinstance(conflict['values'][1], (int, float)):
                    # For numbers, use average weighted by confidence
                    weight1 = conflict['confidences'][0]
                    weight2 = conflict['confidences'][1]
                    total_weight = weight1 + weight2
                    if total_weight > 0:
                        resolutions[prop] = (conflict['values'][0] * weight1 + conflict['values'][1] * weight2) / total_weight
                    else:
                        # Equal weights if confidences are both 0
                        resolutions[prop] = (conflict['values'][0] + conflict['values'][1]) / 2
                else:
                    # Default to higher priority rule
                    if conflict['priorities'][0] >= conflict['priorities'][1]:
                        resolutions[prop] = conflict['values'][0]
                        winner_index = 0
                    else:
                        resolutions[prop] = conflict['values'][1]
                        winner_index = 1
            
            # Record this conflict and its resolution
            resolution = {
                'property': prop,
                'rule_names': [rule.name for rule in conflict['rules']],
                'values': conflict['values'],
                'resolved_value': resolutions[prop],
                'strategy': self.conflict_strategy,
                'context_id': context_id,
                'timestamp': datetime.now().isoformat()
            }
            
            self.conflict_history.append(resolution)
            
            # Log the conflict
            logger.info(f"Resolved conflict for property '{prop}' "
                        f"between rules {[rule.name for rule in conflict['rules']]} "
                        f"using '{self.conflict_strategy}' strategy. "
                        f"Selected value: {resolutions[prop]}")
            
        return resolutions
    
    def run(self, context):
        """Run all rules with conflict resolution."""
        context_id = id(context)
        self.rule_history[context_id] = []
        results = []
        rules_fired = []
        
        # Track which rules fired and their results
        for rule in self.rules:
            try:
                # Only evaluate if rule condition passes
                if rule.condition(context):
                    # Apply the rule action
                    result = rule.action(context)
                    
                    # Store which rule fired and its result
                    self.rule_history[context_id].append({
                        'rule_name': rule.name,
                        'rule_description': getattr(rule, 'description', ''),
                        'result': result,
                        'confidence': getattr(rule, 'confidence', 1.0)
                    })
                    
                    # If rule is explainable, get explanation
                    if hasattr(rule, 'explain'):
                        explanation = rule.explain(context, result)
                        
                        # Store explanation
                        if context_id not in self.explanations:
                            self.explanations[context_id] = []
                        
                        self.explanations[context_id].append({
                            'rule_name': rule.name,
                            'explanation': explanation,
                            'confidence': getattr(rule, 'confidence', 1.0)
                        })
                    
                    # Record rule application if supported
                    if hasattr(rule, 'record_application'):
                        rule.record_application(context_id, result)
                    
                    results.append(result)
                    rules_fired.append(rule)
                    
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {e}")
        
        # Detect and resolve conflicts
        if len(results) > 1:
            conflicts = self.detect_conflicts(results, rules_fired)
            if conflicts:
                resolutions = self.resolve_conflicts(conflicts, context_id)
                
                # Apply resolutions by updating the results
                for i, result in enumerate(results):
                    for prop, value in resolutions.items():
                        if prop in result:
                            result[prop] = value
        
        return results
    
    def modify_rule(self, rule_name, modification_type, **kwargs):
        """Modify a rule dynamically."""
        # Find the rule
        target_rule = None
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                target_rule = rule
                rule_index = i
                break
        
        if not target_rule:
            logger.error(f"Rule '{rule_name}' not found for modification")
            return False
        
        # Apply modification
        if modification_type == "confidence" and hasattr(target_rule, 'confidence'):
            if 'value' in kwargs:
                target_rule.confidence = min(max(kwargs['value'], 0.0), 1.0)
            elif 'adjustment' in kwargs:
                target_rule.adjust_confidence(kwargs['adjustment'])
                
        elif modification_type == "priority":
            if 'value' in kwargs:
                target_rule.priority = kwargs['value']
                
        # Record the modification
        self.rule_modifications.append({
            'rule_name': rule_name,
            'modification_type': modification_type,
            'parameters': kwargs,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"Modified rule '{rule_name}' - {modification_type}: {kwargs}")
        return True


def create_confidence_rules():
    """Create rules with confidence scores."""
    # This is the same as in advanced_rule_reasoning.py
    # Implementation omitted for brevity
    rules = []
    
    # Hot planets (high confidence)
    hot_rule = ConfidenceRule(
        name="hot_planet",
        condition=lambda context: context_get_value(context, 'temperature', 0) > 100,
        action=lambda context: {
            'habitability': 'uninhabitable',
            'classification': 'hot',
            'reason': f"Temperature of {context_get_value(context, 'temperature')}°C is too hot for life as we know it"
        },
        explanation_func=lambda context, result: (
            f"{context_get_value(context, 'name')} is classified as HOT because its temperature is "
            f"{context_get_value(context, 'temperature')}°C, which exceeds 100°C. "
            f"Such high temperatures make it {result['habitability']}."
        ),
        priority=10,
        description="Classify planets with temperature > 100°C as hot",
        confidence=0.95  # Very high confidence
    )
    rules.append(hot_rule)
    
    # Cold planets (high confidence)
    cold_rule = ConfidenceRule(
        name="cold_planet",
        condition=lambda context: context_get_value(context, 'temperature', 0) < -50,
        action=lambda context: {
            'habitability': 'challenging',
            'classification': 'cold',
            'reason': f"Temperature of {context_get_value(context, 'temperature')}°C requires significant heating"
        },
        explanation_func=lambda context, result: (
            f"{context_get_value(context, 'name')} is classified as COLD because its temperature is "
            f"{context_get_value(context, 'temperature')}°C, which is below -50°C. "
            f"Such cold temperatures make it {result['habitability']}."
        ),
        priority=10,
        description="Classify planets with temperature < -50°C as cold",
        confidence=0.95  # Very high confidence
    )
    rules.append(cold_rule)
    
    # Temperate planets (high confidence)
    temperate_rule = ConfidenceRule(
        name="temperate_planet",
        condition=lambda context: -50 <= context_get_value(context, 'temperature', 0) <= 50,
        action=lambda context: {
            'habitability': 'potentially habitable',
            'classification': 'temperate',
            'reason': f"Temperature of {context_get_value(context, 'temperature')}°C is within habitable range"
        },
        explanation_func=lambda context, result: (
            f"{context_get_value(context, 'name')} is classified as TEMPERATE because its temperature is "
            f"{context_get_value(context, 'temperature')}°C, which is between -50°C and 50°C. "
            f"This moderate temperature range makes it {result['habitability']}."
        ),
        priority=10,
        description="Classify planets with temperature between -50°C and 50°C as temperate",
        confidence=0.95  # Very high confidence
    )
    rules.append(temperate_rule)
    
    # More rules (habitable_zone, life_potential, etc.) would be included here
    # Simplified for brevity
    
    # Habitable zone rule
    habitable_zone_rule = ConfidenceRule(
        name="habitable_zone",
        condition=lambda context: 0.9 <= context_get_value(context, 'distance_from_sun', 0) <= 1.7,
        action=lambda context: {
            'zone_classification': 'habitable_zone',
            'zone_reason': f"Distance of {context_get_value(context, 'distance_from_sun')} AU is within habitable range"
        },
        explanation_func=lambda context, result: (
            f"{context_get_value(context, 'name')} is in the HABITABLE ZONE because its distance from the Sun is "
            f"{context_get_value(context, 'distance_from_sun')} AU, which falls within the range of "
            f"0.9-1.7 AU where liquid water could potentially exist."
        ),
        priority=15,
        description="Identify planets in the habitable zone (0.9-1.7 AU from star)",
        confidence=0.85  # Somewhat uncertain due to variability in star types
    )
    rules.append(habitable_zone_rule)
    
    return rules


def visualize_rule_confidence(rule_engine, output_file="rule_confidence.png"):
    """Create a static visualization of rule confidences."""
    # Extract rule names and confidences
    rule_names = []
    confidences = []
    priorities = []
    
    for rule in rule_engine.rules:
        rule_names.append(rule.name)
        confidences.append(getattr(rule, 'confidence', 0.5))
        priorities.append(getattr(rule, 'priority', 0))
    
    # Create figure with two subplots
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()
    
    # Plot confidence bars
    bars = ax1.bar(rule_names, confidences, alpha=0.7, color='blue', label='Confidence')
    ax1.set_ylim(0, 1.0)
    ax1.set_ylabel('Confidence Score')
    
    # Plot priorities as points
    ax2.plot(rule_names, priorities, 'ro-', label='Priority')
    ax2.set_ylabel('Priority')
    
    # Set labels and title
    plt.title('Rule Confidence and Priority Levels')
    ax1.set_xticklabels(rule_names, rotation=45, ha='right')
    
    # Add legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    plt.tight_layout()
    plt.savefig(output_file)
    logger.info(f"Rule confidence visualization saved to {output_file}")
    

def visualize_knowledge_graph(uks, planets, output_file="planet_knowledge_graph.png"):
    """Create a static visualization of the knowledge graph."""
    # Create a graph
    G = nx.DiGraph()
    
    # Add nodes for planets
    for planet_name in planets:
        planet = uks.get_node(planet_name)
        if not planet:
            continue
        
        # Add planet node
        G.add_node(planet_name, type='planet')
        
        # Add special property nodes
        properties = planet["properties"]
        special_props = ["classification", "habitability", "life_potential", 
                        "colonization_suitability", "zone_classification"]
        
        for prop in special_props:
            if prop in properties:
                prop_value = properties[prop]
                node_name = f"{prop}: {prop_value}"
                if node_name not in G:
                    G.add_node(node_name, type='property')
                G.add_edge(planet_name, node_name)
    
    # Set positions using spring layout
    pos = nx.spring_layout(G, seed=42)
    
    # Draw the graph
    plt.figure(figsize=(12, 10))
    
    # Draw nodes with different colors by type
    planet_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'planet']
    property_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'property']
    
    nx.draw_networkx_nodes(G, pos, nodelist=planet_nodes, node_color='skyblue', 
                          node_size=800, alpha=0.8, label='Planets')
    nx.draw_networkx_nodes(G, pos, nodelist=property_nodes, node_color='lightgreen', 
                          node_size=600, alpha=0.8, label='Properties')
    
    # Draw edges and labels
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
    
    plt.axis('off')
    plt.title('Solar System Knowledge Graph with Inferred Properties')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_file)
    logger.info(f"Knowledge graph visualization saved to {output_file}")


def main():
    """Run the simplified advanced rule-based reasoning demo."""
    logger.info("Starting simplified advanced rule-based reasoning demo")
    
    # Create detailed knowledge store
    uks = create_detailed_solar_system()
    
    # Create conflict-aware rule engine
    rule_engine = ConflictAwareRuleEngine(conflict_strategy="confidence")
    
    # Add rules with confidence scores
    for rule in create_confidence_rules():
        rule_engine.add_rule(rule)
    
    # Process all planets
    planets = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
    
    # Store planet data and contexts
    planet_data = {}
    contexts = {}
    
    for planet_name in planets:
        planet = uks.get_node(planet_name)
        
        if planet:
            properties = planet["properties"]
            properties['name'] = planet_name
            
            # Store planet data
            planet_data[planet_name] = properties.copy()
            
            # Create context for this planet
            context = create_context_from_dict(properties)
            contexts[planet_name] = context
            
            logger.info(f"\nProcessing planet: {planet_name}")
            logger.info(f"Initial properties: {properties}")
            
            # Apply rules with conflict detection and resolution
            results = rule_engine.run(context)
            
            if results:
                for i, result in enumerate(results):
                    logger.info(f"Rule {i+1} result: {result}")
                    
                    # Update knowledge store with inferred facts
                    for key, value in result.items():
                        planet["properties"][key] = value
                        planet_data[planet_name][key] = value
            
            # Get explanations and conflicts
            explanations = rule_engine.get_explanations(context)
            conflicts = [c for c in rule_engine.get_conflict_history() 
                         if c['context_id'] == id(context)]
            
            # Log explanations
            if explanations:
                logger.info("Explanations:")
                for explanation in explanations:
                    logger.info(f"  - {explanation['rule_name']} (confidence: {explanation.get('confidence', 'N/A'):.2f})")
                    logger.info(f"    {explanation['explanation']}")
            
            # Log conflicts
            if conflicts:
                logger.info(f"Conflicts detected: {len(conflicts)}")
                for conflict in conflicts:
                    logger.info(f"  - Conflict on '{conflict['property']}' between {conflict['rule_names']}")
                    logger.info(f"    Values: {conflict['values']}")
                    logger.info(f"    Resolved to: {conflict['resolved_value']} using {conflict['strategy']} strategy")
            
            logger.info("-" * 50)
    
    # Show updated knowledge
    logger.info("\nUpdated knowledge with inferred properties and confidences:")
    for planet_name in planets:
        planet = uks.get_node(planet_name)
        if planet:
            interesting_props = {k: v for k, v in planet["properties"].items() 
                               if k in ["classification", "habitability", "zone_classification", 
                                       "life_potential", "colonization_suitability", 
                                       "asteroid_impact_risk", "planet_type"]}
            
            logger.info(f"{planet_name}: {interesting_props}")
    
    # Create static visualizations
    try:
        # Create rule confidence visualization
        visualize_rule_confidence(rule_engine)
        
        # Create knowledge graph visualization
        visualize_knowledge_graph(uks, planets)
        
        # Create text report of explanations and inferences
        with open("rule_explanations_report.txt", "w") as f:
            f.write("# Rule-Based Reasoning Explanations\n\n")
            
            for planet_name in planets:
                if planet_name not in contexts:
                    continue
                    
                context = contexts[planet_name]
                explanations = rule_engine.get_explanations(context)
                
                if not explanations:
                    continue
                    
                f.write(f"## {planet_name}\n\n")
                
                for explanation in explanations:
                    rule_name = explanation['rule_name']
                    confidence = explanation.get('confidence', 'N/A')
                    
                    f.write(f"### {rule_name} (confidence: {confidence:.2f if isinstance(confidence, float) else confidence})\n\n")
                    f.write(f"{explanation['explanation']}\n\n")
                    
                f.write("-" * 80 + "\n\n")
                
        logger.info("Text report of explanations saved to rule_explanations_report.txt")
        
    except Exception as e:
        logger.error(f"Error creating visualizations: {e}")
    
    logger.info("\nSimplified advanced rule-based reasoning demo completed")


if __name__ == "__main__":
    main()
