import axios from 'axios';

const API_HOST = window.location.hostname === 'localhost'
    ? '127.0.0.1'
    : (window.location.hostname || '127.0.0.1');

// In dev mode, Vite proxy forwards /api to port 5000.
// In production, same origin serves both.
const API_BASE = import.meta.env.DEV
    ? ''   // Vite proxy handles it
    : `${window.location.protocol}//${API_HOST}:5000`;

const api = axios.create({
    baseURL: API_BASE,
    timeout: 30000,
    headers: { 'Content-Type': 'application/json' },
});

// ─── Pipeline / System ───────────────────────────────────────
export const getPipelineStatus = () => api.get('/api/v1/pipeline/status');
export const getSystemStatus = () => api.get('/api/v1/system/status');
export const getModelInfo = () => api.get('/api/v1/models/b1/info');

// ─── Walkthrough checks ─────────────────────────────────────
export const checkGpu = () => api.post('/api/v1/walkthrough/action/gpu_check');
export const checkDependencies = () => api.post('/api/v1/walkthrough/action/dependency_check');
export const checkConfig = () => api.post('/api/v1/walkthrough/action/config_check');
export const checkData = () => api.post('/api/v1/walkthrough/action/data_check');

// ─── Builder actions ─────────────────────────────────────────
export const uploadData = (formData) => api.post('/api/v1/builder/data/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
});
export const configureTokenizer = (config) => api.post('/api/v1/builder/tokenizer/configure', config);
export const configureModel = (config) => api.post('/api/v1/builder/model/configure', config);
export const startTraining = (config) => api.post('/api/v1/builder/training/start', config);
export const getTrainingStatus = () => api.get('/api/v1/builder/training/status');
export const stopTraining = () => api.post('/api/v1/builder/training/stop');
export const runEvaluation = (config) => api.post('/api/v1/builder/evaluation/run', config);
export const runInference = (payload) => api.post('/api/v1/builder/inference/run', payload);
export const packageModel = (config) => api.post('/api/v1/builder/deployment/package', config);
export const deployModel = (config) => api.post('/api/v1/builder/deployment/deploy', config);
export const getBuilderFeatures = () => api.get('/api/v1/builder/features');
export const getBuilderStorageStatus = () => api.get('/api/v1/builder/storage/status');
export const runBuilderStorageRetention = (payload) => api.post('/api/v1/builder/storage/retention', payload);

// ─── Knowledge ───────────────────────────────────────────────
export const addFact = (fact) => api.post('/api/v1/builder/knowledge/add_fact', fact);
export const queryKnowledge = (params) => api.get('/api/v1/builder/knowledge/query', { params });

// ─── Navigation ──────────────────────────────────────────────
export const getNavigation = () => api.get('/api/v1/builder/nav');

export default api;
