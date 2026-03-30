export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'cyan-glow': '#00f3ff',
                'magenta-glow': '#ff00ff',
            },
            fontFamily: {
                mono: ['Fira Code', 'monospace'],
            }
        },
    },
    plugins: [],
}
