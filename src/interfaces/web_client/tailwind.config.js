/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'ic': {
                    'bg': '#0a0e17',
                    'surface': '#111827',
                    'card': '#1a1f2e',
                    'sidebar': '#0d1117',
                    'hover': '#1e293b',
                    'border': 'rgba(56,189,248,0.12)',
                },
                'accent': {
                    'cyan': '#38bdf8',
                    'indigo': '#818cf8',
                    'success': '#34d399',
                    'warning': '#fbbf24',
                    'danger': '#f87171',
                    'info': '#a78bfa',
                },
                'txt': {
                    'primary': '#f1f5f9',
                    'secondary': '#94a3b8',
                    'muted': '#64748b',
                },
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
            },
            animation: {
                'fade-in-up': 'fadeInUp 0.4s ease-out',
                'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
            },
            keyframes: {
                fadeInUp: {
                    '0%': { opacity: '0', transform: 'translateY(12px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                pulseGlow: {
                    '0%, 100%': { boxShadow: '0 0 8px rgba(56,189,248,0.2)' },
                    '50%': { boxShadow: '0 0 20px rgba(56,189,248,0.4)' },
                },
            },
        },
    },
    plugins: [],
}
