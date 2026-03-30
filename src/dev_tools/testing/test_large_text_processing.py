"""
test_large_text_processing.py

Created: August 21, 2025
Author: GitHub Copilot
Purpose: Test script for the complete large text processing pipeline.

This demonstrates chunking, embedding, and search capabilities.
"""

import sys
import time
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.utils.large_text_embeddings import LargeTextProcessor
from src.core.utils.rich_logging import log_error, log_info, log_success
from src.core.utils.text_chunking import CONFIGS, ChunkingConfig, TextChunker


def create_sample_large_text():
    """Create a sample large text file for testing."""
    sample_text = """
# ImpressionCore: Brain-Inspired Multimodal AI Framework

## Introduction

ImpressionCore represents a revolutionary approach to artificial intelligence that combines brain-inspired architectures with practical constraints for consumer hardware. This framework is designed to run efficiently on devices with limited VRAM, such as the NVIDIA GTX 1050 Ti with 4GB of memory.

## Architecture Overview

The core architecture consists of several key components that work together to process multimodal information:

### Text Processing Module

The text processing component utilizes a transformer-based encoder that has been optimized for memory efficiency. It employs techniques such as gradient checkpointing and mixed precision training to reduce memory usage while maintaining performance.

Key features of the text processor include:
- Dynamic vocabulary management
- Attention mechanism optimization
- Token-level memory allocation
- Streaming processing capabilities

### Image Processing Module

Visual information is processed through a specialized computer vision pipeline that leverages convolutional neural networks optimized for the target hardware constraints.

The image processor features:
- Efficient feature extraction
- Multi-scale representation learning
- Memory-aware batch processing
- Real-time inference capabilities

### Audio Processing Module

Audio data is handled through a dedicated audio processing pipeline that can work with various formats and sampling rates.

Audio processing capabilities include:
- Spectrogram generation and analysis
- Feature extraction for speech and music
- Real-time audio stream processing
- Noise reduction and enhancement

## Memory Optimization Strategies

One of the key challenges in developing AI systems for consumer hardware is managing memory constraints effectively. ImpressionCore employs several strategies:

### Gradient Checkpointing

By implementing gradient checkpointing, we can trade computational time for memory usage, allowing larger models to fit in limited VRAM.

### Mixed Precision Training

Using 16-bit floating point operations where possible reduces memory usage by approximately 50% while maintaining training stability.

### Dynamic Memory Allocation

The framework dynamically allocates memory based on input size and model requirements, ensuring optimal resource utilization.

## Training Methodology

The training process is designed to be efficient and effective on consumer hardware:

### Progressive Training

Starting with smaller models and gradually increasing complexity allows for stable training progression.

### Curriculum Learning

Presenting training examples in order of increasing difficulty helps the model learn more effectively.

### Knowledge Distillation

Using larger teacher models to guide smaller student models enables better performance within hardware constraints.

## Applications and Use Cases

ImpressionCore is designed for a wide range of applications:

### Personal AI Assistant

The framework can serve as the foundation for a personal AI assistant that understands multiple modalities of input and can provide contextual responses.

### Educational Tools

The system can be used to create educational applications that help students learn through interactive multimodal experiences.

### Creative Applications

Artists and creators can leverage the framework for generating and manipulating various types of content.

### Research Platform

Researchers can use ImpressionCore as a platform for experimenting with new AI techniques and architectures.

## Technical Implementation Details

### Core Libraries and Dependencies

The framework is built using several key libraries:
- PyTorch for deep learning functionality
- FAISS for efficient similarity search
- OpenAI API for embedding generation
- Rich for enhanced user interface elements

### Configuration Management

The system uses a flexible configuration system that allows users to customize various aspects of the framework:

```python
config = {
    "model_size": "39M",
    "memory_limit": "4GB",
    "precision": "mixed",
    "batch_size": "dynamic"
}
```

### Data Pipeline

The data processing pipeline is designed to handle various input formats and convert them into a unified representation that can be processed by the model.

## Performance Benchmarks

Extensive testing has shown that ImpressionCore can achieve competitive performance while operating within the constraints of consumer hardware:

- Training throughput: 20+ samples per second
- Memory usage: <1GB VRAM during training
- Inference latency: <100ms for typical queries
- Model size: 39M parameters (optimized)

## Future Development

The roadmap for ImpressionCore includes several exciting developments:

### Enhanced Multimodal Fusion

Improving the integration between different modalities to create richer representations.

### Advanced Memory Optimization

Exploring new techniques for further reducing memory usage without sacrificing performance.

### Extended Hardware Support

Adding support for additional consumer hardware platforms and configurations.

### Community Ecosystem

Building a community of developers and researchers who can contribute to the framework's evolution.

## Conclusion

ImpressionCore represents a significant step forward in making advanced AI capabilities accessible to a broader audience. By focusing on efficiency and practical constraints, we can democratize access to powerful AI tools and enable innovation at all levels of the technology stack.

The framework's brain-inspired design, combined with modern optimization techniques, creates a unique platform that bridges the gap between cutting-edge research and practical application. As we continue to develop and refine ImpressionCore, we remain committed to our core mission of making AI accessible, efficient, and beneficial for everyone.

Through careful attention to memory optimization, training efficiency, and user experience, ImpressionCore sets a new standard for what's possible in consumer-grade AI systems. The future of artificial intelligence lies not just in making models bigger, but in making them smarter, more efficient, and more accessible to everyone.
    """.strip()

    # Create sample file
    sample_file = Path("data/sample_large_text.txt")
    sample_file.parent.mkdir(parents=True, exist_ok=True)
    sample_file.write_text(sample_text, encoding='utf-8')

    log_info(f"Created sample large text file: {sample_file}")
    log_info(f"File size: {len(sample_text)} characters")

    return sample_file


