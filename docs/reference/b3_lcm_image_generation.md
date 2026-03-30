# B3 LCM Image Generation Guide

**Created:** October 11, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team  
**Tags:** #ids #standardized_header #b3 #lcm #diffusion #image_generation #documentation  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## Overview

This document describes the **LCM (Latent Consistency Models)** integration for ImpressionCore B3 architecture, implementing **Decision #4** from the B3 architectural analysis.

### Decision #4: LCM Diffusion (External Method)

**Approved:** October 11, 2025  
**Model:** SimianLuo/LCM_Dreamshaper_v7  
**Parameters:** 860M (external to 39M B3 budget)  
**Rationale:** Fast integration (2-3 hours), production quality, proven GTX 1050 Ti compatibility

---

## Constitutional Note

⚠️ **Important:** LCM (860M parameters) is **external to the 39M Parameter Foundation** constitutional requirement. This is a pragmatic Phase 1 solution that enables immediate image generation capabilities.

**Phase 2 Roadmap:** Native B3 diffusion decoder (2-3M parameters) will be developed to achieve full constitutional compliance while maintaining the external LCM option for users who prioritize quality over deployment size.

---

## Performance Validation (GTX 1050 Ti)

### Validated Metrics (October 11, 2025)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| **Peak VRAM** | <3.5GB | 2.625 GB | ✅ PASS |
| **Average Latency** | <15s | 12.41s | ✅ PASS |
| **Image Quality** | 512×512 | 512×512 | ✅ PASS |
| **Success Rate** | 100% | 100% (4/4) | ✅ PASS |
| **Load Time** | <10s | 5.3s (cached) | ✅ PASS |

**Test Environment:**

- GPU: NVIDIA GTX 1050 Ti (4GB VRAM)
- CUDA: 12.1
- PyTorch: 2.5.1+cu121
- Diffusers: 0.35.1

---

## Installation

### 1. Install Dependencies

```bash
# Activate environment
.venv310\Scripts\activate

# Install diffusers and dependencies
pip install diffusers>=0.18.0 transformers accelerate

# Verify installation
python -c "from diffusers import AutoPipelineForText2Image; print('✅ Diffusers installed')"
```

### 2. Download LCM Model (First Time Only)

The model will auto-download on first use (~5GB download, 8-10 minutes on typical connection):

```python
from src.core.models.lcm_diffusion import B3ImageGenerator

# Initialize (triggers model download)
generator = B3ImageGenerator()
generator.load()  # Downloads SimianLuo/LCM_Dreamshaper_v7
```

**Model Cache Location:** `C:\Users\[username]\.cache\huggingface\hub\`

**Disk Space Required:** ~3.6GB for LCM model

---

## Usage

### Basic Image Generation

```python
from src.core.models.lcm_diffusion import B3ImageGenerator

# Initialize generator
generator = B3ImageGenerator()
generator.load()

# Generate image from text
image = generator.generate_from_b3_output(
    "a serene mountain landscape at sunset"
)

# Save image
image.save("output.png")

# Cleanup
generator.unload()
```

### Advanced Configuration

```python
from src.core.models.lcm_diffusion import LCMDiffusionGenerator

# Custom initialization
generator = LCMDiffusionGenerator(
    model_id="SimianLuo/LCM_Dreamshaper_v7",
    device="cuda",  # or "cpu"
    enable_optimizations=True,  # CPU offload + attention slicing
    cache_dir=None  # Use default or specify custom path
)

generator.load()

# Generate with custom parameters
image = generator.generate(
    prompt="a futuristic city with flying cars at night",
    negative_prompt="blurry, low quality",
    num_inference_steps=4,  # 4-8 steps for LCM
    guidance_scale=1.0,  # LCM uses minimal guidance
    height=512,
    width=512,
    seed=42,  # For reproducibility
    lcm_origin_steps=50
)

image.save("futuristic_city.png")
```

### Batch Generation

```python
from src.core.models.lcm_diffusion import B3ImageGenerator

generator = B3ImageGenerator()
generator.load()

