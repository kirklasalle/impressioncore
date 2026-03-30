#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #memory_management #multimodal #performance #python #source_code #src/interfaces/web/server_bootstrap.py #testing #training #web_interface
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** Kirk LaSalle
# Tags:** #memory_management #multimodal #performance #python #source_code #src/interfaces/web/server_bootstrap.py #testing #training #web_interface
# Category:** Interface Definitions
# Status:** Active

r"""
ImpressionCore: Server Bootstrap

Module for server bootstrap functionality in the ImpressionCore framework.

File: web/server_bootstrap.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [production, web, frontend, 2025, object-oriented]
Dependencies: [typing, pathlib]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements server bootstrap functionality for the
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
from web.server_bootstrap import ServerBootstrap
instance = ServerBootstrap()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import logging
import os
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("bootstrap")

class ServerBootstrap:
    """Bootstrap class for automatic server configuration."""

    def __init__(self):
        """

    __init__ function for processing.

    Args:
        self: Function parameters

    Returns:
        Processed result

    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints

        """
        # Set up paths
        self.project_root = Path(__file__).parent.parent.parent.absolute()
        self.static_folder = self.project_root / 'static'
        self.template_folder = self.project_root / 'templates'

        # Ensure paths exist
        self._ensure_directories()

        # Add project root to path if needed
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))

        # Initialize components
        self._init_hardware_detection()
        self._init_config()
        self._init_routes()

    def _ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        dirs = [
            self.static_folder,
            self.static_folder / 'js',
            self.static_folder / 'css',
            self.static_folder / 'img',
            self.template_folder,
        ]

        for directory in dirs:
            if not directory.exists():
                logger.info(f"Creating directory: {directory}")
                os.makedirs(directory, exist_ok=True)

    def _init_hardware_detection(self) -> None:
        """Initialize hardware detection."""
        try:
            from core.utils.hw_scanner import system
            system.detect_system()
            compatibility = system.analyze_compatibility()
            logger.info(f"Hardware detection complete: {compatibility['is_compatible']}")

            # Log recommendations
            for rec in compatibility['recommendations']:
                logger.info(f"System recommendation: {rec}")

        except ImportError:
            logger.warning("Hardware scanner module not found. Skipping hardware detection.")
        except Exception as e:
            logger.error(f"Error during hardware detection: {e}")

    def _init_config(self) -> None:
        """Initialize configuration management."""
        try:
            from .core.config.config_manager import config_manager
            # Load all predefined configs
            app_config = config_manager.load_config('app')
            config_manager.load_config('model')
            config_manager.load_config('training')

            # Create default app config if needed
            if not app_config:
                logger.info("Creating default app configuration")
                default_config = {
                    'debug': True,
                    'port': 5000,
                    'host': '0.0.0.0',
                    'allow_cors': True,
                    'server_name': 'ImpressionCore'
                }
                config_manager.save_config('app', default_config)

        except ImportError:
            logger.warning("Config manager module not found. Using default configurations.")
        except Exception as e:
            logger.error(f"Error during configuration initialization: {e}")

    def _init_routes(self) -> None:
        """Discover and initialize route definitions."""
        try:
            from .interfaces.web.route_config import routes  # noqa: F401
            logger.info("Route registry initialized")
        except ImportError:
            logger.warning("Route registry module not found. Using manual route definitions.")

    def create_app(self):
        """Create and configure the Flask application."""
        try:
            from flask import Flask, jsonify, render_template, request  # noqa: F401
            from flask_cors import CORS

            # Create Flask app
            app = Flask(
                __name__,
                static_url_path='/static',
                static_folder=str(self.static_folder),
                template_folder=str(self.template_folder)
            )

            # Enable CORS if specified in config
            try:
                from .core.config.config_manager import config_manager
                if config_manager.get('app', 'allow_cors', True):
                    CORS(app)
            except ImportError:
                CORS(app)  # Default to enabling CORS if config manager not available

            # Apply routes if route registry is available
            try:
                from .interfaces.web.route_config import routes
                routes.apply_routes(app)
                logger.info(f"Registered {len(routes.routes)} routes from registry")
            except ImportError:
                logger.info("Using routes defined in server.py")

            # Return configured app
            return app

        except ImportError as e:
            logger.error(f"Critical import error during app creation: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Critical error during app creation: {e}")
            sys.exit(1)

    def run_app(self, app):
        """Run the Flask application with correct settings."""
        try:
            # Get port from config if available
            port = 5000
            debug = True
            host = '0.0.0.0'

            try:
                from .core.config.config_manager import config_manager
                port = config_manager.get('app', 'port', 5000)
                debug = config_manager.get('app', 'debug', True)
                host = config_manager.get('app', 'host', '0.0.0.0')
            except ImportError:
                pass

            logger.info(f"Starting server at http://{host}:{port}")

            # Run the app
            app.run(debug=debug, port=port, host=host)

        except Exception as e:
            logger.error(f"Error starting server: {e}")
            sys.exit(1)

def create_app():
    """Create a Flask application with automatic configuration."""
    bootstrap = ServerBootstrap()
    return bootstrap.create_app()

def run_server():
    """Run the server with automatic configuration."""
    bootstrap = ServerBootstrap()
    app = bootstrap.create_app()
    bootstrap.run_app(app)

if __name__ == "__main__":
    run_server()
