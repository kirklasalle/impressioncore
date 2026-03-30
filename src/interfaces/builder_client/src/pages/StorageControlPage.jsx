import React, { useEffect, useMemo, useState } from 'react';
import { HardDrive, RefreshCw, ShieldCheck, Trash2 } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Badge, StatCard, Input } from '../components/ui';
import {
    getBuilderStorageStatus,
    runBuilderStorageRetention,
} from '../lib/api';

const PRESETS = {
    basic: {
        label: 'Basic',
        target_free_gb: 72,
        hf_cache_age_days: 45,
        processed_age_days: 60,
        keep_checkpoints_per_dir: 6,
    },
    strong: {
        label: 'Strong',
        target_free_gb: 95,
        hf_cache_age_days: 30,
        processed_age_days: 45,
        keep_checkpoints_per_dir: 4,
    },
    world_class: {
        label: 'World-Class',
        target_free_gb: 119,
        hf_cache_age_days: 21,
        processed_age_days: 30,
        keep_checkpoints_per_dir: 3,
    },
};

export default function StorageControlPage() {
    const [storage, setStorage] = useState(null);
    const [retention, setRetention] = useState(null);
    const [loading, setLoading] = useState(false);
    const [running, setRunning] = useState(false);
    const [preset, setPreset] = useState('strong');

    const [form, setForm] = useState(PRESETS.strong);

    const contractPass = useMemo(
        () => Boolean(storage?.contract?.has_data && storage?.contract?.has_models),
        [storage],
    );

    const loadStatus = async () => {
        setLoading(true);
        try {
            const response = await getBuilderStorageStatus();
            setStorage(response.data);
        } catch (error) {
            console.error('[StorageControl] status failed', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        void loadStatus();
    }, []);

    const applyPreset = (value) => {
        setPreset(value);
        setForm(PRESETS[value]);
    };

    const runRetention = async (enforce) => {
        setRunning(true);
        try {
            const response = await runBuilderStorageRetention({
                ...form,
                enforce,
                preview_limit: 30,
            });
            setRetention(response.data);
            await loadStatus();
        } catch (error) {
            console.error('[StorageControl] retention failed', error);
        } finally {
            setRunning(false);
        }
    };

    const updateField = (key, value) => {
        setForm((prev) => ({ ...prev, [key]: Number(value) }));
    };

    return (
        <ContentArea
            title="Storage Control"
            subtitle="World-class F:/ data + model governance integrated directly into Builder operations."
        >
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
                <StatCard label="Total (GB)" value={storage?.drive?.total_gb ?? '—'} icon={HardDrive} />
                <StatCard label="Used (GB)" value={storage?.drive?.used_gb ?? '—'} icon={Trash2} />
                <StatCard label="Free (GB)" value={storage?.drive?.free_gb ?? '—'} icon={ShieldCheck} />
                <StatCard label="Contract" value={contractPass ? 'PASS' : 'CHECK'} icon={ShieldCheck} />
            </div>

            <Card className="mb-6">
                <div className="flex items-center justify-between gap-3 mb-4">
                    <CardTitle icon={HardDrive}>F:/ Contract + Retention Policies</CardTitle>
                    <button className="btn-secondary" onClick={() => void loadStatus()} disabled={loading}>
                        <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
                    </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                    {Object.entries(PRESETS).map(([key, value]) => (
                        <button
                            key={key}
                            onClick={() => applyPreset(key)}
                            className={`p-3 rounded-xl border text-left transition-all ${preset === key
                                ? 'border-accent-cyan bg-accent-cyan/5'
                                : 'border-ic-border bg-ic-surface hover:border-accent-cyan/40'
                                }`}
                        >
                            <div className="text-sm font-semibold text-txt-primary">{value.label}</div>
                            <div className="text-xs text-txt-muted mt-1">Target Free: {value.target_free_gb} GB</div>
                        </button>
                    ))}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-4">
                    <Input
                        label="Target Free (GB)"
                        type="number"
                        value={form.target_free_gb}
                        onChange={(event) => updateField('target_free_gb', event.target.value)}
                    />
                    <Input
                        label="HF Cache Age (days)"
                        type="number"
                        value={form.hf_cache_age_days}
                        onChange={(event) => updateField('hf_cache_age_days', event.target.value)}
                    />
                    <Input
                        label="Processed Age (days)"
                        type="number"
                        value={form.processed_age_days}
                        onChange={(event) => updateField('processed_age_days', event.target.value)}
                    />
                    <Input
                        label="Keep Checkpoints/Dir"
                        type="number"
                        value={form.keep_checkpoints_per_dir}
                        onChange={(event) => updateField('keep_checkpoints_per_dir', event.target.value)}
                    />
                </div>

                <div className="flex flex-wrap gap-3">
                    <button className="btn-secondary" disabled={running} onClick={() => void runRetention(false)}>
                        <ShieldCheck size={14} /> Preview Cleanup
                    </button>
                    <button className="btn-primary" disabled={running} onClick={() => void runRetention(true)}>
                        <Trash2 size={14} /> Enforce Cleanup
                    </button>
                </div>

                {retention && (
                    <div className="mt-4 p-4 rounded-xl bg-ic-surface border border-ic-border">
                        <div className="flex flex-wrap items-center gap-2 mb-2">
                            <Badge variant={retention.mode === 'enforce' ? 'warning' : 'info'}>
                                Mode: {retention.mode}
                            </Badge>
                            <Badge variant="cyan">Shortfall: {retention.shortfall_gb} GB</Badge>
                            <Badge variant="success">Reclaimed: {retention.reclaimed_gb} GB</Badge>
                            <Badge variant="success">Free Now: {retention.after?.free_gb} GB</Badge>
                        </div>
                        <div className="text-xs text-txt-muted">
                            Candidates: {retention.plan_candidates} · Processed: {retention.processed_candidates} · Reclaimable: {retention.plan_reclaimable_gb} GB
                        </div>
                    </div>
                )}
            </Card>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                <Card>
                    <CardTitle>F:/data Top Directories</CardTitle>
                    <div className="space-y-2 mt-3 max-h-[260px] overflow-auto pr-1">
                        {(storage?.data?.subdirectories ?? []).map((item) => (
                            <div key={item.name} className="flex items-center justify-between text-xs p-2 rounded bg-ic-surface border border-ic-border">
                                <span className="text-txt-secondary">{item.name}</span>
                                <span className="font-mono text-accent-cyan">{item.size_gb} GB</span>
                            </div>
                        ))}
                    </div>
                </Card>

                <Card>
                    <CardTitle>F:/models Top Directories</CardTitle>
                    <div className="space-y-2 mt-3 max-h-[260px] overflow-auto pr-1">
                        {(storage?.models?.subdirectories ?? []).map((item) => (
                            <div key={item.name} className="flex items-center justify-between text-xs p-2 rounded bg-ic-surface border border-ic-border">
                                <span className="text-txt-secondary">{item.name}</span>
                                <span className="font-mono text-accent-cyan">{item.size_gb} GB</span>
                            </div>
                        ))}
                    </div>
                </Card>
            </div>
        </ContentArea>
    );
}
