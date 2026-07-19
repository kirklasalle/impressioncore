# User Guide

**Created:** April 19, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\user\user_guide.md #api #command_line #cuda #documentation #gpu_optimization #inference #memory_management #multimodal #training #web_interface #official #permanent [guide, user, comprehensive, b1-model, multimodal, 2025]  
**Category:** User Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

title: "ImpressionCore User Guide"
tags: [guide, user, comprehensive, b1-model, multimodal, 2025]
created: 2025-06-03
modified: 2025-08-09
version: 2.0.0
authors:

- "Kirk LaSalle"
- "GitHub Copilot"

status: active
category: user
priority: high

---

# ImpressionCore User Guide

## Enhanced Markdown Viewer & IDS UI/UX (2025-06-05)

- **Raw/Rendered Preview Toggle:** Switch between raw HTML and fully rendered (with diagrams) preview modes in the documentation editor.
- **Live Diagram Rendering:** Mermaid diagrams and other JS-based diagrams are now rendered in the preview (requires PyQtWebEngine).
- **Directory Tree Navigation:** The directory tree now supports expandable directories and file selection for easier navigation.
- **Global Theme Support:** The entire application supports dark/light mode, not just the editor.
- **Formatting Toolbar:** Added for markdown editing.
- **Synchronized Scrolling:** Editor and preview panes scroll together.
- **Multi-Tab Editing:** Edit multiple documents at once, with recent files tracking.
- **Tag-Based Filtering & Advanced Search:** Integrated with IDS tagging system for efficient document search and navigation.
- **IDS Integration:** Editor launchable from IDS menu; subprocess launch now sets PYTHONPATH for import reliability.
- **Requirements Updated:** PyQtWebEngine added to requirements.txt and doc_viewer/requirements.txt.
- **Verification:** Full system operation verified in both interactive and automated modes.

See the [Developer Guide](../developer/developer_guide.md) for technical details and [memlog entry](../../src/memlog/ids_uiux_diagram_theme_enhancement_2025-06-05.md) for changelog and verification.

