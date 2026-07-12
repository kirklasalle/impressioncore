import React, { useState, useEffect } from 'react';
import { Shield, Plus, Power, Trash2, AlertTriangle, CheckCircle2 } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import HarnessPageHeader from '../components/layout/HarnessPageHeader';
import TemplateGallery from '../components/harness/TemplateGallery';
import CustomRuleGuide from '../components/harness/CustomRuleGuide';
import { Card, CardTitle, Input, Select, Badge, Toggle } from '../components/ui';
import { listRules, addRule as apiAddRule, deleteRule as apiDeleteRule, toggleRule as apiToggleRule } from '../lib/api';
import { RULE_TEMPLATES } from '../lib/harnessTemplates';
import { cn } from '../lib/utils';
import toast from 'react-hot-toast';

const RULE_STORAGE_KEY = 'ic_applied_rule_templates';

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

export default function RuleEnginePage() {
    const [rules, setRules] = useState([]);
    const [newRule, setNewRule] = useState({
        name: '', category: 'safety', priority: 'medium', condition: '', action: '',
    });
    const [showAdd, setShowAdd] = useState(false);
    const [appliedTemplates, setAppliedTemplates] = useState(() => {
        try { return new Set(JSON.parse(localStorage.getItem(RULE_STORAGE_KEY) || '[]')); }
        catch { return new Set(); }
    });
    const [applyingId, setApplyingId] = useState(null);

    // Load persisted rules on mount
    useEffect(() => {
        listRules().then(({ data }) => {
            if (data.success) setRules(data.rules);
        }).catch(() => { });
    }, []);

    const toggleRule = async (id) => {
        try {
            const { data } = await apiToggleRule(id);
            if (data.success) {
                setRules((p) => p.map((r) => r.id === id ? { ...r, active: data.rule.active } : r));
            }
        } catch {
            setRules((p) => p.map((r) => r.id === id ? { ...r, active: !r.active } : r));
        }
    };
    const removeRule = async (id) => {
        try {
            await apiDeleteRule(id);
            setRules((p) => p.filter((r) => r.id !== id));
            toast('Rule removed');
        } catch {
            setRules((p) => p.filter((r) => r.id !== id));
            toast('Rule removed');
        }
    };
    const addRule = async () => {
        if (!newRule.name || !newRule.condition || !newRule.action) return toast.error('Fill all fields');
        try {
            const { data } = await apiAddRule(newRule);
            if (data.success) {
                setRules((p) => [...p, data.rule]);
                setNewRule({ name: '', category: 'safety', priority: 'medium', condition: '', action: '' });
                setShowAdd(false);
                toast.success('Rule added');
            } else {
                toast.error(data.error || 'Failed to add rule');
            }
        } catch (err) {
            toast.error(err.response?.data?.error || 'Failed to add rule');
        }
    };

    // Apply a rule template suite — adds rules, skipping duplicates by name
    const applyTemplate = async (template) => {
        setApplyingId(template.id);
        const existingNames = new Set(rules.map((r) => r.name.toLowerCase()));
        let added = 0;
        try {
            for (const rule of template.rules) {
                if (existingNames.has(rule.name.toLowerCase())) continue;
                const { data } = await apiAddRule(rule);
                if (data.success) {
                    setRules((p) => [...p, data.rule]);
                    existingNames.add(rule.name.toLowerCase());
                    added++;
                }
            }
            const next = new Set([...appliedTemplates, template.id]);
            setAppliedTemplates(next);
            localStorage.setItem(RULE_STORAGE_KEY, JSON.stringify([...next]));
            toast.success(`Applied "${template.name}" — ${added} new rules added`);
        } catch (err) {
            toast.error(`Error applying template: ${err.message}`);
        } finally {
            setApplyingId(null);
        }
    };

    const active = rules.filter((r) => r.active).length;
    const critical = rules.filter((r) => r.priority === 'critical' && r.active).length;

    return (
        <ContentArea title="Rule Engine" subtitle="Define safety, behavior, and content filtering rules.">
            <HarnessPageHeader
                section="Harness · Rule Engine"
                description="The Rule Engine is the UKS reasoning layer that evaluates conditional IF-THEN rules against the knowledge graph state at inference time. It enables you to define safety filters, ethical constraints, content policies, and behavioral guardrails that shape your model's output — all without retraining. Rules execute in priority order: critical rules fire first, ensuring safety constraints always take precedence."
                capabilities={[
                    'Define conditional rules with IF condition → THEN action patterns',
                    'Categorize rules: Safety, Ethics, Content Filter, Behavior, Output Format, Custom',
                    'Set priority levels: Critical, High, Medium, Low',
                    'Toggle rules on/off without deleting them',
                    'Monitor active vs. disabled rule counts in real time',
                    'Rules apply at inference time — no model retraining required',
                ]}
                builderContext="Part of the UKS subsystem within the Harness. Rules operate on the Knowledge Store at inference time — they constrain and shape model behavior without retraining. This is optional: your model works without rules, but rules add guardrails for safety, compliance, and behavioral alignment."
                reference="Rule evaluation follows a priority-ordered execution model with condition/action factories. Conditions are evaluated against UKS state; if all conditions are true, the rule fires and its actions are applied. Supports rule chaining and execution tracing for debugging."
            />

            <TemplateGallery
                title="Rule Templates"
                description="Pre-built rule suites for safety, ethics, content quality, and behavioral alignment — apply with one click."
                templates={RULE_TEMPLATES}
                onApply={applyTemplate}
                appliedIds={appliedTemplates}
                loadingId={applyingId}
                variant="additive"
                itemLabel="rules"
                itemCount={(t) => t.rules.length}
            />

            <CustomRuleGuide />

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
