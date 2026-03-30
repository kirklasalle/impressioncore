import React, { useState } from 'react';
import { Compass, ChevronRight, CheckCircle2, Circle, Loader2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Badge } from '../components/ui';
import { PIPELINE_STEPS } from '../lib/constants';
import { cn } from '../lib/utils';

export default function WalkthroughPage() {
    const [currentStep, setCurrentStep] = useState(0);
    const [completed, setCompleted] = useState(new Set());

    const markDone = (idx) => {
        setCompleted((prev) => {
            const next = new Set(prev);
            next.add(idx);
            return next;
        });
        if (idx < PIPELINE_STEPS.length - 1) setCurrentStep(idx + 1);
    };

    return (
        <ContentArea title="Guided Walkthrough" subtitle="Step-by-step guide to building your B3 model.">
            {/* Progress bar */}
            <div className="flex items-center gap-1 mb-8">
                {PIPELINE_STEPS.map((step, i) => (
                    <React.Fragment key={step.key}>
                        <button
                            onClick={() => setCurrentStep(i)}
                            className={cn(
                                'w-8 h-8 rounded-full text-xs font-bold flex items-center justify-center transition-all',
                                completed.has(i)
                                    ? 'bg-accent-success text-white'
                                    : i === currentStep
                                        ? 'bg-accent-cyan text-white ring-2 ring-accent-cyan/40'
                                        : 'bg-ic-surface text-txt-muted border border-ic-border'
                            )}
                        >
                            {completed.has(i) ? <CheckCircle2 size={14} /> : step.num}
                        </button>
                        {i < PIPELINE_STEPS.length - 1 && (
                            <div className={cn(
                                'flex-1 h-0.5 rounded-full',
                                completed.has(i) ? 'bg-accent-success' : 'bg-ic-border'
                            )} />
                        )}
                    </React.Fragment>
                ))}
            </div>

            {/* Active Step Card */}
            {PIPELINE_STEPS.map((step, i) => (
                i === currentStep && (
                    <Card key={step.key} className="animate-fade-in-up">
                        <div className="flex items-start gap-4">
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-cyan to-accent-indigo flex items-center justify-center text-white font-bold text-lg shrink-0">
                                {step.num}
                            </div>
                            <div className="flex-1">
                                <div className="flex items-center gap-3">
                                    <h2 className="text-xl font-bold text-txt-primary">{step.label}</h2>
                                    {completed.has(i) && <Badge variant="success">Complete</Badge>}
                                </div>
                                <p className="text-sm text-txt-secondary mt-1">{step.desc}</p>

                                <div className="mt-6 p-4 rounded-xl bg-ic-surface border border-ic-border">
                                    <h3 className="text-sm font-semibold text-txt-primary mb-3">What you'll do:</h3>
                                    <ul className="space-y-2 text-sm text-txt-secondary">
                                        <li className="flex items-start gap-2">
                                            <Circle size={6} className="mt-1.5 text-accent-cyan shrink-0" />
                                            Configure settings for {step.label.toLowerCase()}
                                        </li>
                                        <li className="flex items-start gap-2">
                                            <Circle size={6} className="mt-1.5 text-accent-cyan shrink-0" />
                                            Review the configuration summary
                                        </li>
                                        <li className="flex items-start gap-2">
                                            <Circle size={6} className="mt-1.5 text-accent-cyan shrink-0" />
                                            Run validation checks and proceed
                                        </li>
                                    </ul>
                                </div>

                                <div className="flex items-center gap-3 mt-6">
                                    <Link to={step.route} className="btn-primary">
                                        Open {step.label} <ChevronRight size={16} />
                                    </Link>
                                    <button onClick={() => markDone(i)} className="btn-secondary">
                                        <CheckCircle2 size={16} /> Mark Complete
                                    </button>
                                </div>
                            </div>
                        </div>
                    </Card>
                )
            ))}

            {/* Step List */}
            <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-3">
                {PIPELINE_STEPS.map((step, i) => (
                    <button
                        key={step.key}
                        onClick={() => setCurrentStep(i)}
                        className={cn(
                            'p-3 rounded-xl border text-left flex items-center gap-3 transition-all',
                            i === currentStep ? 'border-accent-cyan bg-accent-cyan/5' : 'border-ic-border bg-ic-card hover:border-accent-cyan/30'
                        )}
                    >
                        <span className={cn(
                            'w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0',
                            completed.has(i) ? 'bg-accent-success text-white'
                                : i === currentStep ? 'bg-accent-cyan text-white'
                                    : 'bg-ic-surface text-txt-muted'
                        )}>
                            {completed.has(i) ? '✓' : step.num}
                        </span>
                        <div>
                            <div className="text-sm font-medium text-txt-primary">{step.label}</div>
                            <div className="text-[10px] text-txt-muted truncate">{step.icon} {step.desc.slice(0, 40)}...</div>
                        </div>
                    </button>
                ))}
            </div>
        </ContentArea>
    );
}
