#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #api #attention_mechanism #inference #memory_management #multimodal #python #source_code #src/interfaces/web\app.py #tokenization #training #web_interface
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** Kirk LaSalle
# Tags:** #api #attention_mechanism #inference #memory_management #multimodal #python #source_code #src\\interfaces\\web\\app.py #tokenization #training #web_interface
# Category:** Interface Definitions
# Status:** Active

"""
ImpressionCore Web Application Factory

This module provides a Flask application factory that integrates with the existing
web frontend and adds multimodal pipeline capabilities to support the B1 model
walkthrough experience.

File: web/app.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-06-05
Version: 1.0.0

Authors:
- GitHub Copilot
- Kirk LaSalle

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [web, flask, factory, integration, b1-model, 2025]
Dependencies: [flask, existing web infrastructure]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This application factory integrates with the existing ImpressionCore web frontend,
preserving all existing functionality while adding multimodal pipeline support
for the B1 model walkthrough menu system.

CRITICAL: This module EXTENDS the existing web infrastructure - it does NOT replace:
- templates/base.html (menu structure preserved)
- static/ directory (CSS, JS, styles preserved)
- routes.py (existing routes preserved)
- server.py (main server logic preserved)

New Features Added:
- Multimodal pipeline integration for B1 model
- Enhanced inference endpoints
- Real-time model status monitoring
- Memory optimization for GTX 1050 Ti

Integration Points:
- /inference route: Enhanced with multimodal pipeline
- /define_model route: B1 model configuration support
- /training route: Pipeline monitoring
- New /api/v1/* endpoints: RESTful API for pipeline operations
"""

import os
import sys
from pathlib import Path
from typing import Any

# Add project root to Python path (to allow src.* imports)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Flask and web dependencies
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

# Rich logging for better UX
from core.utils.rich_logging import get_rich_logger

# Import existing web infrastructure (DO NOT BREAK)
try:
    from interfaces.web.route_config import *  # Existing route configuration
    from interfaces.web.routes import web  # Existing routes blueprint
except ImportError as e:
    print(f"Warning: Could not import existing web routes: {e}")
    web = None

# Import new multimodal pipeline
try:
    from core.ai.inference.pipelines.multimodal_pipeline import create_pipeline
    PIPELINE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Multimodal pipeline not available: {e}")
    PIPELINE_AVAILABLE = False
    create_pipeline = None


