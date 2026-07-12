import { useState } from 'react';
import { Check, ChevronDown, ChevronUp, Package, Loader2 } from 'lucide-react';

/**
 * Reusable template gallery component for Harness pages.
 *
 * @param {object}   props
 * @param {string}   props.title       - Gallery heading
 * @param {string}   props.description - Short description under heading
 * @param {Array}    props.templates   - Array of template/pack objects (must have id, name, desc, icon)
 * @param {Function} props.onApply     - Called with (template) when user clicks Apply
 * @param {Set}      props.appliedIds  - Set of template IDs already applied (shows checkmark)
 * @param {string|null} props.loadingId - ID of template currently being applied (shows spinner)
 * @param {string}   props.variant     - 'additive' (facts/rules — adds items) or 'replace' (layers — replaces all)
 * @param {string}   props.itemLabel   - Label for items count, e.g. "facts", "rules", "layers"
 * @param {Function} props.itemCount   - (template) => number  — how many items a template contains
 */
export default function TemplateGallery({
    title,
    description,
    templates,
    onApply,
    appliedIds = new Set(),
    loadingId = null,
    variant = 'additive',
    itemLabel = 'items',
    itemCount,
}) {
    const [collapsed, setCollapsed] = useState(false);
    const [expandedId, setExpandedId] = useState(null);

    return (
        <div className="bg-ic-surface/60 border border-white/5 rounded-xl overflow-hidden animate-fade-in-up mb-6">
            {/* Header — always visible */}
            <button
                onClick={() => setCollapsed(!collapsed)}
                className="w-full flex items-center justify-between p-4 hover:bg-white/[0.02] transition-colors text-left"
            >
                <div className="flex items-center gap-3">
                    <Package className="w-5 h-5 text-accent-cyan" />
                    <div>
                        <h3 className="text-sm font-semibold text-white">{title}</h3>
                        <p className="text-xs text-gray-400 mt-0.5">{description}</p>
                    </div>
                </div>
                {collapsed ? (
                    <ChevronDown className="w-4 h-4 text-gray-500" />
                ) : (
                    <ChevronUp className="w-4 h-4 text-gray-500" />
                )}
            </button>

            {/* Card grid */}
            {!collapsed && (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 p-4 pt-0">
                    {templates.map((tmpl) => {
                        const Icon = tmpl.icon;
                        const isApplied = appliedIds.has(tmpl.id);
                        const isLoading = loadingId === tmpl.id;
                        const isExpanded = expandedId === tmpl.id;
                        const count = itemCount ? itemCount(tmpl) : 0;

                        return (
                            <div
                                key={tmpl.id}
                                className={`bg-ic-card border rounded-lg p-4 flex flex-col transition-all ${isApplied
                                        ? 'border-accent-success/40'
                                        : 'border-white/5 hover:border-accent-cyan/30'
                                    }`}
                            >
                                {/* Top row: icon + name + badge */}
                                <div className="flex items-start gap-3 mb-2">
                                    <div className="p-2 rounded-lg bg-accent-cyan/10 text-accent-cyan shrink-0">
                                        {Icon && <Icon className="w-4 h-4" />}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2">
                                            <span className="text-sm font-medium text-white truncate">{tmpl.name}</span>
                                            {isApplied && <Check className="w-3.5 h-3.5 text-accent-success shrink-0" />}
                                        </div>
                                        {/* Category / difficulty badge */}
                                        {(tmpl.category || tmpl.difficulty) && (
                                            <span className="inline-block mt-1 text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-white/5 text-gray-400">
                                                {tmpl.category || tmpl.difficulty}
                                            </span>
                                        )}
                                        {tmpl.vramEstimate && (
                                            <span className="inline-block mt-1 ml-1 text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-accent-indigo/10 text-accent-indigo">
                                                {tmpl.vramEstimate}
                                            </span>
                                        )}
                                    </div>
                                </div>

                                {/* Description */}
                                <p className="text-xs text-gray-400 leading-relaxed mb-3 flex-1">
                                    {tmpl.desc}
                                </p>

                                {/* Expandable preview */}
                                {isExpanded && (
                                    <TemplatePreview template={tmpl} itemLabel={itemLabel} />
                                )}

                                {/* Footer: item count + actions */}
                                <div className="flex items-center justify-between mt-auto pt-3 border-t border-white/5">
                                    <span className="text-[11px] text-gray-500">
                                        {count} {itemLabel}
                                    </span>
                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={() => setExpandedId(isExpanded ? null : tmpl.id)}
                                            className="text-[11px] text-accent-cyan hover:text-accent-cyan/80 transition-colors"
                                        >
                                            {isExpanded ? 'Hide' : 'Preview'}
                                        </button>
                                        <button
                                            onClick={() => !isLoading && onApply(tmpl)}
                                            disabled={isLoading}
                                            className={`text-[11px] font-medium px-3 py-1 rounded-md transition-colors ${isApplied
                                                    ? 'bg-accent-success/10 text-accent-success hover:bg-accent-success/20'
                                                    : 'bg-accent-cyan/10 text-accent-cyan hover:bg-accent-cyan/20'
                                                } disabled:opacity-50 disabled:cursor-wait`}
                                        >
                                            {isLoading ? (
                                                <Loader2 className="w-3 h-3 animate-spin" />
                                            ) : isApplied ? (
                                                variant === 'replace' ? 'Re-apply' : 'Applied'
                                            ) : (
                                                'Apply'
                                            )}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}


// ─────────────────────────────────────────────────────────────
// Preview sub-component: shows the items inside a template
// ─────────────────────────────────────────────────────────────

function TemplatePreview({ template, itemLabel }) {
    // Detect which shape we have
    if (template.facts) {
        return (
            <div className="mb-3 max-h-48 overflow-y-auto pr-1 space-y-1">
                {template.facts.map((f, i) => (
                    <div key={i} className="text-[11px] bg-white/[0.02] rounded px-2 py-1">
                        <span className="text-accent-cyan">{f.subject}</span>
                        <span className="text-gray-500 mx-1">{f.predicate}</span>
                        <span className="text-accent-indigo">{f.object}</span>
                    </div>
                ))}
            </div>
        );
    }

    if (template.rules) {
        return (
            <div className="mb-3 max-h-48 overflow-y-auto pr-1 space-y-1">
                {template.rules.map((r, i) => (
                    <div key={i} className="text-[11px] bg-white/[0.02] rounded px-2 py-1.5">
                        <span className="text-white font-medium">{r.name}</span>
                        <div className="text-gray-500 mt-0.5">
                            <span className="text-accent-warning">IF</span> {r.condition}
                        </div>
                        <div className="text-gray-500">
                            <span className="text-accent-success">THEN</span> {r.action}
                        </div>
                    </div>
                ))}
            </div>
        );
    }

    if (template.layers) {
        return (
            <div className="mb-3 max-h-48 overflow-y-auto pr-1 space-y-1">
                {template.layers.map((l) => (
                    <div key={l.id} className="text-[11px] bg-white/[0.02] rounded px-2 py-1.5">
                        <span className="text-white font-medium">{l.name}</span>
                        <span className="text-gray-500 ml-1">({l.type})</span>
                        <div className="pl-3 mt-0.5 space-y-0.5">
                            {l.modules.map((m) => (
                                <div key={m.id} className="text-gray-400">
                                    • {m.name}{' '}
                                    <span className="text-gray-600">{m.config}</span>
                                    {m.inherited && (
                                        <span className="ml-1 text-accent-cyan text-[10px]">inherited</span>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        );
    }

    return null;
}
