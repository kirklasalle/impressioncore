import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { Home, ChevronDown, ChevronRight, Menu, X } from 'lucide-react';
import { cn } from '../../lib/utils';
import { PIPELINE_STEPS, KNOWLEDGE_NAV, ADVANCED_NAV } from '../../lib/constants';

const SidebarSection = ({ title, children, defaultOpen = true }) => {
    const [open, setOpen] = useState(defaultOpen);
    return (
        <div className="mb-2">
            <button
                onClick={() => setOpen(!open)}
                className="w-full flex items-center justify-between px-4 py-2 text-[10px] font-semibold uppercase tracking-widest text-txt-muted hover:text-txt-secondary transition-colors"
            >
                {title}
                {open ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
            </button>
            {open && <div className="space-y-0.5">{children}</div>}
        </div>
    );
};

const SidebarLink = ({ to, icon: Icon, label, badge }) => {
    const location = useLocation();
    const isActive = location.pathname === to;
    return (
        <NavLink
            to={to}
            className={cn(
                'flex items-center gap-3 px-4 py-2 mx-2 rounded-lg text-sm transition-all duration-200',
                isActive
                    ? 'bg-gradient-to-r from-accent-cyan/15 to-accent-indigo/10 text-accent-cyan border-l-2 border-accent-cyan'
                    : 'text-txt-secondary hover:text-txt-primary hover:bg-ic-hover'
            )}
        >
            {badge != null ? (
                <span className={cn('step-badge', isActive && 'step-badge-active')}>
                    {badge}
                </span>
            ) : (
                Icon && <Icon size={16} className="shrink-0" />
            )}
            <span className="truncate">{label}</span>
        </NavLink>
    );
};

export default function Sidebar() {
    const [mobileOpen, setMobileOpen] = useState(false);

    return (
        <>
            {/* Mobile toggle */}
            <button
                onClick={() => setMobileOpen(!mobileOpen)}
                className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-ic-card border border-ic-border text-txt-secondary"
            >
                {mobileOpen ? <X size={20} /> : <Menu size={20} />}
            </button>

            {/* Overlay */}
            {mobileOpen && (
                <div
                    className="lg:hidden fixed inset-0 bg-black/60 z-40"
                    onClick={() => setMobileOpen(false)}
                />
            )}

            {/* Sidebar */}
            <aside className={cn(
                'fixed top-0 left-0 h-screen w-64 z-40 flex flex-col',
                'bg-gradient-to-b from-ic-sidebar to-ic-bg border-r border-ic-border',
                'transition-transform duration-300',
                mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
            )}>
                {/* Header */}
                <div className="p-5 border-b border-ic-border">
                    <NavLink to="/" className="flex items-center gap-3 group" onClick={() => setMobileOpen(false)}>
                        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-accent-cyan to-accent-indigo flex items-center justify-center text-white font-bold text-sm">
                            IC
                        </div>
                        <div>
                            <div className="text-sm font-semibold text-txt-primary group-hover:text-accent-cyan transition-colors">
                                ImpressionCore
                            </div>
                            <div className="text-[10px] font-mono text-accent-cyan">
                                B3 MODEL BUILDER
                            </div>
                        </div>
                    </NavLink>
                </div>

                {/* Navigation */}
                <nav className="flex-1 overflow-y-auto py-4 space-y-1" onClick={() => setMobileOpen(false)}>
                    {/* Home */}
                    <div className="mb-2">
                        <SidebarLink to="/" icon={Home} label="Home" />
                    </div>

                    {/* Build Walkthrough (pipeline steps) */}
                    <SidebarSection title="Build Pipeline">
                        {PIPELINE_STEPS.map((step) => (
                            <SidebarLink
                                key={step.key}
                                to={step.route}
                                icon={step.icon}
                                label={step.label}
                                badge={step.num}
                            />
                        ))}
                    </SidebarSection>

                    {/* Knowledge & AI */}
                    <SidebarSection title="Knowledge & AI" defaultOpen={false}>
                        {KNOWLEDGE_NAV.map((item) => (
                            <SidebarLink key={item.key} to={item.route} icon={item.icon} label={item.label} />
                        ))}
                    </SidebarSection>

                    {/* Advanced */}
                    <SidebarSection title="Advanced" defaultOpen={false}>
                        {ADVANCED_NAV.map((item) => (
                            <SidebarLink key={item.key} to={item.route} icon={item.icon} label={item.label} />
                        ))}
                    </SidebarSection>
                </nav>

                {/* Footer */}
                <div className="p-4 border-t border-ic-border">
                    <div className="text-[10px] font-mono text-txt-muted text-center">
                        ImpressionCore © 2026
                    </div>
                </div>
            </aside>
        </>
    );
}
