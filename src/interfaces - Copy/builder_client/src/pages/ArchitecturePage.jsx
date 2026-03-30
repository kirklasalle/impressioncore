import React, { useState } from 'react';
import { Network, Layers, Zap, Brain, Eye, Ear, ChevronDown, ChevronRight } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Badge, StatCard } from '../components/ui';
import { cn } from '../lib/utils';

const ARCHITECTURE = [
    {
        id: 'embedding', name: 'Embedding Layer', icon: Layers, color: 'cyan',
        desc: 'Token + positional + modality embeddings. Supports text, vision patches, and audio spectrograms.',
        details: ['Vocabulary: 32,000 tokens', 'Hidden dim: 768', 'RoPE positional encoding', 'Vision patch tokenizer (16×16)', 'Audio spectrogram encoder'],
    },
    {
        id: 'attention', name: 'Multi-Head Attention', icon: Brain, color: 'indigo',
        desc: 'Grouped-query attention (GQA) with Flash Attention 2 for memory efficiency.',
        details: ['12 attention heads', '4 KV groups (GQA 3:1)', 'Flash Attention 2 enabled', 'Causal masking', 'Sliding window option (4096)'],
    },
    {
        id: 'ffn', name: 'Feed-Forward Network', icon: Zap, color: 'success',
        desc: 'SwiGLU activation with gated linear units for improved gradient flow.',
        details: ['SwiGLU activation', 'Intermediate: 3072 (4× hidden)', 'Dropout: 0.1', 'Pre-norm (RMSNorm)'],
    },
    {
        id: 'vision', name: 'Vision Encoder', icon: Eye, color: 'warning',
        desc: 'ViT-based patch encoder for image understanding within the unified transformer.',
        details: ['Patch size: 16×16', 'Max resolution: 384×384', 'Shared embedding space', 'Cross-attention fusion'],
    },
    {
        id: 'audio', name: 'Audio Encoder', icon: Ear, color: 'danger',
        desc: 'Spectrogram-based audio processing with convolutional frontend.',
        details: ['Mel spectrogram: 80 bins', 'Conv1D frontend: 2 layers', 'Max duration: 30s', 'Shared transformer backbone'],
    },
    {
        id: 'output', name: 'Output Head', icon: Network, color: 'info',
        desc: 'Language modeling head with tied embeddings for efficient parameter usage.',
        details: ['Tied embedding weights', 'RMSNorm pre-head', 'Temperature scaling', 'Top-p / Top-k sampling'],
    },
];

export default function ArchitecturePage() {
    const [expanded, setExpanded] = useState(new Set(['embedding', 'attention']));

    const toggle = (id) => {
        setExpanded((prev) => {
            const next = new Set(prev);
            next.has(id) ? next.delete(id) : next.add(id);
            return next;
        });
    };

    return (
        <ContentArea title="Architecture Explorer" subtitle="Interactive visualization of the B3 model architecture.">
            {/* Stats */}
            <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 mb-6">
                <StatCard label="Parameters" value="~350M" />
                <StatCard label="Layers" value="24" />
                <StatCard label="Hidden Dim" value="768" />
                <StatCard label="Heads" value="12" />
                <StatCard label="VRAM Est." value="~2.1 GB" />
            </div>

            {/* Flow Visual */}
            <Card className="mb-6">
                <CardTitle icon={Network}>Data Flow</CardTitle>
                <div className="mt-4 flex items-center gap-2 overflow-x-auto pb-2">
                    {ARCHITECTURE.map((block, i) => {
                        const Icon = block.icon;
                        return (
                            <React.Fragment key={block.id}>
                                <button
                                    onClick={() => toggle(block.id)}
                                    className={cn(
                                        'px-4 py-2.5 rounded-xl border flex items-center gap-2 whitespace-nowrap transition-all',
                                        expanded.has(block.id)
                                            ? `border-accent-${block.color}/40 bg-accent-${block.color}/10 text-accent-${block.color}`
                                            : 'border-ic-border bg-ic-surface text-txt-secondary hover:border-accent-cyan/30'
                                    )}
                                >
                                    <Icon size={16} />
                                    <span className="text-sm font-medium">{block.name}</span>
                                </button>
                                {i < ARCHITECTURE.length - 1 && (
                                    <span className="text-accent-cyan/30 shrink-0">→</span>
                                )}
                            </React.Fragment>
                        );
                    })}
                </div>
            </Card>

            {/* Detail Cards */}
            <div className="space-y-3">
                {ARCHITECTURE.map((block) => {
                    const Icon = block.icon;
                    const isOpen = expanded.has(block.id);
                    return (
                        <Card key={block.id}>
                            <button onClick={() => toggle(block.id)} className="w-full flex items-center gap-3">
                                {isOpen ? <ChevronDown size={16} className="text-txt-muted" /> : <ChevronRight size={16} className="text-txt-muted" />}
                                <div className={cn('w-9 h-9 rounded-lg flex items-center justify-center', `bg-accent-${block.color}/20`)}>
                                    <Icon size={18} className={`text-accent-${block.color}`} />
                                </div>
                                <div className="flex-1 text-left">
                                    <div className="text-sm font-semibold text-txt-primary">{block.name}</div>
                                    <div className="text-[11px] text-txt-muted">{block.desc}</div>
                                </div>
                                <Badge variant={block.color}>{block.id}</Badge>
                            </button>
                            {isOpen && (
                                <div className="mt-3 ml-10 p-4 rounded-xl bg-ic-bg border border-ic-border animate-fade-in-up">
                                    <h4 className="text-xs font-semibold text-txt-primary mb-2">Configuration Details</h4>
                                    <ul className="space-y-1">
                                        {block.details.map((d, i) => (
                                            <li key={i} className="text-sm text-txt-secondary flex items-center gap-2">
                                                <span className="w-1.5 h-1.5 rounded-full bg-accent-cyan shrink-0" />
                                                {d}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </Card>
                    );
                })}
            </div>
        </ContentArea>
    );
}
