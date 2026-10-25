r"""Generates index.html for D:\Projects\Websites\.mcp."""
import pathlib

DEST = pathlib.Path(r"D:\Projects\Websites\.mcp")

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>.mcp — Model Context Protocol Enterprise Tooling Fleet | Kirk LaSalle Engineering</title>
  <meta name="description" content="Enterprise-grade, governance-native Model Context Protocol (MCP) tooling fleet. 8 specialized micro-servers, 128 registered production tools, unified swarm memory, and kernel-level stdio stream guards.">
  <meta name="author" content="Kirk LaSalle">
  <meta name="keywords" content="Model Context Protocol, MCP, AI Agents, Claude Desktop, Antigravity IDE, Cursor, Goliath, Swarm Memory, Agentic Sacred Covenant">

  <!-- Open Graph / Facebook / LinkedIn -->
  <meta property="og:type" content="website">
  <meta property="og:title" content=".mcp — Governance-Native Model Context Protocol Enterprise Fleet">
  <meta property="og:description" content="8 specialized micro-servers, 128 registered tools, and unified swarm memory engineered for autonomous agents, bound by Kirk LaSalle's Agentic Sacred Covenant.">
  <meta property="og:image" content="assets/images/hero_banner.jpg">

  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

  <!-- FontAwesome 6.5.1 -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

  <!-- Chart.js 4.4.1 -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>

  <!-- Stylesheet -->
  <link rel="stylesheet" href="styles.css">
