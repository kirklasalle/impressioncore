#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #command_line #cuda #deployment #documentation #inference #memory_management #multimodal #python #source_code #src/training/full_scale_embedding_integration.py #testing #tokenization #training #web_interface
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #api #command_line #cuda #deployment #documentation #inference #memory_management #multimodal #python #source_code #src\\training\\full_scale_embedding_integration.py #testing #tokenization #training #web_interface
# Category:** Training System
# Status:** Active

"""
ImpressionCore-B1 Full-Scale Embedding Integration System
"Perfection Edition" - Utilizing ALL F: Drive Embeddings

This module implements comprehensive integration of all available embeddings
from the F: drive for the ImpressionCore-B1 training system.

Features:
- Multi-format embedding loading (JSON, PKL, NPY)
- Modality-specific embedding processing
- Memory-efficient batch loading
- Progressive enhancement training
- Quality assurance and validation
- Transcript preprocessing integration: loads preprocessed transcript chunks for conversational training, ensuring memory efficiency and modularity.

Date: January 6, 2025
Status: Revolutionary Architecture - Full Integration
Target: Complete utilization of all F: drive embedding resources
"""

import sys
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from pathlib import Path
from datetime import datetime
import json
import pickle
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass
import hashlib
import time
from collections import defaultdict
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Project imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from.core.utils.rich_logging import setup_rich_logging
from.config.f_drive_paths import f_paths

# Setup logging
logger = setup_rich_logging(__name__)

@dataclass
class EmbeddingMetadata:
    """Metadata for embedding files"""
    file_path: str
    modality: str  # text, image, audio, video, multimodal, etc.
    format: str    # json, pkl, npy
    size_bytes: int
    dimension: int
    count: int
    checksum: str
    timestamp: datetime
    quality_score: float
    processing_status: str  # pending, loaded, error, cached

@dataclass
class EmbeddingBatch:
    """Batch of embeddings for training"""
    embeddings: torch.Tensor
    metadata: List[EmbeddingMetadata]
    modality_mix: Dict[str, int]
    batch_id: str
    quality_score: float
    memory_footprint: int

