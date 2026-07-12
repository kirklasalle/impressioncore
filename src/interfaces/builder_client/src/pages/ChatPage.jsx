import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, Settings2, ChevronDown, ChevronUp, FolderOpen, Save, Info, Cpu, Clock, Zap, BarChart3 } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Slider, Input, Toggle, StatCard } from '../components/ui';
import { runInference, getModelInfo, getAvailableModels, getInferenceSettings, saveInferenceSettings, analyzeModelSettings } from '../lib/api';
import { cn } from '../lib/utils';
import toast from 'react-hot-toast';

/* ─── localStorage helpers for chat history persistence ─── */
const CHAT_STORAGE_KEY = 'impressioncore_chat_history';
function loadChatHistory() {
    try {
        const raw = localStorage.getItem(CHAT_STORAGE_KEY);
        if (raw) { const parsed = JSON.parse(raw); if (Array.isArray(parsed) && parsed.length) return parsed; }
    } catch { /* ignore */ }
    return [{ role: 'assistant', text: 'Welcome to the ImpressionCore Chat interface! Ask me anything about your model, training, or configuration.' }];
}
function saveChatHistory(messages) {
    try { localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messages.slice(-200))); } catch { /* ignore */ }
}

/* ─── Default settings ─── */
const DEFAULT_SETTINGS = { temperature: 0.8, maxTokens: 512, topP: 0.9, topK: 50, sampling: true, stream: true };

