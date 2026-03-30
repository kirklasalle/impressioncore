# Development Guide

**Created:** May 24, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\api\development_guide.md #api #attention_mechanism #command_line #cuda #deployment #documentation #gpu_optimization #inference #memory_management #multimodal #testing #training #transformer #web_interface  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

# ImpressionCore API Development Guide

**Last updated:** 2025-05-31
**Responsible:** @GitHubCopilot

## Overview

This guide provides comprehensive information for developers integrating with or extending the ImpressionCore API. It covers authentication, best practices, error handling, rate limiting, and advanced features.

## Quick Start

### Installation and Setup

1. **Start the ImpressionCore Server**

```bash
cd /d/Projects/impressioncore
python run_server.py
```

2. **Verify API Access**

```bash
curl http://localhost:5000/api/v1/status
```

3. **Authenticate**

```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

### Basic Integration Examples

#### Python Integration

```python
import requests
import json

class ImpressionCoreAPI:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def login(self, username, password):
        """Authenticate with the API"""
        response = self.session.post(f"{self.base_url}/login", json={
            "username": username,
            "password": password
        })
        return response.json()
    
    def get_system_status(self):
        """Get system status"""
        response = self.session.get(f"{self.base_url}/api/v1/status")
        return response.json()
    
    def start_training(self, model_name, dataset_path, config):
        """Start a training job"""
        response = self.session.post(f"{self.base_url}/api/v1/training/start", json={
            "model_name": model_name,
            "dataset_path": dataset_path,
            "config": config
        })
        return response.json()
    
    def get_training_status(self, job_id):
        """Get training job status"""
        response = self.session.get(f"{self.base_url}/api/v1/training/{job_id}/status")
        return response.json()
    
    def get_memory_stats(self):
        """Get current memory usage"""
        response = self.session.get(f"{self.base_url}/api/v1/memory/stats")
        return response.json()

# Usage example
api = ImpressionCoreAPI()
api.login("admin", "admin")

# Check system status
status = api.get_system_status()
print(f"System status: {status['status']}")

# Start training
training_config = {
    "learning_rate": 0.001,
    "batch_size": 16,
    "num_epochs": 10,
    "gradient_accumulation_steps": 2
}

result = api.start_training("my_model", "/path/to/dataset", training_config)
job_id = result.get("job_id")

# Monitor training
import time
while True:
    status = api.get_training_status(job_id)
    print(f"Training progress: {status['progress']:.2f}%")
    if status['status'] in ['completed', 'failed']:
        break
    time.sleep(5)
```

#### JavaScript/Node.js Integration

```javascript
const axios = require('axios');

class ImpressionCoreAPI {
    constructor(baseURL = 'http://localhost:5000') {
        this.client = axios.create({
            baseURL,
            timeout: 30000,
            withCredentials: true
        });
    }

    async login(username, password) {
        const response = await this.client.post('/login', {
            username,
            password
        });
        return response.data;
    }

    async getSystemStatus() {
        const response = await this.client.get('/api/v1/status');
        return response.data;
    }

    async startTraining(modelName, datasetPath, config) {
        const response = await this.client.post('/api/v1/training/start', {
            model_name: modelName,
            dataset_path: datasetPath,
            config
        });
        return response.data;
    }

    async getTrainingStatus(jobId) {
        const response = await this.client.get(`/api/v1/training/${jobId}/status`);
        return response.data;
    }

