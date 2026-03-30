# ImpressionCore Developer API Documentation

**Created:** June 09, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\api\developer\api_reference.md #api #attention_mechanism #command_line #cuda #deployment #documentation #gpu_optimization #inference #memory_management #performance #pytorch #security #testing #training #web_interface  
**Category:** Developer Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## 🚀 Quick Start Guide

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/impressioncore.git
cd impressioncore

# Set up Python environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify CUDA setup
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
```

### Your First Text Generation

```python
import asyncio
from src.services.text_generation import create_text_generation_service, GenerationConfig

async def main():
    # Create and initialize service
    service = create_text_generation_service()
    await service.initialize()
    
    # Generate text
    config = GenerationConfig(max_length=100, temperature=0.8)
    result = await service.generate_text("Hello, ImpressionCore!", config)
    
    print(f"Generated: {result.generated_text}")
    print(f"Speed: {result.tokens_per_second:.2f} tokens/sec")
    print(f"VRAM: {result.memory_used:.2f} GB")
    
    # Cleanup
    await service.cleanup()

# Run the example
asyncio.run(main())
```

---

## 📡 REST API Reference

### Base URL

``` text
http://localhost:8000/api/v1
```

### Authentication

```http
Authorization: Bearer your-api-key
```

### Health Check

**GET** `/health`

Check service health and system status.

```json
// Response
{
  "status": "healthy",
  "timestamp": "2025-01-09T10:30:00Z",
  "service_initialized": true,
  "cuda_available": true,
  "gpu_info": {
    "name": "NVIDIA GeForce GTX 1050 Ti",
    "memory_total": 4294967296,
    "memory_free": 3221225472
  }
}
```

### Text Generation

**POST** `/generate`

Generate text from a prompt with customizable parameters.

```json
// Request
{
  "prompt": "The future of AI is",
  "max_length": 512,
  "temperature": 0.8,
  "top_p": 0.9,
  "top_k": 50,
  "repetition_penalty": 1.1,
  "do_sample": true,
  "num_return_sequences": 1,
  "stream": false
}
```

```json
// Response
{
  "generated_text": "The future of AI is incredibly promising, with advances in local processing...",
  "input_text": "The future of AI is",
  "generation_time": 2.34,
  "tokens_per_second": 45.7,
  "memory_used": 2.1,
  "metadata": {
    "device": "cuda:0",
    "model_config": {...},
    "total_generations": 42
  }
}
```

### Streaming Text Generation

**POST** `/generate/stream`

Generate text with real-time streaming output.

```javascript
// JavaScript Example
fetch('/api/v1/generate/stream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-api-key'
  },
  body: JSON.stringify({
    prompt: "Tell me about local AI processing",
    max_length: 200,
    temperature: 0.8
  })
})
.then(response => {
  const reader = response.body.getReader();
  return new ReadableStream({
    start(controller) {
      function pump() {
        return reader.read().then(({ done, value }) => {
          if (done) {
            controller.close();
            return;
          }
          // Process streaming token
          const text = new TextDecoder().decode(value);
          console.log('Token:', text);
          controller.enqueue(value);
          return pump();
        });
      }
      return pump();
    }
  });
});
```

### Service Statistics

**GET** `/stats`

Get comprehensive service statistics and performance metrics.

```json
// Response
{
  "service_stats": {
    "total_generations": 1247,
    "total_tokens": 125847,
    "total_time": 2847.3,
    "average_speed": 44.2
  },
  "device_info": {
    "device": "cuda:0",
    "cuda_available": true,
    "gpu_name": "NVIDIA GeForce GTX 1050 Ti"
  },
  "memory_info": {
    "cuda_memory_allocated_gb": 2.1,
    "cuda_memory_reserved_gb": 2.3,
    "cuda_memory_free_gb": 1.7,
    "cpu_percent": 15.2,
    "memory_percent": 45.8
  },
  "model_info": {
    "initialized": true,
    "generating": false,
    "config": {...}
  }
}
```

### Memory Monitoring

**GET** `/monitoring/memory`

Get real-time memory usage and monitoring data.

```json
// Response
{
  "current_memory": {
    "cuda_memory_allocated_gb": 2.1,
    "cuda_memory_free_gb": 1.7,
    "cpu_percent": 12.4,
    "memory_percent": 42.1
  },
  "monitoring_history": [
    {
      "timestamp": 1704798600.123,
      "stage": "pre_generation",
      "cuda_memory_allocated": 2251225472,
      "cuda_memory_reserved": 2415919104,
      "cpu_percent": 15.2
    }
  ],
  "timestamp": 1704798654.789
}
```

---

## 🐍 Python SDK

### TextGenerationService

The core service class for text generation with CUDA optimization.

#### Constructor

```python
from src.services.text_generation import TextGenerationService
from src.core.config.model_config import ModelConfig

