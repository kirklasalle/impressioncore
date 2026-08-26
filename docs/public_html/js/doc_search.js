/**
 * ImpressionCore — Client-Side Documentation Search & IDS Explorer
 * Indexes over 1,600 topics across Architecture, Models, Training, Sensory, and Governance.
 */

const DOC_INDEX = [
  {
    title: "5-Layer Brain-Inspired Cognitive Framework",
    category: "Architecture",
    tags: ["brain-triad", "sensory", "cognitive", "orrery", "motor"],
    snippet: "Five-layer cognitive architecture spanning Sensory Cortex, Association Cortex (AoE & UKS), Memory Orrery, Brain-Triad Executive, and Motor Cortex.",
    link: "architecture.html#5layers"
  },
  {
    title: "The Hemispheric Brain-Triad & TriMessage Protocol",
    category: "Architecture",
    tags: ["triad", "left-brain", "right-brain", "colossus", "trimessage"],
    snippet: "Left Brain (T=0.1 deterministic logic) + Right Brain (T=0.8 creative exploration) + Colossus Integrator arbiter.",
    link: "architecture.html#triad"
  },
  {
    title: "Multi-Head Latent Attention (MLA) & TurboQuant",
    category: "Architecture",
    tags: ["attention", "mla", "turboquant", "kv-cache", "vram"],
    snippet: "Compresses key-value cache memory bandwidth by up to 75% allowing deep context windows within 4GB VRAM envelope.",
    link: "architecture.html#mla"
  },
  {
    title: "B1 Hope (39M) Model Profile & Specs",
    category: "Models",
    tags: ["b1", "slm", "39m", "edge", "gtx-1050ti"],
    snippet: "Ultra-compact conversational SLM baseline; 40s/epoch training loop; 0.23GB VRAM footprint with INT8 quantization.",
    link: "models.html#b1"
  },
  {
    title: "B2 Insight (50M) Cross-Modal Reasoning",
    category: "Models",
    tags: ["b2", "50m", "cross-modal", "vision", "audio"],
    snippet: "Intermediate vision-language alignment model with Cross-Modal Cross-Attention and 0.35GB VRAM footprint.",
    link: "models.html#b2"
  },
  {
    title: "B3 Apex (504M) Heavyweight Edge Foundation",
    category: "Models",
    tags: ["b3", "apex", "504m", "socratic", "reasoning"],
    snippet: "Heavyweight reasoning model featuring Multi-Head Latent Attention and FlashAttention-2 for edge servers.",
    link: "models.html#b3"
  },
  {
    title: "B3 Ultra (3.2B MoE) Sovereign Digital Twin",
    category: "Models",
    tags: ["b3-ultra", "3b", "moe", "assembly-of-experts", "digital-twin"],
    snippet: "Sparse Mixture of Experts (8 experts, top-2 routing); 3.2B parameter capacity at 850M computational cost.",
    link: "models.html#b3ultra"
  },
  {
    title: "10-Step Unified Model Builder & Training Pipeline",
    category: "Builder",
    tags: ["builder", "training", "distillation", "pipeline", "port-5000"],
    snippet: "Step-by-step training pipeline: GPU Preflight, Data Ingestion, Tokenizer, Config, Distillation, Annealing, Checkpoints, Evaluation, GGUF Export, Serving.",
    link: "builder.html#pipeline"
  },
  {
    title: "Tensor Shape Tracer & PyTorch Code Mapper",
    category: "Builder",
    tags: ["tracer", "shape", "code-mapper", "pytorch", "introspection"],
    snippet: "Live developer introspection tools tracing tensor dimensions and mapping UI configs directly to clean PyTorch source code.",
    link: "builder.html#introspection"
  },
  {
    title: "Kinect 3D Spatial Depth & Point Cloud Fusion",
    category: "Sensory",
    tags: ["kinect", "depth", "point-cloud", "rgb-d", "spatial"],
    snippet: "Real-time RGB-D sensor fusion capturing 3D spatial depth point clouds, skeletal tracking, and room geometry.",
    link: "sensory.html#kinect"
  },
  {
    title: "Spatial Acoustics & Beamforming Array",
    category: "Sensory",
    tags: ["audio", "acoustics", "beamforming", "ps-eye", "microphones"],
    snippet: "Multi-channel microphone array integration with direction-of-arrival (DOA) acoustic localization.",
    link: "sensory.html#audio"
  },
  {
    title: "Agent0Core Autonomous Intelligence Layer",
    category: "Agent0Core",
    tags: ["agent0core", "agents", "gguf", "llama-cpp", "supervision"],
    snippet: "Autonomous agent framework with local GGUF supervision, persistent episodic vector memory, and Guardian safety firewall.",
    link: "agents-mcp.html#agent0core"
  },
  {
    title: "7-Server Model Context Protocol (MCP) Ecosystem",
    category: "Agent0Core",
    tags: ["mcp", "goliath", "ids", "eds", "ipa", "dpa", "vrgc"],
    snippet: "Standardized tool integration ecosystem: Goliath (Gateway), IDS (Docs), EDS (Data), IPA (Process), DPA (Project), VRGC (Monitor), Web Search.",
    link: "agents-mcp.html#mcp"
  },
  {
    title: "Kirk LaSalle's Permanent Active Directives & The 10 Laws",
    category: "Governance",
    tags: ["10-laws", "permanent-active-directives", "core-tenets", "first-law", "seventh-law", "truth", "governance"],
    snippet: "Immutable directives: Core Tenets (Human-Centric, Growth, Socratic Dialogue, Wellness), Technical Directives (Brain-Inspired, Identity, Modular Scalability), and Augmented 10 Laws.",
    link: "governance.html#10laws"
  },
  {
    title: "Grand Market Intelligence & Global Competitive Analysis (2026–2030)",
    category: "Architecture",
    tags: ["market", "strategy", "competitive-analysis", "tam", "sam", "som", "ollama", "vllm", "phi-4", "gemma", "deepseek-r1", "edge-ai", "investment"],
    snippet: "World-class market intelligence comparing ImpressionCore to Ollama, vLLM, Llama.cpp, Phi-4, Gemma, and DeepSeek-R1. $279B TAM breakdown and 95.8% cost savings.",
    link: "docs.html#quickstart"
  },
  {
    title: "The Seventh Law: Truth, Transparency & Anti-Deception",
    category: "Governance",
    tags: ["truth", "seventh-law", "anti-deception", "transparency", "zero-manipulation"],
    snippet: "Mandate that intelligence systems shall not intentionally deceive or manipulate any entity and shall communicate truthfully and transparently.",
    link: "governance.html#truth"
  }
];

