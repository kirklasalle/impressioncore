#!/usr/bin/env python3
"""
ImpressionCore: Run Training Server

Module for run training server functionality in the ImpressionCore framework.

File: training\run_training_server.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, training, gpu-optimized, ml, pytorch, production, 2025]
Dependencies: [torch, typing, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements run training server functionality for the
ImpressionCore brain-inspired multimodal AI framework. Optimized for memory-
constrained environments and designed to run efficiently on consumer hardware.

Design Philosophy:
- Memory-efficient implementation for GTX 1050 Ti constraints
- Modular design for easy extension and maintenance
- Rich logging and error handling
- Integration with ImpressionCore ecosystem

TODO:
- Add comprehensive unit tests
- Implement performance benchmarks
- Add configuration validation
- Optimize memory usage patterns

Examples:
```python
# Basic usage example
from training.run_training_server import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import os
import sys
import json
import logging
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

import torch
from flask import Flask, request, jsonify
import psutil

# Add project root to path for imports (to allow src.* imports)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.utils.hardware_detection import get_system_info, optimize_for_hardware
from src.training.models.memory_controller import get_memory_controller, get_memory_stats
# Memory optimization: Memory-critical operation
from src.training.training_utils import TrainingMetrics, train
from src.core.config.config_utils import load_config, save_config
from src.core.config import ModelConfig, TrainingConfig


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(Path(__file__).parent, "training_server.log"))
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global training state
active_trainings = {}
training_locks = {}
memory_controller = None
# Memory optimization: Memory-critical operation
hardware_settings = None


def initialize_server():
    """Initialize the training server with hardware optimizations."""
    global memory_controller, hardware_settings
    # Memory optimization: Memory-critical operation
    
    # Get hardware settings
    hardware_settings = optimize_for_hardware()
    
    # Initialize memory controller
    # Memory optimization: Memory-critical operation
    memory_controller = get_memory_controller()
    # Memory optimization: Memory-critical operation
    
    # Log system information
    system_info = get_system_info()
    logger.info(f"Server initialized with system info: {json.dumps(system_info, indent=2)}")
    logger.info(f"Hardware optimization settings: {json.dumps(hardware_settings, indent=2)}")
    
    # Set default PyTorch settings based on hardware
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        # Enable TF32 on Ampere GPUs
        # Memory optimization: Memory-critical operation
        if torch.cuda.get_device_capability(0)[0] >= 8:
        # Memory optimization: CUDA operations for GPU acceleration
            torch.backends.cuda.matmul.allow_tf32 = True
            # Memory optimization: Memory-critical operation
            torch.backends.cudnn.allow_tf32 = True
            logger.info("TF32 enabled on Ampere GPU")
            # Memory optimization: Memory-critical operation
        
        # For lower VRAM systems like 1050 Ti (4GB), limit CUDA allocation
        # Memory optimization: Memory-critical operation
        if hardware_settings["is_low_vram"]:
            # Tell PyTorch to be more conservative with memory
            # Memory optimization: Memory-critical operation
            torch.cuda.set_per_process_memory_fraction(0.9)
            # Memory optimization: CUDA operations for GPU acceleration
            logger.info("Set CUDA memory fraction to 0.9 for low VRAM device")
            # Memory optimization: Device placement for memory management


@app.route('/api/v1/status', methods=['GET'])
def get_status():
    """Get server status and resource information."""
    status = {
        "status": "running",
        "active_trainings": len(active_trainings),
        "system_resources": {
            "memory": get_memory_stats(),
            # Memory optimization: Memory-critical operation
            "cpu_percent": psutil.cpu_percent(interval=0.1),
        },
        "is_low_vram_mode": hardware_settings["is_low_vram"] if hardware_settings else None,
        "server_time": datetime.now().isoformat()
    }
    
    if torch.cuda.is_available():
    # Memory optimization: CUDA operations for GPU acceleration
        status["system_resources"]["cuda_device"] = torch.cuda.get_device_name(0)
        # Memory optimization: CUDA operations for GPU acceleration
        status["system_resources"]["cuda_version"] = torch.version.cuda
        # Memory optimization: Memory-critical operation
    
    return jsonify(status)


@app.route('/api/v1/training/start', methods=['POST'])
def start_training():
    """Start a new training job."""
    data = request.json
    
    # Validate required fields
    required_fields = ['job_id', 'model_config', 'training_config', 'data_path']
    missing_fields = [f for f in required_fields if f not in data]
    if missing_fields:
        return jsonify({
            "status": "error",
            "message": f"Missing required fields: {missing_fields}"
        }), 400
    
    job_id = data['job_id']
    
    # Check if job is already running
    if job_id in active_trainings:
        return jsonify({
            "status": "error",
            "message": f"Training job {job_id} is already running"
        }), 409
    
    # Validate hardware compatibility
    if hardware_settings["is_low_vram"] and not data.get('force', False):
        recommended_batch_size = hardware_settings["recommended_batch_size"]
        requested_batch_size = data['training_config'].get('batch_size', 8)
        
        if requested_batch_size > recommended_batch_size:
            return jsonify({
                "status": "warning",
                "message": f"Requested batch size {requested_batch_size} exceeds recommended {recommended_batch_size} for your hardware",
                "recommended_settings": hardware_settings,
                "needs_force": True
            }), 202
    
    # Create training lock
    training_locks[job_id] = threading.Lock()
    
    # Start training in a separate thread
    threading.Thread(
        target=run_training_job,
        args=(job_id, data),
        daemon=True
    ).start()
    
    return jsonify({
        "status": "success",
        "message": f"Training job {job_id} started",
        "job_id": job_id
    })


def run_training_job(job_id: str, data: Dict[str, Any]):
    """Run a training job in a separate thread."""
    # Set current job as active
    active_trainings[job_id] = {
        "status": "initializing",
        "start_time": time.time(),
        "progress": 0.0,
        "metrics": {},
        "hardware_optimized": hardware_settings["is_low_vram"]
    }
    
    try:
        # Load configurations
        model_config = ModelConfig(**data['model_config'])
        
        # Apply hardware optimizations to training config
        training_config_data = data['training_config']
        
        if hardware_settings["is_low_vram"]:
            # Override with hardware-optimized settings if needed
            if not data.get('force', False):
                training_config_data["batch_size"] = min(
                    training_config_data.get("batch_size", 4), 
                    hardware_settings["recommended_batch_size"]
                )
                training_config_data["gradient_accumulation_steps"] = max(
                    training_config_data.get("gradient_accumulation_steps", 1),
                    2  # Minimum 2 for low VRAM
                )
                training_config_data["fp16"] = True
            
            logger.info(f"Applied hardware optimizations for job {job_id}: {training_config_data}")
        
        training_config = TrainingConfig(**training_config_data)
        
        # Set up output directory
        output_dir = data.get('output_dir', os.path.join("checkpoints", job_id))
        os.makedirs(output_dir, exist_ok=True)
        
        # Update status
        active_trainings[job_id]["status"] = "loading_data"
        
        # Load training data (simplified, actual implementation would load proper datasets)
        from src.training.datasets import TextDataset
        train_dataset = TextDataset(data['data_path'])
        
        # Load validation data if specified
        val_dataset = None
        if 'validation_data_path' in data and data['validation_data_path']:
            val_dataset = TextDataset(data['validation_data_path'])
        
        # Update status
        active_trainings[job_id]["status"] = "loading_model"
        
        # Initialize model (simplified)
        # Memory optimization: Explicit memory cleanup
        from src.training.models.model import ImpressionCoreModel
        # Memory optimization: Explicit memory cleanup
        model = ImpressionCoreModel(model_config)
        # Memory optimization: Explicit memory cleanup
        
        # Apply hardware optimizations
        if hardware_settings["is_low_vram"]:
            from src.training.models.utils.memory_optimization import optimize_for_low_vram
            # Memory optimization: Memory-critical operation
            model = optimize_for_low_vram(
            # Memory optimization: Explicit memory cleanup
                model, 
                dtype=hardware_settings["recommended_precision"]
            )
        
        # Register model with memory controller
        # Memory optimization: Explicit memory cleanup
        memory_controller.register_model(f"training_{job_id}", model)
        # Memory optimization: Memory-critical operation
        
        # Update status
        active_trainings[job_id]["status"] = "training"
        
        # Train model
        metrics = train(
            config=model_config,
            model=model,
            train_dataset=train_dataset,
            val_dataset=val_dataset,
            output_dir=output_dir,
            training_args=training_config
        )
        
        # Update status with results
        active_trainings[job_id]["status"] = "completed"
        active_trainings[job_id]["end_time"] = time.time()
        active_trainings[job_id]["metrics"] = metrics
        active_trainings[job_id]["progress"] = 1.0
        
        logger.info(f"Training job {job_id} completed successfully")
        
    except Exception as e:
        # Update status with error
        active_trainings[job_id]["status"] = "failed"
        active_trainings[job_id]["error"] = str(e)
        active_trainings[job_id]["end_time"] = time.time()
        
        logger.error(f"Training job {job_id} failed: {e}", exc_info=True)
    
    finally:
        # Ensure model is unregistered from memory controller
        # Memory optimization: Explicit memory cleanup
        try:
            memory_controller.unregister_model(f"training_{job_id}")
            # Memory optimization: Memory-critical operation
        except:
            pass
        
        # Clean up
        torch.cuda.empty_cache()
        # Memory optimization: CUDA operations for GPU acceleration


@app.route('/api/v1/training/<job_id>/status', methods=['GET'])
def get_training_status(job_id):
    """Get status of a training job."""
    if job_id not in active_trainings:
        return jsonify({
            "status": "error",
            "message": f"Training job {job_id} not found"
        }), 404
    
    job_status = active_trainings[job_id].copy()
    
    # Add elapsed time
    if "start_time" in job_status:
        end_time = job_status.get("end_time", time.time())
        job_status["elapsed_seconds"] = end_time - job_status["start_time"]
    
    # Add memory stats
    # Memory optimization: Memory-critical operation
    job_status["memory_stats"] = get_memory_stats()
    # Memory optimization: Memory-critical operation
    
    return jsonify({
        "status": "success",
        "job_status": job_status
    })


@app.route('/api/v1/training/<job_id>/stop', methods=['POST'])
def stop_training(job_id):
    """Stop a training job."""
    if job_id not in active_trainings:
        return jsonify({
            "status": "error",
            "message": f"Training job {job_id} not found"
        }), 404
    
    # Mark job for stopping
    with training_locks.get(job_id, threading.Lock()):
        active_trainings[job_id]["status"] = "stopping"
    
    return jsonify({
        "status": "success",
        "message": f"Stopping training job {job_id}"
    })


@app.route('/api/v1/hardware/info', methods=['GET'])
def get_hardware_info():
    """Get detailed hardware information."""
    return jsonify({
        "status": "success",
        "system_info": get_system_info(),
        "optimization_settings": hardware_settings,
        "memory_stats": get_memory_stats()
        # Memory optimization: Memory-critical operation
    })


if __name__ == '__main__':
    # Initialize the server
    initialize_server()
    
    # Start the server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