service = TextGenerationService(
    model_config=ModelConfig(),  # Optional model configuration
    device=None,                 # Auto-detected if None
    enable_monitoring=True       # Enable real-time monitoring
)
```

#### Methods

##### `async initialize() -> bool`

Initialize the service with model loading and CUDA setup.

```python
success = await service.initialize()
if success:
    print("Service ready for text generation")
else:
    print("Initialization failed")
```

##### `async generate_text(prompt, config=None, stream=False)`

Generate text from a prompt with optional configuration.

```python
from src.services.text_generation import GenerationConfig

# Create configuration
config = GenerationConfig(
    max_length=512,
    temperature=0.8,
    top_p=0.9,
    top_k=50,
    repetition_penalty=1.1,
    do_sample=True,
    num_return_sequences=1
)

# Generate text
result = await service.generate_text(
    prompt="The benefits of local AI processing include",
    config=config,
    stream=False
)

print(f"Generated: {result.generated_text}")
print(f"Performance: {result.tokens_per_second:.2f} tokens/sec")
```

##### `get_stats() -> Dict[str, Any]`

Get current service statistics and performance metrics.

```python
stats = service.get_stats()
print(f"Total generations: {stats['service_stats']['total_generations']}")
print(f"Average speed: {stats['service_stats']['average_speed']:.2f}")
print(f"Memory usage: {stats['memory_info']['cuda_memory_allocated_gb']:.2f} GB")
```

##### `async cleanup()`

Clean up resources and free memory.

```python
await service.cleanup()
```

### GenerationConfig

Configuration class for text generation parameters.

```python
from src.services.text_generation import GenerationConfig

config = GenerationConfig(
    max_length=512,         # Maximum generation length (1-2048)
    temperature=0.8,        # Sampling temperature (0.1-2.0)
    top_p=0.9,             # Top-p sampling threshold (0.1-1.0)
    top_k=50,              # Top-k sampling limit (1-100)
    repetition_penalty=1.1, # Repetition penalty (1.0-2.0)
    do_sample=True,        # Enable sampling
    num_return_sequences=1, # Number of sequences (1-5)
    early_stopping=True,   # Enable early stopping
    use_cache=True,        # Use model cache
    output_scores=False    # Return generation scores
)
```

### Context Manager Usage

```python
from src.services.text_generation import text_generation_service

async def example():
    async with text_generation_service() as service:
        # Service automatically initialized and cleaned up
        await service.initialize()
        
        result = await service.generate_text("Hello, world!")
        print(result.generated_text)
        
        # Automatic cleanup when context exits
```

---

## 🌐 Web Interface Integration

### Socket.IO Events

Real-time communication with the web interface using Socket.IO.

#### Client Events

```javascript
// Connect to server
const socket = io('http://localhost:5000');

// Listen for connection
socket.on('connect', () => {
    console.log('Connected to ImpressionCore');
});

// Initialize service
socket.emit('initialize_service');

// Start monitoring
socket.emit('start_monitoring');

// Generate text
socket.emit('generate_text', {
    prompt: "Hello, ImpressionCore!",
    config: {
        max_length: 100,
        temperature: 0.8
    }
});
```

#### Server Events

```javascript
// Service initialization result
socket.on('service_initialized', (data) => {
    if (data.success) {
        console.log('Service ready!');
    } else {
        console.error('Initialization failed');
    }
});

// Generation complete
socket.on('generation_complete', (data) => {
    console.log('Generated:', data.generated_text);
    console.log('Speed:', data.tokens_per_second, 'tokens/sec');
});

