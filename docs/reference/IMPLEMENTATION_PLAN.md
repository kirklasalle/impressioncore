# Implementation Plan

**Created:** March 09, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\IMPLEMENTATION_PLAN.md #attention_mechanism #cuda #docs\reference\implementation_plan.md #documentation #gpu_optimization #inference #memory_management #multimodal #performance #testing #tokenization #training #transformer  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

# ImpressionCore Implementation Plan

This document provides concrete implementation steps for the next phase of ImpressionCore development, based on the roadmap priorities.

## Core Model Implementation (Priority 1)

### 1. Transformer Architecture Implementation

```python
# Implementation steps for core transformer:
from torch import nn
import torch

class ImpressionTransformerBlock(nn.Module):
    def __init__(self, dim, num_heads=8, mlp_ratio=4, dropout=0.1, attn_dropout=0.1):
        super().__init__()
        # 1. Self-attention components
        self.norm1 = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(dim, num_heads, dropout=attn_dropout)
        
        # 2. Feed-forward components
        self.norm2 = nn.LayerNorm(dim)
        mlp_hidden_dim = int(dim * mlp_ratio)
        self.mlp = nn.Sequential(
            nn.Linear(dim, mlp_hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(mlp_hidden_dim, dim),
            nn.Dropout(dropout)
        )
        
    def forward(self, x):
        # Apply attention with residual connection
        attn_output, _ = self.attn(self.norm1(x), self.norm1(x), self.norm1(x))
        x = x + attn_output
        
        # Apply feed-forward with residual connection
        x = x + self.mlp(self.norm2(x))
        return x

# Memory optimization techniques:
def apply_gradient_checkpointing(model):
    """Enable gradient checkpointing to reduce memory usage during training"""
    if hasattr(model, "gradient_checkpointing_enable"):
        model.gradient_checkpointing_enable()
    return model

def setup_attention_chunking(model, chunk_size=128):
    """Configure attention chunking for reduced memory footprint"""
    # Implementation depends on the specific attention mechanism
    # This would modify the forward pass of attention layers
    pass
```

### 2. Diffusion Model Integration

```python
# Implementation approach for noise prediction network:
class DiffusionUNet(nn.Module):
    def __init__(self, in_channels, model_channels, out_channels, num_res_blocks):
        super().__init__()
        # Encoder blocks
        self.encoder = nn.ModuleList([
            # Resolution reducing blocks
        ])
        
        # Middle block with transformer attention
        self.middle = ImpressionTransformerBlock(model_channels)
        
        # Decoder blocks with skip connections
        self.decoder = nn.ModuleList([
            # Resolution increasing blocks
        ])
        
        # Output layer
        self.out = nn.Conv2d(model_channels, out_channels, kernel_size=3, padding=1)
    
    def forward(self, x, timesteps):
        # Timestep embedding
        emb = self.time_embedding(timesteps)
        
        # Process through encoder, save skip connections
        skips = []
        for block in self.encoder:
            x = block(x, emb)
            skips.append(x)
        
        # Process middle
        x = self.middle(x)
        
        # Process through decoder using skip connections
        for block in self.decoder:
            x = torch.cat([x, skips.pop()], dim=1)
            x = block(x, emb)
        
        return self.out(x)
```

## Pipeline Integration (Priority 2)

### 1. Tokenization Pipeline

Implement a unified tokenization system that can handle both text and images:

```python
class MultimodalTokenizer:
    def __init__(self, text_vocab_size=50257, image_patch_size=16):
        # Text tokenizer (using an existing model like GPT-2's tokenizer)
        self.text_tokenizer = AutoTokenizer.from_pretrained("gpt2")
        
        # Image tokenizer (convert images to patches)
        self.image_patch_size = image_patch_size
    
    def tokenize_text(self, text, max_length=512):
        """Convert text to token IDs"""
        return self.text_tokenizer(
            text,
            max_length=max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
    
    def tokenize_image(self, image):
        """Convert image to patches"""
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        
        # Convert to tensor if needed
        if not isinstance(image, torch.Tensor):
            transform = transforms.ToTensor()
            image = transform(image)
        
        # Extract patches
        B, C, H, W = image.shape
        patches = image.unfold(2, self.image_patch_size, self.image_patch_size) \
                       .unfold(3, self.image_patch_size, self.image_patch_size) \
                       .permute(0, 2, 3, 1, 4, 5) \
                       .flatten(3)
        
        return patches
    
    def encode_multimodal(self, text=None, image=None):
        """Process both text and image into a unified representation"""
        encodings = {}
        
        if text is not None:
            encodings["text"] = self.tokenize_text(text)
        
        if image is not None:
            encodings["image"] = self.tokenize_image(image)
            
        return encodings
```

