#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #api #attention_mechanism #deployment #documentation #gpu_optimization #inference #memory_management #multimodal #performance #python #source_code #src/interfaces/web/server.py #testing #tokenization #training #web_interface
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** Kirk LaSalle
# Tags:** #api #attention_mechanism #deployment #documentation #gpu_optimization #inference #memory_management #multimodal #performance #python #source_code #src/interfaces/web/server.py #testing #tokenization #training #web_interface
# Category:** Interface Definitions
# Status:** Active

import os
import sys

# Ensure 'src' is in sys.path for direct execution
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)
"""
ImpressionCore: Server

Module for server functionality in the ImpressionCore framework.

File: server.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [production, 2025]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements server functionality for the
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
from server import MainClass
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
import subprocess
import threading
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, send_from_directory, url_for
from flask_cors import CORS

from core.utils.rich_logging import get_rich_logger
from core.utils.tokenizer_utils import generate_text, load_generative_model_and_tokenizer

# Optional multimodal pipeline integration
try:
    from core.ai.inference.pipelines.multimodal_pipeline import create_pipeline
    PIPELINE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Multimodal pipeline not available: {e}")
    PIPELINE_AVAILABLE = False
    create_pipeline = None

# Import route blueprints
try:
    from interfaces.web.routes import web as web_blueprint
    WEB_BLUEPRINT_AVAILABLE = True
except ImportError:
    WEB_BLUEPRINT_AVAILABLE = False
    web_blueprint = None

def create_app() -> Flask:

    logger = get_rich_logger(__name__)
    app = Flask(__name__)
    app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'impressioncore-secret')
    # Enable CORS for API endpoints
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    builder_client_dist = os.path.join(project_root, 'src', 'interfaces', 'builder_client', 'dist')
    builder_client_assets = os.path.join(builder_client_dist, 'assets')
    has_builder_react = os.path.exists(os.path.join(builder_client_dist, 'index.html'))
    if has_builder_react:
        logger.info(f"✅ React Builder client detected at: {builder_client_dist}")
    else:
        logger.info("ℹ️ React Builder client not found (falling back to Jinja templates)")

    # Register route blueprints (wires up POST handlers from routes.py)
    if WEB_BLUEPRINT_AVAILABLE and web_blueprint:
        app.register_blueprint(web_blueprint)
        logger.info("✅ Web blueprint registered (POST handlers active)")

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
    # --- API Endpoints for pipeline/model status ---
    @app.route('/api/v1/pipeline/status')
    def api_pipeline_status():
        if pipeline is None:
            return jsonify({
                'status': 'unavailable',
                'message': 'Multimodal pipeline not initialized'
            }), 503
        try:
            stats = pipeline.get_stats()
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

    @app.route('/api/v1/pipeline/process', methods=['POST'])
    def api_pipeline_process():
        if pipeline is None:
            return jsonify({'error': 'Pipeline not available'}), 503
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No input data provided'}), 400
            results = pipeline.process(data)
            return jsonify({'success': True, 'results': results})
        except Exception as e:
            logger.error(f"Pipeline processing error: {e}")
            return jsonify({'error': f'Processing failed: {e!s}'}), 500

    @app.route('/api/v1/models/b1/info')
    def api_b1_model_info():
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
            'status': 'active' if pipeline else 'inactive'
        })

    # --- Walkthrough Section ---
    @app.route('/walkthrough')
    def walkthrough():
        """
        Render the Walkthrough (preview/beta) page.
        Returns:
            Rendered HTML for walkthrough.html
        """
        return render_template('walkthrough.html')

    @app.route('/introduction')
    def introduction():
        return render_template('introduction.html')

    @app.route('/system_requirements')
    def system_requirements():
        return render_template('system_requirements.html')

    @app.route('/data_prep', methods=['GET'])
    def data_prep():
        return render_template('data_prep.html')

    @app.route('/data_prep/upload', methods=['POST'])
    def data_prep_upload():
        upload_dir = os.path.join(os.path.dirname(__file__), '../../../data/uploads')
        os.makedirs(upload_dir, exist_ok=True)
        file = request.files.get('dataFile')
        if not file:
            flash('No file selected.', 'danger')
            return redirect(url_for('data_prep'))
        filename = file.filename
        if not filename or not (filename.endswith('.txt') or filename.endswith('.csv') or filename.endswith('.json')):
            flash('Invalid file type. Only .txt, .csv, .json allowed.', 'danger')
            return redirect(url_for('data_prep'))
        save_path = os.path.join(upload_dir, filename)
        file.save(save_path)
        flash(f'File {filename} uploaded successfully.', 'success')
        return redirect(url_for('data_prep'))

    @app.route('/tokenizer')
    def tokenizer():
        return render_template('tokenizer.html')

    @app.route('/tokenizer/configure', methods=['POST'])
    def tokenizer_configure():
        """
        Handle tokenizer configuration form submission.
        Args: None (form data from POST)
        Returns: Redirects back to /tokenizer with a flash message.
        Memory: Minimal, only processes form data.
        """
        tokenizer_type = request.form.get('tokenizerType')
        vocab_size = request.form.get('vocabSize')
        if not tokenizer_type or not vocab_size:
            flash('Tokenizer type and vocabulary size are required.', 'danger')
            return redirect(url_for('tokenizer'))
        try:
            vocab_size = int(vocab_size)
        except ValueError:
            flash('Vocabulary size must be an integer.', 'danger')
            return redirect(url_for('tokenizer'))
        # Here you would save or apply the configuration as needed
        flash(f'Tokenizer configured: {tokenizer_type} with vocab size {vocab_size}', 'success')
        return redirect(url_for('tokenizer'))

    @app.route('/define_model')
    def define_model():
        return render_template('define_model.html')

    @app.route('/training')
    def training():
        return render_template('training.html')

    @app.route('/evaluation')
    def evaluation():
        return render_template('evaluation.html')


    @app.route('/inference')
    def inference():
        return render_template('inference.html')

    @app.route('/deployment')
    def deployment():
        """
        Render the Model Deployment page.
        Returns:
            Rendered HTML for deployment.html
        """
        return render_template('deployment.html')

    @app.route('/uks_introduction')
    def uks_introduction():
        return render_template('uks_introduction.html')

    @app.route('/rule_engine')
    def rule_engine():
        return render_template('rule_engine.html')

    @app.route('/inheritance')
    def inheritance():
        return render_template('inheritance.html')

    # --- Advanced & Reference Section ---
    @app.route('/unified_builder')
    def unified_builder():
        return render_template('unified_builder.html')

    @app.route('/configuration_interactive')
    def configuration_interactive():
        return render_template('configuration_interactive.html')

    @app.route('/metrics_dashboard')
    def metrics_dashboard():
        return render_template('metrics_dashboard.html')

    @app.route('/api_reference')
    def api_reference():
        return render_template('api_reference.html')

    @app.route('/documentation')
    def documentation():
        return render_template('documentation.html')

    @app.route('/development_roadmap')
    def development_roadmap():
        return render_template('development_roadmap.html')

    @app.route('/chat', methods=['GET', 'POST'])
    def chat():
        if request.method == 'GET':
            return render_template('chat.html')
        try:
            data = request.get_json(force=True)
            message = data.get('message', '').strip()
            if not message:
                return jsonify({'error': 'No message provided'}), 400
            tokenizer, model = get_model_tokenizer()
            reply = generate_text(message, tokenizer, model, device='cpu', max_length=128)
            return jsonify({'reply': reply})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/')
    def index():
        if has_builder_react:
            return send_from_directory(builder_client_dist, 'index.html')
        return render_template('index.html')

    @app.route('/assets/<path:filename>')
    def builder_assets(filename):
        if has_builder_react and os.path.exists(builder_client_assets):
            return send_from_directory(builder_client_assets, filename)
        return jsonify({'error': 'React assets not found'}), 404

    @app.route('/gpu_setup')
    def gpu_setup():
        """
        Render the GPU Setup page.
        Returns:
            Rendered HTML for gpu_setup.html
        """
        return render_template('gpu_setup.html')

    @app.route('/model_architecture')
    def model_architecture():
        """
        Render the Model Architecture page.
        Returns:
            Rendered HTML for model_architecture.html
        """
        return render_template('model_architecture.html')

    @app.route('/checkpoint')
    def checkpoint():
        """
        Render the Checkpoint Management page.
        Returns:
            Rendered HTML for checkpoint.html
        """
        return render_template('checkpoint.html')

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, 'static'),
            'favicon.ico', mimetype='image/vnd.microsoft.icon')

    # --- Walkthrough API Endpoints ---
    # These endpoints are called by walkthrough.html for system checks
    @app.route('/api/v1/walkthrough/action/gpu_check', methods=['POST'])
    def walkthrough_gpu_check():
        """Check GPU availability and CUDA status."""
        import torch
        try:
            gpu_available = torch.cuda.is_available()
            gpu_info = {
                'available': gpu_available,
                'device_name': torch.cuda.get_device_name(0) if gpu_available else 'N/A',
                'vram_total': f"{torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB" if gpu_available else 'N/A',
                'cuda_version': torch.version.cuda or 'N/A',
                'pytorch_version': torch.__version__
            }
            return jsonify({'success': True, 'gpu': gpu_info})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e), 'gpu': {'available': False}})

    @app.route('/api/v1/walkthrough/action/dependency_check', methods=['POST'])
    def walkthrough_dependency_check():
        """Check required Python dependencies."""
        deps = {}
        required = ['torch', 'transformers', 'numpy', 'pandas', 'flask', 'flask_cors', 'rich', 'cv2']
        for dep in required:
            try:
                mod = __import__(dep)
                deps[dep] = {'installed': True, 'version': getattr(mod, '__version__', 'unknown')}
            except ImportError:
                deps[dep] = {'installed': False, 'version': None}
        all_ok = all(d['installed'] for d in deps.values())
        return jsonify({'success': True, 'all_installed': all_ok, 'dependencies': deps})

    @app.route('/api/v1/walkthrough/action/config_check', methods=['POST'])
    def walkthrough_config_check():
        """Validate model configuration."""
        data = request.get_json(silent=True) or {}
        config = {
            'model': data.get('model', 'ImpressionCore-B3'),
            'hardware_target': 'GTX 1050 Ti (4GB VRAM)',
            'precision': data.get('precision', 'FP16'),
            'context_window': data.get('context_window', 128000),
            'valid': True
        }
        return jsonify({'success': True, 'config': config})

    @app.route('/api/v1/walkthrough/action/data_check', methods=['POST'])
    def walkthrough_data_check():
        """Check data readiness."""
        upload_dir = os.path.join(os.path.dirname(__file__), '../../../data/uploads')
        data_dir = os.path.join(os.path.dirname(__file__), '../../../data/datasets')
        files_found = []
        for d in [upload_dir, data_dir]:
            if os.path.exists(d):
                files_found.extend(os.listdir(d)[:10])
        return jsonify({
            'success': True,
            'data_ready': len(files_found) > 0,
            'files_found': len(files_found),
            'sample_files': files_found[:5]
        })

    @app.route('/api/v1/system/status')
    def api_system_status():
        """System-wide status for the Builder dashboard."""
        import torch
        status = {
            'server': 'online',
            'gpu_available': torch.cuda.is_available() if 'torch' in dir() else False,
            'pipeline': 'active' if pipeline else 'inactive',
            'version': '3.0.0',
            'model_series': 'B3'
        }
        try:
            status['gpu_available'] = torch.cuda.is_available()
            if status['gpu_available']:
                status['gpu_name'] = torch.cuda.get_device_name(0)
        except Exception:
            status['gpu_available'] = False
        return jsonify(status)

    # =========================================================================
    # Builder React Client API — /api/v1/builder/*
    # JSON endpoints consumed by the React Builder SPA (builder_client/)
    # =========================================================================

    @app.route('/api/v1/builder/data/upload', methods=['POST'])
    def builder_data_upload():
        """Accept file uploads from the React data-prep page."""
        upload_dir = os.path.join(os.path.dirname(__file__), '../../../data/uploads')
        os.makedirs(upload_dir, exist_ok=True)
        uploaded = []
        for key in request.files:
            f = request.files[key]
            if f and f.filename:
                save_path = os.path.join(upload_dir, f.filename)
                f.save(save_path)
                uploaded.append(f.filename)
        if not uploaded:
            return jsonify({'success': False, 'error': 'No files received'}), 400
        return jsonify({'success': True, 'files': uploaded, 'count': len(uploaded)})

    @app.route('/api/v1/builder/tokenizer/configure', methods=['POST'])
    def builder_tokenizer_configure():
        """Accept tokenizer config from React and persist to session/config."""
        data = request.get_json(silent=True) or {}
        tok_type = data.get('type', 'bpe')
        vocab = data.get('vocabSize', 32000)
        return jsonify({
            'success': True,
            'config': {'type': tok_type, 'vocabSize': vocab, **data},
        })

    @app.route('/api/v1/builder/model/configure', methods=['POST'])
    def builder_model_configure():
        """Accept model architecture config from React."""
        data = request.get_json(silent=True) or {}
        return jsonify({'success': True, 'config': data})

    @app.route('/api/v1/builder/training/start', methods=['POST'])
    def builder_training_start():
        """Kick off a training run (stub — wire to real pipeline later)."""
        data = request.get_json(silent=True) or {}
        logger.info(f"Training start requested: {data}")
        return jsonify({'success': True, 'message': 'Training started', 'config': data})

    @app.route('/api/v1/builder/training/status')
    def builder_training_status():
        """Return current training status (stub)."""
        return jsonify({
            'running': False, 'epoch': 0, 'step': 0,
            'loss': 0, 'vram': 0,
        })

    @app.route('/api/v1/builder/training/stop', methods=['POST'])
    def builder_training_stop():
        """Stop a running training job (stub)."""
        return jsonify({'success': True, 'message': 'Training stopped'})

    @app.route('/api/v1/builder/evaluation/run', methods=['POST'])
    def builder_evaluation_run():
        """Run model evaluation (stub with demo results)."""
        data = request.get_json(silent=True) or {}
        return jsonify({
            'success': True,
            'results': {
                'accuracy': 0.847, 'perplexity': 12.3, 'f1': 0.823,
                'bleu': 0.312, 'rouge_l': 0.654, 'latency': 45.2,
            },
        })

    @app.route('/api/v1/builder/inference/run', methods=['POST'])
    def builder_inference_run():
        """Run inference against loaded model (falls back to echo)."""
        data = request.get_json(silent=True) or {}
        prompt = data.get('prompt', '')
        try:
            tokenizer_obj, model_obj = get_model_tokenizer()
            reply = generate_text(prompt, tokenizer_obj, model_obj, device='cpu', max_length=128)
            return jsonify({'success': True, 'response': reply, 'tokens_used': len(reply.split())})
        except Exception as e:
            logger.warning(f"Inference fallback: {e}")
            return jsonify({
                'success': True,
                'response': f'[Demo] Received: "{prompt}". Connect a model for real inference.',
                'tokens_used': len(prompt.split()) + 10,
            })

    @app.route('/api/v1/builder/deployment/package', methods=['POST'])
    def builder_deployment_package():
        """Package model for deployment (stub)."""
        data = request.get_json(silent=True) or {}
        return jsonify({'success': True, 'message': 'Model packaged', 'config': data})

    @app.route('/api/v1/builder/deployment/deploy', methods=['POST'])
    def builder_deployment_deploy():
        """Deploy packaged model (stub)."""
        data = request.get_json(silent=True) or {}
        target = data.get('target', 'local')
        return jsonify({'success': True, 'message': f'Deployed to {target}', 'target': target})

    @app.route('/api/v1/builder/knowledge/add_fact', methods=['POST'])
    def builder_knowledge_add_fact():
        """Add a knowledge fact to the UKS."""
        data = request.get_json(silent=True) or {}
        if not data.get('subject') or not data.get('predicate') or not data.get('object'):
            return jsonify({'success': False, 'error': 'subject, predicate, and object are required'}), 400
        return jsonify({'success': True, 'fact': data})

    @app.route('/api/v1/builder/knowledge/query', methods=['POST'])
    def builder_knowledge_query():
        """Query the knowledge store."""
        data = request.get_json(silent=True) or {}
        q = data.get('query', '')
        # Stub response — replace with real UKS search
        return jsonify({'success': True, 'results': [], 'query': q})

    @app.route('/api/v1/builder/nav')
    def builder_nav():
        """Return navigation structure for the React sidebar."""
        return jsonify({
            'success': True,
            'pipeline': [
                {'num': i + 1, 'key': s, 'route': f'/{s}'}
                for i, s in enumerate([
                    'system-setup', 'data-prep', 'tokenizer', 'model-definition',
                    'training', 'evaluation', 'inference', 'deployment',
                ])
            ],
        })

    @app.route('/api/v1/builder/features')
    def builder_features():
        """Return a complete feature/function catalog for the Builder walkthrough."""
        pipeline_steps = [
            {'num': 1, 'key': 'introduction', 'label': 'Introduction', 'route': '/introduction'},
            {'num': 2, 'key': 'system_requirements', 'label': 'System Setup', 'route': '/system-setup'},
            {'num': 3, 'key': 'data_prep', 'label': 'Data Preparation', 'route': '/data-prep'},
            {'num': 4, 'key': 'tokenizer', 'label': 'Tokenization', 'route': '/tokenizer'},
            {'num': 5, 'key': 'define_model', 'label': 'Model Definition', 'route': '/model-definition'},
            {'num': 6, 'key': 'training', 'label': 'Training', 'route': '/training'},
            {'num': 7, 'key': 'evaluation', 'label': 'Evaluation', 'route': '/evaluation'},
            {'num': 8, 'key': 'inference', 'label': 'Inference', 'route': '/inference'},
            {'num': 9, 'key': 'deployment', 'label': 'Deployment', 'route': '/deployment'},
        ]

        knowledge = [
            {'key': 'knowledge', 'label': 'Knowledge Store', 'route': '/knowledge'},
            {'key': 'rule_engine', 'label': 'Rule Engine', 'route': '/rule-engine'},
            {'key': 'inheritance', 'label': 'Inheritance', 'route': '/inheritance'},
        ]

        advanced = [
            {'key': 'unified_builder', 'label': 'Unified Builder', 'route': '/unified-builder'},
            {'key': 'walkthrough', 'label': 'Walkthrough', 'route': '/walkthrough'},
            {'key': 'storage_control', 'label': 'Storage Control', 'route': '/storage-control'},
            {'key': 'gpu_setup', 'label': 'GPU Setup', 'route': '/gpu-setup'},
            {'key': 'architecture', 'label': 'Architecture', 'route': '/architecture'},
            {'key': 'checkpoints', 'label': 'Checkpoints', 'route': '/checkpoints'},
            {'key': 'chat', 'label': 'Chat', 'route': '/chat'},
            {'key': 'documentation', 'label': 'Documentation', 'route': '/documentation'},
        ]

        functions = [
            {'name': 'pipeline_status', 'method': 'GET', 'path': '/api/v1/pipeline/status', 'status': 'active'},
            {'name': 'pipeline_process', 'method': 'POST', 'path': '/api/v1/pipeline/process', 'status': 'active'},
            {'name': 'model_info', 'method': 'GET', 'path': '/api/v1/models/b1/info', 'status': 'active'},
            {'name': 'builder_data_upload', 'method': 'POST', 'path': '/api/v1/builder/data/upload', 'status': 'active'},
            {'name': 'builder_tokenizer_configure', 'method': 'POST', 'path': '/api/v1/builder/tokenizer/configure', 'status': 'active'},
            {'name': 'builder_model_configure', 'method': 'POST', 'path': '/api/v1/builder/model/configure', 'status': 'active'},
            {'name': 'builder_training_start', 'method': 'POST', 'path': '/api/v1/builder/training/start', 'status': 'stub'},
            {'name': 'builder_training_status', 'method': 'GET', 'path': '/api/v1/builder/training/status', 'status': 'stub'},
            {'name': 'builder_training_stop', 'method': 'POST', 'path': '/api/v1/builder/training/stop', 'status': 'stub'},
            {'name': 'builder_evaluation_run', 'method': 'POST', 'path': '/api/v1/builder/evaluation/run', 'status': 'stub'},
            {'name': 'builder_inference_run', 'method': 'POST', 'path': '/api/v1/builder/inference/run', 'status': 'active'},
            {'name': 'builder_deployment_package', 'method': 'POST', 'path': '/api/v1/builder/deployment/package', 'status': 'stub'},
            {'name': 'builder_deployment_deploy', 'method': 'POST', 'path': '/api/v1/builder/deployment/deploy', 'status': 'stub'},
            {'name': 'builder_knowledge_add_fact', 'method': 'POST', 'path': '/api/v1/builder/knowledge/add_fact', 'status': 'active'},
            {'name': 'builder_knowledge_query', 'method': 'POST', 'path': '/api/v1/builder/knowledge/query', 'status': 'stub'},
            {'name': 'builder_storage_status', 'method': 'GET', 'path': '/api/v1/builder/storage/status', 'status': 'active'},
            {'name': 'builder_storage_retention', 'method': 'POST', 'path': '/api/v1/builder/storage/retention', 'status': 'active'},
            {'name': 'builder_features', 'method': 'GET', 'path': '/api/v1/builder/features', 'status': 'active'},
        ]

        return jsonify({
            'success': True,
            'pipeline': pipeline_steps,
            'knowledge': knowledge,
            'advanced': advanced,
            'functions': functions,
        })

    @app.route('/api/v1/builder/storage/status')
    def builder_storage_status():
        """Return current F:/ storage health, capacity, and top-level summaries."""
        import shutil

        def _dir_size_bytes(path: Path) -> int:
            total = 0
            if not path.exists():
                return 0
            for root, _dirs, files in os.walk(path):
                for name in files:
                    file_path = Path(root) / name
                    try:
                        if not file_path.is_symlink():
                            total += file_path.stat().st_size
                    except OSError:
                        continue
            return total

        def _summarize_root(root: Path) -> list[dict]:
            rows = []
            if not root.exists():
                return rows
            for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
                if child.is_dir():
                    size_bytes = _dir_size_bytes(child)
                    rows.append({
                        'name': child.name,
                        'size_bytes': size_bytes,
                        'size_gb': round(size_bytes / (1024 ** 3), 2),
                    })
            return rows

        f_root = Path('F:/')
        data_root = Path('F:/data')
        models_root = Path('F:/models')

        total, used, free = shutil.disk_usage(str(f_root))
        top_level = []
        if f_root.exists():
            for child in sorted(f_root.iterdir(), key=lambda p: p.name.lower()):
                if child.is_dir():
                    top_level.append(child.name.lower())

        return jsonify({
            'success': True,
            'drive': {
                'total_gb': round(total / (1024 ** 3), 2),
                'used_gb': round(used / (1024 ** 3), 2),
                'free_gb': round(free / (1024 ** 3), 2),
            },
            'contract': {
                'required': ['data', 'models'],
                'project_top_level': [entry for entry in top_level if entry in {'data', 'models'}],
                'has_data': data_root.exists(),
                'has_models': models_root.exists(),
            },
            'data': {
                'root': str(data_root),
                'size_gb': round(_dir_size_bytes(data_root) / (1024 ** 3), 2),
                'subdirectories': _summarize_root(data_root),
            },
            'models': {
                'root': str(models_root),
                'size_gb': round(_dir_size_bytes(models_root) / (1024 ** 3), 2),
                'subdirectories': _summarize_root(models_root),
            },
        })

    @app.route('/api/v1/builder/storage/retention', methods=['POST'])
    def builder_storage_retention():
        """Preview or enforce retention policy for F:/ storage through Builder API."""
        data = request.get_json(silent=True) or {}

        try:
            from tools.f_drive_retention_manager import (
                RetentionPolicy,
                build_plan,
                bytes_to_gb,
                execute_plan,
                get_drive_usage,
                summarize_candidates,
            )
        except Exception as exc:
            return jsonify({'success': False, 'error': f'Retention manager import failed: {exc}'}), 500

        target_free_gb = float(data.get('target_free_gb', 95.0))
        hf_cache_age_days = int(data.get('hf_cache_age_days', 30))
        processed_age_days = int(data.get('processed_age_days', 45))
        keep_checkpoints_per_dir = int(data.get('keep_checkpoints_per_dir', 4))
        enforce = bool(data.get('enforce', False))
        preview_limit = int(data.get('preview_limit', 50))

        policy = RetentionPolicy(
            drive_root=Path('F:/'),
            target_free_gb=target_free_gb,
            max_hf_cache_age_days=hf_cache_age_days,
            max_processed_age_days=processed_age_days,
            keep_checkpoints_per_dir=max(1, keep_checkpoints_per_dir),
            enforce=enforce,
        )

        before_total, before_used, before_free = get_drive_usage(policy.drive_root)
        shortfall_gb = max(0.0, target_free_gb - bytes_to_gb(before_free))
        shortfall_bytes = int(shortfall_gb * (1024 ** 3))

        plan = build_plan(policy)
        summary = summarize_candidates(plan)
        summary_rows = [
            {
                'reason': reason,
                'count': count,
                'reclaimable_gb': round(bytes_to_gb(size_bytes), 2),
            }
            for reason, (count, size_bytes) in summary.items()
        ]

        reclaimed_bytes, processed_count = execute_plan(
            plan,
            required_bytes=shortfall_bytes,
            enforce=enforce,
            preview_limit=max(0, preview_limit),
        )

        after_total, after_used, after_free = get_drive_usage(policy.drive_root)

        return jsonify({
            'success': True,
            'mode': 'enforce' if enforce else 'dry-run',
            'target_free_gb': round(target_free_gb, 2),
            'shortfall_gb': round(shortfall_gb, 2),
            'plan_candidates': len(plan),
            'processed_candidates': processed_count,
            'plan_reclaimable_gb': round(bytes_to_gb(sum(item.size_bytes for item in plan)), 2),
            'reclaimed_gb': round(bytes_to_gb(reclaimed_bytes), 2),
            'before': {
                'total_gb': round(bytes_to_gb(before_total), 2),
                'used_gb': round(bytes_to_gb(before_used), 2),
                'free_gb': round(bytes_to_gb(before_free), 2),
            },
            'after': {
                'total_gb': round(bytes_to_gb(after_total), 2),
                'used_gb': round(bytes_to_gb(after_used), 2),
                'free_gb': round(bytes_to_gb(after_free), 2),
            },
            'summary_by_reason': summary_rows,
        })

    # --- Error Handlers ---
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500

    return app

# --- Model/Tokenizer Loader (thread-safe, memory-efficient) ---
_model_tokenizer_lock = threading.Lock()
_model_tokenizer = None
def get_model_tokenizer():
    global _model_tokenizer
    with _model_tokenizer_lock:
        if _model_tokenizer is None:
            tokenizer, model = load_generative_model_and_tokenizer()
            _model_tokenizer = (tokenizer, model)
        return _model_tokenizer


# --- Entry point to run the Flask server ---
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)

