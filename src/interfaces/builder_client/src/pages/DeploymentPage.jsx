import React, { useState } from 'react';
import { Rocket, Package, Cloud, Monitor, Cpu, Loader2, Play, Square, FolderOpen, CheckCircle2, FileText, Settings, X, ArrowUp, HardDrive, Folder, Lock } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Input, Select, ProgressBar, Badge, StatCard } from '../components/ui';
import { packageModel, deployModel, browseDataDir } from '../lib/api';
import { EXPORT_FORMATS } from '../lib/constants';
import { cn } from '../lib/utils';
import toast from 'react-hot-toast';

const DEPLOY_TARGETS = [
    { key: 'cloud', label: 'Cloud', icon: Cloud, desc: 'AWS / GCP / Azure', tooltip: 'Deploy to cloud infrastructure (AWS, GCP, Azure). Generates a Dockerfile and Flask serving script for containerized deployment.' },
    { key: 'edge', label: 'Edge', icon: Cpu, desc: 'IoT / Mobile', tooltip: 'Deploy to edge devices (IoT, mobile). Produces a lightweight container bundle optimized for resource-constrained environments.' },
    { key: 'local', label: 'Local', icon: Monitor, desc: 'On-Premise Server', tooltip: 'Deploy to a local on-premise server. Creates a ready-to-run Python serve script in the production_packages directory.' },
];

const DEPLOY_PATHS = {
    cloud: 'production_packages/cloud_deploy_{timestamp}/',
    edge: 'production_packages/edge_deploy_{timestamp}/',
    local: 'production_packages/local_deploy/',
};

