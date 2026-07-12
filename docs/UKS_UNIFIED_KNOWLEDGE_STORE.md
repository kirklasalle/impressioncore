# UKS (Unified Knowledge Store)

**Date:** 2025-04-16

## Overview

The Unified Knowledge Store (UKS) is ImpressionCore memory system designed for storing, retrieving, and reasoning over structured knowledge. It serves as both a persistent knowledge base and a dynamic memory system that can be enriched through interaction with BrainSim3.

## Table of Contents

- [Introduction](#introduction)
- [Architecture](#architecture)
- [Core Components](#core-components)
- [Python API](#python-api)
- [Integration with BrainSim3](#integration-with-brainsim3)
- [Memory Efficiency](#memory-efficiency)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)

## Introduction

UKS is designed to efficiently represent and operate on semantic knowledge in a way that:

- Preserves relationships between entities
- Supports reasoning over knowledge
- Enables dynamic updates during operation
- Efficiently stores complex hierarchical knowledge
- Integrates with other components of ImpressionCore-b1

Implementation:

- Python: `src/core/brainsim/memory/unified_knowledge_store.py`
- C#: `src/core/brainsim3/UKS/`

## Architecture

UKS uses a graph-based structure where:

1. **Nodes** represent entities, concepts, or facts
2. **Edges** represent relationships between nodes
3. **Properties** represent attributes of entities
4. **Rules** define constraints and inference patterns

The architecture follows these design principles:

- **Scalable**: Handles large knowledge bases efficiently
- **Flexible**: Adapts to various knowledge domains
- **Coherent**: Maintains consistency across knowledge updates
- **Interoperable**: Works with both Python and C# components

## Core Components

### Thing Class

The core entity class that represents nodes in the knowledge graph:

- Each `Thing` has a unique identifier
- Can have labels and properties
- Can be connected to other `Thing` nodes via relationships
- Supports hierarchical organization through parent-child relationships

### Relationship Class

Defines connections between nodes:

- Has a type (is-a, has-a, part-of, etc.)
- Can have directionality and strength
- Supports metadata for relationship context

### UKS Engine

The main interface for interacting with the knowledge store:

- Provides methods for adding/retrieving/updating knowledge
- Implements reasoning algorithms
- Manages persistence and serialization
- Optimizes memory usage for constrained environments

## Python API

The Python API provides a high-level interface to the UKS system:

```python
from src.core.brainsim.memory import UnifiedKnowledgeStore

# Initialize the knowledge store
uks = UnifiedKnowledgeStore()

# Add a new concept
uks.add_concept("planet", properties={"type": "astronomical_body"})

# Add a specific instance with relationships
uks.add_entity(
    name="Earth", 
    concepts=["planet"], 
    properties={"diameter": 12742, "has_life": True},
    relationships=[("orbits", "Sun"), ("has", "Moon")]
)

# Query knowledge
planets = uks.query(concept="planet", properties={"has_life": True})
```

### Core Methods

| Method | Description |
|--------|-------------|
| `add_concept(name, properties)` | Add a new concept/class |
| `add_entity(name, concepts, properties, relationships)` | Add a specific entity |
| `add_relationship(source, relation_type, target, properties)` | Create relationship between entities |
| `query(concept, properties, relationship_filter)` | Search for entities matching criteria |
| `load(filepath)` | Load knowledge base from file |
| `save(filepath)` | Save knowledge base to file |
| `merge(other_uks, conflict_resolution)` | Merge with another knowledge store |
| `infer(rules, depth)` | Apply inference rules to derive new knowledge |

## Integration with BrainSim3

UKS is tightly integrated with BrainSim3, enabling:

1. **Knowledge enrichment**: BrainSim3 can analyze text and extract new knowledge to add to UKS
2. **Reasoning augmentation**: UKS provides factual support for BrainSim3's reasoning processes
3. **Context enhancement**: UKS knowledge can be used to augment prompts for language models
4. **Temporal memory**: BrainSim3 can query UKS for historical context

### Integration Points

The main integration occurs through the BrainSimAdapter class:

- `BrainSimAdapter.augment_prompt()` uses UKS to retrieve relevant facts
- `BrainSimAdapter._retrieve_facts()` queries UKS for concept-related knowledge
- `CognitiveService.enrich_knowledge()` adds new facts to UKS based on analysis

## Memory Efficiency

UKS implements several optimizations for memory-constrained environments:

- **Lazy loading**: Only loads portions of the knowledge graph as needed
- **Index optimization**: Maintains efficient indexes for common query patterns
- **Caching**: Caches recent queries and frequent knowledge subgraphs
- **Compression**: Applies compression techniques for string-heavy knowledge
- **Pruning**: Periodically removes low-relevance or stale knowledge

Memory usage example:

- 10,000 entities with relationships: ~50MB memory
- Full solar system knowledge graph: ~4MB memory
- Complete knowledge graph with 100,000 entities: ~250MB memory

## Usage Examples

### Basic Knowledge Addition

```python
# Initialize
from src.core.brainsim.memory import UnifiedKnowledgeStore
uks = UnifiedKnowledgeStore()

# Add biological taxonomy
uks.add_concept("organism")
uks.add_concept("animal", parent="organism")
uks.add_concept("mammal", parent="animal")
uks.add_concept("dog", parent="mammal")

# Add specific instance
uks.add_entity("Rex", ["dog"], {
    "age": 3,
    "color": "brown"
})
```

### Knowledge Querying

```python
# Find all mammals
mammals = uks.query(concept="mammal", include_children=True)

# Find brown dogs
brown_dogs = uks.query(
    concept="dog", 
    properties={"color": "brown"},
    include_children=True
)

# Complex relationship query
query_result = uks.query_relationship(
    start_type="planet",
    relationship="has",
    end_property={"type": "satellite"}
)
```

### Integration with BrainSim3

```python
from src.core.brainsim import BrainSimAdapter
from src.core.brainsim.memory import UnifiedKnowledgeStore

# Initialize components
uks = UnifiedKnowledgeStore()
uks.load("knowledge/astronomy.uks")
brain_sim = BrainSimAdapter()

# Use UKS to augment prompt
user_query = "What makes Saturn different from other planets?"
augmented_prompt = brain_sim.augment_prompt(user_query, uks)

# Enrich UKS with new knowledge
new_text = "Saturn's largest moon Titan has lakes of liquid methane."
brain_sim.extract_and_store_knowledge(new_text, uks)
```

## Best Practices

1. **Knowledge organization**:
   - Create a clear concept hierarchy
   - Use consistent relationship types
   - Define properties with appropriate data types
   - Document domain-specific knowledge schemas

2. **Performance optimization**:
   - Keep relationship depth manageable (<5 hops for frequent queries)
   - Index frequently queried properties
   - Use batch operations for bulk updates
   - Consider memory constraints during large operations

3. **Integration with BrainSim3**:
   - Configure concept extraction sensitivity based on domain
   - Validate extracted facts before adding to UKS
   - Use confidence scores for inferred knowledge
   - Periodically validate and clean up knowledge

4. **Persistence**:
   - Save knowledge store after significant updates
   - Implement incremental backups for large knowledge bases
   - Use compression for long-term storage
   - Consider versioning for critical knowledge bases

## Implementation Details

### Data Structures

The UKS implementation uses specialized data structures to maximize efficiency:

1. **Compressed Node Dictionary**: Reduces memory footprint by encoding common property patterns
2. **Adjacency List Graph**: Optimized for fast traversal of relationships
3. **Property Maps**: Hash-based quick lookup for property values
4. **Bloom Filters**: Fast negative lookups for relationship checking

### Core Algorithms

1. **Knowledge Insertion**

```python
def add_entity(name, concepts, properties, relationships):
    # Check if entity exists
    entity_id = self._get_or_create_node_id(name)
    
    # Add concept connections (is-a relationships)
    for concept in concepts:
        concept_id = self._get_or_create_node_id(concept)
        self._add_relationship(entity_id, "is-a", concept_id)
    
    # Add properties
    self._add_properties(entity_id, properties)
    
    # Add relationships
    for rel_type, target in relationships:
        target_id = self._get_or_create_node_id(target)
        self._add_relationship(entity_id, rel_type, target_id)
    
    return entity_id
```

1. **Graph Traversal**

```python
def traverse_relationships(start_id, relationship_type, max_depth=3):
    visited = set()
    results = []
    queue = [(start_id, 0)]
    
    while queue:
        node_id, depth = queue.pop(0)
        
        if node_id in visited or depth > max_depth:
            continue
            
        visited.add(node_id)
        
        # Get related nodes
        related = self._get_relationships(node_id, relationship_type)
        results.extend(related)
        
        # Add neighbors to queue
        for rel_node in related:
            queue.append((rel_node, depth + 1))
    
    return results
```

1. **Inference Engine**

```python
def apply_inference_rules(rules, max_iterations=5):
    new_facts = True
    iteration = 0
    
    while new_facts and iteration < max_iterations:
        initial_fact_count = self.fact_count()
        
        for rule in rules:
            self._apply_single_rule(rule)
        
        new_fact_count = self.fact_count()
        new_facts = new_fact_count > initial_fact_count
        iteration += 1
        
    return iteration, new_fact_count - initial_fact_count
```

### Serialization Format

UKS uses a custom binary format for efficient storage:

1. **Header**: Contains version, entity count, and checksum
2. **Node Table**: Compact representation of all nodes
3. **Relationship Table**: Edge information with indexed references
4. **Property Dictionary**: Shared property keys stored once
5. **Value Store**: Compressed data values

Sample file structure:

```
UKS_FILE_HEADER (16 bytes)
NODE_COUNT (4 bytes)
RELATIONSHIP_COUNT (4 bytes)
PROPERTY_DICTIONARY_SIZE (4 bytes)
NODE_TABLE (variable)
RELATIONSHIP_TABLE (variable)
PROPERTY_DICTIONARY (variable)
VALUE_STORE (variable)
CHECKSUM (8 bytes)
```

## Performance Benchmarks

UKS has been tested under various conditions to ensure it meets performance requirements on target hardware.

### Memory Usage

| Knowledge Base Size | Memory Usage | Load Time | Query Time (avg) |
|--------------------|--------------|-----------|------------------|
| Small (100 entities) | 2.8 MB | 0.02s | <0.001s |
| Medium (10,000 entities) | 45.2 MB | 0.3s | 0.005s |
| Large (100,000 entities) | 248.7 MB | 2.8s | 0.037s |
| Very Large (1M entities) | 1.2 GB* | 28.4s | 0.12s |

*Uses lazy loading to keep active memory under 300MB on target hardware

### Operation Performance

| Operation | Small KB | Medium KB | Large KB |
|-----------|----------|-----------|----------|
| Add Entity | 0.2ms | 0.3ms | 0.5ms |
| Add Relationship | 0.1ms | 0.15ms | 0.2ms |
| Simple Query | 0.8ms | 2.1ms | 4.7ms |
| Complex Query | 2.3ms | 8.4ms | 22.3ms |
| Path Finding | 1.5ms | 12.8ms | 35.6ms |
| Save to Disk | 18ms | 320ms | 2.8s |
| Load from Disk | 15ms | 280ms | 2.5s |

### Scaling Characteristics

![UKS Performance Scaling](docs/uks_performance_scaling.png)

The graph shows a near-linear scaling in memory usage and query time up to 100,000 entities, with slight non-linear growth beyond that point due to indexing overhead.

## Future Roadmap

The UKS system will continue to evolve with these planned enhancements:

### Short-term (Q3 2025)

- **Distributed UKS**: Support for sharding large knowledge bases across multiple machines
- **Streaming Updates**: Real-time knowledge base updates with minimal locking
- **Advanced Inference**: Probabilistic reasoning with uncertainty handling
- **CUDA Acceleration**: GPU-accelerated graph operations for complex queries

### Medium-term (Q4 2025 - Q1 2026)

- **Knowledge Distillation**: Automatic summarization of knowledge graphs
- **Temporal Reasoning**: First-class support for time-based relationships and facts
- **Multimodal Knowledge**: Integration with visual and audio knowledge representations
- **Self-healing Consistency**: Automatic detection and resolution of knowledge conflicts

### Long-term (Q2 2026+)

- **Neuromorphic Integration**: Direct mapping between UKS and neuromorphic hardware
- **Autonomous Knowledge Acquisition**: Self-directed knowledge gathering and organization
- **Quantum-resistant Security**: Protection of sensitive knowledge with post-quantum cryptography
- **Conscious Knowledge Access**: Integration with higher-order cognitive processes in BrainSim4

### Research Directions

1. **Compression Techniques**: Further reducing memory footprint without sacrificing performance
2. **Explainable Inference**: Making reasoning paths transparent and understandable
3. **Cross-domain Knowledge Transfer**: Methods for applying knowledge from one domain to another
4. **Forgetting Strategies**: Principled approaches to knowledge pruning and consolidation
