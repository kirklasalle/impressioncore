import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send, Settings2, Bot, User } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Slider, Input, Toggle, StatCard } from '../components/ui';
import { runInference } from '../lib/api';
import { cn } from '../lib/utils';

export default function InferencePage() {
    const [messages, setMessages] = useState([
        { role: 'assistant', text: 'Hello! I\'m the ImpressionCore B3 model. How can I help you?' },
    ]);
    const [input, setInput] = useState('');
    const [sending, setSending] = useState(false);
    const [settings, setSettings] = useState({
        temperature: 0.7, maxTokens: 512, topP: 0.9, topK: 50, sampling: true,
    });
    const [stats, setStats] = useState({ messages: 1, tokens: 0, avgLatency: 0, tps: 0 });
    const chatEndRef = useRef(null);

    const updateSetting = (key, val) => setSettings((p) => ({ ...p, [key]: val }));

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async () => {
        const text = input.trim();
        if (!text || sending) return;
        setInput('');
        setMessages((p) => [...p, { role: 'user', text }]);
        setSending(true);
        const start = Date.now();

        try {
            const { data } = await runInference({ prompt: text, ...settings });
            const latency = Date.now() - start;
            const reply = data.response || data.text || 'No response generated.';
            setMessages((p) => [...p, { role: 'assistant', text: reply }]);
            setStats((s) => ({
                messages: s.messages + 2,
                tokens: s.tokens + (data.tokens_used || text.split(' ').length + reply.split(' ').length),
                avgLatency: Math.round((s.avgLatency * (s.messages - 1) + latency) / s.messages),
                tps: data.tokens_per_second || Math.round((reply.split(' ').length / latency) * 1000),
            }));
        } catch {
            // Demo fallback
            const latency = Date.now() - start;
            const reply = `I understand you said: "${text}". This is a demo response from the ImpressionCore B3 inference engine. Connect the Flask API backend to get real model outputs.`;
            setMessages((p) => [...p, { role: 'assistant', text: reply }]);
            setStats((s) => ({
                messages: s.messages + 2,
                tokens: s.tokens + text.split(' ').length + reply.split(' ').length,
                avgLatency: Math.round((s.avgLatency * (s.messages - 1) + latency) / s.messages),
                tps: Math.round((reply.split(' ').length / Math.max(latency, 1)) * 1000),
            }));
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
                        <div className="flex items-center gap-3 pb-4 border-b border-ic-border">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-cyan to-accent-indigo flex items-center justify-center">
                                <Bot size={16} className="text-white" />
                            </div>
                            <div>
                                <div className="text-sm font-semibold text-txt-primary">ImpressionCore B3</div>
                                <div className="flex items-center gap-1.5 text-[10px] text-txt-muted">
                                    <span className="w-1.5 h-1.5 rounded-full bg-accent-success animate-pulse" />
                                    Online
                                </div>
                            </div>
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
                    </Card>
                </div>

                {/* Settings — 1 col */}
                <div className="space-y-4">
                    <Card>
                        <CardTitle icon={Settings2}>Generation Settings</CardTitle>
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
