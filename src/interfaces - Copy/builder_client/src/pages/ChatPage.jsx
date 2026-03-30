import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, Send, Bot, User, Sparkles, Settings2 } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Slider, Toggle, StatCard } from '../components/ui';
import { cn } from '../lib/utils';

export default function ChatPage() {
    const [messages, setMessages] = useState([
        { role: 'assistant', text: 'Welcome to the ImpressionCore Chat interface! Ask me anything about your model, training, or configuration.' },
    ]);
    const [input, setInput] = useState('');
    const [sending, setSending] = useState(false);
    const [settings, setSettings] = useState({ temperature: 0.8, stream: true });
    const chatRef = useRef(null);

    useEffect(() => {
        chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: 'smooth' });
    }, [messages]);

    const QUICK_PROMPTS = [
        'What is the current model architecture?',
        'How much VRAM will training require?',
        'Explain the B3 training pipeline',
        'What optimizations are available?',
    ];

    const handleSend = async (text) => {
        const msg = text || input.trim();
        if (!msg || sending) return;
        setInput('');
        setMessages((p) => [...p, { role: 'user', text: msg }]);
        setSending(true);

        // Simulate response
        await new Promise((r) => setTimeout(r, 800 + Math.random() * 1200));
        const responses = {
            'architecture': 'The B3 architecture is a 24-layer transformer with 768 hidden dim, 12 attention heads using GQA (3:1 ratio), SwiGLU FFN, RoPE positional encoding, and Flash Attention 2. It supports text, vision, and audio modalities through a shared embedding space.',
            'vram': 'With FP16 precision and gradient checkpointing enabled, training requires approximately 2.1 GB for the model + 1.5 GB for optimizer states + 0.3 GB overhead = ~3.9 GB total, fitting within the 4 GB GTX 1050 Ti target.',
            'pipeline': 'The B3 pipeline has 9 steps: System Setup → Data Prep → Tokenizer → Model Definition → Training → Evaluation → Inference → Deployment. Each step builds on the previous with validation checkpoints.',
            'optimization': 'Available optimizations: FP16/BF16 mixed precision, gradient checkpointing, Flash Attention 2, GQA (reduces KV cache), INT8/INT4 quantization for inference, knowledge distillation, and structured pruning.',
        };

        const key = Object.keys(responses).find((k) => msg.toLowerCase().includes(k));
        const reply = key ? responses[key]
            : `I understand your question about "${msg}". In the context of ImpressionCore B3, this relates to the model builder pipeline. For detailed information, check the relevant pipeline step or documentation page.`;

        setMessages((p) => [...p, { role: 'assistant', text: reply }]);
        setSending(false);
    };

    return (
        <ContentArea title="Chat" subtitle="Conversational interface for model queries and assistance.">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Chat — 3 cols */}
                <div className="lg:col-span-3">
                    <Card className="flex flex-col h-[600px]">
                        <div className="flex items-center gap-3 pb-3 border-b border-ic-border">
                            <Sparkles size={18} className="text-accent-cyan" />
                            <span className="text-sm font-semibold text-txt-primary">ImpressionCore Assistant</span>
                            <span className="w-1.5 h-1.5 rounded-full bg-accent-success animate-pulse" />
                        </div>

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

                {/* Settings — 1 col */}
                <div className="space-y-4">
                    <Card>
                        <CardTitle icon={Settings2}>Settings</CardTitle>
                        <div className="mt-4 space-y-4">
                            <Slider label="Temperature" value={settings.temperature} min={0} max={2} step={0.1}
                                onChange={(e) => setSettings((p) => ({ ...p, temperature: +e.target.value }))} />
                            <Toggle label="Streaming" checked={settings.stream}
                                onChange={(e) => setSettings((p) => ({ ...p, stream: e.target.checked }))} />
                        </div>
                    </Card>
                    <Card>
                        <div className="grid grid-cols-2 gap-3">
                            <StatCard label="Messages" value={messages.length} />
                            <StatCard label="Session" value="Active" />
                        </div>
                    </Card>
                </div>
            </div>
        </ContentArea>
    );
}
