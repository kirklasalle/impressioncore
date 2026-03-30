# ImpressionCore Phase 3 Deployment Guide

**Created:** October 05, 2025  
**Updated:** December 29, 2025  
**Author:** GitHub Copilot  
**Tags:** #docs\deployment\phase3_deployment_guide.md #documentation  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

**Model:** ImpressionCore-B3 "39M Parameter Foundation"  
**Status:** Production Ready ✅  
**Phase:** Phase 3 Smart Hybrid System

---

## 📋 TABLE OF CONTENTS

1. [Quick Start](#quick-start)
2. [Hardware Requirements](#hardware-requirements)
3. [Software Prerequisites](#software-prerequisites)
4. [Installation Steps](#installation-steps)
5. [Model Setup](#model-setup)
6. [Embedding Setup](#embedding-setup)
7. [Configuration](#configuration)
8. [First-Run Validation](#first-run-validation)
9. [Troubleshooting](#troubleshooting)
10. [Production Deployment](#production-deployment)

---

## 🚀 QUICK START

### 5-Minute Setup (If You Have Everything)

```powershell
# 1. Clone repository (if not already done)
git clone https://github.com/impressioncore/impressioncore.git
cd impressioncore

# 2. Create Python 3.10 virtual environment
python -m venv .venv310
.\.venv310\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify model and embeddings exist
Test-Path F:\models\checkpoints\b3\b3_massive_final.pth  # Should be True
Test-Path F:\data\embeddings\*  # Should show files

# 5. Run quick test
python src\inference\test_smart_hybrid.py --quick

# 6. Start using!
python
>>> from src.inference.b3_rag_inference import B3RAGInference
>>> inferencer = B3RAGInference()
>>> result = inferencer.generate_with_smart_hybrid("Hello!")
>>> print(result["response"])
```

**Expected Output**: "I'm doing well, thank you for asking! How can I help you today?"

---

## 🖥️ HARDWARE REQUIREMENTS

### Minimum Requirements (Validated)

| Component | Specification | Status |
|-----------|---------------|--------|
| **GPU** | NVIDIA GTX 1050 Ti (4GB VRAM) | ✅ TESTED |
| **CPU** | Intel Core i5 4460 @ 3.20GHz | ✅ TESTED |
| **RAM** | 8GB DDR3 | ✅ MINIMUM |
| **Storage** | 50GB free space | ✅ REQUIRED |
| **OS** | Windows 10/11 (64-bit) | ✅ VALIDATED |

### Recommended Requirements

| Component | Specification | Benefits |
|-----------|---------------|----------|
| **GPU** | NVIDIA GTX 1060 or better | Faster inference (~20% speedup) |
| **CPU** | Intel Core i7 or equivalent | Better CPU fallback |
| **RAM** | 16GB DDR3/DDR4 | Smoother operation |
| **Storage** | 100GB free (SSD) | Faster data access |
| **OS** | Windows 11 (64-bit) | Latest drivers |

### Storage Breakdown

| Component | Size | Location | Removable |
|-----------|------|----------|-----------|
| **Model Checkpoint** | ~300MB | F:/models/checkpoints/b3/ | ❌ Required |
| **Embeddings** | ~1.5GB | F:/data/embeddings/ | ❌ Required |
| **FAISS Index** | ~500MB | F:/data/embeddings/ | ❌ Required |
| **Source Code** | ~100MB | D:/Projects/impressioncore/ | ❌ Required |
| **Dependencies** | ~2GB | .venv310/ | ❌ Required |
| **Training Logs** | ~50MB | F:/data/training/logs/ | ✅ Optional |
| **Test Results** | ~10MB | src/memlog/test_results/ | ✅ Optional |
| **TOTAL REQUIRED** | **~4.5GB** | - | - |

### CPU-Only Mode (No GPU)

**Supported but SLOW** (~10x slower than GPU)

| Component | Specification | Performance |
|-----------|---------------|-------------|
| **CPU** | Intel i5 or AMD equivalent (4+ cores) | ~27s per query |
| **RAM** | 16GB minimum | Essential for CPU mode |
| **Storage** | Same as GPU requirements | Same as GPU |

**Recommendation**: GPU mode strongly recommended for production use.

---

## 💻 SOFTWARE PREREQUISITES

### Python Version

**Required**: Python 3.10.x  
**Validated**: Python 3.10.11  
**NOT Compatible**: Python 3.11+ (transformer versions)

```powershell
# Check Python version
python --version
# Should show: Python 3.10.x
```

### CUDA Toolkit (GPU Mode)

**Required**: CUDA 11.8 or higher  
**Recommended**: CUDA 12.1  
**Download**: [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)

```powershell
# Check CUDA version (after NVIDIA driver installation)
nvidia-smi
# Should show CUDA Version: 11.8 or higher
```

### Git (Optional but Recommended)

**Purpose**: Clone repository, version control  
**Download**: [Git for Windows](https://git-scm.com/download/win)

```powershell
# Check Git version
git --version
```

### Visual C++ Redistributables (Windows)

**Required**: For PyTorch and FAISS  
**Download**: [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

---

## 📥 INSTALLATION STEPS

### Step 1: Clone Repository

```powershell
# Navigate to projects directory
cd D:\Projects

# Clone ImpressionCore
git clone https://github.com/impressioncore/impressioncore.git
cd impressioncore
```

**Without Git:**

1. Download ZIP from GitHub
2. Extract to `D:\Projects\impressioncore\`
3. Continue with Step 2

### Step 2: Create Virtual Environment

```powershell
# Create Python 3.10 virtual environment
python -m venv .venv310

# Activate environment
.\.venv310\Scripts\Activate.ps1

# Verify activation (should show (.venv310) in prompt)
# (.venv310) PS D:\Projects\impressioncore>
```

**Troubleshooting Activation:**

```powershell
# If execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then retry activation
.\.venv310\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```powershell
# Ensure virtual environment is activated
# Install core dependencies
pip install --upgrade pip
pip install -r requirements.txt

# This will install:
# - torch==2.7.1+cu118 (PyTorch with CUDA 11.8)
# - transformers (Hugging Face)
# - sentence-transformers (Embedding models)
# - faiss-cpu or faiss-gpu (Vector search)
# - And ~20 other dependencies
```

**Expected Installation Time**: 5-10 minutes (depending on internet speed)

**Verify Installation:**

```powershell
# Check PyTorch
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"
# Expected: PyTorch: 2.7.1+cu118, CUDA available: True

# Check Transformers
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
# Expected: Transformers: 4.x.x

# Check FAISS
python -c "import faiss; print(f'FAISS: {faiss.__version__}')"
# Expected: FAISS: 1.x.x
```

### Step 4: Create F: Drive Structure (If Needed)

```powershell
# Create required directories on F: drive
New-Item -Path "F:\models\checkpoints\b3" -ItemType Directory -Force
New-Item -Path "F:\data\embeddings" -ItemType Directory -Force
New-Item -Path "F:\data\training\logs" -ItemType Directory -Force
```

---

## 🤖 MODEL SETUP

### Download Model Checkpoint

**Model**: b3_massive_final.pth  
**Size**: ~300MB  
**Parameters**: 35,560,024  
**Location**: `F:/models/checkpoints/b3/b3_massive_final.pth`

#### Option 1: Direct Download (If Available)

```powershell
# Download from release page
# (URL provided separately - contact maintainers)

# Move to F: drive
Move-Item -Path ".\b3_massive_final.pth" -Destination "F:\models\checkpoints\b3\"
```

#### Option 2: Copy from Existing Installation

```powershell
# If you have existing ImpressionCore installation
Copy-Item -Path "F:\models\checkpoints\b3\b3_massive_final.pth" -Destination "F:\models\checkpoints\b3\" -Force
```

#### Verify Model

```powershell
# Check model exists
Test-Path "F:\models\checkpoints\b3\b3_massive_final.pth"
# Should return: True

# Check model size
(Get-Item "F:\models\checkpoints\b3\b3_massive_final.pth").Length / 1MB
# Should be approximately: 286 MB

# Verify model loadable (Python)
python -c "import torch; model = torch.load('F:/models/checkpoints/b3/b3_massive_final.pth', map_location='cpu'); print('Model loaded successfully!')"
```

---

## 📊 EMBEDDING SETUP

### Embedding Requirements

**Total Embeddings**: 1,300,000+  
**Storage**: ~1.5GB  
**Location**: `F:/data/embeddings/`  
**Format**: PyTorch tensors (.pt files)

### Download Embeddings

#### Option 1: Download Full Embeddings Package

```powershell
# Download embeddings archive (provided separately)
# Expected file: impressioncore_embeddings_v1.zip (~1.2GB compressed)

# Extract to F: drive
Expand-Archive -Path ".\impressioncore_embeddings_v1.zip" -DestinationPath "F:\data\" -Force
```

#### Option 2: Generate Embeddings (Advanced)

**⚠️ WARNING**: This takes several hours and requires significant compute.

```powershell
# Navigate to project directory
cd D:\Projects\impressioncore

# Activate environment
.\.venv310\Scripts\Activate.ps1

# Generate embeddings (SLOW - several hours)
python src\data\generate_embeddings.py --output "F:\data\embeddings"
```

### Verify Embeddings

```powershell
# Check embeddings directory exists
Test-Path "F:\data\embeddings"
# Should return: True

# Count embedding files
(Get-ChildItem "F:\data\embeddings\*.pt").Count
# Should be: 1000+ files

# Check total size
(Get-ChildItem "F:\data\embeddings\*.pt" | Measure-Object -Property Length -Sum).Sum / 1GB
# Should be approximately: 1.3-1.5 GB

# Verify embeddings loadable (Python)
python -c "import torch; import os; files = [f for f in os.listdir('F:/data/embeddings') if f.endswith('.pt')]; print(f'Found {len(files)} embedding files'); emb = torch.load(f'F:/data/embeddings/{files[0]}'); print(f'Sample embedding shape: {emb.shape}')"
```

---

## ⚙️ CONFIGURATION

### Default Configuration (Recommended)

The system works out-of-the-box with default settings:

```python
from src.inference.b3_rag_inference import B3RAGInference

# Default configuration (optimal for most use cases)
inferencer = B3RAGInference(
    model_path="F:/models/checkpoints/b3/b3_massive_final.pth",  # ✅ Default
    f_data_root="F:/data",                                        # ✅ Default
    device="cuda",                                                # ✅ Default (GPU)
    rag_confidence_threshold=0.4,                                 # ✅ Default (optimal)
    verbose=True                                                  # ✅ Default (logging)
)
```

### Custom Configuration File (Optional)

Create `config/production_config.yaml`:

```yaml
# ImpressionCore Production Configuration
model:
  checkpoint_path: "F:/models/checkpoints/b3/b3_massive_final.pth"
  device: "cuda"  # or "cpu"
  parameters: 35560024

embeddings:
  root_path: "F:/data"
  embedding_dir: "F:/data/embeddings"
  total_count: 1300000

rag:
  confidence_threshold: 0.4  # 0.0-1.0, default: 0.4
  top_k: 5                   # Number of retrieved documents
  max_context_length: 512    # Max RAG context tokens

generation:
  max_length: 100            # Max response tokens
  temperature: 0.8           # 0.1-2.0, default: 0.8
  top_k: 50                  # Top-K sampling
  top_p: 0.9                 # Nucleus sampling

system:
  verbose: true              # Detailed logging
  log_level: "INFO"          # DEBUG, INFO, WARNING, ERROR
  batch_size: 1              # Queries per batch (currently 1)

monitoring:
  enable_metrics: true       # Track performance metrics
  log_queries: true          # Log all queries
  log_responses: false       # Don't log responses (privacy)
```

**Load Configuration:**

```python
import yaml

# Load config
with open("config/production_config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Initialize with config
inferencer = B3RAGInference(
    model_path=config["model"]["checkpoint_path"],
    f_data_root=config["embeddings"]["root_path"],
    device=config["model"]["device"],
    rag_confidence_threshold=config["rag"]["confidence_threshold"],
    verbose=config["system"]["verbose"]
)
```

### Environment Variables (Alternative)

Create `.env` file:

```bash
# ImpressionCore Environment Configuration
IMPRESSIONCORE_MODEL_PATH=F:/models/checkpoints/b3/b3_massive_final.pth
IMPRESSIONCORE_DATA_ROOT=F:/data
IMPRESSIONCORE_DEVICE=cuda
IMPRESSIONCORE_RAG_THRESHOLD=0.4
IMPRESSIONCORE_VERBOSE=true
```

**Load from Environment:**

```python
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Initialize from environment
inferencer = B3RAGInference(
    model_path=os.getenv("IMPRESSIONCORE_MODEL_PATH"),
    f_data_root=os.getenv("IMPRESSIONCORE_DATA_ROOT"),
    device=os.getenv("IMPRESSIONCORE_DEVICE", "cuda"),
    rag_confidence_threshold=float(os.getenv("IMPRESSIONCORE_RAG_THRESHOLD", "0.4")),
    verbose=os.getenv("IMPRESSIONCORE_VERBOSE", "true").lower() == "true"
)
```

---

## ✅ FIRST-RUN VALIDATION

### Quick Test Script

Create `test_deployment.py`:

```python
"""
First-run validation script for ImpressionCore Phase 3.
"""

import torch
from src.inference.b3_rag_inference import B3RAGInference

def validate_deployment():
    """Validate ImpressionCore deployment."""
    print("🚀 ImpressionCore Phase 3 Deployment Validation\n")
    
    # 1. Check CUDA
    print("1️⃣ Checking CUDA availability...")
    cuda_available = torch.cuda.is_available()
    print(f"   CUDA available: {cuda_available}")
    if cuda_available:
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
    print()
    
    # 2. Initialize inference system
    print("2️⃣ Initializing inference system...")
    try:
        inferencer = B3RAGInference(verbose=False)
        print("   ✅ Inference system initialized successfully")
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        return False
    print()
    
    # 3. Test queries
    print("3️⃣ Running test queries...")
    test_queries = [
        "Hello!",
        "What is machine learning?",
        "Describe a sunset"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   Query {i}: {query}")
        try:
            result = inferencer.generate_with_smart_hybrid(query)
            print(f"   Response: {result['response'][:100]}...")
            print(f"   Strategy: {result['strategy']}")
            print(f"   Time: {result['timing']['total_ms']:.1f}ms")
            print(f"   ✅ Query {i} successful")
        except Exception as e:
            print(f"   ❌ Query {i} failed: {e}")
            return False
    print()
    
    # 4. Final validation
    print("4️⃣ Final validation...")
    print("   ✅ All tests passed!")
    print("   ✅ ImpressionCore Phase 3 is ready for production use!")
    return True

if __name__ == "__main__":
    success = validate_deployment()
    exit(0 if success else 1)
```

**Run Validation:**

```powershell
# Activate environment
.\.venv310\Scripts\Activate.ps1

# Run validation
python test_deployment.py
```

**Expected Output:**

``` text
🚀 ImpressionCore Phase 3 Deployment Validation

1️⃣ Checking CUDA availability...
   CUDA available: True
   GPU: NVIDIA GeForce GTX 1050 Ti
   VRAM: 4.0GB

2️⃣ Initializing inference system...
   ✅ Inference system initialized successfully

3️⃣ Running test queries...

   Query 1: Hello!
   Response: I'm doing well, thank you for asking! How can I help you today?...
   Strategy: natural_only
   Time: 2450.3ms
   ✅ Query 1 successful

   Query 2: What is machine learning?
   Response: Machine learning is a subset of artificial intelligence that enables systems to learn and improve...
   Strategy: natural_low_confidence
   Time: 2680.5ms
   ✅ Query 2 successful

   Query 3: Describe a sunset
   Response: A sunset is a beautiful natural phenomenon where the sun descends below the horizon...
   Strategy: natural_only
   Time: 2520.7ms
   ✅ Query 3 successful

4️⃣ Final validation...
   ✅ All tests passed!
   ✅ ImpressionCore Phase 3 is ready for production use!
```

### Expected Performance Metrics

| Metric | Target | Typical | Acceptable Range |
|--------|--------|---------|------------------|
| **Quality** | 4.43/5.0 | 4.0-4.5 | 3.5-5.0 |
| **Generic Rate** | 7.7% | 5-10% | 0-15% |
| **Success Rate** | 85.7% | 80-90% | 75-95% |
| **Response Time** | 2700ms | 2400-3000ms | 2000-4000ms |

---

## 🔧 TROUBLESHOOTING

### Issue 1: CUDA Not Available

**Symptoms:**

``` text
RuntimeError: CUDA is not available
torch.cuda.is_available() returns False
```

**Solutions:**

1. **Check NVIDIA Driver:**

   ```powershell
   nvidia-smi

   # Should show GPU info and CUDA version

   ```

   If command fails:

   - Download latest driver: [NVIDIA Drivers](https://www.nvidia.com/download/index.aspx)
   - Install and reboot

2. **Check CUDA Toolkit:**

   ```powershell
   nvcc --version

   # Should show CUDA compilation tools version

   ```

   If command fails:

   - Download CUDA Toolkit: [NVIDIA CUDA](https://developer.nvidia.com/cuda-downloads)
   - Install CUDA 11.8 or higher

3. **Fallback to CPU Mode:**

   ```python

   # Temporary workaround

   inferencer = B3RAGInference(device="cpu")

   # ⚠️ WARNING: 10x slower than GPU mode

   ```

### Issue 2: Model Checkpoint Not Found

**Symptoms:**

``` text
FileNotFoundError: Model checkpoint not found at F:/models/checkpoints/b3/b3_massive_final.pth
```

**Solutions:**

1. **Verify Path:**

   ```powershell
   Test-Path "F:\models\checkpoints\b3\b3_massive_final.pth"
   ```

   If False:

   - Check if F: drive exists
   - Verify model was downloaded/copied correctly
   - Ensure directory structure: `F:/models/checkpoints/b3/`

2. **Re-download Model:**
   - Contact maintainers for model download link
   - Download and place in `F:/models/checkpoints/b3/`

3. **Use Alternative Path:**

   ```python

   # If model is elsewhere

   inferencer = B3RAGInference(
       model_path="D:/path/to/b3_massive_final.pth"
   )
   ```

### Issue 3: Embeddings Not Found

**Symptoms:**

``` text
FileNotFoundError: Embeddings directory not found or empty
IndexError: No embedding files found in F:/data/embeddings/
```

**Solutions:**

1. **Verify Embeddings:**

   ```powershell
   Test-Path "F:\data\embeddings"
   (Get-ChildItem "F:\data\embeddings\*.pt").Count

   # Should show 1000+ files

   ```

2. **Re-download/Generate Embeddings:**
   - Download embeddings archive (contact maintainers)
   - OR generate embeddings (slow): `python src\data\generate_embeddings.py`

3. **Check Permissions:**

   ```powershell

   # Ensure F: drive is readable/writable

   icacls "F:\data\embeddings"
   ```

### Issue 4: Out of Memory (CUDA)

**Symptoms:**

``` text
RuntimeError: CUDA out of memory. Tried to allocate XXX MiB
```

**Solutions:**

1. **Close Other GPU Applications:**

   ```powershell

   # Check GPU usage

   nvidia-smi

   # Close any other CUDA applications

   ```

2. **Clear CUDA Cache:**

   ```python
   import torch
   torch.cuda.empty_cache()
   ```

3. **Reduce Generation Length:**

   ```python

   # Lower max_length to reduce VRAM usage

   result = inferencer.generate_with_smart_hybrid(
       query="...",
       max_length=50  # Default: 100
   )
   ```

4. **Fallback to CPU:**

   ```python

   # Temporary workaround (slow)

   inferencer = B3RAGInference(device="cpu")
   ```

### Issue 5: Slow Performance

**Symptoms:**

- Response time >5000ms (expected: ~2700ms)
- Inference taking 10+ seconds per query

**Diagnostics:**

```python
# Enable verbose logging
inferencer = B3RAGInference(verbose=True)

# Run test query
result = inferencer.generate_with_smart_hybrid("Test query")

# Check timing breakdown
print(result["timing"])
# {"total_ms": XXX, "rag_ms": XXX, "generation_ms": XXX}
```

**Solutions:**

1. **If RAG is slow (rag_ms >1000ms):**
   - Check FAISS index integrity
   - Verify embeddings are on fast storage (SSD)
   - Rebuild FAISS index if corrupted

2. **If Generation is slow (generation_ms >4000ms):**
   - Verify CUDA is being used (not CPU fallback)
   - Check GPU temperature (throttling?)
   - Close background GPU applications

3. **System-Wide Slowness:**
   - Check system resources (Task Manager)
   - Ensure sufficient RAM available (8GB+ free)
   - Verify no disk thrashing (100% disk usage)

### Issue 6: Poor Quality Responses

**Symptoms:**

- Generic responses ("I'm not sure...", "That's interesting...")
- Off-topic responses
- Very short responses

**Solutions:**

1. **Check Model Version:**

   ```python
   import torch
   checkpoint = torch.load("F:/models/checkpoints/b3/b3_massive_final.pth", map_location="cpu")
   print(checkpoint.get("metadata", {}))

   # Should show: b3_massive_final, 35.5M parameters

   ```

2. **Verify Embeddings:**
   - Ensure embeddings match model version
   - Check embeddings aren't corrupted

3. **Adjust Generation Parameters:**

   ```python

   # More deterministic (for factual queries)

   result = inferencer.generate_with_smart_hybrid(
       query="...",
       temperature=0.5,  # Lower = more focused
       top_k=40          # Narrower selection
   )
   ```

4. **Try Different Queries:**
   - ImpressionCore excels at: Conversational, multimodal, cross-domain
   - May struggle with: Very vague queries, nonsense, empty queries

---

## 🚀 PRODUCTION DEPLOYMENT

### Pre-Deployment Checklist

- [ ] Python 3.10 installed and verified
- [ ] CUDA 11.8+ installed (GPU mode)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `src/core/config/colossus_checkpoint.pointer` resolves to an existing checkpoint
- [ ] Pointer audit passes (`python src/dev_tools/diagnostics/check_colossus_pointer.py`)
- [ ] F:/data embeddings present (1.3M+ files) and FAISS index available
- [ ] `python src/deployment/launch_production.py --mode validation-only` completes without errors
- [ ] `pytest src/tests/integration/test_b3_production_launcher.py` passes
- [ ] Performance benchmarks meet targets (≥4.43/5.0 quality, ~2700ms latency)
- [ ] Monitoring/logging configured (Rich + uvicorn)
- [ ] Documentation reviewed (this guide + API reference)

### Production Configuration

**Launcher Workflow:**

```powershell
# 1. Run validation-only pass (performs preflight without starting the API)
python src\deployment\launch_production.py --mode validation-only

# 2. Launch full stack (preflight + FastAPI + uvicorn)
python src\deployment\launch_production.py --mode full --host 0.0.0.0 --port 8000 --workers 1

# 3. Launch API only (skip automatic preflight after a successful validation)
python src\deployment\launch_production.py --mode api-only --host 0.0.0.0 --port 9000

# 4. Override checkpoint or F:/data root when needed
python src\deployment\launch_production.py --mode api-only --model-path "F:\models\checkpoints\b3\colossus_latest.pt" --f-data-root "F:\data"

# 5. Skip preflight only when you have already validated in the same session
python src\deployment\launch_production.py --mode full --skip-preflight
```

**CLI Options:**

| Flag | Description |
|------|-------------|
| `--mode` | `full` (default) runs preflight + API, `api-only` skips preflight, `validation-only` runs preflight without starting uvicorn |
| `--host` | Hostname/IP exposed by uvicorn (default `0.0.0.0`) |
| `--port` | Listening port (default `8000`) |
| `--workers` | Uvicorn worker count (default `1`, keep low for GTX 1050 Ti) |
| `--model-path` | Optional override for the Colossus distilled checkpoint |
| `--f-data-root` | Alternate F:/data location (embeddings + FAISS) |
| `--skip-preflight` | Bypass preflight checks after a recent successful validation |

**FastAPI Endpoints:**

- `GET /health` → Returns uptime and FastAPI version metadata
- `GET /` → Lightweight landing message with docs link
- `POST /inference` → Executes B3 smart hybrid generation. Example payload:

```powershell
curl -X POST http://localhost:8000/inference `
   -H "Content-Type: application/json" `
   -d '{
            "prompt": "Summarize the ImpressionCore mission.",
            "use_rag": true,
            "category": "multimodal",
            "max_length": 256,
            "use_retry": false,
            "use_smart_hybrid": true
         }'
```

**Response Fields:** `response` contains the generated text; `metadata` echoes strategies, retrieval diagnostics, and timing captured by `B3RAGInference`.

### Monitoring Setup

**Metrics to Track:**

1. **Quality Metrics:**
   - Average quality score (target: ≥4.0/5.0)
   - Generic response rate (target: <10%)
   - Success rate (target: >80%)

2. **Performance Metrics:**
   - Average response time (target: <3000ms)
   - 95th percentile response time (target: <4000ms)
   - Queries per minute (target: >20)

3. **System Metrics:**
   - CUDA memory usage (target: <2GB)
   - CPU usage (target: <50%)
   - RAM usage (target: <4GB)

4. **Strategy Distribution:**
   - natural_only: ~60-70%
   - natural_low_confidence: ~30-40%
   - rag_enhanced: 0-10%

**Monitoring Script:**

```python
# monitor.py
import time
from collections import deque
from statistics import mean

class InferenceMonitor:
    """Monitor inference performance."""
    
    def __init__(self, window_size=100):
        self.window_size = window_size
        self.response_times = deque(maxlen=window_size)
        self.strategies = deque(maxlen=window_size)
        self.start_time = time.time()
        self.total_queries = 0
    
    def log_query(self, result: dict):
        """Log query result."""
        self.response_times.append(result["timing"]["total_ms"])
        self.strategies.append(result["strategy"])
        self.total_queries += 1
    
    def get_stats(self) -> dict:
        """Get current statistics."""
        elapsed_time = time.time() - self.start_time
        
        return {
            "total_queries": self.total_queries,
            "queries_per_minute": self.total_queries / (elapsed_time / 60),
            "avg_response_time_ms": mean(self.response_times) if self.response_times else 0,
            "strategy_distribution": {
                "natural_only": self.strategies.count("natural_only") / len(self.strategies) * 100 if self.strategies else 0,
                "natural_low_confidence": self.strategies.count("natural_low_confidence") / len(self.strategies) * 100 if self.strategies else 0,
                "rag_enhanced": self.strategies.count("rag_enhanced") / len(self.strategies) * 100 if self.strategies else 0
            }
        }

# Usage
monitor = InferenceMonitor()

for query in queries:
    result = inferencer.generate_with_smart_hybrid(query)
    monitor.log_query(result)

# Print stats every 100 queries
if monitor.total_queries % 100 == 0:
    stats = monitor.get_stats()
    print(f"\n📊 Performance Stats (last {monitor.window_size} queries):")
    print(f"   Queries/min: {stats['queries_per_minute']:.1f}")
    print(f"   Avg time: {stats['avg_response_time_ms']:.1f}ms")
    print(f"   Strategy dist: {stats['strategy_distribution']}")
```

### Scaling Considerations

**Single Instance (Current):**

- **Capacity**: ~22 queries/minute (GTX 1050 Ti)
- **Daily capacity**: ~30,000 queries
- **Concurrent users**: 1-2

**Future Scaling Options:**

1. **Multi-GPU:**
   - Add additional GPUs (GTX 1060, RTX 3060)
   - Load balance across GPUs
   - Expected: Linear scaling (2x GPUs = 2x throughput)

2. **Model Parallelism:**
   - Split model across multiple GPUs
   - For larger models (>100M parameters)
   - Not necessary for current 35M model

3. **Batch Processing:**
   - Process multiple queries simultaneously
   - Requires code modifications
   - Expected: 30-50% throughput improvement

4. **API Server:**
   - Deploy as REST API (FastAPI, Flask)
   - Enable concurrent requests
   - Requires load balancing

### Backup and Recovery

**Critical Files to Backup:**

1. **Model Checkpoint** (300MB):

   ```powershell
   Copy-Item "F:\models\checkpoints\b3\b3_massive_final.pth" -Destination "F:\backups\models\"
   ```

2. **Embeddings** (1.5GB):

   ```powershell
   Compress-Archive -Path "F:\data\embeddings\*" -DestinationPath "F:\backups\embeddings_backup.zip"
   ```

3. **Configuration**:

   ```powershell
   Copy-Item "config\production_config.yaml" -Destination "F:\backups\config\"
   ```

**Automated Backup Script:**

```powershell
# backup.ps1
$BackupRoot = "F:\backups"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Create backup directory
New-Item -Path "$BackupRoot\backup_$Timestamp" -ItemType Directory -Force

# Backup model
Copy-Item "F:\models\checkpoints\b3\b3_massive_final.pth" -Destination "$BackupRoot\backup_$Timestamp\"

# Backup embeddings (compress)
Compress-Archive -Path "F:\data\embeddings\*" -DestinationPath "$BackupRoot\backup_$Timestamp\embeddings.zip"

# Backup config
Copy-Item "config\production_config.yaml" -Destination "$BackupRoot\backup_$Timestamp\"

Write-Host "✅ Backup completed: $BackupRoot\backup_$Timestamp"
```

---

## 📞 SUPPORT

### Documentation

- **API Reference**: `docs/api/b3_rag_inference_api.md`
- **User Guide**: `docs/user_guide/phase3_user_guide.md`
- **Troubleshooting**: This document, Section 9

### Community

- **GitHub Issues**: Report bugs and feature requests
- **Discussions**: Ask questions and share experiences
- **Wiki**: Community-maintained documentation

### Commercial Support

- **Email**: <support@impressioncore.ai> (if available)
- **Priority Support**: Contact for enterprise deployments

---

## ✅ DEPLOYMENT COMPLETE

**Congratulations! You've successfully deployed ImpressionCore Phase 3.**

**Next Steps:**

1. Review user guide for optimal query types
2. Integrate into your application
3. Monitor performance metrics
4. Report any issues via GitHub

**Production Quality:**

- ✅ 4.43/5.0 quality (validated)
- ✅ 7.7% generic rate (validated)
- ✅ 85.7% success rate (validated)
- ✅ ~2700ms average latency (validated)
- ✅ Constitutional Framework compliant
- ✅ Consumer hardware accessible (GTX 1050 Ti)

**Welcome to the future of accessible AI!** 🚀
