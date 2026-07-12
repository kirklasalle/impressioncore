import React, { useState, useMemo, useEffect } from 'react';
import { Boxes, Cpu, Save, Loader2 } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Input, Select, Toggle, ProgressBar, StatCard, Badge } from '../components/ui';
import { configureModel, getModelConfig } from '../lib/api';
import { formatNumber, estimateParams, estimateVRAM } from '../lib/utils';
import { MODEL_PRESETS, PRECISION_OPTIONS, VRAM_TARGET_GB } from '../lib/constants';
import toast from 'react-hot-toast';

export default function ModelDefinitionPage() {
    const [config, setConfig] = useState({
        architecture: 'transformer', preset: 'custom',
        layers: 8, hiddenSize: 768, heads: 12,
        intermediateSize: 3072, contextWindow: 4096,
        vocabSize: 50257, precision: 'fp16', activation: 'gelu',
        flashAttention: true, rope: true,
    });
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        getModelConfig().then(({ data }) => {
            if (data.success && data.config) setConfig((prev) => ({ ...prev, ...data.config }));
        }).catch(() => { });
    }, []);

    const update = (key, val) => {
        const next = { ...config, [key]: val };
        // Auto-fill from preset
        if (key === 'preset' && MODEL_PRESETS[val]) {
            Object.assign(next, MODEL_PRESETS[val]);
        }
        setConfig(next);
    };

    const params = useMemo(() => estimateParams(config), [config.layers, config.hiddenSize, config.vocabSize]);
    const vram = useMemo(() => estimateVRAM(params, config.precision), [params, config.precision]);
    const vramPct = (vram / VRAM_TARGET_GB) * 100;
    const vramVariant = vramPct <= 70 ? 'success' : vramPct <= 95 ? 'warning' : 'danger';

    const handleSave = async () => {
        setSaving(true);
        try {
            await configureModel(config);
            toast.success('Model configuration saved');
        } catch (err) {
            toast.error(err.response?.data?.error || 'Save failed');
        } finally {
            setSaving(false);
        }
    };

    return (
        <ContentArea title="Model Definition" subtitle="Define the transformer architecture and resource budget.">
            <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
                {/* Config — 3 cols */}
                <div className="lg:col-span-3 space-y-4">
                    <Card>
                        <CardTitle icon={Boxes}>Architecture Configuration</CardTitle>
                        <div className="mt-4 space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <Select label="Architecture" options={[
                                    { value: 'transformer', label: 'Transformer' },
                                    { value: 'mamba', label: 'Mamba (SSM)' },
                                    { value: 'rwkv', label: 'RWKV' },
                                ]} value={config.architecture} onChange={(e) => update('architecture', e.target.value)} />
                                <Select label="Model Size Preset" options={Object.keys(MODEL_PRESETS).map((k) => ({ value: k, label: k.charAt(0).toUpperCase() + k.slice(1) }))}
                                    value={config.preset} onChange={(e) => update('preset', e.target.value)} />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <Input label="Layers" type="number" value={config.layers} onChange={(e) => update('layers', +e.target.value)} />
                                <Input label="Hidden Size" type="number" value={config.hiddenSize} onChange={(e) => update('hiddenSize', +e.target.value)} />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <Input label="Attention Heads" type="number" value={config.heads} onChange={(e) => update('heads', +e.target.value)} />
                                <Input label="Intermediate Size" type="number" value={config.intermediateSize} onChange={(e) => update('intermediateSize', +e.target.value)} />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <Input label="Context Window" type="number" value={config.contextWindow} onChange={(e) => update('contextWindow', +e.target.value)} />
                                <Input label="Vocab Size" type="number" value={config.vocabSize} onChange={(e) => update('vocabSize', +e.target.value)} />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <Select label="Precision" options={PRECISION_OPTIONS} value={config.precision} onChange={(e) => update('precision', e.target.value)} />
                            </div>
                            <Select label="Activation Function" options={[
                                { value: 'gelu', label: 'GELU' }, { value: 'silu', label: 'SiLU (Swish)' },
                                { value: 'relu', label: 'ReLU' }, { value: 'gelu_new', label: 'GELU (New)' },
                            ]} value={config.activation} onChange={(e) => update('activation', e.target.value)} />
                            <div className="grid grid-cols-2 gap-4">
                                <Toggle label="Flash Attention" checked={config.flashAttention}
                                    onChange={(e) => update('flashAttention', e.target.checked)} />
                                <Toggle label="RoPE Embeddings" checked={config.rope}
                                    onChange={(e) => update('rope', e.target.checked)} />
                            </div>
                        </div>
                        <button onClick={handleSave} disabled={saving} className="btn-primary mt-4 w-full justify-center">
                            {saving ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}
                            Save Configuration
                        </button>
                    </Card>
                </div>

                {/* Summary — 2 cols */}
                <div className="lg:col-span-2 space-y-4">
                    <Card>
                        <CardTitle icon={Cpu}>Model Summary</CardTitle>
                        <div className="mt-4 space-y-3">
                            <div className="flex justify-between text-sm"><span className="text-txt-muted">Architecture</span><span className="text-txt-primary font-mono">{config.architecture}</span></div>
                            <div className="flex justify-between text-sm"><span className="text-txt-muted">Layers × Heads</span><span className="text-txt-primary font-mono">{config.layers} × {config.heads}</span></div>
                            <div className="flex justify-between text-sm"><span className="text-txt-muted">Hidden Size</span><span className="text-txt-primary font-mono">{formatNumber(config.hiddenSize)}</span></div>
                            <div className="flex justify-between text-sm"><span className="text-txt-muted">Intermediate Size</span><span className="text-txt-primary font-mono">{formatNumber(config.intermediateSize)}</span></div>
                            <div className="flex justify-between text-sm"><span className="text-txt-muted">Context Window</span><span className="text-txt-primary font-mono">{formatNumber(config.contextWindow)}</span></div>
                            <div className="flex justify-between text-sm"><span className="text-txt-muted">Precision</span><span className="text-txt-primary font-mono">{config.precision.toUpperCase()}</span></div>
                            <div className="border-t border-ic-border my-3" />
                            <div className="flex justify-between text-sm"><span className="text-txt-muted">Est. Parameters</span><span className="text-accent-cyan font-mono font-bold">{formatNumber(params)}</span></div>
                            {config.flashAttention && <Badge variant="cyan" className="mr-1">Flash Attn</Badge>}
                            {config.rope && <Badge variant="info">RoPE</Badge>}
                        </div>
                    </Card>

                    <Card>
                        <CardTitle>VRAM Estimation</CardTitle>
                        <div className="mt-4">
                            <div className="flex justify-between text-sm mb-2">
                                <span className="text-txt-muted">Estimated VRAM</span>
                                <span className={`font-mono font-bold ${vramVariant === 'success' ? 'text-accent-success' : vramVariant === 'warning' ? 'text-accent-warning' : 'text-accent-danger'}`}>
                                    {vram.toFixed(2)} GB / {VRAM_TARGET_GB} GB
                                </span>
                            </div>
                            <ProgressBar value={vramPct} max={100} variant={vramVariant} />
                            <p className="text-[10px] text-txt-muted mt-2">
                                Target: NVIDIA GTX 1050 Ti ({VRAM_TARGET_GB} GB VRAM).
                                {vramPct > 95 && ' ⚠️ Model exceeds VRAM budget — consider reducing size or using quantization.'}
                            </p>
                        </div>
                    </Card>
                </div>
            </div>
        </ContentArea>
    );
}