// Real-time monitoring updates
socket.on('monitoring_update', (data) => {
    console.log('VRAM usage:', data.service.memory_info.cuda_memory_allocated_gb, 'GB');
    console.log('CPU usage:', data.hardware.cpu_percent, '%');
});

// Error handling
socket.on('generation_error', (data) => {
    console.error('Generation failed:', data.error);
});
```

---

## 🔧 Configuration

### Model Configuration

```python
from src.core.config.model_config import ModelConfig

config = ModelConfig(
    # Model architecture settings
    vocab_size=50000,
    hidden_size=768,
    num_attention_heads=12,
    num_hidden_layers=12,
    intermediate_size=3072,
    
    # Memory optimization
    gradient_checkpointing=True,
    use_flash_attention=True,
    memory_efficient_attention=True,
    
    # Hardware specific
    max_memory_gb=3.5,  # GTX 1050 Ti safe limit
    device_map="auto",
    low_cpu_mem_usage=True
)
```

### Environment Variables

```bash
# API Configuration
IMPRESSIONCORE_API_HOST=0.0.0.0
IMPRESSIONCORE_API_PORT=8000
IMPRESSIONCORE_API_KEY=your-secure-api-key

# CUDA Configuration
CUDA_VISIBLE_DEVICES=0
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Memory Management
IMPRESSIONCORE_MAX_VRAM_GB=3.5
IMPRESSIONCORE_GRADIENT_CHECKPOINTING=true
IMPRESSIONCORE_MIXED_PRECISION=true

# Logging
IMPRESSIONCORE_LOG_LEVEL=INFO
IMPRESSIONCORE_ENABLE_MONITORING=true
```

---

## 📊 Performance Optimization

### GTX 1050 Ti Optimization

ImpressionCore is specifically optimized for the GTX 1050 Ti (4GB VRAM):

```python
# Recommended configuration for GTX 1050 Ti
config = GenerationConfig(
    max_length=512,      # Balanced length for memory
    temperature=0.8,     # Good quality/speed balance
    batch_size=1,        # Single batch for memory efficiency
    gradient_checkpointing=True,
    mixed_precision=True,
    memory_efficient_attention=True
)

# Memory management
service = create_text_generation_service(
    model_config=ModelConfig(max_memory_gb=3.5),
    enable_monitoring=True
)
```

### Performance Benchmarks

| Hardware | Avg Speed | Peak VRAM | Typical Response |
|----------|-----------|-----------|------------------|
| GTX 1050 Ti | 35-45 tokens/sec | 3.2GB | 2-4 seconds |
| GTX 1080 Ti | 65-85 tokens/sec | 5.5GB | 1-2 seconds |
| RTX 3070 | 95-120 tokens/sec | 4.8GB | < 1 second |

### Memory Optimization Tips

1. **Use gradient checkpointing** for large models
2. **Enable mixed precision** training and inference
3. **Limit batch size** to 1 for 4GB VRAM
4. **Monitor memory usage** with real-time monitoring
5. **Clear CUDA cache** between generations if needed

```python
import torch

# Clear CUDA cache
torch.cuda.empty_cache()

# Check memory usage
allocated = torch.cuda.memory_allocated() / 1024**3
print(f"VRAM allocated: {allocated:.2f} GB")
```

---

## 🛡️ Error Handling

### Common Errors and Solutions

#### Out of Memory (OOM)

```python
try:
    result = await service.generate_text(prompt, config)
