# 🎨 ImpressionCore Public Website — Illustration & Visual Asset Manifest

**Document:** Comprehensive Image, Diagram, and Visual Component Manifest  
**Target:** `docs/public_html/` Generation Suite  
**Date:** August 2026  
**Status:** Master Asset Specifications Matrix  

---

## 📐 Image Asset Sizing & Formats Specification

To guarantee a "beyond SOTA" aesthetic experience across all displays (from high-DPI smartphones to 4K / 5K ultrawide monitors), every visual asset is defined with precise aspect ratios, target resolutions, CSS frame classes, and fallback protocols:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 ASSET DIMENSION MATRIX                                 │
├───────────────────┬──────────────┬─────────────────────────┬───────────────────────────┤
│ Format Tier       │ Aspect Ratio │ Master Dimensions       │ Responsive Breakpoints    │
├───────────────────┼──────────────┼─────────────────────────┼───────────────────────────┤
│ 🌌 Cosmic Ultra   │ 21:9         │ 3840×1645 / 2560×1097   │ 1920×822, 1280×548, 768px │
│ 🖥️ Panoramic Hero │ 16:9         │ 2560×1440 / 1920×1080   │ 1280×720, 960×540, 640px  │
│ 📐 Technical Card │ 4:3          │ 1600×1200 / 1200×900    │ 800×600, 600×450, 400px   │
│ 💎 High-Res Ratio │ 3:2          │ 1800×1200 / 1200×800    │ 900×600, 600×400, 450px   │
│ 🏷️ Square Avatar  │ 1:1          │ 1024×1024 / 512×512     │ 256×256, 128×128, 64×64   │
│ 📱 Mobile Spreads │ 9:16         │ 1080×1920 / 720×1280    │ 540×960, 360×640          │
└───────────────────┴──────────────┴─────────────────────────┴───────────────────────────┘
```

---

## 🖼️ Catalog of Core Visual Assets & Exact Workspace Mappings

Below is the verified registry of existing visual assets in the ImpressionCore workspace, mapped to their website sections, resolutions, and generated illustration captions:

### 1. Hero & Architectural Visuals

| Asset Identifier | Source File Path | Optimal Ratio & Dimensions | Target Web Placement | Visual Description & Copy Context |
|---|---|---|---|---|
| `HERO_ARCHITECTURE` | `docs/assets/impressioncore_hero_architecture.png` | **21:9 / 16:9** (2560×1440) | `index.html` (Hero), `architecture.html` (Top) | Five-layer brain-inspired multimodal AI architecture diagram illustrating Sensory Cortex, Cognitive Core (AoE & UKS), Memory Orrery, Brain-Triad Executive, and Motor Cortex. |
| `BUILDER_SUITE_FLAGSHIP` | `docs/assets/builder_ui_interactive_suite.png` | **16:9** (1920×1080) | `index.html` (Showcase), `builder.html` (Hero) | Flagship Cyber-Noir Glassmorphism suite depicting the live model builder, parameter presets, 3D neural node graph, and real-time loss telemetry. |
| `COGNITIVE_TRIAD` | `docs/assets/cognitive_triad_orchestration.png` | **16:9 / 4:3** (1920×1080) | `architecture.html`, `governance.html` | The Brain-Triad orchestration system: Analytical Left Hemisphere ($T=0.1$), Creative Right Hemisphere ($T=0.8$), and Colossus Central Arbiter with 10 Laws oversight. |
| `MODEL_LINEUP_FLOW` | `docs/assets/model_lineup_and_builder_flow.png` | **16:9 / 3:2** (1920×1080) | `models.html`, `builder.html` | Canonical model lineup table (B1 39M, B2 50M, B3 504M, B3 Ultra 3B MoE) linked with the 10-step unified training & distillation pipeline. |

---

### 2. Live Builder Introspection & Telemetry Visuals

| Asset Identifier | Source File Path | Optimal Ratio & Dimensions | Target Web Placement | Visual Description & Copy Context |
|---|---|---|---|---|
| `BUILDER_TOP_PREFLIGHT` | `docs/assets/builder_live_unified_builder_top.png` | **16:9** (1920×1080) | `builder.html` (Step 1) | Live GPU preflight, hardware capability check, VRAM budget tracker, and 10-step training pipeline controller on Port 5000. |
| `BUILDER_3D_ORBIT` | `docs/assets/builder_live_architecture_orbit.png` | **16:9 / 4:3** (1600×1000) | `builder.html`, `index.html` | Interactive 3D neural node orbit visualizing layer connectivity, tensor dimensions, and forward pass routing in real time. |
| `BUILDER_MODEL_PRESETS` | `docs/assets/builder_live_architecture_details.png` | **16:9** (1920×1080) | `models.html`, `builder.html` | Model definition selector showing auto-population of canonical B-Series parameters and GTX 1050 Ti VRAM budget bar. |
| `BUILDER_TRAINING_MONITOR` | `docs/assets/builder_live_training_progress.png` | **16:9** (1920×1080) | `builder.html` (Step 6) | Live training progress dashboard with real-time loss convergence curves, Cosine Annealing learning rate schedule, and step counter. |
| `BUILDER_SHAPE_TRACER` | `docs/assets/builder_live_shape_tracer.png` | **16:9** (1920×1080) | `builder.html` (Introspection) | Live tensor shape tracer inspecting batch dimensions, hidden sizes, and intermediate layer representations. |
| `BUILDER_CODE_MAPPER` | `docs/assets/builder_live_code_mapper.png` | **16:9** (1920×1080) | `builder.html` (Code Engine) | PyTorch code mapper directly correlating UI parameter selections with underlying clean PyTorch neural network classes. |
| `BUILDER_CHAT_ASSISTANT` | `docs/assets/builder_live_chat.png` | **16:9 / 4:3** (1600×1000) | `builder.html` (Assistant) | Embedded AI model builder assistant for querying architectural parameters, hyperparameters, and live diagnostics. |
| `BUILDER_INTERACTIVE_CONFIG` | `docs/assets/builder_live_interactive_config.png` | **16:9** (1920×1080) | `builder.html`, `models.html` | Dynamic parameter sliders for hidden size, layers, and context length with real-time hardware feasibility scoring. |
| `BUILDER_DATA_PREP` | `docs/assets/builder_live_data_prep.png` | **16:9** (1920×1080) | `builder.html` (Step 2) | Data ingestion and dataset preparation interface supporting streaming JSONL, text, audio, and visual feature matrices. |
| `BUILDER_SYS_REQUIREMENTS` | `docs/assets/builder_live_system_requirements.png` | **16:9** (1920×1080) | `docs.html`, `index.html` | Hardware compatibility checker showing multi-tier support from GTX 1050 Ti up to enterprise GPU clusters. |

---

### 3. Sensory, Robotics & Embodiment Visuals

| Asset Identifier | Source File Path | Optimal Ratio & Dimensions | Target Web Placement | Visual Description & Copy Context |
|---|---|---|---|---|
| `KINECT_DEPTH_TRACKING` | `docs/assets/screenshot53-frontend-kinect.png` | **16:9** (1920×1080) | `sensory.html` (Hero) | Kinect sensor fusion interface capturing 3D spatial depth point clouds, infrared human tracking, and environment mapping. |
| `SPATIAL_ACOUSTICS` | `docs/assets/screenshot26-tracking-and-accoustics.png` | **16:9** (1920×1080) | `sensory.html` (Acoustics) | Multi-channel microphone array tracking and acoustic beamforming for real-time spatial speaker localization. |
| `NEURAL_THOUGHT_STREAM` | `docs/assets/screenshot31-neural-thought-stream.png` | **16:9** (1920×1080) | `sensory.html`, `architecture.html` | Real-time neural thought stream showing live token probability distributions and latency metrics during continuous processing. |
| `QUICKCAM_ORBIT_VISION` | `docs/assets/[Neural] QuickCam Orbit [DSHOW].png` | **4:3 / 16:9** (1280×960) | `sensory.html` (Robotics) | Pan-tilt-zoom robotic camera tracking integration with direct DirectShow driver hook and facial coordinate locks. |
| `AVATAR_PROSODY_RESPONSE` | `docs/assets/screenshot36-avatar-response-01.png` | **16:9** (1920×1080) | `sensory.html`, `governance.html` | Digital twin conversational avatar showing emotional prosody synchronization and real-time speech synthesis. |

---

### 4. Agentic Intelligence, Governance & Proofs

| Asset Identifier | Source File Path | Optimal Ratio & Dimensions | Target Web Placement | Visual Description & Copy Context |
|---|---|---|---|---|
| `TASKMGR_GPU_PROOF` | `docs/assets/TaskManager-GPU_Performance_Screenshot.png` | **16:9 / 4:3** (1280×720) | `index.html`, `models.html` | Empirical Windows Task Manager proof demonstrating stable GPU VRAM utilization strictly bounded under 4GB on NVIDIA GTX 1050 Ti. |
| `MLA_ATTENTION_DIAGRAM` | `docs/assets/muti_head_latent_attention.png` | **16:9 / 3:2** (1600×1000) | `architecture.html` (MLA) | Mathematical diagram of Multi-Head Latent Attention showing compressed key-value latent projections and RoPE decoupling. |
| `MEMORY_ORRERY_GRAPH` | `docs/assets/solar_system_knowledge_graph.png` | **4:3 / 1:1** (1024×1024) | `architecture.html`, `index.html` | Dynamic Memory Orrery cosmic graph showing planetary knowledge nodes orbiting the central cognitive sun. |
| `AGENTIC_CONTROL_DASHBOARD` | `docs/assets/agentic_control_01.png` | **16:9** (1920×1080) | `agents-mcp.html` (Hero) | Agent0Core control center with autonomous tool execution, Guardian safety firewall, and task execution logs. |
| `UKS_KNOWLEDGE_STORE` | `docs/assets/knowledge_ai_Knowledge_store_01.png` | **16:9** (1920×1080) | `agents-mcp.html` (UKS) | Universal Knowledge Store (UKS) semantic vector indexing and graph relation retrieval interface. |
| `AVATAR_LUKE_TWIN` | `docs/assets/Luke.png` | **1:1 / 4:3** (1024×1024) | `governance.html`, `index.html` | Digital Impression prototype avatar "Luke", embodying the lifelong digital companion and secure personal identity mission. |

---

## 🎨 Interactive CSS Presentation Classes

All illustrations in the website will be embedded using dedicated semantic CSS containers providing glowing cyber-borders, glassmorphism backdrop reflections, and interactive zoom modals:

```css
/* Master Glowing Illustration Frame */
.ic-figure-frame {
  position: relative;
  border-radius: 1rem;
  overflow: hidden;
  border: 1px solid var(--border-glass);
  background: var(--bg-glass-card);
  box-shadow: var(--shadow-glass);
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.ic-figure-frame:hover {
  border-color: var(--border-glass-bright);
  box-shadow: var(--shadow-neon-cyan), var(--shadow-glass);
  transform: translateY(-4px) scale(1.01);
}

.ic-figure-frame img {
  width: 100%;
  height: auto;
  display: block;
  object-fit: cover;
  transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.ic-figure-frame:hover img {
  transform: scale(1.03);
}

/* Technical Telemetry Caption */
.ic-figure-caption {
  padding: 0.85rem 1.25rem;
  font-family: var(--font-mono);
  font-size: 0.82rem;
  color: var(--accent-cyan);
  background: rgba(10, 15, 24, 0.85);
  border-top: 1px solid var(--border-glass);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
```

---

*This asset manifest ensures every illustration in the ImpressionCore archive is utilized with maximum aesthetic impact and technical precision.*
