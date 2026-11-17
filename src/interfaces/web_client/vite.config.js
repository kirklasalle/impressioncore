import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { runtimeGateway, runtimeProxy } from './runtime-proxy.mjs'

const runtimeKey = process.env.IMPRESSIONCORE_API_KEY

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [runtimeGateway(runtimeKey), react()],
    server: {
        port: 5173,
        strictPort: true,
        host: '127.0.0.1',
        cors: false,
        proxy: runtimeProxy(runtimeKey)
    },
    preview: {
        host: '127.0.0.1',
        cors: false,
        proxy: runtimeProxy(runtimeKey)
    },
})