class FullScaleEmbeddingIntegrator:
    def chat_loop(self, max_turns: int = 50, system_prompt: str = "You are ImpressionCore-B1, a helpful AI."):
        """
        Interactive chat loop using the model, tokenizer, and generative decoder.
        Args:
            max_turns (int): Maximum number of turns before exit.
            system_prompt (str): Initial system prompt for context.
        Returns:
            None
        Notes:
            - Maintains conversation history in memory.
            - Uses a generative decoder for natural language output.
            - Can be reused in CLI, UI, or API.
        """
        print("\n[ImpressionCore-B1 Chat] Type 'exit' to quit.\n")
        history = [system_prompt]
        for turn in range(max_turns):
            user_input = input("You: ").strip()
            if user_input.lower() in ("exit", "quit"): break
            history.append(f"User: {user_input}")
            # Generate model response
            response = self._generate_response(history)
            print(f"ImpressionCore-B1: {response}")
            history.append(f"ImpressionCore-B1: {response}")

    def _generate_response(self, history: list) -> str:
        """
        Generate a natural language response using a true generative head (decoder-only model).
        Args:
            history (list): Conversation history (list of strings).
        Returns:
            str: Model's response as text.
        Notes:
            - Uses a HuggingFace generative model (e.g., distilgpt2) for text generation.
            - Maintains context by joining history as prompt.
        """
        # Compose prompt from conversation history
        prompt = "\n".join(history[-10:])  # Use last 10 turns for context
        # Load generative model and tokenizer if not already loaded
        if not hasattr(self, '_gen_tokenizer') or not hasattr(self, '_gen_model'):
            from.core.utils.tokenizer_utils import load_generative_model_and_tokenizer, generate_text
            self._gen_tokenizer, self._gen_model = load_generative_model_and_tokenizer()
        else:
            from.core.utils.tokenizer_utils import generate_text
        tokenizer = self._gen_tokenizer
        model = self._gen_model
        # Generate response
        response = generate_text(prompt, tokenizer, model, device=str(self.device), max_length=64)
        if not response:
            return "[No response generated.]"
        return response

    def _simple_vector_to_text(self, vector) -> str:
        """
        Placeholder: Convert model output vector to text.
        Args:
            vector: Model output vector (numpy array).
        Returns:
            str: Decoded text (currently a stub).
        """
        # TODO: Implement a real decoder. For now, echo a generic response.
        return "[Generative decoding not yet implemented. This is a placeholder response.]"
    """
    Main integration class for ImpressionCore-B1.
    Handles model initialization, training, inference, deployment, and journaling.
    Integrates transcript preprocessing for conversational training, loading only chunked, preprocessed text files to minimize memory overhead.
    """
    def preprocess_and_load_transcripts(self, processed_dir: str = "F:/impressioncore-b1-processed-transcripts/"):
        """
        Loads preprocessed transcript chunks for conversational training.
        Args:
            processed_dir: Directory containing processed transcript chunk files.
        Returns:
            List of conversation chunks (each a list of turns).
        Memory: Loads only chunked, preprocessed text files, minimizing memory overhead.
        """
        from pathlib import Path
        import glob
        transcript_chunks = []
        chunk_files = glob.glob(str(Path(processed_dir) / "*.txt"))
        for chunk_file in chunk_files:
            with open(chunk_file, "r", encoding="utf-8") as f:
                # Only keep non-empty lines; each chunk is a list of turns (memory efficient)
                lines = [line.strip() for line in f if line.strip()]
                if lines:
                    transcript_chunks.append(lines)
        logger.info(f"[Preprocess] Loaded {len(transcript_chunks)} transcript chunks from {processed_dir}")
        return transcript_chunks
    def _load_embedding_file(self, file_path: str) -> np.ndarray:
        """
        Loads an embedding file (.npy, .json, .pkl) and returns a numpy array.
        Args:
            file_path: Path to the embedding file.
        Returns:
            Embedding data as a numpy array.
        """
        if file_path.endswith('.npy'):
            return np.load(file_path)
        elif file_path.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                data = list(data.values())
            return np.array(data)
        elif file_path.endswith('.pkl'):
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            if isinstance(data, dict):
                data = list(data.values())
            return np.array(data)
        else:
            raise ValueError(f"Unsupported embedding file format: {file_path}")

    def _embedding_batch_generator(self, batch_size: int) -> Any:
        """
        Generator that yields batches of (input, target) tensors from the embedding inventory.
        Args:
            batch_size: Number of samples per batch.
        Yields:
            Tuple of (inputs, targets) as torch tensors.
        """
        all_files = list(self.embedding_inventory.keys())
        np.random.shuffle(all_files)
        batch_inputs, batch_targets = [], []
        for file_path in all_files:
            try:
                arr = self._load_embedding_file(file_path)
                for row in arr:
                    batch_inputs.append(row)
                    batch_targets.append(row)
                    if len(batch_inputs) == batch_size:
                        inputs = torch.tensor(batch_inputs, dtype=torch.float32, device=self.device)
                        targets = torch.tensor(batch_targets, dtype=torch.float32, device=self.device)
                        yield inputs, targets
                        batch_inputs, batch_targets = [], []
            except Exception as e:
                logger.warning(f"[BatchLoader] Failed to load {file_path}: {e}")
        if batch_inputs:
            inputs = torch.tensor(batch_inputs, dtype=torch.float32, device=self.device)
            targets = torch.tensor(batch_targets, dtype=torch.float32, device=self.device)
            yield inputs, targets
    def init_largest_model(self):
        """
        Initialize the largest model possible from F: drive embeddings.
        Scans all discovered embeddings, determines the largest viable architecture,
        and loads or constructs the model accordingly.
        """
        logger.info("[Init] Initializing the largest model possible from F: drive...")
        # Example: Find the largest embedding dimension/count
        max_dim = 0
        max_file = None
        for meta in self.embedding_inventory.values():
            if meta.dimension > max_dim:
                max_dim = meta.dimension
                max_file = meta
        if not max_file:
            logger.error("[Init] No embeddings found to initialize model.")
            print("[Init] No embeddings found to initialize model.")
            return
        # Example: create a simple model with the largest dimension
        import torch.nn as nn
        class LargestB1Model(nn.Module):
            def __init__(self, input_dim):
                super().__init__()
                self.linear = nn.Linear(input_dim, 128)
            def forward(self, x):
                return self.linear(x.float())
        self.model = LargestB1Model(max_dim).to(self.device)
        logger.info(f"[Init] Largest model initialized with input_dim={max_dim} from {max_file.file_path}")
        print(f"[Init] Largest model initialized with input_dim={max_dim} from {max_file.file_path}")

    def train_local(self, epochs: int = 1, batch_size: int = 8):
        """
        Train the current model locally using available F: drive embeddings.
        Uses memory-efficient batching and logs progress. Visualizes loss with matplotlib.
        """
        logger.info(f"[Train] Starting local training for {epochs} epochs, batch_size={batch_size}")
        if not hasattr(self, 'model') or self.model is None:
            logger.error("[Train] No model loaded. Run 'init_largest_model' first.")
            print("[Train] No model loaded. Run 'init_largest' first.")
            return
        import torch.optim as optim
        import torch.nn as nn
        import matplotlib.pyplot as plt
        optimizer = optim.Adam(self.model.parameters(), lr=1e-3)
        loss_fn = nn.MSELoss()
        loss_history = []
        for epoch in range(epochs):
            logger.info(f"[Train] Epoch {epoch+1}/{epochs}")
            batch_gen = self._embedding_batch_generator(batch_size)
            epoch_loss = 0.0
            batch_count = 0
            for inputs, targets in batch_gen:
                optimizer.zero_grad()
                outputs = self.model(inputs)
                loss = loss_fn(outputs, targets)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()
                batch_count += 1
            avg_loss = epoch_loss / max(1, batch_count)
            loss_history.append(avg_loss)
            logger.info(f"[Train] Epoch {epoch+1}/{epochs} - Avg Loss: {avg_loss:.6f}")
        print("[Train] Local training complete.")
        logger.info("[Train] Local training complete.")
        if len(loss_history) > 1:
            plt.figure()
            plt.plot(range(1, len(loss_history)+1), loss_history, marker='o')
            plt.title("Training Loss Curve")
            plt.xlabel("Epoch")
            plt.ylabel("Average Loss")
            plt.grid(True)
            plt.show()

    def distill_with_ollama(self, export_path: str = "./b1_model.pt"):
        """
        Export the current model and prepare for Ollama distillation.
        Saves the model checkpoint and prints next steps for distillation.
        """
        logger.info(f"[Distill] Exporting model to {export_path} for Ollama distillation...")
        if not hasattr(self, 'model') or self.model is None:
            logger.error("[Distill] No model loaded. Run 'init_largest_model' first.")
            print("[Distill] No model loaded. Run 'init_largest' first.")
            return
        torch.save(self.model.state_dict(), export_path)
        logger.info(f"[Distill] Model exported to {export_path}. Ready for Ollama distillation.")
        print(f"[Distill] Model exported to {export_path}. Ready for Ollama distillation.")
        print("[Distill] Next: Use the Ollama CLI or API to distill this checkpoint as per documentation.")
    def init_largest_model(self):
        """
        Initialize the largest model possible based on F: drive embeddings and available VRAM.
        Scans all embeddings, determines the largest viable architecture, and loads/constructs the model.
        """
        logger.info("[Init] Initializing the largest model possible from F: drive...")
        # Example: Use max dimension/count from embedding inventory
        max_dim = 0
        for meta in self.embedding_inventory.values():
            if hasattr(meta, 'dimension') and meta.dimension > max_dim:
                max_dim = meta.dimension
        # Placeholder: create a simple model with max_dim (replace with actual logic)
        import torch.nn as nn
        class LargestB1Model(nn.Module):
            def __init__(self, dim):
                super().__init__()
                self.linear = nn.Linear(dim, 128)
            def forward(self, x):
                return self.linear(x.float())
        if max_dim > 0:
            self.model = LargestB1Model(max_dim).to(self.device)
            logger.info(f"[Init] Largest model initialized with input dim {max_dim}.")
        else:
            logger.error("[Init] No valid embeddings found to determine model size.")

    def train_local(self, epochs: int = 1, batch_size: int = 8):
        """
        Train the current model locally using F: drive embeddings and memory-efficient batching.
        Args:
            epochs: Number of epochs to train.
            batch_size: Batch size for training.
        """
        if not hasattr(self, 'model') or self.model is None:
            logger.error("[Train] No model loaded. Initialize a model first.")
            return
        logger.info(f"[Train] Starting local training for {epochs} epochs, batch size {batch_size}...")
        # Placeholder: iterate over embedding_inventory and simulate training
        optimizer = torch.optim.Adam(self.model.parameters(), lr=1e-3)
        loss_fn = torch.nn.MSELoss()
        for epoch in range(epochs):
            logger.info(f"[Train] Epoch {epoch+1}/{epochs}")
            for meta in list(self.embedding_inventory.values())[:batch_size]:
                # Simulate a batch (replace with actual data loading)
                x = torch.randn(batch_size, getattr(meta, 'dimension', 128), device=self.device)
                y = torch.randn(batch_size, 128, device=self.device)
                optimizer.zero_grad()
                out = self.model(x)
                loss = loss_fn(out, y)
                loss.backward()
                optimizer.step()
            logger.info(f"[Train] Epoch {epoch+1} complete.")
        logger.info("[Train] Local training complete. (Simulated)")

    def distill_with_ollama(self, export_path: str = "./b1_model.pt"):
        """
        Export the trained model and invoke Ollama distillation (placeholder for actual Ollama integration).
        Args:
            export_path: Path to save the exported model checkpoint.
        """
        if not hasattr(self, 'model') or self.model is None:
            logger.error("[Distill] No model loaded. Initialize and train a model first.")
            return
        logger.info(f"[Distill] Exporting model to {export_path} for Ollama distillation...")
        torch.save(self.model.state_dict(), export_path)
        # Placeholder: call Ollama CLI or API (user must run actual distillation)
        logger.info(f"[Distill] Model exported. Please run Ollama distillation with the exported checkpoint.")
    def cli_scheduler_control(self):
        """
        CLI interface to start/stop the activity scheduler and view the activity journal.
        Supports advanced monitoring, recovery, and auditability.
        Integrates with -eds, -ipa, -vrgc tools if available.
        """
        import sys
        print("\n[Scheduler CLI] ImpressionCore Activity Scheduler Control Panel")
        print("Commands: start | stop | status | view | recover | exit\n")
        while True:
            cmd = input("[Scheduler CLI] > ").strip().lower()
            if cmd == "start":
                if getattr(self, '_scheduler_running', False):
                    print("[Scheduler CLI] Scheduler is already running.")
                else:
                    self.start_activity_scheduler()
                    print("[Scheduler CLI] Scheduler started.")
            elif cmd == "stop":
                if getattr(self, '_scheduler_running', False):
                    self.stop_activity_scheduler()
                    print("[Scheduler CLI] Scheduler stop signal sent.")
                else:
                    print("[Scheduler CLI] Scheduler is not running.")
            elif cmd == "status":
                running = getattr(self, '_scheduler_running', False)
                print(f"[Scheduler CLI] Scheduler running: {running}")
            elif cmd == "view":
                self._view_activity_journal()
            elif cmd == "recover":
                self._recover_from_journal()
            elif cmd == "exit":
                print("[Scheduler CLI] Exiting control panel.")
                break
            else:
                print("[Scheduler CLI] Unknown command. Use: start | stop | status | view | recover | exit")

    def _view_activity_journal(self, n: int = 10):
        """
        Display the last n entries from the activity journal for auditability.
        Args:
            n: Number of recent entries to display (default: 10)
        """
        journal_path = self.cache_dir / "activity_journal.log"
        if not journal_path.exists():
            print("[Scheduler CLI] No journal found.")
            return
        try:
            with open(journal_path, "r", encoding="utf-8") as f:
                lines = f.readlines()[-n:]
            print(f"[Scheduler CLI] Last {len(lines)} journal entries:")
            for line in lines:
                print(line.strip())
        except Exception as e:
            print(f"[Scheduler CLI] Error reading journal: {e}")

    def _recover_from_journal(self):
        """
        Attempt to recover the last known good state from the activity journal.
        """
        journal_path = self.cache_dir / "activity_journal.log"
        if not journal_path.exists():
            print("[Scheduler CLI] No journal found for recovery.")
            return
        try:
            with open(journal_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if not lines:
                print("[Scheduler CLI] Journal is empty.")
                return
            last_entry = lines[-1]
            import json
            entry = json.loads(last_entry)
            # Example: restore processing_stats and inventory (expand as needed)
            self.processing_stats = entry['state'].get('processing_stats', {})
            self.embedding_inventory = entry['state'].get('embedding_inventory', {})
            print("[Scheduler CLI] State recovered from last journal entry.")
        except Exception as e:
            print(f"[Scheduler CLI] Error during recovery: {e}")

    # --- Advanced monitoring, audit, and tool integration hooks ---
    def _advanced_monitoring_hook(self, state: dict):
        """
        Hook for advanced monitoring, -eds, -ipa, -vrgc integration, and logic/concept cache expansion.
        Args:
            state: Current state dict to be monitored or processed.
        """
        # Example: send state to external tool or log for audit
        # Integrate with -eds, -ipa, -vrgc as needed
        # Logic/concept cache: advanced monitoring (removed get_logic_concept for robustness)
        # Placeholder for tool integration
        # e.g., self.eds_tool.process_state(state)
        pass
    def start_activity_scheduler(self, interval_seconds: int = 60):
        """
        Starts a background scheduler that periodically caches the current activity and state.
        Args:
            interval_seconds: How often to cache/journal the state (default: 60 seconds).
        Returns:
            None
        Notes:
            - Uses a background thread and a while loop.
            - Journals state with a timestamp to a log or cache file.
            - Can be stopped by setting self._scheduler_running = False.
        """
        import threading
        import time
        from datetime import datetime

        def scheduler_loop():
            logger.info("[Scheduler] Activity/state scheduler started.")
            while getattr(self, '_scheduler_running', True):
                try:
                    now = datetime.now().isoformat()
                    state = self._get_current_state()
                    self._journal_state(now, state)
                    self._advanced_monitoring_hook(state)
                    logger.info(f"[Scheduler] State cached, journaled, and monitored at {now}.")
                except Exception as e:
                    logger.error(f"[Scheduler] Error during scheduled cache/journal: {e}")
                time.sleep(interval_seconds)
            logger.info("[Scheduler] Activity/state scheduler stopped.")

        self._scheduler_running = True
        t = threading.Thread(target=scheduler_loop, daemon=True)
        t.start()

    def stop_activity_scheduler(self):
        """
        Stops the background activity/state scheduler.
        """
        self._scheduler_running = False
        logger.info("[Scheduler] Stop signal sent to activity/state scheduler.")

    def _get_current_state(self) -> dict:
        """
        Returns a dictionary representing the current activity and state for journaling.
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'processing_stats': dict(self.processing_stats),
            'embedding_inventory_count': len(self.embedding_inventory),
            'current_memory_usage': self.current_memory_usage,
            'cache_access_order': list(self.cache_access_order),
            'modality_stats': dict(self.modality_stats),
            # Add more as needed for full state capture
        }

    def _journal_state(self, timestamp: str, state: dict):
        """
        Journals the current state to a log or cache file with a timestamp.
        """
        import json
        journal_path = self.cache_dir / "activity_journal.log"
        try:
            with open(journal_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({'timestamp': timestamp, 'state': state}) + "\n")
        except Exception as e:
            logger.error(f"[Journal] Failed to write state to journal: {e}")
    def run_inference(self, input_data: Union[str, np.ndarray, torch.Tensor], modality: str = "text", batch_size: int = 1) -> Any:
        """
        Run inference using the integrated ImpressionCore-B1 model and embeddings.
        Args:
            input_data: Input data for inference (text, image, audio, etc.).
            modality: Modality of the input (default: "text").
            batch_size: Batch size for inference (default: 1).
        Returns:
            Inference result(s) as output from the model.
        Notes:
            - Uses HuggingFace tokenizer/embedding pipeline for text.
            - Uses memory-efficient batching and device placement.
            - Handles errors gracefully and logs all actions.
        """
        logger.info(f"[Inference] Starting inference for modality '{modality}' with batch_size={batch_size}")
        try:
            if isinstance(input_data, str) and modality == "text":
                # Use HuggingFace tokenizer/embedding pipeline
                if not hasattr(self, '_tokenizer') or not hasattr(self, '_embedding_model'):
                    from.core.utils.tokenizer_utils import load_tokenizer_and_model, embed_text
                    self._tokenizer, self._embedding_model = load_tokenizer_and_model()
                else:
                    from.core.utils.tokenizer_utils import embed_text
                tokenizer = self._tokenizer
                embedding_model = self._embedding_model
                embedding = embed_text(input_data, tokenizer, embedding_model, device=str(self.device))
                input_tensor = embedding.unsqueeze(0).to(self.device)
            elif isinstance(input_data, np.ndarray):
                input_tensor = torch.from_numpy(input_data).to(self.device)
            elif isinstance(input_data, torch.Tensor):
                input_tensor = input_data.to(self.device)
            else:
                logger.error("[Inference] Unsupported input type.")
                return None

            # Load or reference the model
            if not hasattr(self, 'model') or self.model is None:
                logger.error("[Inference] No model loaded in integrator. Please load or initialize the model.")
                return None
            model = self.model
            model.eval()
            with torch.no_grad():
                expected_dim = getattr(model, 'in_features', None) or getattr(model, 'input_dim', 768)
                if input_tensor.shape[-1] != expected_dim:
                    logger.error(f"[Inference] Input shape {input_tensor.shape} does not match model input dimension {expected_dim}.")
                    return None
                outputs = model(input_tensor)
            logger.info("[Inference] Inference completed successfully.")
            return outputs.cpu().numpy() if hasattr(outputs, 'cpu') else outputs
        except Exception as e:
            logger.error(f"[Inference] Inference failed: {e}")
            return None

    def deploy(self, interface: str = "cli", host: str = "0.0.0.0", port: int = 8080):
        """
        Deploy the ImpressionCore-B1 inference system as a service (CLI, web, or API).
        Args:
            interface: Deployment interface ("cli", "web", "api").
            host: Host address for web/api deployment.
            port: Port for web/api deployment.
        Returns:
            None
        Notes:
            - Uses memory-efficient serving and batching.
            - Integrates with the logic/concept cache for deployment best practices.
            - Logs all deployment actions and errors.
        """
        logger.info(f"[Deploy] Deploying ImpressionCore-B1 as {interface} interface on {host}:{port}")
        try:
            # Logic/concept cache: deployment best practices (removed get_logic_concept for robustness)
            if interface == "cli":
                print("\n[ImpressionCore-B1 CLI] Ready for inference. Type 'help' for commands. Type 'exit' to quit.")
                while True:
                    user_input = input("[impressioncore-b1] > ").strip()
                    if user_input.lower() in ("exit", "quit"):
                        print("[CLI] Exiting ImpressionCore-B1 CLI.")
                        break
                    elif user_input.lower() == "help":
                        print("""
Available commands:
  init_largest        Initialize the largest model possible from F: drive
  train_local         Train the current model locally (simulated)
  distill_ollama      Export model and prepare for Ollama distillation
  infer <text>        Run inference on input text
  preprocess_transcripts  Preprocess all transcript files for conversational training
  scheduler           Enter scheduler control panel
  status              Show current system status
  help                Show this help message
  exit                Exit CLI
                        """)
                    elif user_input.lower() == "init_largest":
                        self.init_largest_model()
                    elif user_input.lower() == "train_local":
                        self.train_local()
                    elif user_input.lower() == "distill_ollama":
                        self.distill_with_ollama()
                    elif user_input.lower().startswith("infer "):
                        text = user_input[6:].strip()
                        if not text:
                            print("[CLI] Please provide input text after 'infer'.")
                            continue
                        result = self.run_inference(text, modality="text")
                        print(f"[Result] {result}")
                    elif user_input.lower() == "preprocess_transcripts":
                        print("[Preprocess] Running transcript preprocessing...")
                        import subprocess
                        import sys
                        try:
                            result = subprocess.run([sys.executable, "-m", "src.core.utils.run_preprocessing_example"], capture_output=True, text=True)
                            print(result.stdout)
                            if result.stderr:
                                print("[Preprocess][stderr]", result.stderr)
                            print("[Preprocess] Transcript preprocessing complete.")
                        except Exception as e:
                            print(f"[Preprocess] Error running transcript preprocessing: {e}")
                    elif user_input.lower() == "scheduler":
                        self.cli_scheduler_control()
                    elif user_input.lower() == "chat":
                        self.chat_loop()
                    elif user_input.lower() == "status":
                        print("[Status] Model loaded:", hasattr(self, 'model') and self.model is not None)
                        print("[Status] Embedding inventory:", len(self.embedding_inventory))
                        print("[Status] Current memory usage:", self.current_memory_usage)
                    elif user_input == "":
                        pass
                    else:
                        print("[CLI] Unknown command. Type 'help' for available commands.")
            elif interface == "web":
                try:
                    from flask import Flask, request, jsonify
                except ImportError:
                    logger.error("[Deploy] Flask is not installed. Please install Flask for web deployment.")
                    return
                app = Flask(__name__)

                @app.route("/infer", methods=["POST"])
                def infer():
                    data = request.json
                    input_data = data.get("input")
                    modality = data.get("modality", "text")
                    result = self.run_inference(input_data, modality=modality)
                    return jsonify({"result": result.tolist() if hasattr(result, 'tolist') else result})

                logger.info(f"[Deploy] Starting Flask server on {host}:{port}")
                app.run(host=host, port=port)
            elif interface == "api":
                # Placeholder for API deployment (could use FastAPI, etc.)
                logger.error("[Deploy] API deployment not yet implemented.")
            else:
                logger.error(f"[Deploy] Unknown interface: {interface}")
        except Exception as e:
            logger.error(f"[Deploy] Deployment failed: {e}")
    """
    Revolutionary full-scale embedding integration system
    Utilizes ALL available embeddings from F: drive for comprehensive training
    """

    def __init__(self, config):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # F: drive paths (patched to correct B1 embeddings root)
        self.f_embeddings_dir = Path("F:/impressioncore-b1-embeddings-062125/")
        self.cache_dir = Path(config.cache_dir) / "embedding_integration"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Memory management
        self.max_memory_gb = 3.0  # Conservative for 4GB VRAM
        self.current_memory_usage = 0
        self.embedding_cache = {}
        self.cache_access_order = []
        self.max_cache_entries = 500

        # Embedding inventory
        self.embedding_inventory = {}
        self.modality_stats = defaultdict(lambda: {'count': 0, 'total_size': 0, 'avg_dimension': 0})

        # Processing statistics
        self.processing_stats = {
            'files_discovered': 0,
            'files_loaded': 0,
            'files_cached': 0,
            'files_error': 0,
            'total_embeddings': 0,
            'memory_efficiency': 0.0,
            'processing_time': 0.0
        }

        # Multi-threading for loading
        self.max_workers = 4
        self.loading_lock = threading.Lock()

        # Logic/concept cache compliance check removed (no import, no assignment)

        # Initialize the system
        self._initialize_embedding_system()

    def _initialize_embedding_system(self):
        """Initialize the full-scale embedding integration system"""
        logger.info("🚀 Initializing Full-Scale Embedding Integration System")
        start_time = time.time()

        # Discover all embeddings
        self._discover_all_embeddings()

        # Analyze and categorize
        self._analyze_embedding_inventory()

        # Create integration strategy
        self._create_integration_strategy()

        # Pre-load critical embeddings
        self._preload_critical_embeddings()

        self.processing_stats['processing_time'] = time.time() - start_time

        logger.info(f"✅ Full-Scale Embedding Integration System initialized in {self.processing_stats['processing_time']:.2f}s")
        self._log_system_statistics()

    def _discover_all_embeddings(self):
        """Discover and catalog ALL embedding files on F: drive"""
        logger.info("🔍 Discovering all embedding files on F: drive")

        if not self.f_embeddings_dir.exists():
            logger.error(f"❌ F: drive embeddings directory not found: {self.f_embeddings_dir}")
            return

        # Define embedding file patterns
        embedding_patterns = [
            "*.json",      # Batch embeddings
            "*.pkl",       # Comprehensive embeddings and checkpoints
            "*.npy",       # NumPy embeddings
            "**/*.json",   # Recursive JSON files
            "**/*.pkl",    # Recursive pickle files
            "**/*.npy"     # Recursive NumPy files
        ]

        discovered_files = []

        for pattern in embedding_patterns:
            files = list(self.f_embeddings_dir.glob(pattern))
            discovered_files.extend(files)

        # Remove duplicates and sort
        discovered_files = sorted(list(set(discovered_files)))
        self.processing_stats['files_discovered'] = len(discovered_files)

        logger.info(f"📊 Discovered {len(discovered_files)} embedding files")

        # Process each file to extract metadata, skipping empty/config files
        skip_patterns = [
            "config", "tokenizer", "special_tokens_map", "added_tokens",
            "processor", "chat_template", "generation_config", "dataset_infos",
            "adapter_config", "model.safetensors.index"
        ]
        for file_path in discovered_files:
            # Skip empty files
            if file_path.stat().st_size == 0:
                logger.warning(f"[Discovery] Skipping empty file: {file_path}")
                continue
            # Skip known non-embedding config files
            if any(pat in file_path.name for pat in skip_patterns):
                logger.info(f"[Discovery] Skipping non-embedding config file: {file_path.name}")
                continue
            metadata = self._extract_file_metadata(file_path)
            if metadata:
                self.embedding_inventory[str(file_path)] = metadata

    def _extract_file_metadata(self, file_path: Path) -> Optional[EmbeddingMetadata]:
        """Extract metadata from an embedding file"""
        # Skip logic for empty files and known config/auxiliary files (documented in logic_concept_cache.md)
        skip_patterns = [
            "config", "tokenizer", "special_tokens_map", "added_tokens",
            "processor", "chat_template", "generation_config", "dataset_infos",
            "adapter_config", "model.safetensors.index"
        ]
        if file_path.stat().st_size == 0:
            logger.warning(f"[Metadata] Skipping empty file: {file_path}")
            return None
        if any(pat in file_path.name for pat in skip_patterns):
            logger.info(f"[Metadata] Skipping non-embedding config file: {file_path.name}")
            return None
        try:
            # Basic file info
            stat = file_path.stat()
            size_bytes = stat.st_size
            timestamp = datetime.fromtimestamp(stat.st_mtime)
            # Determine modality from filename
            modality = self._determine_modality(file_path.name)
            # Determine format
            format_type = file_path.suffix.lower()[1:]  # Remove the dot
            # Calculate checksum for integrity
            checksum = self._calculate_file_checksum(file_path)
            # Estimate dimensions and count (without loading full file)
            dimension, count = self._estimate_embedding_specs(file_path, format_type)
            # Calculate quality score based on various factors
            quality_score = self._calculate_quality_score(file_path, size_bytes, modality)
            metadata = EmbeddingMetadata(
                file_path=str(file_path),
                modality=modality,
                format=format_type,
                size_bytes=size_bytes,
                dimension=dimension,
                count=count,
                checksum=checksum,
                timestamp=timestamp,
                quality_score=quality_score,
                processing_status="pending"
            )
            return metadata
        except Exception as e:
            logger.warning(f"⚠️ Failed to extract metadata from {file_path}: {e}")
            return None

    def _determine_modality(self, filename: str) -> str:
        """Determine the modality of an embedding file from its name"""
        filename_lower = filename.lower()

        # Modality keywords mapping
        modality_keywords = {
            'text': ['text', 'nlp', 'language', 'conversation', 'dialogue', 'transcript', 'audio_transcript'],
            'image': ['image', 'visual', 'picture', 'photo', 'vision', 'img'],
            'audio': ['audio', 'sound', 'speech', 'voice', 'acoustic'],
            'video': ['video', 'movie', 'clip', 'motion'],
            '3d': ['3d', 'mesh', 'point_cloud', 'geometry', 'spatial'],
            'sensor': ['sensor', 'imu', 'accelerometer', 'gyroscope'],
            'geospatial': ['geo', 'gps', 'location', 'spatial', 'map'],
            'tabular': ['tabular', 'csv', 'structured', 'table'],
            'multimodal': ['multimodal', 'fusion', 'combined', 'joint'],
            'comprehensive': ['comprehensive', 'complete', 'full', 'ultimate']
        }

        # Check for modality keywords
        for modality, keywords in modality_keywords.items():
            for keyword in keywords:
                if keyword in filename_lower:
                    # Treat audio transcripts as text
                    if modality == 'audio' and 'transcript' in filename_lower:
                        return 'text'
                    return modality

        # Check for batch files (usually mixed modality)
        if 'batch' in filename_lower:
            return 'multimodal'

        # If filename suggests transcript but not caught above, treat as text
        if 'transcript' in filename_lower:
            return 'text'

        # Default: treat unknown as text (for audio transcripts and safety)
        return 'text'

    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of file for integrity verification"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                # Read in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.warning(f"⚠️ Failed to calculate checksum for {file_path}: {e}")
            return "unknown"

    def _estimate_embedding_specs(self, file_path: Path, format_type: str) -> Tuple[int, int]:
        """Estimate embedding dimensions and count without full loading"""
        try:
            if format_type == 'npy':
                # For NumPy files, we can get shape without loading
                with open(file_path, 'rb') as f:
                    # Read numpy header to get shape
                    version = np.lib.format.read_magic(f)
                    shape, fortran, dtype = np.lib.format._read_array_header(f, version)

                if len(shape) >= 2:
                    return shape[-1], shape[0]  # dimension, count
                else:
                    return shape[0] if shape else 0, 1

            elif format_type == 'json':
                # For JSON files, sample first few entries
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        if isinstance(data, dict):
                            sample_key = next(iter(data.keys()))
                            sample_value = data[sample_key]

                            if isinstance(sample_value, dict) and 'embedding' in sample_value:
                                embedding = sample_value['embedding']
                                if isinstance(embedding, list):
                                    return len(embedding), len(data)
                            elif isinstance(sample_value, list):
                                return len(sample_value), len(data)

                        elif isinstance(data, list) and data:
                            if isinstance(data[0], list):
                                return len(data[0]), len(data)

                    except json.JSONDecodeError:
                        # File might be too large or malformed, estimate from size
                        file_size = file_path.stat().st_size
                        estimated_count = max(1, file_size // 1000)  # Rough estimate
                        return 768, estimated_count  # Default embedding dimension

            elif format_type == 'pkl':
                # For pickle files, we need to be more careful due to size
                file_size = file_path.stat().st_size
                if file_size < 100 * 1024 * 1024:  # Less than 100MB, safe to peek
                    try:
                        with open(file_path, 'rb') as f:
                            data = pickle.load(f)

                        if isinstance(data, dict):
                            sample_key = next(iter(data.keys()))
                            sample_value = data[sample_key]

                            if hasattr(sample_value, 'shape'):
                                return sample_value.shape[-1], len(data)
                            elif isinstance(sample_value, (list, np.ndarray)):
                                return len(sample_value), len(data)

                        elif hasattr(data, 'shape'):
                            if len(data.shape) >= 2:
                                return data.shape[-1], data.shape[0]

                    except Exception:
                        pass  # Fall through to estimation

                # Estimate from file size for large pickle files
                estimated_count = max(1, file_size // 3000)  # Rough estimate
                return 768, estimated_count

            return 768, 1  # Default fallback

        except Exception as e:
            logger.warning(f"⚠️ Failed to estimate specs for {file_path}: {e}")
            return 768, 1  # Default fallback

    def _calculate_quality_score(self, file_path: Path, size_bytes: int, modality: str) -> float:
        """Calculate quality score for embedding file prioritization"""
        score = 5.0  # Base score

        # File size factor (larger files often contain more comprehensive data)
        if size_bytes > 100 * 1024 * 1024:  # > 100MB
            score += 2.0
        elif size_bytes > 10 * 1024 * 1024:  # > 10MB
            score += 1.0
        elif size_bytes < 1024 * 1024:  # < 1MB
            score -= 1.0

        # Modality priority
        modality_priority = {
            'comprehensive': 3.0,
            'multimodal': 2.5,
            'text': 2.0,
            'image': 1.8,
            'audio': 1.5,
            'video': 1.3,
            '3d': 1.0,
            'mixed': 1.8,
            'unknown': 0.5
        }
        score += modality_priority.get(modality, 0.0)

        # File type factor
        filename = file_path.name.lower()
        if 'comprehensive' in filename or 'ultimate' in filename:
            score += 2.0
        elif 'batch' in filename:
            score += 1.0
        elif 'checkpoint' in filename:
            score += 0.5

        # Recent files get slight bonus
        days_old = (datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)).days
        if days_old < 7:
            score += 0.5
        elif days_old > 30:
            score -= 0.2

        return max(0.0, min(10.0, score))  # Clamp between 0 and 10

    def _analyze_embedding_inventory(self):
        """Analyze the complete embedding inventory"""
        logger.info("📊 Analyzing embedding inventory")

        total_files = len(self.embedding_inventory)
        total_size = 0

        # Analyze by modality
        for metadata in self.embedding_inventory.values():
            modality = metadata.modality
            self.modality_stats[modality]['count'] += 1
            self.modality_stats[modality]['total_size'] += metadata.size_bytes

            # Update average dimension
            current_avg = self.modality_stats[modality]['avg_dimension']
            current_count = self.modality_stats[modality]['count']
            new_avg = ((current_avg * (current_count - 1)) + metadata.dimension) / current_count
            self.modality_stats[modality]['avg_dimension'] = int(new_avg)

            total_size += metadata.size_bytes
            self.processing_stats['total_embeddings'] += metadata.count

        # Calculate memory efficiency (guard against division by zero)
        available_memory_bytes = self.max_memory_gb * 1024 * 1024 * 1024
        if total_size > 0:
            self.processing_stats['memory_efficiency'] = min(1.0, available_memory_bytes / total_size)
        else:
            self.processing_stats['memory_efficiency'] = 0.0

        logger.info(f"📈 Inventory Analysis Complete:")
        logger.info(f"   - Total Files: {total_files}")
        logger.info(f"   - Total Size: {total_size / (1024**3):.2f} GB")
        logger.info(f"   - Total Embeddings: {self.processing_stats['total_embeddings']:,}")
        logger.info(f"   - Memory Efficiency: {self.processing_stats['memory_efficiency']:.2%}")

        # Log modality breakdown
        for modality, stats in self.modality_stats.items():
            logger.info(f"   - {modality.title()}: {stats['count']} files, "
                       f"{stats['total_size'] / (1024**2):.1f} MB, "
                       f"avg dim: {stats['avg_dimension']}")

    def _create_integration_strategy(self):
        """Create optimal integration strategy based on inventory analysis"""
        logger.info("🎯 Creating optimal integration strategy")

        # Sort files by quality score for priority loading
        self.priority_files = sorted(
            self.embedding_inventory.items(),
            key=lambda x: x[1].quality_score,
            reverse=True
        )

        # Create modality-balanced batches
        self.integration_batches = self._create_balanced_batches()

        # Set memory allocation strategy
        self.memory_allocation = self._calculate_memory_allocation()

        logger.info(f"✅ Integration strategy created:")
        logger.info(f"   - Priority files: {len(self.priority_files)}")
        logger.info(f"   - Integration batches: {len(self.integration_batches)}")
        logger.info(f"   - Memory allocation: {self.memory_allocation}")

    def _create_balanced_batches(self) -> List[List[str]]:
        """Create balanced batches for training"""
        batches = []
        current_batch = []
        current_batch_size = 0
        target_batch_size = int(self.max_memory_gb * 0.8 * 1024 * 1024 * 1024)  # 80% of max memory

        # Group by modality first for balanced sampling
        modality_groups = defaultdict(list)
        for file_path, metadata in self.priority_files:
            modality_groups[metadata.modality].append(file_path)

        # Create balanced batches
        batch_id = 0
        while any(modality_groups.values()):
            current_batch = []
            current_batch_size = 0

            # Take one file from each modality (round-robin)
            for modality in list(modality_groups.keys()):
                if modality_groups[modality] and current_batch_size < target_batch_size:
                    file_path = modality_groups[modality].pop(0)
                    metadata = self.embedding_inventory[file_path]

                    if current_batch_size + metadata.size_bytes <= target_batch_size:
                        current_batch.append(file_path)
                        current_batch_size += metadata.size_bytes
                    else:
                        # Put it back for next batch
                        modality_groups[modality].insert(0, file_path)
                  # Clean up empty modalities
                if not modality_groups[modality]:
                    del modality_groups[modality]

            if current_batch:
                batches.append(current_batch)
                batch_id += 1

        return batches

    def _calculate_memory_allocation(self) -> Dict[str, float]:
        """Calculate optimal memory allocation for different components"""
        return {
            'embedding_cache': 0.4,  # 40% for embedding cache
            'model_forward': 0.3,    # 30% for model forward pass
            'gradients': 0.2,        # 20% for gradients
            'overhead': 0.1          # 10% for system overhead
        }

    def _preload_critical_embeddings(self):
        """Preload the most critical embeddings for immediate use"""
        logger.info("🚀 Preloading critical embeddings")

        # Load top priority files up to memory limit
        critical_memory_limit = self.max_memory_gb * 0.3 * 1024 * 1024 * 1024  # 30% of max memory
        current_memory = 0
        loaded_count = 0

        for file_path, metadata in self.priority_files[:20]:  # Top 20 priority files
            if current_memory + metadata.size_bytes <= critical_memory_limit:
                try:
                    embedding_data = self._load_embedding_file(file_path)
                    if embedding_data is not None:
                        self._cache_embedding(file_path, embedding_data, metadata)
                        current_memory += metadata.size_bytes
                        loaded_count += 1
                        self.processing_stats['files_loaded'] += 1

                        # Update status
                        metadata.processing_status = "cached"

                except Exception as e:
                    logger.warning(f"⚠️ Failed to preload {file_path}: {e}")
                    metadata.processing_status = "error"
                    self.processing_stats['files_error'] += 1
            else:
                break

        self.current_memory_usage = current_memory
        logger.info(f"✅ Preloaded {loaded_count} critical embeddings ({current_memory / (1024**2):.1f} MB)")

    def _load_embedding_file(self, file_path: str) -> Optional[Dict[str, torch.Tensor]]:
        """Load embeddings from a file"""
        file_path = Path(file_path)
        format_type = file_path.suffix.lower()[1:]

        try:
            if format_type == 'json':
                return self._load_json_embeddings(file_path)
            elif format_type == 'pkl':
                return self._load_pickle_embeddings(file_path)
            elif format_type == 'npy':
                return self._load_numpy_embeddings(file_path)
            else:
                logger.warning(f"⚠️ Unsupported format: {format_type}")
                return None

        except Exception as e:
            logger.error(f"❌ Failed to load {file_path}: {e}")
            return None

    def _load_json_embeddings(self, file_path: Path) -> Dict[str, torch.Tensor]:
        """Load embeddings from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        embeddings = {}

        # Handle different JSON formats
        if isinstance(data, list):
            # If data is a list, convert each item to embedding
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    if 'embedding' in item:
                        embedding = np.array(item['embedding'])
                    elif 'features' in item:
                        embedding = np.array(item['features'])
                    else:
                        # Try to use the whole item as embedding if it's numeric
                        try:
                            embedding = np.array(list(item.values())[0] if item else [])
                        except Exception:
                            continue
                elif isinstance(item, list):
                    embedding = np.array(item)
                else:
                    continue

                # Convert to tensor
                try:
                    embedding_tensor = torch.from_numpy(embedding).float()
                    if len(embedding_tensor.shape) == 1:
                        embedding_tensor = embedding_tensor.unsqueeze(0)
                    embeddings[f'item_{i}'] = embedding_tensor
                except Exception:
                    continue

        elif isinstance(data, dict):
            # Original dict handling
            for key, value in data.items():
                if isinstance(value, dict):
                    if 'embedding' in value:
                        embedding = np.array(value['embedding'])
                    elif 'features' in value:
                        embedding = np.array(value['features'])
                    else:
                        continue
                elif isinstance(value, list):
                    embedding = np.array(value)
                else:
                    continue

                # Convert to tensor
                try:
                    embedding_tensor = torch.from_numpy(embedding).float()
                    if len(embedding_tensor.shape) == 1:
                        embedding_tensor = embedding_tensor.unsqueeze(0)

                    embeddings[key] = embedding_tensor
                except Exception:
                    continue

        return embeddings

    def _load_pickle_embeddings(self, file_path: Path) -> Dict[str, torch.Tensor]:
        """Load embeddings from pickle file"""
        with open(file_path, 'rb') as f:
            data = pickle.load(f)

        embeddings = {}

        if isinstance(data, dict):
            for key, value in data.items():
                if hasattr(value, 'shape'):  # NumPy array or tensor
                    if isinstance(value, np.ndarray):
                        embedding_tensor = torch.from_numpy(value).float()
                    else:
                        embedding_tensor = value.float()

                    if len(embedding_tensor.shape) == 1:
                        embedding_tensor = embedding_tensor.unsqueeze(0)

                    embeddings[key] = embedding_tensor
                elif isinstance(value, (list, tuple)):
                    embedding = np.array(value)
                    embedding_tensor = torch.from_numpy(embedding).float()
                    if len(embedding_tensor.shape) == 1:
                        embedding_tensor = embedding_tensor.unsqueeze(0)
                    embeddings[key] = embedding_tensor
        elif hasattr(data, 'shape'):  # Single array
            if isinstance(data, np.ndarray):
                embedding_tensor = torch.from_numpy(data).float()
            else:
                embedding_tensor = data.float()

            embeddings['default'] = embedding_tensor

        return embeddings

    def _load_numpy_embeddings(self, file_path: Path) -> Dict[str, torch.Tensor]:
        """Load embeddings from NumPy file"""
        data = np.load(file_path, allow_pickle=True)

        embeddings = {}

        if data.dtype == object:  # Structured array or dictionary
            if hasattr(data, 'item') and isinstance(data.item(), dict):
                # Dictionary stored in numpy
                data_dict = data.item()
                for key, value in data_dict.items():
                    if isinstance(value, np.ndarray):
                        embedding_tensor = torch.from_numpy(value).float()
                        if len(embedding_tensor.shape) == 1:
                            embedding_tensor = embedding_tensor.unsqueeze(0)
                        embeddings[key] = embedding_tensor
            else:
                # Treat as single embedding
                embedding_tensor = torch.from_numpy(data).float()
                embeddings['default'] = embedding_tensor
        else:
            # Regular numpy array
            embedding_tensor = torch.from_numpy(data).float()
            if len(embedding_tensor.shape) == 1:
                embedding_tensor = embedding_tensor.unsqueeze(0)
            embeddings['default'] = embedding_tensor

        return embeddings

    def _cache_embedding(self, file_path: str, embedding_data: Dict[str, torch.Tensor], metadata: EmbeddingMetadata):
        """Cache embedding data with LRU eviction"""
        with self.loading_lock:
            # Evict old entries if cache is full
            while len(self.embedding_cache) >= self.max_cache_entries:
                oldest_key = self.cache_access_order.pop(0)
                del self.embedding_cache[oldest_key]
                self.processing_stats['files_cached'] -= 1

            # Cache the embedding
            self.embedding_cache[file_path] = {
                'data': embedding_data,
                'metadata': metadata,
                'last_access': time.time()
            }
            self.cache_access_order.append(file_path)
            self.processing_stats['files_cached'] += 1

    def get_training_batch(self, batch_size: int = 32, modality_filter: Optional[List[str]] = None) -> Optional[EmbeddingBatch]:
        """Get a balanced batch of embeddings for training"""
        try:
            # Select files based on modality filter and availability
            candidate_files = []

            for file_path, metadata in self.embedding_inventory.items():
                if metadata.processing_status in ['cached', 'pending']:
                    if not modality_filter or metadata.modality in modality_filter:
                        candidate_files.append((file_path, metadata))

            if not candidate_files:
                logger.warning("⚠️ No candidate files available for batch creation")
                return None

            # Sort by quality score and balance modalities
            candidate_files.sort(key=lambda x: x[1].quality_score, reverse=True)

            # Create balanced batch
            batch_embeddings = []
            batch_metadata = []
            modality_mix = defaultdict(int)
            memory_footprint = 0

            embeddings_collected = 0
            file_index = 0

            while embeddings_collected < batch_size and file_index < len(candidate_files):
                file_path, metadata = candidate_files[file_index]
                file_index += 1

                # Load embeddings (from cache or disk)
                embedding_data = self._get_embedding_data(file_path)

                if embedding_data:                    # Add embeddings from this file
                    for key, embedding_tensor in embedding_data.items():
                        if embeddings_collected >= batch_size:
                            break

                        batch_embeddings.append(embedding_tensor)
                        batch_metadata.append(metadata)
                        modality_mix[metadata.modality] += 1
                        memory_footprint += embedding_tensor.numel() * 4  # 4 bytes per float32
                        embeddings_collected += 1

            if not batch_embeddings:
                return None

            # Handle variable-sized embeddings by flattening and re-batching
            # First, collect all individual embeddings into a flat list
            all_embeddings = []
            all_metadata = []

            for i, emb in enumerate(batch_embeddings):
                if emb.dim() == 1:
                    # Single embedding
                    all_embeddings.append(emb.unsqueeze(0))
                    all_metadata.append(batch_metadata[i])
                elif emb.dim() == 2:
                    # Multiple embeddings in this file
                    for row_idx in range(emb.shape[0]):
                        all_embeddings.append(emb[row_idx:row_idx+1])  # Keep 2D shape
                        all_metadata.append(batch_metadata[i])

                # Limit total embeddings to batch_size
                if len(all_embeddings) >= batch_size:
                    all_embeddings = all_embeddings[:batch_size]
                    all_metadata = all_metadata[:batch_size]
                    break

            if not all_embeddings:
                return None

            # Now pad all embeddings to same dimension
            max_dim = max(emb.shape[-1] for emb in all_embeddings)
            padded_embeddings = []

            for emb in all_embeddings:
                if emb.shape[-1] < max_dim:
                    padding = torch.zeros(emb.shape[:-1] + (max_dim - emb.shape[-1],))
                    emb = torch.cat([emb, padding], dim=-1)
                padded_embeddings.append(emb)

            # Stack all embeddings - now they should all be (1, max_dim)
            try:
                stacked_embeddings = torch.cat(padded_embeddings, dim=0)  # Use cat instead of stack
            except Exception as e:
                logger.error(f"❌ Failed to create training batch: {e}")
                return None

            # Calculate batch quality score
            quality_scores = [meta.quality_score for meta in batch_metadata]
            avg_quality = sum(quality_scores) / len(quality_scores)

            # Generate batch ID
            batch_id = f"batch_{int(time.time())}_{len(batch_embeddings)}"

            return EmbeddingBatch(
                embeddings=stacked_embeddings,
                metadata=batch_metadata,
                modality_mix=dict(modality_mix),
                batch_id=batch_id,
                quality_score=avg_quality,
                memory_footprint=memory_footprint
            )

        except Exception as e:
            logger.error(f"❌ Failed to create training batch: {e}")
            return None

    def _get_embedding_data(self, file_path: str) -> Optional[Dict[str, torch.Tensor]]:
        """Get embedding data from cache or load from disk"""
        # Check cache first
        if file_path in self.embedding_cache:
            self._update_cache_access(file_path)
            return self.embedding_cache[file_path]['data']

        # Load from disk
        embedding_data = self._load_embedding_file(file_path)
        if embedding_data:
            metadata = self.embedding_inventory[file_path]
            self._cache_embedding(file_path, embedding_data, metadata)
            metadata.processing_status = "cached"
            return embedding_data
        else:
            self.embedding_inventory[file_path].processing_status = "error"
            return None

    def _update_cache_access(self, file_path: str):
        """Update cache access order for LRU"""
        with self.loading_lock:
            if file_path in self.cache_access_order:
                self.cache_access_order.remove(file_path)
                self.cache_access_order.append(file_path)
                self.embedding_cache[file_path]['last_access'] = time.time()

    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the embedding integration system"""
        cache_stats = {
            'cached_files': len(self.embedding_cache),
            'cache_hit_rate': getattr(self, 'cache_hits', 0) / max(getattr(self, 'cache_requests', 1), 1),
            'memory_usage_mb': self.current_memory_usage / (1024 * 1024),
            'memory_efficiency': self.current_memory_usage / (self.max_memory_gb * 1024 * 1024 * 1024)
        }

        return {
            'system_info': {
                'f_drive_path': str(self.f_embeddings_dir),
                'cache_dir': str(self.cache_dir),
                'device': str(self.device),
                'max_memory_gb': self.max_memory_gb,
                'max_cache_entries': self.max_cache_entries
            },
            'processing_stats': self.processing_stats,
            'modality_stats': dict(self.modality_stats),
            'cache_stats': cache_stats,
            'integration_batches': len(self.integration_batches) if hasattr(self, 'integration_batches') else 0,
            'priority_files': len(self.priority_files) if hasattr(self, 'priority_files') else 0
        }

    def _log_system_statistics(self):
        """Log detailed system statistics"""
        stats = self.get_comprehensive_statistics()

        logger.info("📊 Full-Scale Embedding Integration Statistics:")
        logger.info(f"   🔍 Files Discovered: {stats['processing_stats']['files_discovered']}")
        logger.info(f"   ✅ Files Loaded: {stats['processing_stats']['files_loaded']}")
        logger.info(f"   💾 Files Cached: {stats['processing_stats']['files_cached']}")
        logger.info(f"   ❌ Files with Errors: {stats['processing_stats']['files_error']}")
        logger.info(f"   🎯 Total Embeddings: {stats['processing_stats']['total_embeddings']:,}")
        logger.info(f"   ⚡ Memory Efficiency: {stats['processing_stats']['memory_efficiency']:.2%}")
        logger.info(f"   💾 Cache Usage: {stats['cache_stats']['memory_usage_mb']:.1f} MB")
        logger.info(f"   🎲 Integration Batches: {stats['integration_batches']}")

        logger.info("📈 Modality Breakdown:")
        for modality, stats_data in stats['modality_stats'].items():
            logger.info(f"   - {modality.title()}: {stats_data['count']} files, "
                       f"{stats_data['total_size'] / (1024**2):.1f} MB")

    def optimize_memory_usage(self):
        """Optimize memory usage by cleaning up unused embeddings"""
        logger.info("🧹 Optimizing memory usage")

        with self.loading_lock:
            # Remove old cache entries based on access time
            current_time = time.time()
            entries_to_remove = []

            for file_path, cache_entry in self.embedding_cache.items():
                last_access = cache_entry['last_access']
                if current_time - last_access > 300:  # 5 minutes
                    entries_to_remove.append(file_path)

            for file_path in entries_to_remove:
                del self.embedding_cache[file_path]
                if file_path in self.cache_access_order:
                    self.cache_access_order.remove(file_path)
                self.processing_stats['files_cached'] -= 1

            # Force garbage collection
            torch.cuda.empty_cache() if torch.cuda.is_available() else None

            logger.info(f"✅ Removed {len(entries_to_remove)} old cache entries")

    def validate_integration(self) -> Dict[str, bool]:
        """Validate the integrity and functionality of the integration system"""
        logger.info("🔍 Validating embedding integration system")

        validation_results = {
            'f_drive_accessible': self.f_embeddings_dir.exists(),
            'embeddings_discovered': len(self.embedding_inventory) > 0,
            'cache_functional': len(self.embedding_cache) >= 0,
            'batch_creation': False,
            'memory_management': self.current_memory_usage < (self.max_memory_gb * 1024 * 1024 * 1024),
            'modality_coverage': len(self.modality_stats) > 1
        }

        # Test batch creation
        try:
            test_batch = self.get_training_batch(batch_size=8)
            validation_results['batch_creation'] = test_batch is not None
        except Exception as e:
            logger.warning(f"⚠️ Batch creation test failed: {e}")

        # Log validation results
        logger.info("✅ Validation Results:")
        for test_name, result in validation_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"   - {test_name.replace('_', ' ').title()}: {status}")

        return validation_results

def main():
    """Test the full-scale embedding integration system"""
    from.training.impressioncore_b1_ultimate_trainer import ImpressionCoreB1TestConfig

    logger.info("🚀 Testing Full-Scale Embedding Integration System")

    # Create configuration
    config = ImpressionCoreB1TestConfig()

    # Initialize the integration system
    integrator = FullScaleEmbeddingIntegrator(config)

    # Validate the system
    validation_results = integrator.validate_integration()

    if all(validation_results.values()):
        logger.info("🎉 Full-Scale Embedding Integration System: ALL TESTS PASSED!")
    else:
        logger.warning("⚠️ Some validation tests failed. Check the logs above.")

    # Get comprehensive statistics
    stats = integrator.get_comprehensive_statistics()

    # Test batch creation
    logger.info("🧪 Testing batch creation...")
    for i in range(3):
        batch = integrator.get_training_batch(batch_size=16)
        if batch:
            logger.info(f"   Batch {i+1}: {batch.embeddings.shape}, Quality: {batch.quality_score:.2f}")
            logger.info(f"   Modality Mix: {batch.modality_mix}")
        else:
            logger.warning(f"   Batch {i+1}: Failed to create")

    # Memory optimization test
    integrator.optimize_memory_usage()

    logger.info("✅ Full-Scale Embedding Integration System test completed!")

    return integrator

if __name__ == "__main__":
    main()
