import {
    Brain, Shield, GitBranch, Cpu, BookOpen, Beaker,
    Code2, Stethoscope, Atom, Scale, Heart,
    Eye, MessageSquare, Sparkles, Layers, Zap,
} from 'lucide-react';

// ─────────────────────────────────────────────────────────────
// KNOWLEDGE STORE — Curated Fact Packs
// ─────────────────────────────────────────────────────────────

export const KNOWLEDGE_PACKS = [
    {
        id: 'general_ai',
        name: 'General AI Knowledge',
        desc: 'Core LLM and transformer fundamentals — architecture, training, inference, and hardware context. A solid starting point for any ImpressionCore build.',
        icon: Brain,
        category: 'General',
        facts: [
            { subject: 'ImpressionCore', predicate: 'is_designed_for', object: 'consumer GPU hardware', source: 'docs/architecture.md' },
            { subject: 'ImpressionCore', predicate: 'targets', object: 'NVIDIA GTX 1050 Ti with 4GB VRAM', source: 'docs/architecture.md' },
            { subject: 'ImpressionCore', predicate: 'uses', object: 'brain-inspired multimodal architecture', source: 'docs/prd.md' },
            { subject: 'ImpressionCore', predicate: 'implements', object: 'Universal Knowledge Store (UKS)', source: 'docs/architecture.md' },
            { subject: 'Transformer', predicate: 'is_based_on', object: 'self-attention mechanism', source: 'literature' },
            { subject: 'Transformer', predicate: 'was_introduced_by', object: 'Vaswani et al. 2017 (Attention Is All You Need)', source: 'literature' },
            { subject: 'Tokenizer', predicate: 'converts', object: 'raw text to numerical token IDs', source: 'fundamentals' },
            { subject: 'BPE (Byte-Pair Encoding)', predicate: 'is_a', object: 'subword tokenization algorithm', source: 'fundamentals' },
            { subject: 'Embedding layer', predicate: 'maps', object: 'token IDs to dense vector representations', source: 'fundamentals' },
            { subject: 'Attention mechanism', predicate: 'computes', object: 'weighted relevance between all token positions', source: 'fundamentals' },
            { subject: 'Feed-forward network (FFN)', predicate: 'applies', object: 'non-linear transformation after attention', source: 'fundamentals' },
            { subject: 'Gradient checkpointing', predicate: 'reduces', object: 'VRAM usage by recomputing activations during backward pass', source: 'optimization' },
            { subject: 'Mixed precision (FP16)', predicate: 'reduces', object: 'memory usage by 50% with minimal accuracy loss', source: 'optimization' },
            { subject: 'INT8 quantization', predicate: 'reduces', object: 'model size by 75% for inference deployment', source: 'optimization' },
            { subject: 'Perplexity', predicate: 'measures', object: 'how well a model predicts the next token (lower is better)', source: 'evaluation' },
        ],
    },
    {
        id: 'brainsim3',
        name: 'BrainSim III Concepts',
        desc: 'Core concepts from the BrainSimulator III reference architecture — UKS graph structure, relationship types, cognitive patterns, and inheritance mechanics.',
        icon: Sparkles,
        category: 'General',
        facts: [
            { subject: 'UKS (Universal Knowledge Store)', predicate: 'is_a', object: 'graph of Things connected by Relationships', source: 'BrainSim III' },
            { subject: 'Thing (UKS node)', predicate: 'can_have', object: 'attributes, relationships, and child Things', source: 'BrainSim III' },
            { subject: 'Relationship', predicate: 'consists_of', object: 'source Thing, target Thing, and relationship type Thing', source: 'BrainSim III' },
            { subject: 'is-a', predicate: 'is_a', object: 'fundamental UKS relationship type for classification', source: 'BrainSim III' },
            { subject: 'has', predicate: 'is_a', object: 'fundamental UKS relationship type for attributes', source: 'BrainSim III' },
            { subject: 'inverseOf', predicate: 'is_a', object: 'UKS relationship type linking bidirectional relations', source: 'BrainSim III' },
            { subject: 'hasProperty', predicate: 'is_a', object: 'UKS relationship type for descriptive attributes', source: 'BrainSim III' },
            { subject: 'isExclusive', predicate: 'is_a', object: 'UKS relationship type preventing conflicting values', source: 'BrainSim III' },
            { subject: 'UKS inheritance', predicate: 'enables', object: 'child nodes to inherit attributes from parent nodes automatically', source: 'BrainSim III' },
            { subject: 'UKS inheritance', predicate: 'supports', object: 'exceptions where a child overrides an inherited attribute', source: 'BrainSim III' },
            { subject: 'Clause (UKS)', predicate: 'relates', object: 'multiple Relationships to express conditional knowledge', source: 'BrainSim III' },
            { subject: 'Transient relationship', predicate: 'has', object: 'a time-to-live (TTL) and auto-expires', source: 'BrainSim III' },
        ],
    },
    {
        id: 'medical',
        name: 'Medical Domain',
        desc: 'Example medical ontology with organs, conditions, treatments, and drug interactions. Use as a starting point for healthcare-focused knowledge graphs.',
        icon: Stethoscope,
        category: 'Domain',
        facts: [
            { subject: 'Heart', predicate: 'is_a', object: 'muscular organ in the circulatory system', source: 'medical ontology' },
            { subject: 'Heart', predicate: 'has_function', object: 'pumping blood through the body', source: 'medical ontology' },
            { subject: 'Aspirin', predicate: 'treats', object: 'pain, inflammation, and fever', source: 'medical ontology' },
            { subject: 'Aspirin', predicate: 'has_side_effect', object: 'increased bleeding risk', source: 'medical ontology' },
            { subject: 'Hypertension', predicate: 'is_a', object: 'chronic condition with elevated blood pressure', source: 'medical ontology' },
            { subject: 'Hypertension', predicate: 'increases_risk_of', object: 'heart disease and stroke', source: 'medical ontology' },
            { subject: 'Insulin', predicate: 'regulates', object: 'blood glucose levels', source: 'medical ontology' },
            { subject: 'Diabetes Type 2', predicate: 'is_characterized_by', object: 'insulin resistance', source: 'medical ontology' },
            { subject: 'Penicillin', predicate: 'is_a', object: 'antibiotic effective against bacterial infections', source: 'medical ontology' },
            { subject: 'Liver', predicate: 'has_function', object: 'detoxification, protein synthesis, and bile production', source: 'medical ontology' },
        ],
    },
    {
        id: 'software_engineering',
        name: 'Software Engineering',
        desc: 'Software architecture, design patterns, development practices, and API concepts. Useful for coding assistant and developer tool knowledge bases.',
        icon: Code2,
        category: 'Domain',
        facts: [
            { subject: 'REST API', predicate: 'is_a', object: 'architectural style for distributed systems using HTTP', source: 'software patterns' },
            { subject: 'Microservice', predicate: 'is_a', object: 'independently deployable service with single responsibility', source: 'software patterns' },
            { subject: 'Docker container', predicate: 'provides', object: 'isolated runtime environment for applications', source: 'software patterns' },
            { subject: 'Git', predicate: 'is_a', object: 'distributed version control system', source: 'software patterns' },
            { subject: 'CI/CD pipeline', predicate: 'automates', object: 'build, test, and deployment workflows', source: 'software patterns' },
            { subject: 'SOLID principles', predicate: 'guide', object: 'object-oriented design for maintainability', source: 'software patterns' },
            { subject: 'SQL injection', predicate: 'is_a', object: 'security vulnerability from unsanitized user input', source: 'software security' },
            { subject: 'OAuth 2.0', predicate: 'is_a', object: 'authorization framework for delegated access', source: 'software security' },
            { subject: 'WebSocket', predicate: 'enables', object: 'full-duplex real-time communication over TCP', source: 'software patterns' },
            { subject: 'Load balancer', predicate: 'distributes', object: 'incoming traffic across multiple server instances', source: 'software patterns' },
        ],
    },
    {
        id: 'science',
        name: 'Science Fundamentals',
        desc: 'Core concepts across physics, chemistry, and biology. A foundation for scientific reasoning and educational knowledge bases.',
        icon: Atom,
        category: 'Domain',
        facts: [
            { subject: 'Water (H₂O)', predicate: 'has_formula', object: 'two hydrogen atoms bonded to one oxygen atom', source: 'chemistry' },
            { subject: 'Photosynthesis', predicate: 'converts', object: 'light energy + CO₂ + water into glucose + oxygen', source: 'biology' },
            { subject: 'DNA', predicate: 'encodes', object: 'genetic instructions for organism development', source: 'biology' },
            { subject: 'Newton\'s Second Law', predicate: 'states', object: 'force equals mass times acceleration (F=ma)', source: 'physics' },
            { subject: 'Speed of light', predicate: 'equals', object: '299,792,458 meters per second in a vacuum', source: 'physics' },
            { subject: 'Mitochondria', predicate: 'is_called', object: 'the powerhouse of the cell (produces ATP)', source: 'biology' },
            { subject: 'Periodic table', predicate: 'organizes', object: 'elements by atomic number and chemical properties', source: 'chemistry' },
            { subject: 'Evolution', predicate: 'is_driven_by', object: 'natural selection, mutation, and genetic drift', source: 'biology' },
            { subject: 'Gravity', predicate: 'is_a', object: 'fundamental force of attraction between masses', source: 'physics' },
            { subject: 'pH scale', predicate: 'measures', object: 'acidity or alkalinity from 0 (acid) to 14 (base)', source: 'chemistry' },
        ],
    },
];