export default function ChatPage() {
    /* ── Chat state ── */
    const [messages, setMessages] = useState(loadChatHistory);
    const [input, setInput] = useState('');
    const [sending, setSending] = useState(false);
    const chatRef = useRef(null);

    /* ── Settings state ── */
    const [settings, setSettings] = useState({ ...DEFAULT_SETTINGS });
    const updateSetting = (key, val) => setSettings((p) => ({ ...p, [key]: val }));

    /* ── Model state ── */
    const [modelInfo, setModelInfo] = useState({ name: 'ImpressionCore', status: 'checking' });
    const [availableModels, setAvailableModels] = useState([]);
    const [selectedModel, setSelectedModel] = useState('');
    const [includeCheckpoints, setIncludeCheckpoints] = useState(false);
    const [analyzing, setAnalyzing] = useState(false);
    const selectedModelObj = availableModels.find((m) => m.id === selectedModel);

    /* ── Stats state ── */
    const [stats, setStats] = useState({ messages: 1, tokens: 0, avgLatency: 0, tps: 0 });
    const sessionStartRef = useRef(Date.now());

    /* ── Educational panel state ── */
    const [showLearn, setShowLearn] = useState(false);

    /* ── Scroll on new messages ── */
    useEffect(() => {
        chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: 'smooth' });
    }, [messages]);

    /* ── Persist chat to localStorage ── */
    useEffect(() => { saveChatHistory(messages); }, [messages]);

    /* ── Fetch model info on mount ── */
    useEffect(() => {
        getModelInfo()
            .then(({ data }) => {
                setModelInfo({ name: data.name || 'ImpressionCore-B3', status: data.status === 'active' ? 'online' : 'offline' });
            })
            .catch(() => { setModelInfo((m) => ({ ...m, status: 'offline' })); });
    }, []);

    /* ── Fetch available models ── */
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

    /* ── Load saved inference settings on mount ── */
    useEffect(() => {
        getInferenceSettings()
            .then(({ data }) => { if (data.success && data.config) setSettings((prev) => ({ ...prev, ...data.config })); })
            .catch(() => { });
    }, []);

    /* ── Quick prompts ── */
    const QUICK_PROMPTS = [
        'What is the current model architecture?',
        'How much VRAM will training require?',
        'Explain the B3 training pipeline',
        'What optimizations are available?',
    ];

    /* ── Analyze model settings ── */
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
        } catch { toast.error('Failed to analyze model'); }
        finally { setAnalyzing(false); }
    };

    /* ── Save settings ── */
    const handleSaveSettings = async () => {
        try {
            const { data } = await saveInferenceSettings(settings);
            if (data.success) toast.success('Settings saved');
        } catch { toast.error('Failed to save settings'); }
    };

    /* ── Send message — real inference with demo fallback ── */
    const handleSend = async (text) => {
        const msg = text || input.trim();
        if (!msg || sending) return;
        setInput('');
        setMessages((p) => [...p, { role: 'user', text: msg }]);
        setSending(true);
        const start = Date.now();

        try {
            const { data } = await runInference({ prompt: msg, model: selectedModel, ...settings });
            const latency = Date.now() - start;
            const reply = data.response || data.text || 'No response generated.';
            if (data.model_name) setModelInfo((m) => ({ ...m, name: data.model_name, status: 'online' }));
            setMessages((p) => [...p, { role: 'assistant', text: reply }]);
            const tokensUsed = data.tokens_used || msg.split(' ').length + reply.split(' ').length;
            const tokPerSec = data.tokens_per_second || Math.round((reply.split(' ').length / Math.max(latency, 1)) * 1000);
            setStats((s) => ({
                messages: s.messages + 2,
                tokens: s.tokens + tokensUsed,
                avgLatency: Math.round((s.avgLatency * (s.messages - 1) + latency) / Math.max(s.messages, 1)),
                tps: tokPerSec,
            }));
        } catch {
            setModelInfo((m) => ({ ...m, status: 'offline' }));
            const latency = Date.now() - start;
            const reply = `I understand you said: "${msg}". The inference backend is currently unavailable — this is a demo response. Start the Flask API backend to get real model outputs.`;
            setMessages((p) => [...p, { role: 'assistant', text: reply }]);
            const tokensUsed = msg.split(' ').length + reply.split(' ').length;
            setStats((s) => ({
                messages: s.messages + 2,
                tokens: s.tokens + tokensUsed,
                avgLatency: Math.round((s.avgLatency * (s.messages - 1) + latency) / Math.max(s.messages, 1)),
                tps: Math.round((reply.split(' ').length / Math.max(latency, 1)) * 1000),
            }));
        } finally {
            setSending(false);
        }
    };

    /* ── Clear chat history ── */
    const handleClearChat = () => {
        const initial = [{ role: 'assistant', text: 'Chat cleared. How can I help you?' }];
        setMessages(initial);
        setStats({ messages: 1, tokens: 0, avgLatency: 0, tps: 0 });
        sessionStartRef.current = Date.now();
        toast.success('Chat history cleared');
    };

    return (
        <ContentArea title="Chat" subtitle="Conversational interface for model queries and assistance.">
            {/* ──────── Educational "What is Inference?" Panel ──────── */}
            <div className="mb-6">
                <button
                    onClick={() => setShowLearn((v) => !v)}
                    className="flex items-center gap-2 text-sm text-accent-cyan hover:text-accent-cyan/80 transition-colors"
                >
                    <Info size={16} />
                    <span>{showLearn ? 'Hide' : 'Learn about'} Chat Inference</span>
                    {showLearn ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                </button>
                {showLearn && (
                    <Card className="mt-3">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 text-sm text-txt-primary leading-relaxed">
                            <div>
                                <h4 className="text-accent-cyan font-semibold mb-2 flex items-center gap-1.5">
                                    <Cpu size={14} /> What is Inference?
                                </h4>
                                <p className="text-txt-secondary text-xs">
                                    <strong className="text-txt-primary">Inference</strong> is the process of using a trained AI model to generate
                                    predictions or responses from new input. Unlike <em>training</em> (where the model learns from data),
                                    inference is where the model <em>applies</em> what it learned. When you type a message here, the model
                                    processes your text and generates a response — that's inference in action.
                                </p>
                            </div>
                            <div>
                                <h4 className="text-accent-cyan font-semibold mb-2 flex items-center gap-1.5">
                                    <Zap size={14} /> How Chat Inference Works
                                </h4>
                                <ol className="text-txt-secondary text-xs space-y-1 list-decimal list-inside">
                                    <li><strong className="text-txt-primary">Tokenization</strong> — Your message is split into tokens (sub-word units) the model understands</li>
                                    <li><strong className="text-txt-primary">Forward Pass</strong> — Tokens flow through the transformer layers, producing probability distributions for the next token</li>
                                    <li><strong className="text-txt-primary">Sampling</strong> — A token is selected from the distribution using your Temperature, Top-K, and Top-P settings</li>
                                    <li><strong className="text-txt-primary">Detokenization</strong> — Selected tokens are converted back into readable text</li>
                                    <li><strong className="text-txt-primary">Repeat</strong> — Steps 2–4 repeat until a stop token or Max Tokens limit is reached</li>
                                </ol>
                            </div>
                            <div>
                                <h4 className="text-accent-cyan font-semibold mb-2 flex items-center gap-1.5">
                                    <Settings2 size={14} /> Key Parameters Explained
                                </h4>
                                <dl className="text-txt-secondary text-xs space-y-1.5">
                                    <div><dt className="text-txt-primary font-medium inline">Temperature</dt> — Controls randomness. Low (0.1) = deterministic and focused. High (1.5) = creative and varied.</div>
                                    <div><dt className="text-txt-primary font-medium inline">Top-K</dt> — Limits sampling to the K most probable tokens. Lower K = more focused.</div>
                                    <div><dt className="text-txt-primary font-medium inline">Top-P (Nucleus)</dt> — Samples from the smallest set of tokens whose cumulative probability exceeds P. Dynamically adjusts the candidate pool.</div>
                                    <div><dt className="text-txt-primary font-medium inline">Max Tokens</dt> — Maximum number of tokens the model will generate in its response.</div>
                                </dl>
                            </div>
                            <div>
                                <h4 className="text-accent-indigo font-semibold mb-2 flex items-center gap-1.5">
                                    <FolderOpen size={14} /> Model Types
                                </h4>
                                <dl className="text-txt-secondary text-xs space-y-1.5">
                                    <div><dt className="text-txt-primary font-medium inline">Checkpoint (.pt)</dt> — A snapshot of model weights saved during training. May include optimizer state. Select these to test specific training stages.</div>
                                    <div><dt className="text-txt-primary font-medium inline">HuggingFace Model</dt> — A directory containing config.json, tokenizer files, and weights in a standardized format. Ready for production use.</div>
                                </dl>
                            </div>
                            <div className="md:col-span-2 lg:col-span-2">
                                <h4 className="text-accent-success font-semibold mb-2 flex items-center gap-1.5">
                                    <BarChart3 size={14} /> ImpressionCore on Constrained Hardware
                                </h4>
                                <p className="text-txt-secondary text-xs">
                                    ImpressionCore B3 is designed to run inference on consumer GPUs like the GTX 1050 Ti (4 GB VRAM).
                                    Optimizations include <strong className="text-txt-primary">FP16 mixed precision</strong> (halves memory),
                                    <strong className="text-txt-primary"> Grouped-Query Attention</strong> (reduces KV cache by 3×),
                                    <strong className="text-txt-primary"> Flash Attention 2</strong> (faster with less memory),
                                    and <strong className="text-txt-primary"> INT4/INT8 quantization</strong> for even smaller footprints.
                                    The model fits in ~2.1 GB with FP16 — well within the 4 GB target.
                                </p>
                            </div>
                        </div>
                    </Card>
                )}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* ──────── Chat Panel — 3 cols ──────── */}
                <div className="lg:col-span-3">
                    <Card className="flex flex-col h-[600px]">
                        {/* Header with model selector */}
                        <div className="pb-3 border-b border-ic-border space-y-2">
                            <div className="flex items-center gap-3">
                                <Sparkles size={18} className="text-accent-cyan shrink-0" />
                                <div className="min-w-0">
                                    <span className="text-sm font-semibold text-txt-primary">ImpressionCore Assistant</span>
                                    <div className="flex items-center gap-1.5 text-[10px] text-gray-300">
                                        <span className={cn(
                                            'w-1.5 h-1.5 rounded-full',
                                            modelInfo.status === 'online' && 'bg-accent-success animate-pulse',
                                            modelInfo.status === 'offline' && 'bg-accent-danger',
                                            modelInfo.status === 'checking' && 'bg-accent-warning animate-pulse',
                                        )} />
                                        {modelInfo.status === 'online' ? 'Online' : modelInfo.status === 'checking' ? 'Connecting...' : 'Offline'}
                                        {modelInfo.name && <span className="text-txt-muted ml-1">· {modelInfo.name}</span>}
                                    </div>
                                </div>

                                {/* ── Model Selection Dropdown (upper-right) ── */}
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
                                        className="appearance-none bg-ic-surface border border-ic-border rounded-lg px-3 py-1.5 pr-7 text-xs text-white cursor-pointer focus:outline-none focus:border-accent-cyan max-w-[220px]"
                                    >
                                        {availableModels.length === 0 && <option value="">No models found</option>}
                                        {availableModels.map((m) => (
                                            <option key={m.id} value={m.id}>
                                                {m.name} {m.type === 'huggingface' ? '(HF)' : m.type === 'checkpoint' ? '(ckpt)' : ''}
                                            </option>
                                        ))}
                                    </select>
                                    <ChevronDown size={12} className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                                </div>

                                {/* Include All Checkpoints toggle */}
                                <label className="flex items-center gap-1.5 shrink-0 cursor-pointer" title="Include all models and checkpoints from F:\models\checkpoints">
                                    <input
                                        type="checkbox"
                                        checked={includeCheckpoints}
                                        onChange={(e) => setIncludeCheckpoints(e.target.checked)}
                                        className="w-3.5 h-3.5 rounded border-ic-border bg-ic-surface text-accent-cyan focus:ring-accent-cyan cursor-pointer"
                                    />
                                    <FolderOpen size={12} className="text-txt-muted" />
                                    <span className="text-[10px] text-txt-muted whitespace-nowrap">All Checkpoints</span>
                                </label>
                            </div>
                            {/* Path detail row */}
                            {selectedModelObj?.path && (
                                <div className="flex items-center gap-1.5 text-[10px] text-txt-muted pl-7">
                                    <FolderOpen size={10} className="shrink-0" />
                                    <span className="font-mono truncate">{selectedModelObj.path}</span>
                                    <span className="text-accent-cyan/60">{' · '}{selectedModelObj.type}</span>
                                </div>
                            )}
                        </div>

                        {/* Messages */}
                        <div ref={chatRef} className="flex-1 overflow-y-auto py-4 space-y-4">
                            {messages.map((msg, i) => (
                                <div key={i} className={cn('flex gap-3', msg.role === 'user' ? 'justify-end' : 'justify-start')}>
                                    {msg.role === 'assistant' && (
                                        <div className="w-7 h-7 rounded-full bg-accent-cyan/20 flex items-center justify-center shrink-0 mt-0.5">
                                            <Bot size={14} className="text-accent-cyan" />
                                        </div>
                                    )}
                                    <div className={cn(
                                        'max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed',
                                        msg.role === 'user'
                                            ? 'bg-gradient-to-r from-accent-cyan to-accent-indigo text-white rounded-br-md'
                                            : 'bg-ic-surface text-txt-primary rounded-bl-md'
                                    )}>
                                        {msg.text}
                                    </div>
                                    {msg.role === 'user' && (
                                        <div className="w-7 h-7 rounded-full bg-accent-indigo/20 flex items-center justify-center shrink-0 mt-0.5">
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
                        </div>

                        {/* Quick prompts */}
                        <div className="flex gap-2 pb-3 overflow-x-auto">
                            {QUICK_PROMPTS.map((p, i) => (
                                <button key={i} onClick={() => handleSend(p)}
                                    className="px-3 py-1.5 rounded-full border border-ic-border bg-ic-surface text-[11px] text-txt-secondary hover:border-accent-cyan/30 hover:text-accent-cyan transition-colors whitespace-nowrap">
                                    {p}
                                </button>
                            ))}
                        </div>

                        <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex gap-3 pt-3 border-t border-ic-border">
                            <input className="input-dark flex-1" placeholder="Ask anything..." value={input}
                                onChange={(e) => setInput(e.target.value)} disabled={sending} />
                            <button type="submit" disabled={sending || !input.trim()} className="btn-primary px-4">
                                <Send size={16} />
                            </button>
                        </form>
                    </Card>
                </div>

                {/* ──────── Settings Sidebar — 1 col ──────── */}
                <div className="space-y-4">
                    {/* Model Info Card */}
                    {selectedModelObj && (
                        <Card>
                            <CardTitle icon={Cpu}>Model Info</CardTitle>
                            <dl className="mt-3 space-y-1.5 text-xs">
                                <div className="flex justify-between">
                                    <dt className="text-txt-muted">Name</dt>
                                    <dd className="text-txt-primary font-medium truncate ml-2 max-w-[140px]" title={selectedModelObj.name}>{selectedModelObj.name}</dd>
                                </div>
                                <div className="flex justify-between">
                                    <dt className="text-txt-muted">Type</dt>
                                    <dd>
                                        <span className={cn(
                                            'px-1.5 py-0.5 rounded text-[10px] font-medium',
                                            selectedModelObj.type === 'huggingface' ? 'bg-accent-indigo/15 text-accent-indigo' : 'bg-accent-cyan/15 text-accent-cyan'
                                        )}>
                                            {selectedModelObj.type === 'huggingface' ? 'HuggingFace' : 'Checkpoint'}
                                        </span>
                                    </dd>
                                </div>
                                <div className="flex justify-between">
                                    <dt className="text-txt-muted">Provider</dt>
                                    <dd className="text-txt-primary text-[11px]">Local</dd>
                                </div>
                                {selectedModelObj.size_mb && (
                                    <div className="flex justify-between">
                                        <dt className="text-txt-muted">Size</dt>
                                        <dd className="text-txt-primary text-[11px]">{selectedModelObj.size_mb} MB</dd>
                                    </div>
                                )}
                                {selectedModelObj.last_modified && (
                                    <div className="flex justify-between">
                                        <dt className="text-txt-muted">Modified</dt>
                                        <dd className="text-txt-primary text-[11px]">{new Date(selectedModelObj.last_modified * 1000).toLocaleDateString()}</dd>
                                    </div>
                                )}
                                {selectedModelObj.config_info && (
                                    <>
                                        {selectedModelObj.config_info.model_type && (
                                            <div className="flex justify-between">
                                                <dt className="text-txt-muted">Architecture</dt>
                                                <dd className="text-txt-primary text-[11px]">{selectedModelObj.config_info.model_type}</dd>
                                            </div>
                                        )}
                                        {selectedModelObj.config_info.hidden_size && (
                                            <div className="flex justify-between">
                                                <dt className="text-txt-muted">Hidden Size</dt>
                                                <dd className="text-txt-primary text-[11px]">{selectedModelObj.config_info.hidden_size}</dd>
                                            </div>
                                        )}
                                        {selectedModelObj.config_info.num_layers && (
                                            <div className="flex justify-between">
                                                <dt className="text-txt-muted">Layers</dt>
                                                <dd className="text-txt-primary text-[11px]">{selectedModelObj.config_info.num_layers}</dd>
                                            </div>
                                        )}
                                        {selectedModelObj.config_info.num_attention_heads && (
                                            <div className="flex justify-between">
                                                <dt className="text-txt-muted">Attn Heads</dt>
                                                <dd className="text-txt-primary text-[11px]">{selectedModelObj.config_info.num_attention_heads}</dd>
                                            </div>
                                        )}
                                        {selectedModelObj.config_info.vocab_size && (
                                            <div className="flex justify-between">
                                                <dt className="text-txt-muted">Vocab Size</dt>
                                                <dd className="text-txt-primary text-[11px]">{selectedModelObj.config_info.vocab_size.toLocaleString()}</dd>
                                            </div>
                                        )}
                                    </>
                                )}
                                <div className="pt-1">
                                    <span className="text-[10px] text-txt-muted font-mono truncate block" title={selectedModelObj.path}>{selectedModelObj.path}</span>
                                </div>
                            </dl>
                        </Card>
                    )}

                    {/* Generation Settings Card */}
                    <Card>
                        <div className="flex items-center justify-between">
                            <CardTitle icon={Settings2}>Settings</CardTitle>
                            <div className="flex items-center gap-1.5">
                                <button
                                    onClick={handleAnalyze}
                                    disabled={analyzing || !selectedModel}
                                    className="flex items-center gap-1 px-2 py-1 text-[10px] rounded-md bg-accent-cyan/10 text-accent-cyan hover:bg-accent-cyan/20 disabled:opacity-50 transition-colors"
                                    title="Auto-configure settings for selected model"
                                >
                                    <Sparkles size={10} className={analyzing ? 'animate-spin' : ''} />
                                    {analyzing ? '...' : 'Analyze'}
                                </button>
                                <button
                                    onClick={handleSaveSettings}
                                    className="flex items-center gap-1 px-2 py-1 text-[10px] rounded-md bg-accent-success/10 text-accent-success hover:bg-accent-success/20 transition-colors"
                                    title="Save current settings"
                                >
                                    <Save size={10} />
                                    Save
                                </button>
                            </div>
                        </div>
                        <div className="mt-4 space-y-4">
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
                            <Toggle label="Streaming" checked={settings.stream}
                                onChange={(e) => updateSetting('stream', e.target.checked)} />
                            <button
                                onClick={() => { setSettings({ ...DEFAULT_SETTINGS }); toast.success('Settings reset to defaults'); }}
                                className="w-full text-center text-[10px] text-txt-muted hover:text-accent-cyan py-1 transition-colors"
                            >
                                Reset to Defaults
                            </button>
                        </div>
                    </Card>

                    {/* Session Stats Card */}
                    <Card>
                        <CardTitle>Session Stats</CardTitle>
                        <div className="grid grid-cols-2 gap-3 mt-3">
                            <StatCard label="Messages" value={stats.messages} />
                            <StatCard label="Tokens" value={stats.tokens} />
                            <StatCard label="Avg Latency" value={`${stats.avgLatency}ms`} />
                            <StatCard label="Tokens/sec" value={stats.tps} />
                        </div>
                        <div className="flex items-center justify-between mt-3 pt-2 border-t border-ic-border">
                            <div className="flex items-center gap-1 text-[10px] text-txt-muted">
                                <Clock size={10} />
                                <span>{Math.round((Date.now() - sessionStartRef.current) / 60000)}m session</span>
                            </div>
                            <button
                                onClick={handleClearChat}
                                className="text-[10px] text-accent-danger/70 hover:text-accent-danger transition-colors"
                            >
                                Clear Chat
                            </button>
                        </div>
                    </Card>
                </div>
            </div>
        </ContentArea>
    );
}