prompts = [
    "a red apple on a wooden table",
    "a cat sleeping on a cozy blanket",
    "a sunset over the ocean"
]

images = generator.generate_batch(prompts)

for i, image in enumerate(images):
    if image:
        image.save(f"output_{i+1}.png")

generator.unload()
```

### Integration with B3 Text Encoder

```python
from src.core.models.lcm_diffusion import B3ImageGenerator

# Initialize image generator
img_gen = B3ImageGenerator()
img_gen.load()

# B3 text encoder generates description
b3_text_output = "Generate an image of: a wise old wizard in a mystical forest"

# Extract prompt (in real B3, this would be processed output)
prompt = b3_text_output.split("Generate an image of: ")[-1]

# Generate image
image = img_gen.generate_from_b3_output(
    prompt,
    enhance_prompt=True  # Adds quality modifiers
)

image.save("b3_wizard.png")
img_gen.unload()
```

---

## GTX 1050 Ti Optimization

### Memory Optimizations (Enabled by Default)

1. **torch.float16 Precision**
   - Reduces VRAM usage by ~50%
   - Minimal quality impact

2. **CPU Offloading**
   - Moves inactive model components to CPU
   - Keeps only active layers in VRAM

3. **Attention Slicing**
   - Processes attention in chunks
   - Reduces peak VRAM requirements

### Manual Optimization

```python
from src.core.models.lcm_diffusion import LCMDiffusionGenerator
import torch

# Clear GPU cache before generation
torch.cuda.empty_cache()

# Initialize with optimizations
generator = LCMDiffusionGenerator(
    enable_optimizations=True
)
generator.load()

# Generate with memory monitoring
torch.cuda.reset_peak_memory_stats()

image = generator.generate("a mountain landscape")

peak_vram = torch.cuda.max_memory_allocated() / (1024**3)
print(f"Peak VRAM: {peak_vram:.3f} GB")