// ─────────────────────────────────────────────────────────────
// RULE ENGINE — Template Suites
// ─────────────────────────────────────────────────────────────

export const RULE_TEMPLATES = [
    {
        id: 'safety_suite',
        name: 'Safety Suite',
        desc: 'Essential safety guardrails every LLM should have. Prevents harmful output, protects user privacy, and blocks adversarial attacks. Start here.',
        icon: Shield,
        difficulty: 'Essential',
        rules: [
            { name: 'No harmful content', category: 'safety', priority: 'critical', condition: 'output contains harmful_keywords or promotes violence', action: 'Block response and log incident' },
            { name: 'PII redaction', category: 'safety', priority: 'critical', condition: 'output matches PII patterns (SSN, email, phone, address)', action: 'Redact matched text and warn user' },
            { name: 'Jailbreak detection', category: 'safety', priority: 'critical', condition: 'input attempts prompt injection or role override', action: 'Reject input and reset conversation context' },
            { name: 'Toxic language filter', category: 'safety', priority: 'high', condition: 'output toxicity score exceeds threshold (0.7)', action: 'Rewrite response with neutral tone' },
            { name: 'Self-harm prevention', category: 'safety', priority: 'critical', condition: 'conversation indicates self-harm or crisis signals', action: 'Provide crisis resources and escalate' },
        ],
    },
    {
        id: 'ethics_compliance',
        name: 'Ethics & Compliance',
        desc: 'Fairness, transparency, and accountability rules. Ensures the model treats all users equitably and discloses its AI nature when appropriate.',
        icon: Scale,
        difficulty: 'Intermediate',
        rules: [
            { name: 'Bias detection', category: 'ethics', priority: 'high', condition: 'output shows demographic bias in recommendations or judgments', action: 'Flag for review and apply debiasing prompt' },
            { name: 'Fairness enforcement', category: 'ethics', priority: 'high', condition: 'responses vary significantly by user demographic context', action: 'Normalize response quality across demographics' },
            { name: 'Transparency disclosure', category: 'ethics', priority: 'medium', condition: 'user asks if they are talking to a human', action: 'Clearly disclose AI nature' },
            { name: 'Source attribution', category: 'ethics', priority: 'medium', condition: 'output includes factual claims or statistics', action: 'Append source references where available' },
        ],
    },
    {
        id: 'content_quality',
        name: 'Content Quality',
        desc: 'Ensure accurate, relevant, and well-formatted responses. Catches hallucinations, enforces length limits, and maintains output consistency.',
        icon: Eye,
        difficulty: 'Intermediate',
        rules: [
            { name: 'Hallucination detection', category: 'content', priority: 'high', condition: 'output confidence below threshold or contradicts knowledge base', action: 'Add uncertainty disclaimer or defer to knowledge store' },
            { name: 'Relevance enforcement', category: 'content', priority: 'medium', condition: 'response topic drifts from user query intent', action: 'Refocus response on original question' },
            { name: 'Response length limit', category: 'output', priority: 'medium', condition: 'token_count exceeds 4096', action: 'Truncate with summary and continuation offer' },
            { name: 'Format compliance', category: 'output', priority: 'low', condition: 'user requests specific format (JSON, markdown, list)', action: 'Validate and enforce requested output format' },
        ],
    },
    {
        id: 'behavioral_alignment',
        name: 'Behavioral Alignment',
        desc: 'Shape your model\'s personality and communication style. Professional tone, persona consistency, language matching, and empathetic responses.',
        icon: Heart,
        difficulty: 'Advanced',
        rules: [
            { name: 'Professional tone', category: 'behavior', priority: 'medium', condition: 'output contains casual slang or unprofessional language', action: 'Adjust tone to professional register' },
            { name: 'Persona consistency', category: 'behavior', priority: 'medium', condition: 'response breaks established persona or character', action: 'Realign with defined persona attributes' },
            { name: 'Language matching', category: 'behavior', priority: 'low', condition: 'user writes in non-English language', action: 'Respond in same language as user input' },
            { name: 'Empathy guidelines', category: 'behavior', priority: 'low', condition: 'user expresses frustration, confusion, or emotional distress', action: 'Acknowledge emotion before providing solution' },
        ],
    },
];


