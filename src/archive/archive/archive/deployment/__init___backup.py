
⚠️ ARCHIVED FILE
This file has been archived for historical, compatibility, or deprecation reasons. Do not modify or use in active development.

#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #api #deployment #inference #multimodal #python #source_code #src/deployment/__init___backup.py #testing #web_interface
**Category:** Deployment Tools
**Status:** Active
"""









# !/usr/bin/env python3

**Created:** 2024-10-15
**Updated:** 2025-07-26 10_27_01
**Author:** Kirk LaSalle
**Tags:** #api #deployment #inference #multimodal #python #source_code #src/deployment/__init___backup.py #testing #web_interface
**Category:** Deployment Tools
**Status:** Active

"""
ImpressionCore Deployment Infrastructure

File: src/deployment/__init__.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-01-06 (System Timestamp)
Status: PRODUCTION-READY ✅

Purpose: Export deployment infrastructure components for ImpressionCore-B1
         including production management, user testing, and launch coordination.

Authors:
- GitHub Copilot (Senior Production Lead)
- Kirk LaSalle (Project Owner)

License: MIT
Copyright (c) 2025 ImpressionCore Team

# Core deployment infrastructure
from .production_manager import ProductionDeploymentManager
from .user_testing_manager import (
    UserTestingManager,
    TestingPhase,
    FeedbackType,
    UserSession,
    UserFeedback
)
from .launch_production import ImpressionCoreProductionLauncher

# Legacy deployment optimization (preserved for compatibility)
try:
    from .onnx_export import ONNXExporter, ONNXExportConfig
    from .tensorrt_optimizer import TensorRTOptimizer, TensorRTConfig
    from .mobile_deployment import MobileDeployment, MobileConfig
    from .distributed_inference import DistributedInference, DistributedConfig
    from .deployment_manager import DeploymentManager, DeploymentConfig
    LEGACY_DEPLOYMENT_AVAILABLE = True
except ImportError:
    LEGACY_DEPLOYMENT_AVAILABLE = False

# Export all deployment components
__all__ = [
    # Production Management (NEW - Phase 8B)
    "ProductionDeploymentManager",

    # User Testing Infrastructure (NEW - Phase 8B)
    "UserTestingManager",
    "TestingPhase",
    "FeedbackType",
    "UserSession",
    "UserFeedback",

    # Production Launcher (NEW - Phase 8B)
    "ImpressionCoreProductionLauncher"
]

# Add legacy components if available
if LEGACY_DEPLOYMENT_AVAILABLE:
    __all__.extend([
        'ONNXExporter',
        'ONNXExportConfig',
        'TensorRTOptimizer',
        'TensorRTConfig',
        'MobileDeployment',
        'MobileConfig',
        'DistributedInference',
        'DistributedConfig',
        'DeploymentManager',
        'DeploymentConfig'
    ])

# Version information
__version__ = "1.0.0"
__status__ = "Production-Ready"

# Module metadata
DEPLOYMENT_MODULES = {
    "production_manager": {
        "description": "Comprehensive production deployment management",
        "features": ["system validation", "health monitoring", "deployment automation"],
        "status": "ready"
    },
    "user_testing_manager": {
        "description": "User testing infrastructure and feedback collection",
        "features": ["session management", "feedback collection", "accessibility testing"],
        "status": "ready"
    },
    "launch_production": {
        "description": "Production launcher and orchestration",
        "features": ["component initialization", "service management", "monitoring"],
        "status": "ready"
    }
}

def get_deployment_status():
    """
    Get comprehensive deployment infrastructure status.

    Returns:
        Dictionary containing deployment readiness information
    """
    return {
        "infrastructure_version": __version__,
        "status": __status__,
        "modules": DEPLOYMENT_MODULES,
        "capabilities": [
            "Production deployment automation",
            "System health monitoring",
            "User testing and feedback collection",
            "Accessibility compliance testing",
            "Performance metrics collection",
            "Graceful service management"
        ],
        "b1_ready": True,
        "phase_8b_complete": True,
        "legacy_optimization_available": LEGACY_DEPLOYMENT_AVAILABLE
    }

def quick_launch(mode="validation-only", **kwargs):
    """
    Quick launch function for ImpressionCore-B1.

    Args:
        mode: Launch mode ("full", "validation-only", "web-only", "api-only")
        **kwargs: Additional launch parameters

    Returns:
        ImpressionCoreProductionLauncher instance
    """
    launcher = ImpressionCoreProductionLauncher()
    success = launcher.launch_production(mode=mode, **kwargs)
      if success:
        print(f"✅ ImpressionCore-B1 {mode} launch successful!")
    else:
        print(f"❌ ImpressionCore-B1 {mode} launch failed!")

    return launcher
