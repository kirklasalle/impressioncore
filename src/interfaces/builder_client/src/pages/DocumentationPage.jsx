import React, { useState } from 'react';
import { BookOpen, Search, ExternalLink, FileText, Code, Lightbulb, Bookmark } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Badge } from '../components/ui';
import { cn } from '../lib/utils';

const DOCS = [
    {
        category: 'Getting Started',
        items: [
            { title: 'Installation Guide', desc: 'Set up Python, CUDA, and project dependencies', icon: Code, tags: ['setup', 'python'] },
            { title: 'Quick Start', desc: 'Build your first B3 model in 10 minutes', icon: Lightbulb, tags: ['tutorial', 'beginner'] },
            { title: 'Hardware Requirements', desc: 'GPU, RAM, and storage recommendations', icon: FileText, tags: ['hardware', 'gpu'] },
        ],
    },
    {
        category: 'Architecture',
        items: [
            { title: 'B3 Architecture Overview', desc: 'Transformer design, attention mechanisms, and module hierarchy', icon: FileText, tags: ['architecture', 'transformer'] },
            { title: 'Multimodal Pipeline', desc: 'Text, vision, and audio processing pathways', icon: FileText, tags: ['multimodal', 'vision', 'audio'] },
            { title: 'Memory Optimization', desc: 'Gradient checkpointing, mixed precision, Flash Attention', icon: Lightbulb, tags: ['optimization', 'vram'] },
        ],
    },
    {
        category: 'Training',
        items: [
            { title: 'Training Pipeline', desc: 'End-to-end training workflow and hyperparameters', icon: Code, tags: ['training', 'pipeline'] },
            { title: 'Data Preparation', desc: 'Dataset formats, preprocessing, and augmentation', icon: FileText, tags: ['data', 'preprocessing'] },
            { title: 'Curriculum Learning', desc: 'Progressive difficulty and multi-phase training', icon: Lightbulb, tags: ['curriculum', 'training'] },
            { title: 'Knowledge Distillation', desc: 'Teacher-student framework for model compression', icon: FileText, tags: ['distillation', 'compression'] },
        ],
    },
    {
        category: 'Deployment',
        items: [
            { title: 'Export Formats', desc: 'PyTorch, SafeTensors, ONNX, TensorRT', icon: Code, tags: ['export', 'deployment'] },
            { title: 'Quantization Guide', desc: 'INT8/INT4 quantization for inference', icon: Lightbulb, tags: ['quantization', 'optimization'] },
            { title: 'API Reference', desc: 'REST API endpoints and WebSocket interfaces', icon: Code, tags: ['api', 'reference'] },
        ],
    },
    {
        category: 'Reference',
        items: [
            { title: 'Configuration Reference', desc: 'All YAML/JSON configuration options', icon: FileText, tags: ['config', 'reference'] },
            { title: 'CLI Commands', desc: 'Command-line tools and utilities', icon: Code, tags: ['cli', 'tools'] },
            { title: 'Troubleshooting', desc: 'Common issues and solutions', icon: Lightbulb, tags: ['debug', 'faq'] },
        ],
    },
];

export default function DocumentationPage() {
    const [query, setQuery] = useState('');
    const [activeCategory, setActiveCategory] = useState(null);

    const q = query.toLowerCase();
    const filtered = DOCS.map((cat) => ({
        ...cat,
        items: cat.items.filter((item) =>
            !q || item.title.toLowerCase().includes(q) || item.desc.toLowerCase().includes(q) || item.tags.some((t) => t.includes(q))
        ),
    })).filter((cat) => cat.items.length > 0 && (!activeCategory || cat.category === activeCategory));

    const totalDocs = DOCS.reduce((a, c) => a + c.items.length, 0);

    return (
        <ContentArea title="Documentation" subtitle="Browse guides, references, and tutorials.">
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
                    {DOCS.map((cat) => (
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
                            const Icon = item.icon;
                            return (
                                <Card key={item.title} className="group cursor-pointer hover:border-accent-cyan/40 transition-colors">
                                    <div className="flex items-start gap-3">
                                        <div className="w-9 h-9 rounded-lg bg-accent-cyan/10 flex items-center justify-center shrink-0 group-hover:bg-accent-cyan/20 transition-colors">
                                            <Icon size={18} className="text-accent-cyan" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2">
                                                <h3 className="text-sm font-semibold text-txt-primary truncate">{item.title}</h3>
                                                <ExternalLink size={12} className="text-txt-muted opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
                                            </div>
                                            <p className="text-[11px] text-txt-muted mt-0.5 line-clamp-2">{item.desc}</p>
                                            <div className="flex gap-1 mt-2">
                                                {item.tags.map((tag) => (
                                                    <Badge key={tag} variant="default">{tag}</Badge>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                </Card>
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
