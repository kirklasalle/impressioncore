# Memory Optimization Implementation Examples

This document provides practical, real-world examples of implementing memory optimizations for common scenarios in ImpressionCore.

## Table of Contents

1. [Running a Text Generation Model on 4GB GPU](#running-a-text-generation-model-on-4gb-gpu)
2. [Training a Medium-Sized Model on Limited Hardware](#training-a-medium-sized-model-on-limited-hardware)
3. [Running Stable Diffusion on 4GB VRAM](#running-stable-diffusion-on-4gb-vram)
4. [Processing Long Context Windows](#processing-long-context-windows)
5. [Multimodal Generation with Memory Constraints](#multimodal-generation-with-memory-constraints)
6. [Memory-Efficient Fine-Tuning](#memory-efficient-fine-tuning)

## Running a Text Generation Model on 4GB GPU

This example shows how to run a 1B parameter text generation model on a GTX 1050 Ti 4GB GPU:

```python
from src.utils.memory_optimization import optimize_for_low_vram
from src.models import ImpressionTextGenerator
import torch

# 1. Load model with 8-bit quantization
model = ImpressionTextGenerator.from_pretrained(
    "impression/text-generator-1b",
    load_in_8bit=True
)

# 2. Apply comprehensive memory optimizations
model = optimize_for_low_vram(
    model,
    dtype=torch.float16,        # Use FP16 precision
    cpu_offload=True,           # Enable CPU offloading
    chunk_size=64               # Small attention chunks
)

# 3. Configure generation parameters for memory efficiency
generation_config = {
    "max_new_tokens": 128,      # Limit output length
    "do_sample": True,          # Sampling uses less memory than beam search
    "temperature": 0.7,
    "top_p": 0.9,
    "use_cache": True,          # Enable KV caching (saves memory for generation)
    "pad_token_id": model.config.eos_token_id,
    "repetition_penalty": 1.2
}

# 4. Run inference with manual memory management
torch.cuda.empty_cache()        # Clear GPU cache before generation

# 5. Generate text
prompt = "ImpressionCore is a framework designed to"
with torch.no_grad():           # Disable gradient tracking
    output = model.generate(
        prompt,
        **generation_config
    )

print(output)

# 6. Clean up after generation
torch.cuda.empty_cache()
gc.collect()
```

### Key Memory Optimizations

- 8-bit quantization reduces model size by ~60%
- FP16 precision cuts memory in half compared to FP32
- CPU offloading moves less used parameters to CPU memory
- Small attention chunks reduce peak memory usage
- KV caching optimizes memory usage during generation
- Manual memory management with `empty_cache()`

## Training a Medium-Sized Model on Limited Hardware

This example demonstrates how to train a 350M parameter model on a 4GB GPU:

```python
from src.utils.memory_optimization import apply_gradient_checkpointing
from src.utils.training import train_with_accumulation
from src.models import ImpressionTransformer
import torch

# 1. Create a smaller model configuration
config = {
    "hidden_size": 512,         # Smaller hidden dimensions
    "num_layers": 8,            # Fewer layers
    "intermediate_size": 1024,  # Smaller FFN
    "num_attention_heads": 8,   # Fewer attention heads
}

# 2. Initialize model with mixed precision
model = ImpressionTransformer(config)
model = model.to(torch.bfloat16).cuda()  # BF16 more stable than FP16 for training

# 3. Apply gradient checkpointing
model = apply_gradient_checkpointing(model)

# 4. Use 8-bit optimizer to save memory
import bitsandbytes as bnb
optimizer = bnb.optim.AdamW8bit(
    model.parameters(),
    lr=5e-5,
    weight_decay=0.01
)

# 5. Configure training with gradient accumulation
training_args = {
    "batch_size": 1,             # Minimal batch size
    "accumulation_steps": 32,    # Accumulate for effective batch of 32
    "epochs": 3,
    "warmup_steps": 100,
    "fp16": False,               # Using BF16 instead
    "bf16": True,
    "learning_rate": 5e-5,
    "max_grad_norm": 1.0,
    "logging_steps": 10
}

# 6. Create memory-efficient dataloader
dataloader = create_dataloader(
    dataset,
    batch_size=training_args["batch_size"],
    pin_memory=False            # Avoid extra memory overhead
)

# 7. Train with accumulation and memory monitoring
train_with_accumulation(
    model=model,
    dataloader=dataloader,
    optimizer=optimizer,
    args=training_args,
    monitor_memory=True         # Track memory usage during training
)
```

### Key Memory Optimizations

- Smaller model architecture (512 hidden size instead of 768+)
- BF16 precision for stable training with reduced memory
- Gradient checkpointing sacrifices speed for memory savings
- 8-bit Adam optimizer reduces optimizer state memory by 75%
- Gradient accumulation allows small per-step batches
- Memory monitoring to catch OOM issues early

## Running Stable Diffusion on 4GB VRAM

This example shows how to run Stable Diffusion image generation on a 4GB GPU:

```python
from src.utils.memory_optimization import optimize_diffusion_model_for_low_vram
from src.models.diffusion import ImpressionDiffusionPipeline
import torch

# 1. Load model with CPU offloading and 8-bit UNet
pipeline = ImpressionDiffusionPipeline.from_pretrained(
    "impression/stable-diffusion-v2",
    torch_dtype=torch.float16,
    safety_checker=None          # Disable for memory savings
)

# 2. Apply comprehensive memory optimizations
pipeline = optimize_diffusion_model_for_low_vram(
    pipeline,
    dtype=torch.float16,         # FP16 precision
    enable_sequential_cpu_offload=True,  # Load components to GPU only when needed
    enable_attention_slicing=True,       # Slice attention operations
    enable_vae_slicing=True,             # Process VAE operations in slices
    enable_xformers_memory_efficient_attention=True  # Use xformers if available
)

# 3. Generate images with sequential processing and memory clearing
def generate_with_low_memory(prompt, height=512, width=512):
    # Clear cache before generation
    torch.cuda.empty_cache()
    gc.collect()
    
    # Generate with smaller resolution
    image = pipeline(
        prompt=prompt,
        height=height,
        width=width,
        num_inference_steps=25,  # Fewer steps save memory
        guidance_scale=7.5
    ).images[0]
    
    # Clear cache after generation
    torch.cuda.empty_cache()
    gc.collect()
    
    return image

# 4. Generate image
image = generate_with_low_memory(
    "a beautiful sunset over mountains, photorealistic",
    height=512,
    width=512
)
image.save("output.png")
```

### Key Memory Optimizations

- FP16 precision for model parameters
- Sequential CPU offloading (only one component in GPU at a time)
- Attention slicing to process attention in smaller chunks
- VAE slicing to decode images in patches
- Memory-efficient attention implementation
- Reduced image size (512x512 instead of 1024x1024)
- Memory clearing before and after generation

## Processing Long Context Windows

This example demonstrates processing very long text sequences (8K+ tokens) on limited memory:

```python
from src.utils.memory_optimization import setup_attention_chunking
from src.models import ImpressionLongContextModel
import torch

# 1. Load a context-optimized model
model = ImpressionLongContextModel.from_pretrained(
    "impression/context-lite-model"
)

# 2. Convert to lower precision
model = model.to(torch.float16).cuda()

# 3. Apply aggressive attention chunking for long sequences
model = setup_attention_chunking(
    model, 
    chunk_size=32  # Very small chunks for long context
)

# 4. Process long text in segments with sliding window
def process_long_text_with_sliding_window(text, model, window_size=1024, stride=768):
    tokens = tokenizer.encode(text)
    results = []
    
    # Process overlapping windows
    for i in range(0, len(tokens), stride):
        # Extract window with overlap
        window = tokens[i:i + window_size]
        
        # Clear cache between windows
        torch.cuda.empty_cache()
        
        # Process window
        with torch.no_grad():
            output = model(torch.tensor([window]).cuda())
            
        # Store results
        results.append(output)
        
    # Combine results (implementation specific to your task)
    return combine_results(results)

# 5. Apply to an 8K token document
with open("long_document.txt", "r") as f:
    long_text = f.read()

result = process_long_text_with_sliding_window(
    long_text,
    model,
    window_size=1024,
    stride=768
)

print(f"Processed document with {len(tokenizer.encode(long_text))} tokens")
```

### Key Memory Optimizations

- FP16 precision for all computations
- Very small attention chunks (32) to handle long sequences
- Sliding window approach to process text incrementally
- Memory clearing between processing windows
- Using a model variant optimized for context length

## Multimodal Generation with Memory Constraints

This example shows how to handle multimodal tasks efficiently with limited memory:

```python
from src.utils.memory_optimization import optimize_for_low_vram, selective_cpu_offload
from src.models import ImpressionMultimodalModel
import torch

# 1. Load model with optimizations
model = ImpressionMultimodalModel.from_pretrained(
    "impression/multimodal-mini"
)
model = model.to(torch.float16).cuda()

# 2. Apply selective offloading based on component use
# Keep vision encoder on GPU, move unused components to CPU
model = selective_cpu_offload(
    model,
    keep_modules=["vision_encoder"],  # Keep on GPU
    offload_modules=[                 # Move to CPU
        "audio_encoder", 
        "text_decoder.layers.0", 
        "text_decoder.layers.1"
    ]
)

# 3. Set up dynamic component loading
def multimodal_generate_with_memory_management(model, image, text_prompt):
    # 1. Process image first (vision encoder already on GPU)
    with torch.no_grad():
        image_features = model.encode_image(image)
    
    # 2. Clear unnecessary tensors
    del image
    torch.cuda.empty_cache()
    
    # 3. Move text decoder to GPU, keep image features
    model.text_decoder = model.text_decoder.cuda()
    
    # 4. Generate text based on image
    with torch.no_grad():
        output = model.generate_from_image_features(
            image_features, 
            text_prompt,
            max_length=128
        )
    
    # 5. Clean up
    torch.cuda.empty_cache()
    
    return output

# 4. Process image with text prompt
from PIL import Image
import requests
from io import BytesIO

# Load image
response = requests.get("https://example.com/image.jpg")
image = Image.open(BytesIO(response.content)).convert("RGB")
image_tensor = preprocess_image(image).unsqueeze(0).to("cuda", torch.float16)

# Generate caption
result = multimodal_generate_with_memory_management(
    model,
    image_tensor,
    "Describe this image:"
)

print(result)
```

### Key Memory Optimizations

- FP16 precision for all operations
- Selective component offloading based on task phase
- Dynamic loading of components when needed
- Strategic memory clearing between processing steps
- Single-sample processing to minimize memory footprint

## Memory-Efficient Fine-Tuning

This example demonstrates memory-efficient fine-tuning using parameter-efficient techniques:

```python
from src.utils.memory_optimization import optimize_for_training
from src.finetuning import apply_lora, create_peft_config
import torch
from peft import get_peft_model

# 1. Load base model in 8-bit
from transformers import AutoModelForCausalLM
base_model = AutoModelForCausalLM.from_pretrained(
    "impression/base-model-1b",
    load_in_8bit=True,
    device_map="auto"
)

# 2. Apply memory optimizations for training
base_model = optimize_for_training(
    base_model,
    precision="bfloat16",
    gradient_accumulation_steps=16
)

# 3. Create LoRA configuration for parameter-efficient fine-tuning
lora_config = create_peft_config(
    r=16,                       # LoRA rank
    lora_alpha=32,              # LoRA alpha
    target_modules=[            # Apply LoRA to specific modules
        "q_proj", "v_proj", "k_proj", "o_proj", 
        "gate_proj", "up_proj", "down_proj"
    ],
    bias="none",
    task_type="CAUSAL_LM"
)

# 4. Convert to LoRA model (trains only a small number of parameters)
model = get_peft_model(base_model, lora_config)

# 5. Configure optimizer to save memory
optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=2e-4,
    weight_decay=0.001,
    eps=1e-8
)

# 6. Set up memory-efficient training loop
def train_with_memory_efficiency(model, train_dataloader, optimizer, epochs):
    # Training loop with memory optimizations
    model.train()
    for epoch in range(epochs):
        for step, batch in enumerate(train_dataloader):
            # Move batch to device one element at a time to control memory
            inputs = {k: v.to(model.device) for k, v in batch.items()}
            
            # Forward pass
            outputs = model(**inputs)
            loss = outputs.loss / 16  # Dividing by gradient accumulation steps
            
            # Backward pass
            loss.backward()
            
            # Update only when accumulation complete
            if (step + 1) % 16 == 0:
                optimizer.step()
                optimizer.zero_grad()
                
                # Clear cache
                torch.cuda.empty_cache()
                
            # Log progress
            if step % 50 == 0:
                print(f"Epoch {epoch}, Step {step}, Loss {loss.item()}")
                
                # Monitor memory
                from src.utils.memory_optimization import monitor_memory_usage
                memory_stats = monitor_memory_usage()
                print(f"Memory usage: {memory_stats['current_gb']:.2f}GB")

# 7. Train the model
train_with_memory_efficiency(
    model, 
    train_dataloader, 
    optimizer,
    epochs=3
)

# 8. Save LoRA weights only (very small file)
model.save_pretrained("lora_weights")
```

### Key Memory Optimizations

- 8-bit base model loading reduces model memory by ~60%
- LoRA fine-tuning reduces trainable parameters by 99%
- BF16 precision for stable training with reduced memory
- Gradient accumulation for effective larger batches
- Controlled device placement of tensors
- Regular memory monitoring and clearing
- Saving only adapter weights (tiny compared to full model)

## Additional Tips for Extreme Memory Constraints

For cases where even the above optimizations aren't sufficient:

1. **Model Surgery**: Remove unnecessary model components

   ```python
   # Example: Remove embedding pooling layer if not needed
   model.embeddings.pooler = None
   ```

2. **Progressive Module Loading**: Load only parts of the model at a time

   ```python
   # Process through model layers sequentially
   activation = input_embedding
   for i, layer in enumerate(model.layers):
       # Move just this layer to GPU
       current_layer = layer.to("cuda")
       # Process
       activation = current_layer(activation)
       # Move back to CPU
       current_layer = current_layer.to("cpu")
   ```

3. **Activation Checkpointing with Custom Granularity**:

   ```python
   # Apply checkpointing to specific sub-components
   from torch.utils.checkpoint import checkpoint
   
   def custom_checkpoint_forward(module_list, x):
       for i, module in enumerate(module_list):
           x = module(x)
           if i % 2 == 0:  # Checkpoint every other module
               x = checkpoint(lambda y: module_list[i+1](y), x)
       return x
   ```

4. **Mixed Quantization Precision**:

   ```python
   # Use different precision for different parts
   model.embeddings = model.embeddings.to(torch.float16)
   model.transformer = quantize_model(model.transformer, bits=8)
   model.lm_head = model.lm_head.to(torch.float32)  # Keep critical parts in FP32
   ```

By combining these strategies, ImpressionCore can run sophisticated AI models even on hardware with severe memory constraints like the NVIDIA GTX 1050 Ti with only 4GB VRAM.