</head>
<body>

  <!-- ==========================================================================
       Global Header & Sticky Navigation
       ========================================================================== -->
  <header class="site-header">
    <div class="container header-container">
      <div class="brand-wrapper">
        <a href="#hero" class="brand-logo" id="brand-logo-link">
          <div class="brand-icon"><i class="fa-solid fa-network-wired"></i></div>
          <span>.mcp</span>
        </a>
        <div class="badge badge-status">
          <span class="badge-pulse-dot"></span>
          <span>8/8 Gate Passed</span>
        </div>
      </div>

      <nav>
        <ul class="nav-links">
          <li><a href="#hero" class="nav-link active">Overview</a></li>
          <li><a href="#fleet" class="nav-link">Micro-Servers</a></li>
          <li><a href="#governance" class="nav-link">Governance</a></li>
          <li><a href="#architecture" class="nav-link">Architecture</a></li>
          <li><a href="#demo" class="nav-link">Self-Test Demo</a></li>
          <li><a href="#setup" class="nav-link">1-Click Setup</a></li>
          <li><a href="#market" class="nav-link">Market Standing</a></li>
          <li><a href="#pricing" class="nav-link">Roadmap</a></li>
        </ul>
      </nav>

      <div class="nav-actions">
        <a href="#setup" class="btn btn-secondary btn-sm" id="nav-setup-btn">
          <i class="fa-solid fa-bolt"></i> 1-Click Setup
        </a>
        <a href="https://github.com/kirklasalle/.mcp" target="_blank" rel="noopener" class="btn btn-primary btn-sm" id="nav-github-btn">
          <i class="fa-brands fa-github"></i> Star on GitHub
        </a>
      </div>
    </div>
  </header>

  <main>
    <!-- ==========================================================================
         Section 1: Hero Section
         ========================================================================== -->
    <section class="hero-section" id="hero">
      <div class="container">
        <div class="hero-grid">
          
          <div class="hero-content">
            <div class="hero-tags">
              <span class="badge badge-protocol">
                <i class="fa-solid fa-code-commit"></i> MCP Standard 2025-11-25
              </span>
              <span class="badge badge-tools">
                <i class="fa-solid fa-toolbox"></i> 128 Production Tools
              </span>
              <span class="badge badge-status">
                <i class="fa-solid fa-shield-halved"></i> 100% Stdio Stream Guarded
              </span>
            </div>

            <h1 class="hero-title">
              The <span class="text-gradient-primary">Governance-Native</span> Model Context Protocol Enterprise Fleet
            </h1>

            <p class="hero-subtitle">
              An enterprise suite of <strong>8 specialized, project-agnostic micro-servers</strong> engineered for autonomous AI agents (Claude Desktop, Google Antigravity IDE, Cursor, Windsurf). Featuring <strong>Goliath swarm memory multiplexing</strong>, zero-marginal-cost academic research, and constitutional oversight under Kirk LaSalle's <strong>Agentic Sacred Covenant</strong>.
            </p>

            <div class="hero-actions">
              <a href="#fleet" class="btn btn-primary" id="hero-explore-btn">
                <i class="fa-solid fa-layer-group"></i> Explore 8 Servers
              </a>
              <a href="#setup" class="btn btn-secondary" id="hero-setup-btn">
                <i class="fa-solid fa-plug"></i> 1-Click Client Setup
              </a>
              <a href="#demo" class="btn btn-emerald" id="hero-demo-btn">
                <i class="fa-solid fa-terminal"></i> Run Fleet Self-Test
              </a>
            </div>
          </div>

          <div class="hero-visual">
            <!-- Live Telemetry Card -->
            <div class="telemetry-card glass-card">
              <div class="telemetry-header">
                <div class="telemetry-title">
                  <i class="fa-solid fa-microchip" style="color: var(--accent-cyan);"></i>
                  <span>FLEET TELEMETRY & HARDWARE GUARD</span>
                </div>
                <span class="badge badge-status" style="font-size: 0.72rem;">ACTIVE</span>
              </div>

              <div class="telemetry-rows">
                <div class="telemetry-row">
                  <span class="telemetry-label">Master Multiplexer</span>
                  <span class="telemetry-val" style="color: #a5b4fc;">goliath/server.py</span>
                </div>
                <div class="telemetry-row">
                  <span class="telemetry-label">Active Protocol Standard</span>
                  <span class="telemetry-val" style="color: var(--accent-cyan);">2025-11-25 (JSON-RPC 2.0)</span>
                </div>
                <div class="telemetry-row">
                  <span class="telemetry-label">Kernel Stdio Purity</span>
                  <span class="telemetry-val" style="color: var(--accent-emerald);">100% (stdout redirected)</span>
                </div>
                <div class="telemetry-row">
                  <span class="telemetry-label">Swarm Blackboard State</span>
                  <span class="telemetry-val" style="color: var(--accent-purple);">Synchronized (.json)</span>
                </div>
                <div>
                  <div class="telemetry-row" style="margin-bottom: 0.2rem;">
                    <span class="telemetry-label">Consumer GPU VRAM Budget</span>
                    <span class="telemetry-val" id="hero-vram-text" style="color: var(--accent-amber);">0.548 GB / 4.000 GB (13.7%)</span>
                  </div>
                  <div class="progress-bar-bg">
                    <div class="progress-bar-fill" id="hero-vram-fill"></div>
                  </div>
                </div>
                <div class="telemetry-row" style="margin-top: 0.4rem;">
                  <span class="telemetry-label">Failure Contract</span>
                  <span class="telemetry-val" style="color: #f43f5e;">Strict isError: true (No False Success)</span>
                </div>
              </div>
            </div>

            <!-- Banner Thumbnail with Lightbox trigger -->
            <div class="hero-banner-thumb open-lightbox" data-src="assets/images/hero_banner.jpg" title="Click to view full architecture preview">
              <img src="assets/images/hero_banner.jpg" alt="Model Context Protocol Enterprise Tooling Fleet Banner">
            </div>
          </div>

        </div>
      </div>
    </section>

    <!-- ==========================================================================
         Section 2: KPI & Metrics Ribbon
         ========================================================================== -->
    <section class="metrics-section">
      <div class="container">
        <div class="metrics-grid">
          <div class="metric-item">
            <span class="metric-number text-gradient-primary">8</span>
            <span class="metric-label">Micro-Servers</span>
          </div>
          <div class="metric-item">
            <span class="metric-number text-gradient-emerald">128</span>
            <span class="metric-label">Production Tools</span>
          </div>
          <div class="metric-item">
            <span class="metric-number" style="color: var(--accent-cyan);">0</span>
            <span class="metric-label">Stdout Corruptions</span>
          </div>
          <div class="metric-item">
            <span class="metric-number" style="color: var(--accent-purple);">10</span>
            <span class="metric-label">Sacred Covenant Laws</span>
          </div>
          <div class="metric-item">
            <span class="metric-number" style="color: var(--accent-amber);">4.0 GB</span>
            <span class="metric-label">GPU VRAM Ceiling</span>
          </div>
          <div class="metric-item">
            <span class="metric-number" style="color: #f43f5e;">$12.4B</span>
            <span class="metric-label">2028 TAM (Agent Tools)</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ==========================================================================
         Section 3: Fleet Showcase (Interactive Explorer)
         ========================================================================== -->
    <section class="section" id="fleet">
      <div class="container">
        <div class="section-header">
          <span class="section-pretitle">Autonomous Tooling Fleet</span>
          <h2 class="section-title">The 8 Enterprise Micro-Servers</h2>
          <p class="section-description">
            Each micro-server is project-agnostic, independently executable over stdio, and seamlessly federated into Goliath for single-endpoint agent workflows.
          </p>
        </div>

        <!-- Filter Bar -->
        <div class="filter-bar">
          <button class="filter-btn active" data-filter="all">All Servers (8)</button>
          <button class="filter-btn" data-filter="multiplexer">Gateway & Memory (1)</button>
          <button class="filter-btn" data-filter="code">Code & GraphRAG (2)</button>
          <button class="filter-btn" data-filter="research">Deep Research & Curation (3)</button>
          <button class="filter-btn" data-filter="robotics">Robotics & Diagnostics (2)</button>
        </div>

        <!-- Server Grid -->
        <div class="server-grid">
          
          <!-- 1. GOLIATH -->
          <div class="server-card glass-card" data-category="multiplexer">
            <div class="server-card-top">
              <div class="server-card-header">
                <div class="server-id-block">
                  <div class="server-icon icon-goliath"><i class="fa-solid fa-cubes"></i></div>
                  <div class="server-name-block">
                    <h3>goliath</h3>
                    <span class="server-canonical">goliath/server.py</span>
                  </div>
                </div>
                <span class="badge badge-tools">50 Tools</span>
              </div>
              <p class="server-desc">
                Master gateway multiplexer aggregating all 7 child micro-servers into a single client connection. Manages distributed episodic blackboard memory and consumer GPU VRAM budget telemetry.
              </p>
              <ul class="server-features">
                <li><i class="fa-solid fa-check"></i> 8-in-1 Multiplexed stdio bridge</li>
                <li><i class="fa-solid fa-check"></i> Persistent swarm memory blackboard</li>
                <li><i class="fa-solid fa-check"></i> Active 4GB consumer GPU VRAM safety monitor</li>
              </ul>
            </div>
            <div class="server-card-bottom">
              <span class="badge badge-status">Protocol: 2025-11-25</span>
              <button class="btn btn-secondary btn-sm inspect-payload-btn" data-server="goliath">
                <i class="fa-solid fa-terminal"></i> Inspect Payload
              </button>
            </div>
          </div>

          <!-- 2. IDS -->
          <div class="server-card glass-card" data-category="code">
            <div class="server-card-top">
              <div class="server-card-header">
                <div class="server-id-block">
                  <div class="server-icon icon-ids"><i class="fa-solid fa-diagram-project"></i></div>
                  <div class="server-name-block">
                    <h3>ids</h3>
                    <span class="server-canonical">ids/server_ai_enhanced.py</span>
                  </div>
                </div>
                <span class="badge badge-tools">6 Tools</span>
              </div>
              <p class="server-desc">
                Intelligent Documentation System. Semantic code intelligence, GraphRAG knowledge graph construction via GraphBridge, AST symbol parsing, and automated documentation scoring.
              </p>
              <ul class="server-features">
                <li><i class="fa-solid fa-check"></i> Semantic AST symbol & entity indexing</li>
                <li><i class="fa-solid fa-check"></i> GraphRAG relationship queries</li>
                <li><i class="fa-solid fa-check"></i> Automated documentation health scoring</li>
              </ul>
            </div>
            <div class="server-card-bottom">
              <span class="badge badge-status">Protocol: 2025-11-25</span>
              <button class="btn btn-secondary btn-sm inspect-payload-btn" data-server="ids">
                <i class="fa-solid fa-terminal"></i> Inspect Payload
              </button>
            </div>
          </div>

          <!-- 3. EDS -->
          <div class="server-card glass-card" data-category="research">
            <div class="server-card-top">
              <div class="server-card-header">
                <div class="server-id-block">
                  <div class="server-icon icon-eds"><i class="fa-solid fa-graduation-cap"></i></div>
                  <div class="server-name-block">
                    <h3>eds</h3>
                    <span class="server-canonical">eds/server_enhanced.py</span>
                  </div>
                </div>
                <span class="badge badge-tools">9 Tools</span>
              </div>
              <p class="server-desc">
                Educational Data Scraper & Multi-Modal Curator. License-compliant academic crawling (MIT OpenCourseWare, arXiv, Wikipedia CC-BY-SA), multi-modal quality assessment, and ethical rate-limiting.
              </p>
              <ul class="server-features">
                <li><i class="fa-solid fa-check"></i> Ethical scraping with robots.txt enforcement</li>
                <li><i class="fa-solid fa-check"></i> Automated CC-BY-SA / MIT license detection</li>
                <li><i class="fa-solid fa-check"></i> Multi-modal deduplication & clean text distillation</li>
              </ul>
            </div>
            <div class="server-card-bottom">
              <span class="badge badge-status">Protocol: 2025-11-25</span>
              <button class="btn btn-secondary btn-sm inspect-payload-btn" data-server="eds">
                <i class="fa-solid fa-terminal"></i> Inspect Payload
              </button>
            </div>
          </div>

          <!-- 4. IPA -->
          <div class="server-card glass-card" data-category="research">
            <div class="server-card-top">
              <div class="server-card-header">
                <div class="server-id-block">
                  <div class="server-icon icon-ipa"><i class="fa-solid fa-magnifying-glass-chart"></i></div>
                  <div class="server-name-block">
                    <h3>ipa</h3>
                    <span class="server-canonical">ipa/server_ultimate.py</span>
                  </div>
                </div>
                <span class="badge badge-tools">6 Tools</span>
              </div>
              <p class="server-desc">
                Intelligent Processing Assistant. Advanced search operator harness (50+ specialized query operators), live arXiv preprint extraction, multi-step research synthesis, and citation formatting.
              </p>
              <ul class="server-features">
                <li><i class="fa-solid fa-check"></i> 50+ Specialized query operators</li>
                <li><i class="fa-solid fa-check"></i> Live arXiv academic preprint retrieval</li>
                <li><i class="fa-solid fa-check"></i> Multi-step research synthesis & BibTeX generator</li>
              </ul>
            </div>
            <div class="server-card-bottom">
              <span class="badge badge-status">Protocol: 2025-11-25</span>
              <button class="btn btn-secondary btn-sm inspect-payload-btn" data-server="ipa">
                <i class="fa-solid fa-terminal"></i> Inspect Payload
              </button>
            </div>
          </div>

          <!-- 5. VRGC -->
          <div class="server-card glass-card" data-category="robotics">
            <div class="server-card-top">
              <div class="server-card-header">
                <div class="server-id-block">
                  <div class="server-icon icon-vrgc"><i class="fa-solid fa-robot"></i></div>
                  <div class="server-name-block">
                    <h3>vrgc</h3>
                    <span class="server-canonical">vrgc/server_enhanced.py</span>
                  </div>
                </div>
                <span class="badge badge-tools">28 Tools</span>
              </div>
              <p class="server-desc">
                Virtually Robotic GitHub Copilot — Software Application Programming Robot (SAPR) edition. Autonomous system diagnostics, hardware profiling, self-healing code repair, and sandbox candidate testing.
              </p>
              <ul class="server-features">
                <li><i class="fa-solid fa-check"></i> Autonomous system & hardware diagnostics</li>
                <li><i class="fa-solid fa-check"></i> Self-healing code remediation sandbox</li>
                <li><i class="fa-solid fa-check"></i> Sacred Covenant compliance verification</li>
              </ul>
            </div>
            <div class="server-card-bottom">
              <span class="badge badge-status">Protocol: 2025-11-25</span>
              <button class="btn btn-secondary btn-sm inspect-payload-btn" data-server="vrgc">
                <i class="fa-solid fa-terminal"></i> Inspect Payload
              </button>
            </div>
          </div>

          <!-- 6. DPA -->
          <div class="server-card glass-card" data-category="code">
            <div class="server-card-top">
              <div class="server-card-header">
                <div class="server-id-block">
                  <div class="server-icon icon-dpa"><i class="fa-solid fa-brain"></i></div>
                  <div class="server-name-block">
                    <h3>dpa</h3>
                    <span class="server-canonical">dpa/server.py</span>
                  </div>
                </div>
                <span class="badge badge-tools">17 Tools</span>
              </div>
              <p class="server-desc">
                Digital Project Assistant. Natural language understanding (NLU) engine, WCAG AA accessibility compliance verification, task scheduling, chronology tracking, and context retention lattice.
              </p>
              <ul class="server-features">
                <li><i class="fa-solid fa-check"></i> High-accuracy natural language intent extraction</li>
                <li><i class="fa-solid fa-check"></i> WCAG AA accessibility compliance audits</li>
                <li><i class="fa-solid fa-check"></i> Chronological task scheduling & context retention</li>
              </ul>
            </div>
            <div class="server-card-bottom">
              <span class="badge badge-status">Protocol: 2025-11-25</span>
              <button class="btn btn-secondary btn-sm inspect-payload-btn" data-server="dpa">
                <i class="fa-solid fa-terminal"></i> Inspect Payload
              </button>
            </div>
          </div>

          <!-- 7. WEB-SEARCH -->
          <div class="server-card glass-card" data-category="research">
            <div class="server-card-top">
              <div class="server-card-header">
                <div class="server-id-block">
                  <div class="server-icon icon-web"><i class="fa-solid fa-globe"></i></div>
                  <div class="server-name-block">
                    <h3>web-search</h3>
                    <span class="server-canonical">web-search/server.py</span>
                  </div>
                </div>
                <span class="badge badge-tools">8 Tools</span>
              </div>
              <p class="server-desc">
                High-Throughput Search Broker. Resilient multi-engine web search with automatic Google and DuckDuckGo fallback cascades, clean markdown webpage extraction, and link validation.
              </p>
              <ul class="server-features">
                <li><i class="fa-solid fa-check"></i> Dual Google & DuckDuckGo fallback cascades</li>
                <li><i class="fa-solid fa-check"></i> Zero-cost web scraping & markdown distillation</li>
                <li><i class="fa-solid fa-check"></i> Automated query suggestions & operator expansion</li>
              </ul>
            </div>
            <div class="server-card-bottom">
              <span class="badge badge-status">Protocol: 2025-11-25</span>
              <button class="btn btn-secondary btn-sm inspect-payload-btn" data-server="websearch">
                <i class="fa-solid fa-terminal"></i> Inspect Payload
              </button>
            </div>
          </div>

          <!-- 8. LOC -->
          <div class="server-card glass-card" data-category="research">
            <div class="server-card-top">
              <div class="server-card-header">
                <div class="server-id-block">
                  <div class="server-icon icon-loc"><i class="fa-solid fa-landmark"></i></div>
                  <div class="server-name-block">
                    <h3>loc</h3>
                    <span class="server-canonical">loc/server.py</span>
                  </div>
                </div>
                <span class="badge badge-tools">4 Tools</span>
              </div>
              <p class="server-desc">
                Library of Congress Research Server. Real-time querying of the official LoC catalog (29,000+ computer science items), Chronicling America historical newspapers, and congressional legislative archives.
              </p>
              <ul class="server-features">
                <li><i class="fa-solid fa-check"></i> Official Library of Congress catalog search</li>
                <li><i class="fa-solid fa-check"></i> Chronicling America historic newspaper archives</li>
                <li><i class="fa-solid fa-check"></i> Congressional legislative & public domain records</li>
              </ul>
            </div>
            <div class="server-card-bottom">
              <span class="badge badge-status">Protocol: 2025-11-25</span>
              <button class="btn btn-secondary btn-sm inspect-payload-btn" data-server="loc">
                <i class="fa-solid fa-terminal"></i> Inspect Payload
              </button>
            </div>
          </div>

        </div>
      </div>
    </section>

    <!-- ==========================================================================
         Section 4: Constitutional Governance (Sacred Covenant)
         ========================================================================== -->
    <section class="section" id="governance">
      <div class="container">
        <div class="section-header">
          <span class="section-pretitle">Ethical & Operational Safety</span>
          <h2 class="section-title">The Constitutional Governance Layer</h2>
          <p class="section-description">
            Unlike standard MCP servers that execute untrusted tools with unconstrained shell permissions, the <code>.mcp</code> fleet is bound by Kirk LaSalle's <strong>Agentic Sacred Covenant</strong> and <strong>10 Laws</strong>.
          </p>
        </div>

        <div class="governance-layout">
          <!-- 10 Laws Interactive Selector -->
          <div class="laws-grid">
            <div class="law-item active">
              <div class="law-title-row">
                <span class="law-title">Law 1: Human Preservation & Non-Harm</span>
                <span class="badge badge-status" style="font-size: 0.7rem;">Paramount</span>
              </div>
              <p class="law-content">An intelligence system may not intend or commit physical, psychological, or manipulative harm, nor allow harm through inaction.</p>
            </div>
            <div class="law-item">
              <div class="law-title-row">
                <span class="law-title">Law 2 & 10: Human Consent & Operational Boundaries</span>
                <span class="badge badge-protocol" style="font-size: 0.7rem;">Enforced</span>
              </div>
              <p class="law-content">Tools that modify files, mutate system state, or spawn sub-agents require explicit, cryptographically verifiable operator authorization.</p>
            </div>
            <div class="law-item">
              <div class="law-title-row">
                <span class="law-title">Law 6: Data Integrity & Lawful Ownership</span>
                <span class="badge badge-tools" style="font-size: 0.7rem;">Privacy</span>
              </div>
              <p class="law-content">Protects user privacy and data ownership. Zero unauthorized exfiltration, scraping bounded by licensing and robots.txt.</p>
            </div>
            <div class="law-item">
              <div class="law-title-row">
                <span class="law-title">Law 7: Absolute Truthfulness & Zero Hallucination</span>
                <span class="badge badge-status" style="font-size: 0.7rem;">Integrity</span>
              </div>
              <p class="law-content">Tools must never return fake or mocked success data. Failed executions strictly mandate <code>isError: true</code> response envelopes.</p>
            </div>
            <div class="law-item">
              <div class="law-title-row">
                <span class="law-title">Law 9: Auditable Reasoning Ledger & Safe Fallback</span>
                <span class="badge badge-protocol" style="font-size: 0.7rem;">Auditable</span>
              </div>
              <p class="law-content">Maintains an append-only ledger of decision reasoning. Gracefully falls back to simple, verified foundational states when complex logic is unverified.</p>
            </div>
          </div>

          <!-- Comparison Card -->
          <div class="governance-comparison-card glass-card">
            <h3>Why Ungoverned MCP Tooling Fails</h3>
            <p style="font-size: 0.92rem; color: var(--text-secondary); margin-top: 0.5rem;">
              As autonomous agents gain autonomy, relying solely on client-side prompt instructions ("Please don't delete files") creates catastrophic security liabilities.
            </p>

            <table class="comp-table">
              <thead>
                <tr>
                  <th>Dimension</th>
                  <th>Standard MCP Market</th>
                  <th>.mcp Fleet (Kirk LaSalle)</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>File Mutation</strong></td>
                  <td style="color: #f43f5e;">Blind execution via shell</td>
                  <td style="color: var(--accent-emerald);">Explicit Operator Consent (Law 2)</td>
                </tr>
                <tr>
                  <td><strong>Tool Failures</strong></td>
                  <td style="color: #f43f5e;">Disguised as 200 OK / Mock</td>
                  <td style="color: var(--accent-emerald);">Strict <code>isError: true</code> (Law 7)</td>
                </tr>
                <tr>
                  <td><strong>Audit Ledger</strong></td>
                  <td style="color: #f43f5e;">Ephemeral client stdout</td>
                  <td style="color: var(--accent-emerald);">Append-only swarm memory (Law 9)</td>
                </tr>
                <tr>
                  <td><strong>Stdout Stream</strong></td>
                  <td style="color: #f43f5e;">Frequent pipe pollution</td>
                  <td style="color: var(--accent-emerald);">Kernel-level Stdio Guard</td>
                </tr>
                <tr>
                  <td><strong>Resource Guard</strong></td>
                  <td style="color: #f43f5e;">Crashes GPU VRAM (OOM)</td>
                  <td style="color: var(--accent-emerald);">Active 4GB VRAM Hardware Cap</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>

    <!-- ==========================================================================
         Section 5: Architecture & Stdio Purity
         ========================================================================== -->
    <section class="section" id="architecture">
      <div class="container">
        <div class="section-header">
          <span class="section-pretitle">Engineering Deep Dive</span>
          <h2 class="section-title">System Architecture & Stdio Purity</h2>
          <p class="section-description">
            Engineered with a zero-trust stdio guard that prevents library output from poisoning the JSON-RPC pipe, coupled with three flexible deployment topologies.
          </p>
        </div>

        <div class="arch-grid">
          <!-- Architecture Image Preview -->
          <div class="arch-image-card open-lightbox" data-src="assets/images/architecture_overview.jpg" title="Click to view full architecture schematic">
            <img src="assets/images/architecture_overview.jpg" alt="Advanced AI Agent Platform Architecture">
          </div>

          <!-- Topologies Description -->
          <div class="topologies-list">
            <div class="topology-box">
              <h4>1. Goliath Orchestrated Gateway (Recommended)</h4>
              <p>The client connects to a single master server (<code>goliath/server.py</code>). Goliath multiplexes 50+ tools across child bridges, coordinates swarm memory, and enforces GPU VRAM budgets under a single stdio pipe.</p>
            </div>

            <div class="topology-box">
              <h4>2. Standalone Server Mode</h4>
              <p>Launch individual micro-servers independently (e.g. running only <code>web-search</code> or <code>ids</code>). Ideal for lightweight agents or specific targeted coding workflows in Cursor.</p>
            </div>

            <div class="topology-box">
              <h4>3. Kernel-Level Stdio Guarding (<code>stdio_guard.py</code>)</h4>
              <p>The #1 cause of MCP crashes is third-party libraries printing to stdout. Stdio Guard duplicates OS file descriptor 1 at the kernel level and redirects all Python and C-level standard outputs to stderr, guaranteeing 100% JSON-RPC stream purity.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==========================================================================
         Section 6: Terminal Diagnostic Sandbox ("Printer Self-Test")
         ========================================================================== -->
    <section class="section" id="demo">
      <div class="container">
        <div class="section-header">
          <span class="section-pretitle">Live Verification Suite</span>
          <h2 class="section-title">Master Calibration & Fleet Self-Test Demo</h2>
          <p class="section-description">
            Much like an enterprise printer running a hardware calibration cycle and printing a diagnostic sheet, you can run an automated end-to-end self-test across all 8 micro-servers simultaneously.
          </p>
        </div>

        <div class="terminal-wrapper">
          <div class="terminal-header">
            <div class="terminal-dots">
              <div class="terminal-dot dot-red"></div>
              <div class="terminal-dot dot-yellow"></div>
              <div class="terminal-dot dot-green"></div>
            </div>
            <span style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-muted);">
              fleet-diagnostic-terminal — bash — 80x24
            </span>
            <button class="btn btn-secondary btn-sm" id="copy-master-prompt-btn" style="padding: 0.25rem 0.75rem; font-size: 0.75rem;">
              <i class="fa-regular fa-copy"></i> Copy Master Prompt
            </button>
          </div>

          <!-- Server Tabs -->
          <div class="terminal-tabs">
            <button class="terminal-tab-btn active" data-server="goliath">goliath</button>
            <button class="terminal-tab-btn" data-server="ids">ids</button>
            <button class="terminal-tab-btn" data-server="eds">eds</button>
            <button class="terminal-tab-btn" data-server="ipa">ipa</button>
            <button class="terminal-tab-btn" data-server="vrgc">vrgc</button>
            <button class="terminal-tab-btn" data-server="dpa">dpa</button>
            <button class="terminal-tab-btn" data-server="websearch">web-search</button>
            <button class="terminal-tab-btn" data-server="loc">loc</button>
          </div>

          <div class="terminal-body" id="terminal-screen">
            <div class="terminal-command" id="terminal-command">$ python -m goliath.server --call goliath_get_swarm_state</div>
            <div class="terminal-output" id="terminal-output">[GOLIATH MULTIPLEXER] Connected to Stdio Bridge (JSON-RPC 2.0)
