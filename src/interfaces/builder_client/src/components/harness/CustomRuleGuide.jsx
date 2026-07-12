import { useState } from 'react';
import { BookOpen, ChevronDown, ChevronUp, Lightbulb } from 'lucide-react';
import { CUSTOM_RULE_GUIDE } from '../../lib/harnessTemplates';

/**
 * Collapsible educational guide for writing custom rules.
 * Renders sections from CUSTOM_RULE_GUIDE with examples, priority levels,
 * categories, and practical tips.
 */
export default function CustomRuleGuide() {
    const [open, setOpen] = useState(false);

    const priorityColor = {
        danger: 'text-accent-danger bg-accent-danger/10',
        warning: 'text-accent-warning bg-accent-warning/10',
        info: 'text-accent-cyan bg-accent-cyan/10',
        default: 'text-gray-300 bg-white/5',
    };

    return (
        <div className="bg-ic-surface/60 border border-white/5 rounded-xl overflow-hidden animate-fade-in-up mb-6">
            {/* Toggle header */}
            <button
                onClick={() => setOpen(!open)}
                className="w-full flex items-center justify-between p-4 hover:bg-white/[0.02] transition-colors text-left"
            >
                <div className="flex items-center gap-3">
                    <BookOpen className="w-5 h-5 text-accent-indigo" />
                    <div>
                        <h3 className="text-sm font-semibold text-white">{CUSTOM_RULE_GUIDE.title}</h3>
                        <p className="text-xs text-gray-400 mt-0.5">
                            Learn how to write effective IF-THEN rules for your model
                        </p>
                    </div>
                </div>
                {open ? (
                    <ChevronUp className="w-4 h-4 text-gray-500" />
                ) : (
                    <ChevronDown className="w-4 h-4 text-gray-500" />
                )}
            </button>

            {/* Content sections */}
            {open && (
                <div className="px-4 pb-4 space-y-5">
                    {CUSTOM_RULE_GUIDE.sections.map((section, idx) => (
                        <div key={idx}>
                            <h4 className="text-xs font-semibold text-accent-cyan uppercase tracking-wider mb-2">
                                {section.heading}
                            </h4>
                            {section.content && (
                                <p className="text-xs text-gray-400 leading-relaxed mb-2">
                                    {section.content}
                                </p>
                            )}

                            {/* Condition / Action examples */}
                            {section.examples && (
                                <div className="space-y-1">
                                    {section.examples.map((ex, i) => (
                                        <div
                                            key={i}
                                            className="flex items-start gap-2 text-[11px] bg-white/[0.02] rounded px-3 py-1.5"
                                        >
                                            <code className="text-accent-cyan whitespace-nowrap shrink-0">
                                                {ex.condition}
                                            </code>
                                            <span className="text-gray-500">— {ex.explanation}</span>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Priority levels */}
                            {section.levels && (
                                <div className="space-y-1">
                                    {section.levels.map((lv, i) => (
                                        <div
                                            key={i}
                                            className="flex items-center gap-2 text-[11px] bg-white/[0.02] rounded px-3 py-1.5"
                                        >
                                            <span
                                                className={`px-2 py-0.5 rounded font-medium ${priorityColor[lv.color] || priorityColor.default
                                                    }`}
                                            >
                                                {lv.level}
                                            </span>
                                            <span className="text-gray-400">{lv.use}</span>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Categories */}
                            {section.categories && (
                                <div className="grid grid-cols-2 gap-1">
                                    {section.categories.map((cat, i) => (
                                        <div
                                            key={i}
                                            className="text-[11px] bg-white/[0.02] rounded px-3 py-1.5"
                                        >
                                            <span className="text-white font-medium">{cat.name}</span>
                                            <span className="text-gray-500 ml-1">— {cat.desc}</span>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Tips list */}
                            {section.tips && (
                                <div className="space-y-1">
                                    {section.tips.map((tip, i) => (
                                        <div
                                            key={i}
                                            className="flex items-start gap-2 text-[11px] bg-white/[0.02] rounded px-3 py-1.5"
                                        >
                                            <Lightbulb className="w-3 h-3 text-accent-warning shrink-0 mt-0.5" />
                                            <span className="text-gray-400">{tip}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
