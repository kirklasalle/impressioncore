import React from 'react';
import { Link } from 'react-router-dom';
import { Zap, Brain, Layers, ArrowRight, Cpu } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card } from '../components/ui';
import { cn } from '../lib/utils';
import { PIPELINE_STEPS } from '../lib/constants';

const CAPABILITIES = [
    { icon: Cpu, title: 'Consumer GPU', desc: 'Optimized for GTX 1050 Ti (4GB VRAM) with gradient checkpointing and mixed precision.' },
    { icon: Brain, title: 'Brain-Inspired', desc: 'Neural architecture inspired by biological cognition patterns and memory systems.' },
    { icon: Layers, title: 'Multimodal', desc: 'Process text, images, audio, and video in a unified transformer pipeline.' },
    { icon: Zap, title: 'End-to-End', desc: 'Complete pipeline from data preparation through deployment in 9 guided steps.' },
];

export default function HomePage() {
    return (
        <ContentArea>
            {/* Hero */}
            <div className="text-center mb-12">
                <h1 className="text-4xl lg:text-5xl font-bold mb-4">
                    <span className="gradient-text">ImpressionCore B3</span>
                </h1>
                <p className="text-lg text-txt-secondary max-w-2xl mx-auto mb-8">
                    World-class model builder for brain-inspired multimodal AI.
                    Build, train, evaluate, and deploy — all from one dashboard.
                </p>
                <div className="flex items-center justify-center gap-4 flex-wrap">
                    <Link to="/introduction" className="btn-primary">
                        <ArrowRight size={16} /> Get Started
                    </Link>
                    <Link to="/walkthrough" className="btn-secondary">
                        Interactive Walkthrough
                    </Link>
                    <Link to="/unified-builder" className="btn-secondary">
                        Unified Builder
                    </Link>
                </div>
            </div>

            {/* Pipeline Steps Grid */}
            <h2 className="text-lg font-semibold text-txt-primary mb-4">Build Pipeline</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-12">
                {PIPELINE_STEPS.map((step) => {
                    const Icon = step.icon;
                    return (
                        <Link key={step.key} to={step.route} className="group">
                            <Card className="h-full flex items-start gap-4 hover:-translate-y-1 transition-transform">
                                <span className={cn(
                                    'step-badge shrink-0 mt-0.5',
                                    'group-hover:step-badge-active transition-all'
                                )}>
                                    {step.num}
                                </span>
                                <div>
                                    <div className="text-sm font-semibold text-txt-primary group-hover:text-accent-cyan transition-colors mb-1">
                                        {step.label}
                                    </div>
                                    <div className="text-xs text-txt-muted leading-relaxed">
                                        {step.desc}
                                    </div>
                                </div>
                            </Card>
                        </Link>
                    );
                })}
            </div>

            {/* Capabilities */}
            <h2 className="text-lg font-semibold text-txt-primary mb-4">Capabilities</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {CAPABILITIES.map((cap) => {
                    const Icon = cap.icon;
                    return (
                        <Card key={cap.title} className="text-center">
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-cyan/20 to-accent-indigo/20 flex items-center justify-center mx-auto mb-3">
                                <Icon size={22} className="text-accent-cyan" />
                            </div>
                            <div className="text-sm font-semibold text-txt-primary mb-1">{cap.title}</div>
                            <div className="text-xs text-txt-muted leading-relaxed">{cap.desc}</div>
                        </Card>
                    );
                })}
            </div>
        </ContentArea>
    );
}
