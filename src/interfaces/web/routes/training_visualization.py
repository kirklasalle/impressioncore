#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #api #attention_mechanism #cuda #gpu_optimization #memory_management #multimodal #python #source_code #src/interfaces/web/routes/training_visualization.py #testing #training #transformer #web_interface
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** Kirk LaSalle
# Tags:** #api #attention_mechanism #cuda #gpu_optimization #memory_management #multimodal #python #source_code #src\\interfaces\\web\\routes\\training_visualization.py #testing #training #transformer #web_interface
# Category:** Interface Definitions
# Status:** Active

"""
ImpressionCore - Brain-Inspired Multimodal AI Framework

File: src/web/routes/training_visualization.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-25
Modified: 2025-05-25
Version: 1.0.0

Authors:
- Kirk LaSalle & GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [web, routes]
Dependencies: [] # TODO: Auto-detect or allow manual input
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
# TODO: Add a brief description of this file's purpose.

Design Philosophy:
# TODO: Add design philosophy if applicable.

Memory Considerations:
# TODO: Document any specific memory considerations for this file.

Examples:
# TODO: Provide usage examples if applicable.

Notes:
# TODO: Add any relevant notes.
"""
"""
Training visualization routes for ImpressionCore
Provides real-time training metrics, model visualization, and checkpoint management
"""

import glob
import json
import logging
import math
import os
import threading
import time

import psutil
import torch
from flask import Blueprint, jsonify, render_template, request
from flask_sock import Sock

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
training_viz = Blueprint('training_viz', __name__)

# WebSocket for real-time updates
sock = Sock()

# Training control flags
training_viz.is_training = False
training_viz.is_paused = False
training_viz.current_trainer = None
training_viz.training_thread = None

@training_viz.route('/training/dashboard')
def dashboard():
    """Render the main training dashboard"""
    return render_template('training/dashboard.html')

@training_viz.route('/training/checkpoints')
def checkpoints():
    """Render the checkpoint management interface"""
    return render_template('training/checkpoints.html')

@training_viz.route('/training/architecture')
def architecture():
    """Render the model architecture visualization"""
    return render_template('training/architecture.html')

@sock.route('/training/metrics')
def metrics_socket(ws):
    """WebSocket endpoint for real-time training metrics"""
    try:
        while True:
            # Get latest metrics
            metrics = current_metrics()

            # Send metrics update
            ws.send(json.dumps(metrics))

            # Update every second
            time.sleep(1)
    except Exception as e:
        logger.error(f"WebSocket error: {e!s}")

def current_metrics():
    """Get current training and system metrics"""
    metrics = {
        'system': {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'gpu_memory_used': torch.cuda.memory_allocated() // 1024**2 if torch.cuda.is_available() else 0,
            'gpu_memory_total': torch.cuda.get_device_properties(0).total_memory // 1024**2 if torch.cuda.is_available() else 0,
        }
    }

    # Add training metrics if available
    if hasattr(training_viz, 'current_trainer') and training_viz.current_trainer:
        trainer_metrics = training_viz.current_trainer.metrics
        metrics['training'] = {
            'loss': trainer_metrics.get('train_loss', [])[-100:],  # Last 100 values
            'val_loss': trainer_metrics.get('val_loss', []),
            'learning_rate': trainer_metrics.get('learning_rate', [])[-100:],  # Last 100 values
            'tokens_per_second': trainer_metrics.get('tokens_per_second', 0),
            'elapsed_time': trainer_metrics.get('elapsed_time', 0),
            'is_training': training_viz.is_training,
            'is_paused': training_viz.is_paused
        }
    else:
        metrics['training'] = {
            'is_training': False,
            'is_paused': False
        }

    return metrics

@training_viz.route('/training/api/architecture')
def get_architecture():
    """API endpoint for model architecture data"""
    try:
        # This would normally load from the actual model
        # For now, we'll return a mock architecture
        arch_data = generate_mock_architecture()
        return jsonify(arch_data)
    except Exception as e:
        logger.error(f"Error getting architecture: {e!s}")
        return jsonify({'error': str(e)}), 500