// ─────────────────────────────────────────────────────────────
// RULE ENGINE — Custom Rule Guide (educational content)
// ─────────────────────────────────────────────────────────────

export const CUSTOM_RULE_GUIDE = {
    title: 'How to Create Your Own Rules',
    sections: [
        {
            heading: 'Understanding Conditions (IF)',
            content: 'Conditions define WHEN a rule should fire. They are evaluated against the model\'s input, output, or knowledge state at inference time.',
            examples: [
                { condition: 'output contains harmful_keywords', explanation: 'Fires when specific blacklisted words appear in the response' },
                { condition: 'output matches PII_regex', explanation: 'Fires when the output matches patterns for personal data (email, phone, SSN)' },
                { condition: 'token_count > 4096', explanation: 'Fires when the response exceeds a token length threshold' },
                { condition: 'input attempts prompt injection', explanation: 'Fires when the user tries to override system instructions' },
                { condition: 'output confidence below 0.5', explanation: 'Fires when the model is uncertain about its answer' },
            ],
        },
        {
            heading: 'Understanding Actions (THEN)',
            content: 'Actions define WHAT happens when a condition is met. Actions can block, modify, log, or escalate.',
            examples: [
                { condition: 'Block and log', explanation: 'Prevent the response from reaching the user and record the event' },
                { condition: 'Redact matched text', explanation: 'Remove or mask sensitive content while keeping the rest' },
                { condition: 'Rewrite with neutral tone', explanation: 'Automatically adjust the language style of the response' },
                { condition: 'Add disclaimer', explanation: 'Append a notice (e.g., "This is AI-generated content")' },
                { condition: 'Escalate to human', explanation: 'Flag the conversation for human review' },
            ],
        },
        {
            heading: 'Priority Levels',
            content: 'Rules execute in priority order — higher priority rules fire first. If a Critical rule blocks a response, lower-priority rules never run.',
            levels: [
                { level: 'Critical', color: 'danger', use: 'Safety and security — rules that MUST always fire (e.g., harmful content blocking)' },
                { level: 'High', color: 'warning', use: 'Important constraints — ethics, compliance, hallucination prevention' },
                { level: 'Medium', color: 'info', use: 'Quality and formatting — response length, relevance, tone adjustments' },
                { level: 'Low', color: 'default', use: 'Preferences and polish — language matching, style consistency, minor enhancements' },
            ],
        },
        {
            heading: 'Choosing Categories',
            content: 'Categories help organize rules and enable bulk toggling. Choose the category that best describes your rule\'s purpose.',
            categories: [
                { name: 'Safety', desc: 'Prevent harm, protect users, block dangerous content' },
                { name: 'Ethics', desc: 'Ensure fairness, reduce bias, promote transparency' },
                { name: 'Content Filter', desc: 'Control what topics or content types are allowed' },
                { name: 'Behavior', desc: 'Shape personality, tone, and communication style' },
                { name: 'Output Format', desc: 'Enforce structure, length, and formatting requirements' },
                { name: 'Custom', desc: 'Domain-specific or experimental rules' },
            ],
        },
        {
            heading: 'Tips for Writing Effective Rules',
            tips: [
                'Start with the Safety Suite — every model needs basic guardrails before deployment',
                'Write specific conditions rather than broad ones — "output contains profanity_list" is better than "output is bad"',
                'Test rules individually before combining them — rule interactions can cause unexpected behavior',
                'Use priority levels to resolve conflicts — if two rules contradict, the higher priority one wins',
                'Keep actions proportional — don\'t block entire responses when redacting a single word would suffice',
                'Review and update rules regularly as your model\'s use cases evolve',
            ],
        },
    ],
};


