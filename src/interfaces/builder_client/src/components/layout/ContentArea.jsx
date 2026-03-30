import React from 'react';
import { cn } from '../../lib/utils';

export default function ContentArea({ title, subtitle, children, className }) {
    return (
        <main className={cn('ml-0 lg:ml-64 min-h-screen p-6 lg:p-8', className)}>
            {(title || subtitle) && (
                <div className="mb-8 animate-fade-in-up">
                    {title && (
                        <h1 className="text-2xl font-bold text-txt-primary">{title}</h1>
                    )}
                    {subtitle && (
                        <p className="mt-1 text-sm text-txt-secondary">{subtitle}</p>
                    )}
                </div>
            )}
            <div className="animate-fade-in-up">
                {children}
            </div>
        </main>
    );
}
