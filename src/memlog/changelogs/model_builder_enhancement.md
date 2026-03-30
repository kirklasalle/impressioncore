# Model Builder Changes

## 2025-03-23 09:14

### Changed

- Switched to Diffusion Transformer architecture
- Added latent head for representation learning
- Enabled memory-optimized MoE and UKS components

### Details

- Model Architecture:
  - 4 transformer layers
  - 256 hidden dimension
  - 8 attention heads
  - 1024 intermediate size
  - 128 latent dimension
  - 2 MoE experts
  - 256 UKS knowledge size

### Memory Optimizations

- FP16 mixed precision
- Gradient checkpointing
- Memory efficient attention
- Reduced expert and knowledge store sizes
- Batch size 16 with gradient accumulation 4

### Estimated Memory Usage

- Model parameters: ~0.8GB
- Activation buffers: ~0.7GB
- Total with safety margin: 2.0GB VRAM

### Diffusion Parameters

- 100 diffusion steps
- Cosine beta schedule
- Time embeddings enabled
- Latent head with VAE-style encoding
