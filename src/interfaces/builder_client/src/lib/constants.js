import {
    Home, BookOpen, Monitor, Database, Type, Boxes,
    GraduationCap, BarChart3, MessageSquare, Rocket,
    Compass, Brain, Scale, GitBranch, Layers,
    Cpu, Network, Save, MessageCircle, FileText, HardDrive
} from 'lucide-react';

/** Pipeline step definitions — drives sidebar + homepage grid */
export const PIPELINE_STEPS = [
    { num: 1, key: 'introduction', label: 'Introduction', icon: BookOpen, route: '/introduction', desc: 'Architecture overview and design principles' },
    { num: 2, key: 'system_requirements', label: 'System Setup', icon: Monitor, route: '/system-setup', desc: 'Hardware requirements and environment validation' },
    { num: 3, key: 'data_prep', label: 'Data Preparation', icon: Database, route: '/data-prep', desc: 'Upload, validate, and clean training datasets' },
    { num: 4, key: 'tokenizer', label: 'Tokenization', icon: Type, route: '/tokenizer', desc: 'Configure and train the tokenizer vocabulary' },
    { num: 5, key: 'define_model', label: 'Model Definition', icon: Boxes, route: '/model-definition', desc: 'Define architecture, layers, and precision' },
    { num: 6, key: 'training', label: 'Training', icon: GraduationCap, route: '/training', desc: 'Configure hyperparameters and launch training' },
    { num: 7, key: 'evaluation', label: 'Evaluation', icon: BarChart3, route: '/evaluation', desc: 'Run benchmarks and analyze model quality' },
    { num: 8, key: 'inference', label: 'Inference', icon: MessageSquare, route: '/inference', desc: 'Chat with your trained model in real-time' },
    { num: 9, key: 'deployment', label: 'Deployment', icon: Rocket, route: '/deployment', desc: 'Package and deploy your model to production' },
];

/**
 * Harness section — post-build integration layer
 *
 * The 9-step Build Pipeline (PIPELINE_STEPS) creates the LLM.
 * The Harness connects the trained model to structured knowledge, behavioral
 * constraints, and real-world interfaces at inference time. These are optional
 * because the LLM can also be used standalone via CLI or API key.
 *
 * All current Harness methods are UKS (Universal Knowledge Store) subsystems
 * inspired by BrainSim III's graph of Things + Relationships.
 *
 * To add a new Harness method, append an entry with:
 *   { key: 'unique_key', label: 'Display Name', icon: LucideIcon, route: '/route-path', desc: 'Short description' }
 *
 * Future candidates: RAG Pipeline, Tool-Use API, Multimodal Adapter, MCP Bridge
 */
export const HARNESS_SECTION_DESC = 'Connect your model to the world';

export const HARNESS_NAV = [
    { key: 'uks', label: 'Knowledge Store', icon: Brain, route: '/knowledge', desc: 'Manage structured knowledge facts that power inference' },
    { key: 'rule_engine', label: 'Rule Engine', icon: Scale, route: '/rule-engine', desc: 'Define safety, behavior, and content filtering rules' },
    { key: 'inheritance', label: 'Inheritance', icon: GitBranch, route: '/inheritance', desc: 'Configure knowledge hierarchy and module inheritance' },
];

/** Advanced section */
export const ADVANCED_NAV = [
    { key: 'unified_builder', label: 'Unified Builder', icon: Layers, route: '/unified-builder' },
    { key: 'walkthrough', label: 'Walkthrough', icon: Compass, route: '/walkthrough' },
    { key: 'storage_control', label: 'Storage Control', icon: HardDrive, route: '/storage-control' },
    { key: 'gpu_setup', label: 'GPU Setup', icon: Cpu, route: '/gpu-setup' },
    { key: 'architecture', label: 'Architecture', icon: Network, route: '/architecture' },
    { key: 'checkpoints', label: 'Checkpoints', icon: Save, route: '/checkpoints' },
    { key: 'chat', label: 'Chat', icon: MessageCircle, route: '/chat' },
    { key: 'documentation', label: 'Documentation', icon: FileText, route: '/documentation' },
];

/** Model architecture presets */
export const MODEL_PRESETS = {
    'nano': { layers: 6, hiddenSize: 384, heads: 6, contextWindow: 512, vocabSize: 32000 },
    'micro': { layers: 12, hiddenSize: 512, heads: 8, contextWindow: 1024, vocabSize: 32000 },
    'small': { layers: 12, hiddenSize: 768, heads: 12, contextWindow: 2048, vocabSize: 32000 },
    'medium': { layers: 24, hiddenSize: 1024, heads: 16, contextWindow: 4096, vocabSize: 50257 },
    'large': { layers: 36, hiddenSize: 1536, heads: 16, contextWindow: 8192, vocabSize: 50257 },
    'custom': null,
};

/** Precision options */
export const PRECISION_OPTIONS = [
    { value: 'fp32', label: 'Float32 (Full)', bytes: 4 },
    { value: 'fp16', label: 'Float16 (Half)', bytes: 2 },
    { value: 'bf16', label: 'BFloat16', bytes: 2 },
    { value: 'int8', label: 'INT8 (Quantized)', bytes: 1 },
];

/** Target VRAM budget (GTX 1050 Ti) */
export const VRAM_TARGET_GB = 4.0;

/** Tokenizer types */
export const TOKENIZER_TYPES = [
    { value: 'bpe', label: 'Byte-Pair Encoding (BPE)' },
    { value: 'wordpiece', label: 'WordPiece' },
    { value: 'unigram', label: 'Unigram' },
    { value: 'sentencepiece', label: 'SentencePiece' },
];

/** Evaluation metrics */
export const EVAL_METRICS = [
    { key: 'accuracy', label: 'Accuracy', icon: '🎯' },
    { key: 'perplexity', label: 'Perplexity', icon: '📊' },
    { key: 'f1', label: 'F1 Score', icon: '⚖️' },
    { key: 'bleu', label: 'BLEU', icon: '🔤' },
    { key: 'rouge_l', label: 'ROUGE-L', icon: '📝' },
    { key: 'latency', label: 'Latency (ms)', icon: '⚡' },
];

/** Export formats */
export const EXPORT_FORMATS = [
    { value: 'pytorch', label: 'PyTorch (.pt)' },
    { value: 'safetensors', label: 'SafeTensors (.safetensors)' },
    { value: 'onnx', label: 'ONNX (.onnx)' },
    { value: 'tensorrt', label: 'TensorRT (.engine)' },
];

/** LR scheduler options */
export const LR_SCHEDULERS = [
    { value: 'cosine', label: 'Cosine Annealing' },
    { value: 'linear', label: 'Linear Warmup' },
    { value: 'constant', label: 'Constant' },
    { value: 'cosine_restart', label: 'Cosine w/ Restarts' },
    { value: 'polynomial', label: 'Polynomial Decay' },
];
