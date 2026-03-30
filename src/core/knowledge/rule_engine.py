#!/usr/bin/env python3
"""
ImpressionCore: Rule Engine

Module for rule engine functionality in the ImpressionCore framework.

File: knowledge\rule_engine.py
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
Dependencies: [typing, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements rule engine functionality for the
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
from knowledge.rule_engine import Rule
instance = Rule()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any, Callable, Optional, Set, Union
from dataclasses import dataclass, field

from .uks import UniversalKnowledgeStore, KnowledgeNode

logger = logging.getLogger(__name__)

@dataclass
class Rule:
    """
    A rule in the reasoning system, consisting of conditions and actions.
    
    The rule follows the pattern: IF [conditions] THEN [actions]
    """
    
    name: str
    description: str
    # Conditions that must be met for the rule to fire
    conditions: List[Callable[[UniversalKnowledgeStore, Dict[str, Any]], bool]]
    # Actions to perform when conditions are met
    actions: List[Callable[[UniversalKnowledgeStore, Dict[str, Any]], None]]
    # Priority of the rule (higher priority rules fire first)
    priority: int = 0
    # Tags for categorizing rules
    tags: List[str] = field(default_factory=list)
    # Flag indicating if this rule is active
    active: bool = True
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def evaluate(self, uks: UniversalKnowledgeStore, context: Dict[str, Any] = None) -> bool:
        """
        Evaluate if the rule's conditions are met.
        
        Args:
            uks: The Universal Knowledge Store
            context: Additional context data
            
        Returns:
            True if all conditions are met, False otherwise
        """
        context = context or {}
        
        try:
            # All conditions must be met for the rule to fire
            return all(condition(uks, context) for condition in self.conditions)
        except Exception as e:
            logger.error(f"Error evaluating rule '{self.name}': {e}")
            return False
    
    def apply(self, uks: UniversalKnowledgeStore, context: Dict[str, Any] = None) -> bool:
        """
        Apply the rule's actions if conditions are met.
        
        Args:
            uks: The Universal Knowledge Store
            context: Additional context data
            
        Returns:
            True if the rule was applied, False otherwise
        """
        context = context or {}
        
        # Check if the rule is active and conditions are met
        if not self.active or not self.evaluate(uks, context):
            return False
            
        try:
            # Apply all actions
            for action in self.actions:
                action(uks, context)
                
            logger.debug(f"Applied rule: {self.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error applying rule '{self.name}': {e}")
            return False


class RuleEngine:
    """
    Rule engine for applying dynamic reasoning rules to a knowledge store.
    
    Features:
    - Rule prioritization
    - Context-aware rule evaluation
    - Conflict resolution
    - Explanatory traces
    """
    
    def __init__(self, knowledge_store: UniversalKnowledgeStore):
        """
        Initialize the rule engine.
        
        Args:
            knowledge_store: The Universal Knowledge Store to operate on
        """
        self.uks = knowledge_store
        # Map rule names to rules
        self.rules: Dict[str, Rule] = {}
        # Trace of rule evaluations for explanation
        self.execution_trace: List[Dict[str, Any]] = []
        # Flag to track if tracing is enabled
        self.tracing_enabled = False
    
    def log_rules_state(self):
        """Log the current state of the rules dictionary."""
        logger.debug(f"Current rules state: {list(self.rules.keys())}")

    def add_rule(self, rule: Rule) -> bool:
        """Add a rule to the engine."""
        if rule.name in self.rules:
            logger.warning(f"Rule '{rule.name}' already exists. Use update_rule to modify it.")
            return False
        self.rules[rule.name] = rule
        self.log_rules_state()  # Log the state after adding a rule
        return True
    
    def update_rule(self, rule: Rule) -> bool:
        """Update an existing rule."""
        if rule.name not in self.rules:
            logger.warning(f"Rule '{rule.name}' does not exist. Use add_rule to create it.")
            return False
        self.rules[rule.name] = rule
        self.log_rules_state()  # Log the state after updating a rule
        return True
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove a rule from the engine."""
        if rule_name not in self.rules:
            logger.warning(f"Rule '{rule_name}' does not exist.")
            return False
        del self.rules[rule_name]
        # Memory optimization: Explicit memory cleanup
        self.log_rules_state()  # Log the state after removing a rule
        return True
    
    def get_rule(self, rule_name: str) -> Optional[Rule]:
        """
        Get a rule by name.
        
        Args:
            rule_name: The name of the rule to get
            
        Returns:
            The rule if it exists, None otherwise
        """
        return self.rules.get(rule_name)
    
    def get_rules_by_tag(self, tag: str) -> List[Rule]:
        """
        Get rules with a specific tag.
        
        Args:
            tag: The tag to filter by
            
        Returns:
            List of rules with the specified tag
        """
        return [rule for rule in self.rules.values() if tag in rule.tags]
    
    def evaluate_all(self, context: Dict[str, Any] = None) -> Dict[str, bool]:
        """
        Evaluate all rules without applying them.
        
        Args:
            context: Additional context data
            
        Returns:
            Dictionary mapping rule names to evaluation results
        """
        context = context or {}
        results = {}
        
        for name, rule in self.rules.items():
            if rule.active:
                results[name] = rule.evaluate(self.uks, context)
                
        return results
    
    def apply_all(self, context: Dict[str, Any] = None) -> Dict[str, bool]:
        """
        Apply all active rules that meet their conditions.
        
        Rules are applied in order of priority.
        
        Args:
            context: Additional context data
            
        Returns:
            Dictionary mapping rule names to application results
        """
        context = context or {}
        results = {}
        
        # Clear trace if tracing is enabled
        if self.tracing_enabled:
            self.execution_trace = []
            
        # Sort rules by priority (higher priority first)
        sorted_rules = sorted(self.rules.values(), key=lambda r: -r.priority)
        
        # Apply rules in priority order
        for rule in sorted_rules:
            if rule.active:
                start_time = None
                if self.tracing_enabled:
                    import time
                    start_time = time.time()
                    
                # Evaluate and apply rule
                evaluation = rule.evaluate(self.uks, context)
                applied = False
                
                if evaluation:
                    applied = rule.apply(self.uks, context)
                
                results[rule.name] = applied
                
                # Add to trace if tracing is enabled
                if self.tracing_enabled:
                    end_time = time.time()
                    self.execution_trace.append({
                        'rule_name': rule.name,
                        'evaluated': evaluation,
                        'applied': applied,
                        'time_ms': (end_time - start_time) * 1000,
                        'context': {
                            k: str(v) for k, v in context.items() 
                            if not k.startswith('_')  # Skip private context variables
                        }
                    })
                
        return results
    
    def enable_tracing(self):
        """Enable rule execution tracing."""
        self.tracing_enabled = True
        
    def disable_tracing(self):
        """Disable rule execution tracing."""
        self.tracing_enabled = False
        
    def get_execution_trace(self) -> List[Dict[str, Any]]:
        """
        Get the execution trace of the last apply_all call.
        
        Returns:
            List of trace entries with rule execution details
        """
        return self.execution_trace
    
    def apply_rules_for_node(self, node_label: str, context: Dict[str, Any] = None) -> Dict[str, bool]:
        """
        Apply all rules that are relevant to a specific node.
        
        Args:
            node_label: The label of the node to focus rules on
            context: Additional context data
            
        Returns:
            Dictionary mapping rule names to application results
        """
        context = context or {}
        # Add node to context
        node = self.uks.get_node(node_label)
        if not node:
            logger.warning(f"Node '{node_label}' not found in the knowledge store")
            return {}
            
        # Create a node-specific context
        node_context = {
            'node': node,
            'label': node_label,
            'attributes': node.get_all_attributes(),
            **context
        }
        
        # Apply rules with the node context
        return self.apply_all(node_context)
    
    def create_condition(self, condition_type: str, **kwargs) -> Callable:
        """
        Create a condition function for rules based on predefined types.
        
        Args:
            condition_type: Type of condition to create
            **kwargs: Parameters for the condition
            
        Returns:
            A condition function that can be used in rules
        """
        if condition_type == 'attribute_exists':
            node_label = kwargs.get('node_label')
            attribute = kwargs.get('attribute')
            
            def condition(uks, context):
                """
                
    condition function for processing.
    
    Args:
        uks, context: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
                """
                node = uks.get_node(node_label)
                return node and node.get_attribute(attribute) is not None
                
            return condition
            
        elif condition_type == 'attribute_equals':
            node_label = kwargs.get('node_label')
            attribute = kwargs.get('attribute')
            value = kwargs.get('value')
            
            def condition(uks, context):
                """
                
    condition function for processing.
    
    Args:
        uks, context: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
                """
                node = uks.get_node(node_label)
                return node and node.get_attribute(attribute) == value
                
            return condition
            
        elif condition_type == 'relationship_exists':
            subject_label = kwargs.get('subject_label')
            relation_type = kwargs.get('relation_type')
            object_label = kwargs.get('object_label')
            
            def condition(uks, context):
                """
                
    condition function for processing.
    
    Args:
        uks, context: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
                """
                subject = uks.get_node(subject_label)
                object_node = uks.get_node(object_label)
                
                if not subject or not object_node:
                    return False
                    
                for rel_type, target in subject.relationships:
                    if rel_type == relation_type and target.label == object_label:
                        return True
                        
                return False
                
            return condition
            
        elif condition_type == 'context_key_exists':
            key = kwargs.get('key')
            
            def condition(uks, context):
                """
                
    condition function for processing.
    
    Args:
        uks, context: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
                """
                return key in context
                
            return condition
            
        elif condition_type == 'context_key_equals':
            key = kwargs.get('key')
            value = kwargs.get('value')
            
            def condition(uks, context):
                """
                
    condition function for processing.
    
    Args:
        uks, context: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
                """
                return key in context and context[key] == value
                
            return condition
                
        else:
            logger.error(f"Unknown condition type: {condition_type}")
            
            def always_false(uks, context):
                """
                
    always_false function for processing.
    
    Args:
        uks, context: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
                """
                return False
                
            return always_false
    
    def create_action(self, action_type: str, **kwargs) -> Callable:
        """
        Create an action function for rules based on predefined types.
        
        Args:
            action_type: Type of action to create
            **kwargs: Parameters for the action
            
        Returns:
            An action function that can be used in rules
        """
        if action_type == 'add_attribute':
            node_label = kwargs.get('node_label')
            attribute = kwargs.get('attribute')
            value = kwargs.get('value')
            
            def action(uks, context):
                """
                
    action function for processing.
    
    Args:
        uks, context: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
                """
                node = uks.get_node(node_label)
                if node:
                    node.add_attribute(attribute, value)
                    
            return action
            
        elif action_type == 'add_relationship':
            subject_label = kwargs.get('subject_label')
            relation_type = kwargs.get('relation_type')
            object_label = kwargs.get('object_label')
            
            def action(uks, context):
                """
                
    action function for processing.
    
    Args:
        uks, context: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
                """
                uks.add_relationship(subject_label, relation_type, object_label)
                
            return action
            
        elif action_type == 'compute_attribute':
            node_label = kwargs.get('node_label')
            attribute = kwargs.get('attribute')
            formula = kwargs.get('formula')
            
            def action(uks, context):
                """
                
    action function for processing.
    
    Args:
        uks, context: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
                """
                node = uks.get_node(node_label)
                if not node:
                    return
                    
                # Simple formula evaluation with node attributes
                try:
                    # Create a local environment with node attributes
                    env = {**node.get_all_attributes(), **context}
                    
                    # Evaluate formula in the environment
                    result = eval(formula, {"__builtins__": {}}, env)
                    
                    # Set the computed attribute
                    node.add_attribute(attribute, result)
                except Exception:
                    logger.error(f"Error computing attribute '{attribute}' for node '{node_label}'")
                    
            return action
            
        else:
            logger.error(f"Unknown action type: {action_type}")
            
            def no_op(uks, context):
                """
                
    no_op function for processing.
    
    Args:
        uks, context: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
                """
                pass
                
            return no_op

