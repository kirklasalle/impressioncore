import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/** Merge Tailwind classes — same pattern as OrbOS */
export const cn = (...inputs) => twMerge(clsx(inputs));

/** Format number with commas: 1234567 → "1,234,567" */
export const formatNumber = (n) => {
    if (n == null) return '—';
    return Number(n).toLocaleString();
};

/** Format bytes: 1048576 → "1.00 MB" */
export const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/** Clamp a number to [min, max] */
export const clamp = (val, min, max) => Math.min(Math.max(val, min), max);

/** Estimate model parameters from architecture config */
export const estimateParams = ({ layers = 12, hiddenSize = 768, vocabSize = 32000 }) => {
    const embedding = vocabSize * hiddenSize;
    const attention = layers * (4 * hiddenSize * hiddenSize);
    const ffn = layers * (8 * hiddenSize * hiddenSize);
    const layerNorm = layers * (4 * hiddenSize);
    return embedding + attention + ffn + layerNorm;
};

/** Estimate VRAM in GB from parameter count and precision */
export const estimateVRAM = (params, precision = 'fp16') => {
    const bytesPerParam = precision === 'fp32' ? 4 : precision === 'bf16' ? 2 : 2;
    const modelGB = (params * bytesPerParam) / (1024 ** 3);
    const overheadGB = modelGB * 0.3; // ~30% overhead for optimizer states, activations
    return modelGB + overheadGB;
};
