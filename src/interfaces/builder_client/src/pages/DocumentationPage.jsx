import React, { useState, useEffect } from 'react';
import { BookOpen, Search, ExternalLink, FileText, Code, Lightbulb, Bookmark, AlertCircle } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Badge } from '../components/ui';
import { getDocsCatalog } from '../lib/api';
import { cn } from '../lib/utils';

const ICON_MAP = { FileText, Code, Lightbulb };
const LOCAL_WIKI_HOST = (typeof window !== 'undefined' && window.location?.hostname && window.location.hostname !== '0.0.0.0')
    ? window.location.hostname
    : '127.0.0.1';
const LOCAL_WIKI_BASE = `http://${LOCAL_WIKI_HOST}:8080`;
const LOCAL_WIKI_URL = `${LOCAL_WIKI_BASE}/index.html`;
const LOCAL_WIKI_SEARCH_URL = `${LOCAL_WIKI_BASE}/search.html`;
const WIKI_DEEP_LINKS = [
    { label: 'Architecture', href: `${LOCAL_WIKI_BASE}/architecture/index.html` },
    { label: 'Training', href: `${LOCAL_WIKI_BASE}/training/index.html` },
    { label: 'User Guides', href: `${LOCAL_WIKI_BASE}/user-guides/index.html` },
    { label: 'API Reference', href: `${LOCAL_WIKI_BASE}/api-reference/index.html` },
    { label: 'Optimization', href: `${LOCAL_WIKI_BASE}/memory-optimization/index.html` },
    { label: 'Security', href: `${LOCAL_WIKI_BASE}/security/index.html` },
];

const WIKI_FILE_ROUTE_MAP = {
    'user_guide.md': 'user-guides/impressioncore-user-guide-updated-2025-04-22.html',
    'cli_build_walkthrough.md': 'user-guides/impressioncore-b1-cli-build-walkthrough.html',
    'GPU_SETUP.md': 'memory-optimization/gpu-setup-guide.html',
    'walkthrough.md': 'user-guides/walkthrough-system-refinement-sensor-fusion.html',
    'user_guide_tools.md': 'user-guides/impressioncore-tools-user-guide.html',
    'ARCHITECTURE.md': 'architecture/impressioncore-architecture.html',
    'B3_ARCHITECTURE_COMPREHENSIVE_DOCUMENTATION.md': 'b-series/impressioncore-b3-architecture---comprehensive-documentation.html',
    'MEMORY_EFFICIENT_ATTENTION.md': 'memory-optimization/memory-efficient-attention-and-128k-context-windows.html',
    'memory_optimization_strategies.md': 'memory-optimization/memory-optimization-strategies-for-impressioncore.html',
    'gpu-optimization.md': 'memory-optimization/gpu-optimization-strategy-for-impressioncore.html',
    'B2_NEXT_GENERATION_MULTIMODAL_ARCHITECTURE_DESIGN.md': 'b-series/impressioncore-b2---next-generation-multimodal-ai-architecture.html',
    'training-pipeline.md': 'uncategorized/training-pipeline.html',
    'DATA_PREPARATION_WORKFLOW.md': 'data-tokenization/data-preparation-workflow.html',
    'tokenization_guide.md': 'data-tokenization/impressioncore-tokenization-guide.html',
    'foundation_curriculum.md': 'training/foundation-curriculum-the-empathic-reasoner.html',
    'B1_KNOWLEDGE_DISTILLATION_COMPLETE_PIPELINE_DOCUMENTATION.md': 'training/impressioncore-b1-knowledge-distillation-pipeline---complete-development.html',
    'bulletproof_training_system_documentation.md': 'uncategorized/impressioncore-b1-bulletproof-training-system-documentation.html',
    'B2_REVOLUTIONARY_4PHASE_TRAINING_METHODOLOGY.md': 'training/impressioncore-b2-revolutionary-4-phase-training-methodology.html',
    'DEPLOYMENT_SUMMARY.md': 'deployment/deployment-summary.html',
    'api_reference.md': 'api-reference/impressioncore-api-reference.html',
    'inference_api.md': 'uncategorized/1-inference-pipeline-overview.html',
    'CHECKPOINT_MANAGEMENT.md': 'uncategorized/checkpoint-management-in-impressioncore.html',
    'UKS_UNIFIED_KNOWLEDGE_STORE.md': 'uncategorized/uks-unified-knowledge-store.html',
    'RULE_ENGINE_API.md': 'uncategorized/rule-engine-api-guide.html',
    'security.md': 'security/security-in-impressioncore.html',
    'AI_Ethics_Review_Board_Charter.md': 'constitutional/ai-ethics-review-board-aerb-charter.html',
    'prd.md': 'uncategorized/product-requirements-document-prd.html',
    'development_roadmap.md': 'uncategorized/impressioncore-b1-development-roadmap.html',
    'TROUBLESHOOTING.md': 'troubleshooting/impressioncore-troubleshooting-guide.html',
    'error_codes_registry.md': 'uncategorized/error-codes-registry-1.html',
    'CHANGELOG.md': 'uncategorized/changelog.html',
    'api_contracts.md': 'api-reference/api-contracts-for-impressioncore.html',
};