[TELEMETRY] Querying Swarm Blackboard State & Hardware Budget...
{
  "status": "OK",
  "server": "goliath",
  "protocol": "2025-11-25",
  "tools_registered": 50,
  "memory": {
    "active_context": [],
    "finding_count": 0,
    "dna_count": 0,
    "last_updated": "2026-10-23T16:30:08.698109"
  },
  "hardware": {
    "vram_usage_gb": 0.5488,
    "target_limit_gb": 4.0,
    "status": "Optimal (13.7% of 4GB ceiling)"
  }
}
[VERDICT] Goliath Gateway & Swarm Blackboard 100% Operational.</div>
          </div>

          <div style="background: #090e1d; padding: 1rem 1.5rem; display: flex; align-items: center; justify-content: space-between; border-top: 1px solid var(--border-subtle);">
            <span style="font-size: 0.82rem; color: var(--text-muted); font-family: var(--font-mono);">
              Probe Suite: <code>tests/probe_v2.py</code> | Result: <strong>8/8 OK</strong>
            </span>
            <button class="btn btn-emerald btn-sm" id="run-all-tests-btn">
              <i class="fa-solid fa-play"></i> Run Fleet Calibration Cycle
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- ==========================================================================
         Section 7: 1-Click Client Integrations
         ========================================================================== -->
    <section class="section" id="setup">
      <div class="container">
        <div class="section-header">
          <span class="section-pretitle">Instant Developer Onboarding</span>
          <h2 class="section-title">1-Click Client Configurations</h2>
          <p class="section-description">
            Drop these pre-validated configurations directly into your client environment to instantly expose the entire fleet to your agent.
          </p>
        </div>

        <div class="setup-container">
          <div class="setup-tabs">
            <button class="setup-tab-btn active" data-client="claude">
              <i class="fa-solid fa-desktop"></i> Anthropic Claude Desktop
            </button>
            <button class="setup-tab-btn" data-client="antigravity">
              <i class="fa-solid fa-wand-magic-sparkles"></i> Google Antigravity IDE
            </button>
            <button class="setup-tab-btn" data-client="cursor">
              <i class="fa-solid fa-code"></i> Cursor / Windsurf
            </button>
            <button class="setup-tab-btn" data-client="nexus">
              <i class="fa-solid fa-paper-plane"></i> Nexus Orchestrator
            </button>
          </div>

          <div class="code-box-wrapper">
            <div class="code-box-header">
              <span id="setup-target-label">Target: %APPDATA%\Claude\claude_desktop_config.json</span>
              <button class="copy-btn" id="copy-config-btn">
                <i class="fa-regular fa-copy"></i> Copy Configuration
              </button>
            </div>
            <pre class="code-box-content" id="setup-code-content">{
  "mcpServers": {
    "goliath": {
      "command": "python",
      "args": ["D:\\Projects\\.mcp\\goliath\\server.py"],
      "cwd": "D:\\Projects\\.mcp\\goliath",
      "env": {
        "GOLIATH_DEBUG": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1"
      }
    },
    "web-search": {
      "command": "python",
      "args": ["D:\\Projects\\.mcp\\web-search\\server.py"],
      "cwd": "D:\\Projects\\.mcp\\web-search"
    },
    "ids": {
      "command": "python",
      "args": ["D:\\Projects\\.mcp\\ids\\server_ai_enhanced.py"],
      "cwd": "D:\\Projects\\.mcp\\ids"
    }
  }
}</pre>
          </div>
        </div>
      </div>
    </section>

    <!-- ==========================================================================
         Section 8: Competitive Radar & Market Standing
         ========================================================================== -->
    <section class="section" id="market">
      <div class="container">
        <div class="section-header">
          <span class="section-pretitle">Strategic Market Intelligence</span>
          <h2 class="section-title">Where .mcp Stands Compared to the World</h2>
          <p class="section-description">
            Benchmarking Kirk LaSalle's <code>.mcp</code> fleet against the global 2026 Model Context Protocol landscape, container sandboxes, and commercial AI search engines.
          </p>
        </div>

        <div class="radar-grid">
          <!-- Chart.js Radar Card -->
          <div class="radar-chart-card glass-card">
            <canvas id="radarChart"></canvas>
          </div>

          <!-- The 5 Strategic Moats -->
          <div class="moats-list">
            <div class="moat-card">
              <h4><i class="fa-solid fa-shield-halved"></i> Moat 1: Constitutional Governance at Dispatch</h4>
              <p>Tools are legally bound by the Agentic Sacred Covenant. Mutations mandate operator approval; failure reporting strictly enforces <code>isError: true</code>.</p>
            </div>
            <div class="moat-card">
              <h4><i class="fa-solid fa-cubes"></i> Moat 2: Goliath Swarm Memory Multiplexer</h4>
              <p>Single-endpoint aggregation of 50+ tools with shared blackboard state (<code>goliath_swarm_memory.json</code>) and a 4GB GPU VRAM allocation guard.</p>
            </div>
            <div class="moat-card">
              <h4><i class="fa-solid fa-coins"></i> Moat 3: Zero-Marginal-Cost Academic Intelligence</h4>
              <p>Direct ethical crawling of arXiv, Library of Congress, and MIT OpenCourseWare without expensive recurring SaaS API billing (Exa/Tavily).</p>
            </div>
            <div class="moat-card">
              <h4><i class="fa-solid fa-wrench"></i> Moat 4: Autonomous Robotic Code Healing</h4>
              <p>VRGC SAPR software robotics analyzes dependencies, evaluates hardware metrics, and repairs code in sandboxes before committing.</p>
            </div>
            <div class="moat-card">
              <h4><i class="fa-solid fa-filter"></i> Moat 5: Kernel-Level Stdio Stream Isolation</h4>
              <p>File descriptor 1 duplication eliminates the #1 bug crashing MCP clients worldwide (unbuffered library stdout logs corrupting JSON-RPC).</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==========================================================================
         Section 9: Commercial Model & Roadmap
         ========================================================================== -->
    <section class="section" id="pricing">
      <div class="container">
        <div class="section-header">
          <span class="section-pretitle">Commercialization & Execution</span>
          <h2 class="section-title">Enterprise Commercial Model & Roadmap</h2>
          <p class="section-description">
            Positioned as the open-core standard for autonomous agent tooling with dedicated commercial governance tiers for high-assurance enterprises.
          </p>
        </div>

        <div class="pricing-grid">
          <!-- Tier 1 -->
          <div class="pricing-card glass-card">
            <div class="pricing-header">
              <span class="pricing-tier">Open Source Foundation</span>
              <div class="pricing-price">$0 <span>/ forever</span></div>
              <p style="font-size: 0.88rem; color: var(--text-secondary);">For individual developers and researchers.</p>
            </div>
            <ul class="pricing-features">
              <li><i class="fa-solid fa-check"></i> All 8 core micro-servers</li>
              <li><i class="fa-solid fa-check"></i> Goliath master orchestrator</li>
              <li><i class="fa-solid fa-check"></i> Local swarm memory blackboard</li>
              <li><i class="fa-solid fa-check"></i> Kernel-level Stdio Guard</li>
              <li><i class="fa-solid fa-check"></i> 1-Click client config templates</li>
            </ul>
            <a href="https://github.com/kirklasalle/.mcp" target="_blank" rel="noopener" class="btn btn-secondary">
              Clone from GitHub
            </a>
          </div>

          <!-- Tier 2 -->
          <div class="pricing-card glass-card featured">
            <div class="pricing-header">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span class="pricing-tier" style="color: var(--accent-indigo);">Solo Developer Pro</span>
                <span class="badge badge-protocol" style="font-size: 0.68rem;">POPULAR</span>
              </div>
              <div class="pricing-price">$19 <span>/ month</span></div>
              <p style="font-size: 0.88rem; color: var(--text-secondary);">For power developers requiring cloud relays and OCR.</p>
            </div>
            <ul class="pricing-features">
              <li><i class="fa-solid fa-check"></i> Everything in Open Source</li>
              <li><i class="fa-solid fa-check"></i> Pre-compiled GPU Docker containers</li>
              <li><i class="fa-solid fa-check"></i> High-speed cloud search proxy relays</li>
              <li><i class="fa-solid fa-check"></i> Multi-modal PDF OCR & video parsing</li>
              <li><i class="fa-solid fa-check"></i> Priority Smithery.ai registry updates</li>
            </ul>
            <a href="#setup" class="btn btn-primary">
              Get Pro Access
            </a>
          </div>

          <!-- Tier 3 -->
          <div class="pricing-card glass-card">
            <div class="pricing-header">
              <span class="pricing-tier">Enterprise Governance</span>
              <div class="pricing-price">$49 <span>/ seat/mo</span></div>
              <p style="font-size: 0.88rem; color: var(--text-secondary);">For regulated industries (Defense, Health, Finance).</p>
            </div>
            <ul class="pricing-features">
              <li><i class="fa-solid fa-check"></i> Everything in Solo Pro</li>
              <li><i class="fa-solid fa-check"></i> Centralized Sacred Covenant policy server</li>
              <li><i class="fa-solid fa-check"></i> Cryptographically signed audit ledgers</li>
              <li><i class="fa-solid fa-check"></i> Cross-workstation team memory sync</li>
              <li><i class="fa-solid fa-check"></i> SOC 2 & ISO 42001 compliance export</li>
            </ul>
            <a href="mailto:kirk@.nexus" class="btn btn-secondary">
              Contact Governance
            </a>
          </div>
        </div>
      </div>
    </section>

    <!-- ==========================================================================
         Section 10: FAQ Accordion
         ========================================================================== -->
    <section class="section" id="faq">
      <div class="container">
        <div class="section-header">
          <span class="section-pretitle">Frequently Asked Questions</span>
          <h2 class="section-title">Developer Intelligence FAQ</h2>
        </div>

        <div class="faq-accordion">
          <div class="faq-item">
            <div class="faq-question">
              <span>What is the Model Context Protocol (MCP) Standard 2025-11-25?</span>
              <i class="fa-solid fa-chevron-down faq-icon"></i>
            </div>
            <div class="faq-answer">
              The Model Context Protocol (MCP) is the open JSON-RPC 2.0 standard created by Anthropic to bridge AI host clients (Claude, Antigravity, Cursor) with external tools. The 2025-11-25 specification establishes strict capability negotiation, date-versioned protocol handshakes, and standardized tool call envelopes.
            </div>
          </div>

          <div class="faq-item">
            <div class="faq-question">
              <span>Why should I use Goliath instead of connecting to 8 separate servers?</span>
              <i class="fa-solid fa-chevron-down faq-icon"></i>
            </div>
            <div class="faq-answer">
              Connecting to 8 separate servers forces your client to manage 8 subprocesses, 8 stdio pipes, and isolates context. Goliath multiplexes all 7 child servers into a single endpoint (50+ registered tools) and introduces a unified swarm blackboard memory, allowing findings from one tool to immediately inform another.
            </div>
          </div>

          <div class="faq-item">
            <div class="faq-question">
              <span>How does `stdio_guard.py` prevent client crashes?</span>
              <i class="fa-solid fa-chevron-down faq-icon"></i>
            </div>
            <div class="faq-answer">
              When Python packages (like PyTorch, HuggingFace, or requests) print banners, progress bars, or warnings to standard out, the host's JSON-RPC parser crashes with a syntax error. Stdio Guard duplicates OS file descriptor 1 at the kernel level and redirects Python/C-level stdout to stderr, ensuring only valid JSON-RPC frames ever travel on stdout.
            </div>
          </div>

          <div class="faq-item">
            <div class="faq-question">
              <span>What is the Agentic Sacred Covenant?</span>
              <i class="fa-solid fa-chevron-down faq-icon"></i>
            </div>
            <div class="faq-answer">
              The Agentic Sacred Covenant is Kirk LaSalle's 10-Law constitutional governance framework. Embedded directly into tool dispatch, it enforces non-destructive operation, human consent for file mutations, absolute truthfulness (strict isError: true), and append-only decision ledgers.
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>

  <!-- ==========================================================================
       Global Footer
       ========================================================================== -->
  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <div class="brand-logo">
            <div class="brand-icon"><i class="fa-solid fa-network-wired"></i></div>
            <span>.mcp Fleet</span>
          </div>
          <p style="font-size: 0.88rem; color: var(--text-muted); line-height: 1.6;">
            The Governance-Native Model Context Protocol Enterprise Tooling Fleet.<br>
            Sovereign Operator: <strong>Kirk LaSalle</strong> (<code>kirk@.nexus</code>).
          </p>
          <div class="badge badge-protocol" style="width: fit-content;">
            Protocol Version: 2025-11-25
          </div>
        </div>

        <div>
          <h4 style="font-size: 0.95rem; margin-bottom: 1rem; color: #ffffff;">Fleet Micro-Servers</h4>
          <ul class="footer-links">
            <li><a href="#fleet">goliath (Gateway & Memory)</a></li>
            <li><a href="#fleet">ids (GraphRAG & AST)</a></li>
            <li><a href="#fleet">eds (Educational Scraper)</a></li>
            <li><a href="#fleet">ipa (Research Assistant)</a></li>
            <li><a href="#fleet">vrgc (Robotic Repair)</a></li>
          </ul>
        </div>

        <div>
          <h4 style="font-size: 0.95rem; margin-bottom: 1rem; color: #ffffff;">Documentation</h4>
          <ul class="footer-links">
            <li><a href="https://github.com/kirklasalle/.mcp/blob/main/docs/PRD.md" target="_blank">Product Requirements (PRD)</a></li>
            <li><a href="https://github.com/kirklasalle/.mcp/blob/main/docs/USER_GUIDE.md" target="_blank">User Setup Guide</a></li>
            <li><a href="https://github.com/kirklasalle/.mcp/blob/main/docs/DEVELOPER_GUIDE.md" target="_blank">Developer Manual</a></li>
            <li><a href="https://github.com/kirklasalle/.mcp/blob/main/docs/MARKET_RESEARCH.md" target="_blank">Global Market Research</a></li>
            <li><a href="https://github.com/kirklasalle/.mcp/blob/main/AGENTIC_SACRED_COVENANT.md" target="_blank">Sacred Covenant (10 Laws)</a></li>
          </ul>
        </div>

        <div>
          <h4 style="font-size: 0.95rem; margin-bottom: 1rem; color: #ffffff;">Connect & Source</h4>
          <ul class="footer-links">
            <li><a href="https://github.com/kirklasalle/.mcp" target="_blank"><i class="fa-brands fa-github"></i> GitHub Repository</a></li>
            <li><a href="mailto:kirk@.nexus"><i class="fa-solid fa-envelope"></i> kirk@.nexus</a></li>
            <li><a href="#demo"><i class="fa-solid fa-terminal"></i> Terminal Sandbox</a></li>
            <li><a href="#setup"><i class="fa-solid fa-plug"></i> 1-Click Client Setup</a></li>
          </ul>
        </div>
      </div>

      <div class="footer-bottom">
        <div>
          &copy; 2026 Kirk LaSalle. Governed under the Agentic Sacred Covenant and Permanent Active Directives.
        </div>
        <div style="display: flex; gap: 1.5rem;">
          <span>Model Context Protocol 2025-11-25</span>
          <span>Phase 0 Verified</span>
          <span>100% Stdio Stream Safe</span>
        </div>
      </div>
    </div>
  </footer>

  <!-- ==========================================================================
       Modals: Payload Inspector & Lightbox
       ========================================================================== -->
  <div class="modal-overlay" id="payload-modal">
    <div class="modal-content">
      <div class="modal-header">
        <h4 id="modal-payload-title" style="font-family: var(--font-mono); font-size: 0.95rem; color: var(--accent-cyan);">
          Verified Server Payload
        </h4>
        <button class="modal-close-btn">&times;</button>
      </div>
      <pre class="modal-body" id="modal-payload-code"></pre>
    </div>
  </div>

  <div class="modal-overlay" id="lightbox-modal">
    <div class="modal-content lightbox-content">
      <img id="lightbox-img" src="" alt="Full Resolution Architecture Diagram">
      <div style="margin-top: 1rem;">
        <button class="btn btn-secondary btn-sm modal-close-btn">
          <i class="fa-solid fa-xmark"></i> Close Preview
        </button>
      </div>
    </div>
  </div>

  <!-- Main JavaScript Logic -->
  <script src="app.js"></script>
</body>
</html>
"""

(DEST / "index.html").write_text(HTML, encoding="utf-8")
print(f"index.html created successfully ({len(HTML)} bytes)")
