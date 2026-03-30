import React, { useState } from 'react';
import { Shield, Plus, Power, Trash2, AlertTriangle, CheckCircle2 } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Input, Select, Badge, Toggle } from '../components/ui';
import { cn } from '../lib/utils';
import toast from 'react-hot-toast';

const PRIORITIES = [
    { value: 'critical', label: 'Critical', color: 'danger' },
    { value: 'high', label: 'High', color: 'warning' },
    { value: 'medium', label: 'Medium', color: 'info' },
    { value: 'low', label: 'Low', color: 'default' },
];
const CATEGORIES = [
    { value: 'safety', label: 'Safety' },
    { value: 'ethics', label: 'Ethics' },
    { value: 'content', label: 'Content Filter' },
    { value: 'behavior', label: 'Behavior' },
    { value: 'output', label: 'Output Format' },
    { value: 'custom', label: 'Custom' },
];

const DEFAULT_RULES = [
    { id: 1, name: 'No harmful content', category: 'safety', priority: 'critical', active: true, condition: 'output contains harmful_keywords', action: 'Block and log' },
    { id: 2, name: 'PII redaction', category: 'safety', priority: 'critical', active: true, condition: 'output matches PII_regex', action: 'Redact matched text' },
    { id: 3, name: 'Response length limit', category: 'output', priority: 'medium', active: true, condition: 'token_count > 4096', action: 'Truncate with notice' },
    { id: 4, name: 'Ethical guidelines', category: 'ethics', priority: 'high', active: true, condition: 'topic in ethical_sensitive_list', action: 'Apply ethical framework' },
];

export default function RuleEnginePage() {
    const [rules, setRules] = useState(DEFAULT_RULES);
    const [newRule, setNewRule] = useState({
        name: '', category: 'safety', priority: 'medium', condition: '', action: '',
    });
    const [showAdd, setShowAdd] = useState(false);

    const toggleRule = (id) => {
        setRules((p) => p.map((r) => r.id === id ? { ...r, active: !r.active } : r));
    };
    const removeRule = (id) => {
        setRules((p) => p.filter((r) => r.id !== id));
        toast('Rule removed');
    };
    const addRule = () => {
        if (!newRule.name || !newRule.condition || !newRule.action) return toast.error('Fill all fields');
        setRules((p) => [...p, { ...newRule, id: Date.now(), active: true }]);
        setNewRule({ name: '', category: 'safety', priority: 'medium', condition: '', action: '' });
        setShowAdd(false);
        toast.success('Rule added');
    };

    const active = rules.filter((r) => r.active).length;
    const critical = rules.filter((r) => r.priority === 'critical' && r.active).length;

    return (
        <ContentArea title="Rule Engine" subtitle="Define safety, behavior, and content filtering rules.">
            {/* Stats */}
            <div className="grid grid-cols-4 gap-3 mb-6">
                <div className="stat-card"><span className="text-lg font-bold text-txt-primary">{rules.length}</span><span className="text-[10px] text-txt-muted">Total Rules</span></div>
                <div className="stat-card"><span className="text-lg font-bold text-accent-success">{active}</span><span className="text-[10px] text-txt-muted">Active</span></div>
                <div className="stat-card"><span className="text-lg font-bold text-accent-danger">{critical}</span><span className="text-[10px] text-txt-muted">Critical</span></div>
                <div className="stat-card"><span className="text-lg font-bold text-txt-secondary">{rules.length - active}</span><span className="text-[10px] text-txt-muted">Disabled</span></div>
            </div>

            {/* Rule List */}
            <Card className="mb-4">
                <div className="flex items-center justify-between">
                    <CardTitle icon={Shield}>Active Rules</CardTitle>
                    <button onClick={() => setShowAdd(!showAdd)} className="btn-primary text-xs py-1.5">
                        <Plus size={14} /> Add Rule
                    </button>
                </div>
                <div className="mt-4 space-y-2">
                    {rules.map((rule) => (
                        <div key={rule.id} className={cn(
                            'flex items-center gap-4 p-3 rounded-xl border transition-all',
                            rule.active ? 'bg-ic-surface border-ic-border' : 'bg-ic-bg border-ic-border/50 opacity-60'
                        )}>
                            <button onClick={() => toggleRule(rule.id)}>
                                <Power size={16} className={rule.active ? 'text-accent-success' : 'text-txt-muted'} />
                            </button>
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                    <span className="text-sm font-medium text-txt-primary">{rule.name}</span>
                                    <Badge variant={PRIORITIES.find((p) => p.value === rule.priority)?.color || 'default'}>
                                        {rule.priority}
                                    </Badge>
                                    <Badge variant="info">{rule.category}</Badge>
                                </div>
                                <div className="text-[11px] text-txt-muted mt-0.5 font-mono truncate">
                                    IF {rule.condition} → {rule.action}
                                </div>
                            </div>
                            <button onClick={() => removeRule(rule.id)} className="text-txt-muted hover:text-accent-danger transition-colors">
                                <Trash2 size={14} />
                            </button>
                        </div>
                    ))}
                </div>
            </Card>

            {/* Add Rule Form */}
            {showAdd && (
                <Card className="animate-fade-in-up">
                    <CardTitle icon={Plus}>New Rule</CardTitle>
                    <div className="mt-4 space-y-3">
                        <Input label="Rule Name" value={newRule.name}
                            onChange={(e) => setNewRule((p) => ({ ...p, name: e.target.value }))} />
                        <div className="grid grid-cols-2 gap-4">
                            <Select label="Category" options={CATEGORIES} value={newRule.category}
                                onChange={(e) => setNewRule((p) => ({ ...p, category: e.target.value }))} />
                            <Select label="Priority" options={PRIORITIES} value={newRule.priority}
                                onChange={(e) => setNewRule((p) => ({ ...p, priority: e.target.value }))} />
                        </div>
                        <Input label="Condition" placeholder="e.g. output contains keyword" value={newRule.condition}
                            onChange={(e) => setNewRule((p) => ({ ...p, condition: e.target.value }))} />
                        <Input label="Action" placeholder="e.g. Block and notify" value={newRule.action}
                            onChange={(e) => setNewRule((p) => ({ ...p, action: e.target.value }))} />
                        <div className="flex gap-3">
                            <button onClick={addRule} className="btn-primary flex-1 justify-center"><CheckCircle2 size={16} /> Add</button>
                            <button onClick={() => setShowAdd(false)} className="btn-secondary flex-1 justify-center">Cancel</button>
                        </div>
                    </div>
                </Card>
            )}
        </ContentArea>
    );
}