function normalizeWikiUrl(value) {
    if (!value) return null;
    if (/^https?:\/\//i.test(value)) return value;
    const route = String(value).replace(/^\//, '');
    return `${LOCAL_WIKI_BASE}/${route}`;
}

function getWikiRouteLabel(item) {
    const preferredRoute = item?.wikiUrl
        || item?.wiki_url
        || item?.wiki_path
        || item?.wikiPath
        || WIKI_FILE_ROUTE_MAP[item?.file];

    if (preferredRoute) {
        if (/^https?:\/\//i.test(preferredRoute)) {
            try {
                return new URL(preferredRoute).pathname.replace(/^\//, '') || 'index.html';
            } catch {
                return preferredRoute;
            }
        }
        return String(preferredRoute).replace(/^\//, '');
    }

    if (item?.title || item?.file) {
        const searchQuery = encodeURIComponent(item.title || item.file);
        return `search.html?q=${searchQuery}`;
    }

    return 'index.html';
}

function resolveWikiDocUrl(item) {
    const preferredUrl = normalizeWikiUrl(
        item?.wikiUrl || item?.wiki_url || item?.wiki_path || item?.wikiPath
    );
    if (preferredUrl) return preferredUrl;

    const mappedUrl = normalizeWikiUrl(WIKI_FILE_ROUTE_MAP[item?.file]);
    if (mappedUrl) return mappedUrl;

    if (item?.title || item?.file) {
        const searchQuery = encodeURIComponent(item.title || item.file);
        return `${LOCAL_WIKI_SEARCH_URL}?q=${searchQuery}`;
    }

    return LOCAL_WIKI_URL;
}

/* ── Fallback catalog shown instantly while server loads ──────── */
const FALLBACK_DOCS = [
    {
        category: 'Getting Started',
        items: [
            { title: 'User Guide', desc: 'Complete user guide covering system requirements, setup, and usage for ImpressionCore as a privacy-first digital twin AI.', file: 'user_guide.md', path: 'docs/user_guide.md', icon: 'FileText', tags: ['guide', 'setup', 'overview'], exists: true },
            { title: 'CLI Build Walkthrough', desc: 'Step-by-step CLI walkthrough with mermaid flowcharts \u2014 from documentation review and hardware checks through training and deployment.', file: 'cli_build_walkthrough.md', path: 'docs/cli_build_walkthrough.md', icon: 'Code', tags: ['cli', 'walkthrough', 'tutorial'], exists: true },
            { title: 'GPU Setup Guide', desc: 'Hardware compatibility guide for NVIDIA GPUs with optimization details for legacy cards like the GTX 1050 Ti (4GB VRAM).', file: 'GPU_SETUP.md', path: 'docs/GPU_SETUP.md', icon: 'Lightbulb', tags: ['gpu', 'hardware', 'cuda'], exists: true },
            { title: 'System Walkthrough', desc: 'System refinement and sensor fusion walkthrough covering the complete model builder pipeline.', file: 'walkthrough.md', path: 'docs/walkthrough.md', icon: 'FileText', tags: ['walkthrough', 'pipeline'], exists: true },
            { title: 'Tools Reference', desc: 'Cheat sheet for all available tools including database connections, schema retrieval, MCP servers, and utility scripts.', file: 'user_guide_tools.md', path: 'docs/user_guide_tools.md', icon: 'Code', tags: ['tools', 'reference', 'mcp'], exists: true },
        ],
    },
    {
        category: 'Architecture',
        items: [
            { title: 'Architecture Overview', desc: 'System overview of the brain-inspired multi-modal LLM with modular components for reasoning, memory, and secure communication.', file: 'ARCHITECTURE.md', path: 'docs/ARCHITECTURE.md', icon: 'FileText', tags: ['architecture', 'system'], exists: true },
            { title: 'B3 Architecture (Comprehensive)', desc: 'Full B3 architecture documentation with IDS integration, parameter scaling analysis, transformer design, and module hierarchy.', file: 'B3_ARCHITECTURE_COMPREHENSIVE_DOCUMENTATION.md', path: 'docs/B3_ARCHITECTURE_COMPREHENSIVE_DOCUMENTATION.md', icon: 'FileText', tags: ['b3', 'architecture', 'transformer'], exists: true },
            { title: 'Memory-Efficient Attention', desc: 'Technical deep-dive into memory-efficient attention mechanisms supporting 128k context windows on consumer hardware.', file: 'MEMORY_EFFICIENT_ATTENTION.md', path: 'docs/MEMORY_EFFICIENT_ATTENTION.md', icon: 'Lightbulb', tags: ['attention', 'memory', 'optimization'], exists: true },
            { title: 'Memory Optimization Strategies', desc: 'Comprehensive strategies including chunked attention, gradient checkpointing, and mixed precision targeting GTX 1050 Ti.', file: 'memory_optimization_strategies.md', path: 'docs/memory_optimization_strategies.md', icon: 'Lightbulb', tags: ['memory', 'vram', 'optimization'], exists: true },
            { title: 'GPU Optimization', desc: 'Hardware-specific GPU optimization strategy detailing VRAM management, compute capability, and CUDA core utilization.', file: 'gpu-optimization.md', path: 'docs/gpu-optimization.md', icon: 'Code', tags: ['gpu', 'cuda', 'performance'], exists: true },
            { title: 'Multimodal Pipeline Design', desc: 'Next-generation multimodal architecture design for text, vision, and audio processing pathways.', file: 'B2_NEXT_GENERATION_MULTIMODAL_ARCHITECTURE_DESIGN.md', path: 'docs/B2_NEXT_GENERATION_MULTIMODAL_ARCHITECTURE_DESIGN.md', icon: 'FileText', tags: ['multimodal', 'vision', 'audio'], exists: true },
        ],
    },
    {
        category: 'Training',
        items: [
            { title: 'Training Pipeline', desc: 'Comprehensive training framework unifying explicit knowledge retrieval, transformer LLM, and diffusion/DiT visual generation.', file: 'training-pipeline.md', path: 'docs/training-pipeline.md', icon: 'Code', tags: ['training', 'pipeline'], exists: true },
            { title: 'Data Preparation Workflow', desc: 'End-to-end data preparation pipeline covering dataset formats, preprocessing, validation, and augmentation.', file: 'DATA_PREPARATION_WORKFLOW.md', path: 'docs/DATA_PREPARATION_WORKFLOW.md', icon: 'FileText', tags: ['data', 'preprocessing', 'pipeline'], exists: true },
            { title: 'Tokenization Guide', desc: 'Comprehensive guide to converting text and images into discrete tokens for neural network processing \u2014 BPE, WordPiece, and Patch-VQ.', file: 'tokenization_guide.md', path: 'docs/tokenization_guide.md', icon: 'FileText', tags: ['tokenizer', 'bpe', 'encoding'], exists: true },
            { title: 'Foundation Curriculum', desc: '"The Empathic Reasoner" foundation curriculum design for progressive multi-phase training with difficulty scaling.', file: 'foundation_curriculum.md', path: 'docs/foundation_curriculum.md', icon: 'Lightbulb', tags: ['curriculum', 'training', 'phases'], exists: true },
            { title: 'Knowledge Distillation Pipeline', desc: 'Complete B1 teacher-student knowledge distillation pipeline with technical specs and IDS indexing.', file: 'B1_KNOWLEDGE_DISTILLATION_COMPLETE_PIPELINE_DOCUMENTATION.md', path: 'docs/B1_KNOWLEDGE_DISTILLATION_COMPLETE_PIPELINE_DOCUMENTATION.md', icon: 'FileText', tags: ['distillation', 'compression', 'b1'], exists: true },
            { title: 'Bulletproof Training System', desc: 'Fault-tolerant training system documentation covering checkpointing, recovery, error handling, and resilience patterns.', file: 'bulletproof_training_system_documentation.md', path: 'docs/bulletproof_training_system_documentation.md', icon: 'Lightbulb', tags: ['training', 'reliability', 'checkpoints'], exists: true },
            { title: 'B2 Revolutionary 4-Phase Methodology', desc: 'The revolutionary 4-phase training methodology \u2014 pretraining, alignment, distillation, and deployment.', file: 'B2_REVOLUTIONARY_4PHASE_TRAINING_METHODOLOGY.md', path: 'docs/B2_REVOLUTIONARY_4PHASE_TRAINING_METHODOLOGY.md', icon: 'Code', tags: ['b2', 'training', 'methodology'], exists: true },
        ],
    },
    {
        category: 'Deployment',
        items: [
            { title: 'Deployment Summary', desc: 'Production deployment guide covering packaging, environment configuration, service endpoints, and monitoring.', file: 'DEPLOYMENT_SUMMARY.md', path: 'docs/DEPLOYMENT_SUMMARY.md', icon: 'Code', tags: ['deployment', 'production'], exists: true },
            { title: 'API Reference', desc: 'Detailed API reference documenting ModalEngine, UniversalKnowledgeStore, MultiModalProcessor, and all REST endpoints.', file: 'api_reference.md', path: 'docs/api_reference.md', icon: 'Code', tags: ['api', 'reference', 'endpoints'], exists: true },
            { title: 'Inference API', desc: 'Inference API for memory-efficient pipeline supporting low VRAM environments, multimodal inputs, and streaming responses.', file: 'inference_api.md', path: 'docs/inference_api.md', icon: 'Code', tags: ['inference', 'api', 'streaming'], exists: true },
            { title: 'Checkpoint Management', desc: 'Checkpoint saving, loading, and lifecycle management for training and deployment.', file: 'CHECKPOINT_MANAGEMENT.md', path: 'docs/CHECKPOINT_MANAGEMENT.md', icon: 'FileText', tags: ['checkpoints', 'storage'], exists: true },
        ],
    },
    {
        category: 'Knowledge & Safety',
        items: [
            { title: 'Unified Knowledge Store (UKS)', desc: 'System documentation for storing, retrieving, and reasoning over structured knowledge using a graph-based representation.', file: 'UKS_UNIFIED_KNOWLEDGE_STORE.md', path: 'docs/UKS_UNIFIED_KNOWLEDGE_STORE.md', icon: 'FileText', tags: ['uks', 'knowledge', 'graph'], exists: true },
            { title: 'Rule Engine API', desc: 'Rule Engine API guide covering the Context class, rule definition DSL, evaluation environment, and safety enforcement.', file: 'RULE_ENGINE_API.md', path: 'docs/RULE_ENGINE_API.md', icon: 'Code', tags: ['rules', 'safety', 'api'], exists: true },
            { title: 'Security Architecture', desc: 'Multi-layered security documentation outlining data protection, access control, encryption, and compliance measures.', file: 'security.md', path: 'docs/security.md', icon: 'Lightbulb', tags: ['security', 'privacy', 'encryption'], exists: true },
            { title: 'AI Ethics Review Board Charter', desc: 'Charter defining the AI Ethics Review Board, its principles, review processes, and governance framework.', file: 'AI_Ethics_Review_Board_Charter.md', path: 'docs/AI_Ethics_Review_Board_Charter.md', icon: 'FileText', tags: ['ethics', 'governance', 'review'], exists: true },
        ],
    },
    {
        category: 'Reference',
        items: [
            { title: 'Product Requirements (PRD)', desc: 'Product Requirements Document defining ImpressionCore as a Lifelong Digital Assistant and Personal AI ID system with full feature specifications.', file: 'prd.md', path: 'docs/prd.md', icon: 'FileText', tags: ['prd', 'requirements', 'product'], exists: true },
            { title: 'Development Roadmap', desc: 'Development roadmap tracking completed milestones (Flash Attention, KV Cache, LoRA) and upcoming phases.', file: 'development_roadmap.md', path: 'docs/development_roadmap.md', icon: 'FileText', tags: ['roadmap', 'planning', 'milestones'], exists: true },
            { title: 'Troubleshooting', desc: 'Troubleshooting guide with solutions for common issues including UKS import errors, CUDA failures, and component test problems.', file: 'TROUBLESHOOTING.md', path: 'docs/TROUBLESHOOTING.md', icon: 'Lightbulb', tags: ['debug', 'faq', 'errors'], exists: true },
            { title: 'Error Codes Registry', desc: 'Standardized error codes registry categorizing errors by type (SYS, IO, LOGIC, WEB) with descriptions and recovery steps.', file: 'error_codes_registry.md', path: 'docs/error_codes_registry.md', icon: 'Code', tags: ['errors', 'codes', 'reference'], exists: true },
            { title: 'Changelog', desc: 'Project changelog documenting all fixes, features, performance improvements, and breaking changes across releases.', file: 'CHANGELOG.md', path: 'docs/CHANGELOG.md', icon: 'FileText', tags: ['changelog', 'releases', 'history'], exists: true },
            { title: 'API Contracts', desc: 'Formal API contracts defining request/response schemas, versioning, and backward compatibility guarantees.', file: 'api_contracts.md', path: 'docs/api_contracts.md', icon: 'Code', tags: ['api', 'contracts', 'schemas'], exists: true },
        ],
    },
];

export default function DocumentationPage() {
    const [docs, setDocs] = useState(FALLBACK_DOCS);
    const [query, setQuery] = useState('');
    const [activeCategory, setActiveCategory] = useState(null);

    // Load catalog from server (with exists flags) on mount
    useEffect(() => {
        getDocsCatalog().then(({ data }) => {
            if (data.success && data.categories?.length) setDocs(data.categories);
        }).catch(() => { });
    }, []);

    const q = query.toLowerCase();
    const filtered = docs.map((cat) => ({
        ...cat,
        items: cat.items.filter((item) =>
            !q || item.title.toLowerCase().includes(q) || item.desc.toLowerCase().includes(q) || item.tags.some((t) => t.includes(q))
        ),
    })).filter((cat) => cat.items.length > 0 && (!activeCategory || cat.category === activeCategory));

    const totalDocs = docs.reduce((a, c) => a + c.items.length, 0);

    return (
        <ContentArea title="Documentation" subtitle="Browse guides, references, tutorials, and the local cyberpunk wiki.">
            <Card className="mb-6 overflow-hidden">
                <div className="flex flex-col xl:flex-row gap-4 xl:items-center xl:justify-between">
                    <div className="max-w-2xl">
                        <Badge variant="cyan" className="mb-3">Builder-synced local wiki</Badge>
                        <h2 className="text-xl font-semibold text-txt-primary">Cyberpunk documentation hub</h2>
                        <p className="text-sm text-txt-secondary mt-2">
                            Open the full local wiki for category browsing, sticky navigation, search-first discovery,
                            and the same ImpressionCore glow-and-gradient styling used across the builder client.
                        </p>
                        <div className="flex flex-wrap gap-2 mt-4">
                            <a href={LOCAL_WIKI_URL} target="_blank" rel="noopener noreferrer" className="btn-primary">
                                <BookOpen size={16} />
                                Open Local Wiki
                            </a>
                            <a href={LOCAL_WIKI_SEARCH_URL} target="_blank" rel="noopener noreferrer" className="btn-secondary">
                                <Search size={16} />
                                Search Wiki
                            </a>
                        </div>
                        <p className="text-[11px] font-mono text-txt-muted mt-3">
                            Serve locally with <code className="text-accent-cyan">.\.venv\Scripts\python.exe docs/wiki/build_wiki.py --serve</code>
                        </p>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 min-w-[260px]">
                        <div className="stat-card">
                            <div className="text-lg font-bold font-mono text-txt-primary">{totalDocs}</div>
                            <div className="text-[10px] uppercase tracking-wider text-txt-muted mt-0.5">Docs</div>
                        </div>
                        <div className="stat-card">
                            <div className="text-lg font-bold font-mono text-txt-primary">{docs.length}</div>
                            <div className="text-[10px] uppercase tracking-wider text-txt-muted mt-0.5">Categories</div>
                        </div>
                        <div className="stat-card sm:col-span-1 col-span-2">
                            <div className="text-lg font-bold font-mono text-txt-primary">Wiki</div>
                            <div className="text-[10px] uppercase tracking-wider text-txt-muted mt-0.5">Builder parity</div>
                        </div>
                    </div>
                </div>

                <div className="flex flex-wrap gap-2 mt-4">
                    {WIKI_DEEP_LINKS.map((link) => (
                        <a
                            key={link.label}
                            href={link.href}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap border border-ic-border text-txt-secondary hover:border-accent-cyan/30 hover:text-txt-primary transition-colors"
                        >
                            {link.label}
                        </a>
                    ))}
                </div>
            </Card>

            {/* Search + Filters */}
            <div className="flex flex-col sm:flex-row gap-4 mb-6">
                <div className="relative flex-1">
                    <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-txt-muted" />
                    <input
                        className="input-dark w-full pl-10"
                        placeholder="Search documentation..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                    />
                </div>
                <div className="flex gap-2 overflow-x-auto">
                    <button
                        onClick={() => setActiveCategory(null)}
                        className={cn(
                            'px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap border transition-colors',
                            !activeCategory ? 'bg-accent-cyan text-white border-accent-cyan' : 'border-ic-border text-txt-secondary hover:border-accent-cyan/30'
                        )}
                    >
                        All ({totalDocs})
                    </button>
                    {docs.map((cat) => (
                        <button
                            key={cat.category}
                            onClick={() => setActiveCategory(activeCategory === cat.category ? null : cat.category)}
                            className={cn(
                                'px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap border transition-colors',
                                activeCategory === cat.category ? 'bg-accent-cyan text-white border-accent-cyan' : 'border-ic-border text-txt-secondary hover:border-accent-cyan/30'
                            )}
                        >
                            {cat.category} ({cat.items.length})
                        </button>
                    ))}
                </div>
            </div>

            {/* Docs Grid */}
            {filtered.map((cat) => (
                <div key={cat.category} className="mb-8">
                    <h2 className="text-sm font-semibold text-txt-primary mb-3 flex items-center gap-2">
                        <Bookmark size={14} className="text-accent-cyan" />
                        {cat.category}
                    </h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                        {cat.items.map((item) => {
                            const Icon = ICON_MAP[item.icon] || FileText;
                            const docUrl = resolveWikiDocUrl(item);
                            const wikiRouteLabel = getWikiRouteLabel(item);
                            return (
                                <a key={item.title} href={docUrl} target="_blank" rel="noopener noreferrer"
                                    className="block no-underline">
                                    <Card className="group cursor-pointer hover:border-accent-cyan/40 transition-colors h-full">
                                        <div className="flex items-start gap-3">
                                            <div className="w-9 h-9 rounded-lg bg-accent-cyan/10 flex items-center justify-center shrink-0 group-hover:bg-accent-cyan/20 transition-colors">
                                                <Icon size={18} className="text-accent-cyan" />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center gap-2">
                                                    <h3 className="text-sm font-semibold text-txt-primary truncate">{item.title}</h3>
                                                    {item.exists === false && (
                                                        <AlertCircle size={12} className="text-accent-warning shrink-0" title="File not found" />
                                                    )}
                                                    <ExternalLink size={12} className="text-txt-muted opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
                                                </div>
                                                <p className="text-[11px] text-txt-muted mt-0.5 line-clamp-2">{item.desc}</p>
                                                <div className="flex flex-wrap gap-1 mt-2">
                                                    {item.tags.map((tag) => (
                                                        <Badge key={tag} variant="default">{tag}</Badge>
                                                    ))}
                                                </div>
                                                {wikiRouteLabel && (
                                                    <div className="text-[9px] font-mono text-txt-muted/60 mt-1.5 truncate">
                                                        {wikiRouteLabel}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </Card>
                                </a>
                            );
                        })}
                    </div>
                </div>
            ))}

            {filtered.length === 0 && (
                <Card className="flex items-center justify-center h-40">
                    <div className="text-center text-txt-muted">
                        <BookOpen size={32} className="mx-auto mb-2 opacity-30" />
                        <p className="text-sm">No documentation found for "{query}"</p>
                    </div>
                </Card>
            )}
        </ContentArea>
    );
}
