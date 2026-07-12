import React, { useState } from 'react';
import { Type, Play, Loader2, Sparkles } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Input, Select, Toggle, Badge, StatCard } from '../components/ui';
import { configureTokenizer, tokenizeText } from '../lib/api';
import { TOKENIZER_TYPES } from '../lib/constants';
import toast from 'react-hot-toast';

const TOKEN_COLORS = [
    'bg-accent-cyan/20 text-accent-cyan',
    'bg-accent-indigo/20 text-accent-indigo',
    'bg-accent-success/20 text-accent-success',
    'bg-accent-warning/20 text-accent-warning',
    'bg-accent-danger/20 text-accent-danger',
    'bg-accent-info/20 text-accent-info',
];

export default function TokenizerPage() {
    const [config, setConfig] = useState({
        type: 'bpe', vocabSize: 50257, minFrequency: 2,
        maxTokenLength: 16, specialTokens: '<pad>,<eos>,<bos>,<unk>',
        normalize: true, imagePatchVQ: false,
    });
    const [training, setTraining] = useState(false);
    const [testInput, setTestInput] = useState('ImpressionCore builds brain-inspired AI models.');
    const [tokens, setTokens] = useState(null);

    const update = (key, val) => setConfig((p) => ({ ...p, [key]: val }));

    const handleTrain = async () => {
        setTraining(true);
        try {
            await configureTokenizer(config);
            toast.success('Tokenizer configured successfully');
        } catch (err) {
            toast.error(err.response?.data?.error || 'Configuration failed');
        } finally {
            setTraining(false);
        }
    };

    const [compression, setCompression] = useState(null);

    const handleTokenize = async () => {
        try {
            const { data } = await tokenizeText(testInput);
            if (data.success) {
                setTokens(data.tokens);
                setCompression(data.compression);
            } else {
                toast.error(data.error || 'Tokenization failed');
            }
        } catch {
            // Fallback to client-side splitting if server unavailable
            const words = testInput.split(/(\s+|[.,!?;:'"-])/g).filter(Boolean);
            setTokens(words);
            setCompression(null);
        }
    };

    return (
        <ContentArea title="Tokenization" subtitle="Configure and train the tokenizer vocabulary.">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Config */}
                <div className="space-y-4">
                    <Card>
                        <CardTitle icon={Type}>Tokenizer Configuration</CardTitle>
                        <div className="mt-4 space-y-4">
                            <Select label="Tokenizer Type" options={TOKENIZER_TYPES}
                                value={config.type} onChange={(e) => update('type', e.target.value)} />
                            <Input label="Vocabulary Size" type="number"
                                value={config.vocabSize} onChange={(e) => update('vocabSize', +e.target.value)} />
                            <div className="grid grid-cols-2 gap-4">
                                <Input label="Min Frequency" type="number"
                                    value={config.minFrequency} onChange={(e) => update('minFrequency', +e.target.value)} />
                                <Input label="Max Token Length" type="number"
                                    value={config.maxTokenLength} onChange={(e) => update('maxTokenLength', +e.target.value)} />
                            </div>
                            <Input label="Special Tokens" placeholder="<pad>,<eos>,<bos>,<unk>"
                                value={config.specialTokens} onChange={(e) => update('specialTokens', e.target.value)} />
                            <Toggle label="Unicode Normalization" checked={config.normalize}
                                onChange={(e) => update('normalize', e.target.checked)} />
                            <Toggle label="Image Patch-VQ Tokenization" checked={config.imagePatchVQ}
                                onChange={(e) => update('imagePatchVQ', e.target.checked)} />
                        </div>
                        <button onClick={handleTrain} disabled={training} className="btn-primary mt-4 w-full justify-center">
                            {training ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
                            Train Tokenizer
                        </button>
                    </Card>

                    <Card>
                        <CardTitle icon={Sparkles}>Supported Modes</CardTitle>
                        <div className="mt-3 space-y-2 text-xs text-txt-muted">
                            <div><Badge variant="cyan">Text BPE</Badge> Byte-pair encoding for text with configurable vocab size and special tokens.</div>
                            <div className="mt-2"><Badge variant="info">Image Patch-VQ</Badge> Vector-quantized image patches for visual token embeddings.</div>
                        </div>
                    </Card>
                </div>

                {/* Preview */}
                <div className="space-y-4">
                    <Card>
                        <CardTitle>Tokenizer Preview</CardTitle>
                        <div className="mt-4 space-y-4">
                            <textarea
                                className="input-dark min-h-[80px]"
                                placeholder="Enter text to tokenize..."
                                value={testInput}
                                onChange={(e) => setTestInput(e.target.value)}
                            />
                            <button onClick={handleTokenize} className="btn-secondary w-full justify-center">
                                <Type size={16} /> Tokenize
                            </button>
                        </div>
                        {tokens && (
                            <div className="mt-4">
                                <div className="flex flex-wrap gap-1.5">
                                    {tokens.map((tok, i) => (
                                        <span key={i} className={`px-2 py-1 rounded text-xs font-mono ${TOKEN_COLORS[i % TOKEN_COLORS.length]}`}>
                                            {tok}
                                        </span>
                                    ))}
                                </div>
                                <div className="grid grid-cols-3 gap-3 mt-4">
                                    <StatCard label="Tokens" value={tokens.length} />
                                    <StatCard label="Compression" value={compression ? `${compression}x` : `${(testInput.length / Math.max(tokens.length, 1)).toFixed(1)}x`} />
                                    <StatCard label="Characters" value={testInput.length} />
                                </div>
                            </div>
                        )}
                    </Card>
                </div>
            </div>
        </ContentArea>
    );
}
