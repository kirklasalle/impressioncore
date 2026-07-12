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
export const getSystemHardware = () => api.get('/api/v1/system/hardware');
export const getModelInfo = () => api.get('/api/v1/models/b1/info');
export const getAvailableModels = (params) => api.get('/api/v1/models/available', { params });

// ─── Builder GPU ─────────────────────────────────────────────
export const detectGpu = () => api.get('/api/v1/builder/gpu/detect');

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
export const scanDataDir = (path) => api.post('/api/v1/builder/data/scan', { path });
export const startDataAnalysis = (path) => api.post('/api/v1/builder/data/analyze', { path });
export const getAnalysisStatus = () => api.get('/api/v1/builder/data/analyze/status');
export const browseDataDir = (path) => api.post('/api/v1/builder/data/browse', { path });

// ─── Data Prep Persistence & Profiles ────────────────────────
export const getActiveDataPrep = () => api.get('/api/v1/builder/data/active');
export const saveActiveDataPrep = (state) => api.put('/api/v1/builder/data/active', state);
export const listDataPrepProfiles = () => api.get('/api/v1/builder/data/profiles');
export const saveDataPrepProfile = (profile) => api.post('/api/v1/builder/data/profiles', profile);
export const loadDataPrepProfile = (id) => api.get(`/api/v1/builder/data/profiles/${id}`);
export const deleteDataPrepProfile = (id) => api.delete(`/api/v1/builder/data/profiles/${id}`);

export const configureTokenizer = (config) => api.post('/api/v1/builder/tokenizer/configure', config);
export const tokenizeText = (text) => api.post('/api/v1/builder/tokenizer/tokenize', { text });
export const configureModel = (config) => api.post('/api/v1/builder/model/configure', config);
export const getModelConfig = () => api.get('/api/v1/builder/model/configure');
export const startTraining = (config) => api.post('/api/v1/builder/training/start', config);
export const getTrainingStatus = () => api.get('/api/v1/builder/training/status');
export const stopTraining = () => api.post('/api/v1/builder/training/stop');
export const getTrainingConfig = () => api.get('/api/v1/builder/training/configure');
export const saveTrainingConfig = (config) => api.post('/api/v1/builder/training/configure', config);
export const getCheckpoints = () => api.get('/api/v1/builder/training/checkpoints');
export const deleteCheckpoint = (name) => api.delete(`/api/v1/builder/training/checkpoints/${encodeURIComponent(name)}`);
export const setCheckpointDir = (directory) => api.post('/api/v1/builder/training/checkpoints/dir', { directory });
export const runEvaluation = (config) => api.post('/api/v1/builder/evaluation/run', config);
export const runInference = (payload) => api.post('/api/v1/builder/inference/run', payload);
export const getInferenceSettings = () => api.get('/api/v1/builder/inference/settings');
export const saveInferenceSettings = (config) => api.post('/api/v1/builder/inference/settings', config);
export const analyzeModelSettings = (model) => api.post('/api/v1/builder/inference/analyze', { model });
export const packageModel = (config) => api.post('/api/v1/builder/deployment/package', config);
export const deployModel = (config) => api.post('/api/v1/builder/deployment/deploy', config);
export const getBuilderFeatures = () => api.get('/api/v1/builder/features');
export const getBuilderStorageStatus = () => api.get('/api/v1/builder/storage/status', { timeout: 90000 });
export const runBuilderStorageRetention = (payload) => api.post('/api/v1/builder/storage/retention', payload);

// ─── Walkthrough Progress ────────────────────────────────────
export const getWalkthroughProgress = () => api.get('/api/v1/builder/walkthrough/progress');
export const saveWalkthroughProgress = (progress) => api.put('/api/v1/builder/walkthrough/progress', progress);

// ─── Knowledge ───────────────────────────────────────────────
export const listFacts = () => api.get('/api/v1/builder/knowledge/facts');
export const addFact = (fact) => api.post('/api/v1/builder/knowledge/add_fact', fact);
export const deleteFact = (id) => api.delete(`/api/v1/builder/knowledge/facts/${id}`);
export const queryKnowledge = (query) => api.post('/api/v1/builder/knowledge/query', { query });

// ─── Rules ───────────────────────────────────────────────────
export const listRules = () => api.get('/api/v1/builder/rules');
export const addRule = (rule) => api.post('/api/v1/builder/rules', rule);
export const deleteRule = (id) => api.delete(`/api/v1/builder/rules/${id}`);
export const toggleRule = (id) => api.post(`/api/v1/builder/rules/${id}/toggle`);

// ─── Inheritance ───────────────────────────────────────────
export const listLayers = () => api.get('/api/v1/builder/inheritance/layers');
export const saveLayers = (layers) => api.put('/api/v1/builder/inheritance/layers', { layers });
export const toggleLayerActive = (id) => api.post(`/api/v1/builder/inheritance/layers/${id}/toggle`);
export const toggleModuleInherited = (layerId, moduleId) => api.post(`/api/v1/builder/inheritance/layers/${layerId}/modules/${moduleId}/toggle`);

// ─── Documentation ───────────────────────────────────────────
export const getDocsCatalog = (q) => api.get('/api/v1/builder/docs', { params: q ? { q } : {} });

// ─── Navigation ──────────────────────────────────────────────
export const getNavigation = () => api.get('/api/v1/builder/nav');

export default api;
