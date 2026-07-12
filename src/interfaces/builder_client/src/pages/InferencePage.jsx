import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send, Settings2, Bot, User, ChevronDown, FolderOpen, Sparkles, Save, Camera, Clock, Cpu, Zap, BarChart3 } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Slider, Input, Toggle, StatCard } from '../components/ui';
import { runInference, getModelInfo, getAvailableModels, getInferenceSettings, saveInferenceSettings, analyzeModelSettings } from '../lib/api';
import { cn } from '../lib/utils';
import toast from 'react-hot-toast';

export default function InferencePage() {
    const [messages, setMessages] = useState([
        { role: 'assistant', text: 'Hello! I\'m ready to chat. How can I help you?' },
    ]);
    const [input, setInput] = useState('');
    const [sending, setSending] = useState(false);
    const [settings, setSettings] = useState({
        temperature: 0.7, maxTokens: 512, topP: 0.9, topK: 50, sampling: true,
    });
    const [stats, setStats] = useState({ messages: 1, tokens: 0, avgLatency: 0, tps: 0 });
    const [modelInfo, setModelInfo] = useState({ name: 'ImpressionCore', status: 'checking' });
    const [availableModels, setAvailableModels] = useState([]);
    const [selectedModel, setSelectedModel] = useState('');
    const [includeCheckpoints, setIncludeCheckpoints] = useState(false);
    const [analyzing, setAnalyzing] = useState(false);
    const [telemetryLog, setTelemetryLog] = useState([]);
    const chatEndRef = useRef(null);
    const sessionStartRef = useRef(Date.now());

    const updateSetting = (key, val) => setSettings((p) => ({ ...p, [key]: val }));

    const selectedModelObj = availableModels.find((m) => m.id === selectedModel);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    useEffect(() => {
        getModelInfo()
            .then(({ data }) => {
                setModelInfo({
                    name: data.name || 'ImpressionCore-B1',
                    status: data.status === 'active' ? 'online' : 'offline',
                });
            })
            .catch(() => {
                setModelInfo((m) => ({ ...m, status: 'offline' }));
            });
    }, []);

    useEffect(() => {
        const params = includeCheckpoints ? { include_checkpoints: true } : undefined;
        getAvailableModels(params)
            .then(({ data }) => {
                const models = data.models || [];
                setAvailableModels(models);
                if (models.length > 0 && !models.find((m) => m.id === selectedModel)) {
                    const active = models.find((m) => m.status === 'active');
                    setSelectedModel(active ? active.id : models[0].id);
                }
            })
            .catch(() => { });
    }, [includeCheckpoints]);

    // Load saved inference settings on mount
    useEffect(() => {
        getInferenceSettings()
            .then(({ data }) => {
                if (data.success && data.config) {
                    setSettings((prev) => ({ ...prev, ...data.config }));
                }
            })
            .catch(() => {});
    }, []);

    const handleAnalyze = async () => {
        if (analyzing) return;
        setAnalyzing(true);
        try {
            const { data } = await analyzeModelSettings(selectedModel);
            if (data.success && data.recommended) {
                setSettings((prev) => ({ ...prev, ...data.recommended }));
                const info = data.config_info || {};
                const detail = info.model_type ? ` (${info.model_type}, ${info.num_layers} layers)` : '';
                toast.success(`Settings optimized for ${data.model}${detail}`);
            }
        } catch {
            toast.error('Failed to analyze model');
        } finally {
            setAnalyzing(false);
        }
    };

    const handleSaveSettings = async () => {
        try {
            const { data } = await saveInferenceSettings(settings);
            if (data.success) {
                toast.success('Settings saved');
            }
        } catch {
            toast.error('Failed to save settings');
        }
    };

    const handleSend = async () => {
        const text = input.trim();
        if (!text || sending) return;
        setInput('');
        setMessages((p) => [...p, { role: 'user', text }]);
        setSending(true);
        const start = Date.now();

        try {
            const { data } = await runInference({ prompt: text, model: selectedModel, ...settings });
            const latency = Date.now() - start;
            const reply = data.response || data.text || 'No response generated.';
            if (data.model_name) {
                setModelInfo((m) => ({ ...m, name: data.model_name, status: 'online' }));
            }
            setMessages((p) => [...p, { role: 'assistant', text: reply }]);
            const tokensUsed = data.tokens_used || text.split(' ').length + reply.split(' ').length;
            const tokPerSec = data.tokens_per_second || Math.round((reply.split(' ').length / latency) * 1000);
            setStats((s) => ({
                messages: s.messages + 2,
                tokens: s.tokens + tokensUsed,
                avgLatency: Math.round((s.avgLatency * (s.messages - 1) + latency) / s.messages),
                tps: tokPerSec,
            }));
            setTelemetryLog((prev) => [...prev, {
                timestamp: new Date().toISOString(),
                prompt: text.slice(0, 80) + (text.length > 80 ? '...' : ''),
                model: data.model_name || modelInfo.name,
                latencyMs: latency,
                tokensUsed,
                tokPerSec,
                settings: { ...settings },
            }]);
        } catch {
            // Demo fallback
            setModelInfo((m) => ({ ...m, status: 'offline' }));
            const latency = Date.now() - start;
            const reply = `I understand you said: "${text}". This is a demo response from the ImpressionCore B3 inference engine. Connect the Flask API backend to get real model outputs.`;
            setMessages((p) => [...p, { role: 'assistant', text: reply }]);
            const tokensUsed = text.split(' ').length + reply.split(' ').length;
            const tokPerSec = Math.round((reply.split(' ').length / Math.max(latency, 1)) * 1000);
            setStats((s) => ({
                messages: s.messages + 2,
                tokens: s.tokens + tokensUsed,
                avgLatency: Math.round((s.avgLatency * (s.messages - 1) + latency) / s.messages),
                tps: tokPerSec,
            }));
            setTelemetryLog((prev) => [...prev, {
                timestamp: new Date().toISOString(),
                prompt: text.slice(0, 80) + (text.length > 80 ? '...' : ''),
                model: modelInfo.name + ' (demo)',
                latencyMs: latency,
                tokensUsed,
                tokPerSec,
                settings: { ...settings },
            }]);
        } finally {
            setSending(false);
        }
    };

    return (
        <ContentArea title="Inference" subtitle="Chat with your trained model in real-time.">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Chat Panel — 2 cols */}
                <div className="lg:col-span-2">
                    <Card className="flex flex-col h-[600px]">
                        {/* Header */}
                        <div className="pb-4 border-b border-ic-border space-y-2">
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-cyan to-accent-indigo flex items-center justify-center shrink-0">
                                    <Bot size={16} className="text-white" />
                                </div>
                                <div className="min-w-0">
                                    <div className="text-sm font-semibold text-white truncate">{modelInfo.name}</div>
                                    <div className="flex items-center gap-1.5 text-[10px] text-gray-300">
                                        <span className={cn(
                                            'w-1.5 h-1.5 rounded-full',
                                            modelInfo.status === 'online' && 'bg-accent-success animate-pulse',
                                            modelInfo.status === 'offline' && 'bg-accent-danger',
                                            modelInfo.status === 'checking' && 'bg-accent-warning animate-pulse',
                                        )} />
                                        {modelInfo.status === 'online' ? 'Online' : modelInfo.status === 'checking' ? 'Connecting...' : 'Offline'}
                                    </div>
                                </div>
                                {/* Model dropdown */}
                                <div className="relative ml-auto">
                                    <select
                                        value={selectedModel}
                                        onChange={(e) => {
                                            setSelectedModel(e.target.value);
                                            const m = availableModels.find((mod) => mod.id === e.target.value);
                                            if (m) {
                                                setModelInfo((prev) => ({ ...prev, name: m.name }));
                                                toast(`Model set to ${m.name} — will load on next message`, { icon: '\u2699\uFE0F' });
                                            }
                                        }}
                                        className="appearance-none bg-ic-surface border border-ic-border rounded-lg px-3 py-1.5 pr-7 text-xs text-white cursor-pointer focus:outline-none focus:border-accent-cyan max-w-[200px]"
                                    >
                                        {availableModels.map((m) => (
                                            <option key={m.id} value={m.id}>{m.name}</option>
                                        ))}
                                    </select>
                                    <ChevronDown size={12} className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                                </div>
                                {/* Model path */}
                                {selectedModelObj?.path && (
                                    <span className="text-[10px] font-mono text-txt-muted truncate max-w-[220px]" title={selectedModelObj.path}>
                                        {selectedModelObj.path}
                                    </span>
                                )}
                                {/* Include Checkpoints toggle */}
                                <label className="flex items-center gap-1.5 shrink-0 cursor-pointer" title="Include all models and checkpoints from F:\\models\\checkpoints">
                                    <input
                                        type="checkbox"
                                        checked={includeCheckpoints}
                                        onChange={(e) => setIncludeCheckpoints(e.target.checked)}
                                        className="w-3.5 h-3.5 rounded border-ic-border bg-ic-surface text-accent-cyan focus:ring-accent-cyan cursor-pointer"
                                    />
                                    <FolderOpen size={12} className="text-txt-muted" />
                                    <span className="text-[10px] text-txt-muted whitespace-nowrap">Include all Checkpoints</span>
                                </label>
                            </div>
                            {/* Path detail row */}
                            {selectedModelObj?.path && (
                                <div className="flex items-center gap-1.5 text-[10px] text-txt-muted pl-11">
                                    <FolderOpen size={10} className="shrink-0" />
                                    <span className="font-mono truncate">{selectedModelObj.path}</span>
                                    <span className="text-accent-cyan/60">{' \u00b7 '}{selectedModelObj.type}</span>
                                </div>
                            )}
                        </div>

                        {/* Messages */}
                        <div className="flex-1 overflow-y-auto py-4 space-y-4">
                            {messages.map((msg, i) => (
                                <div key={i} className={cn('flex gap-3', msg.role === 'user' ? 'justify-end' : 'justify-start')}>
                                    {msg.role === 'assistant' && (
                                        <div className="w-7 h-7 rounded-full bg-accent-cyan/20 flex items-center justify-center shrink-0">
                                            <Bot size={14} className="text-accent-cyan" />
                                        </div>
                                    )}
                                    <div className={cn(
                                        'max-w-[75%] rounded-2xl px-4 py-2.5 text-sm',
                                        msg.role === 'user'
                                            ? 'bg-gradient-to-r from-accent-cyan to-accent-indigo text-white rounded-br-md'
                                            : 'bg-ic-surface text-txt-primary rounded-bl-md'
                                    )}>
                                        {msg.text}
                                    </div>
                                    {msg.role === 'user' && (
                                        <div className="w-7 h-7 rounded-full bg-accent-indigo/20 flex items-center justify-center shrink-0">
                                            <User size={14} className="text-accent-indigo" />
                                        </div>
                                    )}
                                </div>
                            ))}
                            {sending && (
                                <div className="flex gap-3">
                                    <div className="w-7 h-7 rounded-full bg-accent-cyan/20 flex items-center justify-center shrink-0">
                                        <Bot size={14} className="text-accent-cyan" />
                                    </div>
                                    <div className="bg-ic-surface rounded-2xl rounded-bl-md px-4 py-3">
                                        <div className="flex gap-1">
                                            <span className="w-2 h-2 bg-accent-cyan rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                            <span className="w-2 h-2 bg-accent-cyan rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                            <span className="w-2 h-2 bg-accent-cyan rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                        </div>
                                    </div>
                                </div>
                            )}
                            <div ref={chatEndRef} />
                        </div>

                        {/* Input */}
                        <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex gap-3 pt-4 border-t border-ic-border">
                            <input
                                className="input-dark flex-1"
                                placeholder="Type a message..."
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                disabled={sending}
                            />
                            <button type="submit" disabled={sending || !input.trim()} className="btn-primary px-4">
                                <Send size={16} />
                            </button>
                        </form>
                        <div className="flex items-center gap-1.5 mt-2 text-[10px] font-mono text-gray-300">
                            <span className={cn(
                                'w-1 h-1 rounded-full',
                                modelInfo.status === 'online' ? 'bg-accent-success' : modelInfo.status === 'checking' ? 'bg-accent-warning' : 'bg-accent-danger',
                            )} />
                            Model: {modelInfo.name}
                        </div>
                    </Card>

                    {/* Usage Monitor and Reporting */}
                    <Card className="mt-4">
                        <div className="flex items-center justify-between">
                            <CardTitle icon={BarChart3}>Usage Monitor and Reporting</CardTitle>
                            <button
                                onClick={() => {
                                    const now = new Date();
                                    const sessionDuration = Math.round((Date.now() - sessionStartRef.current) / 1000);
                                    const mins = Math.floor(sessionDuration / 60);
                                    const secs = sessionDuration % 60;
                                    const report = [
                                        '='.repeat(60),
                                        '  IMPRESSIONCORE INFERENCE TELEMETRY SNAPSHOT',
                                        '='.repeat(60),
                                        `  Generated: ${now.toLocaleString()}`,
                                        `  Session Duration: ${mins}m ${secs}s`,
                                        `  Model: ${modelInfo.name} (${modelInfo.status})`,
                                        `  Selected: ${selectedModelObj?.name || selectedModel}`,
                                        `  Path: ${selectedModelObj?.path || 'N/A'}`,
                                        '-'.repeat(60),
                                        '  SESSION TOTALS',
                                        '-'.repeat(60),
                                        `  Messages: ${stats.messages}`,
                                        `  Total Tokens: ${stats.tokens}`,
                                        `  Avg Latency: ${stats.avgLatency}ms`,
                                        `  Last Tokens/sec: ${stats.tps}`,
                                        '-'.repeat(60),
                                        '  GENERATION SETTINGS',
                                        '-'.repeat(60),
                                        `  Temperature: ${settings.temperature}`,
                                        `  Max Tokens: ${settings.maxTokens}`,
                                        `  Top-P: ${settings.topP}`,
                                        `  Top-K: ${settings.topK}`,
                                        `  Sampling: ${settings.sampling ? 'Enabled' : 'Disabled'}`,
                                        '-'.repeat(60),
                                        `  REQUEST LOG (${telemetryLog.length} requests)`,
                                        '-'.repeat(60),
                                        ...telemetryLog.map((t, i) => [
                                            `  #${i + 1}  ${new Date(t.timestamp).toLocaleTimeString()}`,
                                            `       Model: ${t.model}`,
                                            `       Prompt: "${t.prompt}"`,
                                            `       Latency: ${t.latencyMs}ms | Tokens: ${t.tokensUsed} | TPS: ${t.tokPerSec}`,
                                            `       Settings: temp=${t.settings.temperature} top_p=${t.settings.topP} top_k=${t.settings.topK}`,
                                        ]).flat(),
                                        '='.repeat(60),
                                    ].join('\n');
                                    const blob = new Blob([report], { type: 'text/plain' });
                                    const url = URL.createObjectURL(blob);
                                    const a = document.createElement('a');
                                    a.href = url;
                                    a.download = `inference_snapshot_${now.toISOString().replace(/[:.]/g, '-').slice(0, 19)}.txt`;
                                    a.click();
                                    URL.revokeObjectURL(url);
                                    toast.success('Snapshot report downloaded');
                                }}
                                className="flex items-center gap-1 px-2 py-1 text-[11px] rounded-md bg-accent-indigo/10 text-accent-indigo hover:bg-accent-indigo/20 transition-colors"
                                title="Download a snapshot report of current telemetry"
                            >
                                <Camera size={12} />
                                Snapshot
                            </button>
                        </div>
                        <div className="mt-3 space-y-3">
                            {/* Live metrics row */}
                            <div className="grid grid-cols-4 gap-2">
                                <div className="bg-ic-surface rounded-lg p-2 text-center">
                                    <div className="flex items-center justify-center gap-1 text-[10px] text-txt-muted mb-1"><Clock size={10} />Session</div>
                                    <div className="text-xs font-mono text-white">{Math.round((Date.now() - sessionStartRef.current) / 60000)}m</div>
                                </div>
                                <div className="bg-ic-surface rounded-lg p-2 text-center">
                                    <div className="flex items-center justify-center gap-1 text-[10px] text-txt-muted mb-1"><Cpu size={10} />Requests</div>
                                    <div className="text-xs font-mono text-white">{telemetryLog.length}</div>
                                </div>
                                <div className="bg-ic-surface rounded-lg p-2 text-center">
                                    <div className="flex items-center justify-center gap-1 text-[10px] text-txt-muted mb-1"><Zap size={10} />Tokens</div>
                                    <div className="text-xs font-mono text-white">{stats.tokens}</div>
                                </div>
                                <div className="bg-ic-surface rounded-lg p-2 text-center">
                                    <div className="flex items-center justify-center gap-1 text-[10px] text-txt-muted mb-1"><BarChart3 size={10} />TPS</div>
                                    <div className="text-xs font-mono text-white">{stats.tps}</div>
                                </div>
                            </div>
                            {/* Request log */}
                            <div className="max-h-[180px] overflow-y-auto space-y-1.5">
                                {telemetryLog.length === 0 ? (
                                    <div className="text-[11px] text-txt-muted text-center py-3">No requests yet — send a message to start collecting telemetry.</div>
                                ) : (
                                    telemetryLog.slice().reverse().map((t, i) => (
                                        <div key={i} className="bg-ic-surface rounded-lg px-3 py-2 text-[11px] font-mono">
                                            <div className="flex items-center justify-between text-txt-muted">
                                                <span>#{telemetryLog.length - i} {new Date(t.timestamp).toLocaleTimeString()}</span>
                                                <span className="text-accent-cyan">{t.model}</span>
                                            </div>
                                            <div className="text-white mt-0.5 truncate" title={t.prompt}>"{t.prompt}"</div>
                                            <div className="flex items-center gap-3 mt-1 text-txt-muted">
                                                <span><Clock size={9} className="inline mr-0.5" />{t.latencyMs}ms</span>
                                                <span><Zap size={9} className="inline mr-0.5" />{t.tokensUsed} tok</span>
                                                <span><BarChart3 size={9} className="inline mr-0.5" />{t.tokPerSec} TPS</span>
                                                <span>temp={t.settings.temperature}</span>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    </Card>
                </div>

                {/* Settings — 1 col */}
                <div className="space-y-4">
                    <Card>
                        <div className="flex items-center justify-between">
                            <CardTitle icon={Settings2}>Generation Settings</CardTitle>
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={handleAnalyze}
                                    disabled={analyzing}
                                    className="flex items-center gap-1 px-2 py-1 text-[11px] rounded-md bg-accent-cyan/10 text-accent-cyan hover:bg-accent-cyan/20 disabled:opacity-50 transition-colors"
                                    title="Auto-configure settings for selected model"
                                >
                                    <Sparkles size={12} className={analyzing ? 'animate-spin' : ''} />
                                    {analyzing ? 'Analyzing...' : 'Analyze'}
                                </button>
                                <button
                                    onClick={handleSaveSettings}
                                    className="flex items-center gap-1 px-2 py-1 text-[11px] rounded-md bg-accent-success/10 text-accent-success hover:bg-accent-success/20 transition-colors"
                                    title="Save current settings"
                                >
                                    <Save size={12} />
                                    Save
                                </button>
                            </div>
                        </div>
                        <div className="mt-4 space-y-5">
                            <Slider label="Temperature" value={settings.temperature} min={0} max={2} step={0.05}
                                onChange={(e) => updateSetting('temperature', +e.target.value)} />
                            <Input label="Max Tokens" type="number" value={settings.maxTokens}
                                onChange={(e) => updateSetting('maxTokens', +e.target.value)} />
                            <Slider label="Top-P" value={settings.topP} min={0} max={1} step={0.05}
                                onChange={(e) => updateSetting('topP', +e.target.value)} />
                            <Input label="Top-K" type="number" value={settings.topK}
                                onChange={(e) => updateSetting('topK', +e.target.value)} />
                            <Toggle label="Sampling" checked={settings.sampling}
                                onChange={(e) => updateSetting('sampling', e.target.checked)} />
                        </div>
                    </Card>

                    <Card>
                        <CardTitle>Session Stats</CardTitle>
                        <div className="grid grid-cols-2 gap-3 mt-4">
                            <StatCard label="Messages" value={stats.messages} />
                            <StatCard label="Tokens" value={stats.tokens} />
                            <StatCard label="Avg Latency" value={`${stats.avgLatency}ms`} />
                            <StatCard label="Tokens/sec" value={stats.tps} />
                        </div>
                    </Card>
                </div>
            </div>
        </ContentArea>
    );
}