@training_viz.route('/training/api/checkpoints')
def get_checkpoints():
    """API endpoint for checkpoint list"""
    try:
        # Use proper path within src directory
        default_checkpoints_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'training', 'checkpoints')
        checkpoints_dir = os.environ.get('IMPRESSIONCORE_CHECKPOINTS_DIR', default_checkpoints_dir)
        checkpoints = []

        for checkpoint_path in glob.glob(f"{checkpoints_dir}/*.pt"):
            # This would normally load actual checkpoint metadata
            # For now, use mock data based on the filename
            filename = os.path.basename(checkpoint_path)
            global_step = extract_step_from_filename(filename)

            checkpoint_data = {
                'name': filename,
                'path': checkpoint_path,
                'global_step': global_step,
                'metrics': generate_mock_metrics(global_step)
            }

            checkpoints.append(checkpoint_data)

        return jsonify(checkpoints)
    except Exception as e:
        logger.error(f"Error getting checkpoints: {e!s}")
        return jsonify({'error': str(e)}), 500

@training_viz.route('/training/api/checkpoints/load', methods=['POST'])
def load_checkpoint():
    """API endpoint for loading a checkpoint"""
    try:
        data = request.get_json()
        checkpoint_path = data.get('path')

        if not checkpoint_path or not os.path.exists(checkpoint_path):
            return jsonify({'error': 'Invalid checkpoint path'}), 400

        # This would normally load the checkpoint into the model
        logger.info(f"Loading checkpoint: {checkpoint_path}")

        # Simulate loading delay
        time.sleep(1)

        return jsonify({'success': True, 'message': 'Checkpoint loaded'})
    except Exception as e:
        logger.error(f"Error loading checkpoint: {e!s}")
        return jsonify({'error': str(e)}), 500

@training_viz.route('/training/api/checkpoints/delete', methods=['POST'])
def delete_checkpoint():
    """API endpoint for deleting a checkpoint"""
    try:
        data = request.get_json()
        checkpoint_path = data.get('path')

        if not checkpoint_path or not os.path.exists(checkpoint_path):
            return jsonify({'error': 'Invalid checkpoint path'}), 400

        # Delete the checkpoint file
        os.remove(checkpoint_path)
        logger.info(f"Deleted checkpoint: {checkpoint_path}")

        return jsonify({'success': True, 'message': 'Checkpoint deleted'})
    except Exception as e:
        logger.error(f"Error deleting checkpoint: {e!s}")
        return jsonify({'error': str(e)}), 500

# New API endpoints for training control

@training_viz.route('/training/api/control/pause', methods=['POST'])
def pause_training():
    """API endpoint for pausing training"""
    try:
        if not training_viz.is_training:
            return jsonify({'error': 'No training session is running'}), 400

        if training_viz.is_paused:
            return jsonify({'error': 'Training is already paused'}), 400

        if training_viz.current_trainer:
            # Set pause flag on trainer
            training_viz.current_trainer.pause()
            training_viz.is_paused = True
            logger.info("Training paused")
            return jsonify({'success': True, 'message': 'Training paused'})
        else:
            return jsonify({'error': 'No active trainer found'}), 500
    except Exception as e:
        logger.error(f"Error pausing training: {e!s}")
        return jsonify({'error': str(e)}), 500

@training_viz.route('/training/api/control/resume', methods=['POST'])
def resume_training():
    """API endpoint for resuming training"""
    try:
        if not training_viz.is_training:
            return jsonify({'error': 'No training session is running'}), 400

        if not training_viz.is_paused:
            return jsonify({'error': 'Training is not paused'}), 400

        if training_viz.current_trainer:
            # Resume training
            training_viz.current_trainer.resume()
            training_viz.is_paused = False
            logger.info("Training resumed")
            return jsonify({'success': True, 'message': 'Training resumed'})
        else:
            return jsonify({'error': 'No active trainer found'}), 500
    except Exception as e:
        logger.error(f"Error resuming training: {e!s}")
        return jsonify({'error': str(e)}), 500