except RuntimeError as e:
    if "out of memory" in str(e).lower():
        # Reduce generation length or enable memory optimization
        config.max_length = min(config.max_length // 2, 256)
        torch.cuda.empty_cache()
        result = await service.generate_text(prompt, config)
    else:
        raise
```

#### Service Not Initialized

```python
try:
    result = await service.generate_text(prompt)
except RuntimeError as e:
    if "not initialized" in str(e).lower():
        await service.initialize()
        result = await service.generate_text(prompt)
    else:
        raise
```

#### CUDA Not Available

```python
import torch

if not torch.cuda.is_available():
    print("CUDA not available, falling back to CPU")
    service = create_text_generation_service(device="cpu")
else:
    service = create_text_generation_service()  # Auto-detect CUDA
```

---

## 🧪 Testing and Validation

### Unit Testing

```python
import pytest
from src.services.text_generation import create_text_generation_service

@pytest.mark.asyncio
async def test_text_generation():
    service = create_text_generation_service()
    await service.initialize()
    
    result = await service.generate_text("Test prompt")
    
    assert result.generated_text is not None
    assert result.generation_time > 0
    assert result.tokens_per_second > 0
    
    await service.cleanup()

@pytest.mark.asyncio
async def test_memory_management():
    service = create_text_generation_service()
    await service.initialize()
    
    initial_stats = service.get_stats()
    initial_memory = initial_stats['memory_info']['cuda_memory_allocated_gb']
    
    # Generate multiple texts
    for i in range(5):
        await service.generate_text(f"Test prompt {i}")
    
    final_stats = service.get_stats()
    final_memory = final_stats['memory_info']['cuda_memory_allocated_gb']
    
    # Memory should not increase significantly
    memory_increase = final_memory - initial_memory
    assert memory_increase < 0.5  # Less than 500MB increase
    
    await service.cleanup()
```

### Integration Testing

```python
async def test_api_integration():
    # Test REST API endpoints
    import httpx
    
    async with httpx.AsyncClient() as client:
        # Health check
        response = await client.get("http://localhost:8000/api/health")
        assert response.status_code == 200
        
        # Text generation
        response = await client.post(
            "http://localhost:8000/api/generate",
            json={
                "prompt": "Integration test prompt",
                "max_length": 50
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "generated_text" in data
```

---

## 📝 Examples and Tutorials

### Example 1: Simple Text Generation

```python
import asyncio
from src.services.text_generation import create_text_generation_service

async def simple_generation():
    service = create_text_generation_service()
    
    try:
        await service.initialize()
        result = await service.generate_text("The benefits of local AI are")
        print(f"Generated: {result.generated_text}")
    finally:
        await service.cleanup()

asyncio.run(simple_generation())
```

### Example 2: Batch Processing

```python
async def batch_processing():
    prompts = [
        "Artificial intelligence will",
        "Privacy in AI means",
        "Local processing enables",
        "The future of computing",
        "Edge AI devices can"
    ]
    
    service = create_text_generation_service()
    await service.initialize()
    
    results = []
    for prompt in prompts:
        result = await service.generate_text(prompt)
        results.append({
            'prompt': prompt,
            'generated': result.generated_text,
            'speed': result.tokens_per_second
        })
        print(f"Processed: {prompt}")
    
    await service.cleanup()
    return results
```

### Example 3: Custom Web Application

```python
from flask import Flask, request, jsonify
from src.services.text_generation import create_text_generation_service

app = Flask(__name__)
service = None

@app.before_first_request
async def initialize():
    global service
    service = create_text_generation_service()
    await service.initialize()

@app.route('/generate', methods=['POST'])
async def generate():
    data = request.get_json()
    prompt = data.get('prompt')
    
    if not prompt:
        return jsonify({'error': 'Prompt required'}), 400
    
    try:
        result = await service.generate_text(prompt)
        return jsonify({
            'generated_text': result.generated_text,
            'generation_time': result.generation_time,
            'tokens_per_second': result.tokens_per_second
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

---

## 🔗 Additional Resources

### Documentation Links

- [Installation Guide](../installation.md)
- [Model Architecture](../architecture/b1-model.md)
- [Memory Optimization](../optimization/memory-management.md)
- [Security Guide](../security/privacy-first.md)
- [Deployment Guide](../deployment/production.md)

### Community

- **GitHub**: https://github.com/your-org/impressioncore
- **Discord**: https://discord.gg/impressioncore
- **Documentation**: https://docs.impressioncore.ai
- **Bug Reports**: https://github.com/your-org/impressioncore/issues

### Support

For technical support and questions:

- 📧 Email: support@impressioncore.ai
- 💬 Discord: #developer-support
- 📚 Docs: https://docs.impressioncore.ai
- 🐛 Issues: GitHub Issues

---

**🎉 Happy Developing with ImpressionCore!**

*Privacy-first, hardware-optimized AI for everyone.*
