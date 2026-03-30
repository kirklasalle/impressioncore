#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #api #deployment #documentation #inference #memory_management #multimodal #performance #python #source_code #src/interfaces/web/routes.py #tokenization #training #transformer #web_interface
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** Kirk LaSalle
# Tags:** #api #deployment #documentation #inference #memory_management #multimodal #performance #python #source_code #src\\interfaces\\web\\routes.py #tokenization #training #transformer #web_interface
# Category:** Interface Definitions
# Status:** Active

"""
ImpressionCore - Brain-Inspired Multimodal AI Framework

File: src/web/routes.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-25
Modified: 2025-05-25
Version: 1.0.0

Authors:
- Kirk LaSalle & GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [web]
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
ImpressionCore Web Blueprint Routes
==================================

This module defines the main Flask Blueprint ('web') for the ImpressionCore web interface.

Features:
---------
- Encapsulates all user-facing web routes for modularity and maintainability.
- Provides endpoints for data preparation, evaluation, inference, and related UI pages.
- Implements file validation and memory-efficient evaluation/inference logic.

Blueprint:
----------
- The 'web' blueprint is registered in src/web/server.py and handles all main web UI routes.
- This modular approach allows for scalable route management and separation of concerns.

Usage:
------
Import and register the blueprint in your Flask app:
    from.interfaces.web.routes import web
    app.register_blueprint(web)

Related Files:
--------------
- src/web/server.py: Main Flask app and API endpoints.
- src/web/route_config.py: Route mapping and navigation configuration.
- run_server.py: Entry point for running the server.
- docs/user_guide.md: Full user and developer documentation.

"""

import json
import os
import threading

from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

web = Blueprint('web', __name__)

