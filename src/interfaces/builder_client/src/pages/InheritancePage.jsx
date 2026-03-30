import React, { useState } from 'react';
import { GitBranch, ChevronDown, ChevronRight, Plus, Trash2, Radio, ArrowRight } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Input, Select, Badge, Toggle } from '../components/ui';
import { cn } from '../lib/utils';
import toast from 'react-hot-toast';

const DEFAULT_LAYERS = [
    {
        id: 1, name: 'Foundation Layer', type: 'base', active: true, expanded: true,
        modules: [
            { id: 101, name: 'Embedding', config: 'vocab=32000, dim=768', inherited: false },
            { id: 102, name: 'Positional Encoding', config: 'RoPE, max_len=2048', inherited: false },
        ],
    },
    {
        id: 2, name: 'Attention Layer', type: 'attention', active: true, expanded: true,
        modules: [
            { id: 201, name: 'Multi-Head Attention', config: 'heads=12, dim=768', inherited: true },
            { id: 202, name: 'Flash Attention', config: 'enabled=true, causal=true', inherited: false },
        ],
    },
    {
        id: 3, name: 'FFN Layer', type: 'ffn', active: true, expanded: false,
        modules: [
            { id: 301, name: 'SwiGLU FFN', config: 'intermediate=3072', inherited: true },
            { id: 302, name: 'Dropout', config: 'p=0.1', inherited: true },
        ],
    },
    {
        id: 4, name: 'Output Layer', type: 'output', active: true, expanded: false,
        modules: [
            { id: 401, name: 'Layer Norm', config: 'eps=1e-6', inherited: true },
            { id: 402, name: 'LM Head', config: 'vocab=32000, tied=true', inherited: true },
        ],
    },
];

export default function InheritancePage() {
    const [layers, setLayers] = useState(DEFAULT_LAYERS);

    const toggleExpand = (id) => {
        setLayers((p) => p.map((l) => l.id === id ? { ...l, expanded: !l.expanded } : l));
    };
    const toggleActive = (id) => {
        setLayers((p) => p.map((l) => l.id === id ? { ...l, active: !l.active } : l));
    };
    const toggleInherited = (layerId, moduleId) => {
        setLayers((p) => p.map((l) => l.id === layerId ? {
            ...l,
            modules: l.modules.map((m) => m.id === moduleId ? { ...m, inherited: !m.inherited } : m),
        } : l));
    };

    const totalModules = layers.reduce((a, l) => a + l.modules.length, 0);
    const inheritedCount = layers.reduce((a, l) => a + l.modules.filter((m) => m.inherited).length, 0);

    return (
        <ContentArea title="Model Inheritance" subtitle="Configure layer hierarchy and module inheritance chains.">
            {/* Stats */}
            <div className="grid grid-cols-4 gap-3 mb-6">
                <div className="stat-card"><span className="text-lg font-bold text-txt-primary">{layers.length}</span><span className="text-[10px] text-txt-muted">Layers</span></div>
                <div className="stat-card"><span className="text-lg font-bold text-accent-cyan">{totalModules}</span><span className="text-[10px] text-txt-muted">Modules</span></div>
                <div className="stat-card"><span className="text-lg font-bold text-accent-indigo">{inheritedCount}</span><span className="text-[10px] text-txt-muted">Inherited</span></div>
                <div className="stat-card"><span className="text-lg font-bold text-accent-success">{layers.filter((l) => l.active).length}</span><span className="text-[10px] text-txt-muted">Active</span></div>
            </div>

            {/* Inheritance Chain Visual */}
            <Card className="mb-6">
                <CardTitle icon={GitBranch}>Inheritance Chain</CardTitle>
                <div className="mt-4 flex items-center gap-2 overflow-x-auto pb-2">
                    {layers.map((layer, i) => (
                        <React.Fragment key={layer.id}>
                            <div className={cn(
                                'px-4 py-2 rounded-lg border text-sm font-medium whitespace-nowrap',
                                layer.active
                                    ? 'bg-accent-cyan/10 border-accent-cyan/40 text-accent-cyan'
                                    : 'bg-ic-surface border-ic-border text-txt-muted line-through'
                            )}>
                                {layer.name}
                            </div>
                            {i < layers.length - 1 && (
                                <ArrowRight size={16} className="text-accent-cyan/40 shrink-0" />
                            )}
                        </React.Fragment>
                    ))}
                </div>
            </Card>

            {/* Layer Details */}
            <div className="space-y-3">
                {layers.map((layer) => (
                    <Card key={layer.id} className={cn(!layer.active && 'opacity-50')}>
                        <div className="flex items-center gap-3">
                            <button onClick={() => toggleExpand(layer.id)} className="text-txt-muted hover:text-txt-primary">
                                {layer.expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                            </button>
                            <div className="flex-1">
                                <div className="flex items-center gap-2">
                                    <span className="text-sm font-semibold text-txt-primary">{layer.name}</span>
                                    <Badge variant={
                                        layer.type === 'base' ? 'cyan'
                                            : layer.type === 'attention' ? 'info'
                                                : layer.type === 'ffn' ? 'success'
                                                    : 'warning'
                                    }>{layer.type}</Badge>
                                </div>
                                <div className="text-[10px] text-txt-muted">{layer.modules.length} modules</div>
                            </div>
                            <Toggle label="" checked={layer.active} onChange={() => toggleActive(layer.id)} />
                        </div>

                        {layer.expanded && (
                            <div className="mt-3 ml-7 space-y-2 border-l-2 border-ic-border pl-4">
                                {layer.modules.map((mod) => (
                                    <div key={mod.id} className="flex items-center gap-3 p-2 rounded-lg bg-ic-bg/50">
                                        <Radio size={14} className={mod.inherited ? 'text-accent-indigo' : 'text-txt-muted'} />
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2">
                                                <span className="text-sm text-txt-primary">{mod.name}</span>
                                                {mod.inherited && <Badge variant="info">inherited</Badge>}
                                            </div>
                                            <span className="text-[10px] font-mono text-txt-muted">{mod.config}</span>
                                        </div>
                                        <button
                                            onClick={() => toggleInherited(layer.id, mod.id)}
                                            className={cn(
                                                'text-[10px] px-2 py-0.5 rounded-full border transition-colors',
                                                mod.inherited
                                                    ? 'border-accent-indigo/40 text-accent-indigo'
                                                    : 'border-ic-border text-txt-muted hover:border-accent-indigo/40'
                                            )}
                                        >
                                            {mod.inherited ? 'Inherited' : 'Override'}
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </Card>
                ))}
            </div>
        </ContentArea>
    );
}
