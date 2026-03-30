import React, { useState, useEffect } from 'react';
import { Archive, Download, Trash2, RefreshCw, Loader2, Clock, HardDrive } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Badge, StatCard } from '../components/ui';
import { cn, formatBytes } from '../lib/utils';
import toast from 'react-hot-toast';

const DEMO_CHECKPOINTS = [
    { id: 1, name: 'checkpoint_epoch_3_final', epoch: 3, step: 12000, loss: 1.234, size: 1_400_000_000, timestamp: '2025-01-15T14:30:00', best: true },
    { id: 2, name: 'checkpoint_epoch_2', epoch: 2, step: 8000, loss: 1.567, size: 1_400_000_000, timestamp: '2025-01-15T10:15:00', best: false },
    { id: 3, name: 'checkpoint_epoch_1', epoch: 1, step: 4000, loss: 2.345, size: 1_400_000_000, timestamp: '2025-01-14T22:45:00', best: false },
    { id: 4, name: 'checkpoint_warmup_500', epoch: 0, step: 500, loss: 4.123, size: 1_400_000_000, timestamp: '2025-01-14T20:00:00', best: false },
];

export default function CheckpointsPage() {
    const [checkpoints, setCheckpoints] = useState(DEMO_CHECKPOINTS);
    const [loading, setLoading] = useState(false);
    const [selected, setSelected] = useState(null);

    const refresh = async () => {
        setLoading(true);
        // Simulate API call
        await new Promise((r) => setTimeout(r, 500));
        setLoading(false);
        toast.success('Refreshed');
    };

    const handleDelete = (id) => {
        setCheckpoints((p) => p.filter((c) => c.id !== id));
        if (selected === id) setSelected(null);
        toast('Checkpoint removed');
    };

    const totalSize = checkpoints.reduce((a, c) => a + c.size, 0);
    const best = checkpoints.find((c) => c.best);

    return (
        <ContentArea title="Checkpoint Manager" subtitle="Browse, compare, and manage model checkpoints.">
            <div className="flex items-center justify-between mb-4">
                <div className="grid grid-cols-3 gap-3 flex-1 mr-4">
                    <StatCard icon={Archive} label="Checkpoints" value={checkpoints.length} />
                    <StatCard icon={HardDrive} label="Total Size" value={formatBytes(totalSize)} />
                    <StatCard icon={Clock} label="Best Loss" value={best ? best.loss.toFixed(3) : '—'} />
                </div>
                <button onClick={refresh} disabled={loading} className="btn-secondary">
                    {loading ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />}
                    Refresh
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* List */}
                <div className="lg:col-span-2 space-y-2">
                    {checkpoints.map((cp) => (
                        <button
                            key={cp.id}
                            onClick={() => setSelected(cp.id)}
                            className={cn(
                                'w-full flex items-center gap-4 p-4 rounded-xl border text-left transition-all',
                                selected === cp.id ? 'border-accent-cyan bg-accent-cyan/5' : 'border-ic-border bg-ic-card hover:border-accent-cyan/30'
                            )}
                        >
                            <div className="w-10 h-10 rounded-lg bg-ic-surface border border-ic-border flex items-center justify-center shrink-0">
                                <Archive size={18} className={cp.best ? 'text-accent-success' : 'text-txt-muted'} />
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                    <span className="text-sm font-semibold text-txt-primary truncate">{cp.name}</span>
                                    {cp.best && <Badge variant="success">Best</Badge>}
                                </div>
                                <div className="flex items-center gap-3 text-[11px] text-txt-muted mt-0.5">
                                    <span>Epoch {cp.epoch}</span>
                                    <span>Step {cp.step.toLocaleString()}</span>
                                    <span>Loss: {cp.loss.toFixed(3)}</span>
                                    <span>{formatBytes(cp.size)}</span>
                                </div>
                            </div>
                            <div className="flex items-center gap-2 shrink-0">
                                <button className="p-1.5 rounded-lg hover:bg-accent-cyan/10 text-txt-muted hover:text-accent-cyan transition-colors"
                                    onClick={(e) => { e.stopPropagation(); toast('Download started'); }}>
                                    <Download size={14} />
                                </button>
                                <button className="p-1.5 rounded-lg hover:bg-accent-danger/10 text-txt-muted hover:text-accent-danger transition-colors"
                                    onClick={(e) => { e.stopPropagation(); handleDelete(cp.id); }}>
                                    <Trash2 size={14} />
                                </button>
                            </div>
                        </button>
                    ))}
                    {checkpoints.length === 0 && (
                        <Card className="flex items-center justify-center h-40">
                            <div className="text-center text-txt-muted">
                                <Archive size={32} className="mx-auto mb-2 opacity-30" />
                                <p className="text-sm">No checkpoints found</p>
                            </div>
                        </Card>
                    )}
                </div>

                {/* Detail */}
                <div>
                    {selected ? (() => {
                        const cp = checkpoints.find((c) => c.id === selected);
                        if (!cp) return null;
                        return (
                            <Card className="animate-fade-in-up sticky top-4">
                                <CardTitle>Checkpoint Details</CardTitle>
                                <div className="mt-4 space-y-3">
                                    <div className="p-3 rounded-lg bg-ic-bg">
                                        <div className="text-[10px] text-txt-muted uppercase">Name</div>
                                        <div className="text-sm font-mono text-txt-primary mt-0.5">{cp.name}</div>
                                    </div>
                                    <div className="grid grid-cols-2 gap-3">
                                        <div className="p-3 rounded-lg bg-ic-bg">
                                            <div className="text-[10px] text-txt-muted uppercase">Epoch</div>
                                            <div className="text-sm font-mono text-txt-primary mt-0.5">{cp.epoch}</div>
                                        </div>
                                        <div className="p-3 rounded-lg bg-ic-bg">
                                            <div className="text-[10px] text-txt-muted uppercase">Step</div>
                                            <div className="text-sm font-mono text-txt-primary mt-0.5">{cp.step.toLocaleString()}</div>
                                        </div>
                                        <div className="p-3 rounded-lg bg-ic-bg">
                                            <div className="text-[10px] text-txt-muted uppercase">Loss</div>
                                            <div className="text-sm font-mono text-accent-cyan mt-0.5">{cp.loss.toFixed(4)}</div>
                                        </div>
                                        <div className="p-3 rounded-lg bg-ic-bg">
                                            <div className="text-[10px] text-txt-muted uppercase">Size</div>
                                            <div className="text-sm font-mono text-txt-primary mt-0.5">{formatBytes(cp.size)}</div>
                                        </div>
                                    </div>
                                    <div className="p-3 rounded-lg bg-ic-bg">
                                        <div className="text-[10px] text-txt-muted uppercase">Created</div>
                                        <div className="text-sm text-txt-primary mt-0.5">{new Date(cp.timestamp).toLocaleString()}</div>
                                    </div>
                                    <button className="btn-primary w-full justify-center" onClick={() => toast.success('Checkpoint loaded')}>
                                        Load Checkpoint
                                    </button>
                                </div>
                            </Card>
                        );
                    })() : (
                        <Card className="flex items-center justify-center h-64">
                            <div className="text-center text-txt-muted">
                                <Archive size={32} className="mx-auto mb-2 opacity-30" />
                                <p className="text-sm">Select a checkpoint</p>
                            </div>
                        </Card>
                    )}
                </div>
            </div>
        </ContentArea>
    );
}
