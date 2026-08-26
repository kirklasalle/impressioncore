# Audit and Design Proposal: World-Class Interactive Model Visualization

## 🔍 Current Architecture Page Audit

Our current Vis.js implementation provides basic panning, zooming, and node coloring, but has several limitations that prevent it from being a truly "world-class" developer tool:

1. **Linear Sequential Layout:** The layout is a static 2D linear chain. It doesn't dynamically adapt when layers are clicked or inspected, making it feel like a static diagram that has been made zoomable, rather than a living tool.
2. **Lack of Dynamic Compound Folding (No Hierarchy):** Users cannot click on a large node (like "Transformer Block 0") to "expand" it inline or double-click to drill down. The graph remains crowded (in "Complete View") or too sparse (in "Simplified View").
3. **No Dynamic Shape/Dimension Tracing:** A critical task for model developers is tracing how tensor dimensions change across layers (e.g., sequence length, model dimensions, head projections). Currently, these shapes are static strings rather than interactive flow tags.
4. **Disconnected Details Panel:** The details table at the bottom is static. It does not update dynamically when a user hovers over or clicks on nodes in the network graph.

---

## 🎨 World-Class Interactive Presentation Concepts

Here are three distinct architectural directions we can take to elevate this page to a premium, production-grade tool:

### Concept A: Dynamic Hierarchical Expand/Collapse (Vis.js / Cytoscape)
Allows the user to see the high-level flow, and double-click or click an "Expand" badge on any block to unfold its internal structure (Attention, MLP, LayerNorm, Residual Addition) inline.

* **Interactivity:** Zooming, panning, dragging, click-to-expand, click-to-collapse, and dynamic color-coding.
* **Goal Alignment:** Helps developers isolate specific sub-blocks of the network without getting overwhelmed by the complete 50+ node list.

### Concept B: 3D Force-Directed Model Graph (Three.js / 3d-force-graph)
A full 3D interactive mesh representation of the model architecture, allowing the user to rotate the model structure in 3D, fly through blocks, and inspect layer weight heatmaps.

* **Interactivity:** Orbit controls, glow effects, fly-to-node animation, and 3D particle flows along data pathways showing forward/backward pass directions.
* **Goal Alignment:** High-impact visual that immediately clarifies multi-branch networks (e.g., cross-attention, multimodal input paths).

### Concept C: Split-Screen Flow Inspector (Visualizer + Code Mapper)
A split-screen view: the left side displays an interactive SVG layer block diagram (similar to Netron), and the right side displays a tabbed detail inspector containing:
1. **Interactive Charts:** Highcharts/Chart.js showing parameter footprint per layer.
2. **Code Mapper:** The exact PyTorch initialization code of that specific submodule.
3. **Dimension Tracer:** Drag-and-drop inputs to trace shapes through the network layers.

---

## 🏗️ Comparative Options Table

| Option | Dev Complexity | Performance Cost | UX / Researcher Utility | Aesthetics |
| :--- | :---: | :---: | :---: | :---: |
| **Option 1: Hierarchical Expand/Collapse** | Medium | Low | High (Focus on specific layers) | Premium |
| **Option 2: 3D Force-Directed Graph** | High | Medium | Medium (High impact, lower code clarity) | World-Class |
| **Option 3: Split-Screen Flow & Code Inspector** | High | Low | Extremely High (Directly aids debugging) | Professional |

---

## 🛠️ Proposed Implementation Plan (Phased)

1. **Phase 1: Table & Style Unification** ✅ (Completed: resolved contrast issues and standardized theme color mapping).
2. **Phase 2: Interactive State Engine** (Link node clicks to the details panel, update labels dynamically).
3. **Phase 3: Implement Chosen Visualization Concept** (Hierarchical Folding, 3D, or Code Inspector).
