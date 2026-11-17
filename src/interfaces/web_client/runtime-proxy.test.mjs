import assert from 'node:assert/strict';
import test from 'node:test';
import { checkLocalRequest, isRuntimePath } from './runtime-proxy.mjs';

const request = (headers = {}, address = '127.0.0.1') => ({
    socket: { remoteAddress: address },
    headers: { host: 'localhost:5173', ...headers },
});

test('local HTTP, media and WebSocket requests share a server-only credential boundary', () => {
    assert.equal(checkLocalRequest(request({ origin: 'http://localhost:5173' }), 'test'), null);
    assert.equal(checkLocalRequest(request({ 'sec-fetch-site': 'same-origin' }), 'test'), null);
    assert.equal(checkLocalRequest(request(), '').status, 503);
    assert.equal(checkLocalRequest(request({}, '192.0.2.1'), 'test').status, 403);
    assert.equal(checkLocalRequest(request({ origin: 'https://other.invalid' }), 'test').status, 403);
    assert.equal(checkLocalRequest(request({ 'sec-fetch-site': 'cross-site' }), 'test').status, 403);
    assert.equal(checkLocalRequest(request({ host: 'other.invalid:5173' }), 'test').status, 403);
    for (const path of ['/v1/hardware', '/ws/skeleton', '/captures/frame.jpg', '/audio/tts.wav', '/health/ready'])
        assert.equal(isRuntimePath(path), true);
    assert.equal(isRuntimePath('/v1-not-a-route'), false);
    assert.equal(isRuntimePath('/src/App.jsx'), false);
});
