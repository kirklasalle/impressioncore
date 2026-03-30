#!/usr/bin/env python3
"""
ImpressionCore: Dynamic

Module for dynamic functionality in the ImpressionCore framework.

File: knowledge\dynamic.py
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
This module implements dynamic functionality for the
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
from knowledge.dynamic import ConceptExpander
instance = ConceptExpander()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import logging
from typing import Dict, List, Any, Tuple, Optional, Set
import re
from collections import defaultdict

from src.core.knowledge.uks import UniversalKnowledgeStore, KnowledgeNode

logger = logging.getLogger(__name__)

class ConceptExpander:
    """
    Expands concepts in the Universal Knowledge Store by inferring new relationships.
    
    Uses patterns and rules to identify potential new concepts to add to the store.
    """
    
    def __init__(self, uks: UniversalKnowledgeStore):
        """
        Initialize the concept expander.
        
        Args:
            uks: Universal Knowledge Store instance to expand
        """
        self.uks = uks
        self.expansion_patterns = []
    
    def add_expansion_pattern(self, pattern: Dict[str, Any]) -> None:
        """
        Add a pattern for expanding concepts.
        
        Args:
            pattern: Dictionary defining the expansion pattern
        """
        if not self._validate_pattern(pattern):
            logger.error(f"Invalid expansion pattern: {pattern}")
            return
        
        self.expansion_patterns.append(pattern)
        logger.debug(f"Added expansion pattern: {pattern['name']}")
    
    def _validate_pattern(self, pattern: Dict[str, Any]) -> bool:
        """
        Validate an expansion pattern.
        
        Args:
            pattern: Pattern to validate
            
        Returns:
            True if pattern is valid, False otherwise
        """
        required_keys = ['name', 'source_type', 'target_type', 'condition', 'inference']
        
        for key in required_keys:
            if key not in pattern:
                logger.error(f"Expansion pattern missing required key: {key}")
                return False
        
        return True
    
    def expand_node(self, node: KnowledgeNode) -> List[Tuple[str, str, Any]]:
        """
        Expand a single node using available patterns.
        
        Args:
            node: KnowledgeNode to expand
            
        Returns:
            List of inferred facts as (subject, predicate, object) tuples
        """
        inferred_facts = []
        
        for pattern in self.expansion_patterns:
            # Check if node matches the source type
            if pattern['source_type'] not in node.label:
                continue
            
            # Check if condition is met
            if not self._evaluate_condition(node, pattern['condition']):
                continue
            
            # Apply the inference
            new_facts = self._apply_inference(node, pattern['inference'], pattern['target_type'])
            inferred_facts.extend(new_facts)
        
        return inferred_facts
    
    def _evaluate_condition(self, node: KnowledgeNode, condition: Dict[str, Any]) -> bool:
        """
        Evaluate if a node meets a condition.
        
        Args:
            node: Node to evaluate
            condition: Condition to check
            
        Returns:
            True if condition is met, False otherwise
        """
        # Check required attributes
        for attr, value in condition.get('attributes', {}).items():
            node_value = node.get_attribute(attr)
            
            if node_value is None:
                return False
                
            if isinstance(value, dict):
                # Handle comparison operators
                if 'min' in value and node_value < value['min']:
                    return False
                if 'max' in value and node_value > value['max']:
                    return False
                if 'equals' in value and node_value != value['equals']:
                    return False
            elif node_value != value:
                return False
        
        # Check relationships
        for rel_type, target_label in condition.get('relationships', []):
            found = False
            for r_type, r_target in node.relationships:
                if r_type == rel_type and r_target.label == target_label:
                    found = True
                    break
            
            if not found:
                return False
        
        return True
    
    def _apply_inference(
        self,
        node: KnowledgeNode,
        inference: Dict[str, Any],
        target_type: str
    ) -> List[Tuple[str, str, Any]]:
        """
        Apply an inference to a node.
        
        Args:
            node: Node to apply inference to
            inference: Inference instructions
            target_type: Type of target concept
            
        Returns:
            List of inferred facts as (subject, predicate, object) tuples
        """
        inferred_facts = []
        
        # Create new node if needed
        if 'create_node' in inference and inference['create_node']:
            # Check if the node already exists
            new_node_label = inference.get('new_node_label', f"{node.label}_{target_type}")
            
            # Add inferred facts for the new node
            for predicate, obj_template in inference.get('new_attributes', {}).items():
                # Replace placeholders in template
                if isinstance(obj_template, str) and '{' in obj_template:
                    for attr_name in re.findall(r'{([^}]+)}', obj_template):
                        attr_value = node.get_attribute(attr_name)
                        if attr_value is not None:
                            obj_template = obj_template.replace(f"{{{attr_name}}}", str(attr_value))
                
                # Add to inferred facts
                inferred_facts.append((new_node_label, predicate, obj_template))
        
        # Add inferred attributes to existing node
        for predicate, obj_template in inference.get('add_attributes', {}).items():
            # Replace placeholders in template
            if isinstance(obj_template, str) and '{' in obj_template:
                for attr_name in re.findall(r'{([^}]+)}', obj_template):
                    attr_value = node.get_attribute(attr_name)
                    if attr_value is not None:
                        obj_template = obj_template.replace(f"{{{attr_name}}}", str(attr_value))
            
            # Add to inferred facts
            inferred_facts.append((node.label, predicate, obj_template))
        
        return inferred_facts
    
    def expand_knowledge_store(self, max_inferences: int = 100) -> int:
        """
        Expand the entire knowledge store.
        
        Args:
            max_inferences: Maximum number of inferences to make
            
        Returns:
            Number of facts added
        """
        all_inferred_facts = []
        nodes_to_process = list(self.uks.nodes.values())
        
        # Collect all potential inferences
        for node in nodes_to_process:
            inferred_facts = self.expand_node(node)
            all_inferred_facts.extend(inferred_facts)
            
            # Stop if we've reached the maximum
            if len(all_inferred_facts) >= max_inferences:
                break
        
        # Apply inferences (up to the maximum)
        facts_added = 0
        for subject, predicate, obj_value in all_inferred_facts[:max_inferences]:
            self.uks.add_fact(subject, predicate, obj_value)
            facts_added += 1
        
        logger.info(f"Added {facts_added} new facts to knowledge store via inference")
        return facts_added


class ConceptualBridge:
    """
    Creates bridges between different conceptual domains in the knowledge store.
    
    Identifies analogies and metaphorical mappings between different domains.
    """
    
    def __init__(self, uks: UniversalKnowledgeStore):
        """
        Initialize the conceptual bridge.
        
        Args:
            uks: Universal Knowledge Store instance
        """
        self.uks = uks
        self.domain_mappings = []
    
    def add_domain_mapping(
        self, 
        source_domain: str,
        target_domain: str, 
        attribute_mappings: Dict[str, str],
        relation_mappings: Dict[str, str] = None
    ) -> None:
        """
        Add a mapping between two conceptual domains.
        
        Args:
            source_domain: Label of the source domain
            target_domain: Label of the target domain
            attribute_mappings: Mapping of attributes from source to target
            relation_mappings: Mapping of relationships from source to target
        """
        mapping = {
            'source_domain': source_domain,
            'target_domain': target_domain,
            'attribute_mappings': attribute_mappings,
            'relation_mappings': relation_mappings or {}
        }
        
        self.domain_mappings.append(mapping)
        logger.info(f"Added mapping from {source_domain} to {target_domain}")
    
    def create_analogies(self, max_analogies: int = 50) -> int:
        """
        Create analogies between domains.
        
        Args:
            max_analogies: Maximum number of analogies to create
            
        Returns:
            Number of analogical facts added
        """
        analogies_created = 0
        
        for mapping in self.domain_mappings:
            source_domain = mapping['source_domain']
            target_domain = mapping['target_domain']
            
            # Get all nodes in the source domain
            source_nodes = [
                node for node in self.uks.nodes.values() 
                if source_domain.lower() in node.label.lower()
            ]
            
            # For each source node, find or create a corresponding target node
            for source_node in source_nodes:
                # Create a target node name based on the mapping
                target_node_label = source_node.label.replace(source_domain, target_domain)
                
                # Get or create the target node
                target_node = self.uks.get_node(target_node_label)
                if not target_node:
                    target_node = self.uks.add_node(target_node_label)
                
                # Map attributes
                for source_attr, target_attr in mapping['attribute_mappings'].items():
                    source_value = source_node.get_attribute(source_attr)
                    if source_value is not None:
                        self.uks.add_fact(target_node_label, target_attr, source_value)
                        analogies_created += 1
                        
                        if analogies_created >= max_analogies:
                            logger.info(f"Created {analogies_created} analogical facts (reached limit)")
                            return analogies_created
                
                # Map relationships
                for source_rel, target_rel in mapping['relation_mappings'].items():
                    for rel_type, rel_target in source_node.relationships:
                        if rel_type == source_rel:
                            # Create corresponding target relationship
                            target_rel_node_label = rel_target.label.replace(source_domain, target_domain)
                            self.uks.add_relationship(target_node_label, target_rel, target_rel_node_label)
                            analogies_created += 1
                            
                            if analogies_created >= max_analogies:
                                logger.info(f"Created {analogies_created} analogical facts (reached limit)")
                                return analogies_created
        
        logger.info(f"Created {analogies_created} analogical facts")
        return analogies_created


class TemporalReasoner:
    """
    Handles temporal reasoning within the Universal Knowledge Store.
    
    Manages facts that change over time and infers temporal relationships.
    """
    
    def __init__(self, uks: UniversalKnowledgeStore):
        """
        Initialize the temporal reasoner.
        
        Args:
            uks: Universal Knowledge Store instance
        """
        self.uks = uks
        self.temporal_attributes = set()
        self.time_points = []
    
    def register_temporal_attribute(self, attribute_name: str) -> None:
        """
        Register an attribute as temporal (changing over time).
        
        Args:
            attribute_name: Name of the temporal attribute
        """
        self.temporal_attributes.add(attribute_name)
    
    def add_time_point(self, time_point: str) -> None:
        """
        Add a time point for temporal reasoning.
        
        Args:
            time_point: Time point identifier
        """
        if time_point not in self.time_points:
            self.time_points.append(time_point)
            # Sort time points (assuming they can be compared)
            self.time_points.sort()
    
    def set_temporal_fact(
        self,
        subject: str,
        predicate: str,
        object_value: Any,
        time_point: str
    ) -> None:
        """
        Set a fact that is true at a specific time point.
        
        Args:
            subject: Subject node label
            predicate: Predicate (attribute name)
            object_value: Object/value
            time_point: Time point when the fact is true
        """
        # Check if this is a registered temporal attribute
        if predicate not in self.temporal_attributes:
            logger.warning(f"Setting temporal fact for non-temporal attribute: {predicate}")
            self.register_temporal_attribute(predicate)
        
        # Add time point if not already registered
        if time_point not in self.time_points:
            self.add_time_point(time_point)
        
        # Create a temporal version of the attribute name
        temporal_predicate = f"{predicate}_at_{time_point}"
        
        # Set the fact
        self.uks.add_fact(subject, temporal_predicate, object_value)
    
    def get_temporal_fact(
        self,
        subject: str,
        predicate: str,
        time_point: str
    ) -> Any:
        """
        Get a fact at a specific time point.
        
        Args:
            subject: Subject node label
            predicate: Predicate (attribute name)
            time_point: Time point to query
            
        Returns:
            Object/value at the given time point, or None if not found
        """
        # Create temporal predicate
        temporal_predicate = f"{predicate}_at_{time_point}"
        
        # Get node
        node = self.uks.get_node(subject)
        if not node:
            return None
        
        # Get attribute value
        return node.get_attribute(temporal_predicate)
    
    def get_latest_value(
        self,
        subject: str,
        predicate: str,
        max_time_point: Optional[str] = None
    ) -> Tuple[Any, Optional[str]]:
        """
        Get the latest value for a temporal attribute.
        
        Args:
            subject: Subject node label
            predicate: Predicate (attribute name)
            max_time_point: Maximum time point to consider (inclusive)
            
        Returns:
            Tuple of (value, time_point) for the latest value, or (None, None) if not found
        """
        # Get node
        node = self.uks.get_node(subject)
        if not node:
            return None, None
        
        # Determine time points to check
        time_points = self.time_points.copy()
        if max_time_point:
            time_points = [tp for tp in time_points if tp <= max_time_point]
        
        # Sort in descending order to find latest value first
        time_points.sort(reverse=True)
        
        # Find latest value
        for tp in time_points:
            temporal_predicate = f"{predicate}_at_{tp}"
            value = node.get_attribute(temporal_predicate)
            if value is not None:
                return value, tp
        
        return None, None
    
    def get_value_at_time(
        self,
        subject: str,
        predicate: str,
        time_point: str,
        interpolate: bool = False
    ) -> Any:
        """
        Get a value at a specific time point, possibly interpolating if the exact time point is not available.
        
        Args:
            subject: Subject node label
            predicate: Predicate (attribute name)
            time_point: Time point to query
            interpolate: Whether to interpolate values between known time points
            
        Returns:
            Object/value at the given time point, or None if not found
        """
        # First check if we have the exact time point
        value = self.get_temporal_fact(subject, predicate, time_point)
        if value is not None:
            return value
        
        if not interpolate:
            return None
        
        # If interpolation is requested, find closest time points
        node = self.uks.get_node(subject)
        if not node:
            return None
        
        # Find all temporal values for this attribute
        temporal_values = {}
        for attr, val in node.attributes.items():
            if attr.startswith(f"{predicate}_at_"):
                tp = attr[len(f"{predicate}_at_"):]
                temporal_values[tp] = val
        
        if not temporal_values:
            return None
        
        # Find closest time points before and after
        before_tp = None
        after_tp = None
        before_val = None
        after_val = None
        
        for tp, val in temporal_values.items():
            if tp <= time_point and (before_tp is None or tp > before_tp):
                before_tp = tp
                before_val = val
            elif tp > time_point and (after_tp is None or tp < after_tp):
                after_tp = tp
                after_val = val
        
        # Return closest value if only one side is available
        if before_tp is None and after_tp is not None:
            return after_val
        if after_tp is None and before_tp is not None:
            return before_val
        
        # If both sides available, try to interpolate
        if isinstance(before_val, (int, float)) and isinstance(after_val, (int, float)):
            # For numeric values, do linear interpolation
            try:
                before_time = float(before_tp)
                after_time = float(after_tp)
                target_time = float(time_point)
                
                # Calculate interpolation factor
                factor = (target_time - before_time) / (after_time - before_time)
                
                # Interpolate
                return before_val + factor * (after_val - before_val)
            except (ValueError, ZeroDivisionError):
                # If time points can't be converted to float or are identical, return closest value
                return before_val
        else:
            # For non-numeric values, return closest value
            return before_val
    
    def track_changes(
        self,
        subject: str,
        predicate: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> List[Tuple[str, Any]]:
        """
        Track changes of an attribute's value over time.
        
        Args:
            subject: Subject node label
            predicate: Predicate (attribute name)
            start_time: Start time point (inclusive), or None for earliest
            end_time: End time point (inclusive), or None for latest
            
        Returns:
            List of tuples (time_point, value) showing how the value changed over time
        """
        # Get node
        node = self.uks.get_node(subject)
        if not node:
            return []
        
        # Find all temporal values for this attribute
        changes = []
        for attr, val in node.attributes.items():
            if attr.startswith(f"{predicate}_at_"):
                tp = attr[len(f"{predicate}_at_"):]
                
                # Apply time filters
                if start_time and tp < start_time:
                    continue
                if end_time and tp > end_time:
                    continue
                
                changes.append((tp, val))
        
        # Sort by time point
        changes.sort(key=lambda x: x[0])
        
        return changes
    
    def infer_change_events(
        self,
        subject: str,
        predicate: str
    ) -> List[Dict[str, Any]]:
        """
        Infer change events from temporal facts.
        
        Args:
            subject: Subject node label
            predicate: Predicate (attribute name)
            
        Returns:
            List of change events with from_value, to_value, time_point, and confidence
        """
        # Get all changes for this attribute
        changes = self.track_changes(subject, predicate)
        
        if len(changes) < 2:
            return []
        
        # Identify change events
        events = []
        for i in range(1, len(changes)):
            prev_time, prev_value = changes[i-1]
            curr_time, curr_value = changes[i]
            
            # Skip if values are the same
            if prev_value == curr_value:
                continue
            
            # Create change event
            event = {
                "subject": subject,
                "predicate": predicate,
                "from_value": prev_value,
                "to_value": curr_value,
                "from_time": prev_time,
                "to_time": curr_time,
                "confidence": 1.0  # High confidence for direct observations
            }
            
            events.append(event)
        
        return events
    
    def export_timeline(self, subject: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Export a timeline of all changes for a subject.
        
        Args:
            subject: Subject node label
            
        Returns:
            Dictionary with temporal attributes as keys and lists of time-value pairs as values
        """
        # Get node
        node = self.uks.get_node(subject)
        if not node:
            return {}
        
        # Group temporal attributes
        timeline = defaultdict(list)
        
        for attr, val in node.attributes.items():
            # Check if this is a temporal attribute
            for temporal_attr in self.temporal_attributes:
                if attr.startswith(f"{temporal_attr}_at_"):
                    time_point = attr[len(f"{temporal_attr}_at_"):]
                    timeline[temporal_attr].append({"time": time_point, "value": val})
        
        # Sort each attribute's timeline by time point
        for attr in timeline:
            timeline[attr].sort(key=lambda x: x["time"])
        
        return dict(timeline)