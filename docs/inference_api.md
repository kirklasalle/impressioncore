"""
ImpressionCore-b1 Inference API Documentation

This document describes the usage, integration, and memory optimization strategies for the ImpressionCore-b1 inference pipeline and web API.

---

# 1. Inference Pipeline Overview

The `run_inference` function in `src/inference/pipeline.py` provides a memory-efficient, functional API for running inference on text, image, or multimodal data. It is optimized for low VRAM (e.g., GTX 1050 Ti, 4GB) and supports:
- Automatic device selection (CPU/GPU)
- Precision control (fp16, bf16, fp32)
- Batch processing with configurable batch size
- Autocast and no_grad for memory savings

## Example Usage

```python
import torch
from src.inference import run_inference

class DummyModel(torch.nn.Module):
    def forward(self, x, **kwargs):
        return x * 2

model = DummyModel()
input_tensor = torch.tensor([1.0, 2.0, 3.0])
output = run_inference(model, input_tensor, device="cpu", precision="fp32")
print("Inference output:", output)
```

---

# 2. Web API Integration

The web server exposes a POST endpoint at `/api/inference` for running inference from the UI or external clients.

## Endpoint
- **URL:** `/api/inference`
- **Method:** POST
- **Auth:** Required (session-based)
- **Request JSON:**
  - `input_data`: List or tensor-like input (required)
  - `precision`: 'fp16', 'bf16', or 'fp32' (optional, default: 'fp16')
  - `max_batch_size`: Integer (optional, default: 1)
- **Response JSON:**
  - `output`: Model output (as list or string)
  - `error`: Error message (if any)

## Example Request
```json
{
  "input_data": [1.0, 2.0, 3.0],
  "precision": "fp32",
  "max_batch_size": 1
}
```

## Example Response
```json
{
  "output": [2.0, 4.0, 6.0]
}
```

---

## Model Selection and Dynamic Loading (Updated 2025-04-18)

### Model Listing
- The `/api/models` endpoint scans `src/models/` and subdirectories for all `.pt` model files.
- Returns a list of models with:
  - `name`: Model name (from filename)
  - `path`: Relative path (for selection)
  - `size`: File size in bytes
  - `last_modified`: ISO timestamp
  - `description`: From `config.json` if available, else 'No description.'
- The frontend dropdown is dynamically populated with this list.
- **impressioncore-b1** (from `impressioncore-base/model.pt`) is always the default selection.

### Model Loading and Caching
- On server startup, no models are loaded by default.
- When a model is selected for inference, it is loaded from disk and cached in memory for future use.
- The cache is thread-safe and avoids reloading models unnecessarily.
- Model metadata is displayed in the UI info panel.

### Inference Endpoint
- `/api/inference` uses the selected model from the dropdown (default: impressioncore-b1).
- Supports text and image (multimodal) input.
- Returns output, tokens generated, and generation speed.
- Handles errors (model not found, OOM, etc.) gracefully.

### Example Request
```json
{
  "input_text": "What is ImpressionCore?",
  "model": "impressioncore-base/model.pt",
  "temperature": 1.0,
  "max_tokens": 100,
  "top_p": 0.9
}
```

### Example Response
```json
{
  "output": "ImpressionCore is a brain-inspired multimodal AI framework...",
  "tokens_generated": 8,
  "generation_speed": 12.5
}
```

### Adding New Models
- Place new `.pt` model files in `src/models/` or a subdirectory.
- Optionally, add a `config.json` with a `description` field for richer UI info.
- The new model will appear in the dropdown automatically.

---

## Memory and Performance
- Models are loaded with `map_location='cpu'` by default for safety.
- Only one copy of each model is kept in memory at a time.
- Designed for low VRAM (GTX 1050 Ti, 4GB) and memory-efficient inference.

---

## Error Handling
- All errors are returned as JSON with an `error` field.
- Model loading and inference errors are logged and reported to the user.

---

## Security
- All endpoints require authentication.
- Input is validated and sanitized before processing.

---

## Last Updated
- 2025-04-18

# 3. Memory Optimization Strategies
- Uses `torch.no_grad()` and `torch.autocast()` for reduced memory usage.
- Processes data in small batches to avoid VRAM spikes.
- Supports precision control to further reduce memory footprint.
- Designed for safe operation on 4GB VRAM GPUs.

---

# 4. Error Handling
- All errors are logged and returned as JSON with an `error` field.
- Input validation is performed to prevent misuse.
- Handles device selection and OOM gracefully.

---

# 5. Security
- API endpoint is protected by session authentication.
- Input is validated and sanitized before processing.

---

# 6. Extending for Real Models
- Replace the dummy model in the API with your actual model loading logic.
- Ensure the model is loaded once and reused for efficiency.
- Adapt input preprocessing as needed for your model type (text, image, etc.).

---

# 7. Testing
- Use memory profiling tools (e.g., memory_profiler, tracemalloc) to validate memory usage.
- Test with various input sizes and precision settings.

---

# 8. References
- See `src/inference/pipeline.py` for implementation details.
- See `src/inference/example_usage.py` for a runnable example.
- See `src/web/server.py` for web API integration.

---

# 9. Contact
For support or questions, see the ImpressionCore documentation or contact the project maintainers.

"""
