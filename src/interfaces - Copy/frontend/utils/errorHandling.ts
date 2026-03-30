/**
 * Error handling utilities for ImpressionCore UI
 * Provides user-friendly error messages and recovery suggestions
 */

export interface ErrorDetails {
  code: string;
  message: string;
  suggestions: string[];
  isRecoverable: boolean;
  memoryRelated: boolean;
}

// Error categories
export const ErrorTypes = {
  MEMORY: 'memory',
  HARDWARE: 'hardware',
  CONFIGURATION: 'config',
  NETWORK: 'network',
  UNKNOWN: 'unknown',
} as const;

// Error codes and their user-friendly messages
const ERROR_MESSAGES: Record<string, ErrorDetails> = {
  'MEMORY_OOM': {
    code: 'MEMORY_OOM',
    message: 'Out of memory error occurred',
    suggestions: [
      'Reduce model size or batch size',
      'Enable memory optimizations',
      'Try using FP16 precision',
      'Enable gradient checkpointing',
    ],
    isRecoverable: true,
    memoryRelated: true,
  },
  'MEMORY_FRAGMENTATION': {
    code: 'MEMORY_FRAGMENTATION',
    message: 'GPU memory fragmentation detected',
    suggestions: [
      'Restart the training process',
      'Reduce batch size',
      'Enable memory efficient attention',
    ],
    isRecoverable: true,
    memoryRelated: true,
  },
  'HARDWARE_UNSUPPORTED': {
    code: 'HARDWARE_UNSUPPORTED',
    message: 'Hardware capability not supported',
    suggestions: [
      'Check GPU compatibility',
      'Update GPU drivers',
      'Use CPU fallback mode',
    ],
    isRecoverable: false,
    memoryRelated: false,
  },
  'CONFIG_INVALID': {
    code: 'CONFIG_INVALID',
    message: 'Invalid model configuration',
    suggestions: [
      'Check parameter values',
      'Ensure configuration is complete',
      'Use recommended settings for your hardware',
    ],
    isRecoverable: true,
    memoryRelated: false,
  },
};

export class ModelError extends Error {
  public details: ErrorDetails;

  constructor(code: string, additionalInfo?: string) {
    const details = ERROR_MESSAGES[code] || {
      code: 'UNKNOWN',
      message: 'An unknown error occurred',
      suggestions: ['Try refreshing the page', 'Check console for details'],
      isRecoverable: false,
      memoryRelated: false,
    };

    super(additionalInfo ? `${details.message}: ${additionalInfo}` : details.message);
    this.name = 'ModelError';
    this.details = details;
  }

  public isMemoryRelated(): boolean {
    return this.details.memoryRelated;
  }

  public getSuggestions(): string[] {
    return this.details.suggestions;
  }

  public isRecoverable(): boolean {
    return this.details.isRecoverable;
  }
}

export function handleModelError(error: Error | ModelError): ErrorDetails {
  if (error instanceof ModelError) {
    return error.details;
  }

  // Try to categorize unknown errors
  const errorMessage = error.message.toLowerCase();
  
  if (errorMessage.includes('out of memory') || errorMessage.includes('cuda') || errorMessage.includes('gpu')) {
    return ERROR_MESSAGES['MEMORY_OOM'];
  }

  if (errorMessage.includes('configuration') || errorMessage.includes('parameter')) {
    return ERROR_MESSAGES['CONFIG_INVALID'];
  }

  return {
    code: 'UNKNOWN',
    message: error.message,
    suggestions: ['Try refreshing the page', 'Check console for details'],
    isRecoverable: false,
    memoryRelated: false,
  };
}

export function getMemoryErrorRecoverySteps(config: any): string[] {
  const steps: string[] = [];
  const { batch_size, hidden_size, num_layers, use_fp16 } = config;

  if (batch_size > 1) {
    steps.push(`Reduce batch size from ${batch_size} to ${batch_size - 1}`);
  }

  if (!use_fp16) {
    steps.push('Enable FP16 precision for reduced memory usage');
  }

  if (hidden_size > 768) {
    steps.push(`Reduce hidden size to 768 or lower (currently ${hidden_size})`);
  }

  if (num_layers > 12) {
    steps.push(`Reduce number of layers to 12 or lower (currently ${num_layers})`);
  }

  if (steps.length === 0) {
    steps.push('Enable all memory optimization options');
    steps.push('Consider using a smaller model architecture');
  }

  return steps;
}

export function suggestHardwareUpgrades(error: ModelError): string[] {
  if (!error.isMemoryRelated()) {
    return [];
  }

  return [
    'Consider upgrading to a GPU with more VRAM for larger models',
    'Use a cloud GPU service for training larger models',
    'Implement model parallel training across multiple GPUs',
    'Use CPU offloading for portions of the model',
  ];
}