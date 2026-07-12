#!/usr/bin/env python3
r"""
ImpressionCore: Server

Decomposed Flask application entry point for ImpressionCore. Wires up modular
blueprints and starts the server. Optimized for memory-constrained environments
(e.g., GTX 1050 Ti 4GB VRAM).
"""

import os
import sys
import warnings
import json
import threading
from pathlib import Path

# Suppress pynvml deprecation FutureWarning (internal to PyTorch, cosmetic only)
warnings.filterwarnings("ignore", message=".*pynvml.*deprecated.*", category=FutureWarning)

# Ensure project root and 'src' are in sys.path for direct execution
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS

from src.core.utils.rich_logging import get_rich_logger
from src.core.utils.tokenizer_utils import generate_text, load_generative_model_and_tokenizer

# Optional multimodal pipeline integration
try:
    from src.core.ai.inference.pipelines.multimodal_pipeline import create_pipeline
    PIPELINE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Multimodal pipeline not available: {e}")
    PIPELINE_AVAILABLE = False
    create_pipeline = None

# Import route blueprints
try:
    from interfaces.web.routes import web as web_blueprint
    from interfaces.web.routes.configuration import config_bp
    from interfaces.web.routes.tokenizer_training import tokenizer_training_bp
    from interfaces.web.routes.model_visualization import model_viz as model_viz_bp
    from interfaces.web.routes.training_visualization import training_viz as training_viz_bp
    from interfaces.web.routes.deployment import deployment_bp
    from interfaces.web.routes.training_routes import training_bp
    from interfaces.web.routes.model_definition import model_definition as model_definition_bp
    from interfaces.web.routes.metrics import metrics_bp
    from interfaces.web.routes.builder import builder_bp
    WEB_BLUEPRINT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Route blueprints not fully available: {e}")
    WEB_BLUEPRINT_AVAILABLE = False
    web_blueprint = None

def create_app() -> Flask:
    logger = get_rich_logger(__name__)
    app = Flask(__name__)
    app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'impressioncore-secret')
    
    # Enable CORS for API endpoints
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Prevent stale HTML on hard refresh
    @app.after_request
    def set_cache_headers(response):
        if response.content_type and 'text/html' in response.content_type:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

    builder_client_dist = os.path.join(project_root, 'src', 'interfaces', 'builder_client', 'dist')
    builder_client_assets = os.path.join(builder_client_dist, 'assets')
    has_builder_react = os.path.exists(os.path.join(builder_client_dist, 'index.html'))
    if has_builder_react:
        logger.info(f"✅ React Builder client detected at: {builder_client_dist}")
    else:
        logger.info("ℹ️ React Builder client not found (falling back to Jinja templates)")

    # Optional multimodal pipeline
    pipeline = None
    if PIPELINE_AVAILABLE:
        try:
            logger.info("Initializing multimodal pipeline...")
            pipeline = create_pipeline(device='auto')
            logger.info("✅ Multimodal pipeline initialized")
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
            pipeline = None

    # Inject variables/states into builder blueprint module
    if WEB_BLUEPRINT_AVAILABLE:
        import interfaces.web.routes.builder as builder_module
        builder_module.pipeline = pipeline
        builder_module.project_root = project_root
        builder_module.builder_client_dist = builder_client_dist
        builder_module.has_builder_react = has_builder_react
        builder_module.builder_client_assets = builder_client_assets

    # Register route blueprints
    if WEB_BLUEPRINT_AVAILABLE and web_blueprint:
        app.register_blueprint(web_blueprint)
        app.register_blueprint(config_bp)
        app.register_blueprint(tokenizer_training_bp)
        app.register_blueprint(model_viz_bp)
        app.register_blueprint(training_viz_bp)
        app.register_blueprint(deployment_bp)
        app.register_blueprint(training_bp)
        app.register_blueprint(model_definition_bp)
        app.register_blueprint(metrics_bp)
        app.register_blueprint(builder_bp)

        # Alias blueprint endpoints to unprefixed names for legacy templates.
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
        logger.info("✅ All route blueprints registered successfully")

    return app

# --- Entry point to run the Flask server ---
if __name__ == "__main__":
    # Filter out noisy favicon.ico requests from the access log
    import logging as _logging
    class _FaviconFilter(_logging.Filter):
        def filter(self, record):
            return '/favicon.ico' not in record.getMessage()
    _logging.getLogger('werkzeug').addFilter(_FaviconFilter())

    app = create_app()
    # use_reloader=False prevents double startup (pipeline loads once)
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
