# ImpressionCore Model Training Guide

## Monitoring and Debugging

### 1. Memory Usage Tracking

```python
from src.utils.memory_optimization import monitor_memory_usage, track_memory_usage

# Monitor overall memory usage
memory_stats = monitor_memory_usage()
print(f"Current memory: {memory_stats['current_gb']:.2f} GB")
print(f"Peak memory: {memory_stats['max_gb']:.2f} GB")

# Use the decorator to track specific functions
@track_memory_usage
def train_epoch(model, dataloader):
    # Implementation
    pass
```

### 2. Training Visualization

ImpressionCore includes a browser-based dashboard for real-time monitoring:

```python
from src.visualization import start_training_dashboard

# Start the dashboard server (access at http://localhost:8080)
dashboard = start_training_dashboard(model, interval_seconds=5)

# In your training loop, update metrics
for epoch in range(epochs):
    # Training code
    dashboard.update({
        'loss': current_loss,
        'lr': current_lr,
        'memory_usage': memory_stats['current_gb'],
        'epoch': epoch
    })
```

### 3. Debugging Out-of-Memory Issues

When encountering OOM errors:

```python
from src.utils.memory_optimization import debug_memory_usage

# Analyze model for memory bottlenecks
memory_analysis = debug_memory_usage(model, sample_input)
print(f"Largest modules by memory:")
for module_name, memory_gb in memory_analysis['module_sizes']:
    print(f"- {module_name}: {memory_gb:.2f} GB")

# Suggested optimizations
for suggestion in memory_analysis['suggestions']:
    print(f"- {suggestion}")
```

## Training Configurations

### 1. Low VRAM Configuration (4GB)

For hardware like GTX 1050 Ti:

```yaml
# config_low_vram.yaml
model:
  hidden_size: 512
  num_layers: 8
  intermediate_size: 1024
  num_heads: 8
  
training:
  precision: "float16"
  gradient_checkpointing: true
  attention_chunk_size: 64
  batch_size: 1
  gradient_accumulation_steps: 16
  effective_batch_size: 16  # batch_size * gradient_accumulation_steps
  cpu_offload: true
  offload_optimizer: true
  scheduler: "cosine"
  learning_rate: 5e-5
  warmup_steps: 100
  max_steps: 10000
```

### 2. Medium VRAM Configuration (8GB)

For hardware like RTX 2060:

```yaml
# config_medium_vram.yaml
model:
  hidden_size: 768
  num_layers: 12
  intermediate_size: 2048
  num_heads: 12
  
training:
  precision: "float16"
  gradient_checkpointing: true
  attention_chunk_size: 128
  batch_size: 2
  gradient_accumulation_steps: 8
  effective_batch_size: 16
  cpu_offload: false
  scheduler: "cosine"
  learning_rate: 5e-5
  warmup_steps: 100
  max_steps: 10000
```

### 3. High VRAM Configuration (16GB+)

For hardware like RTX 3090:

```yaml
# config_high_vram.yaml
model:
  hidden_size: 1024
  num_layers: 24
  intermediate_size: 4096
  num_heads: 16
  
training:
  precision: "bfloat16"  # More stable than float16 for training
  gradient_checkpointing: false
  batch_size: 8
  gradient_accumulation_steps: 2
  effective_batch_size: 16
  cpu_offload: false
  scheduler: "cosine"
  learning_rate: 5e-5
  warmup_steps: 100
  max_steps: 10000
```

## Advanced Training Techniques

### 1. Distributed Training

For multi-GPU systems:

```python
from src.distributed import setup_distributed_training

# Initialize distributed environment
world_size, local_rank = setup_distributed_training()

# Load model with distributed settings
model = ImpressionModel.from_config(
    config,
    distributed=True,
    local_rank=local_rank
)

# Use DistributedDataParallel
from torch.nn.parallel import DistributedDataParallel
model = DistributedDataParallel(
    model, 
    device_ids=[local_rank],
    output_device=local_rank
)
```

### 2. DeepSpeed Integration

For advanced memory optimizations:

```python
from src.optimization import setup_deepspeed

# Configure DeepSpeed
ds_config = {
    "zero_optimization": {
        "stage": 2,
        "offload_optimizer": {
            "device": "cpu"
        },
        "contiguous_gradients": True
    },
    "fp16": {
        "enabled": True
    },
    "train_micro_batch_size_per_gpu": 1
}

# Initialize model and optimizer with DeepSpeed
model, optimizer, _, _ = setup_deepspeed(
    model=model,
    ds_config=ds_config,
    training_args=training_args
)
```

### 3. Mixed Precision Training with Automatic Mixed Precision

```python
from torch.cuda.amp import autocast, GradScaler

# Initialize scaler
scaler = GradScaler()

# Training loop with automatic mixed precision
for batch in dataloader:
    optimizer.zero_grad()
    
    # Forward pass with mixed precision
    with autocast():
        outputs = model(batch)
        loss = loss_function(outputs)
    
    # Scale loss and backprop
    scaler.scale(loss).backward()
    
    # Unscale gradients and optimizer step
    scaler.unscale_(optimizer)
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    scaler.step(optimizer)
    scaler.update()
```

## Checkpointing and Resuming Training

### 1. Efficient Checkpointing

```python
from src.utils.checkpointing import save_memory_efficient_checkpoint

# Save checkpoint with memory optimization
save_memory_efficient_checkpoint(
    model=model,
    optimizer=optimizer,
    scheduler=scheduler,
    path="./checkpoints/checkpoint_latest.pt",
    keep_in_cpu=True,  # Keep a copy in CPU memory
    shard_size_gb=1.0  # Split large models into smaller files
)
```

### 2. Resuming Training

```python
from src.utils.checkpointing import load_memory_efficient_checkpoint

# Resume from checkpoint
checkpoint = load_memory_efficient_checkpoint(
    path="./checkpoints/checkpoint_latest.pt",
    map_location="cuda",
    load_optimizer=True
)

model.load_state_dict(checkpoint['model'])
optimizer.load_state_dict(checkpoint['optimizer'])
scheduler.load_state_dict(checkpoint['scheduler'])
start_epoch = checkpoint['epoch']
```

## Conclusion

Training models with ImpressionCore on hardware with limited VRAM is made possible through these memory optimization techniques. By applying the right combination of optimizations for your specific hardware, you can train sophisticated models even on consumer-grade GPUs like the GTX 1050 Ti.

For further assistance, refer to:

- [Memory Optimization Guide](./memory_optimization.md)
- [Technical Memory Implementation Details](../technical/memory_optimizations.md)
- [API Reference](../api/memory_optimization_api.md)

Or join our community Discord server for user support and discussions on hardware-optimized AI development.
