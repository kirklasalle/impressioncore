# 📘 ImpressionCore Models User Guide & Operator Manual

**Author:** Kirk LaSalle & Antigravity AI Partner  
**Target Audience:** AI Practitioners, Model Builders & System Operators  
**Date:** August 26, 2026  
**Status:** Canonical User & Operator Manual  

---

## 1. Introduction: The ImpressionCore Model Lineup

ImpressionCore provides a versatile family of brain-inspired AI models tailored for privacy-first, local execution on everyday hardware. Whether you are running a lightweight edge device with a 4GB graphics card or a high-end workstation, there is an ImpressionCore model designed for your environment.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       IMPRESSIONCORE MODEL HIERARCHY                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  ⚡ B1 Hope (39M)    ──> Ultra-low latency, real-time edge SLM (~0.23 GB VRAM)│
│  👁️ B2 Insight (50M) ──> Cross-modal reasoning & perception    (~0.35 GB VRAM)│
│  🧠 B3 Apex (504M)   ──> Heavyweight Socratic reasoning & code (~1.80 GB VRAM)│
│  🌐 B3 Ultra (3B)    ──> Multimodal 8-Expert Cognitive MoE     (~3.80 GB VRAM)│
│  🏛️ C1 Triad Plane   ──> Sovereign Left/Right/Oversight Triad  (Governed)     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Hardware Compatibility & Model Selection Guide

Find your hardware profile below to identify the optimal model configuration:

| Your Hardware Setup | Recommended Model | Recommended Precision | Expected Generation Speed |
| :--- | :--- | :---: | :---: |
| **Pure CPU (Intel i5 / AMD Ryzen 5, 16GB RAM)** | **B1 Hope 39M** | `INT8` or `FP32` | ~25–45 tokens/sec |
| **NVIDIA GTX 1050 Ti (4GB VRAM)** | **B1 Hope 39M** / **B2 Insight 50M** | `FP16` | ~55–65 tokens/sec |
| **NVIDIA GTX 1050 Ti (4GB VRAM)** | **B3 Apex 504M** | `FP16` (Grad Accum 16) | ~12–18 tokens/sec |
| **NVIDIA GTX 1050 Ti (4GB VRAM)** | **B3 Ultra 3B MoE** | `INT4` (Quantized) | ~6–10 tokens/sec |
| **NVIDIA RTX 3060 / 4060 (8GB–12GB VRAM)** | **B3 Apex 504M** / **B3 Ultra 3B** | `FP16` | ~60–120 tokens/sec |
| **Multi-GPU / High-End Server (16GB+ VRAM)** | **C1 Colossus Triad Suite** | `FP16` / `BF16` | ~150+ tokens/sec |

---

## 3. How to Build Models in the ImpressionCore Web Builder

The **ImpressionCore Model Builder** provides a guided, visual interface accessible in your web browser.

### Step 1: Launch the Local Builder Server
Double-click `launch_builder.bat` in the project root, or execute via PowerShell:
```powershell
.venv310\Scripts\python.exe src/interfaces/web/server.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** and sign in:
- **Username:** `admin`
- **Password:** `admin`

---

### Step 2: Auto-Load Model Presets
1. Click **Model Definition** in the sidebar.
2. Select your desired profile from the **Model Size Preset** dropdown:
   - `B1 Hope 39M (Edge SLM)`
   - `B2 Insight 50M`
   - `B3 Apex 504M`
   - `B3 Ultra 3B MoE`
3. **Watch the fields auto-fill:** Layers, Hidden Size, Attention Heads, Context Window, and FFN Dimension instantly populate with the verified optimal settings.
4. **Inspect the VRAM Estimation Bar:** Confirm the green indicator showing your model safely fits within your GPU's VRAM budget.
5. Click **Save Configuration**.

---

### Step 3: Launch Training & Build Your Model
1. Click **Training** in the sidebar.
2. Adjust your training parameters (or keep canonical defaults):
   - **Epochs:** 2–3
   - **Batch Size:** 1 or 2
   - **Precision:** `fp16` (Half Precision)
3. Click **Start Training**:
   - The background training loop begins immediately.
   - Monitor real-time **Loss Convergence** (watch loss decrease from ~5.0 down to sub-1.0), **Step Counter**, and **GPU VRAM Allocation**.

---

### Step 4: Test Your Model with Live Inference
1. Click **Inference** in the sidebar.
2. Select your newly trained model checkpoint.
3. Configure your text generation settings:
   - **Temperature:** `0.7` *(Lower for factual logic, higher for creative responses)*
   - **Top-P:** `0.90`
   - **Max Tokens:** `128`
4. Enter a test prompt and click **Generate**:
   > *"Explain the core principles of ImpressionCore digital identity:"*
5. Review the generated stream and latency statistics.

---

### Step 5: Benchmark & Evaluate
1. Click **Evaluation** in the sidebar.
2. Select evaluation metrics: `Accuracy`, `BLEU`, `F1 Score`, `Perplexity`, `Latency`.
3. Click **Run Evaluation** to score your model's quality.

---

### Step 6: Package for Production Deployment
1. Click **Deployment** in the sidebar.
2. Select your export format: `PyTorch (.pt)`, `SafeTensors (.safetensors)`, or `ONNX (.onnx)`.
3. Select optimization level: `Quantized INT8` (Recommended for Edge) or `FP16`.
4. Click **Package Model for Deployment**:
   - The bundle is saved in `production_packages/` ready for distribution.

---

## 4. Inference Parameters & Tuning Tips

| Parameter | Recommended Range | Description & Tuning Impact |
| :--- | :---: | :--- |
| **Temperature** | `0.2` – `0.8` | Controls randomness. Use `0.2` for deterministic code/math; `0.7` for natural Socratic conversation. |
| **Top-P (Nucleus)**| `0.80` – `0.95` | Cumulative probability cutoff. `0.90` eliminates nonsensical tail tokens. |
| **Top-K** | `30` – `50` | Filters vocabulary to the top $K$ candidates before sampling. |
| **Max Tokens** | `64` – `512` | Maximum length of generated output tokens per response. |
| **Repetition Penalty**| `1.05` – `1.20` | Penalizes repeated n-grams, preventing cyclic loops. |

---

## 5. Frequently Asked Questions & Troubleshooting

### Q1: What should I do if I encounter an "Out of Memory" (CUDA OOM) error?
- **Solution 1:** In **Training**, reduce `Batch Size` to `1` and increase `Gradient Accumulation Steps` to `8` or `16`.
- **Solution 2:** Ensure `Precision` is set to `fp16` rather than `fp32`.
- **Solution 3:** In `Model Definition`, enable `Gradient Checkpointing`.

### Q2: Can I run ImpressionCore models without a dedicated GPU?
- **Yes!** ImpressionCore includes an automatic CPU fallback engine. B1 Hope 39M and B2 Insight 50M run smoothly on standard quad-core CPUs.

### Q3: Where are my trained model checkpoints stored?
- Checkpoints are saved locally in `F:\models\checkpoints` (or the folder configured in your Training settings) and packaged into `production_packages/`.