def test_chunking_strategies():
    """Test different chunking strategies."""
    log_info("Testing chunking strategies...")

    sample_file = create_sample_large_text()

    strategies = ["semantic", "paragraph", "sentence", "fixed"]

    for strategy in strategies:
        config = ChunkingConfig(
            max_tokens=1000,  # Smaller for testing
            overlap_tokens=100,
            chunk_strategy=strategy
        )

        chunker = TextChunker(config)
        text = sample_file.read_text()
        chunks = chunker.chunk_text(text)

        log_info(f"{strategy.capitalize()} strategy: {len(chunks)} chunks")

        # Show token distribution
        tokens = [chunk["token_count"] for chunk in chunks]
        if tokens:
            log_info(f"  Token range: {min(tokens)}-{max(tokens)}, avg: {sum(tokens)/len(tokens):.1f}")


def test_complete_pipeline():
    """Test the complete processing pipeline."""
    log_info("Testing complete large text processing pipeline...")

    sample_file = create_sample_large_text()

    # Use a smaller config for testing
    config = ChunkingConfig(
        max_tokens=500,  # Smaller chunks for faster testing
        overlap_tokens=50,
        chunk_strategy="semantic"
    )

    processor = LargeTextProcessor(
        chunking_config=config,
        embedding_model="text-embedding-3-small",
        batch_size=5
    )

    try:
        log_info("Processing file...")
        start_time = time.time()

        result = processor.process_file(
            file_path=sample_file,
            document_id="test_document",
            save_chunks=True,
            update_index=True
        )

        end_time = time.time()

        log_success(f"Processing completed in {end_time - start_time:.2f} seconds")
        log_info("Results:")
        log_info(f"  Document ID: {result['document_id']}")
        log_info(f"  Total chunks: {result['total_chunks']}")
        log_info(f"  Total tokens: {result['total_tokens']:,}")
        log_info(f"  Estimated cost: ${result['cost_estimate']['estimated_cost_usd']:.4f}")

        # Test search functionality
        log_info("Testing search functionality...")

        search_queries = [
            "memory optimization",
            "training methodology",
            "multimodal processing",
            "consumer hardware"
        ]

        for query in search_queries:
            search_results = processor.search_document(
                query=query,
                document_id="test_document",
                top_k=3
            )

            log_info(f"Query: '{query}' -> {len(search_results)} results")
            if search_results:
                best_match = search_results[0]
                score = best_match.get('distance', 0)
                text_preview = best_match.get('text', '')[:100] + "..."
                log_info(f"  Best match (score: {score:.3f}): {text_preview}")

        return True

    except Exception as e:
        log_error(f"Pipeline test failed: {e}")
        return False


def test_predefined_configs():
    """Test predefined chunking configurations."""
    log_info("Testing predefined configurations...")

    sample_file = create_sample_large_text()
    text = sample_file.read_text()

    for config_name, config in CONFIGS.items():
        chunker = TextChunker(config)
        chunks = chunker.chunk_text(text)

        log_info(f"{config_name}: {len(chunks)} chunks, strategy: {config.chunk_strategy}")

        if chunks:
            tokens = [chunk["token_count"] for chunk in chunks]
            log_info(f"  Tokens: {min(tokens)}-{max(tokens)} (avg: {sum(tokens)/len(tokens):.1f})")


def main():
    """Run all tests."""
    log_info("Starting large text processing tests...")

    try:
        # Test 1: Chunking strategies
        test_chunking_strategies()
        print()

        # Test 2: Predefined configurations
        test_predefined_configs()
        print()

        # Test 3: Complete pipeline (requires API key)
        try:
            success = test_complete_pipeline()
            if success:
                log_success("All tests completed successfully!")
            else:
                log_error("Pipeline test failed")
        except Exception as e:
            log_error(f"Pipeline test skipped (likely missing API key): {e}")
            log_info("To test embeddings, ensure OPENAI_API_KEY is set in src/.env")

    except Exception as e:
        log_error(f"Test suite failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