class ImpressionCoreWebApp:
    """
    Web application factory for ImpressionCore.

    This class creates and configures the Flask application while preserving
    all existing web frontend functionality and adding multimodal pipeline support.
    """

    def __init__(self):
        self.logger = get_rich_logger(__name__)
        self.app = None
        self.pipeline = None

    def create_app(self, config: dict[str, Any] | None = None) -> Flask:
        """
        Create and configure the Flask application.

        Args:
            config: Optional configuration dictionary

        Returns:
            Flask: Configured Flask application
        """
        self.logger.info("Creating ImpressionCore web application...")

        # Create Flask app
        self.app = Flask(
            __name__,
            template_folder='templates',
            static_folder='static'
        )

        # Configure app
        self._configure_app(config or {})

        # Initialize multimodal pipeline if available
        self._initialize_pipeline()

        # Register blueprints (PRESERVE existing functionality)
        self._register_blueprints()

        # Add new API routes for pipeline integration
        self._register_api_routes()

        # Add enhanced route handlers
        self._enhance_existing_routes()

        self.logger.info("✅ ImpressionCore web application created successfully")
        return self.app

    def _configure_app(self, config: dict[str, Any]):
        """Configure Flask application settings."""
        # Default configuration
        default_config = {
            'SECRET_KEY': os.environ.get('SECRET_KEY', 'impression-core-dev-key'),
            'DEBUG': os.environ.get('FLASK_DEBUG', 'False').lower() == 'true',
            'UPLOAD_FOLDER': 'uploads',
            'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max file size
            'WTF_CSRF_ENABLED': False,  # Disable CSRF for API endpoints
        }

        # Merge with provided config
        default_config.update(config)

        # Apply configuration
        for key, value in default_config.items():
            self.app.config[key] = value
          # Enable CORS for API endpoints
        CORS(self.app, resources={r"/api/*": {"origins": "*"}})

        self.logger.info("Flask application configured")

    def _initialize_pipeline(self):
        """Initialize the multimodal pipeline if available."""
        if not PIPELINE_AVAILABLE:
            self.logger.warning("Multimodal pipeline not available - some features disabled")
            return

        try:
            self.logger.info("Initializing multimodal pipeline...")
            self.pipeline = create_pipeline(
                device='auto'
            )
            self.logger.info("✅ Multimodal pipeline initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize pipeline: {e}")
            self.pipeline = None

    def _register_blueprints(self):
        """Register existing blueprints (PRESERVE functionality)."""
        if web is not None:
            self.app.register_blueprint(web)
            self.logger.info("✅ Existing web routes registered")
        else:
            self.logger.warning("Existing web routes not available")

    def _register_api_routes(self):
        """Register new API routes for pipeline integration."""

        @self.app.route('/api/v1/pipeline/status')
        def api_pipeline_status():
            """Get multimodal pipeline status."""
            if self.pipeline is None:
                return jsonify({
                    'status': 'unavailable',
                    'message': 'Multimodal pipeline not initialized'
                }), 503

            try:
                stats = self.pipeline.get_stats()
                return jsonify({
                    'status': 'available',
                    'stats': stats,
                    'model': 'ImpressionCore-B1'
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500

        @self.app.route('/api/v1/pipeline/process', methods=['POST'])
        def api_pipeline_process():
            """Process input through the multimodal pipeline."""
            if self.pipeline is None:
                return jsonify({
                    'error': 'Pipeline not available'
                }), 503

            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No input data provided'}), 400

                # Process through pipeline
                results = self.pipeline.process(data)

                return jsonify({
                    'success': True,
                    'results': results
                })

            except Exception as e:
                self.logger.error(f"Pipeline processing error: {e}")
                return jsonify({
                    'error': f'Processing failed: {e!s}'
                }), 500

        @self.app.route('/api/v1/models/b1/info')
        def api_b1_model_info():
            """Get B1 model information."""
            return jsonify({
                'name': 'ImpressionCore-B1',
                'description': 'Brain-inspired multimodal AI model optimized for GTX 1050 Ti',
                'version': '1.0.0',
                'memory_target': '4GB VRAM',
                'capabilities': [
                    'Text processing',
                    'Multimodal inference',
                    'Memory-optimized generation',
                    'Chunked attention'
                ],
                'status': 'active' if self.pipeline else 'inactive'
            })

        self.logger.info("✅ API routes registered")

    def _enhance_existing_routes(self):
        """Enhance existing routes with pipeline integration."""

        # Enhanced inference page with pipeline integration
        @self.app.route('/inference_enhanced')
        def inference_enhanced():
            """Enhanced inference page with multimodal pipeline support."""
            pipeline_status = {
                'available': self.pipeline is not None,
                'model': 'ImpressionCore-B1',
                'memory_optimized': True
            }

            if self.pipeline:
                try:
                    pipeline_status['stats'] = self.pipeline.get_stats()
                except Exception:
                    pipeline_status['stats'] = {}

            return render_template(
                'inference.html',  # Use existing template
                pipeline_status=pipeline_status,
                enhanced=True
            )

        # Model status endpoint for the walkthrough menu
        @self.app.route('/model_status')
        def model_status():
            """Get current model status for the walkthrough menu."""
            return jsonify({
                'current_model': 'ImpressionCore-B1',
                'pipeline_ready': self.pipeline is not None,
                'walkthrough_complete': self._check_walkthrough_status(),
                'memory_optimized': True,
                'target_hardware': 'GTX 1050 Ti (4GB VRAM)'
            })

        self.logger.info("✅ Enhanced route handlers added")

    def _check_walkthrough_status(self) -> dict[str, bool]:
        """Check completion status of walkthrough steps."""
        # This would check actual completion status in a real implementation
        return {
            'introduction': True,
            'system_requirements': True,
            'data_prep': False,  # User needs to complete
            'tokenizer': False,
            'define_model': True,  # B1 model available
            'training': False,
            'evaluation': False,
            'inference': self.pipeline is not None,
            'uks_introduction': False,
            'rule_engine': False,
            'inheritance': False
        }

    def get_pipeline(self):
        """Get the multimodal pipeline instance."""
        return self.pipeline

    def cleanup(self):
        """Clean up resources."""
        if self.pipeline:
            self.pipeline.cleanup()
        self.logger.info("Web application cleanup complete")


# Application factory function
def create_app(config: dict[str, Any] | None = None) -> Flask:
    """
    Create and configure the ImpressionCore web application.

    This is the main entry point for creating the Flask app with all
    existing functionality preserved and new pipeline features added.

    Args:
        config: Optional configuration dictionary

    Returns:
        Flask: Configured Flask application with multimodal pipeline support

    Example:
        ```python
        from interfaces.web.app import create_app

        app = create_app()
        app.run(debug=True, host='0.0.0.0', port=5000)
        ```
    """
    web_app = ImpressionCoreWebApp()
    return web_app.create_app(config)


# Global reference for cleanup
_web_app_instance = None


def get_app_instance() -> ImpressionCoreWebApp | None:
    """Get the current web app instance."""
    global _web_app_instance
    return _web_app_instance


if __name__ == "__main__":
    # Development server
    app = create_app({'DEBUG': True})

    print("🚀 Starting ImpressionCore Web Application")
    print("📝 Existing web interface preserved")
    print("🔧 Multimodal pipeline integration added")
    print("🎯 Optimized for GTX 1050 Ti (4GB VRAM)")
    print("🌐 Server starting at http://localhost:5000")

    try:
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped")
        if _web_app_instance:
            _web_app_instance.cleanup()