    async processMultimodal(formData) {
        const response = await this.client.post('/api/v1/multimodal/process', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return response.data;
    }
}

// Usage example
(async () => {
    const api = new ImpressionCoreAPI();
    
    try {
        // Login
        await api.login('admin', 'admin');
        
        // Check system status
        const status = await api.getSystemStatus();
        console.log('System status:', status.status);
        
        // Start training
        const trainingConfig = {
            learning_rate: 0.001,
            batch_size: 16,
            num_epochs: 10
        };
        
        const result = await api.startTraining('my_model', '/path/to/dataset', trainingConfig);
        console.log('Training started:', result.job_id);
        
    } catch (error) {
        console.error('API Error:', error.response?.data || error.message);
    }
})();
```

## Authentication

### Session-Based Authentication

The API uses session cookies for web-based authentication:

```python
# Login creates a session cookie
response = requests.post('/login', json={
    'username': 'admin',
    'password': 'admin'
})

# Subsequent requests use the session
session = requests.Session()
session.post('/login', json={'username': 'admin', 'password': 'admin'})
response = session.get('/api/v1/status')  # Authenticated
```

### API Key Authentication

For programmatic access, use API keys:

```python
# Generate an API key (requires session auth first)
session.post('/login', json={'username': 'admin', 'password': 'admin'})
key_response = session.post('/api/v1/user/api-key')
api_key = key_response.json()['key']

# Use API key for requests
headers = {'Authorization': f'Bearer {api_key}'}
response = requests.get('/api/v1/status', headers=headers)
```

## Error Handling

### Standard Error Response Format

```json
{
  "success": false,
  "error": "Detailed error message",
  "code": "ERROR_CODE",
  "details": {
    "field_errors": {},
    "validation_errors": [],
    "stack_trace": "..."
  }
}
```

### Error Handling Best Practices

```python
def handle_api_response(response):
    """Handle API response with proper error checking"""
    try:
        data = response.json()
        if not data.get('success', False):
            error_code = data.get('code', 'UNKNOWN_ERROR')
            error_message = data.get('error', 'Unknown error occurred')
            raise APIError(error_code, error_message, data.get('details', {}))
        return data['data']
    except requests.JSONDecodeError:
        raise APIError('INVALID_RESPONSE', 'Invalid JSON response')

class APIError(Exception):
    def __init__(self, code, message, details=None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"{code}: {message}")

# Usage
try:
    response = api.session.get('/api/v1/model/info')
    data = handle_api_response(response)
except APIError as e:
    if e.code == 'MODEL_NOT_LOADED':
        print("Model needs to be loaded first")
    elif e.code == 'GPU_ERROR':
        print("GPU unavailable, switch to CPU mode")
    else:
        print(f"Unexpected error: {e}")
```

## Rate Limiting

### Rate Limits

- **Anonymous requests**: 100 requests per hour
- **Authenticated users**: 1000 requests per hour
- **Training operations**: 10 concurrent jobs
- **WebSocket connections**: 50 concurrent connections

### Handling Rate Limits

```python
import time
from functools import wraps

def retry_on_rate_limit(max_retries=3, backoff_factor=2):
    """Decorator to retry requests on rate limit"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    response = func(*args, **kwargs)
                    if response.status_code == 429:
                        # Rate limited
                        retry_after = int(response.headers.get('Retry-After', 60))
                        if attempt < max_retries - 1:
                            time.sleep(retry_after * (backoff_factor ** attempt))
                            continue
                    return response
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(backoff_factor ** attempt)
            return response
        return wrapper
    return decorator

@retry_on_rate_limit()
def make_api_request():
    return requests.get('/api/v1/status')
```

## WebSocket Integration

### Real-time Training Updates

```python
import websocket
import json
import threading

class TrainingMonitor:
    def __init__(self, job_id):
        self.job_id = job_id
        self.ws = None
        
    def on_message(self, ws, message):
        data = json.loads(message)
        if data['type'] == 'training_update':
            print(f"Progress: {data['progress']:.1f}%, Loss: {data['loss']:.4f}")
    
    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")
    
    def start_monitoring(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            f"ws://localhost:5000/ws/training",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        
        # Start WebSocket in separate thread
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()

# Usage
monitor = TrainingMonitor("job_123")
monitor.start_monitoring()
```

### JavaScript WebSocket Integration

```javascript
class TrainingWebSocket {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    connect() {
        this.ws = new WebSocket('ws://localhost:5000/ws/training');
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectAttempts = 0;
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.reconnect();
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'training_update':
                this.updateProgress(data.progress, data.loss);
                break;
            case 'training_complete':
                this.onTrainingComplete(data);
                break;
            case 'error':
                this.onError(data.error);
                break;
        }
    }
    
    reconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => {
                console.log(`Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                this.connect();
            }, 1000 * this.reconnectAttempts);
        }
    }
    
    updateProgress(progress, loss) {
        // Update UI with training progress
        document.getElementById('progress').value = progress;
        document.getElementById('loss').textContent = loss.toFixed(4);
    }
}

// Usage
const trainingWS = new TrainingWebSocket();
trainingWS.connect();
```

## Advanced Features

### Memory Optimization

```python
def optimize_for_limited_vram():
    """Configure training for 4GB VRAM (GTX 1050 Ti)"""
    
    # Enable memory optimizations
    memory_config = {
        "strategy": "aggressive",
        "target_utilization": 0.85,
        "enable_offloading": True,
        "quantization_level": "int8"
    }
    
    response = api.session.post('/api/v1/memory/optimize', json=memory_config)
    
    # Configure training for low VRAM
    training_config = {
        "batch_size": 1,
        "gradient_accumulation_steps": 16,
        "mixed_precision": True,
        "gradient_checkpointing": True,
        "dataloader_num_workers": 2
    }
    
    return training_config
```

### Multimodal Processing

```python
def process_multimodal_content(text, image_path, audio_path):
    """Process multimodal content through the API"""
    
    files = {
        'text': (None, text),
        'image': (os.path.basename(image_path), open(image_path, 'rb'), 'image/jpeg'),
        'audio': (os.path.basename(audio_path), open(audio_path, 'rb'), 'audio/wav'),
        'processing_mode': (None, 'fusion')
    }
    
    response = api.session.post('/api/v1/multimodal/process', files=files)
    
    # Close file handles
    files['image'][1].close()
    files['audio'][1].close()
    
    return response.json()
```

### Brain Simulation Integration

```python
def use_brain_simulation(prompt):
    """Use brain simulation for enhanced reasoning"""
    
    # Initialize brain simulation
    config = {
        "memory_size": 10000,
        "cognitive_modules": ["reasoning", "memory", "attention"]
    }
    api.session.post('/api/v1/brainsim/initialize', json={"config": config})
    
    # Augment prompt with brain simulation
    augment_response = api.session.post('/api/v1/brainsim/augment-prompt', json={
        "prompt": prompt,
        "enhancement_type": "reasoning"
    })
    
    enhanced_prompt = augment_response.json()['data']['enhanced_prompt']
    
    # Use cognitive reasoning
    reasoning_response = api.session.post('/api/v1/brainsim/cognitive/reasoning', json={
        "input": enhanced_prompt,
        "context": {"domain": "general"}
    })
    
    return reasoning_response.json()
```

## Performance Optimization

### Batch Processing

```python
def batch_process_texts(texts, batch_size=32):
    """Process multiple texts efficiently"""
    results = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        
        response = api.session.post('/api/v1/inference/batch', json={
            "inputs": batch,
            "batch_size": len(batch)
        })
        
        results.extend(response.json()['data']['outputs'])
    
    return results
```

### Async Processing

```python
import asyncio
import aiohttp

class AsyncImpressionCoreAPI:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    async def get_training_status(self, job_id):
        async with self.session.get(f"{self.base_url}/api/v1/training/{job_id}/status") as response:
            return await response.json()
    
    async def monitor_multiple_jobs(self, job_ids):
        tasks = [self.get_training_status(job_id) for job_id in job_ids]
        results = await asyncio.gather(*tasks)
        return dict(zip(job_ids, results))

# Usage
async def main():
    async with AsyncImpressionCoreAPI() as api:
        job_statuses = await api.monitor_multiple_jobs(['job1', 'job2', 'job3'])
        print(job_statuses)

asyncio.run(main())
```

## Testing

### Unit Testing

```python
import unittest
from unittest.mock import Mock, patch

class TestImpressionCoreAPI(unittest.TestCase):
    def setUp(self):
        self.api = ImpressionCoreAPI()
    
    @patch('requests.Session.post')
    def test_login_success(self, mock_post):
        mock_post.return_value.json.return_value = {"success": True}
        
        result = self.api.login("admin", "admin")
        self.assertTrue(result["success"])
        
        mock_post.assert_called_once_with(
            "http://localhost:5000/login",
            json={"username": "admin", "password": "admin"}
        )
    
    @patch('requests.Session.get')
    def test_get_system_status(self, mock_get):
        expected_response = {
            "success": True,
            "status": "healthy",
            "version": "1.0.0"
        }
        mock_get.return_value.json.return_value = expected_response
        
        result = self.api.get_system_status()
        self.assertEqual(result["status"], "healthy")

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing

```python
import pytest

class TestAPIIntegration:
    @pytest.fixture
    def api(self):
        api = ImpressionCoreAPI()
        # Login for authenticated tests
        api.login("admin", "admin")
        return api
    
    def test_full_training_workflow(self, api):
        # Create model
        model_config = {
            "model_name": "test_model",
            "architecture": "transformer",
            "config": {
                "vocab_size": 1000,
                "hidden_size": 256,
                "num_layers": 4
            }
        }
        
        model_result = api.session.post('/api/v1/model/create', json=model_config)
        assert model_result.json()["success"]
        
        # Start training
        training_config = {
            "learning_rate": 0.001,
            "batch_size": 8,
            "num_epochs": 1
        }
        
        training_result = api.start_training("test_model", "/path/to/test/data", training_config)
        assert "job_id" in training_result
        
        job_id = training_result["job_id"]
        
        # Monitor training
        status = api.get_training_status(job_id)
        assert status["status"] in ["running", "completed", "pending"]
```

## Deployment Considerations

### Production Configuration

```python
# Production API client with proper configuration
class ProductionImpressionCoreAPI(ImpressionCoreAPI):
    def __init__(self, base_url, api_key=None, timeout=30):
        super().__init__(base_url)
        self.api_key = api_key
        self.session.timeout = timeout
        
        # Add retry strategy
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set API key header if provided
        if self.api_key:
            self.session.headers.update({'Authorization': f'Bearer {self.api_key}'})
```

### Health Monitoring

```python
def health_check(api):
    """Comprehensive health check"""
    try:
        # Check basic connectivity
        status = api.get_system_status()
        if status['status'] != 'healthy':
            return False
        
        # Check GPU availability
        gpu_response = api.session.get('/api/check_gpu')
        gpu_available = gpu_response.json().get('gpu_available', False)
        
        # Check memory usage
        memory_stats = api.get_memory_stats()
        gpu_utilization = memory_stats['data']['gpu']['utilization']
        
        # Alert if GPU utilization is too high
        if gpu_utilization > 0.95:
            print("Warning: GPU utilization very high")
        
        return True
        
    except Exception as e:
        print(f"Health check failed: {e}")
        return False
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure the server is running: `python run_server.py`
   - Check firewall settings
   - Verify port 5000 is available

2. **Authentication Errors**
   - Check username/password
   - Ensure session cookies are enabled
   - Verify API key format

3. **Memory Errors**
   - Reduce batch size
   - Enable gradient checkpointing
   - Use CPU offloading

4. **GPU Errors**
   - Check CUDA installation
   - Verify GPU driver compatibility
   - Monitor GPU memory usage

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Log all HTTP requests
import http.client as http_client
http_client.HTTPConnection.debuglevel = 1
```

## Best Practices

1. **Always handle errors gracefully**
2. **Use appropriate timeout values**
3. **Implement retry logic for transient failures**
4. **Monitor memory usage when training large models**
5. **Use WebSockets for real-time updates**
6. **Batch requests when possible**
7. **Cache responses when appropriate**
8. **Validate input data before sending**
9. **Use async/await for concurrent operations**
10. **Implement proper logging and monitoring**

---

_This guide is continuously updated with new features and best practices. Last updated: 2025-05-24_
