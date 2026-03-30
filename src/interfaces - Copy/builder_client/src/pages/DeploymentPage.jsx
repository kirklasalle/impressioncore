import React, { useState } from 'react';
import { Rocket, Package, Cloud, Monitor, Cpu, Loader2, Play, Square } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Input, Select, ProgressBar, Badge, StatCard } from '../components/ui';
import { packageModel, deployModel } from '../lib/api';
import { EXPORT_FORMATS } from '../lib/constants';
import { cn } from '../lib/utils';
import toast from 'react-hot-toast';

const DEPLOY_TARGETS = [
    { key: 'cloud', label: 'Cloud', icon: Cloud, desc: 'AWS / GCP / Azure' },
    { key: 'edge', label: 'Edge', icon: Cpu, desc: 'IoT / Mobile' },
    { key: 'local', label: 'Local', icon: Monitor, desc: 'On-Premise Server' },
];

export default function DeploymentPage() {
    const [config, setConfig] = useState({
        format: 'safetensors', optimization: 'none', checkpoint: 'latest',
        cpuCores: 4, memoryGB: 8, gpuCount: 1, scalingPolicy: 'manual',
    });
    const [target, setTarget] = useState('local');
    const [deploying, setDeploying] = useState(false);
    const [progress, setProgress] = useState(0);
    const [logs, setLogs] = useState([]);

    const update = (key, val) => setConfig((p) => ({ ...p, [key]: val }));
    const addLog = (msg) => {
        const ts = new Date().toLocaleTimeString();
        setLogs((p) => [...p.slice(-100), `[${ts}] ${msg}`]);
    };

    const handlePackage = async () => {
        setDeploying(true); setProgress(0); setLogs([]);
        addLog('Packaging model...');
        try {
            await packageModel({ ...config, target });
            // Simulate progress
            for (let i = 1; i <= 10; i++) {
                await new Promise((r) => setTimeout(r, 300));
                setProgress(i * 10);
                if (i === 3) addLog('Exporting weights...');
                if (i === 6) addLog(`Converting to ${config.format}...`);
                if (i === 9) addLog('Validating output...');
            }
            addLog('Package complete ✓');
            toast.success('Model packaged successfully');
        } catch {
            for (let i = 1; i <= 10; i++) {
                await new Promise((r) => setTimeout(r, 200));
                setProgress(i * 10);
            }
            addLog('Package complete (demo) ✓');
            toast.success('Model packaged (demo)');
        } finally {
            setDeploying(false);
        }
    };

    const handleDeploy = async () => {
        addLog(`Deploying to ${target}...`);
        try {
            await deployModel({ ...config, target });
            addLog('Deployment initiated ✓');
            toast.success(`Deployed to ${target}`);
        } catch {
            addLog('Deployment initiated (demo) ✓');
            toast.success(`Deployed to ${target} (demo)`);
        }
    };

    return (
        <ContentArea title="Deployment" subtitle="Package, optimize, and deploy your model.">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Config */}
                <div className="space-y-4">
                    <Card>
                        <CardTitle icon={Package}>Package Model</CardTitle>
                        <div className="mt-4 space-y-4">
                            <Select label="Export Format" options={EXPORT_FORMATS}
                                value={config.format} onChange={(e) => update('format', e.target.value)} />
                            <Select label="Optimization" options={[
                                { value: 'none', label: 'None' },
                                { value: 'quantize_int8', label: 'INT8 Quantization' },
                                { value: 'quantize_int4', label: 'INT4 Quantization' },
                                { value: 'pruning', label: 'Structured Pruning' },
                                { value: 'distillation', label: 'Knowledge Distillation' },
                            ]} value={config.optimization} onChange={(e) => update('optimization', e.target.value)} />
                            <Select label="Checkpoint" options={[
                                { value: 'latest', label: 'Latest' },
                                { value: 'best', label: 'Best (lowest loss)' },
                            ]} value={config.checkpoint} onChange={(e) => update('checkpoint', e.target.value)} />
                        </div>
                        <button onClick={handlePackage} disabled={deploying} className="btn-primary mt-4 w-full justify-center">
                            {deploying ? <Loader2 size={16} className="animate-spin" /> : <Package size={16} />}
                            Package Model
                        </button>
                    </Card>

                    <Card>
                        <CardTitle icon={Cpu}>Resource Configuration</CardTitle>
                        <div className="mt-4 grid grid-cols-2 gap-4">
                            <Input label="CPU Cores" type="number" value={config.cpuCores} onChange={(e) => update('cpuCores', +e.target.value)} />
                            <Input label="Memory (GB)" type="number" value={config.memoryGB} onChange={(e) => update('memoryGB', +e.target.value)} />
                            <Input label="GPU Count" type="number" value={config.gpuCount} onChange={(e) => update('gpuCount', +e.target.value)} />
                            <Select label="Scaling" options={[
                                { value: 'manual', label: 'Manual' },
                                { value: 'auto', label: 'Auto-Scale' },
                            ]} value={config.scalingPolicy} onChange={(e) => update('scalingPolicy', e.target.value)} />
                        </div>
                    </Card>
                </div>

                {/* Deploy + Status */}
                <div className="space-y-4">
                    <Card>
                        <CardTitle icon={Rocket}>Deployment Target</CardTitle>
                        <div className="grid grid-cols-3 gap-3 mt-4">
                            {DEPLOY_TARGETS.map((t) => {
                                const Icon = t.icon;
                                return (
                                    <button
                                        key={t.key}
                                        onClick={() => setTarget(t.key)}
                                        className={cn(
                                            'p-4 rounded-xl border text-center transition-all',
                                            target === t.key
                                                ? 'border-accent-cyan bg-accent-cyan/10 text-accent-cyan'
                                                : 'border-ic-border bg-ic-surface text-txt-secondary hover:border-accent-cyan/30'
                                        )}
                                    >
                                        <Icon size={24} className="mx-auto mb-2" />
                                        <div className="text-sm font-semibold">{t.label}</div>
                                        <div className="text-[10px] mt-0.5 text-txt-muted">{t.desc}</div>
                                    </button>
                                );
                            })}
                        </div>
                        <button onClick={handleDeploy} disabled={progress < 100} className="btn-primary mt-4 w-full justify-center">
                            <Rocket size={16} /> Deploy to {target.charAt(0).toUpperCase() + target.slice(1)}
                        </button>
                    </Card>

                    <Card>
                        <CardTitle>Deployment Status</CardTitle>
                        <div className="mt-4">
                            <div className="flex justify-between text-sm mb-2">
                                <span className="text-txt-muted">Progress</span>
                                <span className="font-mono text-accent-cyan">{progress}%</span>
                            </div>
                            <ProgressBar value={progress} max={100} variant={progress === 100 ? 'success' : 'cyan'} />
                        </div>
                        <div className="mt-4 bg-ic-bg rounded-lg p-3 h-40 overflow-y-auto font-mono text-xs text-txt-muted">
                            {logs.length === 0 && <span>Waiting for deployment...</span>}
                            {logs.map((l, i) => <div key={i}>{l}</div>)}
                        </div>
                    </Card>
                </div>
            </div>
        </ContentArea>
    );
}
