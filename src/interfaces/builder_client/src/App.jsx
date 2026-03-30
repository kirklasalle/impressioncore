import React from 'react';
import { Outlet } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Sidebar from './components/layout/Sidebar';

export default function App() {
    return (
        <div className="min-h-screen bg-ic-bg">
            <Toaster
                position="top-right"
                toastOptions={{
                    duration: 4000,
                    style: {
                        background: '#1a1f2e',
                        color: '#f1f5f9',
                        border: '1px solid rgba(56,189,248,0.12)',
                        fontSize: '13px',
                    },
                    success: { iconTheme: { primary: '#34d399', secondary: '#fff' } },
                    error: { iconTheme: { primary: '#f87171', secondary: '#fff' } },
                }}
            />
            <Sidebar />
            <Outlet />
        </div>
    );
}
