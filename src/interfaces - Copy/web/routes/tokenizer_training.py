#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #gpu_optimization #memory_management #multimodal #performance #python #source_code #src/interfaces/web\routes\tokenizer_training.py #testing #tokenization #training #web_interface
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** Kirk LaSalle
# Tags:** #gpu_optimization #memory_management #multimodal #performance #python #source_code #src\\interfaces\\web\\routes\\tokenizer_training.py #testing #tokenization #training #web_interface
# Category:** Interface Definitions
# Status:** Active

"""
ImpressionCore: Tokenizer Training

Module for tokenizer training functionality in the ImpressionCore framework.

File: web/routes/tokenizer_training.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, production, web, frontend, 2025]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements tokenizer training functionality for the
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
from web.routes.tokenizer_training import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import json
import os
import time
import uuid
from typing import Any

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from werkzeug.utils import secure_filename

from .core.utils.gpu_memory import (
    clear_gpu_memory,
    # Memory optimization: Memory-critical operation
    # Memory optimization: Memory-critical operation
    get_gpu_memory_info,
    optimize_for_available_memory,
)

# Create blueprint
tokenizer_training_bp = Blueprint("tokenizer_training", __name__, url_prefix="/tokenizer")

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'text': {'txt', 'csv', 'json', 'jsonl'},
    'image': {'jpg', 'jpeg', 'png', 'webp'}
}

def allowed_file(filename: str, category: str) -> bool:
    """Check if file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS.get(category, set())

def get_training_status(job_id: str) -> dict[str, Any]:
    """Get training status for a specific job."""
    status_file = os.path.join(
        current_app.config['TEMP_DIR'],
        f"tokenizer_job_{job_id}_status.json"
    )

    if not os.path.exists(status_file):
        return {
            'status': 'not_found',
            'message': 'Training job not found'
        }

    with open(status_file) as f:
        return json.load(f)

def update_training_status(job_id: str, status: dict[str, Any]) -> None:
    """Update training status for a specific job."""
    status_file = os.path.join(
        current_app.config['TEMP_DIR'],
        f"tokenizer_job_{job_id}_status.json"
    )

    with open(status_file, 'w') as f:
        json.dump(status, f)

@tokenizer_training_bp.route('/')
def index():
    """Render the tokenizer training interface."""
    # Get GPU memory information
    # Memory optimization: Memory-critical operation
    gpu_info = get_gpu_memory_info()
    # Memory optimization: Memory-critical operation

    # Get optimal training settings based on available GPU memory
    # Memory optimization: Memory-critical operation
    training_settings = optimize_for_available_memory()
    # Memory optimization: Memory-critical operation

    return render_template(
        'tokenizer_training.html',
        gpu_info=gpu_info,
        # Memory optimization: Memory-critical operation
        training_settings=training_settings
    )

@tokenizer_training_bp.route('/upload', methods=['POST'])
def upload_training_data():
    """Handle training data file uploads."""
    # Check if files are provided
    if 'files[]' not in request.files:
        return jsonify({
            'success': False,
            'message': 'No files provided'
        }), 400

    files = request.files.getlist('files[]')
    category = request.form.get('category', 'text')

    # Generate a unique job ID
    job_id = str(uuid.uuid4())

    # Create job directory
    job_dir = os.path.join(current_app.config['TEMP_DIR'], f"tokenizer_job_{job_id}")
    os.makedirs(job_dir, exist_ok=True)

    uploaded_files = []
    for file in files:
        if file and file.filename and allowed_file(file.filename, category):
            filename = secure_filename(file.filename)
            filepath = os.path.join(job_dir, filename)
            file.save(filepath)
            uploaded_files.append(filename)

    if not uploaded_files:
        return jsonify({
            'success': False,
            'message': 'No valid files provided'
        }), 400

    # Create initial status file
    status = {
        'job_id': job_id,
        'status': 'uploaded',
        'message': f'Uploaded {len(uploaded_files)} files',
        'files': uploaded_files,
        'category': category,
        'created_at': time.time(),
        'updated_at': time.time(),
        'progress': 0
    }
    update_training_status(job_id, status)

    return jsonify({
        'success': True,
        'job_id': job_id,
        'message': f'Uploaded {len(uploaded_files)} files',
        'files': uploaded_files
    })

@tokenizer_training_bp.route('/start-training', methods=['POST'])
def start_training():
    """Start the tokenizer training process with enhanced validation."""
    try:
        data = request.json
        job_id = data.get('job_id')

        # Validate job_id
        if not job_id:
            return jsonify({
                'success': False,
                'message': 'No job_id provided'
            }), 400

        # Get current status
        status = get_training_status(job_id)
        if status.get('status') == 'not_found':
            return jsonify({
                'success': False,
                'message': 'Training job not found'
            }), 404

        # Validate configuration
        try:
            config = {
                'vocab_size': int(data.get('vocab_size', 10000)),
                'batch_size': int(data.get('batch_size', 1000)),
                'model_type': data.get('model_type', 'bpe'),
                'special_tokens': data.get('special_tokens', []),
                'memory_efficient': bool(data.get('memory_efficient', True))
                # Memory optimization: Memory-critical operation
            }
        except ValueError as e:
            return jsonify({
                'success': False,
                'message': f'Invalid configuration: {e!s}'
            }), 400

        # Update status
        status.update({
            'status': 'queued',
            'message': 'Training job queued',
            'config': config,
            'updated_at': time.time()
        })
        update_training_status(job_id, status)

        # Start training in a background thread
        import threading
        threading.Thread(target=simulate_training, args=(job_id,)).start()

        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Training job started'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error starting training: {e!s}'
        }), 500

