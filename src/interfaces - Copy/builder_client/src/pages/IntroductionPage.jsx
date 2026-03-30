import React from 'react';
import { BookOpen, Cpu, Brain, Layers, Zap, Eye } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Badge } from '../components/ui';

const PRINCIPLES = [
    { icon: Brain, title: 'Brain-Inspired Architecture', desc: 'Neural pathways modeled after biological cognition, with multi-scale attention and associative memory modules.' },
    { icon: Cpu, title: 'Hardware-Efficient Design', desc: 'Every component optimized for consumer GPUs (4GB VRAM target). Gradient checkpointing, mixed precision, and dynamic batching built in.' },
    { icon: Layers, title: 'Modular Pipeline', desc: 'Each stage (data → tokenizer → model → train → eval → deploy) is independently configurable and testable.' },
    { icon: Eye, title: 'Multimodal Processing', desc: 'Text, image, audio, and video processed through unified transformer backbone with modality-specific encoders.' },
    { icon: Zap, title: 'Real-Time Inference', desc: 'Optimized inference path with KV-cache, speculative decoding, and batched generation for responsive interaction.' },
];

export default function IntroductionPage() {
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
                            return (
                                <Card key={p.title} className="flex items-start gap-4">
                                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-accent-cyan/20 to-accent-indigo/20 flex items-center justify-center shrink-0">
                                        <Icon size={18} className="text-accent-cyan" />
                                    </div>
                                    <div>
                                        <h3 className="text-sm font-semibold text-txt-primary mb-1">{p.title}</h3>
                                        <p className="text-xs text-txt-muted leading-relaxed">{p.desc}</p>
                                    </div>
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
