# ImpressionCore User Guide (Updated 2025-04-22)

## Source of Truth Notice

This file is a mirror. Canonical user guide: docs/user/user_guide.md.
Sync policy: docs/process/DOCUMENTATION_CANONICALIZATION_PLAN_20260718.md.

---

## 1. Introduction & Overview

ImpressionCore is a brain-inspired, privacy-first digital twin AI. It features modular cognitive architecture, secure memory, and lifelong learning. See [impressioncore_b1_architecture.md](impressioncore_b1_architecture.md) for diagrams and technical details.

<a name="system-requirements"></a>

### System Requirements

- Minimum GPU: NVIDIA GTX 1050 Ti (4GB VRAM)
- CPU: Intel Core i5 4460 @ 3.20GHz or better
- RAM: 16GB (32GB recommended)
- OS: Windows, Linux, or macOS (latest versions recommended)
- Python: 3.10+
- Disk: 20GB free space

## 2. System & Environment Setup

- **System Requirements:** See [System Requirements](#system-requirements).
- **Installation:** Follow the steps for prerequisites, cloning, and Python environment setup.
- **GPU Setup:** See [GPU_SETUP.md](GPU_SETUP.md).
- **Memory Optimization:** See [memory_optimization_strategies.md](memory_optimization_strategies.md).
- **Verification:** Run `python getting_started.py` to check your environment.
- **Troubleshooting:** Use memlog and [troubleshoot.bat](../troubleshoot.bat) for diagnostics.

## 3. Data Preparation

- **Supported Data:** Text, images, audio, structured data.
- **Steps:** Ingest → validate → preprocess.
- **Tools:** Use the web UI or CLI for data upload and inspection.
- **References:** See [modal_engine_tokenizer_integration.md](modal_engine_tokenizer_integration.md).

### 3.1 Audio Data Support

ImpressionCore includes a world-class audio processing pipeline built on `librosa`, `torchaudio`, and `soundfile`.

**Supported Formats:** WAV, MP3, FLAC, OGG, AIFF

**Feature Extraction Capabilities:**

- **MFCC** (Mel-Frequency Cepstral Coefficients) — compact speech representation
- **Mel Spectrogram** — frequency-domain analysis optimized for human perception
- **Chroma Features** — harmonic/tonal content analysis
- **Tonnetz** — tonal centroid features for music and speech prosody
- **Spectral Contrast** — spectral peak vs. valley analysis
- **Zero-Crossing Rate** — signal periodicity detection
- **Voice Activity Detection (VAD)** — speech segment isolation

**Hardware Constraints (GTX 1050 Ti / 4GB VRAM):**

- Maximum audio duration: 30 seconds per chunk (configurable)
- Chunk-based processing for longer audio files (streaming mode)
- All feature extraction runs on CPU (zero VRAM impact)
- `torchaudio` transforms leverage CUDA when beneficial

**Advanced Capabilities:**

- Audio-Language Integration for cross-modal understanding
- Emotion recognition from speech features
- Speaker identification pipeline
- Real-time audio streaming support (planned)

**Installation:**

```bash
pip install librosa soundfile audioread
pip install torchaudio --index-url https://download.pytorch.org/whl/cu124
```

**References:** See [audio_processor.md](developer/components/audio_processor.md) for developer details.

## 4. Tokenization

- **Options:** BPE for text, custom for images.
- **Training:** Train or load tokenizers as needed.
- **Memory Efficiency:** See [memory_efficient_tokenization.md](memory_efficient_tokenization.md).

## 5. Model Definition

- **Template:** Select ImpressionCore-b1 in the UI.
- **Parameters:** Context window, memory, precision.
- **Advanced:** Enable Mixture of Experts, LoRA if available.
- **Interactive Configuration:** Use the interactive configuration UI to optimize settings for your hardware.
- **References:** [model_architecture.md](model_architecture.md).

## 6. Training

- **Configuration:** Set up training in the UI.
- **Monitoring:** Use UI or terminal for progress.
- **Checkpoints:** Saved automatically. See [CHECKPOINT_MANAGEMENT.md](CHECKPOINT_MANAGEMENT.md).

<a name="evaluation"></a>

## 7. Evaluation

- **Metrics:** Perplexity, BLEU, ROUGE.
- **Dashboard:** View results in the evaluation dashboard (see web UI Evaluation page).
- **Metrics Dashboard:** Use the dedicated metrics dashboard to visualize memory usage, model quality metrics, and advanced features performance.
- **API & Services:** Evaluation endpoints and services are available for automated and manual model assessment.
- **References:** [Evaluation Details](#7-evaluation).

## 8. Inference & Deployment

- **Inference:** Load models and run inference via UI or API.
- **Optimization:** See [inference_api.md](inference_api.md).

## 9. Dynamic Memory Management

- **Purpose:** Enables running larger models than might typically fit in VRAM by dynamically offloading and reloading model parts (layers or modules) between GPU and CPU memory based on available resources and operational needs.
- **Core Component:** `DynamicMemoryOptimizer` located in `src/core/memory/dynamic_manager.py`.
- **How it Works:**
  - Identifies candidate layers for offloading.
  - Monitors available GPU memory.
  - Strategically moves less-used or larger layers to CPU RAM when GPU memory is scarce and reloads them when needed for computation.
- **Usage:**
  - Import `DynamicMemoryOptimizer` from `src.core.memory.dynamic_manager`.
  - Initialize it with your model and (optionally) a list of module keys to consider for offloading.
  - Call the `adapt_to_available_memory()` method before critical sections like training loops or evaluation runs.
- **Benefits:** Allows for training and inference of more complex models on hardware with limited VRAM, such as the target NVIDIA GTX 1050 Ti.
- **Considerations:** Introduces some latency due to data transfers between CPU and GPU. The optimizer aims to minimize this by making intelligent decisions about what and when to offload/reload.
- **Integration Example:** See `src/training/evaluation/evaluate_cifar10.py` for an example of how it's integrated into an evaluation script.

## 10. Tokenization Benchmarking

- **Purpose:** To evaluate and compare the performance (speed and memory usage) of different tokenization strategies and implementations within ImpressionCore.
- **Tool:** `benchmark_tokenizer.py` located in `src/tools/`.
- **How to Use:**
  - The script can be configured to run benchmarks on various tokenizers (e.g., Hugging Face tokenizers, custom SentencePiece models) against different datasets.
  - Execute the script from the command line, specifying parameters such as tokenizer paths, dataset names, and batch sizes.
  - `python src/tools/benchmark_tokenizer.py --tokenizer_name_or_path <path_or_hf_name> --dataset_name <hf_dataset_name> --dataset_config <config_name> --text_column <col_name> --num_samples <N>`
- **Output:** The tool outputs metrics like tokenization speed (tokens/second or samples/second) and memory footprint.
- **Analysis:** Results help in selecting the most efficient tokenizer for specific tasks and hardware constraints, contributing to overall system performance, especially on memory-limited devices.
- **Further Details:** For detailed benchmark results, methodologies, and analysis, refer to [BENCHMARKING_TOOLS.md](BENCHMARKING_TOOLS.md).

## 11. Knowledge Store (UKS)

- **Overview:** UKS provides persistent, queryable memory for ImpressionCore-b1. See [BRAINSIM3.md](BRAINSIM3.md).
- **Usage:** Add/query knowledge via UI or API. See [KNOWLEDGE_MODULE_USAGE.md](KNOWLEDGE_MODULE_USAGE.md).
- **Features:** Memory efficiency, streaming, security.

## 12. Rule Engine

- **Purpose:** Add custom logic and constraints.
- **Integration:** Works with UKS and model pipeline.
- **References:** [component-integration.md](component-integration.md).

## 13. Inheritance

- **Modularity:** Extend and inherit capabilities modularly.
- **Structure:** Graph-based for extensibility.
- **References:** [model_architecture.md](model_architecture.md).

## 14. Unified Builder (Advanced)

- **Workflows:** Advanced workflows and multi-model orchestration.
- **References:** [model_builder_enhancement_plan.md](model_builder_enhancement_plan.md).

## 15. Interactive Configuration

- **Hardware Presets:** Optimize settings for your specific hardware environment.
- **Memory Estimation:** Get real-time estimates of memory usage for different configurations.
- **Advanced Features:** Enable and configure MoE and LoRA support through an intuitive UI.
- **References:** See the Interactive Configuration page in the web UI.

## 16. Metrics Dashboard

- **Memory Usage:** Track GPU and CPU memory usage over time.
- **Model Quality:** Visualize accuracy, perplexity, and other quality metrics.
- **Advanced Features:** Monitor MoE expert utilization and LoRA adaptation quality.
- **Hardware Utilization:** Track GPU and CPU utilization during model operations.
- **References:** See the Metrics Dashboard page in the web UI.

## 17. API Reference

- **Endpoints:** See [api_reference.md](api_reference.md) for all endpoints and usage.

## 18. Documentation & Support

- **Guides:** User and developer guides, tutorials, and examples.
- **References:** [user_guide.md](user_guide.md).

## 19. Development Roadmap

- **Milestones:** See [development_roadmap.md](development_roadmap.md) for future plans.

## 20. Error Handling & Troubleshooting

- **Layers:** Multi-layered error handling and user-friendly messages.
- **Tools:** Use memlog and troubleshooting scripts.
- **References:** [comprehensive_error_handling_plan.md](comprehensive_error_handling_plan.md).

## 21. UI Enhancements & Implementation Details

- **Features:** Modern UI, dashboards, real-time feedback.
- **Status:** See implementation status and timeline in the docs.

---

## Appendix

- For tool usage, see [user_guide_tools.md](user_guide_tools.md).
- Always cross-reference with implementation docs and update as features change.

---

## 2026-2027 User Workflow Updates

Primary planning source for upcoming user-facing changes:

- process/EXECUTION_APPENDIX_2026_2027.md

What users should expect next:

1. Canonical B-series offering selection in Builder (B1 39M, B2 50M, B3 504M).
2. Clear model provenance and integrity workflows (manifest + hash verification).
3. Improved Builder-to-Dashboard continuity for checkpoint discovery and stage labeling.
4. Staged triad experience maturity as C1 Colossus moves from architecture governance to controlled runtime usage.

Documentation operations note:

- After major guide updates, refresh docs/DOCUMENTATION_INDEX.md and confirm IDS MCP search health.
