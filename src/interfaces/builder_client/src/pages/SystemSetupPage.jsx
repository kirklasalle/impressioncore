import React, { useState } from 'react';
import { Monitor, CheckCircle2, XCircle, Loader2, Cpu, HardDrive, MemoryStick } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Badge, StatCard } from '../components/ui';
import { checkGpu, checkDependencies, checkConfig, checkData } from '../lib/api';
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
                                                ? (typeof result.data?.data === 'object' ? JSON.stringify(result.data.data).slice(0, 80) : 'Passed')
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

                {/* HW Requirements */}
                <Card>
                    <CardTitle>Minimum Requirements</CardTitle>
                    <div className="grid grid-cols-3 gap-4 mt-4">
                        <StatCard label="GPU VRAM" value="4 GB" icon={Cpu} />
                        <StatCard label="System RAM" value="16 GB" icon={MemoryStick} />
                        <StatCard label="Python" value="3.10+" icon={Monitor} />
                    </div>
                </Card>
            </div>
        </ContentArea>
    );
}
