import React, { useState, useEffect } from 'react';
import { Monitor, CheckCircle2, XCircle, Loader2, Cpu, HardDrive, MemoryStick } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Badge, StatCard } from '../components/ui';
import { checkGpu, checkDependencies, checkConfig, checkData, getSystemHardware } from '../lib/api';
import toast from 'react-hot-toast';

const CHECKS = [
    { key: 'gpu', label: 'GPU / CUDA', fn: checkGpu, icon: Cpu },
    { key: 'deps', label: 'Dependencies', fn: checkDependencies, icon: HardDrive },
    { key: 'conf', label: 'Configuration', fn: checkConfig, icon: Monitor },
    { key: 'data', label: 'Training Data', fn: checkData, icon: MemoryStick },
];

export default function SystemSetupPage() {
    const [results, setResults] = useState({});
    const [running, setRunning] = useState(null);
    const [hwInfo, setHwInfo] = useState(null);

    useEffect(() => {
        getSystemHardware()
            .then(({ data }) => setHwInfo(data?.hardware ?? null))
            .catch(() => setHwInfo(null));
    }, []);

    const runCheck = async (check) => {
        setRunning(check.key);
        try {
            const { data } = await check.fn();
            setResults((prev) => ({ ...prev, [check.key]: { ok: true, data } }));
            toast.success(`${check.label}: passed`);
        } catch (err) {
            setResults((prev) => ({ ...prev, [check.key]: { ok: false, error: err.message } }));
            toast.error(`${check.label}: failed`);
        } finally {
            setRunning(null);
        }
    };

    const runAll = async () => {
        for (const check of CHECKS) {
            await runCheck(check);
        }
    };

    return (
        <ContentArea title="System Setup" subtitle="Validate hardware, dependencies, and environment before building.">
            <div className="max-w-3xl space-y-6">
                <div className="flex items-center gap-3 mb-2">
                    <button onClick={runAll} className="btn-primary" disabled={running !== null}>
                        {running ? <Loader2 size={16} className="animate-spin" /> : <Monitor size={16} />}
                        Run All Checks
                    </button>
                </div>

                {CHECKS.map((check) => {
                    const Icon = check.icon;
                    const result = results[check.key];
                    const isRunning = running === check.key;
                    return (
                        <Card key={check.key} className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-lg bg-ic-surface flex items-center justify-center">
                                    <Icon size={18} className="text-accent-cyan" />
                                </div>
                                <div>
                                    <div className="text-sm font-semibold text-txt-primary">{check.label}</div>
                                    {result && (
                                        <div className="text-xs text-txt-muted mt-0.5">
                                            {result.ok
                                                ? (check.key === 'gpu' && result.data?.data?.gpu
                                                    ? `${result.data.data.gpu.device_name} — ${result.data.data.gpu.vram_total} VRAM, CUDA ${result.data.data.gpu.cuda_version}`
                                                    : (typeof result.data?.data === 'object' ? JSON.stringify(result.data.data).slice(0, 80) : 'Passed'))
                                                : result.error}
                                        </div>
                                    )}
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                {result && (
                                    result.ok
                                        ? <Badge variant="success"><CheckCircle2 size={12} /> Pass</Badge>
                                        : <Badge variant="danger"><XCircle size={12} /> Fail</Badge>
                                )}
                                <button
                                    onClick={() => runCheck(check)}
                                    disabled={isRunning}
                                    className="btn-secondary text-xs px-3 py-1.5"
                                >
                                    {isRunning ? <Loader2 size={14} className="animate-spin" /> : 'Run'}
                                </button>
                            </div>
                        </Card>
                    );
                })}

                {/* Detected Hardware */}
                <Card>
                    <CardTitle>Detected Hardware</CardTitle>
                    <div className="grid grid-cols-3 gap-4 mt-4">
                        <StatCard label="GPU VRAM" value={hwInfo ? `${hwInfo.gpu.vram_total_gb} GB` : '—'} icon={Cpu} />
                        <StatCard label="System RAM" value={hwInfo ? `${hwInfo.ram.total_gb} GB` : '—'} icon={MemoryStick} />
                        <StatCard label="Python" value={hwInfo ? hwInfo.python : '—'} icon={Monitor} />
                    </div>
                    {hwInfo?.gpu?.name && hwInfo.gpu.name !== 'N/A' && (
                        <div className="text-xs text-txt-muted mt-3 text-center">
                            {hwInfo.gpu.name} &middot; CUDA {hwInfo.gpu.cuda_version} &middot; {hwInfo.cpu.cores} CPU cores
                        </div>
                    )}
                </Card>

                {/* HW Minimum Requirements */}
                <Card>
                    <CardTitle>Minimum Requirements</CardTitle>
                    <div className="grid grid-cols-3 gap-4 mt-4">
                        <div className="stat-card relative">
                            <Cpu size={14} className="text-accent-cyan mx-auto mb-1.5" />
                            <div className="text-lg font-bold font-mono text-txt-primary">4 GB</div>
                            <div className="text-[10px] uppercase tracking-wider text-txt-muted mt-0.5">GPU VRAM</div>
                            {hwInfo && (
                                <div className="absolute top-1.5 right-1.5">
                                    {hwInfo.gpu.vram_total_gb >= 4
                                        ? <CheckCircle2 size={14} className="text-accent-success" />
                                        : <XCircle size={14} className="text-accent-danger" />}
                                </div>
                            )}
                        </div>
                        <div className="stat-card relative">
                            <MemoryStick size={14} className="text-accent-cyan mx-auto mb-1.5" />
                            <div className="text-lg font-bold font-mono text-txt-primary">16 GB</div>
                            <div className="text-[10px] uppercase tracking-wider text-txt-muted mt-0.5">System RAM</div>
                            {hwInfo && (
                                <div className="absolute top-1.5 right-1.5">
                                    {hwInfo.ram.total_gb >= 16
                                        ? <CheckCircle2 size={14} className="text-accent-success" />
                                        : <XCircle size={14} className="text-accent-danger" />}
                                </div>
                            )}
                        </div>
                        <div className="stat-card relative">
                            <Monitor size={14} className="text-accent-cyan mx-auto mb-1.5" />
                            <div className="text-lg font-bold font-mono text-txt-primary">3.10+</div>
                            <div className="text-[10px] uppercase tracking-wider text-txt-muted mt-0.5">Python</div>
                            {hwInfo && (
                                <div className="absolute top-1.5 right-1.5">
                                    {parseFloat(hwInfo.python) >= 3.10
                                        ? <CheckCircle2 size={14} className="text-accent-success" />
                                        : <XCircle size={14} className="text-accent-danger" />}
                                </div>
                            )}
                        </div>
                    </div>
                </Card>
            </div>
        </ContentArea>
    );
}
