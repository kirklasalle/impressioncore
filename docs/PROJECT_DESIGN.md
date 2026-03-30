# ImpressionCore-b1: Nano vLLM-Style Inference Engine Integration

**Created:** June 25, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\PROJECT_DESIGN.md #api #attention_mechanism #cuda #docs\project_design.md #documentation #inference #memory_management #multimodal #performance #pytorch #testing #tokenization #transformer #web_interface  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## Project Design Document: Fast, Modular, Multimodal Inference Engine

### Overview

This document details the design and implementation plan for integrating a Nano vLLM-style, fast, clean, and optimized inference engine into ImpressionCore-b1, with full support for multimodal input, Unified Knowledge Store (UKS), and BrainSimIII prompt augmentation.

---

## 1. Goals & Scope

- Achieve near-parity with vLLM/Nano-vLLM for offline inference speed and code clarity.
- Support text and image (multimodal) prompts.
- Integrate UKS and BrainSimIII for context-augmented inference.
- Maintain memory efficiency for GTX 1050 Ti (4GB VRAM).
- Provide a clean, well-documented, and extensible codebase.

---

## 2. Prioritized Task Breakdown

### Phase 1: Foundation & Planning

1. **Define unified prompt schema** (text, image, metadata fields)
2. **Design module interfaces** for inference, tokenization, model loading, cache, sampling, UKS, and BrainSimIII
3. **Update roadmap** to include this milestone

### Phase 2: Core Implementation

4. **Implement multimodal tokenizer** (`src/data/tokenization/tokenizer.py`)
5. **Develop model wrapper** (`src/models/wrapper.py`) with tensor parallelism, torch.compile, CUDA Graphs
6. **Build minimal inference engine** (`src/inference/engine.py`)
7. **Implement KV cache with prefix reuse** (`src/inference/cache.py`)
8. **Develop sampling engine** (`src/inference/sampling.py`)

### Phase 3: Integration

9. **Integrate UKS context retrieval** (`src/brainsim/memory/uks.py`)
10. **Integrate BrainSimIII prompt augmentation** (`src/brainsim/brainsim3.py`)
11. **Connect all modules in inference engine**

### Phase 4: Testing & Optimization

12. **Unit and integration tests** for all new modules
13. **Profile and optimize for memory/latency** (GTX 1050 Ti)
14. **Document all code and update onboarding guides**

### Phase 5: Documentation & Release

15. **Update `DOCUMENTATION_INDEX.md` and onboarding docs**
16. **Add code walkthroughs and diagrams to web UI**
17. **Announce and document milestone in roadmap**

---

## 3. Design Steps & Rationale

- Use functional, modular code for clarity and extensibility
- Minimize dependencies; prefer PyTorch and Hugging Face
- All modules must be memory-optimized and support multimodal data
- UKS and BrainSimIII are called before tokenization to augment prompt context
- Sampling and cache are pluggable for future research

---

## 4. Roadmap Update (Summary)

- **Q3 2025:**
  - Nano vLLM-style inference engine (multimodal, UKS, BrainSimIII)
  - Full documentation and onboarding
  - Memory and speed benchmarks
- **Q4 2025:**
  - Advanced visualization, further optimization, and user feedback integration

---

## 5. References

- [Nano vLLM](https://github.com/jllllll/nano-vllm)
- ImpressionCore Documentation Index
- ImpressionCore Prime Directive & Sacred Covenant

---

*This document is synchronized with the ImpressionCore roadmap and documentation system. All changes are timestamped and attributed.*

---

## 6. Nano vLLM Analysis & ImpressionCore-b1 Adaptation

### 6.1 Key Architectural Insights from Nano vLLM

- **Fast offline inference**: Comparable to vLLM, achieved via a lean execution pipeline.
- **Readable codebase**: ~1,200 lines, modular, clear separation of engine, cache, sampling, and model logic.
- **Optimization suite**: Prefix caching, tensor parallelism, torch.compile, CUDA Graphs.
- **API pattern**: `LLM` class (inherits from `LLMEngine`), `SamplingParams`, and a `generate()` method for inference.

### 6.2 Mapping Nano vLLM to ImpressionCore-b1 Modules

| Nano vLLM Component         | ImpressionCore-b1 Equivalent                | Notes |
|----------------------------|---------------------------------------------|-------|
| `LLM`, `LLMEngine`         | `src/inference/engine.py`                   | Main inference engine, user API |
| `SamplingParams`           | `src/inference/sampling.py`                 | Sampling config and logic |
| Prefix cache               | `src/inference/cache.py`                    | Extend for multimodal support |
| Model loading/wrapping     | `src/models/wrapper.py`                     | Add tensor parallel, torch.compile, CUDA Graphs |
| Tokenizer                  | `src/data/tokenization/tokenizer.py`        | Extend for text+image |
| Scheduler, block manager   | `src/inference/engine.py` (submodules)      | For advanced scheduling |
| Usage/benchmarks           | `examples/`, `benchmarks/`, web UI          | Add multimodal and context benchmarks |
| Context augmentation       | `src/brainsim/memory/uks.py`, `src/brainsim/brainsim3.py` | UKS and BrainSimIII integration |

### 6.3 Actionable Documentation Plan

1. **Architecture Overview**: Add diagrams and narrative for modular engine, cache, and sampling.
2. **API Reference**: Document main inference interface, config, and usage examples.
3. **Optimization Guide**: Explain prefix caching, tensor parallelism, torch.compile, CUDA Graphs, and hardware tuning.
4. **Integration Guide**: Document UKS/BrainSimIII hooks and multimodal extension points.
5. **Testing & Benchmarking**: Provide scripts and instructions for validating speed, memory, and multimodal performance.

### 6.4 Next Steps


---

## 7. Advanced Model Extensions: MoE and Latent Attention Heads

### 7.1 Mixture of Experts (MoE) Integration

- **Module:** `src/models/layers/moe.py`
- **Integration:**
  - Add `MoELayer` as a drop-in replacement or supplement for feedforward layers in transformer blocks.
  - Configure number of experts and gating in model config.
  - Update `src/models/wrapper.py` to allow model architectures to include MoE layers via config or constructor argument.
  - Ensure inference engine and cache logic are compatible with dynamic expert routing.
- **Design Note:** MoE can be enabled per-layer or globally. Gating can be softmax or top-k.

### 7.2 Latent Attention Heads Integration

- **Module:** `src/models/layers/latent_attention.py`
- **Integration:**
  - Replace standard multihead attention with `LatentMultiheadAttention` in transformer blocks.
  - Use a latent mask (learned or sampled) to control which heads are active per forward pass.
  - Expose configuration for number of latent heads and mask strategy in model wrapper.
  - Ensure compatibility with cache and sampling modules.
- **Design Note:** Latent heads can be used for regularization, efficiency, or adaptive computation.

### 7.3 Documentation & Testing

- Document API and configuration for enabling/disabling MoE and latent attention.
- Add unit and integration tests for new layers in `src/tests/models/layers/`.
- Benchmark performance and memory impact with and without these extensions.

---

### 8. Updated Project Next Steps

1. Integrate MoE and latent attention modules into model wrapper and transformer architectures.
2. Update inference engine to support dynamic expert routing and latent head activation.
3. Expand configuration and API docs for advanced model options.
4. Add tests and benchmarks for MoE and latent attention.
5. Update onboarding and developer docs to reflect new capabilities.
6. Announce milestone and document in roadmap and documentation index.

---
