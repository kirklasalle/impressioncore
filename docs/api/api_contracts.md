# Api Contracts

**Created:** May 24, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\api\api_contracts.md #api #attention_mechanism #deployment #documentation #gpu_optimization #memory_management #multimodal #training  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

# API Contracts and Data Models

**Last updated:** 2025-05-31
**Responsible:** @GitHubCopilot

## Overview

This document defines the data models, schemas, and contracts used by the ImpressionCore API. All endpoints follow these standardized data structures for consistency and type safety.

## Base Response Schema

### Standard Response

```json
{
  "success": boolean,
  "data": any,
  "error": string,
  "code": string,
  "timestamp": string,
  "request_id": string
}
```

### Error Response

```json
{
  "success": false,
  "error": string,
  "code": string,
  "details": {
    "field_errors": object,
    "validation_errors": array,
    "stack_trace": string
  },
  "timestamp": string,
  "request_id": string
}
```

## Authentication Models

### LoginRequest

```json
{
  "username": string,
  "password": string,
  "remember": boolean
}
```

### LoginResponse

```json
{
  "success": true,
  "data": {
    "user_id": string,
    "role": string,
    "session_id": string,
    "expires_at": string
  }
}
```

### APIKey

```json
{
  "id": string,
  "prefix": string,
  "suffix": string,
  "created_at": string,
  "last_used": string,
  "permissions": array
}
```

## Model Management

### ModelConfig

```json
{
  "model_name": string,
  "architecture": string,
  "vocab_size": integer,
  "hidden_size": integer,
  "num_layers": integer,
  "num_attention_heads": integer,
  "intermediate_size": integer,
  "max_position_embeddings": integer,
  "dropout_rate": float,
  "layer_norm_eps": float,
  "activation_function": string
}
```

### ModelInfo

```json
{
  "name": string,
  "architecture": string,
  "parameters": integer,
  "size_mb": float,
  "device": string,
  "precision": string,
  "loaded_at": string,
  "memory_usage": {
    "model_size": float,
    "activation_size": float,
    "optimizer_size": float,
    "total_size": float
  }
}
```

### ModelCreateRequest

```json
{
  "model_name": string,
  "architecture": string,
  "config": ModelConfig,
  "optimization": {
    "quantization": string,
    "pruning": boolean,
    "gradient_checkpointing": boolean
  }
}
```

## Training Models

### TrainingConfig

```json
{
  "learning_rate": float,
  "batch_size": integer,
  "num_epochs": integer,
  "gradient_accumulation_steps": integer,
  "warmup_steps": integer,
  "weight_decay": float,
  "max_grad_norm": float,
  "save_steps": integer,
  "eval_steps": integer,
  "logging_steps": integer,
  "optimization": {
    "optimizer": string,
    "scheduler": string,
    "mixed_precision": boolean,
    "gradient_checkpointing": boolean
  }
}
```

### TrainingStartRequest

```json
{
  "model_name": string,
  "dataset_path": string,
  "config": TrainingConfig,
  "resume_from_checkpoint": string,
  "output_dir": string
}
```

### TrainingStatus

```json
{
  "job_id": string,
  "status": string,
  "progress": float,
  "current_epoch": integer,
  "current_step": integer,
  "total_steps": integer,
  "loss": float,
  "learning_rate": float,
  "throughput": float,
  "eta": string,
  "metrics": {
    "train_loss": float,
    "eval_loss": float,
    "accuracy": float,
    "perplexity": float
  },
  "hardware": {
    "gpu_utilization": float,
    "memory_usage": float,
    "temperature": float
  }
}
```

### TrainingJob

```json
{
  "job_id": string,
  "model_name": string,
  "status": string,
  "config": TrainingConfig,
  "created_at": string,
  "started_at": string,
  "completed_at": string,
  "progress": float,
  "metrics": object,
  "error": string
}
```

## Memory Management

### MemoryStats

```json
{
  "gpu": {
    "used_mb": float,
    "total_mb": float,
    "utilization": float,
    "temperature": float,
    "power_usage": float
  },
  "cpu": {
    "used_mb": float,
    "total_mb": float,
    "utilization": float
  },
  "disk": {
    "cache_size_mb": float,
    "available_mb": float
  }
}
```

### MemoryOptimizationRequest

```json
{
  "strategy": string,
  "target_utilization": float,
  "enable_offloading": boolean,
  "quantization_level": string,
  "gradient_checkpointing": boolean
}
```

### MemoryProfile

```json
{
  "timestamp": string,
  "operation": string,
  "memory_before": MemoryStats,
  "memory_after": MemoryStats,
  "memory_peak": MemoryStats,
  "duration_ms": float
}
```

## 7. Brain Simulation Models

### CognitiveState

Represents the data structure for simulated cognitive states.

```json
{
  "state_id": "string",         // Unique identifier for this state snapshot
  "timestamp": "datetime",      // When this state was generated/retrieved
  "active_concepts": ["string"],// List of currently active concepts or topics
  "emotional_valence": "float", // Ranges from -1.0 (negative) to 1.0 (positive)
  "arousal_level": "float",     // Ranges from 0.0 (calm) to 1.0 (excited)
  "attention_focus": "string",  // Primary focus of attention, if any
  "memory_context": {           // Context from simulated memory systems
    "short_term": ["string"],
    "long_term_associations": ["string"]
  },
  "custom_context": {}          // For any other simulation-specific data
}
```

