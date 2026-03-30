# Research: Direct GPU-Chipset Frame Reading for Brain-Triad Speed

**Created:** December 23, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team  
**Tags:** #docs\research\DIRECT_GPU_FRAME_READING_ROADMAP.md #documentation  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

**Objective**: Bypassing the CPU-bottleneck in video-to-LLM pipelines by reading frames directly from the GPU video decoding chipset (NVDEC/DXVA).

## 🔍 Theoretical Foundations

Traditional video processing requires:

1. GPU Hardware Decode.
2. Transfer from VRAM to System RAM.
3. Preprocessing/Resizing on CPU.
4. Transfer back to GPU VRAM for the Vision Encoder.

**Zero-Copy Strategy**: Keep the decoded frame in VRAM and use **Compute Shaders** or **CUDA Kernels** to resize and tokenize it before passing it to the Multimodal model (e.g., Moondream/Mini-Omni).

## 🛠️ Targeted APIs for Research

- **NVDEC (NVIDIA Video Decoder)**: Native hardware accelerated decoding. Can we map the decoded surface directly to a PyTorch tensor via `cuda_array_interface`?
- **DXVA / D3D11VA**: Standard Windows video acceleration. Requires interop between DirectX and CUDA/Vulkan.
- **Vulkan Video**: The new cross-platform standard for hardware-accelerated video. High potential for "Zero-Copy" workflows.
- **OpenCV with CUDA context**: Investigating `cv2.cuda.createVideoReader`.

## 📈 Projected Performance Gain

| Methodology | Latency (Frames/sec) | CPU Usage |
|-------------|---------------------|-----------|
| Standard Frame Stepping | 5-10 fps | ~30% |
| Direct Chipset Reading | **30-60+ fps** | **<5%** |

## 📅 Roadmap tasks

- [ ] Implement benchmark script for `cv2.cuda.VideoReader`.
- [ ] Explore `Decord` or `FFMS2` GPU-bindings.
- [ ] Experiment with mapping D3D11 textures directly to Torch tensors (Extreme speed path).