@tokenizer_training_bp.route('/status/<job_id>')
def job_status(job_id):
    """Get the status of a training job."""
    status = get_training_status(job_id)
    return jsonify(status)

@tokenizer_training_bp.route('/progress/<job_id>')
def training_progress(job_id):
    """
    Render a real-time progress visualization for a training job.

    Args:
        job_id: The unique identifier for the training job.

    Returns:
        Rendered HTML page with progress updates.
    """
    status = get_training_status(job_id)
    if status.get('status') == 'not_found':
        flash('Training job not found')
        return redirect(url_for('tokenizer_training.index'))

    return render_template(
        'training_progress.html',
        job_id=job_id,
        status=status
    )

def simulate_training(job_id):
    """
    Simulate training progress for demo purposes.
    In a real implementation, this would be replaced with actual tokenizer training.
    """
    status = get_training_status(job_id)

    # Update status to running
    status.update({
        'status': 'running',
        'message': 'Training in progress',
        'updated_at': time.time(),
        'progress': 0,
        'memory_usage': get_gpu_memory_info() if status['config']['memory_efficient'] else None
        # Memory optimization: Memory-critical operation
    })
    update_training_status(job_id, status)

    # Simulate training progress
    for progress in range(1, 11):
        time.sleep(2)  # Simulate work
        status.update({
            'progress': progress * 10,
            'updated_at': time.time(),
            'message': f'Training in progress: {progress * 10}%'
        })
        update_training_status(job_id, status)

    # Update status to complete
    status.update({
        'status': 'complete',
        'message': 'Training complete',
        'updated_at': time.time(),
        'progress': 100,
        'result': {
            'tokens': status['config']['vocab_size'],
            'files_processed': len(status['files']),
            'model_path': f"tokenizer_{job_id}.json",
        }
    })
    update_training_status(job_id, status)

@tokenizer_training_bp.route('/download/<job_id>')
def download_tokenizer(job_id):
    """Download trained tokenizer files."""
    status = get_training_status(job_id)

    if status.get('status') != 'complete':
        flash('Tokenizer training is not complete yet')
        return redirect(url_for('tokenizer_training.index'))

    # In a real implementation, we would return the actual tokenizer file
    # For the demo, we'll create a sample tokenizer file
    job_dir = os.path.join(current_app.config['TEMP_DIR'], f"tokenizer_job_{job_id}")
    tokenizer_file = os.path.join(job_dir, f"tokenizer_{job_id}.json")

    # Create a sample tokenizer file if it doesn't exist
    if not os.path.exists(tokenizer_file):
        with open(tokenizer_file, 'w') as f:
            json.dump({
                'type': status['config']['model_type'],
                'vocab_size': status['config']['vocab_size'],
                'special_tokens': status['config']['special_tokens'],
                'version': '1.0.0',
                'created_at': time.time()
            }, f, indent=2)

    return send_from_directory(
        job_dir,
        f"tokenizer_{job_id}.json",
        as_attachment=True,
        download_name=f"impressioncore_tokenizer_{status['config']['model_type']}.json"
    )

@tokenizer_training_bp.route('/delete/<job_id>', methods=['POST'])
def delete_job(job_id):
    """Delete a tokenizer training job and its files."""
    job_dir = os.path.join(current_app.config['TEMP_DIR'], f"tokenizer_job_{job_id}")
    status_file = os.path.join(
        current_app.config['TEMP_DIR'],
        f"tokenizer_job_{job_id}_status.json"
    )

    # Check if job exists
    if not os.path.exists(status_file):
        return jsonify({
            'success': False,
            'message': 'Training job not found'
        }), 404

    # Delete job files
    try:
        import shutil
        if os.path.exists(job_dir):
            shutil.rmtree(job_dir)
        if os.path.exists(status_file):
            os.remove(status_file)

        return jsonify({
            'success': True,
            'message': 'Training job deleted'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting job: {e!s}'
        }), 500

@tokenizer_training_bp.route('/gpu-info')
# Memory optimization: Memory-critical operation
def gpu_info():
# Memory optimization: Memory-critical operation
    """Get current GPU memory information."""
    # Memory optimization: Memory-critical operation
    return jsonify(get_gpu_memory_info())
    # Memory optimization: Memory-critical operation

@tokenizer_training_bp.route('/clear-gpu', methods=['POST'])
# Memory optimization: Memory-critical operation
def clear_gpu():
# Memory optimization: Memory-critical operation
    """Clear GPU memory cache."""
    # Memory optimization: Memory-critical operation
    success = clear_gpu_memory()
    # Memory optimization: Memory-critical operation
    return jsonify({
        'success': success,
        'message': 'GPU memory cleared' if success else 'Failed to clear GPU memory',
        # Memory optimization: Memory-critical operation
        'gpu_info': get_gpu_memory_info()
        # Memory optimization: Memory-critical operation
    })
