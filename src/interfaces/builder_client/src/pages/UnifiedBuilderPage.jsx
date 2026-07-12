import React from 'react';
import { Layers, ChevronRight, ChevronLeft, CheckCircle2 } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Badge, ProgressBar } from '../components/ui';
import { PIPELINE_STEPS } from '../lib/constants';
import { cn } from '../lib/utils';
import { Link } from 'react-router-dom';
import useWalkthroughProgress from '../hooks/useWalkthroughProgress';

export default function UnifiedBuilderPage() {
    const { currentStep: activeStep, setCurrentStep: setActiveStep, completed, markDone: hookMarkDone, resetProgress, allComplete } = useWalkthroughProgress();

    const completedCount = completed.size;
    const progress = Math.round((completedCount / PIPELINE_STEPS.length) * 100);
    const step = PIPELINE_STEPS[activeStep];

    const markDone = () => hookMarkDone(activeStep);

    return (
        <ContentArea title="Unified Builder" subtitle="End-to-end pipeline in a single view.">
            {/* Progress */}
            <Card className="mb-6">
                <div className="flex items-center justify-between mb-3">
                    <span className="text-sm text-txt-secondary">Overall Progress</span>
                    <span className="text-sm font-mono text-accent-cyan">{completedCount}/{PIPELINE_STEPS.length} steps</span>
                </div>
                <ProgressBar value={progress} max={100} variant={progress === 100 ? 'success' : 'cyan'} />
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Step List — 1 col */}
                <div className="space-y-2">
                    {PIPELINE_STEPS.map((s, i) => (
                        <button
                            key={s.key}
                            onClick={() => setActiveStep(i)}
                            className={cn(
                                'w-full flex items-center gap-3 p-3 rounded-xl border text-left transition-all',
                                i === activeStep ? 'border-accent-cyan bg-accent-cyan/5' : 'border-ic-border bg-ic-card hover:border-accent-cyan/30'
                            )}
                        >
                            <span className={cn(
                                'w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0',
                                completed.has(i) ? 'bg-accent-success text-white'
                                    : i === activeStep ? 'bg-accent-cyan text-white'
                                        : 'bg-ic-surface text-txt-muted'
                            )}>
                                {completed.has(i) ? '✓' : s.num}
                            </span>
                            <div className="flex-1 min-w-0">
                                <div className="text-sm font-medium text-txt-primary truncate">{s.label}</div>
                            </div>
                            {i === activeStep && <ChevronRight size={14} className="text-accent-cyan" />}
                        </button>
                    ))}
                </div>

                {/* Active Step Detail — 3 cols */}
                <div className="lg:col-span-3">
                    <Card className="animate-fade-in-up">
                        <div className="flex items-start gap-4">
                            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-accent-cyan to-accent-indigo flex items-center justify-center text-white text-xl font-bold shrink-0">
                                {step.num}
                            </div>
                            <div className="flex-1">
                                <div className="flex items-center gap-3">
                                    <h2 className="text-xl font-bold text-txt-primary">{step.label}</h2>
                                    {completed.has(activeStep) && <Badge variant="success">Complete</Badge>}
                                </div>
                                <p className="text-sm text-txt-secondary mt-1">{step.desc}</p>

                                <div className="mt-6 p-5 rounded-xl bg-ic-bg border border-ic-border">
                                    <h3 className="text-sm font-semibold text-txt-primary mb-3">Quick Actions</h3>
                                    <div className="flex flex-wrap gap-3">
                                        <Link to={step.route} className="btn-primary text-sm">
                                            Open Full Page <ChevronRight size={14} />
                                        </Link>
                                        {!completed.has(activeStep) && (
                                            <button onClick={markDone} className="btn-secondary text-sm">
                                                <CheckCircle2 size={14} /> Mark Complete
                                            </button>
                                        )}
                                    </div>
                                </div>

                                <div className="flex items-center gap-3 mt-6">
                                    <button
                                        onClick={() => setActiveStep(Math.max(0, activeStep - 1))}
                                        disabled={activeStep === 0}
                                        className="btn-secondary text-sm"
                                    >
                                        <ChevronLeft size={14} /> Previous
                                    </button>
                                    <button
                                        onClick={() => setActiveStep(Math.min(PIPELINE_STEPS.length - 1, activeStep + 1))}
                                        disabled={activeStep === PIPELINE_STEPS.length - 1}
                                        className="btn-secondary text-sm"
                                    >
                                        Next <ChevronRight size={14} />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </Card>
                </div>
            </div>
            {allComplete && (
                <Card className="mt-6">
                    <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-accent-success">All pipeline steps complete!</span>
                        <button onClick={resetProgress} className="btn-secondary text-xs">
                            Reset Walkthrough
                        </button>
                    </div>
                </Card>
            )}
        </ContentArea>
    );
}
