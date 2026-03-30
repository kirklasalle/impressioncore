import React from 'react';
import { cn } from '../../lib/utils';

/* ── Card ─────────────────────────────────────────────────── */
export function Card({ children, className, glow = true, ...props }) {
    return (
        <div className={cn(glow ? 'card-glow' : 'bg-ic-card rounded-xl border border-ic-border p-6', className)} {...props}>
            {children}
        </div>
    );
}

export function CardHeader({ children, className }) {
    return (
        <div className={cn('flex items-center justify-between mb-4', className)}>
            {children}
        </div>
    );
}

export function CardTitle({ children, icon: Icon, className }) {
    return (
        <h3 className={cn('text-sm font-semibold text-txt-primary flex items-center gap-2', className)}>
            {Icon && <Icon size={16} className="text-accent-cyan" />}
            {children}
        </h3>
    );
}

/* ── Badge ────────────────────────────────────────────────── */
export function Badge({ children, variant = 'default', className }) {
    const variants = {
        default: 'bg-ic-surface text-txt-secondary border-ic-border',
        success: 'bg-accent-success/10 text-accent-success border-accent-success/30',
        warning: 'bg-accent-warning/10 text-accent-warning border-accent-warning/30',
        danger: 'bg-accent-danger/10 text-accent-danger border-accent-danger/30',
        info: 'bg-accent-info/10 text-accent-info border-accent-info/30',
        cyan: 'bg-accent-cyan/10 text-accent-cyan border-accent-cyan/30',
    };
    return (
        <span className={cn('inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium border', variants[variant], className)}>
            {children}
        </span>
    );
}

/* ── Input ────────────────────────────────────────────────── */
export function Input({ label, className, ...props }) {
    return (
        <div className={className}>
            {label && <label className="label-upper">{label}</label>}
            <input className="input-dark" {...props} />
        </div>
    );
}

/* ── Select ───────────────────────────────────────────────── */
export function Select({ label, options, className, ...props }) {
    return (
        <div className={className}>
            {label && <label className="label-upper">{label}</label>}
            <select className="input-dark appearance-none cursor-pointer" {...props}>
                {options.map((opt) => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
            </select>
        </div>
    );
}

/* ── Textarea ─────────────────────────────────────────────── */
export function Textarea({ label, className, ...props }) {
    return (
        <div className={className}>
            {label && <label className="label-upper">{label}</label>}
            <textarea className="input-dark resize-y min-h-[80px]" {...props} />
        </div>
    );
}

/* ── Toggle ───────────────────────────────────────────────── */
export function Toggle({ label, checked, onChange, className }) {
    return (
        <label className={cn('flex items-center justify-between cursor-pointer', className)}>
            {label && <span className="text-sm text-txt-secondary">{label}</span>}
            <div className="relative">
                <input type="checkbox" className="sr-only" checked={checked} onChange={onChange} />
                <div className={cn(
                    'w-10 h-5 rounded-full transition-colors',
                    checked ? 'bg-accent-cyan' : 'bg-ic-surface border border-ic-border'
                )} />
                <div className={cn(
                    'absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform',
                    checked ? 'translate-x-5' : 'translate-x-0.5'
                )} />
            </div>
        </label>
    );
}

/* ── Slider ───────────────────────────────────────────────── */
export function Slider({ label, value, onChange, min = 0, max = 1, step = 0.01, showValue = true, className }) {
    return (
        <div className={className}>
            <div className="flex items-center justify-between mb-1.5">
                {label && <label className="label-upper mb-0">{label}</label>}
                {showValue && <span className="text-xs font-mono text-accent-cyan">{value}</span>}
            </div>
            <input
                type="range"
                min={min} max={max} step={step}
                value={value}
                onChange={onChange}
                className="w-full h-1.5 bg-ic-surface rounded-full appearance-none cursor-pointer
                           [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4
                           [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-accent-cyan
                           [&::-webkit-slider-thumb]:shadow-lg [&::-webkit-slider-thumb]:shadow-accent-cyan/30"
            />
        </div>
    );
}

/* ── ProgressBar ──────────────────────────────────────────── */
export function ProgressBar({ value = 0, max = 100, variant = 'cyan', className }) {
    const pct = Math.min((value / max) * 100, 100);
    const colors = {
        cyan: 'from-accent-cyan to-accent-indigo',
        success: 'from-accent-success to-emerald-400',
        warning: 'from-accent-warning to-orange-400',
        danger: 'from-accent-danger to-red-400',
    };
    return (
        <div className={cn('w-full h-2 bg-ic-surface rounded-full overflow-hidden', className)}>
            <div
                className={cn('h-full rounded-full bg-gradient-to-r transition-all duration-500', colors[variant])}
                style={{ width: `${pct}%` }}
            />
        </div>
    );
}

/* ── StatCard ─────────────────────────────────────────────── */
export function StatCard({ label, value, icon: Icon, className }) {
    return (
        <div className={cn('stat-card', className)}>
            {Icon && <Icon size={14} className="text-accent-cyan mx-auto mb-1.5" />}
            <div className="text-lg font-bold font-mono text-txt-primary">{value ?? '—'}</div>
            <div className="text-[10px] uppercase tracking-wider text-txt-muted mt-0.5">{label}</div>
        </div>
    );
}
