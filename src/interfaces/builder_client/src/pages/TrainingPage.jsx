import React, { useState, useEffect, useRef } from 'react';
import { GraduationCap, Play, Square, Loader2, Activity, Save, Trash2, FolderOpen, HardDrive } from 'lucide-react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler } from 'chart.js';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Input, Select, Toggle, StatCard, Badge } from '../components/ui';
import { startTraining, stopTraining, getTrainingStatus, getTrainingConfig, saveTrainingConfig, getCheckpoints, deleteCheckpoint, setCheckpointDir } from '../lib/api';
import { LR_SCHEDULERS, PRECISION_OPTIONS } from '../lib/constants';
import toast from 'react-hot-toast';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler);

export default function TrainingPage() {
    const [config, setConfig] = useState({
        epochs: 3, batchSize: 1, learningRate: 5e-5,
        warmupSteps: 100, scheduler: 'cosine',
        precision: 'fp16', gradCheckpoint: true,
        gradAccumSteps: 8, maxSteps: 0,
    });
    const [saving, setSaving] = useState(false);
    const [status, setStatus] = useState({ running: false, epoch: 0, step: 0, total_steps: 0, loss: 0, vram: 0, vram_total: 0, vram_peak: 0, checkpoint_path: null });
    const [lossHistory, setLossHistory] = useState([]);
    const [logs, setLogs] = useState([]);
    const [checkpoints, setCheckpoints] = useState([]);
    const [ckptDir, setCkptDir] = useState('');
    const pollRef = useRef(null);
    const logEndRef = useRef(null);

    const update = (key, val) => setConfig((p) => ({ ...p, [key]: val }));

    const addLog = (msg) => {
        const ts = new Date().toLocaleTimeString();
        setLogs((p) => [...p.slice(-200), `[${ts}] ${msg}`]);
    };

    const loadCheckpoints = async () => {
        try {
            const { data } = await getCheckpoints();
            if (data.success) {
                setCheckpoints(data.checkpoints || []);
                setCkptDir(data.directory || '');
            }
        } catch { /* ignore */ }
    };

    const handleDeleteCheckpoint = async (name) => {
        try {
            await deleteCheckpoint(name);
            toast.success(`Deleted ${name}`);
            loadCheckpoints();
        } catch (err) {
            toast.error(err.response?.data?.error || 'Delete failed');
        }
    };

    const handleStart = async () => {
        try {
            await startTraining(config);
            setStatus((s) => ({ ...s, running: true }));
            addLog('Training started');
            toast.success('Training started');
            startPolling();
        } catch (err) {
            toast.error(err.response?.data?.error || 'Failed to start training');
        }
    };

    const handleStop = async () => {
        try {
            await stopTraining();
            setStatus((s) => ({ ...s, running: false }));
            addLog('Training stopped');
            toast('Training stopped');
            stopPolling();
            loadCheckpoints();
        } catch (err) {
            toast.error('Failed to stop training');
        }
    };

    const startPolling = () => {
        stopPolling();
        pollRef.current = setInterval(async () => {
            try {
                const { data } = await getTrainingStatus();
                setStatus(data);
                if (data.loss) {
                    setLossHistory((p) => [...p.slice(-100), data.loss]);
                    addLog(`Epoch ${data.epoch} Step ${data.step} — loss: ${data.loss.toFixed(4)}`);
                }
                if (!data.running) {
                    stopPolling();
                    loadCheckpoints();
                }
            } catch { /* ignore poll errors */ }
        }, 3000);
    };

    const stopPolling = () => {
        if (pollRef.current) clearInterval(pollRef.current);
        pollRef.current = null;
    };

    useEffect(() => () => stopPolling(), []);
    useEffect(() => { logEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [logs]);

    useEffect(() => {
        getTrainingConfig().then(({ data }) => {
            if (data.success && data.config) setConfig((prev) => ({ ...prev, ...data.config }));
        }).catch(() => { });
        loadCheckpoints();
    }, []);

    const handleSave = async () => {
        setSaving(true);
        try {
            await saveTrainingConfig(config);
            toast.success('Training configuration saved');
        } catch (err) {
            toast.error(err.response?.data?.error || 'Save failed');
        } finally {
            setSaving(false);
        }
    };

    const vramPct = status.vram_total > 0 ? Math.min((status.vram / status.vram_total) * 100, 100) : 0;

    const chartData = {
        labels: lossHistory.map((_, i) => i),
        datasets: [{
            label: 'Loss',
            data: lossHistory,
            borderColor: '#38bdf8',
            backgroundColor: 'rgba(56,189,248,0.1)',
            fill: true, tension: 0.3, pointRadius: 0, borderWidth: 2,
        }],
    };
    const chartOpts = {
        responsive: true, maintainAspectRatio: false,
        scales: {
            x: { display: false },
            y: { ticks: { color: '#64748b', font: { size: 10, family: 'JetBrains Mono' } }, grid: { color: 'rgba(56,189,248,0.06)' } },
        },
        plugins: { tooltip: { enabled: true }, legend: { display: false } },
    };

    return (
        <ContentArea title="Training" subtitle="Configure hyperparameters and monitor training progress.">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Hyperparameters */}
                <div className="space-y-4">
                    <Card>
                        <CardTitle icon={GraduationCap}>Hyperparameters</CardTitle>
                        <div className="mt-4 space-y-4">
                            <div className="grid grid-cols-3 gap-4">
                                <div title="Number of full passes through the training dataset. More epochs = more learning but risk overfitting. Typical: 1-10.">
                                    <Input label="Epochs" type="number" value={config.epochs} onChange={(e) => update('epochs', +e.target.value)} />
                                </div>
                                <div title="Stop after N optimizer steps regardless of epochs. Set 0 to use epoch-based training. Overrides epochs when > 0.">
                                    <Input label="Max Steps" type="number" value={config.maxSteps} onChange={(e) => update('maxSteps', +e.target.value)} />
                                </div>
                                <div title="Samples processed per forward pass. GTX 1050 Ti: keep at 1 with grad accumulation to simulate larger batches.">
                                    <Input label="Batch Size" type="number" value={config.batchSize} onChange={(e) => update('batchSize', +e.target.value)} />
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div title="Accumulate gradients over N mini-batches before updating weights. Effective batch = batchSize × gradAccumSteps.">
                                    <Input label="Grad Accumulation Steps" type="number" value={config.gradAccumSteps} onChange={(e) => update('gradAccumSteps', +e.target.value)} />
                                </div>
                                <div title="Step size for weight updates. Too high = divergence, too low = slow learning. B3 default: 5e-5.">
                                    <Input label="Learning Rate" type="text" value={config.learningRate} onChange={(e) => update('learningRate', +e.target.value)} />
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div title="Steps with linearly increasing LR before the scheduler takes over. Prevents early training instability.">
                                    <Input label="Warmup Steps" type="number" value={config.warmupSteps} onChange={(e) => update('warmupSteps', +e.target.value)} />
                                </div>
                                <div title="Strategy to decay LR over training. Cosine gives smooth annealing; linear decays steadily; step drops at intervals.">
                                    <Select label="LR Scheduler" options={LR_SCHEDULERS} value={config.scheduler} onChange={(e) => update('scheduler', e.target.value)} />
                                </div>
                            </div>
                            <div title="Numerical precision for training. FP16 halves VRAM usage on CUDA GPUs. Use FP32 for CPU-only or debugging.">
                                <Select label="Precision" options={PRECISION_OPTIONS} value={config.precision} onChange={(e) => update('precision', e.target.value)} />
                            </div>
                            <div title="Trade compute for memory by recomputing activations during backward pass. Saves ~30-40% VRAM. Recommended for 4GB GPUs.">
                                <Toggle label="Gradient Checkpointing" checked={config.gradCheckpoint}
                                    onChange={(e) => update('gradCheckpoint', e.target.checked)} />
                            </div>
                        </div>
                        <div className="flex gap-3 mt-4">
                            <button onClick={handleSave} disabled={saving} className="btn-secondary flex-1 justify-center"
                                title="Persist current hyperparameter configuration to disk. Reloaded automatically on next visit.">
                                {saving ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}
                                Save Config
                            </button>
                            <button onClick={handleStart} disabled={status.running} className="btn-primary flex-1 justify-center"
                                title="Begin training with current hyperparameters. Model weights are updated in-place on the loaded model.">
                                {status.running ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
                                Start Training
                            </button>
                            <button onClick={handleStop} disabled={!status.running} className="btn-danger flex-1 justify-center"
                                title="Gracefully stop the running training loop. A checkpoint is saved automatically before exit.">
                                <Square size={16} /> Stop
                            </button>
                        </div>
                    </Card>

                    {/* Checkpoint Management */}
                    <Card>
                        <CardTitle icon={HardDrive}>Checkpoints</CardTitle>
                        <div className="mt-3" title="Choose the drive and directory where checkpoint .pt files are saved. Click Set to apply.">
                            <label className="block text-xs font-medium text-txt-muted mb-1">Save Directory</label>
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={ckptDir}
                                    onChange={(e) => setCkptDir(e.target.value)}
                                    className="flex-1 bg-ic-bg border border-ic-border rounded-lg px-3 py-1.5 text-xs font-mono text-txt focus:outline-none focus:ring-1 focus:ring-sky-500"
                                    placeholder="F:\models\checkpoints"
                                />
                                <button
                                    onClick={async () => {
                                        try {
                                            const { data } = await setCheckpointDir(ckptDir);
                                            if (data.success) {
                                                toast.success('Checkpoint directory updated');
                                                setCkptDir(data.directory);
                                                loadCheckpoints();
                                            } else {
                                                toast.error(data.error || 'Failed to set directory');
                                            }
                                        } catch (err) {
                                            toast.error(err.response?.data?.error || 'Failed to set directory');
                                        }
                                    }}
                                    className="btn-secondary px-3 py-1.5 text-xs"
                                    title="Validate and set the checkpoint save directory. Creates the directory if it doesn't exist."
                                >
                                    <FolderOpen size={14} /> Set
                                </button>
                            </div>
                        </div>
                        {ckptDir && (
                            <div className="mt-2 flex items-center gap-2 text-xs text-txt-muted" title="Active checkpoint save path. All new training checkpoints will be written here.">
                                <FolderOpen size={14} className="shrink-0" />
                                <span className="font-mono truncate">{ckptDir}</span>
                            </div>
                        )}
                        <div className="mt-3 space-y-2">
                            {checkpoints.length === 0 ? (
                                <p className="text-xs text-txt-muted">No checkpoints saved yet. Start training to generate checkpoints.</p>
                            ) : (
                                checkpoints.map((ck) => (
                                    <div key={ck.name} className="flex items-center justify-between bg-ic-bg rounded-lg px-3 py-2 text-xs">
                                        <div className="flex-1 min-w-0">
                                            <p className="font-mono text-txt truncate" title={ck.path}>{ck.name}</p>
                                            <p className="text-txt-muted">{ck.size_mb} MB · {new Date(ck.modified * 1000).toLocaleString()}</p>
                                        </div>
                                        <button onClick={() => handleDeleteCheckpoint(ck.name)}
                                            className="ml-2 p-1.5 rounded hover:bg-red-500/20 text-red-400 transition-colors"
                                            title={`Delete checkpoint ${ck.name}. This action is irreversible.`}>
                                            <Trash2 size={14} />
                                        </button>
                                    </div>
                                ))
                            )}
                        </div>
                    </Card>
                </div>

                {/* Dashboard */}
                <div className="space-y-4">
                    <Card>
                        <CardTitle icon={Activity}>Live Dashboard</CardTitle>
                        <div className="grid grid-cols-4 gap-3 mt-4">
                            <div title="Current training state. Running = active training loop; Idle = no training in progress.">
                                <StatCard label="Status" value={status.running ? <Badge variant="success">Running</Badge> : <Badge>Idle</Badge>} />
                            </div>
                            <div title="Current epoch out of total configured epochs. Each epoch is one full pass through training data.">
                                <StatCard label="Epoch" value={`${status.epoch}/${config.epochs}`} />
                            </div>
                            <div title="Current optimizer step out of total estimated steps. Each step = one weight update after gradient accumulation.">
                                <StatCard label="Steps" value={`${status.step}/${status.total_steps || '—'}`} />
                            </div>
                            <div title="Cross-entropy loss value. Lower = better. Watch for steady decrease; spikes may indicate learning rate issues.">
                                <StatCard label="Loss" value={status.loss ? status.loss.toFixed(4) : '—'} />
                            </div>
                        </div>
                        {/* VRAM telemetry bar */}
                        <div className="mt-3 space-y-1" title={`GPU VRAM: ${status.vram.toFixed?.(1) || 0}G used / ${status.vram_total.toFixed?.(1) || 0}G total. Peak: ${status.vram_peak.toFixed?.(1) || 0}G.`}>
                            <div className="flex justify-between text-xs text-txt-muted">
                                <span className="flex items-center gap-1"><HardDrive size={12} /> VRAM</span>
                                <span>
                                    {status.vram?.toFixed?.(1) || '0.0'}G / {status.vram_total?.toFixed?.(1) || '—'}G
                                    {status.vram_peak > 0 && <span className="text-amber-400 ml-1">(peak {status.vram_peak.toFixed(1)}G)</span>}
                                </span>
                            </div>
                            <div className="w-full bg-ic-bg rounded-full h-2 overflow-hidden">
                                <div
                                    className={`h-full rounded-full transition-all duration-500 ${vramPct > 90 ? 'bg-red-500' : vramPct > 70 ? 'bg-amber-500' : 'bg-sky-500'}`}
                                    style={{ width: `${vramPct}%` }}
                                />
                            </div>
                        </div>
                    </Card>

                    <Card className="h-56">
                        <CardTitle>Loss Curve</CardTitle>
                        <div className="h-40 mt-2" title="Real-time plot of training loss over steps. A healthy curve shows steady decrease with occasional noise.">
                            {lossHistory.length > 0
                                ? <Line data={chartData} options={chartOpts} />
                                : <div className="h-full flex items-center justify-center text-xs text-txt-muted">Start training to see the loss curve</div>
                            }
                        </div>
                    </Card>

                    <Card>
                        <CardTitle>Training Log</CardTitle>
                        <div className="mt-2 bg-ic-bg rounded-lg p-3 h-44 overflow-y-auto font-mono text-xs text-txt-muted"
                            title="Timestamped training output including loss, learning rate, VRAM usage, and system messages.">
                            {logs.length === 0 && <span className="text-txt-muted">Waiting for training output...</span>}
                            {logs.map((l, i) => <div key={i}>{l}</div>)}
                            <div ref={logEndRef} />
                        </div>
                    </Card>
                </div>
            </div>
        </ContentArea>
    );
}
