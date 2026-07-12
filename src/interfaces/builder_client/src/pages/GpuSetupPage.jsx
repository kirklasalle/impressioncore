import React, { useState } from 'react';
import { RefreshCw, Loader2, CheckCircle2, XCircle, Cpu, HardDrive, Thermometer, AlertTriangle } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Badge, ProgressBar, StatCard } from '../components/ui';
import { detectGpu } from '../lib/api';
import toast from 'react-hot-toast';

export default function GpuSetupPage() {
    const [info, setInfo] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const detect = async () => {
        setLoading(true);
        setError(null);
        try {
            const { data } = await detectGpu();
            if (data.gpu) {
                setInfo(data.gpu);
                toast.success(data.gpu.available ? 'GPU detected' : 'No CUDA GPU found — showing available info');
            } else {
                setError('Unexpected response from server');
                toast.error('Detection returned an unexpected format');
            }
        } catch (err) {
            setError(err?.response?.data?.error || err.message || 'Failed to reach server');
            toast.error('GPU detection failed');
        } finally {
            setLoading(false);
        }
    };

    const vramPct = info ? Math.round((info.vram_used / info.vram_total) * 100) : 0;
    const powerPct = info ? Math.round((info.power_draw / info.power_limit) * 100) : 0;

    return (
        <ContentArea title="GPU Setup" subtitle="Detect, verify, and optimize your GPU configuration.">
            <div className="flex justify-end mb-4">
                <button onClick={detect} disabled={loading} className="btn-primary">
                    {loading ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />}
                    Detect GPU
                </button>
            </div>

            {error && (
                <div className="flex items-center gap-2 mb-4 p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400 text-sm">
                    <AlertTriangle size={16} className="shrink-0" />
                    <span className="flex-1">{error}</span>
                    <button className="btn-secondary text-xs px-2 py-1" onClick={detect} disabled={loading}>Retry</button>
                </div>
            )}

            {!info && !error ? (
                <Card className="flex items-center justify-center h-64">
                    <div className="text-center text-txt-muted">
                        <Cpu size={48} className="mx-auto mb-3 opacity-30" />
                        <p className="text-sm">Click "Detect GPU" to scan hardware</p>
                    </div>
                </Card>
            ) : info ? (
                <div className="space-y-6 animate-fade-in-up">
                    {/* Header */}
                    <Card>
                        <div className="flex items-center gap-4">
                            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-accent-cyan to-accent-indigo flex items-center justify-center">
                                <Cpu size={28} className="text-white" />
                            </div>
                            <div>
                                <h2 className="text-lg font-bold text-txt-primary">{info.name}</h2>
                                <div className="flex gap-2 mt-1">
                                    <Badge variant="cyan">CUDA {info.cuda_version}</Badge>
                                    <Badge variant="info">Driver {info.driver_version}</Badge>
                                    <Badge>SM {info.compute_capability}</Badge>
                                </div>
                            </div>
                            <CheckCircle2 size={24} className="ml-auto text-accent-success" />
                        </div>
                    </Card>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        <StatCard icon={HardDrive} label="VRAM Total" value={`${(info.vram_total / 1024).toFixed(1)} GB`} />
                        <StatCard icon={HardDrive} label="VRAM Free" value={`${(info.vram_free / 1024).toFixed(1)} GB`} />
                        <StatCard icon={Thermometer} label="Temperature" value={`${info.temperature}°C`} />
                        <StatCard icon={Cpu} label="Utilization" value={`${info.utilization}%`} />
                    </div>

                    {/* VRAM + Power */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                        <Card>
                            <CardTitle>VRAM Usage</CardTitle>
                            <div className="mt-3">
                                <div className="flex justify-between text-sm mb-2">
                                    <span className="text-txt-muted">{info.vram_used} MB / {info.vram_total} MB</span>
                                    <span className="font-mono text-accent-cyan">{vramPct}%</span>
                                </div>
                                <ProgressBar value={vramPct} max={100} variant={vramPct > 90 ? 'danger' : vramPct > 70 ? 'warning' : 'success'} />
                            </div>
                            <div className="mt-4 text-xs text-txt-muted space-y-1">
                                <div>GPU Clock: <span className="text-txt-secondary font-mono">{info.gpu_clock} MHz</span></div>
                                <div>Memory Clock: <span className="text-txt-secondary font-mono">{info.memory_clock} MHz</span></div>
                            </div>
                        </Card>
                        <Card>
                            <CardTitle>Power Draw</CardTitle>
                            <div className="mt-3">
                                <div className="flex justify-between text-sm mb-2">
                                    <span className="text-txt-muted">{info.power_draw}W / {info.power_limit}W</span>
                                    <span className="font-mono text-accent-cyan">{powerPct}%</span>
                                </div>
                                <ProgressBar value={powerPct} max={100} variant={powerPct > 90 ? 'danger' : 'cyan'} />
                            </div>
                            <div className="mt-4 p-3 rounded-lg bg-ic-bg border border-ic-border">
                                <h4 className="text-xs font-semibold text-txt-primary mb-1">Optimization Tips</h4>
                                <ul className="text-[10px] text-txt-muted space-y-0.5">
                                    <li>• Use FP16/BF16 precision to halve VRAM</li>
                                    <li>• Enable gradient checkpointing for large models</li>
                                    <li>• Batch size 4 recommended for 4GB VRAM</li>
                                    <li>• Flash Attention reduces memory by ~40%</li>
                                </ul>
                            </div>
                        </Card>
                    </div>
                </div>
            ) : null}
        </ContentArea>
    );
}
