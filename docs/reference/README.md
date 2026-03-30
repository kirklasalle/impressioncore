# Readme

**Created:** March 06, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\README.md #api #cuda #docs\reference\readme.md #documentation #memory_management #multimodal #performance #security #tokenization #transformer #web_interface  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

# Impression Core: Text and Image Tokenization Library

A Python library for efficient tokenization of both text and images using BPE (Byte-Pair Encoding) and learned patch-based tokenization.

## Project Overview

ImpressionCore is a brain-inspired multimodal AI framework designed to:

1. Process information across multiple modalities (text, images, audio, video).
2. Run efficiently on consumer hardware with limited VRAM (target: NVIDIA GTX 1050 Ti with 4GB VRAM).
3. Implement memory optimizations to enable complex AI functionality on constrained hardware.
4. Provide a secure digital identity management system.
5. Serve as a lifelong digital assistant focusing on user safety, growth, and wellness.

## Current Status

### Foundation Setup

- Core infrastructure, documentation, and web interface components are mostly complete.
- Tokenization system is partially implemented with text and image tokenizers.

### Core Development

- Brain-inspired architecture design is complete.
- Core transformer architecture is implemented.
- Diffusion layers and memory optimizations are under development.

### Documentation

- The roadmap has been consolidated into `next_steps_roadmap.md`.
- The `README` has been updated to provide a concise project overview and reference the detailed roadmaps.

## Features

- **Text Tokenization**: Byte-Pair Encoding with configurable vocabulary size.
- **Image Tokenization**: Patch-based encoding with multi-scale reconstruction.
- **Efficient Compression**: Average 8.2 unique tokens per image with SSIM ~0.34.
- **Brain-Inspired Architecture**: Modular design simulating advanced reasoning and communication.
- **Secure Digital Identity Management**: Quantum-resistant cryptography for privacy and security.
- **Interactive Demo**: GUI application for experimenting with tokenizers.

## Next Steps

### Immediate Actions (1-2 Weeks)

- Finalize the `/src/memlog` directory structure for logging and state management.
- Define API contracts and document security requirements.
- Train image tokenizers using VQ-VAE or K-means clustering.

### Short-Term Goals (1-2 Months)

- Implement secure digital identity management foundation.
- Develop task management and reminders system.
- Create benchmarks for tokenization speed and memory usage.

## Installation

```bash
pip install -e .
```

## Getting Started

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/impressioncore.git
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:

   ```bash
   python run_server.py
   ```

4. Access the interactive demo at `http://localhost:8000`.

For detailed setup instructions, refer to the [documentation](./docs/README.md).

## Quick Start

### Text Tokenization

```python
from src.tokenization.bpe import BPETokenizer

# Load trained tokenizer
tokenizer = BPETokenizer.load("data/tokenizers/text_tokenizer.json")

# Tokenize text
text = "Hello, world!"
tokens = tokenizer.encode(text)
reconstructed = tokenizer.decode(tokens)
```

### Image Tokenization

```python
import torch
from PIL import Image
from src.tokenization.image import ImageTokenizer

# Load trained tokenizer
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
tokenizer = ImageTokenizer.load("data/tokenizers/image_tokenizer.pt").to(device)

# Load and tokenize image
image = Image.open("image.jpg").convert('RGB')
image_tensor = tokenizer.transform(image).unsqueeze(0)
tokens = tokenizer.encode(image_tensor)
reconstructed = tokenizer.decode(tokens)
```

## Roadmap

The ImpressionCore project is currently in active development with the following status:

- **Phase 1: Foundation Setup** - Mostly complete
  - Core infrastructure, documentation, and web interface components are implemented.
  - Tokenization system is partially complete with text and image tokenizers implemented.

- **Phase 2: Core Development** - In progress
  - Brain-inspired architecture design is complete.
  - Core transformer architecture is implemented.
  - Diffusion layers and memory optimizations are under development.

For a detailed view of the project's current status and future plans, please refer to `docs/next_steps_roadmap.md` and `docs/development_roadmap.md`.

## License

MIT License