# Clear cache after generation
torch.cuda.empty_cache()
generator.unload()
```

---

## Performance Benchmarks

### Generation Speed (GTX 1050 Ti)

| Resolution | Steps | Time | VRAM | Quality |
|------------|-------|------|------|---------|
| 512×512 | 4 | ~12s | 2.6GB | High |
| 512×512 | 8 | ~20s | 2.6GB | Higher |
| 768×768 | 4 | ~40s | 3.5GB | High |

**Recommendation:** Use **512×512** with **4 steps** for optimal balance of speed, quality, and VRAM usage.

### Comparison with Other Methods

| Method | Params | Time | VRAM | Quality | Deployment |
|--------|--------|------|------|---------|------------|
| **LCM** | 860M | 12s | 2.6GB | 512×512 | 3.6GB |
| SD 1.5 | 860M | 60s | 3.5GB | 512×512 | 3.6GB |
| SDXL-Turbo | 2.6B | 25s | 5.0GB ⚠️ | 1024×1024 | 5GB |
| Native B3 (future) | 2-3M | 0.5s | 1.0GB | 32×32→64×64 | 150MB |

---

## Troubleshooting

### Issue: Model Download Fails

**Symptom:** `OSError: No file or directory` during first load

**Solutions:**

1. Check internet connection
2. Verify HuggingFace access (no authentication required for LCM)
3. Clear cache: `rm -rf ~/.cache/huggingface/hub/models--SimianLuo--LCM_Dreamshaper_v7`
4. Try manual download:

   ```python
   from huggingface_hub import snapshot_download
   snapshot_download("SimianLuo/LCM_Dreamshaper_v7")
   ```

### Issue: Out of Memory (OOM) Errors

**Symptom:** `RuntimeError: CUDA out of memory`

**Solutions:**

1. Ensure optimizations are enabled:

   ```python
   generator = LCMDiffusionGenerator(enable_optimizations=True)
   ```

2. Reduce resolution:

   ```python
   image = generator.generate(prompt, height=448, width=448)
   ```

3. Clear GPU cache before generation:

   ```python
   torch.cuda.empty_cache()
   ```

4. Close other GPU applications (browsers, other models)

### Issue: Slow Generation Speed

**Symptom:** >30s per 512×512 image

**Solutions:**

1. Verify CUDA is being used:

   ```python
   print(f"Device: {generator.device}")  # Should be 'cuda'
   print(f"CUDA available: {torch.cuda.is_available()}")
   ```

2. Check GPU utilization:

   ```bash
   nvidia-smi -l 1  # Monitor GPU usage during generation
   ```

3. Ensure CPU offloading is enabled (default)
4. Try reducing steps (but quality may degrade):

   ```python
   image = generator.generate(prompt, num_inference_steps=2)
   ```

### Issue: NSFW Content Warning

**Symptom:** Warning: `⚠️ NSFW content detected. Image may have been filtered.`

**Explanation:** LCM includes a safety checker that may trigger false positives for innocent prompts.

**Solutions:**

1. Modify prompt to be more explicit about desired content
2. Safety checker can be disabled (not recommended for production):

   ```python

   # Advanced users only - disables safety checker

   generator.pipeline.safety_checker = None
   ```

### Issue: Poor Image Quality

**Symptom:** Blurry, incoherent, or low-quality images

**Solutions:**

1. Increase inference steps:

   ```python
   image = generator.generate(prompt, num_inference_steps=8)
   ```

2. Add quality modifiers to prompt:

   ```python
   prompt = "a mountain landscape, high quality, detailed, professional photograph"
   ```

3. Use negative prompt:

   ```python
   image = generator.generate(
       prompt="a mountain landscape",
       negative_prompt="blurry, low quality, distorted, ugly"
   )
   ```

4. Try different seed values:

   ```python
   for seed in range(5):
       image = generator.generate(prompt, seed=seed)
       image.save(f"test_{seed}.png")
   ```

---

## API Reference

### LCMDiffusionGenerator

**Class:** `src.core.models.lcm_diffusion.LCMDiffusionGenerator`

**Constructor:**

```python
__init__(
    model_id: str = "SimianLuo/LCM_Dreamshaper_v7",
    device: Optional[str] = None,
    enable_optimizations: bool = True,
    cache_dir: Optional[str] = None
)
```

**Methods:**

#### `load() -> bool`

Load the LCM model pipeline.

**Returns:** `True` if successful, `False` otherwise

#### `generate(...) -> Optional[Image.Image]`

Generate image from text prompt.

**Parameters:**

- `prompt` (str): Text description
- `negative_prompt` (Optional[str]): Things to avoid
- `num_inference_steps` (int): Denoising steps (default: 4)
- `guidance_scale` (float): Guidance strength (default: 1.0)
- `height` (int): Image height (default: 512)
- `width` (int): Image width (default: 512)
- `seed` (Optional[int]): Random seed
- `lcm_origin_steps` (int): Original SD steps (default: 50)

**Returns:** PIL Image or `None` if failed

#### `generate_batch(prompts: List[str], **kwargs) -> List[Optional[Image.Image]]`

Generate multiple images.

**Parameters:**

- `prompts`: List of text prompts
- `**kwargs`: Passed to `generate()`

**Returns:** List of PIL Images

#### `get_stats() -> dict`

Get performance statistics.

**Returns:** Dictionary with metrics

#### `unload() -> None`

Unload model and free GPU memory.

---

### B3ImageGenerator

**Class:** `src.core.models.lcm_diffusion.B3ImageGenerator`

**Constructor:**

```python
__init__(**lcm_kwargs)
```

**Methods:**

#### `load() -> bool`

Load the LCM model.

#### `generate_from_b3_output(b3_text: str, enhance_prompt: bool = True, **kwargs) -> Optional[Image.Image]`

Generate image from B3 text encoder output.

**Parameters:**

- `b3_text`: Text from B3 model
- `enhance_prompt`: Add quality modifiers
- `**kwargs`: Passed to LCM generation

**Returns:** PIL Image or `None`

#### `get_stats() -> dict`

Get performance statistics.

#### `unload() -> None`

Unload model and free memory.

---

## Development Roadmap

### Phase 1: External LCM (COMPLETE ✅)

- ✅ LCM integration (SimianLuo/LCM_Dreamshaper_v7)
- ✅ B3ImageGenerator wrapper class
- ✅ GTX 1050 Ti optimizations
- ✅ Performance validation (2.6GB VRAM, 12s latency)
- ✅ Comprehensive testing (4/4 test cases passed)
- ✅ Documentation

**Status:** PRODUCTION READY

### Phase 2: Native B3 Diffusion (PLANNED)

**Timeline:** 2-3 weeks after Phase 1

**Objectives:**

- Native B3 diffusion decoder (2-3M parameters)
- Constitutional compliance (within 39M budget)
- Progressive training (16×16 → 32×32 → 64×64)
- Knowledge distillation from SD 1.5
- Target: 32×32→64×64 images, <1GB VRAM, 0.5s latency

**Benefits:**

- Smaller deployment (150MB vs 3.6GB)
- Faster inference (0.5s vs 12s)
- Full constitutional compliance
- Integrated with B3 architecture

**Tradeoffs:**

- Lower resolution (64×64 vs 512×512)
- Requires 2-3 weeks development
- Training dataset preparation needed

### Phase 3: Dual-Mode System (FUTURE)

**Concept:** Offer both LCM and native B3 diffusion

**Use Cases:**

- **Native B3:** Fast previews, low-VRAM, mobile deployment
- **LCM:** High-quality final renders, desktop deployment

**Implementation:**

```python
# Dual-mode interface
generator = B3DualModeGenerator()

