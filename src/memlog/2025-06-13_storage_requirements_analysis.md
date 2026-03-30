# ImpressionCore Storage Requirements Analysis
**Date**: June 13, 2025  
**Status**: Critical Infrastructure Planning  
**Priority**: HIGH - Storage capacity planning for model training

## Current Drive Space Analysis

### Available Storage:
- **C: Drive**: 53.9 GB free / 248.9 GB total (System drive - 21.7% free)
- **D: Drive**: 45.4 GB free / 250.1 GB total (19.1% free)  
- **G: Drive**: 163.5 GB free / 449.0 GB total (36.4% free)
- **H: Drive**: [Not accessible/mounted]

### Current Project Size:
- **ImpressionCore**: ~104.4 GB (97.2 GB actual project data)
- **Location**: D:\Projects\impressioncore

## Model Training Storage Requirements

### 1. Training Dataset Storage
**Text Datasets:**
- Common Crawl subset: 50-100 GB compressed
- Wikipedia dumps: 20-30 GB
- Books corpus: 10-20 GB
- Code repositories: 15-25 GB
- **Total Raw Text**: ~100-175 GB

**Preprocessed Training Data:**
- Tokenized sequences: 2x raw size = 200-350 GB
- Attention masks: 0.5x raw size = 50-87 GB
- Position embeddings: 10-20 GB
- **Total Preprocessed**: ~260-457 GB

### 2. Model Weights and Checkpoints
**Base Model Weights:**
- Teacher model (large): 2-7 GB
- Student model (optimized): 500MB-2GB
- Intermediate checkpoints: 20-50 GB (10-25 saves)
- **Total Model Storage**: ~23-59 GB

### 3. Training Infrastructure
**Gradient and Optimizer States:**
- AdamW optimizer states: 3x model size
- Gradient accumulation: 2x model size  
- Mixed precision buffers: 1x model size
- **Total Training States**: ~12-36 GB

### 4. Validation and Testing
**Evaluation Datasets:**
- Validation sets: 10-20 GB
- Test benchmarks: 5-10 GB
- Performance logs: 1-5 GB
- **Total Validation**: ~16-35 GB

### 5. Knowledge Distillation Specific
**Teacher Model Outputs:**
- Soft targets cache: 50-100 GB
- Attention transfer data: 20-40 GB
- Feature matching data: 15-30 GB
- **Total KD Data**: ~85-170 GB

## TOTAL STORAGE REQUIREMENTS

### Conservative Estimate: **394-757 GB**
### Realistic Working Space: **500-1000 GB**
### Recommended Safety Buffer: **1.2-1.5 TB**

## Current Storage Capacity Assessment

### ⚠️ CRITICAL ISSUES:
1. **D: Drive**: Only 45.4 GB free - INSUFFICIENT for training
2. **C: Drive**: Only 53.9 GB free - System drive, not recommended for data
3. **G: Drive**: 163.5 GB free - Still insufficient for full training pipeline

### IMMEDIATE REQUIREMENTS:
- **Minimum needed**: 500 GB additional free space
- **Recommended**: 1 TB additional storage
- **Current deficit**: 350-850 GB

## Storage Optimization Strategies

### 1. Data Management
```python
# Implement streaming data loading
class StreamingDataset:
    def __init__(self, data_dir, chunk_size_gb=2):
        self.chunk_size = chunk_size_gb * 1024**3
        self.current_chunk = None
        
    def load_chunk_on_demand(self, index):
        # Load only what's needed in memory
        chunk_idx = index // self.chunk_size
        if self.current_chunk != chunk_idx:
            self.current_chunk = self.load_chunk(chunk_idx)
```

### 2. Progressive Training
```python
# Training phases to minimize storage peaks
TRAINING_PHASES = {
    'phase_1': {'data_size': '50GB', 'duration': '2-3 days'},
    'phase_2': {'data_size': '150GB', 'duration': '5-7 days'},  
    'phase_3': {'data_size': '300GB', 'duration': '10-14 days'}
}
```

### 3. Checkpoint Management
```python
# Automatic cleanup of old checkpoints
MAX_CHECKPOINTS = 5  # Keep only last 5
CHECKPOINT_CLEANUP_SCHEDULE = "every_epoch"
```

## URGENT ACTIONS REQUIRED

### 1. Storage Expansion (CRITICAL)
- [ ] Add external drive (1-2 TB minimum)
- [ ] Consider cloud storage for datasets
- [ ] Implement data archiving system

### 2. G: Drive Utilization
- [ ] Move training data to G: drive (largest available)
- [ ] Implement cross-drive training pipeline
- [ ] Monitor G: drive space during training

### 3. Data Pipeline Optimization
- [ ] Implement streaming data loaders
- [ ] Create checkpoint rotation system
- [ ] Set up automated cleanup scripts

## RECOMMENDATION: Do NOT proceed with full training until storage requirements are met

**Minimum Action**: Add 1TB external storage before beginning serious model training.

---
**Next Steps**: Storage procurement and data pipeline implementation
