#!/usr/bin/env python3
"""
ImpressionCore: Node

Module for node functionality in the ImpressionCore framework.

File: knowledge\node.py
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
This module implements node functionality for the
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
from knowledge.node import KnowledgeNode
instance = KnowledgeNode()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import uuid
from typing import Dict, Any, List, Optional, Set, Union


class KnowledgeNode:
    """
    A node in the knowledge graph representing an entity.
    
    Each node contains attributes, connections to other nodes,
    and can be tagged with various metadata.
    """
    
    def __init__(self, name: str, node_id: Optional[str] = None):
        """
        Initialize a knowledge node.
        
        Args:
            name: The name of the node
            node_id: Optional ID for the node, will be auto-generated if None
        """
        self.name = name
        self.id = node_id if node_id else str(uuid.uuid4())
        self.attributes = {}  # Key-value pairs of attributes
        self.relations = []   # List of relations to other nodes
        self.tags = set()     # Set of tags/categories for this node
        self.embedding = None  # Vector embedding for semantic similarity
    
    # Fixed: Added set_attribute method to match the call in image_generation_demo.py
    def set_attribute(self, key: str, value: Any) -> None:
        """
        Set or update an attribute on the node.
        
        Args:
            key: Attribute name
            value: Attribute value
        """
        self.attributes[key] = value
    
    # Added for backwards compatibility
    def add_attribute(self, key: str, value: Any) -> None:
        """
        Add an attribute to the node (alias for set_attribute).
        
        Args:
            key: Attribute name
            value: Attribute value
        """
        self.set_attribute(key, value)
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """
        Get an attribute from the node.
        
        Args:
            key: Attribute name
            default: Default value if attribute doesn't exist
            
        Returns:
            The attribute value or the default value
        """
        return self.attributes.get(key, default)
    
    def add_relation(self, relation_type: str, target_node: Union[str, 'KnowledgeNode']) -> None:
        """
        Add a relation to another node.
        
        Args:
            relation_type: Type of relation (e.g., "is-a", "part-of")
            target_node: The target node or its ID
        """
        target_id = target_node.id if isinstance(target_node, KnowledgeNode) else target_node
        self.relations.append({
            "type": relation_type,
            "target_id": target_id
        })
    
    def add_tag(self, tag: str) -> None:
        """
        Add a tag to the node.
        
        Args:
            tag: Tag to add
        """
        self.tags.add(tag)
    
    def has_tag(self, tag: str) -> bool:
        """
        Check if the node has a specific tag.
        
        Args:
            tag: Tag to check
            
        Returns:
            True if the node has the tag, False otherwise
        """
        return tag in self.tags
    
    def set_embedding(self, embedding) -> None:
        """
        Set the vector embedding for the node.
        
        Args:
            embedding: Vector embedding
        """
        self.embedding = embedding
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the node to a dictionary.
        
        Returns:
            Dict representation of the node
        """
        return {
            "id": self.id,
            "name": self.name,
            "attributes": self.attributes,
            "relations": self.relations,
            "tags": list(self.tags)
        }
    
    def __str__(self) -> str:
        """String representation of the node."""
        return f"KnowledgeNode(name='{self.name}', id='{self.id}')"
    
    def __repr__(self) -> str:
        """Detailed representation of the node."""
        return f"KnowledgeNode(name='{self.name}', id='{self.id}', attributes={self.attributes}, tags={self.tags})"
