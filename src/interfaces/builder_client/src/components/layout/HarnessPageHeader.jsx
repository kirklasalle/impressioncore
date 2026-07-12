import React from 'react';
import { Info, Zap, BookOpen } from 'lucide-react';

/**
 * HarnessPageHeader — reusable informational hero card for Harness pages.
 *
 * Renders a styled info section explaining the page's purpose, capabilities,
 * builder context, and BrainSim III reference. Designed to be placed as the
 * first child inside ContentArea on any Harness page.
 *
 * To add a new Harness page, import this component and pass your page-specific props.
 *
 * @param {string}   section      — Badge label, e.g. "Harness · Universal Knowledge Store"
 * @param {string}   description  — Rich paragraph explaining what this page does
 * @param {string[]} capabilities — "What You Can Do Here" bullet list
 * @param {string}   builderContext — How this page fits in the ImpressionCore Builder workflow
 * @param {string}   [reference]  — Optional BrainSim III / architectural reference note
 */
export default function HarnessPageHeader({ section, description, capabilities, builderContext, reference }) {
    return (
        <div className="mb-6 rounded-xl border-l-4 border-accent-cyan bg-ic-surface/60 p-5 animate-fade-in-up">
            {/* Section badge */}
            <div className="flex items-center gap-2 mb-3">
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20">
                    <Zap size={10} />
                    {section}
                </span>
            </div>

            {/* Description */}
            <p className="text-sm text-txt-secondary leading-relaxed mb-4">
                {description}
            </p>

            {/* Capabilities */}
            {capabilities && capabilities.length > 0 && (
                <div className="mb-4">
                    <h4 className="text-[11px] font-semibold uppercase tracking-wider text-txt-muted mb-2 flex items-center gap-1.5">
                        <Info size={12} /> What You Can Do Here
                    </h4>
                    <ul className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                        {capabilities.map((item, i) => (
                            <li key={i} className="flex items-start gap-2 text-xs text-txt-secondary">
                                <span className="mt-1 w-1 h-1 rounded-full bg-accent-cyan shrink-0" />
                                {item}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Builder context */}
            <div className="p-3 rounded-lg bg-ic-bg/60 border border-ic-border text-xs text-txt-muted leading-relaxed">
                <span className="font-semibold text-txt-secondary">Builder Context: </span>
                {builderContext}
            </div>

            {/* BrainSim III reference */}
            {reference && (
                <div className="mt-3 flex items-start gap-2 text-[11px] text-txt-muted">
                    <BookOpen size={12} className="mt-0.5 shrink-0 text-accent-indigo" />
                    <span><span className="font-semibold text-accent-indigo">BrainSim III:</span> {reference}</span>
                </div>
            )}
        </div>
    );
}