### 2. Basic Inference Setup

Create a modular inference pipeline for both text and image generation:

```python
class InferencePipeline:
    def __init__(self, model, tokenizer, device="cuda"):
        self.model = model.to(device)
        self.tokenizer = tokenizer
        self.device = device
        
    def generate_text(self, prompt, max_length=100, temperature=0.7):
        """Generate text based on a prompt"""
        input_ids = self.tokenizer.tokenize_text(prompt).input_ids.to(self.device)
        
        # Simple greedy decoding for demo purposes
        for _ in range(max_length):
            outputs = self.model(input_ids)
            next_token_logits = outputs.logits[:, -1, :]
            
            # Apply temperature
            next_token_logits = next_token_logits / temperature
            
            # Get next token
            next_token = torch.argmax(next_token_logits, dim=-1).unsqueeze(-1)
            input_ids = torch.cat([input_ids, next_token], dim=-1)
            
            # Stop if EOS token
            if next_token.item() == self.tokenizer.text_tokenizer.eos_token_id:
                break
                
        return self.tokenizer.text_tokenizer.decode(input_ids[0])
    
    def generate_image(self, prompt, steps=50):
        """Generate image based on text prompt"""
        # Encode the prompt
        text_embeddings = self.model.encode_text(
            self.tokenizer.tokenize_text(prompt).input_ids.to(self.device)
        )
        
        # Start with random noise
        latents = torch.randn(
            (1, self.model.unet.in_channels, 64, 64),
            device=self.device
        )
        
        # Noise scheduler
        scheduler = DDPMScheduler(beta_start=0.00085, beta_end=0.012)
        
        # Denoise through diffusion steps
        for t in scheduler.timesteps:
            # Get model prediction
            with torch.no_grad():
                noise_pred = self.model.unet(
                    latents, 
                    t, 
                    encoder_hidden_states=text_embeddings
                )
            
            # Update latents with scheduler step
            latents = scheduler.step(noise_pred, t, latents).prev_sample
        
        # Decode latents to image
        with torch.no_grad():
            image = self.model.vae.decode(latents / 0.18215).sample
            
        # Process to PIL image
        image = (image / 2 + 0.5).clamp(0, 1)
        image = image.cpu().permute(0, 2, 3, 1).numpy()[0]
        image = Image.fromarray((image * 255).astype(np.uint8))
        
        return image
```

## Training Pipeline Development (Priority 3)

### Data Loading Systems

```python
class MultimodalDataset(torch.utils.data.Dataset):
    def __init__(self, text_data_path, image_data_path, tokenizer):
        self.text_data = self._load_text_data(text_data_path)
        self.image_data = self._load_image_data(image_data_path)
        self.tokenizer = tokenizer
        
    def _load_text_data(self, path):
        # Load text data from file or database
        pass
        
    def _load_image_data(self, path):
        # Load image data and paths
        pass
        
    def __len__(self):
        return min(len(self.text_data), len(self.image_data))
        
    def __getitem__(self, idx):
        text = self.text_data[idx]
        image_path = self.image_data[idx]
        
        # Load and process image
        image = Image.open(image_path).convert('RGB')
        
        # Tokenize both modalities
        encoded = self.tokenizer.encode_multimodal(
            text=text,
            image=image
        )
        
        return encoded
```

## Memory Optimization Implementation (Priority 4)

Implement specific memory optimization techniques for 4GB VRAM constraints:

