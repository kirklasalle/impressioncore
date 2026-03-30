# ImpressionCore EDS: Embedding Dataset Discovery Guide

**Created:** July 10, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\eds_embedding_discovery_guide.md #api #documentation #inference #memory_management #multimodal #testing #training #official #permanent  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## Overview

The `eds_discover_embedding_datasets` tool is a specialized component of the ImpressionCore External Data Sources (EDS) system designed to discover, filter, and recommend datasets specifically suitable for embedding training. This tool focuses on datasets with high-quality annotations, validation splits, and compatibility with consumer hardware constraints.

## Table of Contents

1. [Tool Description](#tool-description)
2. [Parameters](#parameters)
3. [Filtering Logic](#filtering-logic)
4. [Scoring System](#scoring-system)
5. [Usage Examples](#usage-examples)
6. [Output Format](#output-format)
7. [Best Practices](#best-practices)
8. [Hardware Considerations](#hardware-considerations)
9. [Troubleshooting](#troubleshooting)

---

## Tool Description

The `eds_discover_embedding_datasets` tool performs intelligent dataset discovery by:

- **Filtering datasets** based on modality, use case, and annotation requirements
- **Verifying dataset sources** for availability and accessibility
- **Scoring datasets** for embedding suitability and quality
- **Checking hardware compatibility** against VRAM and memory constraints
- **Prioritizing datasets** with validation splits and comprehensive annotations

### Key Features

- **Embedding-Focused**: Only returns datasets marked as `embedding_friendly`
- **Annotation-Aware**: Filters for datasets with annotation support
- **Validation-Ready**: Prioritizes datasets with validation splits
- **Hardware-Constrained**: Respects VRAM and memory limitations
- **Quality-Scored**: Ranks datasets by suitability and quality

---

## Parameters

### `modality` (string, optional)

- **Default**: `"all"`
- **Options**: `"text"`, `"image"`, `"audio"`, `"video"`, `"multimodal"`, `"all"`
- **Description**: Filters datasets by data modality

### `use_case` (string, optional)

- **Default**: `"all"`
- **Options**: `"classification"`, `"similarity"`, `"retrieval"`, `"generation"`, `"all"`
- **Description**: Filters datasets by intended use case

### `min_annotation_coverage` (float, optional)

- **Default**: `0.8`
- **Range**: `0.0` to `1.0`
- **Description**: Minimum required annotation coverage (80% default)

### `require_validation_split` (boolean, optional)

- **Default**: `true`
- **Description**: Whether to require datasets with validation splits

### `hardware_constraints` (object, optional)

- **Default**: `{"vram_gb": 4}`
- **Fields**:
  - `vram_gb`: Available VRAM in GB
  - `max_dataset_size_gb`: Maximum dataset size in GB
- **Description**: Hardware limitations for dataset compatibility

---

## Filtering Logic

### Primary Filters

1. **Modality Filter**
   - Matches dataset categories against requested modality
   - Cross-modal datasets match multiple modalities

2. **Embedding Compatibility**
   - Only includes datasets with `embedding_friendly: true`
   - Excludes datasets unsuitable for embedding training

3. **Annotation Requirements**
   - Requires `annotation_support: true`
   - Filters by minimum annotation coverage threshold

4. **Validation Split Filter**
   - When enabled, requires `validation_sets: true`
   - Ensures proper train/validation/test splits

### Secondary Filters

1. **Hardware Constraints**
   - Memory usage ≤ 2x VRAM limit
   - Dataset size within specified limits

2. **Use Case Alignment**
   - Matches datasets to specific use cases
   - Uses primary and secondary dataset mappings

---

## Scoring System

### Embedding Suitability Score

The embedding suitability score combines multiple factors:

```python
score = base_quality_score + annotation_bonus + use_case_bonus + validation_bonus
```

#### Components

1. **Base Quality Score** (0.0-1.0)
   - From repository quality ratings
   - Reflects overall dataset quality

2. **Annotation Bonus** (0.0-0.4)
   - +0.1 per embedding-friendly annotation type
   - Types: `embeddings`, `similarity_scores`, `pairs`, `labels`

3. **Use Case Bonus** (0.0-0.2)
   - +0.2 for datasets matching specific use cases
   - Based on primary/secondary mappings

4. **Validation Bonus** (0.0-0.1)
   - +0.1 for datasets with validation splits
   - Ensures proper evaluation capability

### Ranking Priority

Datasets are ranked by:

1. **Embedding Suitability Score** (primary)
2. **Quality Score** (secondary)
3. **Annotation Coverage** (tertiary)

---

## Usage Examples

### Basic Discovery

```python
# Discover all embedding-friendly datasets
result = await eds_discover_embedding_datasets()
```

### Modality-Specific Discovery

```python
# Discover image datasets for similarity tasks
result = await eds_discover_embedding_datasets(
    modality="image",
    use_case="similarity",
    min_annotation_coverage=0.9
)
```

### Hardware-Constrained Discovery

```python
# Discover datasets for low-VRAM systems
result = await eds_discover_embedding_datasets(
    hardware_constraints={
        "vram_gb": 2,
        "max_dataset_size_gb": 10
    }
)
```

### Flexible Annotation Requirements

```python
# Allow datasets without validation splits
result = await eds_discover_embedding_datasets(
    require_validation_split=False,
    min_annotation_coverage=0.7
)
```

---

## Output Format

### Response Structure

```json
{
  "success": true,
  "data": {
    "embedding_datasets": [...],
    "total_found": 15,
    "filters_applied": {
      "modality": "text",
      "use_case": "similarity",
      "min_annotation_coverage": 0.8,
      "require_validation_split": true,
      "hardware_constraints": {"vram_gb": 4}
    },
    "annotation_summary": {
      "total_datasets": 15,
      "datasets_with_validation": 12,
      "validation_percentage": 80.0,
      "average_annotation_coverage": 0.87,
      "annotation_types_available": ["labels", "embeddings", "pairs"],
      "annotation_types_count": 3
    },
    "timestamp": "2025-01-17T10:30:00Z"
  }
}
```

### Dataset Entry Format

```json
{
  "name": "huggingface_hub",
  "category": "nlp_datasets",
  "base_url": "https://huggingface.co/datasets",
  "download_url": "https://huggingface.co/datasets/{dataset_name}",
  "categories": ["text", "multimodal"],
  "formats": ["json", "parquet", "csv"],
  "verification": {
    "status": "online",
    "response_time": 245,
    "last_checked": "2025-01-17T10:30:00Z"
  },
  "auth_required": false,
  "notable_datasets": ["squad", "glue", "imdb"],
  "annotation_support": true,
  "validation_sets": true,
  "embedding_friendly": true,
  "annotation_types": ["labels", "embeddings", "pairs"],
  "annotation_coverage": 0.95,
  "embedding_suitability_score": 0.87,
  "quality_score": 0.9,
  "estimated_memory_gb": 3.2,
  "annotation_details": {
    "annotation_types": ["labels", "embeddings", "pairs"],
    "validation_sets": true,
    "annotation_coverage": 0.95,
    "formats": ["json", "parquet"],
    "quality_assurance": {},
    "embedding_ready": true
  }
}
```

---

## Best Practices

### 1. Start with Conservative Filters

```python
# Begin with strict requirements
result = await eds_discover_embedding_datasets(
    min_annotation_coverage=0.9,
    require_validation_split=True
)
```

### 2. Progressively Relax Constraints

```python
# If no results, reduce requirements
result = await eds_discover_embedding_datasets(
    min_annotation_coverage=0.7,
    require_validation_split=False
)
```

### 3. Consider Hardware Limitations

```python
# Match your actual hardware
result = await eds_discover_embedding_datasets(
    hardware_constraints={
        "vram_gb": 4,  # GTX 1050 Ti
        "max_dataset_size_gb": 20
    }
)
```

### 4. Use Modality-Specific Searches

```python
# Better results with specific modalities
for modality in ["text", "image", "audio"]:
    result = await eds_discover_embedding_datasets(modality=modality)
```

### 5. Validate Dataset Quality

```python
# Check verification status
for dataset in result["data"]["embedding_datasets"]:
    if dataset["verification"]["status"] != "online":
        print(f"Warning: {dataset['name']} is not accessible")
```

---

## Hardware Considerations

### VRAM Constraints

The tool respects VRAM limitations by:

- Filtering datasets requiring >2x available VRAM
- Providing memory estimates for each dataset
- Prioritizing memory-efficient datasets

### Memory Estimation

Memory estimates include:

- Dataset loading requirements
- Model inference memory
- Batch processing overhead
- Gradient storage (for training)

### Optimization Recommendations

1. **Use Progressive Loading**
   - Load datasets in chunks
   - Implement streaming for large datasets

2. **Enable Memory Mapping**
   - Use memory-mapped files when possible
   - Reduce RAM usage for large datasets

3. **Optimize Batch Sizes**
   - Use smaller batches for limited VRAM
   - Implement gradient accumulation

---

## Troubleshooting

### Common Issues

#### 1. No Datasets Found

**Symptoms**: Empty results with strict filters

**Solutions**:

- Reduce `min_annotation_coverage` (try 0.7)
- Set `require_validation_split=False`
- Use `modality="all"` for broader search
- Increase `hardware_constraints.vram_gb`

#### 2. Low-Quality Results

**Symptoms**: Datasets with poor embedding suitability scores

**Solutions**:

- Increase `min_annotation_coverage` (try 0.9)
- Use specific `use_case` filtering
- Focus on academic/research repositories
- Check annotation types for relevance

#### 3. Memory Issues

**Symptoms**: Datasets exceed hardware capabilities

**Solutions**:

- Lower `hardware_constraints.vram_gb`
- Set `max_dataset_size_gb` limit
- Use progressive loading techniques
- Consider dataset subsampling

#### 4. Verification Failures

**Symptoms**: Datasets marked as offline or error

**Solutions**:

- Check network connectivity
- Verify API keys for authenticated sources
- Use alternative datasets with similar characteristics
- Report persistent issues to EDS maintainers

### Debugging Tips

1. **Check Filters**

   ```python

   # Review applied filters

   print(result["data"]["filters_applied"])
   ```

2. **Examine Annotation Summary**

   ```python

   # Understand annotation landscape

   print(result["data"]["annotation_summary"])
   ```

3. **Validate Hardware Compatibility**

   ```python

   # Check memory estimates

   for dataset in result["data"]["embedding_datasets"]:
       if dataset["estimated_memory_gb"] > 4:
           print(f"High memory: {dataset['name']}")
   ```

4. **Test Dataset Access**

   ```python

   # Verify dataset availability

   for dataset in result["data"]["embedding_datasets"]:
       if dataset["verification"]["status"] != "online":
           print(f"Offline: {dataset['name']}")
   ```

---

## Advanced Usage

### Custom Scoring

For specialized requirements, consider implementing custom scoring:

```python
def custom_embedding_score(dataset):
    score = dataset["embedding_suitability_score"]
    
    # Bonus for specific annotation types
    if "embeddings" in dataset["annotation_types"]:
        score += 0.2
    
    # Penalty for large datasets
    if dataset["estimated_memory_gb"] > 8:
        score -= 0.1
    
    return max(0, min(1, score))
```

### Batch Processing

For processing multiple use cases:

```python
use_cases = ["classification", "similarity", "retrieval"]
results = {}

for use_case in use_cases:
    results[use_case] = await eds_discover_embedding_datasets(
        use_case=use_case,
        min_annotation_coverage=0.8
    )
```

### Integration with Training Pipeline

```python
# Discover datasets
datasets = await eds_discover_embedding_datasets(
    modality="text",
    use_case="similarity",
    hardware_constraints={"vram_gb": 4}
)

# Filter for best candidates
best_datasets = [
    d for d in datasets["data"]["embedding_datasets"]
    if d["embedding_suitability_score"] > 0.8
]

# Prepare for training
for dataset in best_datasets:
    print(f"Training candidate: {dataset['name']}")
    print(f"Memory requirement: {dataset['estimated_memory_gb']}GB")
    print(f"Annotation coverage: {dataset['annotation_coverage']}")
```

---

## Conclusion

The `eds_discover_embedding_datasets` tool provides a comprehensive solution for discovering high-quality, annotation-rich datasets suitable for embedding training on consumer hardware. By combining intelligent filtering, quality scoring, and hardware awareness, it enables efficient dataset selection for ImpressionCore's embedding training pipeline.

For additional support or feature requests, refer to the ImpressionCore documentation or contact the development team.

---

*Last Updated: January 17, 2025*  
*Version: 1.0*  
*Component: ImpressionCore EDS MCP Server*