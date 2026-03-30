# ImpressionCore Complete API Reference

**Created:** May 24, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\api\complete_api_reference.md #api #attention_mechanism #cuda #deployment #documentation #gpu_optimization #inference #memory_management #multimodal #performance #pytorch #testing #tokenization #training #web_interface  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

Last Updated: 2025-05-31
Responsible: @GitHubCopilot

## Overview

This document provides a complete reference for all ImpressionCore API endpoints, including web routes, REST APIs, WebSocket endpoints, and internal service interfaces. The ImpressionCore platform provides multiple server implementations with comprehensive route coverage across authentication, web applications, REST APIs, WebSocket endpoints, and system utilities.

## Table of Contents

1. [Authentication](#authentication)
2. [Web Application Routes](#web-application-routes)
3. [REST API Endpoints](#rest-api-endpoints)
4. [WebSocket Endpoints](#websocket-endpoints)
5. [System Utilities](#system-utilities)
6. [Brain Simulation API](#brain-simulation-api)
7. [Memory Optimization API](#memory-optimization-api)
8. [Multimodal Processing API](#multimodal-processing-api)
9. [Deployment API](#deployment-api)
10. [Error Handling](#error-handling)
11. [Rate Limiting](#rate-limiting)

## Authentication

### Session-Based Authentication

All protected routes require session authentication via cookies.

**Login Endpoint:**

```http
POST /login
Content-Type: application/json

{
  "username": "string",
  "password": "string",
  "remember": "boolean"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Login successful"
}
```

**Logout Endpoint:**

```http
GET /logout
```

**Response:**

```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### API Key Authentication

For programmatic access to API endpoints, include API key in headers:

```http
Authorization: Bearer <api_key>
```

**Generate API Key:**

```http
GET /api/v1/user/api-keys
Authorization: Required
```

**Response:**

```json
[
  {
    "id": "string",
    "prefix": "string",
    "suffix": "string"
  }
]
```

### Generate API Key

```http
POST /api/v1/user/api-key
Authorization: Required
```

**Response:**

```json
{
  "success": true,
  "key": "string",
  "id": "string"
}
```

### Revoke API Key

```http
DELETE /api/v1/user/api-key/{key_id}
Authorization: Required
```

### Revoke All Sessions

```http
DELETE /api/v1/user/sessions
Authorization: Required
```

## Model Management API

### Create Model

```http
POST /api/v1/model/create
Authorization: Required
Content-Type: application/json

{
  "model_name": "string",
  "architecture": "string",
  "config": {
    "vocab_size": "integer",
    "hidden_size": "integer",
    "num_layers": "integer",
    "num_attention_heads": "integer"
  }
}
```

### Validate Model

```http
POST /api/v1/model/validate
Authorization: Required
Content-Type: application/json

{
  "model_config": "object"
}
```

### Load Model

```http
POST /api/v1/model/load
Authorization: Required
Content-Type: application/json

{
  "model_path": "string",
  "device": "string"
}
```

### Get Model Info

```http
GET /api/v1/model/info
Authorization: Required
```

**Response:**

```json
{
  "success": true,
  "model": {
    "name": "string",
    "architecture": "string",
    "parameters": "integer",
    "size_mb": "float",
    "device": "string"
  }
}
```

## Training API

### Start Training

```http
POST /api/v1/training/start
Authorization: Required
Content-Type: application/json

{
  "model_name": "string",
  "dataset_path": "string",
  "config": {
    "learning_rate": "float",
    "batch_size": "integer",
    "num_epochs": "integer",
    "gradient_accumulation_steps": "integer"
  }
}
```

**Response:**

```json
{
  "success": true,
  "job_id": "string"
}
```

### Get Training Status

```http
GET /api/v1/training/{job_id}/status
Authorization: Required
```

**Response:**

```json
{
  "success": true,
  "status": "string",
  "progress": "float",
  "current_epoch": "integer",
  "loss": "float",
  "metrics": "object"
}
```

### Stop Training

```http
POST /api/v1/training/{job_id}/stop
Authorization: Required
```

### Training WebSocket

```ws
ws://localhost:5000/ws/training
```

Real-time training updates via WebSocket connection.

## Memory Optimization API

This section details APIs for monitoring and managing memory usage within ImpressionCore. The `adaptive_memory_management_function` (from `src/core/memory_manager.py`) is a key component that can be triggered for dynamic adjustments.

### Get Memory Stats

```http
GET /api/v1/memory/stats
Authorization: Required
```

**Response:**

```json
{
  "success": true,
  "memory": {
    "gpu": {
      "used_mb": "float",
      "total_mb": "float",
      "utilization": "float"
    },
    "cpu": {
      "used_mb": "float",
      "total_mb": "float",
      "utilization": "float"
    }
  }
}
```

### Optimize Memory

```http
POST /api/v1/memory/optimize
Authorization: Required
Content-Type: application/json

{
  "strategy": "string (e.g., 'aggressive_gc', 'cache_pruning', 'adaptive')",
  "target_utilization": "float"
}
```

**Note:** The "adaptive" strategy leverages the `adaptive_memory_management_function`.

### Trigger Adaptive Memory Management

```http
POST /api/v1/memory/trigger-adaptive-management
Authorization: Required
Content-Type: application/json

{
  "parameters": {
    "aggressiveness": "float (optional, e.g., 0.0 to 1.0)",
    "target_metric": "string (optional, e.g., 'vram_usage_percent')"
    /* Other relevant parameters for the adaptive function */
  }
}
```

**Description:** Directly invokes the `adaptive_memory_management_function` from `src/core/memory_manager.py` to perform dynamic memory adjustments based on current system state and optional parameters.

### Clear Cache

```http
POST /api/v1/memory/clear-cache
Authorization: Required
```

## Brain Simulation API

The Brain Simulation APIs enable interaction with ImpressionCore's cognitive and knowledge representation capabilities. These are now significantly influenced and managed by the `Brain Simulation Adapter` (implemented in `src/adapters/brain_sim_adapter.py`), which orchestrates calls to underlying brain-inspired modules and the Unified Knowledge Store (UKS).

### Initialize Brain Simulation

```http
POST /api/v1/brainsim/initialize
Authorization: Required
Content-Type: application/json

{
  "config": {
    "memory_size": "integer",
    "cognitive_modules": "array"
  }
}
```

### Call Cognitive Function

```http
POST /api/v1/brainsim/cognitive/{function_name}
Authorization: Required
Content-Type: application/json

{
  "input": "string",
  "context": "object"
}
```

### Augment Prompt

```http
POST /api/v1/brainsim/augment-prompt
Authorization: Required
Content-Type: application/json

{
  "prompt": "string",
  "enhancement_type": "string"
}
```

### UKS (Unified Knowledge Store) Operations

```http
POST /api/v1/brainsim/uks/add-node
Authorization: Required
Content-Type: application/json

{
  "content": "string",
  "node_type": "string",
  "metadata": "object"
}
```

```http
GET /api/v1/brainsim/uks/query
Authorization: Required
Query Parameters: q=string&limit=integer
```

### Get Simulated Cognitive State

Retrieves the current simulated cognitive state or relevant contextual information from the brain simulation.

```http
GET /api/v1/brainsim/cognitive_state
Authorization: Bearer <api_key> (if applicable)
```

**Response:**

```json
{
  "success": true,
  "data": {
    "state_id": "string",
    "timestamp": "datetime",
    "active_concepts": ["string"],
    "emotional_valence": "float", // e.g., -1.0 (negative) to 1.0 (positive)
    "arousal_level": "float", // e.g., 0.0 (calm) to 1.0 (excited)
    "custom_context": {} // Any other relevant contextual data
  },
  "message": "Cognitive state retrieved successfully."
}
```

### Update Simulated Cognitive State (Internal/Debug)

Allows for manual updates or resets of the cognitive state, primarily for debugging or specific testing scenarios.

```http
POST /api/v1/brainsim/cognitive_state
Authorization: Bearer <api_key> (if applicable)
Content-Type: application/json

{
  "target_state": {
    "active_concepts": ["new_concept_1", "new_concept_2"],
    "emotional_valence": 0.5,
    "arousal_level": 0.8
  },
  "reset_to_default": false
}
```

**Response:**

```json
{
  "success": true,
  "message": "Cognitive state updated successfully."
}
```

## 7. Memory Optimization API (System Oversight)

Endpoints related to the Adaptive Memory Management system and System Oversight.

### Get System Memory Metrics

Retrieves current system-wide memory metrics (VRAM, RAM, Swap).

```http
GET /api/v1/system/memory_metrics
Authorization: Bearer <api_key> (if applicable)
```

**Response:** (Mirrors `SystemOversightService.update_memory_metrics()` output)

```json
{
  "success": true,
  "data": {
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
  },
  "message": "Memory metrics retrieved successfully."
}
```

### Trigger Memory Mitigation (Manual Override - Debug/Admin)

Manually triggers a specific memory mitigation strategy. This is typically handled automatically by `adaptive_memory_management` but can be exposed for testing or administrative purposes.

```http
POST /api/v1/system/trigger_mitigation
Authorization: Bearer <api_key> (if applicable)
Content-Type: application/json

{
  "action_type": "string" // e.g., "reduce_precision", "offload_to_cpu", "clear_cache_level_1"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Mitigation action 'action_type' triggered successfully/queued."
}
```

### Get System Health and Anomalies

Retrieves overall system health status and recent anomalies logged by the System Oversight Module.

```http
GET /api/v1/system/health_status
Authorization: Bearer <api_key> (if applicable)
```

**Response:**

```json
{
  "success": true,
  "data": {
    "overall_status": "string", // e.g., "HEALTHY", "WARNING", "CRITICAL"
    "cpu_usage_percent": "float",
    "ram_usage_percent": "float",
    "gpu_vram_usage_percent": "float", // If applicable
    "active_components_status": [
      {
        "id": "string",
        "name": "string",
        "status": "string", // "ONLINE", "DEGRADED", "OFFLINE"
        "health_score": "float",
        "last_checked": "datetime"
      }
    ],
    "recent_anomalies": [
      {
        "timestamp": "datetime",
        "component_id": "string",
        "severity": "string", // "LOW", "MEDIUM", "HIGH", "CRITICAL"
        "description": "string",
        "mitigation_applied": "string"
      }
    ],
    "last_full_health_check": "datetime"
  },
  "message": "System health status retrieved."
}
```

## 8. Multimodal Processing API

The Multimodal Processing API provides endpoints for handling and integrating data from various modalities. The core functionality, particularly for the `/api/v1/multimodal/process` endpoint, is now implemented through the baseline `Multimodal Processing Pipeline` located at `src/multimodal/pipeline.py`. This pipeline manages the flow of multimodal data from input, through fusion, to output.

### Process Multimodal Input

```http
POST /api/v1/multimodal/process
Authorization: Required
Content-Type: multipart/form-data

{
  "text": "string (optional)",
  "image": "file (optional)",
  "audio": "file (optional)",
  "video": "file (optional, future capability)",
  "processing_mode": "string (e.g., 'fusion', 'text_from_image', 'speech_to_text')"
}
```

**Note:** The backend for this endpoint is centered around `src/multimodal/pipeline.py`.

### Stream Processing

```http
POST /api/v1/multimodal/stream/start
Authorization: Required
Content-Type: application/json

{
  "modalities": "array",
  "buffer_size": "integer",
  "processing_config": "object"
}
```

### Cross-Modal Attention

```http
POST /api/v1/multimodal/attention
Authorization: Required
Content-Type: application/json

{
  "query_modality": "string",
  "key_modalities": "array",
  "input_data": "object"
}
```

## Deployment API

The Deployment API provides comprehensive model deployment capabilities across multiple platforms and optimization strategies. This API leverages the deployment manager orchestrator implemented in `src/deployment/deployment_manager.py` and supports ONNX export, TensorRT optimization, mobile deployment, and distributed inference.

### Deploy Model

```http
POST /api/v1/deployment/deploy
Authorization: Required
Content-Type: application/json

{
  "model_name": "string",
  "deployment_type": "string", // "onnx", "tensorrt", "mobile", "distributed"
  "target_platform": "string", // "desktop", "server", "mobile", "cloud"
  "config": {
    "output_dir": "string",
    "batch_size": "integer",
    "sequence_length": "integer",
    "precision": "string", // "fp32", "fp16", "int8", "int4"
    "optimize_for_inference": "boolean",
    "quantization_enabled": "boolean",
    "memory_optimization": "boolean",
    "max_memory_gb": "float",
    "target_latency_ms": "float",
    "min_throughput_tokens_per_sec": "float"
  }
}
```

**Response:**

```json
{
  "success": true,
  "deployment_id": "string",
  "model_path": "string",
  "deployment_type": "string",
  "optimization_applied": "boolean",
  "performance_metrics": {
    "latency_ms": "float",
    "throughput_tokens_per_sec": "float",
    "memory_usage_mb": "float",
    "model_size_mb": "float"
  }
}
```

### Get Deployment Status

```http
GET /api/v1/deployment/status/{deployment_id}
Authorization: Required
```

**Response:**

```json
{
  "success": true,
  "deployment_id": "string",
  "status": "string", // "pending", "in_progress", "completed", "failed"
  "progress": "float", // 0.0 to 1.0
  "message": "string",
  "logs": "array",
  "artifacts": "object"
}
```

### List Deployments

```http
GET /api/v1/deployment/list
Authorization: Required
Query Parameters: limit=integer&offset=integer&status=string
```

**Response:**

```json
{
  "success": true,
  "deployments": [
    {
      "deployment_id": "string",
      "model_name": "string",
      "deployment_type": "string",
      "target_platform": "string",
      "status": "string",
      "created_at": "string",
      "completed_at": "string",
      "performance_metrics": "object"
    }
  ],
  "total": "integer"
}
```

### Hardware Compatibility Check

```http
GET /api/v1/deployment/compatibility
Authorization: Required
Query Parameters: deployment_type=string&target_platform=string
```

**Response:**

```json
{
  "success": true,
  "compatible": "boolean",
  "hardware_info": {
    "cuda_available": "boolean",
    "device_count": "integer",
    "device_name": "string",
    "memory_available_gb": "float",
    "tensorrt_available": "boolean",
    "onnx_available": "boolean"
  },
  "recommendations": "array"
}
```

### Benchmark Deployment

```http
POST /api/v1/deployment/benchmark
Authorization: Required
Content-Type: application/json

{
  "deployment_id": "string",
  "benchmark_config": {
    "iterations": "integer",
    "warmup_iterations": "integer",
    "test_inputs": "array"
  }
}
```

**Response:**

```json
{
  "success": true,
  "deployment_id": "string",
  "benchmark_results": {
    "avg_latency_ms": "float",
    "min_latency_ms": "float",
    "max_latency_ms": "float",
    "throughput_tokens_per_sec": "float",
    "memory_usage_mb": "float",
    "gpu_utilization_percent": "float"
  }
}
```

### Get Deployment Artifacts

```http
GET /api/v1/deployment/artifacts/{deployment_id}
Authorization: Required
```

**Response:**

```json
{
  "success": true,
  "deployment_id": "string",
  "artifacts": {
    "model_path": "string",
    "config_path": "string",
    "optimization_report": "string",
    "performance_report": "string",
    "deployment_logs": "string"
  }
}
```

### Delete Deployment

```http
DELETE /api/v1/deployment/{deployment_id}
Authorization: Required
```

**Response:**

```json
{
  "success": true,
  "message": "Deployment deleted successfully"
}
```

## System Information API

### Get System Status

```http
GET /api/v1/status
```

**Response:**

```json
{
  "success": true,
  "status": "string",
  "version": "string",
  "uptime": "integer",
  "resources": "object"
}
```

### GPU Information

```http
GET /api/v1/system/gpu_info
```

**Response:**

```json
{
  "success": true,
  "gpu": {
    "name": "string",
    "memory_total": "float",
    "memory_used": "float",
    "utilization": "float",
    "temperature": "float"
  }
}
```

### Check GPU

```http
GET /api/check_gpu
```

### Verify PyTorch GPU

```http
GET /api/verify_pytorch_gpu
```

## Metrics API

### Memory Metrics

```http
GET /metrics/api/memory
Query Parameters: days=integer&model=string
```

**Response:**

```json
{
  "success": true,
  "data": [
    {
      "timestamp": "string",
      "model_name": "string",
      "memory_usage": "float",
      "gpu_utilization": "float"
    }
  ]
}
```

### Model Quality Metrics

```http
GET /metrics/api/models
Query Parameters: model=string&feature=string
```

**Response:**

```json
{
  "success": true,
  "data": [
    {
      "model_name": "string",
      "accuracy": "float",
      "loss": "float",
      "perplexity": "float",
      "has_moe": "boolean",
      "has_lora": "boolean"
    }
  ]
}
```

### Advanced Features Metrics

```http
GET /metrics/api/advanced
```

### Hardware Metrics

```http
GET /metrics/api/hardware
```

## Evaluation API

### Get Evaluation Metrics

```http
GET /api/evaluation_metrics
```

**Response:**

```json
{
  "success": true,
  "data": {
    "accuracy": "float",
    "loss": "float",
    "perplexity": "float",
    "bleu_score": "float"
  }
}
```

### Get Evaluation History

```http
GET /api/evaluation_history
```

## Settings API

### Get/Update Settings

```http
GET /api/v1/settings
Authorization: Required
```

```http
POST /api/v1/settings
Authorization: Required
Content-Type: application/json

{
  "settings": "object"
}
```

## Walkthrough API

### Execute Walkthrough Action

```http
GET /api/v1/walkthrough/action/{action_type}
Authorization: Required
```

## Error Handling

All API endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "string",
  "code": "string",
  "details": "object"
}
```

### Common HTTP Status Codes

- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Rate Limited
- `500` - Internal Server Error

## Rate Limiting

API endpoints are subject to rate limiting:

- **Default**: 1000 requests per hour per IP
- **Authenticated users**: 5000 requests per hour
- **Training operations**: 10 concurrent operations

## WebSocket Endpoints

### Training Updates

```ws
ws://localhost:5000/ws/training
```

Real-time training progress, loss updates, and metrics.

### Tokenizer Training

```ws
ws://localhost:5000/ws/tokenizer/{job_id}
```

Real-time tokenizer training progress.

## SDK Examples

### Python SDK Usage

```python
import requests

# Login
response = requests.post('http://localhost:5000/login', json={
    'username': 'admin',
    'password': 'admin'
})

# Start training
response = requests.post('http://localhost:5000/api/v1/training/start', json={
    'model_name': 'my_model',
    'dataset_path': '/path/to/dataset',
    'config': {
        'learning_rate': 0.001,
        'batch_size': 16,
        'num_epochs': 10
    }
})

job_id = response.json()['job_id']

# Monitor training
response = requests.get(f'http://localhost:5000/api/v1/training/{job_id}/status')
status = response.json()
```

### JavaScript/Fetch Usage

```javascript
// Login
const loginResponse = await fetch('/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        username: 'admin',
        password: 'admin'
    })
});

// Get system status
const statusResponse = await fetch('/api/v1/status');
const status = await statusResponse.json();

// WebSocket connection
const ws = new WebSocket('ws://localhost:5000/ws/training');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Training update:', data);
};
```

## Versioning

The API uses semantic versioning:

- Current version: `v1`
- Breaking changes will increment the major version
- Backward compatibility maintained within major versions

## Support

For API support and issues:

- Documentation: `/docs/api/`
- Issues: Project GitHub repository
- Contact: Kirk LaSalle

---

## API Reference Information

This API reference is automatically generated and updated. Last updated: 2025-05-30