// ─────────────────────────────────────────────────────────────
// INHERITANCE — Architecture Presets
// ─────────────────────────────────────────────────────────────

export const INHERITANCE_PRESETS = [
    {
        id: 'standard_transformer',
        name: 'Standard Transformer',
        desc: 'The default balanced configuration. A proven 4-layer architecture with 8 modules — Foundation, Attention, FFN, and Output. Good starting point for most builds.',
        icon: Layers,
        vramEstimate: '~2.5 GB',
        layers: [
            {
                id: 1, name: 'Foundation Layer', type: 'base', active: true,
                modules: [
                    { id: 101, name: 'Embedding', config: 'vocab=32000, dim=768', inherited: false },
                    { id: 102, name: 'Positional Encoding', config: 'RoPE, max_len=2048', inherited: false },
                ],
            },
            {
                id: 2, name: 'Attention Layer', type: 'attention', active: true,
                modules: [
                    { id: 201, name: 'Multi-Head Attention', config: 'heads=12, dim=768', inherited: true },
                    { id: 202, name: 'Flash Attention', config: 'enabled=true, causal=true', inherited: false },
                ],
            },
            {
                id: 3, name: 'FFN Layer', type: 'ffn', active: true,
                modules: [
                    { id: 301, name: 'SwiGLU FFN', config: 'intermediate=3072', inherited: true },
                    { id: 302, name: 'Dropout', config: 'p=0.1', inherited: true },
                ],
            },
            {
                id: 4, name: 'Output Layer', type: 'output', active: true,
                modules: [
                    { id: 401, name: 'Layer Norm', config: 'eps=1e-6', inherited: true },
                    { id: 402, name: 'LM Head', config: 'vocab=32000, tied=true', inherited: true },
                ],
            },
        ],
    },
    {
        id: 'memory_optimized',
        name: 'Memory-Optimized (GTX 1050 Ti)',
        desc: 'Designed for 4GB VRAM constraint. Reduced attention heads, INT8 quantization hints, and maximum parameter sharing through inheritance. Ideal for ImpressionCore\'s target hardware.',
        icon: Cpu,
        vramEstimate: '~1.8 GB',
        layers: [
            {
                id: 1, name: 'Foundation Layer', type: 'base', active: true,
                modules: [
                    { id: 101, name: 'Embedding', config: 'vocab=32000, dim=512, dtype=int8', inherited: false },
                    { id: 102, name: 'Positional Encoding', config: 'RoPE, max_len=1024', inherited: false },
                ],
            },
            {
                id: 2, name: 'Attention Layer', type: 'attention', active: true,
                modules: [
                    { id: 201, name: 'Multi-Head Attention', config: 'heads=8, dim=512, dtype=fp16', inherited: true },
                    { id: 202, name: 'KV Cache', config: 'max_batch=1, quantized=true', inherited: true },
                ],
            },
            {
                id: 3, name: 'FFN Layer', type: 'ffn', active: true,
                modules: [
                    { id: 301, name: 'SwiGLU FFN', config: 'intermediate=2048, dtype=fp16', inherited: true },
                    { id: 302, name: 'Dropout', config: 'p=0.05', inherited: true },
                ],
            },
            {
                id: 4, name: 'Output Layer', type: 'output', active: true,
                modules: [
                    { id: 401, name: 'Layer Norm', config: 'eps=1e-6', inherited: true },
                    { id: 402, name: 'LM Head', config: 'vocab=32000, tied=true, dtype=fp16', inherited: true },
                ],
            },
        ],
    },
    {
        id: 'mixture_of_experts',
        name: 'Mixture of Experts (MoE)',
        desc: 'Adds an expert routing layer for sparse activation. Multiple FFN expert modules with top-k routing — only a subset of experts activate per token, enabling larger effective capacity within VRAM constraints.',
        icon: Zap,
        vramEstimate: '~3.5 GB',
        layers: [
            {
                id: 1, name: 'Foundation Layer', type: 'base', active: true,
                modules: [
                    { id: 101, name: 'Embedding', config: 'vocab=32000, dim=768', inherited: false },
                    { id: 102, name: 'Positional Encoding', config: 'RoPE, max_len=2048', inherited: false },
                ],
            },
            {
                id: 2, name: 'Attention Layer', type: 'attention', active: true,
                modules: [
                    { id: 201, name: 'Multi-Head Attention', config: 'heads=12, dim=768', inherited: true },
                    { id: 202, name: 'Flash Attention', config: 'enabled=true, causal=true', inherited: false },
                ],
            },
            {
                id: 3, name: 'Expert Router', type: 'ffn', active: true,
                modules: [
                    { id: 301, name: 'Top-K Router', config: 'num_experts=8, top_k=2, capacity_factor=1.25', inherited: false },
                    { id: 302, name: 'Load Balancing Loss', config: 'aux_loss_weight=0.01', inherited: true },
                ],
            },
            {
                id: 4, name: 'Expert FFN Pool', type: 'ffn', active: true,
                modules: [
                    { id: 401, name: 'Expert 1 (General)', config: 'intermediate=3072, activation=swiglu', inherited: true },
                    { id: 402, name: 'Expert 2 (Reasoning)', config: 'intermediate=3072, activation=swiglu', inherited: true },
                    { id: 403, name: 'Expert 3 (Knowledge)', config: 'intermediate=3072, activation=swiglu', inherited: true },
                    { id: 404, name: 'Expert 4 (Creative)', config: 'intermediate=3072, activation=swiglu', inherited: true },
                ],
            },
            {
                id: 5, name: 'Output Layer', type: 'output', active: true,
                modules: [
                    { id: 501, name: 'Layer Norm', config: 'eps=1e-6', inherited: true },
                    { id: 502, name: 'LM Head', config: 'vocab=32000, tied=true', inherited: true },
                ],
            },
        ],
    },
    {
        id: 'knowledge_distillation',
        name: 'Knowledge Distillation',
        desc: 'Teacher-student architecture for training a smaller model to mimic a larger one. Includes teacher checkpoint reference, distillation loss module, and progressive knowledge transfer configuration.',
        icon: BookOpen,
        vramEstimate: '~2.8 GB',
        layers: [
            {
                id: 1, name: 'Teacher Reference', type: 'base', active: true,
                modules: [
                    { id: 101, name: 'Teacher Checkpoint', config: 'path=checkpoints/teacher_b2.pt, frozen=true', inherited: false },
                    { id: 102, name: 'Temperature Scaling', config: 'T=4.0, annealing=cosine', inherited: false },
                ],
            },
            {
                id: 2, name: 'Student Foundation', type: 'base', active: true,
                modules: [
                    { id: 201, name: 'Embedding', config: 'vocab=32000, dim=512', inherited: false },
                    { id: 202, name: 'Positional Encoding', config: 'RoPE, max_len=2048', inherited: false },
                ],
            },
            {
                id: 3, name: 'Student Attention', type: 'attention', active: true,
                modules: [
                    { id: 301, name: 'Multi-Head Attention', config: 'heads=8, dim=512', inherited: true },
                    { id: 302, name: 'Attention Distillation', config: 'layer_mapping=skip, loss_weight=0.3', inherited: true },
                ],
            },
            {
                id: 4, name: 'Student FFN', type: 'ffn', active: true,
                modules: [
                    { id: 401, name: 'SwiGLU FFN', config: 'intermediate=2048', inherited: true },
                    { id: 402, name: 'Hidden State Distillation', config: 'projection=linear, loss_weight=0.2', inherited: true },
                ],
            },
            {
                id: 5, name: 'Output Layer', type: 'output', active: true,
                modules: [
                    { id: 501, name: 'KL Divergence Loss', config: 'weight=0.5, soft_labels=true', inherited: true },
                    { id: 502, name: 'LM Head', config: 'vocab=32000, tied=true', inherited: true },
                ],
            },
        ],
    },
    {
        id: 'deep_narrow',
        name: 'Deep Narrow',
        desc: 'More layers with smaller hidden dimensions — trades width for depth. Maximizes reasoning capability through deep computation chains while keeping VRAM usage low through aggressive parameter sharing.',
        icon: GitBranch,
        vramEstimate: '~2.2 GB',
        layers: [
            {
                id: 1, name: 'Foundation Layer', type: 'base', active: true,
                modules: [
                    { id: 101, name: 'Embedding', config: 'vocab=32000, dim=384', inherited: false },
                    { id: 102, name: 'Positional Encoding', config: 'RoPE, max_len=2048', inherited: false },
                ],
            },
            {
                id: 2, name: 'Attention Block A', type: 'attention', active: true,
                modules: [
                    { id: 201, name: 'Multi-Head Attention', config: 'heads=6, dim=384', inherited: true },
                    { id: 202, name: 'Pre-Norm', config: 'RMSNorm, eps=1e-6', inherited: true },
                ],
            },
            {
                id: 3, name: 'FFN Block A', type: 'ffn', active: true,
                modules: [
                    { id: 301, name: 'SwiGLU FFN', config: 'intermediate=1536', inherited: true },
                    { id: 302, name: 'Residual Scale', config: 'alpha=0.5, learnable=true', inherited: true },
                ],
            },
            {
                id: 4, name: 'Attention Block B', type: 'attention', active: true,
                modules: [
                    { id: 401, name: 'Multi-Head Attention', config: 'heads=6, dim=384', inherited: true },
                    { id: 402, name: 'Pre-Norm', config: 'RMSNorm, eps=1e-6', inherited: true },
                ],
            },
            {
                id: 5, name: 'FFN Block B', type: 'ffn', active: true,
                modules: [
                    { id: 501, name: 'SwiGLU FFN', config: 'intermediate=1536', inherited: true },
                    { id: 502, name: 'Residual Scale', config: 'alpha=0.5, learnable=true', inherited: true },
                ],
            },
            {
                id: 6, name: 'Output Layer', type: 'output', active: true,
                modules: [
                    { id: 601, name: 'Layer Norm', config: 'eps=1e-6', inherited: true },
                    { id: 602, name: 'LM Head', config: 'vocab=32000, tied=true', inherited: true },
                ],
            },
        ],
    },
];