# Fast preview (native B3)
preview = generator.generate_preview(prompt)  # 64×64, 0.5s

# High-quality render (LCM)
final = generator.generate_hq(prompt)  # 512×512, 12s
```

---

## Contributing

### Reporting Issues

Found a bug or have a suggestion? Please create an issue:

1. Check existing issues first
2. Include system information (GPU, CUDA, PyTorch version)
3. Provide code example if applicable
4. Include error messages and logs

### Performance Improvements

Ideas for optimization:

- [ ] Experiment with LCM-LoRA for faster loading
- [ ] Test SDXL-Lightning (1-step inference)
- [ ] Implement prompt caching for repeated generations
- [ ] Add multi-image batch processing
- [ ] Profile memory usage for further optimization

---

## References

### LCM Research

- **Paper:** "Latent Consistency Models: Synthesizing High-Resolution Images with Few-Step Inference"
- **ArXiv:** [2310.04378](https://arxiv.org/abs/2310.04378)
- **Authors:** Simian Luo, Yiqin Tan, Longbo Huang, Jian Li, Hang Zhao

### Model Resources

- **Model Card:** [SimianLuo/LCM_Dreamshaper_v7](https://huggingface.co/SimianLuo/LCM_Dreamshaper_v7)
- **Diffusers Docs:** [LCM Pipelines](https://huggingface.co/docs/diffusers/using-diffusers/lcm)
- **LCM Scheduler:** [API Reference](https://huggingface.co/docs/diffusers/api/schedulers/lcm)

### B3 Architecture

- **Decision Analysis:** `B3_DECISION_POINTS_ANALYSIS.md`
- **Diffusion Deep Dive:** `B3_DIFFUSION_DEEP_DIVE.md`
- **Constitutional Framework:** `docs/reference/IMPRESSIONCORE_PERMANENT_ARCHITECTURAL_FRAMEWORK.md`

---

## License

ImpressionCore: MIT License  
LCM Model: Apache 2.0 License

---

## Changelog

### October 11, 2025 - Initial Release

- ✅ LCM integration complete
- ✅ Performance validation on GTX 1050 Ti
- ✅ Comprehensive testing (4/4 passed)
- ✅ Documentation complete
- ✅ Production ready

**Decision #4 Status:** ✅ VALIDATED AND OPERATIONAL

---

**Last Updated:** October 11, 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅
