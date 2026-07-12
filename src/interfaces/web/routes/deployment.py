#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #api #cuda #deployment #inference #memory_management #multimodal #performance #python #pytorch #source_code #src/interfaces/web\routes\\deployment.py #testing #web_interface
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** Kirk LaSalle
# Tags:** #api #cuda #deployment #inference #memory_management #multimodal #performance #python #pytorch #source_code #src\\interfaces\\web\\routes\\deployment.py #testing #web_interface
# Category:** Interface Definitions
# Status:** Active

"""
ImpressionCore: Deployment API Routes

Module for deployment API functionality in the ImpressionCore framework.

File: web/routes/deployment.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-30
Modified: 2025-05-30
Version: 1.0.0

Authors:
- GitHub Copilot
- Kirk LaSalle <kirk@impressioncore.ai>

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [deployment, api, routes, web, 2025]
Dependencies: [flask, torch]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements deployment API routes for the ImpressionCore framework.
Provides REST endpoints for model deployment, status monitoring, and management.

Design Philosophy:
- RESTful API design for deployment operations
- Comprehensive error handling and validation
- Memory-efficient deployment strategies
- Hardware compatibility checks
- Integration with DeploymentManager

API Endpoints:
- POST /api/v1/deployment/deploy - Deploy models with configuration
- GET /api/v1/deployment/status/{deployment_id} - Get deployment status
- GET /api/v1/deployment/list - List all deployments
- GET /api/v1/deployment/compatibility - Hardware compatibility checks
- POST /api/v1/deployment/benchmark - Performance benchmarking
- GET /api/v1/deployment/artifacts/{deployment_id} - Get deployment artifacts
- DELETE /api/v1/deployment/{deployment_id} - Delete deployments
"""

import uuid
from datetime import datetime
from typing import Any

import torch
import torch.nn as nn
from flask import Blueprint, jsonify, request

from src.core.utils.rich_logging import RichLogger

# ImpressionCore imports
from src.deployment.deployment_manager import (
    DeploymentConfig,
    DeploymentManager,
    DeploymentTarget,
    DeploymentType,
    create_deployment_config,
)

# Create blueprint
deployment_bp = Blueprint('deployment', __name__, url_prefix='/api/v1/deployment')

# Initialize logger
logger = RichLogger(__name__).logger

# Global deployment tracking
active_deployments: dict[str, dict[str, Any]] = {}
deployment_managers: dict[str, DeploymentManager] = {}


