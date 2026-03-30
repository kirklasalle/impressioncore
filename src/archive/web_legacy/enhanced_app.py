#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #command_line #cuda #gpu_optimization #memory_management #python #source_code #src/interfaces/web/enhanced_app.py #web_interface
**Category:** Interface Definitions
**Status:** Active
"""









# Enhanced App

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** ImpressionCore Team
# Tags:** #api #command_line #cuda #gpu_optimization #memory_management #python #source_code #src/interfaces/web/enhanced_app.py #web_interface
# Category:** Interface Definitions
# Status:** Active

"""
ImpressionCore Enhanced Web Interface
====================================

Modern web interface with text generation integration,
real-time VRAM monitoring, and professional UI design.

Features:
- Real-time text generation interface
- VRAM monitoring dashboard
- Modern, responsive design
- Integration with text generation service
- Live performance metrics

Author: ImpressionCore Team
Date: 2025-01-09
"""

import asyncio
import logging
import threading
import time
from datetime import datetime

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from .core.utils.hardware_detection import HardwareDetector
from .core.utils.rich_enhancements import RichUI
from .services.text_generation import GenerationConfig, create_text_generation_service


class ImpressionCoreWebInterface:
    """Enhanced web interface for ImpressionCore text generation."""

    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'impressioncore-web-secret-2025'

        # Initialize extensions
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # Initialize components
        self.rich_ui = RichUI()
        self.hardware_detector = HardwareDetector()
        self.text_service = None
        self.monitoring_active = False

        # Logger
        self.logger = logging.getLogger(__name__)

        # Register routes
        self._register_routes()
        self._register_socketio_events()

        self.logger.info("ImpressionCore Web Interface initialized")

    def _register_routes(self):
        """Register Flask routes."""

        @self.app.route('/')
        def index():
            """Main application page."""
            return render_template('index.html')

        @self.app.route('/api/health')
        def health():
            """Health check endpoint."""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'service_initialized': self.text_service is not None and self.text_service.is_initialized,
                'cuda_available': self.hardware_detector.cuda_available(),
                'gpu_info': self.hardware_detector.get_gpu_info()
            })

        @self.app.route('/api/initialize', methods=['POST'])
        def initialize_service():
            """Initialize the text generation service."""
            try:
                if self.text_service is None:
                    self.text_service = create_text_generation_service()

                # Run initialization in thread to avoid blocking
                def init_thread():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(self.text_service.initialize())
                    loop.close()

                    # Emit result via WebSocket
                    self.socketio.emit('service_initialized', {'success': result})

                thread = threading.Thread(target=init_thread)
                thread.start()

                return jsonify({'status': 'initializing'})

            except Exception as e:
                self.logger.error(f"Service initialization failed: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/generate', methods=['POST'])
        def generate_text():
            """Generate text endpoint."""
            try:
                if not self.text_service or not self.text_service.is_initialized:
                    return jsonify({'error': 'Service not initialized'}), 400

                data = request.get_json()
                prompt = data.get('prompt', '')

                if not prompt:
                    return jsonify({'error': 'Prompt is required'}), 400

                # Generation configuration from request
                config = GenerationConfig(
                    max_length=data.get('max_length', 512),
                    temperature=data.get('temperature', 0.8),
                    top_p=data.get('top_p', 0.9),
                    top_k=data.get('top_k', 50),
                    repetition_penalty=data.get('repetition_penalty', 1.1),
                    do_sample=data.get('do_sample', True),
                    num_return_sequences=data.get('num_return_sequences', 1)
                )

                # Generate in thread to avoid blocking
                def generate_thread():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    try:
                        result = loop.run_until_complete(
                            self.text_service.generate_text(prompt, config)
                        )

                        # Emit result via WebSocket
                        self.socketio.emit('generation_complete', {
                            'generated_text': result.generated_text,
                            'generation_time': result.generation_time,
                            'tokens_per_second': result.tokens_per_second,
                            'memory_used': result.memory_used,
                            'metadata': result.metadata
                        })

                    except Exception as e:
                        self.socketio.emit('generation_error', {'error': str(e)})

                    finally:
                        loop.close()

                thread = threading.Thread(target=generate_thread)
                thread.start()

                return jsonify({'status': 'generating'})

            except Exception as e:
                self.logger.error(f"Text generation failed: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/stats')
        def get_stats():
            """Get service statistics."""
            try:
                if not self.text_service:
                    return jsonify({'error': 'Service not available'}), 400

                stats = self.text_service.get_stats()
                return jsonify(stats)

            except Exception as e:
                self.logger.error(f"Failed to get stats: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/static/<path:filename>')
        def static_files(filename):
            """Serve static files."""
            return send_from_directory('static', filename)

    def _register_socketio_events(self):
        """Register WebSocket events."""

        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            self.logger.info("Client connected")
            emit('connected', {'status': 'connected'})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            self.logger.info("Client disconnected")

        @self.socketio.on('start_monitoring')
        def handle_start_monitoring():
            """Start real-time monitoring."""
            self.monitoring_active = True
            self._start_monitoring_thread()
            emit('monitoring_started', {'status': 'monitoring_active'})

        @self.socketio.on('stop_monitoring')
        def handle_stop_monitoring():
            """Stop real-time monitoring."""
            self.monitoring_active = False
            emit('monitoring_stopped', {'status': 'monitoring_inactive'})

    def _start_monitoring_thread(self):
        """Start background monitoring thread."""
        def monitor():
            while self.monitoring_active:
                try:
                    # Get hardware information
                    hardware_info = self.hardware_detector.get_system_status()

                    # Get service stats if available
                    service_stats = {}
                    if self.text_service and self.text_service.is_initialized:
                        service_stats = self.text_service.get_stats()

                    # Emit monitoring data
                    self.socketio.emit('monitoring_update', {
                        'timestamp': time.time(),
                        'hardware': hardware_info,
                        'service': service_stats
                    })

                    time.sleep(2)  # Update every 2 seconds

                except Exception as e:
                    self.logger.error(f"Monitoring error: {e}")
                    time.sleep(5)

        if not hasattr(self, '_monitoring_thread') or not self._monitoring_thread.is_alive():
            self._monitoring_thread = threading.Thread(target=monitor, daemon=True)
            self._monitoring_thread.start()

    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the web application."""
        self.rich_ui.print_status(f"🚀 Starting ImpressionCore Web Interface on {host}:{port}", "info")
        self.socketio.run(self.app, host=host, port=port, debug=debug)


# Create global app instance
web_interface = ImpressionCoreWebInterface()
app = web_interface.app
socketio = web_interface.socketio


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Run the application
    web_interface.run(debug=True)