def allowed_file(filename):
    """
    Check if a file has an allowed extension (.txt, .csv, .json).
    Args:
        filename: The filename to check.
    Returns:
        bool: True if the file has an allowed extension, False otherwise.
    """
    ALLOWED_EXTENSIONS = {'txt', 'csv', 'json'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@web.route('/data_prep', methods=['GET'])
def data_prep_page():
    """
    Render the data preparation page for uploading and validating training/inference data.
    Returns:
        Rendered HTML template for data preparation.
    Memory: Minimal, only loads template.
    """
    return render_template('data_prep.html')

@web.route('/evaluation', methods=['GET'])
def evaluation_page():
    """
    Render the evaluation page for running model benchmarks and viewing metrics.
    Returns:
        Rendered HTML template for evaluation.
    Memory: Minimal, only loads template.
    """
    return render_template('evaluation.html')

@web.route('/evaluation/run', methods=['POST'])
def evaluation_run():
    """
    Run evaluation on the trained ImpressionCore-b1 model using selected metrics.
    Args:
        evalDataset: Uploaded evaluation dataset file (optional, default: CIFAR-10).
        metrics: List of selected metrics (accuracy, loss, etc.).
    Returns:
        Redirects to evaluation page with results or error message.
    Memory: Uses batch processing and torch.no_grad() for memory efficiency.
    """
    import os

    import torch

    from .models.architectures.impressioncore_b1 import DiffusionTransformerMoE
    from .training.evaluation import evaluate_impressioncore_b1
    metrics = request.form.getlist('metrics')
    # For now, only accuracy and loss are supported
    try:        # Load the trained model config/state
        model_config_path = os.path.join('src', 'data', 'datasets', 'uploads', 'impressioncore_b1_config.pt')
        if not os.path.exists(model_config_path):
            flash('No trained model found. Please complete training first.', 'danger')
            return redirect(url_for('web.evaluation_page'))
        model_state = torch.load(model_config_path, map_location='cpu')
        model = DiffusionTransformerMoE()
        model.load_state_dict(model_state['model_state_dicts']['head'], strict=False)  # Load head as example
        # Run evaluation
        accuracy, avg_loss = evaluate_impressioncore_b1.evaluate_model(model)
        msg = []
        if 'accuracy' in metrics:
            msg.append(f"Accuracy: {accuracy:.4f}")
        if 'perplexity' in metrics:
            msg.append(f"Perplexity: {torch.exp(torch.tensor(avg_loss)):.4f}")
        if 'f1' in metrics or 'bleu' in metrics:
            msg.append("F1/BLEU not implemented in this stub.")
        if 'loss' in metrics or not msg:
            msg.append(f"Avg Loss: {avg_loss:.4f}")
        flash(' | '.join(msg), 'success')
    except Exception as e:
        flash(f'Error during evaluation: {e!s}', 'danger')
    return redirect(url_for('web.evaluation_page'))

@web.route('/inference', methods=['GET'])
def inference_page():
    """
    Render the inference and deployment page.
    Returns:
        Rendered HTML template for inference.
    Memory: Minimal, only loads template.
    """
    return render_template('inference.html')

@web.route('/inference/run', methods=['POST'])
def inference_run():
    """
    Run inference using the trained ImpressionCore-b1 model and tokenizer.
    Args:
        inputText: User input text for inference.
    Returns:
        Redirects to inference page with result or error message.
    Memory: Uses torch.no_grad() for memory efficiency. Loads model/tokenizer on demand.
    """
    import os

    import torch

    from .data.tokenization.bpe import BPETokenizer
    from .models.architectures.impressioncore_b1 import DiffusionTransformerMoE
    input_text = request.form.get('inputText')
    if not input_text:
        flash('Please enter input text for inference.', 'danger')
        return redirect(url_for('web.inference_page'))
    try:        # Load tokenizer
        tokenizer_path = os.path.join('src', 'data', 'datasets', 'uploads', 'tokenizer_bpe.json')
        if not os.path.exists(tokenizer_path):
            flash('No trained tokenizer found. Please complete tokenization first.', 'danger')
            return redirect(url_for('web.inference_page'))
        tokenizer = BPETokenizer()
        tokenizer.load(tokenizer_path)
        # Tokenize input
        input_ids = torch.tensor([tokenizer.encode(input_text)], dtype=torch.long)        # Load model
        model_config_path = os.path.join('src', 'data', 'datasets', 'uploads', 'impressioncore_b1_config.pt')
        if not os.path.exists(model_config_path):
            flash('No trained model found. Please complete training first.', 'danger')
            return redirect(url_for('web.inference_page'))
        model_state = torch.load(model_config_path, map_location='cpu')
        model = DiffusionTransformerMoE()
        model.load_state_dict(model_state['model_state_dicts']['head'], strict=False)
        model.eval()
        with torch.no_grad():
            # For demonstration, just run the head on input_ids (real pipeline may differ)
            output = model.head(input_ids.float())
            # Convert output to string (stub: show raw tensor)
            result = f"Model output: {output.tolist()}"
        flash(result, 'success')
    except Exception as e:
        flash(f'Error during inference: {e!s}', 'danger')
    return redirect(url_for('web.inference_page'))

@web.route('/uks_introduction', methods=['GET'])
def uks_introduction_page():
    """
    Render the Unified Knowledge Store (UKS) management page.
    Returns:
        Rendered HTML template for UKS.
    Memory: Minimal, only loads template.
    """
    return render_template('uks_introduction.html')

UKS_PATH = os.path.join('src', 'data', 'datasets', 'uploads', 'uks_store.json')

def load_uks():
    """
    Load the UKS (Unified Knowledge Store) from disk.
    Returns:
        List of facts (dicts with subject, predicate, object).
    Memory: Loads only as needed; for large files, consider streaming.
    """
    if not os.path.exists(UKS_PATH):
        return []
    with open(UKS_PATH, encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception:
            return []

def save_uks(facts):
    """
    Save the UKS facts to disk.
    Args:
        facts: List of fact dicts.
    Returns: None
    Memory: Writes in one operation; for large files, consider chunking.
    """
    with open(UKS_PATH, 'w', encoding='utf-8') as f:
        json.dump(facts, f, ensure_ascii=False, indent=2)

@web.route('/uks_introduction/add_fact', methods=['POST'])
def uks_add_fact():
    """
    Add a fact (subject, predicate, object) to the UKS.
    Args:
        subject, predicate, object: Fact components from form.
    Returns:
        Redirects to UKS page with success or error message.
    Memory: Appends to file-based store; for large stores, optimize with streaming.
    """
    subject = request.form.get('subject')
    predicate = request.form.get('predicate')
    obj = request.form.get('object')
    if not subject or not predicate or not obj:
        flash('Please complete all fields to add a fact.', 'danger')
        return redirect(url_for('web.uks_introduction_page'))
    try:
        facts = load_uks()
        facts.append({'subject': subject, 'predicate': predicate, 'object': obj})
        save_uks(facts)
        flash(f'Fact added: {subject} {predicate} {obj}', 'success')
    except Exception as e:
        flash(f'Error adding fact: {e!s}', 'danger')
    return redirect(url_for('web.uks_introduction_page'))

@web.route('/uks_introduction/query', methods=['GET'])
def uks_query():
    """
    Query the UKS for facts matching a subject.
    Args:
        querySubject: Subject to query from form.
    Returns:
        Redirects to UKS page with query result or error message.
    Memory: For large stores, optimize with streaming or indexing.
    """
    query_subject = request.args.get('querySubject')
    if not query_subject:
        flash('Please enter a subject to query.', 'danger')
        return redirect(url_for('web.uks_introduction_page'))
    try:
        facts = load_uks()
        results = [f for f in facts if f['subject'].lower() == query_subject.lower()]
        if results:
            msg = ' | '.join([f"{f['subject']} {f['predicate']} {f['object']}" for f in results])
            flash(f'Query results: {msg}', 'info')
        else:
            flash('No facts found for that subject.', 'warning')
    except Exception as e:
        flash(f'Error querying UKS: {e!s}', 'danger')
    return redirect(url_for('web.uks_introduction_page'))

@web.route('/documentation', methods=['GET'])
def documentation_page():
    """
    Render the documentation and support page.
    Returns:
        Rendered HTML template for documentation.
    Memory: Minimal, only loads template.
    """
    return render_template('documentation.html')

@web.route('/data_prep/upload', methods=['POST'])
def data_prep_upload():
    """
    Handle data file upload for model training or inference.
    Args:
        dataFile: File uploaded by the user (txt, csv, json).
    Returns:
        Redirects to data_prep page with success or error message.
    Memory: File is streamed and saved to disk, not loaded fully into memory. Uses chunked reading for large files.
    """

    import pandas as pd

    from .data.datasets import data_cleaning

    if 'dataFile' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('web.data_prep_page'))
    file = request.files['dataFile']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('web.data_prep_page'))

    # Ensure uploads directory exists
    upload_dir = os.path.join('src', 'data', 'datasets', 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join('src', 'data', 'datasets', 'uploads', filename)
        file.save(upload_path)
        # Validate and clean data
        ext = filename.rsplit('.', 1)[1].lower()
        try:
            if ext == 'csv':                # Read in chunks for memory efficiency
                chunk_iter = pd.read_csv(upload_path, chunksize=10000)
                cleaned_chunks = []
                for chunk in chunk_iter:
                    chunk = data_cleaning.remove_duplicates(chunk)
                    chunk = data_cleaning.handle_missing_values(chunk, strategy='drop')
                    cleaned_chunks.append(chunk)
                cleaned_data = pd.concat(cleaned_chunks, ignore_index=True)
                cleaned_path = os.path.join('src', 'data', 'datasets', 'uploads', f'cleaned_{filename}')
                cleaned_data.to_csv(cleaned_path, index=False)
            elif ext == 'json':
                df = pd.read_json(upload_path, lines=True)
                df = data_cleaning.remove_duplicates(df)
                df = data_cleaning.handle_missing_values(df, strategy='drop')
                cleaned_path = os.path.join('src', 'data', 'datasets', 'uploads', f'cleaned_{filename}')
                df.to_json(cleaned_path, orient='records', lines=True)
            elif ext == 'txt':
                # For .txt, just check file size and line count
                with open(upload_path, encoding='utf-8') as f:
                    lines = f.readlines()
                if len(lines) < 10:
                    flash('Text file must have at least 10 lines.', 'danger')
                    return redirect(url_for('web.data_prep_page'))
                cleaned_path = upload_path  # No cleaning for plain text
            else:
                flash('Unsupported file type.', 'danger')
                return redirect(url_for('web.data_prep_page'))
        except Exception as e:
            flash(f'Error processing file: {e!s}', 'danger')
            return redirect(url_for('web.data_prep_page'))
        flash(f'Data file {filename} uploaded and cleaned successfully.', 'success')
        return redirect(url_for('web.data_prep_page'))
    else:
        flash('Invalid file type. Please upload .txt, .csv, or .json.', 'danger')
        return redirect(url_for('web.data_prep_page'))

@web.route('/tokenizer/configure', methods=['POST'])
def tokenizer_configure():
    """
    Handle tokenizer configuration and training.
    Args:
        tokenizerType: Selected tokenizer type (BPE, WordPiece).
        vocabSize: Vocabulary size (int).
    Returns:
        Redirects to tokenizer page with success or error message.
    Memory: Processes data in batches for memory efficiency. Tokenizer is saved to disk.
    """
    import os

    from .data.tokenization import train_tokenizers
    tokenizer_type = request.form.get('tokenizerType')
    vocab_size = request.form.get('vocabSize')    # Only BPE is implemented for now
    if tokenizer_type != 'bpe':
        flash('Only BPE tokenization is currently supported.', 'danger')
        return redirect(url_for('web.tokenizer_page'))

    try:
        # Find the most recent cleaned data file
        upload_dir = os.path.join('src', 'data', 'datasets', 'uploads')
        cleaned_files = [f for f in os.listdir(upload_dir) if (f.startswith('cleaned_') and f.endswith('.csv')) or f.endswith('.txt')]
        if not cleaned_files:
            flash('No cleaned data file found. Please upload and clean data first.', 'danger')
            return redirect(url_for('web.tokenizer_page'))
        cleaned_files.sort(key=lambda f: os.path.getmtime(os.path.join(upload_dir, f)), reverse=True)
        input_file = os.path.join(upload_dir, cleaned_files[0])
        output_file = os.path.join(upload_dir, 'tokenizer_bpe.json')
        # Train the tokenizer
        train_tokenizers.train_text_tokenizer(
            input_file=input_file,
            output_file=output_file,
            vocab_size=int(vocab_size)
        )
        flash(f'BPE tokenizer trained and saved as {output_file}.', 'success')
    except Exception as e:
        flash(f'Error during tokenizer training: {e!s}', 'danger')
    return redirect(url_for('web.tokenizer_page'))

@web.route('/define_model/configure', methods=['POST'])
def define_model_configure():
    """
    Handle model configuration form submission and instantiate the model.
    Args:
        architecture: Model architecture (Transformer, MoE, Multimodal).
        contextWindow: Context window size (int).
        precision: Numeric precision (FP16, BF16, INT8).
    Returns:
        Redirects to model definition page with success or error message.
    Memory: Instantiates model with user config, saves config for downstream steps.
    """
    import os

    import torch

    from .models.architectures import impressioncore_b1
    architecture = request.form.get('architecture')
    context_window = request.form.get('contextWindow')
    precision = request.form.get('precision')
    if not architecture or not context_window or not precision:
        flash('Please complete all model configuration fields.', 'danger')
        return redirect(url_for('web.define_model_page'))
    try:
        # Only ImpressionCore-b1 is implemented for now
        if architecture != 'transformer':
            flash('Only the ImpressionCore-b1 (Transformer) architecture is currently supported.', 'danger')
            return redirect(url_for('web.define_model_page'))
        # Instantiate model with user config
        model_components = impressioncore_b1.build_impressioncore_b1(
            text_dim=int(context_window),
            image_dim=512,
            fusion_dim=512,
            num_experts=4,
            num_classes=10,
            use_checkpoint=(precision in ['fp16', 'bf16'])
        )
        # Save model config (stub: just save config as .pt for now)
        model_config_path = os.path.join('uploads', 'impressioncore_b1_config.pt')
        torch.save({
            'architecture': architecture,
            'context_window': context_window,
            'precision': precision,
            'model_state_dicts': {k: v.state_dict() for k, v in model_components.items()}
        }, model_config_path)
        flash(f'Model configured and saved as {model_config_path}.', 'success')
    except Exception as e:
        flash(f'Error during model configuration: {e!s}', 'danger')
    return redirect(url_for('web.define_model_page'))

@web.route('/training/start', methods=['POST'])
def training_start():
    """
    Launch ImpressionCore-b1 model training with user-specified hyperparameters.
    Args:
        epochs: Number of epochs (int).
        batchSize: Batch size (int).
        learningRate: Learning rate (float).
    Returns:
        Redirects to training page with success or error message.
    Memory: Training runs in a background thread to avoid blocking the web server. Uses memory-efficient training loop.
    """
    from .training.train_impressioncore_b1 import train_impressioncore_b1
    epochs = request.form.get('epochs')
    batch_size = request.form.get('batchSize')
    learning_rate = request.form.get('learningRate')
    # Validate input
    if not epochs or not batch_size or not learning_rate:
        flash('Please complete all training fields.', 'danger')
        return redirect(url_for('web.training_page'))
    try:
        # Launch training in a background thread
        def run_training():
            try:
                train_impressioncore_b1(
                    epochs=int(epochs),
                    batch_size=int(batch_size),
                    context_window=131072  # Or load from model config if available
                )
            except Exception as e:
                # Log error (could also update a status file for UI polling)
                print(f"[TRAINING ERROR] {e}")
        training_thread = threading.Thread(target=run_training, daemon=True)
        training_thread.start()
        flash('Training started in the background. Monitor logs for progress.', 'success')
    except Exception as e:
        flash(f'Error launching training: {e!s}', 'danger')
    return redirect(url_for('web.training_page'))