export default function DeploymentPage() {
    const [config, setConfig] = useState({
        format: 'safetensors', optimization: 'none', checkpoint: 'latest',
        cpuCores: 4, memoryGB: 8, gpuCount: 1, scalingPolicy: 'manual',
    });
    const [target, setTarget] = useState('local');
    const [deploying, setDeploying] = useState(false);
    const [progress, setProgress] = useState(0);
    const [logs, setLogs] = useState([]);
    const [packageResult, setPackageResult] = useState(null);
    const [deployResult, setDeployResult] = useState(null);
    const [editingTarget, setEditingTarget] = useState(null);
    const [targetConfig, setTargetConfig] = useState({
        cloud: { provider: 'aws', region: 'us-east-1', instanceType: 'g4dn.xlarge' },
        edge: { device: 'mobile', runtime: 'onnx', memoryLimitMB: 512 },
        local: { outputPath: 'production_packages/local_deploy/' },
    });
    const [showBrowser, setShowBrowser] = useState(false);
    const [browserItems, setBrowserItems] = useState([]);
    const [browserPath, setBrowserPath] = useState('');
    const [browserParent, setBrowserParent] = useState(null);
    const [browserLoading, setBrowserLoading] = useState(false);

    const update = (key, val) => setConfig((p) => ({ ...p, [key]: val }));
    const addLog = (msg) => {
        const ts = new Date().toLocaleTimeString();
        setLogs((p) => [...p.slice(-100), `[${ts}] ${msg}`]);
    };

    const updateTargetConfig = (tgt, key, val) =>
        setTargetConfig((p) => ({ ...p, [tgt]: { ...p[tgt], [key]: val } }));

    const formatBytes = (bytes) => {
        if (!bytes || bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
    };

    const openBrowser = async (path) => {
        setBrowserLoading(true);
        try {
            const { data } = await browseDataDir(path || '');
            setBrowserItems(data?.items || []);
            setBrowserPath(data?.path || '');
            setBrowserParent(data?.parent ?? null);
            setShowBrowser(true);
        } catch (err) {
            toast.error(err.response?.data?.error || 'Failed to browse directory');
        } finally {
            setBrowserLoading(false);
        }
    };

    const selectBrowserFolder = (path) => {
        updateTargetConfig('local', 'outputPath', path);
        setShowBrowser(false);
    };

    const handlePackage = async () => {
        setDeploying(true); setProgress(0); setLogs([]); setPackageResult(null); setDeployResult(null);
        addLog('Packaging model...');
        setProgress(10);
        try {
            const { data } = await packageModel({ ...config, target, targetConfig: targetConfig[target] });
            setProgress(50);
            if (data.success && data.package) {
                const pkg = data.package;
                addLog(`Exported weights in ${pkg.format} format`);
                setProgress(70);
                addLog(`Optimization: ${config.optimization === 'none' ? 'None' : config.optimization}`);
                setProgress(85);
                addLog(`Package: ${pkg.name} (${pkg.size_mb} MB, ${pkg.parameters?.toLocaleString()} params)`);
                addLog(`Files: ${pkg.files.join(', ')}`);
                addLog(`Output path: ${pkg.path}`);
                setProgress(100);
                addLog('Package complete \u2713');
                setPackageResult(pkg);
                toast.success(`Model packaged: ${pkg.name} (${pkg.size_mb} MB)`);
            } else {
                addLog(`Error: ${data.error || 'Unknown packaging error'}`);
                setProgress(0);
                toast.error(data.error || 'Packaging failed');
            }
        } catch (err) {
            const msg = err?.response?.data?.error || err.message || 'Packaging failed';
            addLog(`Error: ${msg}`);
            setProgress(0);
            toast.error(msg);
        } finally {
            setDeploying(false);
        }
    };

    const handleDeploy = async () => {
        addLog(`Deploying to ${target}...`);
        try {
            const { data } = await deployModel({ ...config, target, targetConfig: targetConfig[target] });
            if (data.success && data.deployment) {
                const dep = data.deployment;
                addLog(`Target: ${data.target}`);
                addLog(`Package: ${dep.package}`);
                addLog(`Format: ${dep.format} | Params: ${dep.parameters?.toLocaleString()}`);
                if (dep.serve_script) addLog(`Serve script: ${dep.serve_script}`);
                if (dep.deploy_dir) addLog(`Deploy dir: ${dep.deploy_dir}`);
                if (dep.bundle_dir) addLog(`Bundle dir: ${dep.bundle_dir}`);
                if (dep.dockerfile) addLog(`Dockerfile: ${dep.dockerfile}`);
                addLog('Deployment complete \u2713');
                setDeployResult(dep);
                toast.success(data.message || `Deployed to ${target}`);
            } else {
                addLog(`Error: ${data.error || 'Deployment failed'}`);
                toast.error(data.error || 'Deployment failed');
            }
        } catch (err) {
            const msg = err?.response?.data?.error || err.message || 'Deployment failed';
            addLog(`Error: ${msg}`);
            toast.error(msg);
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
                            <div title="Choose the output weight format. SafeTensors is recommended for safety and speed. ONNX enables cross-platform inference.">
                                <Select label="Export Format" options={EXPORT_FORMATS}
                                    value={config.format} onChange={(e) => update('format', e.target.value)} />
                            </div>
                            <div title="Apply post-training optimization. INT8/INT4 reduce model size and VRAM. Pruning removes redundant weights.">
                                <Select label="Optimization" options={[
                                    { value: 'none', label: 'None' },
                                    { value: 'quantize_int8', label: 'INT8 Quantization' },
                                    { value: 'quantize_int4', label: 'INT4 Quantization' },
                                    { value: 'pruning', label: 'Structured Pruning' },
                                    { value: 'distillation', label: 'Knowledge Distillation' },
                                ]} value={config.optimization} onChange={(e) => update('optimization', e.target.value)} />
                            </div>
                            <div title="Select which checkpoint to package. 'Latest' uses the most recent save. 'Best' picks the checkpoint with lowest loss.">
                                <Select label="Checkpoint" options={[
                                    { value: 'latest', label: 'Latest' },
                                    { value: 'best', label: 'Best (lowest loss)' },
                                ]} value={config.checkpoint} onChange={(e) => update('checkpoint', e.target.value)} />
                            </div>
                        </div>
                        <button
                            onClick={handlePackage}
                            disabled={deploying}
                            className="btn-primary mt-4 w-full justify-center"
                            title="Export model weights to the selected format with optimization applied. Output is saved to production_packages/ directory."
                        >
                            {deploying ? <Loader2 size={16} className="animate-spin" /> : <Package size={16} />}
                            Package Model
                        </button>
                        {packageResult && (
                            <div className="mt-3 bg-ic-surface rounded-lg px-3 py-2 text-[11px] font-mono text-txt-muted space-y-0.5">
                                <div className="flex items-center gap-1.5 text-accent-success"><CheckCircle2 size={11} /> Packaged</div>
                                <div>Name: <span className="text-white">{packageResult.name}</span></div>
                                <div>Format: <span className="text-white">{packageResult.format}</span> | Size: <span className="text-white">{packageResult.size_mb} MB</span></div>
                                <div>Params: <span className="text-white">{packageResult.parameters?.toLocaleString()}</span></div>
                                <div className="truncate" title={packageResult.path}><FolderOpen size={10} className="inline mr-1" />{packageResult.path}</div>
                            </div>
                        )}
                    </Card>

                    <Card>
                        <CardTitle icon={Cpu}>Resource Configuration</CardTitle>
                        <div className="mt-4 grid grid-cols-2 gap-4">
                            <div title="Number of CPU cores allocated to the deployment runtime. Increase for heavier preprocessing or multi-threaded serving.">
                                <Input label="CPU Cores" type="number" value={config.cpuCores} onChange={(e) => update('cpuCores', +e.target.value)} />
                            </div>
                            <div title="System RAM allocated to the deployment container in gigabytes. Ensure enough headroom for model weights plus runtime.">
                                <Input label="Memory (GB)" type="number" value={config.memoryGB} onChange={(e) => update('memoryGB', +e.target.value)} />
                            </div>
                            <div title="Number of GPUs assigned for inference. Set to 0 for CPU-only deployment. Multiple GPUs enable model parallelism.">
                                <Input label="GPU Count" type="number" value={config.gpuCount} onChange={(e) => update('gpuCount', +e.target.value)} />
                            </div>
                            <div title="Scaling policy for the deployment. 'Manual' keeps fixed resources. 'Auto-Scale' adjusts replicas based on traffic.">
                                <Select label="Scaling" options={[
                                    { value: 'manual', label: 'Manual' },
                                    { value: 'auto', label: 'Auto-Scale' },
                                ]} value={config.scalingPolicy} onChange={(e) => update('scalingPolicy', e.target.value)} />
                            </div>
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
                                const isSelected = target === t.key;
                                const isEditing = editingTarget === t.key;
                                return (
                                    <button
                                        key={t.key}
                                        onClick={() => {
                                            setTarget(t.key);
                                            setEditingTarget(isEditing ? null : t.key);
                                        }}
                                        title={t.tooltip}
                                        className={cn(
                                            'p-4 rounded-xl border text-center transition-all relative',
                                            isSelected
                                                ? 'border-accent-cyan bg-accent-cyan/10 text-accent-cyan'
                                                : 'border-ic-border bg-ic-surface text-txt-secondary hover:border-accent-cyan/30'
                                        )}
                                    >
                                        <Icon size={24} className="mx-auto mb-2" />
                                        <div className="text-sm font-semibold">{t.label}</div>
                                        <div className="text-[10px] mt-0.5 text-txt-muted">{t.desc}</div>
                                        {isSelected && (
                                            <Settings size={10} className={cn('absolute top-2 right-2 transition-colors', isEditing ? 'text-accent-cyan' : 'text-txt-muted')} />
                                        )}
                                    </button>
                                );
                            })}
                        </div>

                        {/* Inline target configuration panel */}
                        {editingTarget && (
                            <div className="mt-3 border border-ic-border rounded-xl bg-ic-bg p-3 animate-fade-in-up">
                                <div className="flex items-center justify-between mb-3">
                                    <div className="text-xs font-semibold text-txt-primary flex items-center gap-1.5">
                                        <Settings size={12} className="text-accent-cyan" />
                                        {editingTarget.charAt(0).toUpperCase() + editingTarget.slice(1)} Configuration
                                    </div>
                                    <button onClick={() => setEditingTarget(null)} className="p-1 rounded hover:bg-ic-surface text-txt-muted hover:text-txt-secondary transition-colors">
                                        <X size={12} />
                                    </button>
                                </div>

                                {editingTarget === 'cloud' && (
                                    <div className="grid grid-cols-3 gap-3">
                                        <div title="Cloud provider for deployment. Determines container registry and orchestration platform.">
                                            <Select label="Provider" options={[
                                                { value: 'aws', label: 'AWS' },
                                                { value: 'gcp', label: 'Google Cloud' },
                                                { value: 'azure', label: 'Azure' },
                                            ]} value={targetConfig.cloud.provider} onChange={(e) => updateTargetConfig('cloud', 'provider', e.target.value)} />
                                        </div>
                                        <div title="Target region for the deployment. Choose a region close to your users for lower latency.">
                                            <Input label="Region" value={targetConfig.cloud.region} onChange={(e) => updateTargetConfig('cloud', 'region', e.target.value)} />
                                        </div>
                                        <div title="Cloud compute instance type. GPU instances (g4dn, p3) are recommended for model inference.">
                                            <Input label="Instance Type" value={targetConfig.cloud.instanceType} onChange={(e) => updateTargetConfig('cloud', 'instanceType', e.target.value)} />
                                        </div>
                                    </div>
                                )}

                                {editingTarget === 'edge' && (
                                    <div className="grid grid-cols-3 gap-3">
                                        <div title="Target edge device category. Determines optimization profile and binary format.">
                                            <Select label="Device" options={[
                                                { value: 'mobile', label: 'Mobile (Android/iOS)' },
                                                { value: 'iot', label: 'IoT Device' },
                                                { value: 'raspberry-pi', label: 'Raspberry Pi' },
                                                { value: 'jetson', label: 'NVIDIA Jetson' },
                                            ]} value={targetConfig.edge.device} onChange={(e) => updateTargetConfig('edge', 'device', e.target.value)} />
                                        </div>
                                        <div title="Inference runtime engine. ONNX is cross-platform; TFLite is optimized for mobile; TensorRT for NVIDIA GPUs.">
                                            <Select label="Runtime" options={[
                                                { value: 'onnx', label: 'ONNX Runtime' },
                                                { value: 'tflite', label: 'TensorFlow Lite' },
                                                { value: 'tensorrt', label: 'TensorRT' },
                                            ]} value={targetConfig.edge.runtime} onChange={(e) => updateTargetConfig('edge', 'runtime', e.target.value)} />
                                        </div>
                                        <div title="Maximum memory budget in MB for the edge device. Model will be optimized to fit within this limit.">
                                            <Input label="Memory Limit (MB)" type="number" value={targetConfig.edge.memoryLimitMB} onChange={(e) => updateTargetConfig('edge', 'memoryLimitMB', +e.target.value)} />
                                        </div>
                                    </div>
                                )}

                                {editingTarget === 'local' && (
                                    <div className="space-y-2">
                                        <div title="Local filesystem path where deployment artifacts will be written. Click Browse to navigate.">
                                            <label className="text-[10px] font-semibold uppercase tracking-wider text-txt-muted mb-1 block">Output Path</label>
                                            <div className="flex gap-2">
                                                <input
                                                    type="text"
                                                    value={targetConfig.local.outputPath}
                                                    onChange={(e) => updateTargetConfig('local', 'outputPath', e.target.value)}
                                                    placeholder="production_packages/local_deploy/"
                                                    className="input-dark flex-1"
                                                />
                                                <button
                                                    onClick={() => openBrowser(targetConfig.local.outputPath || '')}
                                                    disabled={browserLoading}
                                                    className="btn-secondary whitespace-nowrap"
                                                    title="Browse filesystem to select a deployment output folder"
                                                >
                                                    {browserLoading ? <Loader2 size={14} className="animate-spin" /> : <FolderOpen size={14} />}
                                                    Browse
                                                </button>
                                            </div>
                                        </div>

                                        {/* Folder browser panel */}
                                        {showBrowser && (
                                            <div className="border border-ic-border rounded-xl bg-ic-bg overflow-hidden animate-fade-in-up">
                                                <div className="flex items-center justify-between px-3 py-2 bg-ic-surface border-b border-ic-border">
                                                    <div className="flex items-center gap-2 text-xs text-txt-primary font-medium min-w-0">
                                                        <Folder size={14} className="text-accent-cyan shrink-0" />
                                                        <span className="truncate">{browserPath || 'Drives'}</span>
                                                    </div>
                                                    <div className="flex items-center gap-1 shrink-0">
                                                        {browserParent !== null && (
                                                            <button onClick={() => openBrowser(browserParent)} className="p-1 rounded hover:bg-ic-bg text-txt-muted hover:text-txt-secondary transition-colors" title="Go up one level">
                                                                <ArrowUp size={14} />
                                                            </button>
                                                        )}
                                                        {browserPath && (
                                                            <button onClick={() => openBrowser('')} className="p-1 rounded hover:bg-ic-bg text-txt-muted hover:text-txt-secondary transition-colors" title="Go to drives">
                                                                <HardDrive size={14} />
                                                            </button>
                                                        )}
                                                        <button onClick={() => setShowBrowser(false)} className="p-1 rounded hover:bg-ic-bg text-txt-muted hover:text-txt-secondary transition-colors">
                                                            <X size={14} />
                                                        </button>
                                                    </div>
                                                </div>
                                                <div className="max-h-44 overflow-y-auto">
                                                    {browserPath && (
                                                        <button
                                                            onClick={() => selectBrowserFolder(browserPath)}
                                                            className="w-full flex items-center gap-2 px-3 py-2 text-xs text-accent-cyan hover:bg-accent-cyan/10 border-b border-ic-border transition-colors"
                                                        >
                                                            <CheckCircle2 size={12} />
                                                            <span className="font-medium">Select this folder</span>
                                                        </button>
                                                    )}
                                                    {browserItems.length === 0 && (
                                                        <div className="px-3 py-4 text-xs text-txt-muted text-center">No subfolders found</div>
                                                    )}
                                                    {browserItems.map((item) => (
                                                        <button
                                                            key={item.path}
                                                            onClick={() => item.locked ? null : openBrowser(item.path)}
                                                            disabled={item.locked}
                                                            className={cn(
                                                                'w-full flex items-center justify-between px-3 py-1.5 text-xs transition-colors',
                                                                item.locked
                                                                    ? 'text-txt-muted cursor-not-allowed opacity-50'
                                                                    : 'text-txt-secondary hover:bg-ic-surface hover:text-txt-primary cursor-pointer'
                                                            )}
                                                        >
                                                            <div className="flex items-center gap-2 min-w-0">
                                                                {item.type === 'drive' ? (
                                                                    <HardDrive size={13} className="text-accent-indigo shrink-0" />
                                                                ) : item.locked ? (
                                                                    <Lock size={13} className="text-txt-muted shrink-0" />
                                                                ) : (
                                                                    <Folder size={13} className="text-accent-warning shrink-0" />
                                                                )}
                                                                <span className="truncate">{item.name}</span>
                                                            </div>
                                                            {item.type === 'drive' && item.total_bytes > 0 && (
                                                                <span className="text-[10px] text-txt-muted shrink-0 ml-2">
                                                                    {formatBytes(item.free_bytes)} free
                                                                </span>
                                                            )}
                                                        </button>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Deployment target location */}
                        <div className="mt-3 bg-ic-surface rounded-lg px-3 py-2">
                            <div className="flex items-center gap-1.5 text-[11px] text-txt-muted mb-1">
                                <FolderOpen size={11} />
                                <span>Target Location</span>
                            </div>
                            {deployResult ? (
                                <div className="text-xs font-mono text-accent-success truncate flex items-center gap-1.5" title={deployResult.deploy_dir || deployResult.bundle_dir || deployResult.serve_script}>
                                    <CheckCircle2 size={11} className="shrink-0" />
                                    {deployResult.deploy_dir || deployResult.bundle_dir || deployResult.serve_script}
                                </div>
                            ) : (
                                <div className="text-xs font-mono text-white truncate" title={target === 'local' ? targetConfig.local.outputPath : DEPLOY_PATHS[target]}>
                                    {target === 'local' ? targetConfig.local.outputPath : DEPLOY_PATHS[target]}
                                </div>
                            )}
                        </div>
                        <button
                            onClick={handleDeploy}
                            disabled={progress < 100}
                            className="btn-primary mt-4 w-full justify-center"
                            title={progress < 100 ? 'Package a model first before deploying. The progress bar must reach 100% to enable this button.' : `Deploy the packaged model to the selected ${target} target. Creates serving artifacts and deployment configuration.`}
                        >
                            <Rocket size={16} /> Deploy to {target.charAt(0).toUpperCase() + target.slice(1)}
                        </button>
                    </Card>

                    <Card>
                        <CardTitle>Deployment Status</CardTitle>
                        <div className="mt-4">
                            <div className="flex justify-between text-sm mb-2">
                                <span className="text-txt-muted" title="Packaging progress from 0-100%. Model must be fully packaged before deployment can begin.">
                                    Progress
                                </span>
                                <span className="font-mono text-accent-cyan">{progress}%</span>
                            </div>
                            <ProgressBar value={progress} max={100} variant={progress === 100 ? 'success' : 'cyan'} />
                        </div>
                        <div
                            className="mt-4 bg-ic-bg rounded-lg p-3 h-40 overflow-y-auto font-mono text-xs text-txt-muted"
                            title="Real-time log output from packaging and deployment operations. Scroll to see history."
                        >
                            {logs.length === 0 && <span>Waiting for deployment...</span>}
                            {logs.map((l, i) => <div key={i}>{l}</div>)}
                        </div>
                    </Card>
                </div>
            </div>
        </ContentArea>
    );
}
