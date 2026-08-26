#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #command_line #memory_management #multimodal #performance #python #source_code #src/interfaces/web\tests/conftest.py #testing #transformer #web_interface
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** Kirk LaSalle
# Tags:** #command_line #memory_management #multimodal #performance #python #source_code #src\\interfaces\\web\\tests\\conftest.py #testing #transformer #web_interface
# Category:** Interface Definitions
# Status:** Active

"""
ImpressionCore: Conftest

Module for conftest functionality in the ImpressionCore framework.

File: web/tests/conftest.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [qa, production, testing, web, frontend, 2025]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements conftest functionality for the
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
from web.tests.conftest import MainClass
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

import pytest
from flask import Flask
from flask_sock import Sock

# Fix import path for absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from interfaces.web.routes.model_definition_init import register_model_definition


@pytest.fixture
def app():
    """Create test application instance"""
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../static'))
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost:5000'

    # Initialize WebSocket
    sock = Sock(app)

    # Add model templates to app config
    # Memory optimization: Explicit memory cleanup
    app.config['MODEL_TEMPLATES'] = {
        'basic-transformer': {
            'name': 'Basic Transformer',
            'numLayers': 12,
            'hiddenSize': 768,
            'numHeads': 12,
            'ffnDim': 3072,
            'dropoutRate': 0.1,
            'maxSeqLength': 1024,
            'enableLoRA': False
        }
    }

    app.secret_key = 'test-secret-key'

    # Register model definition routes without modifying existing ones
    # Memory optimization: Explicit memory cleanup
    from interfaces.web.routes import web as web_blueprint
    from interfaces.web.routes.configuration import config_bp
    from interfaces.web.routes.tokenizer_training import tokenizer_training_bp
    from interfaces.web.routes.model_visualization import model_viz as model_viz_bp
    from interfaces.web.routes.training_visualization import training_viz as training_viz_bp
    from interfaces.web.routes.deployment import deployment_bp
    from interfaces.web.routes.training_routes import training_bp
    from interfaces.web.routes.metrics import metrics_bp
    from interfaces.web.routes.builder import builder_bp
    from interfaces.web.routes.builder_views import builder_views_bp

    with app.app_context():
        register_model_definition(app, sock)
        app.register_blueprint(web_blueprint)
        app.register_blueprint(config_bp)
        app.register_blueprint(tokenizer_training_bp)
        app.register_blueprint(model_viz_bp)
        app.register_blueprint(training_viz_bp)
        app.register_blueprint(deployment_bp)
        app.register_blueprint(training_bp)
        app.register_blueprint(metrics_bp)
        app.register_blueprint(builder_bp)
        app.register_blueprint(builder_views_bp)

        # Alias blueprint endpoints to unprefixed names for legacy templates
        for rule in app.url_map.iter_rules():
            if '.' in rule.endpoint:
                alias = rule.endpoint.split('.', 1)[1]
                if alias not in app.view_functions:
                    app.add_url_rule(
                        rule.rule,
                        endpoint=alias,
                        view_func=app.view_functions[rule.endpoint],
                        methods=rule.methods,
                        defaults=rule.defaults,
                    )

    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def test_config():
    """Provide test model configuration"""
    # Memory optimization: Explicit memory cleanup
    return {
        'numLayers': 12,
        'hiddenSize': 768,
        'numHeads': 12,
        'ffnDim': 3072,
        'dropoutRate': 0.1,
        'maxSeqLength': 1024,
        'enableLoRA': False
    }

@pytest.fixture
def invalid_config():
    """Provide invalid model configuration for testing"""
    # Memory optimization: Explicit memory cleanup
    return {
        'numLayers': 0,  # Invalid: must be >= 1
        'hiddenSize': 100,  # Invalid: must be multiple of 64
        'numHeads': 50,  # Invalid: must be <= 32
        'ffnDim': 1000,  # Invalid: must be multiple of 128
        'dropoutRate': 1.5,  # Invalid: must be <= 1.0
        'maxSeqLength': 100,  # Invalid: must be multiple of 128
        'enableLoRA': False
    }