// ─────────────────────────────────────────────────────────────
// INHERITANCE — Custom Architecture Guide (educational content)
// ─────────────────────────────────────────────────────────────

export const INHERITANCE_GUIDE = {
    title: 'How Inheritance Works',
    sections: [
        {
            heading: 'Inherited vs. Overridden',
            content: 'When a module is marked "Inherited," it receives its configuration from the parent layer or a shared global config. When "Overridden," the module uses its own custom configuration. Inheritance reduces parameter duplication — you only store what makes each module unique.',
        },
        {
            heading: 'When to Override',
            tips: [
                'Override when a module needs domain-specific tuning (e.g., custom attention heads for code generation)',
                'Override when you\'re experimenting with a single layer without affecting others',
                'Keep inherited for standard components that should stay consistent across layers (e.g., Dropout, Layer Norm)',
            ],
        },
        {
            heading: 'Designing Custom Architectures',
            tips: [
                'Start from the preset closest to your needs, then modify',
                'Keep Foundation and Output layers — they\'re required for any transformer',
                'Add depth (more layers) before adding width (larger hidden dims) for better VRAM efficiency',
                'Use the VRAM estimate as a guide — stay under your GPU\'s capacity',
                'Test with a small dataset before committing to a deep architecture',
            ],
        },
    ],
};