```python
def optimize_for_low_vram(model, dtype=torch.float16):
    """Apply various memory optimizations for low VRAM environments"""
    # 1. Convert to 16-bit precision
    model.half()  # or .to(dtype)
    
    # 2. Enable gradient checkpointing
    apply_gradient_checkpointing(model)
    
    # 3. Enable attention chunking
    setup_attention_chunking(model)
    
    # 4. Implement activation offloading for large layers
    # This would require custom autograd function implementation
    
    return model

# Memory usage monitoring function
def monitor_memory_usage():
    """Track CUDA memory usage during model operation"""
    if torch.cuda.is_available():
        print(f"Current memory allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
        print(f"Max memory allocated: {torch.cuda.max_memory_allocated() / 1e9:.2f} GB")
        print(f"Memory cached: {torch.cuda.memory_reserved() / 1e9:.2f} GB")
```

## Testing Framework (Priority 5)

```python
class ModelBenchmark:
    def __init__(self, model, tokenizer, device="cuda"):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        
    def benchmark_inference_speed(self, prompt, iterations=10, max_length=100):
        """Measure text generation speed in tokens per second"""
        input_ids = self.tokenizer.tokenize_text(prompt).input_ids.to(self.device)
        
        start_time = time.time()
        tokens_generated = 0
        
        for _ in range(iterations):
            # Generate text
            tokens = self.model.generate(
                input_ids,
                max_length=max_length,
                do_sample=False  # Use greedy decoding for consistent measurements
            )
            tokens_generated += tokens.shape[1] - input_ids.shape[1]
            
        end_time = time.time()
        duration = end_time - start_time
        
        tokens_per_second = tokens_generated / duration
        print(f"Inference speed: {tokens_per_second:.2f} tokens/second")
        return tokens_per_second
    
    def benchmark_memory_usage(self, batch_size=1, sequence_length=512):
        """Measure peak memory usage during inference and training"""
        # Create dummy inputs
        inputs = torch.randint(
            0, 1000, 
            (batch_size, sequence_length),
            device=self.device
        )
        
        # Record baseline memory
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.empty_cache()
        baseline_memory = torch.cuda.memory_allocated()
        
        # Run inference
        outputs = self.model(inputs)
        
        # Record peak memory after inference
        inference_peak = torch.cuda.max_memory_allocated() - baseline_memory
        
        # Reset stats for training measurement
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.empty_cache()
        
        # Simulate backward pass
        loss = outputs.logits.sum()
        loss.backward()
        
        # Record peak training memory
        training_peak = torch.cuda.max_memory_allocated()
        
        print(f"Inference peak memory: {inference_peak / 1e9:.2f} GB")
        print(f"Training peak memory: {training_peak / 1e9:.2f} GB")
        
        return {
            "inference_peak_gb": inference_peak / 1e9,
            "training_peak_gb": training_peak / 1e9
        }
```

## Integration Plan Timeline

| Week | Focus Area | Key Deliverables |
|------|------------|------------------|
| 1    | Core Model | Basic transformer implementation with memory optimizations |
| 2    | Core Model | Diffusion model integration |
| 3    | Pipelines  | Text and image tokenization systems |
| 4    | Pipelines  | Basic inference implementation for text and images |
| 5    | Training   | Data loading and initial training configuration |
| 6    | Optimizations | Memory usage monitoring and optimization |
| 7    | Testing    | Benchmarking system for both speed and memory |
| 8    | Integration | Connect components to existing interfaces |

## Success Metrics

1. **Memory Efficiency**: Models run on 4GB VRAM GPU with peak usage <3.8GB
2. **Generation Speed**: Text generation >10 tokens/second on GTX 1050 Ti
3. **Quality Metrics**: Generated outputs match or exceed baseline models of similar size
4. **Integration**: All components work together in unified pipeline

## Next Steps

1. Set up development environment with proper monitoring tools
2. Implement core transformer block with memory optimizations
3. Create benchmarking system to track progress
4. Implement tokenization pipeline for text modality first, then expand to images
5. Integrate with existing user interfaces with simple demo capabilities

This implementation plan provides concrete next steps toward achieving Phase 2 goals from the roadmap.