@training_viz.route('/training/api/control/stop', methods=['POST'])
def stop_training():
    """API endpoint for stopping training"""
    try:
        if not training_viz.is_training:
            return jsonify({'error': 'No training session is running'}), 400

        if training_viz.current_trainer:
            # Stop training
            training_viz.current_trainer.stop()
            training_viz.is_training = False
            training_viz.is_paused = False
            logger.info("Training stopped")

            # Wait for training thread to complete
            if training_viz.training_thread and training_viz.training_thread.is_alive():
                training_viz.training_thread.join(timeout=5)

            return jsonify({'success': True, 'message': 'Training stopped'})
        else:
            return jsonify({'error': 'No active trainer found'}), 500
    except Exception as e:
        logger.error(f"Error stopping training: {e!s}")
        return jsonify({'error': str(e)}), 500

@training_viz.route('/training/api/control/save_checkpoint', methods=['POST'])
def save_checkpoint():
    """API endpoint for manually saving checkpoints"""
    try:
        if not training_viz.is_training:
            return jsonify({'error': 'No training session is running'}), 400

        if training_viz.current_trainer:
            # Get checkpoint directory - use proper path within src directory
            default_checkpoints_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'training', 'checkpoints')
            checkpoints_dir = os.environ.get('IMPRESSIONCORE_CHECKPOINTS_DIR', default_checkpoints_dir)
            os.makedirs(checkpoints_dir, exist_ok=True)

            # Generate checkpoint name with current timestamp
            timestamp = int(time.time())
            step = training_viz.current_trainer.global_step
            checkpoint_name = f"manual_checkpoint_{step}_{timestamp}.pt"
            checkpoint_path = os.path.join(checkpoints_dir, checkpoint_name)

            # Save checkpoint
            training_viz.current_trainer.save_checkpoint(checkpoint_path)
            logger.info(f"Manual checkpoint saved: {checkpoint_path}")

            return jsonify({
                'success': True,
                'message': 'Checkpoint saved successfully',
                'checkpoint': {
                    'name': checkpoint_name,
                    'path': checkpoint_path,
                    'global_step': step
                }
            })
        else:
            return jsonify({'error': 'No active trainer found'}), 500
    except Exception as e:
        logger.error(f"Error saving checkpoint: {e!s}")
        return jsonify({'error': str(e)}), 500

@training_viz.route('/training/api/control/status', methods=['GET'])
def training_status():
    """API endpoint for getting current training status"""
    status = {
        'is_training': training_viz.is_training,
        'is_paused': training_viz.is_paused
    }

    if training_viz.current_trainer:
        status.update({
            'global_step': training_viz.current_trainer.global_step,
            'tokens_processed': training_viz.current_trainer.tokens_processed,
            'elapsed_time': training_viz.current_trainer.elapsed_time,
            'current_epoch': training_viz.current_trainer.current_epoch
        })

    return jsonify(status)

@training_viz.route('/training/api/control/start', methods=['POST'])
def start_training():
    """API endpoint for starting a new training run"""
    try:
        if training_viz.is_training:
            return jsonify({'error': 'Training is already in progress'}), 400

        # Get training configuration from request
        config = request.get_json() or {}

        # Import trainer here to avoid circular imports
        from src.training.trainer import ModelTrainer

        # Create trainer instance
        trainer = ModelTrainer(
            model_config=config.get('model_config', {}),
            training_config=config.get('training_config', {})
        )

        # Store trainer instance
        training_viz.current_trainer = trainer
        training_viz.is_training = True
        training_viz.is_paused = False

        # Start training in a separate thread
        def training_worker():
            try:
                trainer.train()
            except Exception as e:
                logger.error(f"Training error: {e!s}")
            finally:
                training_viz.is_training = False
                training_viz.is_paused = False

        training_viz.training_thread = threading.Thread(target=training_worker)
        training_viz.training_thread.daemon = True
        training_viz.training_thread.start()

        logger.info("Training started")
        return jsonify({'success': True, 'message': 'Training started successfully'})

    except Exception as e:
        logger.error(f"Error starting training: {e!s}")
        return jsonify({'error': str(e)}), 500

