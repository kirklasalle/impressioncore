#!/usr/bin/env python3
"""
ImpressionCore Web Builder HTML View Routes Blueprint
"""
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app

# Create blueprint
builder_views_bp = Blueprint('builder_views', __name__)

def _serve_page(filename):
    return render_template(filename)

@builder_views_bp.route('/walkthrough')
def walkthrough():
    return _serve_page('walkthrough.html')

@builder_views_bp.route('/introduction')
def introduction():
    return _serve_page('introduction.html')

@builder_views_bp.route('/system_requirements')
def system_requirements():
    return _serve_page('system_requirements.html')

@builder_views_bp.route('/data_prep', methods=['GET'])
def data_prep():
    return _serve_page('data_prep.html')

@builder_views_bp.route('/data_prep/upload', methods=['POST'])
def data_prep_upload():
    upload_dir = os.path.join(current_app.root_path, '../../../data/uploads')
    os.makedirs(upload_dir, exist_ok=True)
    file = request.files.get('dataFile')
    if not file:
        flash('No file selected.', 'danger')
        return redirect(url_for('builder_views.data_prep'))
    filename = file.filename
    if not filename or not (filename.endswith('.txt') or filename.endswith('.csv') or filename.endswith('.json')):
        flash('Invalid file type. Only .txt, .csv, .json allowed.', 'danger')
        return redirect(url_for('builder_views.data_prep'))
    save_path = os.path.join(upload_dir, filename)
    file.save(save_path)
    flash(f'File {filename} uploaded successfully.', 'success')
    return redirect(url_for('builder_views.data_prep'))

@builder_views_bp.route('/tokenizer')
def tokenizer():
    return _serve_page('tokenizer.html')

@builder_views_bp.route('/tokenizer/configure', methods=['POST'])
def tokenizer_configure():
    tokenizer_type = request.form.get('tokenizerType')
    vocab_size = request.form.get('vocabSize')
    if not tokenizer_type or not vocab_size:
        flash('Tokenizer type and vocabulary size are required.', 'danger')
        return redirect(url_for('builder_views.tokenizer'))
    try:
        vocab_size = int(vocab_size)
    except ValueError:
        flash('Vocabulary size must be an integer.', 'danger')
        return redirect(url_for('builder_views.tokenizer'))
    flash(f'Tokenizer configured: {tokenizer_type} with vocab size {vocab_size}', 'success')
    return redirect(url_for('builder_views.tokenizer'))

@builder_views_bp.route('/define_model')
def define_model():
    return _serve_page('define_model.html')

@builder_views_bp.route('/training')
def training():
    return _serve_page('training.html')

@builder_views_bp.route('/evaluation')
def evaluation():
    return _serve_page('evaluation.html')

@builder_views_bp.route('/inference')
def inference():
    return _serve_page('inference.html')

@builder_views_bp.route('/deployment')
def deployment():
    return _serve_page('deployment.html')

@builder_views_bp.route('/uks_introduction')
def uks_introduction():
    return _serve_page('uks_introduction.html')

@builder_views_bp.route('/rule_engine')
def rule_engine():
    return _serve_page('rule_engine.html')

@builder_views_bp.route('/inheritance')
def inheritance():
    return _serve_page('inheritance.html')

@builder_views_bp.route('/unified_builder')
def unified_builder():
    return _serve_page('unified_builder.html')

@builder_views_bp.route('/configuration_interactive')
def configuration_interactive():
    return _serve_page('configuration_interactive.html')

@builder_views_bp.route('/metrics_dashboard')
def metrics_dashboard():
    return _serve_page('metrics_dashboard.html')

@builder_views_bp.route('/api_reference')
def api_reference():
    return _serve_page('api_reference.html')

@builder_views_bp.route('/documentation')
def documentation():
    return _serve_page('documentation.html')

@builder_views_bp.route('/development_roadmap')
def development_roadmap():
    return _serve_page('development_roadmap.html')

@builder_views_bp.route('/gpu_setup')
def gpu_setup():
    return _serve_page('gpu_setup.html')

@builder_views_bp.route('/model_architecture')
def model_architecture():
    return _serve_page('model_architecture.html')

@builder_views_bp.route('/checkpoint')
def checkpoint():
    return _serve_page('checkpoint.html')

@builder_views_bp.route('/chat', methods=['GET'])
def chat_view():
    return _serve_page('chat.html')
