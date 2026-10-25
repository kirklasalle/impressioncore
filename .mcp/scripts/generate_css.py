"""Generates styles.css for D:\Projects\Websites\.mcp."""
import pathlib

DEST = pathlib.Path(r"D:\Projects\Websites\.mcp")

CSS = """/* ==========================================================================
   .mcp Enterprise Fleet - World-Class Design System & Styles
   Author: Kirk LaSalle Engineering | Protocol Standard: MCP 2025-11-25
   ========================================================================== */

:root {
  /* Color Palette - Obsidian & Cosmos Dark Mode */
  --bg-cosmos: #030712;
  --bg-base: #070d1e;
  --bg-surface: #0c152e;
  --bg-surface-elevated: #111e3f;
  --bg-card: rgba(12, 21, 46, 0.75);
  --bg-card-hover: rgba(18, 32, 68, 0.88);
  --bg-glass: rgba(255, 255, 255, 0.03);

  /* Borders & Glows */
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-bright: rgba(255, 255, 255, 0.16);
  --border-indigo: rgba(99, 102, 241, 0.35);
  --border-cyan: rgba(6, 182, 212, 0.35);
  --border-emerald: rgba(16, 185, 129, 0.35);
  --glow-indigo: 0 0 35px rgba(99, 102, 241, 0.22);
  --glow-cyan: 0 0 35px rgba(6, 182, 212, 0.22);
  --glow-emerald: 0 0 25px rgba(16, 185, 129, 0.25);

  /* Typography Colors */
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --text-heading: #ffffff;

  /* Accent Jewel Tones */
  --accent-indigo: #6366f1;
  --accent-indigo-hover: #4f46e5;
  --accent-cyan: #06b6d4;
  --accent-cyan-hover: #0891b2;
  --accent-emerald: #10b981;
  --accent-emerald-hover: #059669;
  --accent-purple: #8b5cf6;
  --accent-amber: #f59e0b;
  --accent-rose: #f43f5e;
  --accent-blue: #3b82f6;

  /* Layout & Radii */
  --radius-xs: 6px;
  --radius-sm: 10px;
  --radius-md: 16px;
  --radius-lg: 24px;
  --radius-full: 9999px;
  --container-max: 1280px;

  /* Fonts */
  --font-heading: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-body: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  /* Transitions */
  --transition-fast: 0.15s ease;
  --transition-normal: 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  --transition-smooth: 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Base & Reset */
*, *::before, *::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
  font-size: 16px;
}

body {
  background-color: var(--bg-cosmos);
  color: var(--text-primary);
  font-family: var(--font-body);
  line-height: 1.65;
  overflow-x: hidden;
  background-image: 
    radial-gradient(circle at 15% 10%, rgba(99, 102, 241, 0.12) 0%, transparent 40%),
    radial-gradient(circle at 85% 25%, rgba(6, 182, 212, 0.10) 0%, transparent 45%),
    radial-gradient(circle at 50% 65%, rgba(139, 92, 246, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 20% 90%, rgba(16, 185, 129, 0.08) 0%, transparent 40%);
  background-attachment: fixed;
  background-repeat: no-repeat;
}

/* Typography Defaults */
h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-heading);
  color: var(--text-heading);
  font-weight: 700;
  line-height: 1.2;
}

a {
  color: var(--accent-cyan);
  text-decoration: none;
  transition: color var(--transition-fast);
}

a:hover {
  color: #38bdf8;
}

code, pre {
  font-family: var(--font-mono);
}

/* Utilities */
.container {
  width: 100%;
  max-width: var(--container-max);
  margin: 0 auto;
  padding: 0 1.5rem;
}

.text-gradient {
  background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #94a3b8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.text-gradient-primary {
  background: linear-gradient(135deg, #a5b4fc 0%, #818cf8 40%, #06b6d4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.text-gradient-emerald {
  background: linear-gradient(135deg, #a7f3d0 0%, #34d399 50%, #06b6d4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Glass Card */
.glass-card {
  background: var(--bg-card);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
  transition: all var(--transition-normal);
}

.glass-card:hover {
  background: var(--bg-card-hover);
  border-color: var(--border-indigo);
  box-shadow: var(--glow-indigo), 0 16px 40px -10px rgba(0, 0, 0, 0.6);
  transform: translateY(-3px);
}

/* Badges & Pills */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0.85rem;
  font-size: 0.8rem;
  font-weight: 600;
  border-radius: var(--radius-full);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.badge-status {
  background: rgba(16, 185, 129, 0.12);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.badge-pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-emerald);
  box-shadow: 0 0 10px var(--accent-emerald);
  animation: pulse-ring 2s infinite ease-out;
}

@keyframes pulse-ring {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
  70% { transform: scale(1.1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

.badge-protocol {
  background: rgba(99, 102, 241, 0.12);
  color: #a5b4fc;
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.badge-tools {
  background: rgba(6, 182, 212, 0.12);
  color: #67e8f9;
  border: 1px solid rgba(6, 182, 212, 0.3);
  font-family: var(--font-mono);
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  padding: 0.75rem 1.6rem;
  font-family: var(--font-heading);
  font-size: 0.95rem;
  font-weight: 600;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-normal);
  border: none;
  outline: none;
  text-decoration: none;
}

.btn-primary {
  background: linear-gradient(135deg, var(--accent-indigo) 0%, #4338ca 100%);
  color: #ffffff;
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.btn-primary:hover {
  background: linear-gradient(135deg, #818cf8 0%, var(--accent-indigo) 100%);
  box-shadow: 0 6px 28px rgba(99, 102, 241, 0.55);
  transform: translateY(-2px);
  color: #ffffff;
}

.btn-secondary {
  background: var(--bg-surface);
  color: var(--text-primary);
  border: 1px solid var(--border-bright);
}

.btn-secondary:hover {
  background: var(--bg-surface-elevated);
  border-color: var(--border-cyan);
  box-shadow: 0 4px 20px rgba(6, 182, 212, 0.25);
  transform: translateY(-2px);
  color: #ffffff;
}

.btn-emerald {
  background: linear-gradient(135deg, var(--accent-emerald) 0%, #047857 100%);
  color: #ffffff;
  box-shadow: 0 4px 20px rgba(16, 185, 129, 0.35);
}

.btn-emerald:hover {
  background: linear-gradient(135deg, #34d399 0%, var(--accent-emerald) 100%);
  box-shadow: 0 6px 28px rgba(16, 185, 129, 0.55);
  transform: translateY(-2px);
}

.btn-sm {
  padding: 0.45rem 1rem;
  font-size: 0.85rem;
}

/* ==========================================================================
   Header & Navbar
   ========================================================================== */
.site-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: rgba(7, 13, 30, 0.88);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-subtle);
  transition: all var(--transition-normal);
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 4.5rem;
}

.brand-wrapper {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  font-family: var(--font-heading);
  font-size: 1.45rem;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -0.02em;
}

.brand-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-xs);
  background: linear-gradient(135deg, var(--accent-indigo) 0%, var(--accent-cyan) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 1.1rem;
  box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  list-style: none;
}

.nav-link {
  color: var(--text-secondary);
  font-size: 0.92rem;
  font-weight: 500;
  transition: color var(--transition-fast);
}

.nav-link:hover, .nav-link.active {
  color: #ffffff;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

/* ==========================================================================
   Hero Section
   ========================================================================== */
.hero-section {
  position: relative;
  padding: 5rem 0 4rem;
  overflow: hidden;
}

.hero-grid {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 3.5rem;
  align-items: center;
}

.hero-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.hero-tags {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.hero-title {
  font-size: 3.25rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1.15;
}

.hero-subtitle {
  font-size: 1.15rem;
  color: var(--text-secondary);
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-top: 0.5rem;
}

.hero-visual {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.telemetry-card {
  padding: 1.75rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-indigo);
  background: rgba(12, 21, 46, 0.85);
  box-shadow: var(--glow-indigo);
}

.telemetry-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
  padding-bottom: 0.85rem;
  border-bottom: 1px solid var(--border-subtle);
}

.telemetry-title {
  font-size: 0.95rem;
  font-family: var(--font-mono);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.telemetry-rows {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.telemetry-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.9rem;
}

.telemetry-label {
  color: var(--text-muted);
}

.telemetry-val {
  font-family: var(--font-mono);
  font-weight: 600;
}

.progress-bar-bg {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-full);
  overflow: hidden;
  margin-top: 0.4rem;
}

.progress-bar-fill {
  height: 100%;
  border-radius: var(--radius-full);
  background: linear-gradient(90deg, var(--accent-emerald) 0%, var(--accent-cyan) 60%, var(--accent-amber) 100%);
  width: 13.5%;
  transition: width 1s ease-in-out;
}

.hero-banner-thumb {
  width: 100%;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  overflow: hidden;
  cursor: pointer;
  transition: transform var(--transition-normal);
}

.hero-banner-thumb:hover {
  transform: scale(1.02);
  border-color: var(--border-cyan);
}

.hero-banner-thumb img {
  width: 100%;
  height: auto;
  display: block;
}

/* ==========================================================================
   Metrics & KPI Ribbon
   ========================================================================== */
.metrics-section {
  padding: 2.5rem 0;
  border-top: 1px solid var(--border-subtle);
  border-bottom: 1px solid var(--border-subtle);
  background: rgba(12, 21, 46, 0.4);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 1.5rem;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  text-align: center;
  padding: 1rem 0.5rem;
  border-right: 1px solid var(--border-subtle);
}

.metric-item:last-child {
  border-right: none;
}

.metric-number {
  font-family: var(--font-heading);
  font-size: 2.35rem;
  font-weight: 800;
  color: #ffffff;
  line-height: 1;
}

.metric-label {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
}

/* ==========================================================================
   Sections Common
   ========================================================================== */
.section {
  padding: 6rem 0;
  position: relative;
}

.section-header {
  text-align: center;
  max-width: 780px;
  margin: 0 auto 3.5rem;
}

.section-pretitle {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--accent-cyan);
  margin-bottom: 0.75rem;
  display: inline-block;
}

.section-title {
  font-size: 2.45rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-bottom: 1rem;
}

.section-description {
  font-size: 1.05rem;
  color: var(--text-secondary);
  line-height: 1.7;
}

/* ==========================================================================
   Fleet Showcase & Filter
   ========================================================================== */
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 2.5rem;
}

.filter-btn {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  padding: 0.5rem 1.15rem;
  border-radius: var(--radius-full);
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.filter-btn:hover {
  background: var(--bg-surface-elevated);
  color: #ffffff;
  border-color: var(--border-bright);
}

.filter-btn.active {
  background: var(--accent-indigo);
  color: #ffffff;
  border-color: var(--accent-indigo);
  box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
}

.server-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 1.75rem;
}

.server-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 1.75rem;
}

.server-card-top {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.server-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.server-id-block {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.server-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: #ffffff;
}

.icon-goliath { background: linear-gradient(135deg, #8b5cf6, #6366f1); }
.icon-ids { background: linear-gradient(135deg, #06b6d4, #3b82f6); }
.icon-eds { background: linear-gradient(135deg, #10b981, #06b6d4); }
.icon-ipa { background: linear-gradient(135deg, #f59e0b, #f97316); }
.icon-vrgc { background: linear-gradient(135deg, #f43f5e, #ec4899); }
.icon-dpa { background: linear-gradient(135deg, #3b82f6, #6366f1); }
.icon-web { background: linear-gradient(135deg, #06b6d4, #10b981); }
.icon-loc { background: linear-gradient(135deg, #8b5cf6, #ec4899); }

.server-name-block h3 {
  font-size: 1.25rem;
  font-weight: 700;
}

.server-canonical {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-muted);
}

.server-desc {
  font-size: 0.92rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.server-features {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  margin: 0.75rem 0;
}

.server-features li {
  font-size: 0.85rem;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.server-features li i {
  color: var(--accent-emerald);
  font-size: 0.75rem;
}

.server-card-bottom {
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* ==========================================================================
   Constitutional Governance Section
   ========================================================================== */
.governance-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2.5rem;
  align-items: flex-start;
}

.laws-grid {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.law-item {
  padding: 1.15rem;
  border-radius: var(--radius-sm);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  transition: all var(--transition-fast);
  cursor: pointer;
}

.law-item:hover, .law-item.active {
  background: var(--bg-surface-elevated);
  border-color: var(--border-indigo);
  transform: translateX(4px);
}

.law-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.law-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-heading);
}

.law-content {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
  line-height: 1.5;
}

.governance-comparison-card {
  padding: 2rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-bright);
}

.comp-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1.25rem;
  font-size: 0.88rem;
}

.comp-table th, .comp-table td {
  padding: 0.85rem 0.6rem;
  text-align: left;
  border-bottom: 1px solid var(--border-subtle);
}

.comp-table th {
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
}

/* ==========================================================================
   Architecture & Stdio Guard Section
   ========================================================================== */
.arch-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  align-items: center;
}

.arch-image-card {
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
  transition: transform var(--transition-normal);
}

.arch-image-card:hover {
  transform: scale(1.02);
  border-color: var(--border-cyan);
}

.arch-image-card img {
  width: 100%;
  height: auto;
  display: block;
}

.topologies-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.topology-box {
  padding: 1.25rem;
  border-radius: var(--radius-sm);
  background: var(--bg-surface);
  border-left: 4px solid var(--accent-indigo);
}

.topology-box:nth-child(2) {
  border-left-color: var(--accent-cyan);
}

.topology-box:nth-child(3) {
  border-left-color: var(--accent-emerald);
}

.topology-box h4 {
  font-size: 1.05rem;
  margin-bottom: 0.4rem;
}

.topology-box p {
  font-size: 0.88rem;
  color: var(--text-secondary);
}

/* ==========================================================================
   Terminal Diagnostic Sandbox ("Printer Self-Test")
   ========================================================================== */
.terminal-wrapper {
  max-width: 1000px;
  margin: 0 auto;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--border-indigo);
  box-shadow: var(--glow-indigo), 0 20px 40px rgba(0, 0, 0, 0.7);
  background: #060a17;
}

.terminal-header {
  background: #0b1329;
  padding: 0.85rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-subtle);
}

.terminal-dots {
  display: flex;
  gap: 6px;
}

.terminal-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.dot-red { background: #ef4444; }
.dot-yellow { background: #f59e0b; }
.dot-green { background: #10b981; }

.terminal-tabs {
  display: flex;
  gap: 0.35rem;
  overflow-x: auto;
  padding: 0.5rem 1.25rem;
  background: rgba(11, 19, 41, 0.6);
  border-bottom: 1px solid var(--border-subtle);
}

.terminal-tab-btn {
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-muted);
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-xs);
  font-family: var(--font-mono);
  font-size: 0.78rem;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.terminal-tab-btn:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
}

.terminal-tab-btn.active {
  color: var(--accent-cyan);
  background: rgba(6, 182, 212, 0.12);
  border-color: rgba(6, 182, 212, 0.3);
}

.terminal-body {
  padding: 1.5rem;
  min-height: 380px;
  max-height: 480px;
  overflow-y: auto;
  font-family: var(--font-mono);
  font-size: 0.85rem;
  line-height: 1.6;
  color: #e2e8f0;
}

.terminal-command {
  color: #38bdf8;
  margin-bottom: 1rem;
}

.terminal-output {
  white-space: pre-wrap;
  color: #cbd5e1;
}

/* ==========================================================================
   1-Click Setup Matrix
   ========================================================================== */
.setup-container {
  max-width: 960px;
  margin: 0 auto;
}

.setup-tabs {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.setup-tab-btn {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-sm);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.setup-tab-btn:hover {
  background: var(--bg-surface-elevated);
  color: #ffffff;
}

.setup-tab-btn.active {
  background: linear-gradient(135deg, var(--accent-indigo) 0%, #4338ca 100%);
  color: #ffffff;
  border-color: var(--accent-indigo);
  box-shadow: 0 4px 18px rgba(99, 102, 241, 0.35);
}

.code-box-wrapper {
  position: relative;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-bright);
  background: #090e1d;
  overflow: hidden;
}

.code-box-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 1.25rem;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid var(--border-subtle);
  font-size: 0.85rem;
  color: var(--text-muted);
}

.code-box-content {
  padding: 1.5rem;
  max-height: 400px;
  overflow-y: auto;
  font-family: var(--font-mono);
  font-size: 0.85rem;
  color: #93c5fd;
  white-space: pre-wrap;
}

.copy-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  padding: 0.35rem 0.85rem;
  border-radius: var(--radius-xs);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.copy-btn:hover {
  background: rgba(255, 255, 255, 0.16);
}

/* ==========================================================================
   Competitive Radar & Chart
   ========================================================================== */
.radar-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  align-items: center;
}

.radar-chart-card {
  padding: 1.5rem;
  border-radius: var(--radius-md);
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  height: 440px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.moats-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.moat-card {
  padding: 1.25rem;
  border-radius: var(--radius-sm);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  transition: border-color var(--transition-fast);
}

.moat-card:hover {
  border-color: var(--accent-cyan);
}

.moat-card h4 {
  font-size: 1rem;
  margin-bottom: 0.35rem;
  color: var(--accent-cyan);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.moat-card p {
  font-size: 0.86rem;
  color: var(--text-secondary);
}

/* ==========================================================================
   Commercialization & Pricing Cards
   ========================================================================== */
.pricing-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  margin-top: 2rem;
}

.pricing-card {
  padding: 2.25rem 1.75rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-radius: var(--radius-md);
  position: relative;
}

.pricing-card.featured {
  border-color: var(--accent-indigo);
  box-shadow: var(--glow-indigo);
  background: linear-gradient(180deg, rgba(99, 102, 241, 0.12) 0%, var(--bg-card) 60%);
}

.pricing-header {
  margin-bottom: 1.5rem;
}

.pricing-tier {
  font-size: 1rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}

.pricing-price {
  font-size: 2.75rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0.5rem 0;
}

.pricing-price span {
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-muted);
}

.pricing-features {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  margin: 1.5rem 0 2rem;
  font-size: 0.9rem;
}

.pricing-features li {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  color: var(--text-secondary);
}

.pricing-features li i {
  color: var(--accent-emerald);
}

/* ==========================================================================
   FAQ Section
   ========================================================================== */
.faq-accordion {
  max-width: 820px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.faq-item {
  border-radius: var(--radius-sm);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  overflow: hidden;
  transition: all var(--transition-fast);
}

.faq-question {
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  font-weight: 600;
  font-size: 1.05rem;
}

.faq-answer {
  padding: 0 1.5rem 1.25rem;
  font-size: 0.92rem;
  color: var(--text-secondary);
  line-height: 1.65;
  display: none;
}

.faq-item.open .faq-answer {
  display: block;
}

.faq-item.open .faq-icon {
  transform: rotate(180deg);
}

.faq-icon {
  transition: transform var(--transition-fast);
  color: var(--text-muted);
}

/* ==========================================================================
   Footer
   ========================================================================== */
.site-footer {
  padding: 4.5rem 0 2.5rem;
  border-top: 1px solid var(--border-subtle);
  background: rgba(3, 7, 18, 0.9);
}

.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 3rem;
  margin-bottom: 3.5rem;
}

.footer-brand {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.footer-links {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  font-size: 0.9rem;
}

.footer-links li a {
  color: var(--text-secondary);
}

.footer-links li a:hover {
  color: #ffffff;
}

.footer-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 2rem;
  border-top: 1px solid var(--border-subtle);
  font-size: 0.85rem;
  color: var(--text-muted);
}

/* ==========================================================================
   Modal (Payload Viewer & Image Lightbox)
   ========================================================================== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(3, 7, 18, 0.85);
  backdrop-filter: blur(8px);
  z-index: 2000;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.modal-overlay.active {
  display: flex;
}

.modal-content {
  width: 100%;
  max-width: 820px;
  background: #090e1d;
  border: 1px solid var(--border-bright);
  border-radius: var(--radius-md);
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.8);
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.04);
  border-bottom: 1px solid var(--border-subtle);
}

.modal-body {
  padding: 1.5rem;
  max-height: 70vh;
  overflow-y: auto;
  font-family: var(--font-mono);
  font-size: 0.85rem;
}

.modal-close-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 1.25rem;
  cursor: pointer;
}

/* Lightbox Modal Specific */
.lightbox-content {
  max-width: 90vw;
  max-height: 90vh;
  background: transparent;
  border: none;
  box-shadow: none;
  text-align: center;
}

.lightbox-content img {
  max-width: 100%;
  max-height: 85vh;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-indigo);
  box-shadow: var(--glow-indigo), 0 20px 50px rgba(0,0,0,0.8);
}

/* ==========================================================================
   Responsive Breakpoints
   ========================================================================== */
@media (max-width: 1024px) {
  .hero-grid, .arch-grid, .governance-layout, .radar-grid {
    grid-template-columns: 1fr;
  }
  .metrics-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  .metric-item:nth-child(3) {
    border-right: none;
  }
  .pricing-grid {
    grid-template-columns: 1fr;
  }
  .footer-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .nav-links, .nav-actions .btn-secondary {
    display: none;
  }
  .hero-title {
    font-size: 2.35rem;
  }
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .metric-item {
    border-right: none;
  }
  .server-grid {
    grid-template-columns: 1fr;
  }
  .footer-grid {
    grid-template-columns: 1fr;
  }
  .footer-bottom {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
}
"""

(DEST / "styles.css").write_text(CSS, encoding="utf-8")
print(f"styles.css created successfully ({len(CSS)} bytes)")
