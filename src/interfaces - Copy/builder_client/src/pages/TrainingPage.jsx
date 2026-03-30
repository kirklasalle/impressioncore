import React, { useState, useEffect, useRef } from 'react';
import { GraduationCap, Play, Square, Loader2, Activity } from 'lucide-react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler } from 'chart.js';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Input, Select, Toggle, StatCard, Badge } from '../components/ui';
import { startTraining, stopTraining, getTrainingStatus } from '../lib/api';
import { LR_SCHEDULERS, PRECISION_OPTIONS } from '../lib/constants';
import toast from 'react-hot-toast';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler);

export default function TrainingPage() {
    const [config, setConfig] = useState({
        epochs: 3, batchSize: 4, learningRate: 5e-5,
        warmupSteps: 100, scheduler: 'cosine',
        precision: 'fp16', gradCheckpoint: true,
    });
    const [status, setStatus] = useState({ running: false, epoch: 0, step: 0, loss: 0, vram: 0 });
    const [lossHistory, setLossHistory] = useState([]);
    const [logs, setLogs] = useState([]);
    const pollRef = useRef(null);
    const logEndRef = useRef(null);

    const update = (key, val) => setConfig((p) => ({ ...p, [key]: val }));

    const addLog = (msg) => {
        const ts = new Date().toLocaleTimeString();
        setLogs((p) => [...p.slice(-200), `[${ts}] ${msg}`]);
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
                if (!data.running) stopPolling();
            } catch { /* ignore poll errors */ }
        }, 3000);
    };

    const stopPolling = () => {
        if (pollRef.current) clearInterval(pollRef.current);
        pollRef.current = null;
    };

    useEffect(() => () => stopPolling(), []);
    useEffect(() => { logEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [logs]);

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
                            <div className="grid grid-cols-2 gap-4">
                                <Input label="Epochs" type="number" value={config.epochs} onChange={(e) => update('epochs', +e.target.value)} />
                                <Input label="Batch Size" type="number" value={config.batchSize} onChange={(e) => update('batchSize', +e.target.value)} />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <Input label="Learning Rate" type="text" value={config.learningRate} onChange={(e) => update('learningRate', +e.target.value)} />
                                <Input label="Warmup Steps" type="number" value={config.warmupSteps} onChange={(e) => update('warmupSteps', +e.target.value)} />
                            </div>
                            <Select label="LR Scheduler" options={LR_SCHEDULERS} value={config.scheduler} onChange={(e) => update('scheduler', e.target.value)} />
                            <Select label="Precision" options={PRECISION_OPTIONS} value={config.precision} onChange={(e) => update('precision', e.target.value)} />
                            <Toggle label="Gradient Checkpointing" checked={config.gradCheckpoint}
                                onChange={(e) => update('gradCheckpoint', e.target.checked)} />
                        </div>
                        <div className="flex gap-3 mt-4">
                            <button onClick={handleStart} disabled={status.running} className="btn-primary flex-1 justify-center">
                                {status.running ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
                                Start Training
                            </button>
                            <button onClick={handleStop} disabled={!status.running} className="btn-danger flex-1 justify-center">
                                <Square size={16} /> Stop
                            </button>
                        </div>
                    </Card>
                </div>

                {/* Dashboard */}
                <div className="space-y-4">
                    <Card>
                        <CardTitle icon={Activity}>Live Dashboard</CardTitle>
                        <div className="grid grid-cols-4 gap-3 mt-4">
                            <StatCard label="Status" value={status.running ? <Badge variant="success">Running</Badge> : <Badge>Idle</Badge>} />
                            <StatCard label="Epoch" value={`${status.epoch}/${config.epochs}`} />
                            <StatCard label="Loss" value={status.loss ? status.loss.toFixed(4) : '—'} />
                            <StatCard label="VRAM" value={status.vram ? `${status.vram.toFixed(1)}G` : '—'} />
                        </div>
                    </Card>

                    <Card className="h-56">
                        <CardTitle>Loss Curve</CardTitle>
                        <div className="h-40 mt-2">
                            {lossHistory.length > 0
                                ? <Line data={chartData} options={chartOpts} />
                                : <div className="h-full flex items-center justify-center text-xs text-txt-muted">Start training to see the loss curve</div>
                            }
                        </div>
                    </Card>

                    <Card>
                        <CardTitle>Training Log</CardTitle>
                        <div className="mt-2 bg-ic-bg rounded-lg p-3 h-44 overflow-y-auto font-mono text-xs text-txt-muted">
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
