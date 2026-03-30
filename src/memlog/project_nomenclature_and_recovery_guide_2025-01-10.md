# ImpressionCore-B1 Project Nomenclature and Recovery Guide
**Created:** 2025-01-10  
**Author:** GitHub Copilot  
**Purpose:** Complete reference for project names, files, and recovery information

## Project Identity
- **Main Project Name:** ImpressionCore
- **Current Phase:** ImpressionCore-B1 (Brain-inspired iteration 1)
- **Architecture Type:** Brain-inspired multimodal AI framework
- **Hardware Target:** NVIDIA GTX 1050 Ti (4GB VRAM) → GTX 1080 (8GB VRAM)

## Key Directory Structure
```
d:\Projects\impressioncore\
├── src/                                    # Main source directory
│   ├── core/                              # Core system components
│   │   ├── kernel/                        # Central coordination
│   │   ├── liaison/                       # Inter-component communication
│   │   ├── brainsim/                      # Memory and cognitive simulation
│   │   └── utils/                         # Shared utilities and enhancements
│   ├── data/                              # Data processing and management
│   │   └── datasets/                      # Main dataset directory
│   │       ├── text/                      # Text datasets
│   │       ├── audio/                     # Audio datasets with phonemes
│   │       ├── images/                    # Image datasets with captions
│   │       ├── multimodal/                # Cross-modal datasets
│   │       ├── benchmark/                 # Evaluation datasets
│   │       ├── preprocessed/              # Processed datasets
│   │       └── validation/                # Validation datasets
│   ├── training/                          # Model training and optimization
│   ├── interfaces/                        # User interface components
│   │   └── cli/                          # Command line interfaces
│   ├── memlog/                           # System memory and logging
│   └── [other standard directories]
└── docs/                                  # Documentation system (IDS)
```

## Critical File Names

### Core System Files
- `src/interfaces/cli/impressioncore_b1_cuda_cli.py` - Main CUDA-first CLI
- `src/data/dataset_manager.py` - Bulletproof dataset manager
- `src/data/dataset_manager_simplified.py` - Working placeholder version
- `src/training/training_utils.py` - CUDA device selection utilities
- `src/core/utils/memory_controller.py` - VRAM management
- `src/core/utils/rich_enhancements.py` - UI enhancements
- `src/core/utils/rich_logging.py` - Enhanced logging
- `src/core/utils/rich_status_animation.py` - Status animations

### Documentation and Logging
- `src/memlog/DATASET_INTEGRATION_BATON_PASS_2025-01-10.md` - Current state summary
- `src/memlog/bulletproof_development_strategy_2025-01-09.md` - Strategy docs
- `src/memlog/ids_mcp_tool_naming_correction_complete_2025-01-10.md` - IDS tool fixes
- `docs/DOCUMENTATION_INDEX.md` - Main documentation index
- `docs/reference/mvp_definition_and_strategic_context.md` - MVP definition

### Development Tools
- `src/dev_tools/examples/prepare_training_data.py` - Sample data generation
- `src/dev_tools/gpu_diagnostics.py` - GPU validation tools
- `src/dev_tools/launcher_bulletproof.py` - Bulletproof launcher

## IDS MCP Server Tools (Corrected Naming)
**Pattern:** `mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_[function]`

- `mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_search` - Documentation search
- `mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_get-system` - System status
- `mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_list-tags` - Tag listing
- `mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_get-file-i` - File info
- `mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_get-docume` - Documentation stats

## Key Technical Terms and Concepts

### Architecture Terms
- **Brain-inspired multimodal AI framework**
- **CUDA-first development** (hard requirement)
- **Modular extensibility and scalability**
- **Quantum-resistant cryptography**
- **Secure digital identity management**

### Memory Management
- **Bulletproof Data Manager** - Incremental, memory-efficient loading
- **VRAM monitoring and optimization**
- **Gradient checkpointing**
- **Memory profiling with tracemalloc**

### Dataset Requirements (Minimum for MVP)
- **Text:** 1,000 real samples
- **Audio:** 100 real files with phoneme alignment (LibriSpeech, LJSpeech, CommonVoice)
- **Images:** 500 real images with captions

### Hardware Specifications
- **Current:** NVIDIA GTX 1050 Ti (4GB VRAM), Intel i5 4460, 32GB DDR3
- **Target:** GTX 1080 (8GB VRAM) for scaling validation

## Recovery Commands and Setup

### Environment Setup
```bash
# Activate Python environment
source .venv310/Scripts/activate  # Windows Git Bash

# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify CUDA setup
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
```

### CLI Usage
```bash
# Main CLI with CUDA enforcement
python src/interfaces/cli/impressioncore_b1_cuda_cli.py --help

# Dataset management
python src/data/dataset_manager.py --validate-structure

# GPU diagnostics
python src/dev_tools/gpu_diagnostics.py
```

## External Dependencies to Re-download
- **PyTorch with CUDA 12.1 support**
- **Real audio datasets:** LibriSpeech, LJSpeech, or CommonVoice
- **Real image datasets:** COCO, ImageNet subset, or custom scraped
- **Text corpora:** Can be generated or downloaded from public sources

## Repository and Backup Information
- **Main directory:** `d:\Projects\impressioncore`
- **Git repository:** (if initialized, check .git/ folder)
- **Key config files:** `requirements.txt`, `setup.py`, `main.py`

## MCP Server Integration
- **Server name:** impressioncore-ids
- **Function prefix:** mcp_impressioncor_mcp_impressioncor_mcp_impressioncor_
- **Documentation system:** IDS (Intelligent Documentation System)

## Recovery Priority Order
1. **Core system files** (CLI, dataset manager, training utils)
2. **Documentation and memlog** (baton passes, strategy docs)
3. **Development tools** (GPU diagnostics, launchers)
4. **Sample datasets** (can be regenerated with prepare_training_data.py)
5. **Real datasets** (must be downloaded from external sources)

---
**Note:** This guide provides complete nomenclature for rebuilding the ImpressionCore-B1 project from scratch or recovering missing components.
