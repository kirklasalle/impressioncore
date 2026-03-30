import React, { useState } from 'react';
import { Database, Plus, Search, BookOpen, Loader2, Trash2 } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Input, Badge, StatCard } from '../components/ui';
import { addFact, queryKnowledge } from '../lib/api';
import toast from 'react-hot-toast';

export default function KnowledgePage() {
    const [facts, setFacts] = useState([]);
    const [newFact, setNewFact] = useState({ subject: '', predicate: '', object: '', source: '' });
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [searching, setSearching] = useState(false);

    const handleAddFact = async () => {
        if (!newFact.subject || !newFact.predicate || !newFact.object) {
            return toast.error('Subject, Predicate, and Object are required');
        }
        try {
            await addFact(newFact);
            setFacts((p) => [...p, { ...newFact, id: Date.now() }]);
            setNewFact({ subject: '', predicate: '', object: '', source: '' });
            toast.success('Fact added');
        } catch {
            // Local-only fallback
            setFacts((p) => [...p, { ...newFact, id: Date.now() }]);
            setNewFact({ subject: '', predicate: '', object: '', source: '' });
            toast.success('Fact added (local)');
        }
    };

    const handleQuery = async () => {
        if (!query.trim()) return;
        setSearching(true);
        try {
            const { data } = await queryKnowledge(query);
            setResults(data.results || []);
        } catch {
            // Filter local facts
            const q = query.toLowerCase();
            setResults(facts.filter((f) =>
                f.subject.toLowerCase().includes(q) ||
                f.predicate.toLowerCase().includes(q) ||
                f.object.toLowerCase().includes(q)
            ));
        } finally {
            setSearching(false);
        }
    };

    const removeFact = (id) => setFacts((p) => p.filter((f) => f.id !== id));

    return (
        <ContentArea title="Universal Knowledge Store" subtitle="Manage structured knowledge facts that power the AI.">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Add Facts */}
                <div className="space-y-4">
                    <Card>
                        <CardTitle icon={Plus}>Add Knowledge Fact</CardTitle>
                        <div className="mt-4 space-y-3">
                            <Input label="Subject" placeholder="e.g. ImpressionCore" value={newFact.subject}
                                onChange={(e) => setNewFact((p) => ({ ...p, subject: e.target.value }))} />
                            <Input label="Predicate" placeholder="e.g. is_designed_for" value={newFact.predicate}
                                onChange={(e) => setNewFact((p) => ({ ...p, predicate: e.target.value }))} />
                            <Input label="Object" placeholder="e.g. consumer GPU hardware" value={newFact.object}
                                onChange={(e) => setNewFact((p) => ({ ...p, object: e.target.value }))} />
                            <Input label="Source (optional)" placeholder="e.g. docs/architecture.md" value={newFact.source}
                                onChange={(e) => setNewFact((p) => ({ ...p, source: e.target.value }))} />
                        </div>
                        <button onClick={handleAddFact} className="btn-primary mt-4 w-full justify-center">
                            <Plus size={16} /> Add Fact
                        </button>
                    </Card>

                    <Card>
                        <CardTitle icon={Database}>Fact Store ({facts.length})</CardTitle>
                        <div className="mt-4 space-y-2 max-h-64 overflow-y-auto">
                            {facts.length === 0 && (
                                <p className="text-sm text-txt-muted text-center py-4">No facts added yet</p>
                            )}
                            {facts.map((f) => (
                                <div key={f.id} className="flex items-center justify-between p-3 rounded-lg bg-ic-surface border border-ic-border">
                                    <div className="flex-1 min-w-0">
                                        <div className="text-sm text-txt-primary truncate">
                                            <Badge variant="cyan">{f.subject}</Badge>
                                            <span className="mx-1 text-txt-muted">→</span>
                                            <Badge variant="info">{f.predicate}</Badge>
                                            <span className="mx-1 text-txt-muted">→</span>
                                            <Badge>{f.object}</Badge>
                                        </div>
                                        {f.source && <div className="text-[10px] text-txt-muted mt-1">Source: {f.source}</div>}
                                    </div>
                                    <button onClick={() => removeFact(f.id)} className="ml-2 text-txt-muted hover:text-accent-danger transition-colors">
                                        <Trash2 size={14} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    </Card>
                </div>

                {/* Query */}
                <div className="space-y-4">
                    <Card>
                        <CardTitle icon={Search}>Query Knowledge</CardTitle>
                        <div className="mt-4">
                            <div className="flex gap-3">
                                <input className="input-dark flex-1" placeholder="Search knowledge base..."
                                    value={query} onChange={(e) => setQuery(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleQuery()} />
                                <button onClick={handleQuery} disabled={searching} className="btn-primary px-4">
                                    {searching ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
                                </button>
                            </div>
                        </div>
                        <div className="mt-4 space-y-2 max-h-80 overflow-y-auto">
                            {results.length === 0 && (
                                <div className="text-center py-8 text-txt-muted">
                                    <BookOpen size={32} className="mx-auto mb-2 opacity-30" />
                                    <p className="text-sm">Enter a query to search</p>
                                </div>
                            )}
                            {results.map((r, i) => (
                                <div key={i} className="p-3 rounded-lg bg-ic-surface border border-ic-border">
                                    <div className="text-sm text-txt-primary">
                                        <Badge variant="cyan">{r.subject}</Badge>
                                        <span className="mx-1 text-txt-muted">→</span>
                                        <Badge variant="info">{r.predicate}</Badge>
                                        <span className="mx-1 text-txt-muted">→</span>
                                        <Badge>{r.object}</Badge>
                                    </div>
                                    {r.source && <div className="text-[10px] text-txt-muted mt-1">Source: {r.source}</div>}
                                </div>
                            ))}
                        </div>
                    </Card>

                    <Card>
                        <div className="grid grid-cols-3 gap-3">
                            <StatCard label="Total Facts" value={facts.length} />
                            <StatCard label="Queries" value={results.length > 0 ? '1' : '0'} />
                            <StatCard label="Sources" value={new Set(facts.map((f) => f.source).filter(Boolean)).size} />
                        </div>
                    </Card>
                </div>
            </div>
        </ContentArea>
    );
}
