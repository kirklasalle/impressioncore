import React, { useEffect, useMemo, useState } from 'react';
import { AlertTriangle, ChevronRight, CheckCircle2, Circle, HardDrive, RefreshCw, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';
import ContentArea from '../components/layout/ContentArea';
import { Card, Badge, StatCard, Input } from '../components/ui';
import { PIPELINE_STEPS } from '../lib/constants';
import { cn } from '../lib/utils';
import {
    getBuilderFeatures,
    getBuilderStorageStatus,
    runBuilderStorageRetention,
} from '../lib/api';
import useWalkthroughProgress from '../hooks/useWalkthroughProgress';

export default function WalkthroughPage() {
    const { currentStep, setCurrentStep, completed, markDone, resetProgress, allComplete } = useWalkthroughProgress();
    const [features, setFeatures] = useState(null);
    const [storage, setStorage] = useState(null);
    const [storageLoading, setStorageLoading] = useState(false);
    const [storageError, setStorageError] = useState(null);
    const [retentionResult, setRetentionResult] = useState(null);
    const [targetFreeGb, setTargetFreeGb] = useState(95);
    const [loading, setLoading] = useState(false);
    const [retentionBusy, setRetentionBusy] = useState(false);

    const functionCounts = useMemo(() => {
        if (!features?.functions) {
            return { total: 0, active: 0, stub: 0 };
        }
        const total = features.functions.length;
        const active = features.functions.filter((item) => item.status === 'active').length;
        const stub = features.functions.filter((item) => item.status === 'stub').length;
        return { total, active, stub };
    }, [features]);

    const loadStorageData = async () => {
        setStorageLoading(true);
        setStorageError(null);
        try {
            const storageRes = await getBuilderStorageStatus();
            setStorage(storageRes.data);
        } catch (err) {
            console.error('[Walkthrough] storage load failed', err);
            setStorageError(err?.code === 'ECONNABORTED' ? 'Storage scan timed out — F:/ drive has many files.' : 'Failed to load storage status.');
        } finally {
            setStorageLoading(false);
        }
    };

    const loadBuilderData = async () => {
        setLoading(true);
        try {
            const featuresRes = await getBuilderFeatures();
            setFeatures(featuresRes.data);
        } catch (err) {
            console.error('[Walkthrough] features load failed', err);
        } finally {
            setLoading(false);
        }
        void loadStorageData();
    };

    useEffect(() => {
        void loadBuilderData();
    }, []);

    // markDone provided by useWalkthroughProgress hook (persists to localStorage + backend)

    const runRetention = async (enforce = false) => {
        setRetentionBusy(true);
        try {
            const response = await runBuilderStorageRetention({
                target_free_gb: Number(targetFreeGb) || 95,
                enforce,
                preview_limit: 25,
            });
            setRetentionResult(response.data);
            const storageRes = await getBuilderStorageStatus();
            setStorage(storageRes.data);
        } catch (err) {
            console.error('[Walkthrough] retention failed', err);
        } finally {
            setRetentionBusy(false);
        }
    };

    return (
        <ContentArea title="Guided Walkthrough" subtitle="Complete Builder walkthrough with live F:/ management and full feature/function coverage.">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
                <StatCard label="Pipeline Steps" value={features?.pipeline?.length ?? PIPELINE_STEPS.length} />
                <StatCard label="Knowledge Features" value={features?.knowledge?.length ?? 0} />
                <StatCard label="Advanced Features" value={features?.advanced?.length ?? 0} />
                <StatCard label="API Functions" value={functionCounts.total} />
            </div>

            <Card className="mb-8">
                <div className="flex items-center justify-between gap-4 mb-4">
                    <div>
                        <h2 className="text-lg font-bold text-txt-primary flex items-center gap-2" title="Manage storage on the F:/ drive used by the Builder for training data, model weights, and checkpoints.">
                            <HardDrive size={18} className="text-accent-cyan" />
                            Builder F:/ Storage Control
                        </h2>
                        <p className="text-xs text-txt-muted mt-1" title="The Builder reads and writes to F:/data (datasets) and F:/models (weights, checkpoints, exports).">Tied directly into Builder APIs for `F:/data` and `F:/models` operations.</p>
                    </div>
                    <button className="btn-secondary" onClick={() => void loadStorageData()} disabled={storageLoading} title="Re-scan the F:/ drive to get the latest total, used, and free space values.">
                        <RefreshCw size={14} className={storageLoading ? 'animate-spin' : ''} /> Refresh
                    </button>
                </div>

                {storageError && (
                    <div className="flex items-center gap-2 mb-4 p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400 text-sm">
                        <AlertTriangle size={16} className="shrink-0" />
                        <span className="flex-1">{storageError}</span>
                        <button className="btn-secondary text-xs px-2 py-1" onClick={() => void loadStorageData()} disabled={storageLoading}>
                            Retry
                        </button>
                    </div>
                )}

                {storageLoading && !storage && (
                    <div className="flex items-center gap-2 mb-4 text-sm text-txt-muted">
                        <RefreshCw size={14} className="animate-spin text-accent-cyan" />
                        Scanning F:/ drive...
                    </div>
                )}

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                    <div title="Total capacity of the F:/ drive in gigabytes. This is the full physical or partition size.">
                        <StatCard label="Drive Total (GB)" value={storage?.drive?.total_gb ?? '—'} />
                    </div>
                    <div title="Space currently consumed on F:/ by datasets, models, checkpoints, logs, and other Builder artifacts.">
                        <StatCard label="Drive Used (GB)" value={storage?.drive?.used_gb ?? '—'} />
                    </div>
                    <div title="Available free space on F:/. If this drops below your target, run retention to reclaim space.">
                        <StatCard label="Drive Free (GB)" value={storage?.drive?.free_gb ?? '—'} />
                    </div>
                    <div title="PASS = F:/data and F:/models directories both exist and are accessible. CHECK = one or both are missing.">
                        <StatCard label="Contract" value={storage?.contract?.has_data && storage?.contract?.has_models ? 'PASS' : 'CHECK'} />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-end">
                    <div title="Set the minimum free space you want on F:/. Retention will remove old artifacts until this target is met.">
                        <Input
                            label="Target Free Space (GB)"
                            type="number"
                            min="10"
                            step="1"
                            value={targetFreeGb}
                            onChange={(event) => setTargetFreeGb(event.target.value)}
                        />
                    </div>
                    <button className="btn-secondary" disabled={retentionBusy} onClick={() => void runRetention(false)} title="Dry-run: shows which files would be deleted and how much space would be reclaimed — nothing is removed.">
                        <ShieldCheck size={14} /> Preview Retention
                    </button>
                    <button className="btn-primary" disabled={retentionBusy} onClick={() => void runRetention(true)} title="Permanently delete old checkpoints and artifacts on F:/ until target free space is reached. Not reversible.">
                        <ShieldCheck size={14} /> Enforce Retention
                    </button>
                </div>

                {retentionResult && (
                    <div className="mt-4 p-4 rounded-xl bg-ic-surface border border-ic-border">
                        <div className="flex flex-wrap items-center gap-2 mb-2">
                            <span title="dry-run = preview only, no files deleted. enforce = files were permanently removed.">
                                <Badge variant={retentionResult.mode === 'enforce' ? 'warning' : 'info'}>
                                    Mode: {retentionResult.mode}
                                </Badge>
                            </span>
                            <span title="Total gigabytes freed (or projected to be freed in dry-run mode) by the retention policy.">
                                <Badge variant="cyan">Reclaimed: {retentionResult.reclaimed_gb} GB</Badge>
                            </span>
                            <span title="Current free space on F:/ after retention ran. Compare with your target to verify the goal was met.">
                                <Badge variant="success">Free Now: {retentionResult.after?.free_gb} GB</Badge>
                            </span>
                        </div>
                        <p className="text-xs text-txt-muted" title="Shortfall = GB still needed. Candidates = files eligible for removal. Processed = files actually evaluated.">
                            Shortfall: {retentionResult.shortfall_gb} GB · Candidates: {retentionResult.plan_candidates} · Processed: {retentionResult.processed_candidates}
                        </p>
                    </div>
                )}
            </Card>

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
                                    {!completed.has(i) && (
                                        <button onClick={() => markDone(i)} className="btn-secondary">
                                            <CheckCircle2 size={16} /> Mark Complete
                                        </button>
                                    )}
                                </div>
                                {allComplete && (
                                    <div className="mt-4 p-4 rounded-xl bg-accent-success/10 border border-accent-success/30 flex items-center justify-between">
                                        <span className="text-sm font-medium text-accent-success">All steps complete!</span>
                                        <button onClick={resetProgress} className="btn-secondary text-xs">
                                            <RefreshCw size={14} /> Reset Walkthrough
                                        </button>
                                    </div>
                                )}
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
                            <div className="text-[10px] text-txt-muted truncate flex items-center gap-1">
                                <step.icon size={12} className="text-accent-cyan shrink-0" />
                                <span>{step.desc.slice(0, 40)}...</span>
                            </div>
                        </div>
                    </button>
                ))}
            </div>

            <div className="mt-8 grid grid-cols-1 xl:grid-cols-2 gap-4">
                <Card>
                    <h3 className="text-sm font-semibold text-txt-primary mb-3">Complete Feature Coverage</h3>
                    <div className="space-y-3 text-sm">
                        <div>
                            <div className="text-xs uppercase tracking-wide text-txt-muted mb-1">Pipeline</div>
                            <div className="flex flex-wrap gap-2">
                                {(features?.pipeline ?? []).map((item) => (
                                    <Link key={item.key} to={item.route} className="px-2 py-1 rounded bg-ic-surface border border-ic-border text-txt-secondary hover:text-txt-primary">
                                        {item.label}
                                    </Link>
                                ))}
                            </div>
                        </div>
                        <div>
                            <div className="text-xs uppercase tracking-wide text-txt-muted mb-1">Knowledge & AI</div>
                            <div className="flex flex-wrap gap-2">
                                {(features?.knowledge ?? []).map((item) => (
                                    <Link key={item.key} to={item.route} className="px-2 py-1 rounded bg-ic-surface border border-ic-border text-txt-secondary hover:text-txt-primary">
                                        {item.label}
                                    </Link>
                                ))}
                            </div>
                        </div>
                        <div>
                            <div className="text-xs uppercase tracking-wide text-txt-muted mb-1">Advanced</div>
                            <div className="flex flex-wrap gap-2">
                                {(features?.advanced ?? []).map((item) => (
                                    <Link key={item.key} to={item.route} className="px-2 py-1 rounded bg-ic-surface border border-ic-border text-txt-secondary hover:text-txt-primary">
                                        {item.label}
                                    </Link>
                                ))}
                            </div>
                        </div>
                    </div>
                </Card>

                <Card>
                    <h3 className="text-sm font-semibold text-txt-primary mb-3">Supported Functions (Backend)</h3>
                    <div className="max-h-[320px] overflow-auto space-y-2 pr-1">
                        {(features?.functions ?? []).map((fn) => (
                            <div key={`${fn.method}-${fn.path}`} className="p-2 rounded border border-ic-border bg-ic-surface text-xs">
                                <div className="flex items-center justify-between gap-2">
                                    <span className="font-mono text-accent-cyan">{fn.method} {fn.path}</span>
                                    <Badge variant={fn.status === 'active' ? 'success' : 'warning'}>{fn.status}</Badge>
                                </div>
                                <div className="text-txt-muted mt-1">{fn.name}</div>
                            </div>
                        ))}
                    </div>
                </Card>
            </div>
        </ContentArea>
    );
}
