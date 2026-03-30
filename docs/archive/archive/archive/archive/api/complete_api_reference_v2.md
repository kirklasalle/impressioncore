# ⚠️ ARCHIVED FILE

**Created:** June 03, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\archive\archive\archive\api\complete_api_reference_v2.md #api #attention_mechanism #command_line #docs\api\complete_api_reference_v2.md #documentation #gpu_optimization #inference #memory_management #multimodal #testing #training #web_interface [api, reference, endpoints, multimodal, b1-model, 2025]  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

This file has been archived for historical, compatibility, or deprecation reasons. Do not modify or use in active development.

# Complete Api Reference V2

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** Kirk LaSalle  
**Tags:** #api #attention_mechanism #command_line #docs\api\complete_api_reference_v2.md #documentation #gpu_optimization #inference #memory_management #multimodal #testing #training #web_interface  
**Category:** Documentation  
**Status:** Deprecated

---
title: "ImpressionCore API Reference - Complete Documentation"
tags: [api, reference, endpoints, multimodal, b1-model, 2025]
created: 2025-06-03
modified: 2025-06-03
version: 2.0.0
authors: 

  - "Kirk LaSalle"
  - "GitHub Copilot"

status: active
category: api
priority: high
---

# ImpressionCore API Reference - Complete Documentation

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Core API Endpoints](#core-api-endpoints)
4. [Multimodal Processing](#multimodal-processing)
5. [Memory Management](#memory-management)
6. [Brain Simulation](#brain-simulation)
7. [Model Management](#model-management)
8. [Training API](#training-api)
9. [Data Pipeline API](#data-pipeline-api)
10. [Monitoring & Analytics](#monitoring--analytics)
11. [Error Handling](#error-handling)
12. [SDK & Client Libraries](#sdk--client-libraries)
13. [Examples](#examples)
14. [Rate Limits](#rate-limits)
15. [Changelog](#changelog)

## Overview

The ImpressionCore API provides comprehensive access to multimodal AI capabilities, brain-inspired processing, and memory management. The API is designed for efficiency on consumer hardware and supports real-time multimodal interactions.

For a detailed view of the complete API architecture, see [API Architecture Diagram](../assets/images/api_architecture.md).

### Base URL

``` text
Production: https://api.impressioncore.ai/v2
Development: http://localhost:8000/v2
```

### API Versioning

- **Current Version**: v2.0.0
- **Supported Versions**: v2.x, v1.x (deprecated)
- **Version Header**: `X-API-Version: 2.0`

### Response Format

All API responses follow a consistent JSON structure:

```json
{
    "success": true,
    "data": {},
    "metadata": {
        "version": "2.0.0",
        "timestamp": "2025-06-03T15:30:00Z",
        "request_id": "req_abc123",
        "processing_time_ms": 150
    },
    "error": null
}
```

## Authentication

### API Key Authentication

```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
X-API-Version: 2.0
```

### Getting an API Key

```bash
curl -X POST https://api.impressioncore.ai/v2/auth/api-key \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "organization": "Your Organization"
  }'
```

### Token Refresh

```bash
curl -X POST https://api.impressioncore.ai/v2/auth/refresh \
  -H "Authorization: Bearer YOUR_REFRESH_TOKEN" \
  -H "Content-Type: application/json"
```

## Core API Endpoints

### Health Check

**GET** `/health`

Check API health and system status.

```bash
curl -X GET https://api.impressioncore.ai/v2/health
```

**Response:**
```json
{
    "success": true,
    "data": {
        "status": "healthy",
        "version": "2.0.0",
        "uptime_seconds": 3600,
        "gpu_available": true,
        "memory_usage_gb": 2.1,
        "active_models": ["impressioncore_b1"],
        "system_load": 0.65
    }
}
```

### System Information

**GET** `/system/info`

Get detailed system information and capabilities.

```bash
curl -X GET https://api.impressioncore.ai/v2/system/info \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
    "success": true,
    "data": {
        "hardware": {
            "gpu_name": "NVIDIA GTX 1050 Ti",
            "gpu_memory_gb": 4.0,
            "cpu_cores": 4,
            "system_memory_gb": 32.0
        },
        "models": [
            {
                "name": "impressioncore_b1",
                "version": "2.0.0",
                "modalities": ["text", "image", "audio"],
                "memory_usage_gb": 2.1,
                "status": "loaded"
            }
        ],
        "capabilities": {
            "multimodal_fusion": true,
            "brain_simulation": true,
            "memory_optimization": true,
            "real_time_processing": true
        }
    }
}
```

## Multimodal Processing

### Text Generation

**POST** `/generate/text`

Generate text using ImpressionCore's language capabilities.

```bash
curl -X POST https://api.impressioncore.ai/v2/generate/text \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in simple terms",
    "max_length": 500,
    "temperature": 0.7,
    "top_p": 0.9,
    "brain_simulation": true,
    "memory_context": true
  }'
```

**Request Body:**
```json
{
    "prompt": "string (required)",
    "max_length": "integer (default: 512)",
    "temperature": "float (default: 0.7, range: 0.0-2.0)",
    "top_p": "float (default: 0.9, range: 0.0-1.0)",
    "top_k": "integer (default: 50)",
    "brain_simulation": "boolean (default: true)",
    "memory_context": "boolean (default: true)",
    "context_window": "integer (default: 2048)",
    "stream": "boolean (default: false)"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "generated_text": "Quantum computing is like having a magical calculator...",
        "tokens_generated": 125,
        "processing_time_ms": 1250,
        "brain_state": {
            "attention_patterns": [...],
            "memory_activations": [...],
            "cognitive_load": 0.75
        }
    },
    "metadata": {
        "model": "impressioncore_b1",
        "memory_usage_gb": 2.3,
        "gpu_utilization": 0.85
    }
}
```

### Image Generation

**POST** `/generate/image`

Generate images from text descriptions or other inputs.

```bash
curl -X POST https://api.impressioncore.ai/v2/generate/image \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A serene mountain landscape at sunset",
    "width": 512,
    "height": 512,
    "guidance_scale": 7.5,
    "num_inference_steps": 50,
    "brain_context": true
  }'
```

**Request Body:**
```json
{
    "prompt": "string (required)",
    "negative_prompt": "string (optional)",
    "width": "integer (default: 512, options: 256, 512, 768, 1024)",
    "height": "integer (default: 512, options: 256, 512, 768, 1024)",
    "guidance_scale": "float (default: 7.5, range: 1.0-20.0)",
    "num_inference_steps": "integer (default: 50, range: 10-100)",
    "seed": "integer (optional)",
    "brain_context": "boolean (default: true)",
    "style": "string (optional: realistic, artistic, cartoon)",
    "format": "string (default: jpeg, options: jpeg, png, webp)"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "image_url": "https://cdn.impressioncore.ai/images/abc123.jpg",
        "image_base64": "data:image/jpeg;base64,/9j/4AAQ...",
        "width": 512,
        "height": 512,
        "format": "jpeg",
        "processing_time_ms": 5200,
        "generation_params": {
            "actual_steps": 50,
            "guidance_scale": 7.5,
            "seed": 42
        }
    }
}
```

### Audio Generation

**POST** `/generate/audio`

Generate audio from text or other modalities.

```bash
curl -X POST https://api.impressioncore.ai/v2/generate/audio \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a sample text to convert to speech",
    "voice": "neutral",
    "speed": 1.0,
    "pitch": 0.0,
    "emotion": "calm",
    "format": "wav"
  }'
```

**Request Body:**
```json
{
    "text": "string (required)",
    "voice": "string (default: neutral, options: neutral, male, female, child)",
    "speed": "float (default: 1.0, range: 0.5-2.0)",
    "pitch": "float (default: 0.0, range: -2.0-2.0)",
    "emotion": "string (default: neutral, options: neutral, happy, sad, angry, calm)",
    "language": "string (default: en, options: en, es, fr, de, it)",
    "format": "string (default: wav, options: wav, mp3, flac)",
    "sample_rate": "integer (default: 22050, options: 16000, 22050, 44100)",
    "brain_prosody": "boolean (default: true)"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "audio_url": "https://cdn.impressioncore.ai/audio/abc123.wav",
        "audio_base64": "data:audio/wav;base64,UklGRnoGAABXQVZF...",
        "duration_seconds": 3.5,
        "sample_rate": 22050,
        "format": "wav",
        "processing_time_ms": 800,
        "voice_characteristics": {
            "voice_id": "neutral_v2",
            "emotional_intensity": 0.6,
            "prosody_score": 0.85
        }
    }
}
```

### Multimodal Fusion

**POST** `/process/multimodal`

Process multiple modalities together for enhanced understanding.

```bash
curl -X POST https://api.impressioncore.ai/v2/process/multimodal \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "image=@path/to/image.jpg" \
  -F "audio=@path/to/audio.wav" \
  -F "data={
    \"text\": \"Describe what you see and hear\",
    \"task\": \"caption_and_analyze\",
    \"output_modalities\": [\"text\", \"audio\"],
    \"brain_integration\": true
  }"
```

**Request Parameters:**
```json
{
    "text": "string (optional)",
    "image": "file or base64 (optional)",
    "audio": "file or base64 (optional)",
    "task": "string (required: caption, analyze, generate, translate)",
    "output_modalities": "array (default: [\"text\"])",
    "brain_integration": "boolean (default: true)",
    "cross_modal_attention": "boolean (default: true)",
    "context_memory": "boolean (default: true)"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "text_output": "I can see a beautiful sunset over a calm lake...",
        "audio_output": "https://cdn.impressioncore.ai/audio/description_abc123.wav",
        "analysis": {
            "visual_elements": ["sunset", "lake", "mountains", "reflection"],
            "audio_elements": ["gentle waves", "bird calls", "wind"],
            "emotional_tone": "peaceful",
            "scene_understanding": {
                "location": "natural setting",
                "time_of_day": "evening",
                "weather": "calm",
                "mood": "serene"
            }
        },
        "cross_modal_features": {
            "visual_audio_alignment": 0.92,
            "semantic_coherence": 0.88,
            "emotional_consistency": 0.95
        }
    }
}
```

## Memory Management

### Memory Context

**GET** `/memory/context/{session_id}`

Retrieve memory context for a session.

```bash
curl -X GET https://api.impressioncore.ai/v2/memory/context/session_123 \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
    "success": true,
    "data": {
        "session_id": "session_123",
        "working_memory": {
            "capacity": 1024,
            "current_usage": 256,
            "active_concepts": ["quantum computing", "explanation", "simplification"]
        },
        "episodic_memory": {
            "recent_interactions": [
                {
                    "timestamp": "2025-06-03T15:25:00Z",
                    "modality": "text",
                    "content_summary": "Quantum computing explanation request",
                    "emotional_context": "curious"
                }
            ],
            "total_memories": 47
        },
        "semantic_memory": {
            "knowledge_domains": ["technology", "physics", "education"],
            "concept_relationships": [...],
            "expertise_areas": ["quantum physics", "computer science"]
        }
    }
}
```

### Memory Update

**POST** `/memory/update/{session_id}`

Update memory context with new information.

```bash
curl -X POST https://api.impressioncore.ai/v2/memory/update/session_123 \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "interaction": {
      "modality": "text",
      "content": "User asked about quantum computing applications",
      "context": "educational discussion",
      "importance": 0.8
    },
    "consolidate": true
  }'
```

**Request Body:**
```json
{
    "interaction": {
        "modality": "string (required: text, image, audio, multimodal)",
        "content": "string (required)",
        "context": "string (optional)",
        "emotional_state": "string (optional)",
        "importance": "float (default: 0.5, range: 0.0-1.0)"
    },
    "consolidate": "boolean (default: false)",
    "priority": "string (default: normal, options: low, normal, high, critical)"
}
```

### Memory Analytics

**GET** `/memory/analytics/{session_id}`

Get memory usage analytics and insights.

```bash
curl -X GET https://api.impressioncore.ai/v2/memory/analytics/session_123 \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
    "success": true,
    "data": {
        "memory_efficiency": {
            "working_memory_utilization": 0.65,
            "episodic_memory_health": 0.92,
            "semantic_coherence": 0.88,
            "consolidation_rate": 0.78
        },
        "interaction_patterns": {
            "dominant_modalities": ["text", "multimodal"],
            "topic_clusters": ["technology", "education", "science"],
            "temporal_patterns": "consistent_engagement",
            "complexity_trend": "increasing"
        },
        "recommendations": [
            "Consider expanding semantic knowledge in quantum physics",
            "Working memory showing healthy usage patterns",
            "Episodic consolidation performing optimally"
        ]
    }
}
```

## Brain Simulation

### Cognitive State

**GET** `/brain/cognitive-state/{session_id}`

Get current cognitive state and brain simulation data.

```bash
curl -X GET https://api.impressioncore.ai/v2/brain/cognitive-state/session_123 \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
    "success": true,
    "data": {
        "attention_state": {
            "focus_areas": ["language_processing", "knowledge_retrieval"],
            "attention_intensity": 0.78,
            "distraction_level": 0.12,
            "cognitive_load": 0.65
        },
        "processing_regions": {
            "language_cortex": {
                "activation": 0.85,
                "efficiency": 0.92,
                "resource_usage": 0.68
            },
            "visual_cortex": {
                "activation": 0.23,
                "efficiency": 0.88,
                "resource_usage": 0.15
            },
            "integration_areas": {
                "activation": 0.67,
                "efficiency": 0.79,
                "resource_usage": 0.55
            }
        },
        "memory_integration": {
            "working_memory_binding": 0.82,
            "episodic_retrieval": 0.74,
            "semantic_activation": 0.89
        }
    }
}
```

### Brain Metrics

**GET** `/brain/metrics/{session_id}`

Get detailed brain simulation metrics and performance data.

```bash
curl -X GET https://api.impressioncore.ai/v2/brain/metrics/session_123 \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -G -d "time_range=1h" -d "granularity=minute"
```

**Query Parameters:**

- `time_range`: `string` (default: 1h, options: 15m, 1h, 6h, 24h, 7d)
- `granularity`: `string` (default: minute, options: second, minute, hour)
- `metrics`: `array` (optional, filter specific metrics)

**Response:**
```json
{
    "success": true,
    "data": {
        "time_series": [
            {
                "timestamp": "2025-06-03T15:30:00Z",
                "cognitive_load": 0.65,
                "attention_focus": 0.78,
                "memory_efficiency": 0.82,
                "processing_speed": 0.91,
                "neural_plasticity": 0.67
            }
        ],
        "aggregated_metrics": {
            "average_cognitive_load": 0.68,
            "peak_attention": 0.95,
            "memory_consolidation_events": 12,
            "adaptation_rate": 0.73
        },
        "insights": [
            "Consistent high-performance cognitive processing",
            "Memory system showing excellent consolidation",
            "Attention patterns indicate engaged learning state"
        ]
    }
}
```

## Model Management

### Available Models

**GET** `/models`

List all available models and their capabilities.

```bash
curl -X GET https://api.impressioncore.ai/v2/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
    "success": true,
    "data": {
        "models": [
            {
                "id": "impressioncore_b1",
                "name": "ImpressionCore B1",
                "version": "2.0.0",
                "description": "Multimodal brain-inspired AI model",
                "modalities": ["text", "image", "audio"],
                "capabilities": [
                    "multimodal_fusion",
                    "brain_simulation",
                    "adaptive_memory",
                    "real_time_processing"
                ],
                "memory_requirements_gb": 2.1,
                "inference_speed": "fast",
                "quality": "high",
                "status": "active"
            },
            {
                "id": "impressioncore_lite",
                "name": "ImpressionCore Lite",
                "version": "2.0.0",
                "description": "Lightweight variant for resource-constrained environments",
                "modalities": ["text", "audio"],
                "capabilities": [
                    "basic_fusion",
                    "memory_optimization",
                    "fast_inference"
                ],
                "memory_requirements_gb": 0.8,
                "inference_speed": "very_fast",
                "quality": "medium",
                "status": "active"
            }
        ]
    }
}
```

### Model Information

**GET** `/models/{model_id}`

Get detailed information about a specific model.

```bash
curl -X GET https://api.impressioncore.ai/v2/models/impressioncore_b1 \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Load Model

**POST** `/models/{model_id}/load`

Load a specific model for use.

```bash
curl -X POST https://api.impressioncore.ai/v2/models/impressioncore_b1/load \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "optimization_level": "balanced",
    "memory_limit_gb": 3.0,
    "precision": "mixed"
  }'
```

## Training API

### Training Jobs

**POST** `/training/jobs`

Create a new training job.

```bash
curl -X POST https://api.impressioncore.ai/v2/training/jobs \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model_config": {
      "base_model": "impressioncore_b1",
      "modalities": ["text", "image"],
      "optimization": "memory_efficient"
    },
    "dataset": {
      "training_data": "dataset_abc123",
      "validation_split": 0.1,
      "test_split": 0.1
    },
    "training_config": {
      "epochs": 10,
      "batch_size": 16,
      "learning_rate": 1e-4,
      "mixed_precision": true,
      "gradient_checkpointing": true
    }
  }'
```

**Response:**
```json
{
    "success": true,
    "data": {
        "job_id": "job_xyz789",
        "status": "queued",
        "estimated_duration_hours": 4.5,
        "estimated_cost": 12.50,
        "created_at": "2025-06-03T15:30:00Z",
        "model_config": {...},
        "progress_url": "/training/jobs/job_xyz789/progress"
    }
}
```

### Training Progress

**GET** `/training/jobs/{job_id}/progress`

Get training job progress and metrics.

```bash
curl -X GET https://api.impressioncore.ai/v2/training/jobs/job_xyz789/progress \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Training Logs

**GET** `/training/jobs/{job_id}/logs`

Get training logs and detailed metrics.

```bash
curl -X GET https://api.impressioncore.ai/v2/training/jobs/job_xyz789/logs \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -G -d "lines=100" -d "level=info"
```

## Data Pipeline API

### Dataset Upload

**POST** `/data/datasets`

Upload a new dataset for training or fine-tuning.

```bash
curl -X POST https://api.impressioncore.ai/v2/data/datasets \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "dataset=@path/to/dataset.zip" \
  -F "metadata={
    \"name\": \"Custom Multimodal Dataset\",
    \"description\": \"Dataset for custom training\",
    \"modalities\": [\"text\", \"image\"],
    \"format\": \"json\",
    \"license\": \"MIT\"
  }"
```

### Data Processing

**POST** `/data/process`

Process uploaded data through the ImpressionCore pipeline.

```bash
curl -X POST https://api.impressioncore.ai/v2/data/process \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "dataset_abc123",
    "processing_config": {
      "validation": true,
      "cleaning": true,
      "augmentation": false,
      "quality_threshold": 0.8
    },
    "output_format": "h5"
  }'
```

### Data Quality Report

**GET** `/data/datasets/{dataset_id}/quality`

Get data quality analysis and recommendations.

```bash
curl -X GET https://api.impressioncore.ai/v2/data/datasets/dataset_abc123/quality \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Monitoring & Analytics

### Usage Analytics

**GET** `/analytics/usage`

Get API usage analytics and statistics.

```bash
curl -X GET https://api.impressioncore.ai/v2/analytics/usage \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -G -d "period=7d" -d "granularity=day"
```

**Response:**
```json
{
    "success": true,
    "data": {
        "period": "7d",
        "total_requests": 15420,
        "total_processing_time_hours": 12.5,
        "breakdown_by_endpoint": {
            "/generate/text": 8920,
            "/generate/image": 3240,
            "/generate/audio": 1820,
            "/process/multimodal": 1440
        },
        "breakdown_by_modality": {
            "text": 12160,
            "image": 4680,
            "audio": 3420,
            "multimodal": 1440
        },
        "performance_metrics": {
            "average_response_time_ms": 1250,
            "p95_response_time_ms": 3200,
            "success_rate": 0.997,
            "memory_efficiency": 0.89
        }
    }
}
```

### Performance Monitoring

**GET** `/monitoring/performance`

Get real-time performance metrics.

```bash
curl -X GET https://api.impressioncore.ai/v2/monitoring/performance \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
    "success": true,
    "data": {
        "system_health": "healthy",
        "gpu_metrics": {
            "utilization": 0.75,
            "memory_usage_gb": 2.8,
            "temperature_celsius": 65,
            "power_usage_watts": 120
        },
        "cpu_metrics": {
            "utilization": 0.45,
            "memory_usage_gb": 8.2,
            "load_average": [1.2, 1.1, 1.0]
        },
        "model_metrics": {
            "active_models": 2,
            "total_memory_gb": 2.1,
            "inference_queue_length": 3,
            "average_latency_ms": 145
        },
        "api_metrics": {
            "requests_per_minute": 25,
            "active_sessions": 12,
            "error_rate": 0.003
        }
    }
}
```

## Error Handling

### Error Response Format

```json
{
    "success": false,
    "data": null,
    "error": {
        "code": "INVALID_INPUT",
        "message": "The provided input format is not supported",
        "details": {
            "field": "image",
            "expected": "JPEG, PNG, WebP",
            "received": "BMP"
        },
        "request_id": "req_abc123",
        "timestamp": "2025-06-03T15:30:00Z"
    }
}
```

### Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_INPUT` | Invalid input parameters | 400 |
| `UNAUTHORIZED` | Invalid or missing authentication | 401 |
| `FORBIDDEN` | Insufficient permissions | 403 |
| `NOT_FOUND` | Resource not found | 404 |
| `RATE_LIMITED` | Rate limit exceeded | 429 |
| `MODEL_UNAVAILABLE` | Requested model is not available | 503 |
| `MEMORY_EXCEEDED` | Insufficient memory for processing | 507 |
| `PROCESSING_TIMEOUT` | Request processing timeout | 504 |
| `INTERNAL_ERROR` | Internal server error | 500 |

### Retry Strategy

```python
import time
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def api_request_with_retry(url, headers, data):
    response = requests.post(url, headers=headers, json=data)
    
    # Retry on server errors or rate limits
    if response.status_code in [429, 500, 502, 503, 504]:
        raise Exception(f"Retryable error: {response.status_code}")
    
    return response
```

## SDK & Client Libraries

### Python SDK

**Installation:**
```bash
pip install impressioncore-api
```

**Usage:**
```python
from impressioncore import ImpressionCoreClient

# Initialize client
client = ImpressionCoreClient(api_key="your_api_key")

# Text generation
response = client.generate.text(
    prompt="Explain quantum computing",
    max_length=500,
    temperature=0.7
)

# Multimodal processing
with open("image.jpg", "rb") as img_file:
    response = client.process.multimodal(
        text="What's in this image?",
        image=img_file,
        task="caption"
    )

# Memory management
memory_context = client.memory.get_context("session_123")
```

### JavaScript SDK

**Installation:**
```bash
npm install @impressioncore/api
```

**Usage:**
```javascript
import { ImpressionCoreClient } from '@impressioncore/api';

// Initialize client
const client = new ImpressionCoreClient({
    apiKey: 'your_api_key',
    baseURL: 'https://api.impressioncore.ai/v2'
});

// Text generation
const response = await client.generate.text({
    prompt: 'Explain quantum computing',
    maxLength: 500,
    temperature: 0.7
});

// Image generation
const imageResponse = await client.generate.image({
    prompt: 'A serene mountain landscape',
    width: 512,
    height: 512
});
```

### Curl Examples

**Streaming Text Generation:**
```bash
curl -X POST https://api.impressioncore.ai/v2/generate/text \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a story about AI",
    "max_length": 1000,
    "stream": true
  }' \
  --no-buffer
```

**Batch Processing:**
```bash
curl -X POST https://api.impressioncore.ai/v2/process/batch \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "id": "req1",
        "endpoint": "/generate/text",
        "params": {"prompt": "Hello world"}
      },
      {
        "id": "req2", 
        "endpoint": "/generate/image",
        "params": {"prompt": "Beautiful sunset"}
      }
    ]
  }'
```

## Examples

### Complete Multimodal Workflow

```python
#!/usr/bin/env python3
"""Complete multimodal workflow example."""

import requests
import base64
import time

class ImpressionCoreDemo:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.impressioncore.ai/v2"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-API-Version": "2.0"
        }
    
    def multimodal_story_creation(self):
        """Create a complete story with text, image, and audio."""
        
        # Step 1: Generate initial story text
        print("🔄 Generating story text...")
        text_response = requests.post(
            f"{self.base_url}/generate/text",
            headers=self.headers,
            json={
                "prompt": "Write a short story about a magical forest",
                "max_length": 500,
                "temperature": 0.8,
                "brain_simulation": True
            }
        )
        
        story_text = text_response.json()["data"]["generated_text"]
        print(f"✅ Generated story: {story_text[:100]}...")
        
        # Step 2: Generate illustration based on story
        print("🔄 Generating story illustration...")
        image_response = requests.post(
            f"{self.base_url}/generate/image",
            headers=self.headers,
            json={
                "prompt": f"Illustration for this story: {story_text[:200]}",
                "width": 768,
                "height": 512,
                "guidance_scale": 8.0,
                "brain_context": True
            }
        )
        
        image_url = image_response.json()["data"]["image_url"]
        print(f"✅ Generated illustration: {image_url}")
        
        # Step 3: Generate narration audio
        print("🔄 Generating story narration...")
        audio_response = requests.post(
            f"{self.base_url}/generate/audio",
            headers=self.headers,
            json={
                "text": story_text,
                "voice": "neutral",
                "emotion": "mystical",
                "speed": 0.9,
                "brain_prosody": True
            }
        )
        
        audio_url = audio_response.json()["data"]["audio_url"]
        print(f"✅ Generated narration: {audio_url}")
        
        # Step 4: Analyze multimodal coherence
        print("🔄 Analyzing multimodal coherence...")
        
        # Download image for analysis
        img_data = requests.get(image_url).content
        img_b64 = base64.b64encode(img_data).decode()
        
        # Download audio for analysis
        audio_data = requests.get(audio_url).content
        audio_b64 = base64.b64encode(audio_data).decode()
        
        analysis_response = requests.post(
            f"{self.base_url}/process/multimodal",
            headers=self.headers,
            json={
                "text": story_text,
                "image": img_b64,
                "audio": audio_b64,
                "task": "analyze",
                "brain_integration": True
            }
        )
        
        analysis = analysis_response.json()["data"]["analysis"]
        coherence = analysis_response.json()["data"]["cross_modal_features"]
        
        print(f"✅ Coherence analysis:")
        print(f"   - Visual-text alignment: {coherence['visual_audio_alignment']:.2f}")
        print(f"   - Semantic coherence: {coherence['semantic_coherence']:.2f}")
        print(f"   - Emotional consistency: {coherence['emotional_consistency']:.2f}")
        
        return {
            "story_text": story_text,
            "illustration_url": image_url,
            "narration_url": audio_url,
            "coherence_metrics": coherence
        }

# Usage
if __name__ == "__main__":
    demo = ImpressionCoreDemo("your_api_key")
    result = demo.multimodal_story_creation()
    print("\n🎉 Complete multimodal story created successfully!")
```

### Real-time Conversation

```python
#!/usr/bin/env python3
"""Real-time conversation with memory and brain simulation."""

import asyncio
import websockets
import json

class ConversationDemo:
    def __init__(self, api_key):
        self.api_key = api_key
        self.session_id = "conversation_session_001"
        self.memory_context = {}
    
    async def start_conversation(self):
        """Start real-time conversation with ImpressionCore."""
        
        uri = f"wss://api.impressioncore.ai/v2/ws/conversation?api_key={self.api_key}"
        
        async with websockets.connect(uri) as websocket:
            # Initialize session
            await websocket.send(json.dumps({
                "type": "init_session",
                "session_id": self.session_id,
                "config": {
                    "brain_simulation": True,
                    "memory_context": True,
                    "real_time_processing": True
                }
            }))
            
            print("🤖 ImpressionCore: Hello! I'm ready to chat with full brain simulation.")
            
            while True:
                try:
                    # Get user input
                    user_input = input("\n👤 You: ")
                    
                    if user_input.lower() in ['exit', 'quit']:
                        break
                    
                    # Send message
                    await websocket.send(json.dumps({
                        "type": "message",
                        "content": user_input,
                        "modality": "text",
                        "brain_context": True
                    }))
                    
                    # Receive response
                    response = await websocket.recv()
                    data = json.loads(response)
                    
                    if data["type"] == "response":
                        print(f"🤖 ImpressionCore: {data['content']}")
                        
                        # Display brain metrics if available
                        if "brain_metrics" in data:
                            metrics = data["brain_metrics"]
                            print(f"   📊 Cognitive load: {metrics['cognitive_load']:.2f}")
                            print(f"   🧠 Attention focus: {metrics['attention_focus']:.2f}")
                            print(f"   💭 Memory integration: {metrics['memory_integration']:.2f}")
                    
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed")
                    break
                except KeyboardInterrupt:
                    print("\nExiting conversation...")
                    break

# Usage
if __name__ == "__main__":
    demo = ConversationDemo("your_api_key")
    asyncio.run(demo.start_conversation())
```

## Rate Limits

### Current Limits

| Tier | Requests/Minute | Requests/Day | Max Concurrent |
|------|----------------|--------------|----------------|
| Free | 10 | 1,000 | 2 |
| Basic | 100 | 10,000 | 5 |
| Pro | 1,000 | 100,000 | 20 |
| Enterprise | Custom | Custom | Custom |

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1609459200
X-RateLimit-Retry-After: 60
```

### Handling Rate Limits

```python
def handle_rate_limit(response):
    if response.status_code == 429:
        retry_after = int(response.headers.get('X-RateLimit-Retry-After', 60))
        print(f"Rate limited. Retrying in {retry_after} seconds...")
        time.sleep(retry_after)
        return True
    return False
```

## Changelog

### Version 2.0.0 (2025-06-03)

**New Features:**

- Complete multimodal API with text, image, and audio generation
- Brain simulation integration with cognitive state monitoring
- Adaptive memory management with session-based context
- Real-time WebSocket API for conversations
- Comprehensive training and data pipeline APIs

**Improvements:**

- Optimized for 4GB VRAM consumer hardware
- Enhanced error handling and retry mechanisms
- Improved response times and memory efficiency
- Better documentation and examples

**Breaking Changes:**

- API endpoints restructured under `/v2/`
- Authentication now requires Bearer token format
- Response format standardized across all endpoints

### Version 1.x (Deprecated)

Legacy API versions are deprecated and will be sunset on 2025-12-31.

---

## Related Documentation

- [Training Data Guide](../reference/training_data_guide_complete.md) - Complete data preparation guide
- [Model Architecture](../reference/model_architecture_complete.md) - Complete architecture documentation
- [User Guide](../user/user_guide.md) - User guide and tutorials
- [Developer Guide](../developer/ARCHITECTURE.md) - Developer architecture guide

## Support

- **GitHub Issues**: [https://github.com/impressioncore/impressioncore/issues](https://github.com/impressioncore/impressioncore/issues)
- **API Support**: [api-support@impressioncore.ai](mailto:api-support@impressioncore.ai)
- **Documentation**: [https://impressioncore.github.io/docs](https://impressioncore.github.io/docs)
- **Community**: [https://discord.gg/impressioncore](https://discord.gg/impressioncore)

---

**Last Updated**: 2025-06-03  
**Version**: 2.0.0  
**Authors**: Kirk LaSalle, GitHub Copilot  
**Status**: Active