def validate_deployment_request(data: dict[str, Any]) -> tuple[bool, str]:
    """
    Validate deployment request data.

    Args:
        data: Request payload

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['model_name', 'deployment_type']

    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"

    # Validate deployment type
    valid_types = [t.value for t in DeploymentType]
    if data['deployment_type'] not in valid_types:
        return False, f"Invalid deployment_type. Must be one of: {valid_types}"

    # Validate target platform if provided
    if 'target_platform' in data:
        valid_targets = [t.value for t in DeploymentTarget]
        if data['target_platform'] not in valid_targets:
            return False, f"Invalid target_platform. Must be one of: {valid_targets}"

    return True, ""


def get_model_from_name(model_name: str) -> nn.Module | None:
    """
    Load a model by name.

    Args:
        model_name: Name of the model to load

    Returns:
        PyTorch model or None if not found
    """
    try:
        # This is a placeholder - in production, you'd have a model registry
        # For now, we'll create a simple dummy model for testing
        if model_name == "test_model":
            class TestModel(nn.Module):
                def __init__(self):
                    super().__init__()
                    self.linear = nn.Linear(512, 256)

                def forward(self, x):
                    return self.linear(x)

            return TestModel()

        # Add logic to load actual models from registry
        logger.warning(f"Model '{model_name}' not found in registry")
        return None

    except Exception as e:
        logger.error(f"Error loading model '{model_name}': {e}")
        return None


@deployment_bp.route('/deploy', methods=['POST'])
def deploy_model():
    """
    Deploy a model with specified configuration.

    Request Body:
    {
        "model_name": "string",
        "deployment_type": "onnx|tensorrt|mobile|distributed|hybrid",
        "target_platform": "desktop|server|mobile|edge|cloud|embedded",
        "config": {
            "batch_size": 1,
            "sequence_length": 2048,
            "precision": "fp16",
            "optimize_for_inference": true,
            "quantization_enabled": true,
            "memory_optimization": true,
            "max_memory_gb": 4.0
        }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Validate request
        is_valid, error_msg = validate_deployment_request(data)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        # Generate deployment ID
        deployment_id = str(uuid.uuid4())

        # Extract configuration
        model_name = data['model_name']
        deployment_type = DeploymentType(data['deployment_type'])
        target_platform = DeploymentTarget(data.get('target_platform', 'desktop'))

        # Create deployment config
        data.get('config', {})
        deployment_config = create_deployment_config(
            deployment_type=deployment_type,
            target_platform=target_platform,
            model_name=model_name,
            # config_data
        )

        # Load model
        model = get_model_from_name(model_name)
        if model is None:
            return jsonify({"error": f"Model '{model_name}' not found"}), 404

        # Initialize deployment manager
        deployment_manager = DeploymentManager(deployment_config)
        deployment_managers[deployment_id] = deployment_manager

        # Validate model compatibility
        if not deployment_manager.validate_model(model):
            return jsonify({"error": "Model validation failed"}), 400

        # Start deployment
        logger.info(f"Starting deployment {deployment_id} for model {model_name}")

        # Track deployment
        active_deployments[deployment_id] = {
            "id": deployment_id,
            "model_name": model_name,
            "deployment_type": deployment_type.value,
            "target_platform": target_platform.value,
            "status": "deploying",
            "created_at": datetime.now().isoformat(),
            "progress": 0
        }

        # Perform deployment (this could be async in production)
        try:
            result = deployment_manager.deploy(model, deployment_type)

            # Update deployment status
            active_deployments[deployment_id].update({
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "progress": 100,
                "result": result
            })

            return jsonify({
                "deployment_id": deployment_id,
                "status": "completed",
                "message": "Model deployed successfully",
                "result": result
            }), 201

        except Exception as deploy_error:
            active_deployments[deployment_id].update({
                "status": "failed",
                "error": str(deploy_error),
                "failed_at": datetime.now().isoformat()
            })
            raise deploy_error from deploy_error

    except Exception as e:
        logger.error(f"Deployment error: {e}")
        return jsonify({"error": f"Deployment failed: {e!s}"}), 500


@deployment_bp.route('/status/<deployment_id>', methods=['GET'])
def get_deployment_status(deployment_id: str):
    """
    Get the status of a specific deployment.

    Args:
        deployment_id: Unique deployment identifier
    """
    try:
        if deployment_id not in active_deployments:
            return jsonify({"error": "Deployment not found"}), 404

        deployment = active_deployments[deployment_id]

        # Add additional status information if deployment manager exists
        if deployment_id in deployment_managers:
            manager = deployment_managers[deployment_id]

            # Get performance metrics if available
            try:
                metrics = manager.get_performance_metrics()
                deployment["metrics"] = metrics
            except Exception as e:
                logger.warning(f"Could not retrieve metrics for {deployment_id}: {e}")

        return jsonify(deployment), 200

    except Exception as e:
        logger.error(f"Error getting deployment status: {e}")
        return jsonify({"error": f"Failed to get status: {e!s}"}), 500


@deployment_bp.route('/list', methods=['GET'])
def list_deployments():
    """
    List all deployments with optional filtering.

    Query Parameters:
    - status: Filter by deployment status
    - deployment_type: Filter by deployment type
    - model_name: Filter by model name
    """
    try:
        # Get query parameters
        status_filter = request.args.get('status')
        type_filter = request.args.get('deployment_type')
        model_filter = request.args.get('model_name')

        # Filter deployments
        filtered_deployments = []
        for deployment in active_deployments.values():
            # Apply filters
            if status_filter and deployment.get('status') != status_filter:
                continue
            if type_filter and deployment.get('deployment_type') != type_filter:
                continue
            if model_filter and deployment.get('model_name') != model_filter:
                continue

            filtered_deployments.append(deployment)

        return jsonify({
            "deployments": filtered_deployments,
            "total": len(filtered_deployments)
        }), 200

    except Exception as e:
        logger.error(f"Error listing deployments: {e}")
        return jsonify({"error": f"Failed to list deployments: {e!s}"}), 500


@deployment_bp.route('/compatibility', methods=['GET'])
def check_hardware_compatibility():
    """
    Check hardware compatibility for deployment types.

    Query Parameters:
    - deployment_type: Specific deployment type to check
    """
    try:
        deployment_type_param = request.args.get('deployment_type')

        # Create a temporary deployment config for compatibility check
        temp_config = DeploymentConfig()
        temp_manager = DeploymentManager(temp_config)

        # Get hardware compatibility analysis
        compatibility = temp_manager.analyze_hardware_compatibility()

        # Filter by deployment type if specified
        if deployment_type_param:
            if deployment_type_param in compatibility.get('supported_types', []):
                compatibility['requested_type_supported'] = True
            else:
                compatibility['requested_type_supported'] = False

        return jsonify(compatibility), 200

    except Exception as e:
        logger.error(f"Error checking compatibility: {e}")
        return jsonify({"error": f"Failed to check compatibility: {e!s}"}), 500


@deployment_bp.route('/benchmark', methods=['POST'])
def benchmark_deployment():
    """
    Run performance benchmarks for a deployment type.

    Request Body:
    {
        "model_name": "string",
        "deployment_type": "onnx|tensorrt|mobile|distributed",
        "config": {
            "batch_size": 1,
            "sequence_length": 2048,
            "iterations": 100
        }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        model_name = data.get('model_name')
        deployment_type_str = data.get('deployment_type')
        data.get('config', {})

        if not model_name or not deployment_type_str:
            return jsonify({"error": "model_name and deployment_type are required"}), 400

        # Validate deployment type
        try:
            deployment_type = DeploymentType(deployment_type_str)
        except ValueError:
            valid_types = [t.value for t in DeploymentType]
            return jsonify({"error": f"Invalid deployment_type. Must be one of: {valid_types}"}), 400

        # Load model
        model = get_model_from_name(model_name)
        if model is None:
            return jsonify({"error": f"Model '{model_name}' not found"}), 404

        # Create deployment config for benchmarking
        deployment_config = create_deployment_config(
            deployment_type=deployment_type,
            model_name=model_name,
            # config
        )

        # Initialize deployment manager
        deployment_manager = DeploymentManager(deployment_config)

        # Run benchmark
        logger.info(f"Running benchmark for {model_name} with {deployment_type.value}")
        benchmark_results = deployment_manager.benchmark_deployment(model, deployment_type)

        return jsonify({
            "model_name": model_name,
            "deployment_type": deployment_type.value,
            "benchmark_results": benchmark_results,
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Benchmark error: {e}")
        return jsonify({"error": f"Benchmark failed: {e!s}"}), 500


@deployment_bp.route('/artifacts/<deployment_id>', methods=['GET'])
def get_deployment_artifacts(deployment_id: str):
    """
    Get deployment artifacts and files.

    Args:
        deployment_id: Unique deployment identifier
    """
    try:
        if deployment_id not in active_deployments:
            return jsonify({"error": "Deployment not found"}), 404

        if deployment_id not in deployment_managers:
            return jsonify({"error": "Deployment manager not available"}), 404

        manager = deployment_managers[deployment_id]
        artifacts = manager.get_deployment_artifacts()

        return jsonify({
            "deployment_id": deployment_id,
            "artifacts": artifacts,
            "retrieved_at": datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error getting artifacts: {e}")
        return jsonify({"error": f"Failed to get artifacts: {e!s}"}), 500


@deployment_bp.route('/<deployment_id>', methods=['DELETE'])
def delete_deployment(deployment_id: str):
    """
    Delete a deployment and clean up resources.

    Args:
        deployment_id: Unique deployment identifier
    """
    try:
        if deployment_id not in active_deployments:
            return jsonify({"error": "Deployment not found"}), 404

        # Cleanup deployment manager
        if deployment_id in deployment_managers:
            manager = deployment_managers[deployment_id]
            try:
                manager.cleanup()
            except Exception as cleanup_error:
                logger.warning(f"Cleanup error for {deployment_id}: {cleanup_error}")

            del deployment_managers[deployment_id]

        # Remove from active deployments
        active_deployments[deployment_id]
        del active_deployments[deployment_id]

        logger.info(f"Deleted deployment {deployment_id}")

        return jsonify({
            "message": "Deployment deleted successfully",
            "deployment_id": deployment_id,
            "deleted_at": datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error deleting deployment: {e}")
        return jsonify({"error": f"Failed to delete deployment: {e!s}"}), 500


# Error handlers
@deployment_bp.errorhandler(400)
def bad_request(error):
    """Handle bad request errors."""
    return jsonify({"error": "Bad request", "message": str(error)}), 400


@deployment_bp.errorhandler(404)
def not_found(error):
    """Handle not found errors."""
    return jsonify({"error": "Resource not found", "message": str(error)}), 404


@deployment_bp.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error", "message": "An unexpected error occurred"}), 500


# Health check endpoint
@deployment_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for deployment service."""
    try:
        # Basic health checks
        torch_available = torch.cuda.is_available()

        return jsonify({
            "status": "healthy",
            "service": "deployment",
            "timestamp": datetime.now().isoformat(),
            "active_deployments": len(active_deployments),
            "torch_cuda_available": torch_available,
            "version": "1.0.0"
        }), 200

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503


# Initialize logging for the blueprint
logger.info("Deployment API routes initialized")
