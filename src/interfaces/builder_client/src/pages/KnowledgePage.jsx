import React, { useState, useEffect } from 'react';
import { Database, Plus, Search, BookOpen, Loader2, Trash2 } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import HarnessPageHeader from '../components/layout/HarnessPageHeader';
import TemplateGallery from '../components/harness/TemplateGallery';
import { Card, CardTitle, Input, Badge, StatCard } from '../components/ui';
import { listFacts, addFact, deleteFact, queryKnowledge } from '../lib/api';
import { KNOWLEDGE_PACKS } from '../lib/harnessTemplates';
import toast from 'react-hot-toast';

const STORAGE_KEY = 'ic_applied_knowledge_packs';

export default function KnowledgePage() {
    const [facts, setFacts] = useState([]);
    const [newFact, setNewFact] = useState({ subject: '', predicate: '', object: '', source: '' });
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [searching, setSearching] = useState(false);
    const [appliedPacks, setAppliedPacks] = useState(() => {
        try { return new Set(JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')); }
        catch { return new Set(); }
    });
    const [applyingId, setApplyingId] = useState(null);

    // Load persisted facts on mount
    useEffect(() => {
        listFacts().then(({ data }) => {
            if (data.success) setFacts(data.facts);
        }).catch(() => { });
    }, []);

    const handleAddFact = async () => {
        if (!newFact.subject || !newFact.predicate || !newFact.object) {
            return toast.error('Subject, Predicate, and Object are required');
        }
        try {
            const { data } = await addFact(newFact);
            if (data.success) {
                setFacts((p) => [...p, data.fact]);
                setNewFact({ subject: '', predicate: '', object: '', source: '' });
                toast.success('Fact added');
            } else {
                toast.error(data.error || 'Failed to add fact');
            }
        } catch (err) {
            toast.error(err.response?.data?.error || 'Failed to add fact');
        }
    };

    const handleQuery = async () => {
        if (!query.trim()) return;
        setSearching(true);
        try {
            const { data } = await queryKnowledge(query);
            setResults(data.results || []);
        } catch {
            // Fallback: filter local facts
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

    const removeFact = async (id) => {
        try {
            await deleteFact(id);
            setFacts((p) => p.filter((f) => f.id !== id));
        } catch {
            setFacts((p) => p.filter((f) => f.id !== id));
        }
    };

    // Apply a knowledge pack — adds facts, skipping duplicates
    const applyPack = async (pack) => {
        setApplyingId(pack.id);
        const existingKeys = new Set(facts.map((f) => `${f.subject}|${f.predicate}|${f.object}`));
        let added = 0;
        try {
            for (const fact of pack.facts) {
                const key = `${fact.subject}|${fact.predicate}|${fact.object}`;
                if (existingKeys.has(key)) continue;
                const { data } = await addFact(fact);
                if (data.success) {
                    setFacts((p) => [...p, data.fact]);
                    existingKeys.add(key);
                    added++;
                }
            }
            const next = new Set([...appliedPacks, pack.id]);
            setAppliedPacks(next);
            localStorage.setItem(STORAGE_KEY, JSON.stringify([...next]));
            toast.success(`Applied "${pack.name}" — ${added} new facts added`);
        } catch (err) {
            toast.error(`Error applying pack: ${err.message}`);
        } finally {
            setApplyingId(null);
        }
    };

    return (
        <ContentArea title="Universal Knowledge Store" subtitle="Manage structured knowledge facts that power the AI.">
            <HarnessPageHeader
                section="Harness · Universal Knowledge Store"
                description="The Universal Knowledge Store (UKS) is the persistent, structured knowledge graph at the heart of the ImpressionCore Harness. It stores facts as Subject → Predicate → Object triples — a pattern inspired by BrainSim III's graph of Things and Relationships. At inference time, these facts are retrieved and injected into the model's context, giving your LLM access to grounded, structured knowledge without retraining."
                capabilities={[
                    'Add structured knowledge facts (Subject → Predicate → Object)',
                    'Query the knowledge base with natural language search',
                    'Track fact sources for provenance and auditability',
                    'Delete outdated or incorrect knowledge entries',
                    'View real-time statistics on your knowledge graph',
                    'Facts augment LLM context automatically at inference time',
                ]}
                builderContext="This is an optional post-build step. After completing the 9-step Build Pipeline (Introduction through Deployment), use the Knowledge Store to equip your trained model with structured facts it can reference during inference. Your model can also be used standalone via CLI or API key without UKS integration."
                reference="The UKS is a graph of nodes (Things) connected by edges (Relationships). Each Relationship has a source, target, and type — all of which are Things. This enables rich semantic representation of real-world knowledge with inheritance and exception support."
            />

            <TemplateGallery
                title="Knowledge Packs"
                description="One-click curated fact sets — instantly populate your knowledge store with structured domain knowledge."
                templates={KNOWLEDGE_PACKS}
                onApply={applyPack}
                appliedIds={appliedPacks}
                loadingId={applyingId}
                variant="additive"
                itemLabel="facts"
                itemCount={(t) => t.facts.length}
            />

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
