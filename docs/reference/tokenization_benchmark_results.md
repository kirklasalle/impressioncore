# Tokenization Benchmark Results

**Created:** March 08, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\tokenization_benchmark_results.md #documentation #memory_management #performance #testing #tokenization  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

# Tokenization System Benchmark Results

This document provides benchmark results for the ImpressionCore tokenization system, analyzing both text and image tokenization performance on the GTX 1050 Ti hardware.

## Text Tokenization Performance

| Metric | Value |
|--------|-------|
| Vocabulary Size | 50,257 tokens |
| Average Encoding Time | 0.09 ms per sample |
| Average Decoding Time | 0.08 ms per sample |
| Reconstruction Accuracy | 100% (exact match) |
| Memory Usage | Minimal (<1MB) |

The text tokenizer demonstrates excellent performance with perfect reconstruction accuracy and very fast processing times. All test samples were correctly reconstructed without any loss of information.

### Special Token Handling

The text tokenizer correctly handles special tokens such as `<bos>` and `<eos>`, providing options to include them during encoding and skip them during decoding as needed.

## Image Tokenization Performance

| Metric | Value |
|--------|-------|
| Image Size | 256×256 pixels |
| Patch Size | 16×16 pixels |
| Codebook Size | 8,192 tokens |
| Number of Patches | 256 patches per image |
| Encoding Time | ~42.73 ms per image |
| Decoding Time | ~0.53 ms per image |
| Unique Tokens Used | 0.4% of codebook (currently only 1 token) |
| Reconstruction Quality | 5.41 dB PSNR (poor) |
| MSE | 0.287760 |

### Image Tokenization Issues

The image tokenizer currently shows suboptimal results:

1. **Low Token Variety**: Only a single token (2112) is being used repeatedly, indicating that the tokenizer is not properly representing the image diversity.
2. **Poor Reconstruction Quality**: The PSNR of 5.41 dB indicates very poor reconstruction quality.
3. **Underutilization of Codebook**: With 8,192 tokens available but only 1 being used, the codebook is severely underutilized.

### Root Cause Analysis

The primary issue is that the image tokenizer is using a **random codebook** that hasn't been properly trained with image data:
