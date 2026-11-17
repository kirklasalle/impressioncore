export const runtimePaths = ['/v1', '/ws', '/audio', '/captures', '/voice_recordings', '/health', '/static', '/system_monitor.html'];

export function isRuntimePath(url = '') {
    return runtimePaths.some(path => url === path || url.startsWith(`${path}/`) || url.startsWith(`${path}?`));
}

export function checkLocalRequest(request, key) {
    if (!key) return { status: 503, detail: 'Runtime credentials missing. Start the API and UI with the local stack launcher.' };
    const address = request.socket.remoteAddress;
    if (!['127.0.0.1', '::1', '::ffff:127.0.0.1'].includes(address))
        return { status: 403, detail: 'The local runtime gateway only accepts loopback clients.' };
    const host = request.headers.host;
    let expected;
    try {
        expected = new URL(`http://${host}`);
    } catch {
        return { status: 403, detail: 'Invalid local gateway host.' };
    }
    if (!['localhost', '127.0.0.1', '[::1]'].includes(expected.hostname))
        return { status: 403, detail: 'Invalid local gateway host.' };
    const origin = request.headers.origin;
    if ((origin && origin !== expected.origin) ||
        ['cross-site', 'same-site'].includes(request.headers['sec-fetch-site']))
        return { status: 403, detail: 'Cross-origin access to the local runtime gateway is not allowed.' };
    return null;
}

export function runtimeGateway(key) {
    function protect(request, response, next) {
        if (!isRuntimePath(request.url)) return next();
        const error = checkLocalRequest(request, key);
        if (!error) return next();
        response.writeHead(error.status, { 'Content-Type': 'application/json' });
        response.end(JSON.stringify({ detail: error.detail }));
    }
    return {
        name: 'impressioncore-local-runtime',
        configureServer(server) {
            server.middlewares.use(protect);
        },
        configurePreviewServer(server) {
            server.middlewares.use(protect);
        },
    };
}

export function runtimeProxy(key) {
    return Object.fromEntries(runtimePaths.map(path => [path, {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        ws: true,
        configure(proxy) {
            proxy.on('proxyReq', outgoing => outgoing.setHeader('X-API-Key', key || ''));
            proxy.on('proxyReqWs', (outgoing, request, socket) => {
                if (checkLocalRequest(request, key)) {
                    outgoing.destroy();
                    socket.destroy();
                    return;
                }
                outgoing.setHeader('X-API-Key', key);
            });
        },
    }]));
}