---

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Core Features](#core-features)
6. [B1 Model Usage](#b1-model-usage)
7. [Multimodal Processing](#multimodal-processing)
8. [Memory Management](#memory-management)
9. [Web Interface](#web-interface)
10. [CLI Usage](#cli-usage)
11. [Configuration](#configuration)
12. [Troubleshooting](#troubleshooting)
13. [Advanced Features](#advanced-features)
14. [API Integration](#api-integration)
15. [Performance Optimization](#performance-optimization)

## Overview

ImpressionCore is a brain-inspired multimodal AI framework designed to run efficiently on consumer hardware. It provides comprehensive AI capabilities including text processing, image analysis, audio synthesis, and cross-modal understanding - all optimized for hardware with limited VRAM.

**Key Capabilities:**

- **Multimodal Processing**: Text, image, and audio input/output
- **Memory Efficient**: Optimized for 4GB VRAM (NVIDIA GTX 1050 Ti)
- **Brain-Inspired Architecture**: Cognitive simulation and adaptive memory
- **Real-time Processing**: Low-latency inference and generation
- **Extensible Framework**: Modular design for easy enhancement

## System Requirements

### Minimum Requirements

- **GPU**: NVIDIA GTX 1050 Ti (4GB VRAM) or equivalent
- **CPU**: Intel Core i5-4460 @ 3.20GHz or AMD equivalent
- **RAM**: 16GB DDR3/DDR4
- **Storage**: 10GB free space
- **OS**: Windows 10/11, Ubuntu 20.04+, macOS 10.15+

### Recommended Requirements

- **GPU**: NVIDIA RTX 3060 (12GB VRAM) or better
- **CPU**: Intel Core i7 or AMD Ryzen 7
- **RAM**: 32GB DDR4
- **Storage**: 50GB free space (SSD recommended)

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/impressioncore/impressioncore.git
cd impressioncore
```

### Step 2: Environment Setup

```bash
# Create virtual environment
python -m venv .venv310
source .venv310/bin/activate  # Linux/macOS
.venv310\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Initial Configuration

```bash
# Run setup script
python setup_environment.py

# Verify installation
python getting_started.py
```

## Quick Start

### Basic Usage Example

```python
from src.core import ImpressionCore
from src.models.b1_unified_model import B1UnifiedModel

# Initialize the framework
core = ImpressionCore()
model = B1UnifiedModel()

# Process text
result = model.process_text("Hello, ImpressionCore!")
print(result)

# Process image
image_result = model.process_image("path/to/image.jpg")
print(image_result.caption)

# Process audio
audio_result = model.process_audio("path/to/audio.wav")
print(audio_result.transcription)
```

### Web Interface

```bash
# Start the web server
python run_server.py

# Access the interface at http://localhost:5000
```

## Core Features

### B1 Unified Model

The B1 model is the core component providing multimodal processing:

```python
from src.models.b1_unified_model import B1UnifiedModel

model = B1UnifiedModel()

# Configure for your hardware
model.configure_memory_optimization(
    max_vram_gb=4.0,
    enable_gradient_checkpointing=True,
    use_mixed_precision=True
)
```

### Multimodal Pipeline

Process multiple input types simultaneously:

```python
# Multimodal processing
inputs = {
    'text': "Describe this scene",
    'image': "scene.jpg",
    'audio': "background.wav"
}

result = model.process_multimodal(inputs)
print(f"Scene: {result.description}")
print(f"Audio: {result.audio_analysis}")
```

## Multimodal Processing

### Text Processing

- **Tokenization**: Advanced tokenization with memory optimization
- **Embeddings**: High-dimensional text representations
- **Generation**: Text completion and creative writing
- **Understanding**: Semantic analysis and extraction

### Image Processing

- **Analysis**: Object detection and scene understanding
- **Captioning**: Automatic image description generation
- **Enhancement**: Image quality improvement
- **Generation**: Text-to-image synthesis (limited)

### Audio Processing

- **Speech Recognition**: High-accuracy transcription
- **Voice Synthesis**: Natural text-to-speech
- **Audio Analysis**: Music and sound classification
- **Voice Cloning**: Personalized voice generation

## Memory Management

ImpressionCore includes sophisticated memory management optimized for limited VRAM:

### Automatic Optimization

```python
# Memory optimization is enabled by default
model = B1UnifiedModel(auto_optimize_memory=True)

# Manual configuration
model.memory_manager.set_vram_limit(4.0)  # 4GB limit
model.memory_manager.enable_streaming()
```

### Performance Monitoring

```python
# Check memory usage
stats = model.get_memory_stats()
print(f"VRAM Used: {stats.vram_used_gb:.2f} GB")
print(f"Efficiency: {stats.efficiency_percent:.1f}%")
```

## Web Interface Usage

### Starting the Server

```bash
python run_server.py --port 5000 --host 0.0.0.0
```

### Features

- **Interactive Chat**: Text-based conversation interface
- **File Upload**: Process images and audio files
- **Real-time Processing**: Live results and feedback
- **Visualization**: Model performance and memory usage
- **Configuration**: Runtime parameter adjustment

### API Endpoints

- `POST /api/process/text` - Text processing
- `POST /api/process/image` - Image analysis
- `POST /api/process/audio` - Audio processing
- `POST /api/process/multimodal` - Combined processing
- `GET /api/status` - System status and health

## CLI Usage

### Basic Commands

```bash
# Process text from command line
python -m src.cli.text_processor "Your text here"

# Process image
python -m src.cli.image_processor path/to/image.jpg

# Process audio
python -m src.cli.audio_processor path/to/audio.wav

# Batch processing
python -m src.cli.batch_processor --input-dir ./data --output-dir ./results
```

### Advanced Options

```bash
# Configure memory limits
python -m src.cli.text_processor "Text" --max-vram 4.0 --optimize-memory

# Enable verbose logging
python -m src.cli.text_processor "Text" --verbose --log-level DEBUG

# Export results
python -m src.cli.text_processor "Text" --output-format json --save results.json
```

## Configuration

### Configuration Files

Main configuration is stored in `src/config.json`:

```json
{
  "model": {
    "name": "B1UnifiedModel",
    "max_vram_gb": 4.0,
    "enable_memory_optimization": true,
    "mixed_precision": true
  },
  "processing": {
    "batch_size": 1,
    "max_sequence_length": 2048,
    "enable_streaming": true
  },
  "server": {
    "host": "localhost",
    "port": 5000,
    "debug": false
  }
}
```

### Environment Variables

```bash
export IMPRESSIONCORE_VRAM_LIMIT=4.0
export IMPRESSIONCORE_DEBUG=true
export IMPRESSIONCORE_LOG_LEVEL=INFO
```

## Troubleshooting

### Common Issues

#### Out of Memory Errors

```bash
# Reduce batch size
python -m src.cli.text_processor "Text" --batch-size 1

# Enable memory optimization
python -c "from src.models.b1_unified_model import B1UnifiedModel; model = B1UnifiedModel(); model.optimize_for_low_memory()"
```

#### Performance Issues

- Check GPU utilization: `nvidia-smi`
- Monitor memory usage in web interface
- Reduce sequence length for faster processing
- Enable mixed precision training

#### Installation Problems

- Ensure CUDA is properly installed
- Check Python version compatibility (3.10+ recommended)
- Verify all dependencies are installed: `pip check`

### Getting Help

- Check the [Developer Guide](../developer/ARCHITECTURE.md)
- Review [API Documentation](../api/complete_api_reference.md)
- See [Troubleshooting Guide](../reference/TROUBLESHOOTING.md)

## Advanced Features

### Custom Model Training

```python
from src.training.trainer import ImpressionCoreTrainer

trainer = ImpressionCoreTrainer()
trainer.load_dataset("path/to/dataset")
trainer.configure_training(
    learning_rate=1e-4,
    batch_size=2,
    gradient_accumulation_steps=8
)
trainer.train()
```

### Plugin System

```python
from src.plugins import PluginManager

plugin_manager = PluginManager()
plugin_manager.load_plugin("custom_text_processor")
plugin_manager.register_handler("custom_task", my_handler)
```

### Brain Simulation Integration

```python
from src.brainsim.cognitive_arch import CognitiveArchitecture

cognitive = CognitiveArchitecture()
cognitive.initialize_memory_systems()
result = cognitive.process_with_context(input_data, context)
```

## API Integration

### Python SDK

```python
import impressioncore as ic

client = ic.Client(api_key="your-key")
result = client.process_text("Hello world")
```

### REST API

```bash
curl -X POST http://localhost:5000/api/process/text \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello world"}'
```

### WebSocket API

```javascript
const ws = new WebSocket('ws://localhost:5000/ws');
ws.send(JSON.stringify({
    type: 'process_text',
    data: {text: 'Hello world'}
}));
```

## Performance Optimization

### Hardware Optimization

- Use NVIDIA GPUs with CUDA support
- Ensure adequate VRAM (4GB minimum)
- Use fast storage (NVMe SSD recommended)
- Optimize CPU-GPU data transfer

### Software Optimization

- Enable mixed precision training
- Use gradient checkpointing
- Implement model parallelism for large models
- Optimize batch sizes for your hardware
- **TurboQuant KV Cache Compression** — Automatically compresses key-value cache during inference to 3.5 bits/channel, dramatically reducing VRAM usage for long conversations with zero quality loss

### TurboQuant KV Cache Configuration

TurboQuant is enabled by default in B3 models. To adjust settings:

```python
from src.core.models.impressioncore_b3_architecture import B3Config3B

config = B3Config3B(
    kv_cache_quantization="turboquant_3.5bit",  # or "turboquant_2.5bit" for aggressive mode
    kv_cache_bits=3.5,                           # 3.5 (default) or 2.5 (aggressive)
    kv_cache_use_qjl=True,                       # 1-bit residual correction
    kv_cache_rotation_type="hadamard",           # random rotation type
)
```

**VRAM savings at different context lengths:**

| Context Length | FP16 KV Cache | TurboQuant 3.5-bit | Saved |
|---------------|---------------|---------------------|-------|
| 4,096 tokens  | ~75 MB        | ~16 MB              | ~59 MB |
| 16,384 tokens | ~300 MB       | ~66 MB              | ~234 MB |
| 64,000 tokens | ~1.2 GB       | ~260 MB             | ~960 MB |

### Monitoring Performance

```python
from src.core.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor()
monitor.start_profiling()

# Your processing code here

stats = monitor.get_stats()
print(f"Processing time: {stats.total_time:.2f}s")
print(f"Memory peak: {stats.peak_memory_gb:.2f}GB")
```

## Appendix

### Related Documentation

- [Complete User Guide](../user_guide/complete_user_guide.md) - Detailed user documentation
- [User Guide Tools](user_guide_tools.md) - Available tools and utilities
- [Web UI Walkthrough](web_ui_walkthrough.md) - Web interface guide
- [CLI Build Walkthrough](../developer/cli_build_walkthrough.md) - Command-line usage
- [API Reference](../api/complete_api_reference.md) - Complete API documentation

### Support

- [GitHub Issues](https://github.com/impressioncore/impressioncore/issues)
- [Documentation](https://impressioncore.github.io/docs)
- [Community](https://discord.gg/impressioncore)

---

**Last Updated**: 2025-06-03  
**Version**: 2.0.0  
**Authors**: Kirk LaSalle, GitHub Copilot

---

## 2026-2027 Execution Alignment

For active delivery priorities and planned user-facing improvements, see:

- ../process/EXECUTION_APPENDIX_2026_2027.md

This includes B-series offering hardening, Builder and Dashboard continuity updates, and staged C1 Colossus rollout governance.
