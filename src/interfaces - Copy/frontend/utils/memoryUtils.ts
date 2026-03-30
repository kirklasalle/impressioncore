/**
 * Utilities for memory estimation and tracking
 * Optimized for hardware constraints like 4GB VRAM GPUs
 */

export interface MemoryEstimate {
  totalGb: number;
  attentionGb: number;
  ffnGb: number;
  embeddingGb: number;
  activationsGb: number;
  isWithinBudget: boolean;
  warnings: string[];
}

export interface MemoryOptimizationSuggestion {
  type: 'batch_size' | 'hidden_size' | 'layers' | 'sequence_length' | 'precision';
  currentValue: number;
  suggestedValue: number;
  impact: number;
  description: string;
}

export function estimateModelMemory(config: any): MemoryEstimate {
  const {
    batch_size = 1,
    hidden_size = 768,
    num_layers = 12,
    max_sequence_length = 1024,
    use_fp16 = false,
  } = config;

  // Calculate memory requirements for each component
  const bytesPerParam = use_fp16 ? 2 : 4;
  
  // Attention memory
  const attentionMem = (
    (max_sequence_length * max_sequence_length * hidden_size * bytesPerParam) +
    (3 * max_sequence_length * hidden_size * hidden_size * bytesPerParam)
  ) * num_layers * batch_size;

  // FFN memory
  const ffnMem = (
    (4 * max_sequence_length * hidden_size * hidden_size * bytesPerParam) +
    (max_sequence_length * 4 * hidden_size * bytesPerParam)
  ) * num_layers * batch_size;

  // Embedding memory
  const vocabSize = 50257; // Default GPT-2 vocab size
  const embeddingMem = vocabSize * hidden_size * bytesPerParam;

  // Activation memory (rough estimate)
  const activationMem = (
    max_sequence_length * hidden_size * bytesPerParam * 2 + // Layer activations
    max_sequence_length * max_sequence_length * bytesPerParam // Attention maps
  ) * num_layers * batch_size;

  // Convert to GB
  const gbScale = 1024 * 1024 * 1024;
  const attentionGb = attentionMem / gbScale;
  const ffnGb = ffnMem / gbScale;
  const embeddingGb = embeddingMem / gbScale;
  const activationsGb = activationMem / gbScale;
  const totalGb = attentionGb + ffnGb + embeddingGb + activationsGb;

  // Generate warnings
  const warnings: string[] = [];
  if (totalGb > 3.8) { // Conservative limit for 4GB cards
    warnings.push('Model exceeds recommended memory limit for 4GB GPUs');
  }
  if (max_sequence_length > 1024 && totalGb > 2.0) {
    warnings.push('Long sequence length may cause memory issues');
  }
  if (batch_size > 1 && totalGb > 2.0) {
    warnings.push('Consider reducing batch size for better memory efficiency');
  }

  return {
    totalGb,
    attentionGb,
    ffnGb,
    embeddingGb,
    activationsGb,
    isWithinBudget: totalGb <= 3.8,
    warnings,
  };
}

export function suggestMemoryOptimizations(
  config: any,
  currentEstimate: MemoryEstimate
): MemoryOptimizationSuggestion[] {
  const suggestions: MemoryOptimizationSuggestion[] = [];

  if (!currentEstimate.isWithinBudget) {
    // Try different optimizations and estimate their impact
    const { batch_size, hidden_size, num_layers, max_sequence_length, use_fp16 } = config;

    // Check batch size reduction
    if (batch_size > 1) {
      const reducedBatchEstimate = estimateModelMemory({
        ...config,
        batch_size: batch_size - 1,
      });
      suggestions.push({
        type: 'batch_size',
        currentValue: batch_size,
        suggestedValue: batch_size - 1,
        impact: currentEstimate.totalGb - reducedBatchEstimate.totalGb,
        description: `Reducing batch size to ${batch_size - 1} saves ${(currentEstimate.totalGb - reducedBatchEstimate.totalGb).toFixed(1)}GB VRAM`,
      });
    }

    // Check hidden size reduction
    if (hidden_size > 512) {
      const nextSize = Math.max(512, hidden_size - 256);
      const reducedSizeEstimate = estimateModelMemory({
        ...config,
        hidden_size: nextSize,
      });
      suggestions.push({
        type: 'hidden_size',
        currentValue: hidden_size,
        suggestedValue: nextSize,
        impact: currentEstimate.totalGb - reducedSizeEstimate.totalGb,
        description: `Reducing hidden size to ${nextSize} saves ${(currentEstimate.totalGb - reducedSizeEstimate.totalGb).toFixed(1)}GB VRAM`,
      });
    }

    // Check layer reduction
    if (num_layers > 6) {
      const reducedLayersEstimate = estimateModelMemory({
        ...config,
        num_layers: num_layers - 2,
      });
      suggestions.push({
        type: 'layers',
        currentValue: num_layers,
        suggestedValue: num_layers - 2,
        impact: currentEstimate.totalGb - reducedLayersEstimate.totalGb,
        description: `Reducing layers to ${num_layers - 2} saves ${(currentEstimate.totalGb - reducedLayersEstimate.totalGb).toFixed(1)}GB VRAM`,
      });
    }

    // Check sequence length reduction
    if (max_sequence_length > 512) {
      const nextSeqLen = Math.max(512, max_sequence_length - 256);
      const reducedSeqLenEstimate = estimateModelMemory({
        ...config,
        max_sequence_length: nextSeqLen,
      });
      suggestions.push({
        type: 'sequence_length',
        currentValue: max_sequence_length,
        suggestedValue: nextSeqLen,
        impact: currentEstimate.totalGb - reducedSeqLenEstimate.totalGb,
        description: `Reducing sequence length to ${nextSeqLen} saves ${(currentEstimate.totalGb - reducedSeqLenEstimate.totalGb).toFixed(1)}GB VRAM`,
      });
    }

    // Check precision change
    if (!use_fp16) {
      const fp16Estimate = estimateModelMemory({
        ...config,
        use_fp16: true,
      });
      suggestions.push({
        type: 'precision',
        currentValue: 32,
        suggestedValue: 16,
        impact: currentEstimate.totalGb - fp16Estimate.totalGb,
        description: `Enabling FP16 saves ${(currentEstimate.totalGb - fp16Estimate.totalGb).toFixed(1)}GB VRAM`,
      });
    }
  }

  // Sort suggestions by impact
  return suggestions.sort((a, b) => b.impact - a.impact);
}