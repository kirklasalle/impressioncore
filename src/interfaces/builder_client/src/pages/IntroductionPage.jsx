import React, { useState } from 'react';
import { BookOpen, Cpu, Brain, Layers, Zap, Eye, ChevronDown, ChevronRight } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Badge } from '../components/ui';

const PRINCIPLES = [
    {
        id: 'brain', icon: Brain, title: 'Brain-Inspired Architecture',
        desc: 'Neural pathways modeled after biological cognition, with multi-scale attention and associative memory modules.',
        details: [
            'Multi-scale attention mimics cortical micro-columns with local and global receptive fields',
            'Associative memory module enables rapid one-shot binding of novel concepts',
            'Hebbian-inspired weight updates for continual learning without catastrophic forgetting',
            'Hippocampal replay buffer consolidates short-term experience into long-term knowledge',
            'Modality-agnostic cognitive workspace for cross-modal reasoning and abstraction',
        ],
    },
    {
        id: 'hardware', icon: Cpu, title: 'Hardware-Efficient Design',
        desc: 'Every component optimized for consumer GPUs (4GB VRAM target). Gradient checkpointing, mixed precision, and dynamic batching built in.',
        details: [
            'Target hardware: NVIDIA GTX 1050 Ti (4 GB VRAM) — runs full training and inference',
            'Automatic mixed precision (FP16/BF16) reduces memory footprint by ~50%',
            'Gradient checkpointing trades compute for memory, enabling deeper models in limited VRAM',
            'Dynamic micro-batching adapts batch size at runtime based on available GPU memory',
            'Quantization-aware training (4-bit / 8-bit) for ultra-low-memory deployment',
        ],
    },
    {
        id: 'pipeline', icon: Layers, title: 'Modular Pipeline',
        desc: 'Each stage (data → tokenizer → model → train → eval → deploy) is independently configurable and testable.',
        details: [
            'Plug-and-play stages: swap tokenizers, model architectures, or trainers without rewriting glue code',
            'YAML/JSON configuration files drive every stage — no hard-coded hyper-parameters',
            'Each module exposes a standardized interface for unit and integration testing',
            'Pipeline DAG supports parallel execution of independent stages for faster iteration',
            'Built-in checkpoint management with automatic resume on interruption',
        ],
    },
    {
        id: 'multimodal', icon: Eye, title: 'Multimodal Processing',
        desc: 'Text, image, audio, and video processed through unified transformer backbone with modality-specific encoders.',
        details: [
            'Shared transformer backbone fuses representations from all modalities in a common latent space',
            'Vision encoder: ViT-based patch tokenizer (16×16) with cross-attention fusion',
            'Audio encoder: Mel-spectrogram frontend with convolutional feature extractor',
            'Video processing via temporal sampling and frame-level patch sequences',
            'Late-fusion and early-fusion strategies configurable per task for optimal performance',
        ],
    },
    {
        id: 'inference', icon: Zap, title: 'Real-Time Inference',
        desc: 'Optimized inference path with KV-cache, speculative decoding, and batched generation for responsive interaction.',
        details: [
            'Persistent KV-cache eliminates redundant computation for autoregressive generation',
            'Speculative decoding with a lightweight draft model for 2-3× faster token throughput',
            'Continuous batching merges incoming requests to maximize GPU utilization',
            'ONNX Runtime and TensorRT export paths for production-grade latency',
            'Streaming token output via WebSocket for real-time user-facing interaction',
        ],
    },
];

export default function IntroductionPage() {
    const [expanded, setExpanded] = useState(new Set());

    const toggle = (id) => {
        setExpanded((prev) => {
            const next = new Set(prev);
            next.has(id) ? next.delete(id) : next.add(id);
            return next;
        });
    };

    return (
        <ContentArea title="Introduction" subtitle="Architecture overview and core design principles of ImpressionCore B3.">
            <div className="max-w-4xl space-y-8">
                {/* Overview */}
                <Card>
                    <CardTitle icon={BookOpen}>Overview</CardTitle>
                    <p className="text-sm text-txt-secondary leading-relaxed mt-3">
                        ImpressionCore B3 is the third generation of the brain-inspired multimodal AI framework.
                        It processes information across text, images, audio, and video while running efficiently
                        on consumer hardware. The B3 series introduces a refined transformer backbone with
                        dynamic multi-scale attention, enhanced memory consolidation, and a complete end-to-end
                        training pipeline accessible through this builder interface.
                    </p>
                </Card>

                {/* Design Principles */}
                <div>
                    <h2 className="text-lg font-semibold text-txt-primary mb-4">Design Principles</h2>
                    <div className="space-y-4">
                        {PRINCIPLES.map((p) => {
                            const Icon = p.icon;
                            const isOpen = expanded.has(p.id);
                            return (
                                <Card key={p.id}>
                                    <button onClick={() => toggle(p.id)} className="w-full flex items-start gap-4 text-left">
                                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-accent-cyan/20 to-accent-indigo/20 flex items-center justify-center shrink-0">
                                            <Icon size={18} className="text-accent-cyan" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <h3 className="text-sm font-semibold text-txt-primary mb-1">{p.title}</h3>
                                            <p className="text-xs text-txt-muted leading-relaxed">{p.desc}</p>
                                        </div>
                                        {isOpen
                                            ? <ChevronDown size={16} className="text-accent-cyan mt-1 shrink-0" />
                                            : <ChevronRight size={16} className="text-txt-muted mt-1 shrink-0" />
                                        }
                                    </button>
                                    {isOpen && (
                                        <div className="mt-3 ml-14 p-4 rounded-xl bg-ic-bg border border-ic-border animate-fade-in-up">
                                            <ul className="space-y-1.5">
                                                {p.details.map((d, i) => (
                                                    <li key={i} className="text-sm text-txt-secondary flex items-start gap-2">
                                                        <span className="w-1.5 h-1.5 rounded-full bg-accent-cyan shrink-0 mt-1.5" />
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
                </div>

                {/* Tech Stack */}
                <Card>
                    <CardTitle>Technology Stack</CardTitle>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
                        {['PyTorch 2.x', 'Python 3.10+', 'CUDA 12.x', 'Transformers', 'SafeTensors', 'ONNX Runtime', 'Flash Attention', 'BitsAndBytes'].map((tech) => (
                            <Badge key={tech} variant="cyan">{tech}</Badge>
                        ))}
                    </div>
                </Card>
            </div>
        </ContentArea>
    );
}