def extract_step_from_filename(filename):
    """Extract step number from checkpoint filename"""
    try:
        # Assume format like "checkpoint-1000.pt" or "checkpoint_1000.pt"
        parts = filename.split('.')[0].split('-')
        if len(parts) == 1:
            parts = parts[0].split('_')

        if len(parts) > 1:
            return int(parts[-1])
        return 0
    except Exception:
        return 0

def generate_mock_architecture():
    """Generate mock architecture data for visualization"""
    # Create a simplified transformer architecture
    layers = [
        {'id': 'input', 'name': 'Input', 'type': 'Embedding', 'parameters': 38_400_000, 'shape': [50257, 768]},
        {'id': 'pos_embed', 'name': 'Position Embedding', 'type': 'Embedding', 'parameters': 786_432, 'shape': [1024, 768]},
    ]

    # Add transformer layers
    for i in range(12):
        layers.append({'id': f'attn_{i}', 'name': f'Self-Attention {i}', 'type': 'MultiHeadAttention', 'parameters': 2_359_296, 'shape': [768, 768]})
        layers.append({'id': f'ff_{i}', 'name': f'FeedForward {i}', 'type': 'MLP', 'parameters': 4_718_592, 'shape': [768, 3072, 768]})
        layers.append({'id': f'ln1_{i}', 'name': f'LayerNorm 1-{i}', 'type': 'LayerNorm', 'parameters': 1_536, 'shape': [768]})
        layers.append({'id': f'ln2_{i}', 'name': f'LayerNorm 2-{i}', 'type': 'LayerNorm', 'parameters': 1_536, 'shape': [768]})

    # Output layer
    layers.append({'id': 'output', 'name': 'Output', 'type': 'Linear', 'parameters': 38_400_000, 'shape': [768, 50257]})

    # Create nodes and edges for visualization
    nodes = []
    edges = []

    for i, layer in enumerate(layers):
        nodes.append({
            'id': layer['id'],
            'name': layer['name'],
            'type': layer['type'],
        })

        # Connect layers sequentially
        if i > 0:
            edges.append({
                'source': layers[i-1]['id'],
                'target': layer['id']
            })

        # Add residual connections for transformer layers
        if layer['type'] == 'LayerNorm' and i >= 4 and 'ln2' in layer['id']:
            # Connect to previous attention layer
            attn_idx = i - 2
            if attn_idx >= 0 and attn_idx < len(layers):
                edges.append({
                    'source': layers[attn_idx]['id'],
                    'target': layer['id']
                })

    return {
        'layers': layers,
        'nodes': nodes,
        'edges': edges,
        'total_parameters': sum(layer['parameters'] for layer in layers)
    }

def generate_mock_metrics(step):
    """Generate mock training metrics based on step number"""
    # Create realistic-looking training curves
    base_loss = 4.5
    loss_improvement_rate = 0.0001

    train_loss = base_loss * (1 - loss_improvement_rate * step)
    val_loss = train_loss * 1.05  # Validation loss slightly higher

    # Learning rate with cosine decay
    max_steps = 100000
    min_lr = 1e-6
    max_lr = 5e-5

    normalized_step = min(step / max_steps, 1.0)
    cos_decay = 0.5 * (1 + math.cos(math.pi * normalized_step))
    learning_rate = min_lr + (max_lr - min_lr) * cos_decay

    return {
        'train_loss': train_loss,
        'val_loss': val_loss,
        'learning_rate': learning_rate
    }

def init_app(app):
    """Initialize the training visualization module"""
    # Register blueprint
    app.register_blueprint(training_viz)

    # Initialize WebSocket
    sock.init_app(app)

    # Create checkpoints directory if it doesn't exist - use proper path within src directory
    default_checkpoints_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'training', 'checkpoints')
    checkpoints_dir = os.environ.get('IMPRESSIONCORE_CHECKPOINTS_DIR', default_checkpoints_dir)
    os.makedirs(checkpoints_dir, exist_ok=True)

    logger.info("Training visualization module initialized")