### UpdateCognitiveStateRequest

Used to request an update to the simulated cognitive state.

```json
{
  "target_state": { // Optional: specify parts of the state to update
    "active_concepts": ["new_concept_1"],
    "emotional_valence": 0.5,
    "arousal_level": 0.8
  },
  "reset_to_default": "boolean", // If true, resets state to a default baseline
  "trigger_event": "string"      // Optional: an event that might influence the state change
}
```

## 8. System Oversight and Memory Management Models

### SystemMemoryMetrics

Reflects the structure returned by `SystemOversightService.update_memory_metrics()` and the `/api/v1/system/memory_metrics` endpoint.

```json
{
  "vram_usage_gb": "float",
  "vram_total_gb": "float",
  "vram_usage_percent": "float",
  "ram_usage_gb": "float",
  "ram_total_gb": "float",
  "ram_usage_percent": "float",
  "swap_usage_gb": "float",
  "swap_total_gb": "float",
  "swap_usage_percent": "float",
  "timestamp": "datetime"
}
```

### TriggerMitigationRequest

Schema for manually triggering a memory mitigation action.

```json
{
  "action_type": "string" // e.g., "reduce_precision", "offload_to_cpu", "clear_cache_level_1"
}
```

### ComponentHealthStatus

Represents the health status of a single monitored component.

```json
{
  "id": "string",
  "name": "string",
  "status": "string", // "ONLINE", "DEGRADED", "OFFLINE", "UNKNOWN"
  "health_score": "float", // 0-100
  "last_checked": "datetime",
  "details": {} // Component-specific health details
}
```

### AnomalyRecord

Structure for a single anomaly recorded by the System Oversight service.

```json
{
  "timestamp": "datetime",
  "component_id": "string",
  "severity": "string", // "LOW", "MEDIUM", "HIGH", "CRITICAL"
  "description": "string",
  "mitigation_applied": "string", // Optional: name of mitigation action taken
  "details": {} // Additional details about the anomaly
}
```

### SystemHealthStatusResponse

Overall system health status, including component health and recent anomalies.

```json
{
  "overall_status": "string", // e.g., "HEALTHY", "WARNING", "CRITICAL"
  "cpu_usage_percent": "float",
  "ram_usage_percent": "float",
  "gpu_vram_usage_percent": "float", // If applicable
  "active_components_status": [/* Array of ComponentHealthStatus */],
  "recent_anomalies": [/* Array of AnomalyRecord */],
  "last_full_health_check": "datetime"
}
```

## 9. Multimodal Processing Models

### MultimodalInput

```json
{
  "request_id": "string",
  "session_id": "string", // Optional: for session-based context
  "user_id": "string",    // Optional: for user-specific context
  "inputs": [
    {
      "modality": "text", // "text", "image", "audio"
      "content_type": "string", // e.g., "plain_text", "url", "base64_encoded_png", "wav_bytes"
      "data": "string", // The actual data or pointer to it
      "metadata": { // Optional modality-specific metadata
        "language": "en-US", // For text or speech
        "image_source": "user_upload" // For image
      }
    }
    // ... more inputs for other modalities
  ],
  "processing_config": { // Optional: overrides for default processing
    "output_modalities": ["text", "speech"], // Desired output types
    "generation_params": {
      "max_length": 200, // For text generation
      "voice_preference": "female_1" // For speech synthesis
    },
    "brain_sim_influence": 0.7 // How much brain sim context should affect output (0 to 1)
  },
  "streaming_config": { // Optional: for streaming responses
    "enable_streaming": false,
    "chunk_size_ms": 500 // For audio streaming
  }
}
```

### MultimodalProcessingRequest

This is often the same as `MultimodalInput` or wraps it, depending on the specific endpoint structure.
For `/api/v1/multimodal/process`, the body is expected to be `MultimodalInput`.

```json
// Typically, the body of the POST request to /api/v1/multimodal/process
// will be an instance of the MultimodalInput schema defined above.
{
  // ... fields from MultimodalInput ...
}
```

### MultimodalProcessingResponse

```json
{
  "success": true,
  "request_id": "string",
  "outputs": [
    {
      "modality": "text",
      "content_type": "plain_text",
      "data": "This is the generated text.",
      "metadata": {
        "source_model": "ImpressionCore-b1-TextGenerator"
      }
    },
    {
      "modality": "speech",
      "content_type": "audio_url" // or "base64_encoded_wav"
      "data": "https://example.com/path/to/generated_audio.wav",
      "metadata": {
        "voice_used": "female_1",
        "duration_ms": 3500
      }
    }
    // ... more outputs for other modalities
  ],
  "processing_time_ms": 1234,
  "debug_info": { // Optional: for debugging
    "internal_states": {},
    "model_latencies": {}
  }
}
```

### StreamingConfig

```json
{
  "enable_streaming": "boolean",
  "chunk_size_ms": "integer", // For audio streaming: duration of each chunk in milliseconds
  "chunk_size_tokens": "integer" // For text streaming: number of tokens per chunk
}
```

## 10. Deployment Models

---

_This documentation is automatically validated against the actual API implementation. Last updated: 2025-05-24_
