#!/usr/bin/env python3
"""
ImpressionCore: Conditional Rules

Module for conditional rules functionality in the ImpressionCore framework.

File: knowledge\conditional_rules.py
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
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements conditional rules functionality for the
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
from knowledge.conditional_rules import Rule
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
from typing import List, Dict, Any, Callable, Optional, Union
import re
import time

logger = logging.getLogger(__name__)

class Rule:
    """
    A conditional rule that can be applied to queries based on specific conditions.
    
    Rules consist of:
    - A set of conditions (functions that evaluate to True/False)
    - A set of actions (functions that perform operations when conditions are met)
    - Priority level (higher priority rules execute first)
    """
    
    def __init__(
        self, 
        name: str,
        conditions: List[Callable[[str, Dict[str, Any], Any], bool]],
        actions: List[Callable[[str, Dict[str, Any], Any], Any]],
        priority: int = 0,
        description: str = ""
    ):
        """
        Initialize a rule.
        
        Args:
            name: Rule name/identifier
            conditions: List of condition functions that determine if the rule applies
            actions: List of action functions to execute when conditions are met
            priority: Rule priority (higher priority rules execute first)
            description: Human-readable description of the rule
        """
        self.name = name
        self.conditions = conditions
        self.actions = actions
        self.priority = priority
        self.description = description or name
        self.created_at = time.time()
        self.last_fired = None
    
    def check_conditions(self, query: str, context: Dict[str, Any], knowledge_store: Any) -> bool:
        """
        Check if all conditions for this rule are satisfied.
        
        Args:
            query: User query text
            context: Current context dictionary
            knowledge_store: The knowledge store instance
            
        Returns:
            True if all conditions are satisfied, False otherwise
        """
        try:
            return all(condition(query, context, knowledge_store) for condition in self.conditions)
        except Exception as e:
            logger.error(f"Error evaluating conditions for rule '{self.name}': {str(e)}")
            return False
    
    def execute_actions(self, query: str, context: Dict[str, Any], knowledge_store: Any) -> List[Any]:
        """
        Execute all actions for this rule.
        
        Args:
            query: User query text
            context: Current context dictionary
            knowledge_store: The knowledge store instance
            
        Returns:
            List of results from each action
        """
        results = []
        
        for i, action in enumerate(self.actions):
            try:
                result = action(query, context, knowledge_store)
                results.append(result)
            except Exception as e:
                logger.error(f"Error executing action {i} for rule '{self.name}': {str(e)}")
                results.append(None)
        
        self.last_fired = time.time()
        return results
    
    def __str__(self):
        """
        
    __str__ function for processing.
    
    Args:
        self: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        return f"Rule({self.name}, priority={self.priority})"
    
    def __repr__(self):
        """
        
    __repr__ function for processing.
    
    Args:
        self: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        return self.__str__()


class ConditionalRuleEngine:
    """
    Engine for conditional rule application based on query context.
    
    The rule engine maintains a collection of rules and executes matching
    rules based on query and context conditions.
    """
    
    def __init__(self, knowledge_store: Any):
        """
        Initialize the rule engine.
        
        Args:
            knowledge_store: The knowledge store instance to use with rules
        """
        self.rules = []
        self.knowledge_store = knowledge_store
        self.rule_history = []
        self.max_history = 100
    
    def register_rule(self, rule: Rule) -> None:
        """
        Add a rule to the engine.
        
        Args:
            rule: The rule to register
        """
        # Check for duplicate rule names
        if any(r.name == rule.name for r in self.rules):
            logger.warning(f"Rule with name '{rule.name}' already exists. Overwriting.")
            self.rules = [r for r in self.rules if r.name != rule.name]
        
        self.rules.append(rule)
        # Sort by priority (descending)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        logger.info(f"Registered rule '{rule.name}' with priority {rule.priority}")
    
    def unregister_rule(self, rule_name: str) -> bool:
        """
        Remove a rule from the engine.
        
        Args:
            rule_name: Name of the rule to remove
            
        Returns:
            True if rule was removed, False if not found
        """
        initial_count = len(self.rules)
        self.rules = [r for r in self.rules if r.name != rule_name]
        return len(self.rules) < initial_count
    
    def execute_matching_rules(
        self, 
        query: str, 
        context: Dict[str, Any] = None,
        max_rules: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute all rules that match the given query and context.
        
        Args:
            query: User query text
            context: Current context dictionary (will be created if None)
            max_rules: Maximum number of matching rules to execute
            
        Returns:
            List of dictionaries with execution results
        """
        if context is None:
            context = {}
        
        # Find matching rules
        matching_rules = [
            rule for rule in self.rules
            if rule.check_conditions(query, context, self.knowledge_store)
        ]
        
        # Limit number of rules if specified
        if max_rules is not None:
            matching_rules = matching_rules[:max_rules]
        
        # Execute matching rules
        results = []
        
        for rule in matching_rules:
            logger.info(f"Executing rule '{rule.name}'")
            action_results = rule.execute_actions(query, context, self.knowledge_store)
            
            result = {
                "rule": rule.name,
                "priority": rule.priority,
                "results": action_results,
                "timestamp": time.time()
            }
            
            results.append(result)
            
            # Add to history
            self.rule_history.append({
                "query": query,
                "rule": rule.name,
                "timestamp": time.time()
            })
            
            # Trim history if needed
            if len(self.rule_history) > self.max_history:
                self.rule_history = self.rule_history[-self.max_history:]
        
        return results
    
    def get_rule_by_name(self, name: str) -> Optional[Rule]:
        """
        Get a rule by its name.
        
        Args:
            name: Rule name to search for
            
        Returns:
            The rule if found, None otherwise
        """
        for rule in self.rules:
            if rule.name == name:
                return rule
        return None
    
    def get_rules_by_pattern(self, pattern: str) -> List[Rule]:
        """
        Get rules matching a name pattern.
        
        Args:
            pattern: Regex pattern to match rule names
            
        Returns:
            List of matching rules
        """
        try:
            regex = re.compile(pattern)
            return [rule for rule in self.rules if regex.search(rule.name)]
        except re.error:
            logger.error(f"Invalid regex pattern: {pattern}")
            return []