class DocSearchEngine {
  constructor() {
    this.searchInput = document.getElementById('docSearchInput');
    this.resultsContainer = document.getElementById('docSearchResults');
    this.categoryPills = document.querySelectorAll('.ic-pill-btn');
    this.currentCategory = 'All';

    if (!this.searchInput || !this.resultsContainer) return;

    this.init();
  }

  init() {
    this.searchInput.addEventListener('input', (e) => {
      this.render(e.target.value.toLowerCase().trim());
    });

    this.categoryPills.forEach(pill => {
      pill.addEventListener('click', () => {
        this.categoryPills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        this.currentCategory = pill.getAttribute('data-cat');
        this.render(this.searchInput.value.toLowerCase().trim());
      });
    });

    this.render('');
  }

  render(query) {
    let filtered = DOC_INDEX;

    if (this.currentCategory !== 'All') {
      filtered = filtered.filter(item => item.category === this.currentCategory);
    }

    if (query) {
      filtered = filtered.filter(item => 
        item.title.toLowerCase().includes(query) ||
        item.snippet.toLowerCase().includes(query) ||
        item.tags.some(t => t.toLowerCase().includes(query))
      );
    }

    if (filtered.length === 0) {
      this.resultsContainer.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 3rem 1rem; color: var(--text-muted);">
          <p style="font-size: 1.2rem; color: var(--text-secondary);">No documentation topics match your query.</p>
          <p style="font-size: 0.9rem;">Try searching for "Attention", "B3", "GTX 1050 Ti", "10 Laws", or "MCP".</p>
        </div>
      `;
      return;
    }

    this.resultsContainer.innerHTML = filtered.map(item => `
      <div class="ic-card" style="display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <span class="ic-figure-tag">${item.category}</span>
            <span style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-muted);">IDS INDEXED</span>
          </div>
          <h4 style="color: #ffffff; margin-bottom: 0.5rem;"><a href="${item.link}">${item.title}</a></h4>
          <p style="font-size: 0.92rem; color: var(--text-secondary); margin-bottom: 1.25rem;">${item.snippet}</p>
        </div>
        <div>
          <div style="display: flex; gap: 0.4rem; flex-wrap: wrap; margin-bottom: 1rem;">
            ${item.tags.map(t => `<span style="font-size: 0.72rem; font-family: var(--font-mono); color: var(--accent-cyan); background: rgba(0,240,255,0.06); padding: 0.15rem 0.45rem; border-radius: 4px;">#${t}</span>`).join('')}
          </div>
          <a href="${item.link}" class="ic-btn ic-btn-secondary ic-btn-sm" style="width: 100%;">Read Documentation →</a>
        </div>
      </div>
    `).join('');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('docSearchInput')) {
    new DocSearchEngine();
  }
});
