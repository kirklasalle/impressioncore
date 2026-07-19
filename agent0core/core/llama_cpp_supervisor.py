"""
LlamaCppSupervisor - Python Port

Manages local llama-server processes. Spawns/terminates model slots,
manages model loading/unloading, and handles LRU model eviction.
Ported from Prism's TypeScript implementation.
"""

import os
import sys
import time
import logging
import subprocess
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("agent0core.supervisor")

class LlamaModelSlot:
    def __init__(self, slot_id: int, port: int):
        self.id = slot_id
        self.port = port
        self.model_alias: Optional[str] = None
        self.model_path: Optional[str] = None
        self.pid: Optional[int] = None
        self.status: str = "empty"  # empty, loading, ready, error
        self.last_active: float = 0.0
        self.error: Optional[str] = None
        self.draft_model_path: Optional[str] = None
        self.draft_max: int = 16
        self.draft_min: int = 5
        self.draft_p_min: float = 0.9
        self.gpu_layers: Optional[int] = None
        self.flash_attn: bool = False
        self.context_size: int = 4096

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "port": self.port,
            "modelAlias": self.model_alias,
            "modelPath": self.model_path,
            "pid": self.pid,
            "status": self.status,
            "lastActive": self.last_active,
            "error": self.error,
            "draftModelPath": self.draft_model_path,
            "draftMax": self.draft_max,
            "draftMin": self.draft_min,
            "draftPMin": self.draft_p_min,
            "gpuLayers": self.gpu_layers,
            "flashAttn": self.flash_attn,
            "contextSize": self.context_size,
        }

class LlamaCppSupervisor:
    def __init__(
        self,
        binary_path: str = "llama-server",
        base_port: int = 8081,
        max_slots: int = 5,
        default_context: int = 4096,
        models_dir: Optional[str] = None
    ):
        self.binary_path = binary_path
        self.base_port = base_port
        self.max_slots = max_slots
        self.default_context = default_context
        
        # Resolve models directory
        if models_dir is None:
            self.models_dir = str(Path(os.getcwd()) / "models")
        else:
            self.models_dir = models_dir
            
        self.slots: List[LlamaModelSlot] = [
            LlamaModelSlot(i, base_port + i) for i in range(max_slots)
        ]
        self.processes: Dict[int, subprocess.Popen] = {}
        self._lock = threading.Lock()

    def get_config(self) -> Dict[str, Any]:
        return {
            "binaryPath": self.binary_path,
            "basePort": self.base_port,
            "maxSlots": self.max_slots,
            "defaultContext": self.default_context,
            "modelsDir": self.models_dir
        }

    def set_binary_path(self, path: str) -> None:
        self.binary_path = path

    def get_snapshot(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [s.to_dict() for s in self.slots]

    def discover_local_models(self) -> List[str]:
        p = Path(self.models_dir)
        if not p.exists():
            return []
        try:
            models = []
            for f in p.iterdir():
                if f.suffix == ".gguf" and not f.name.lower().startswith("mmproj-"):
                    models.append(f.stem)
            return sorted(models)
        except Exception as e:
            logger.warning(f"Error discovering local models: {e}")
            return []

    def get_model_path(self, alias: str) -> Optional[str]:
        full_path = Path(self.models_dir) / f"{alias}.gguf"
        return str(full_path) if full_path.exists() else None

    def get_port_for_alias(self, model_alias: str) -> Optional[int]:
        with self._lock:
            for slot in self.slots:
                if slot.model_alias == model_alias and slot.status == "ready":
                    slot.last_active = time.time()
                    return slot.port
            return None

    async def load_model(
        self,
        model_path: str,
        model_alias: str,
        ctx_size: Optional[int] = None,
        draft_model_path: Optional[str] = None,
        draft_max: int = 16,
        draft_min: int = 5,
        draft_p_min: float = 0.9,
        gpu_layers: Optional[int] = None,
        flash_attn: bool = False
    ) -> Dict[str, Any]:
        """Loads a model into a slot. Evicts oldest slot using LRU if needed."""
        # Ensure directory of model exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        ctx_size = ctx_size or self.default_context

        with self._lock:
            # 1. Is it already loaded?
            for slot in self.slots:
                if slot.model_alias == model_alias or slot.model_path == model_path:
                    if slot.status == "error":
                        slot.status = "loading"
                        slot.error = None
                        slot.last_active = time.time()
                        # Apply new parameters
                        slot.draft_model_path = draft_model_path
                        slot.draft_max = draft_max
                        slot.draft_min = draft_min
                        slot.draft_p_min = draft_p_min
                        slot.gpu_layers = gpu_layers
                        slot.flash_attn = flash_attn
                        slot.context_size = ctx_size
                        # Start process in background
                        self._spawn_process(slot)
                    else:
                        slot.last_active = time.time()
                    return slot.to_dict()

            # 2. Find empty or error slot
            target_slot = None
            for slot in self.slots:
                if slot.status in ("empty", "error"):
                    target_slot = slot
                    break

            # 3. LRU eviction
            if target_slot is None:
                evictable = sorted(self.slots, key=lambda s: s.last_active)
                target_slot = evictable[0]
                self._unload_slot_under_lock(target_slot.id)

            # Configure slot
            target_slot.model_alias = model_alias
            target_slot.model_path = model_path
            target_slot.status = "loading"
            target_slot.last_active = time.time()
            target_slot.error = None
            target_slot.draft_model_path = draft_model_path
            target_slot.draft_max = draft_max
            target_slot.draft_min = draft_min
            target_slot.draft_p_min = draft_p_min
            target_slot.gpu_layers = gpu_layers
            target_slot.flash_attn = flash_attn
            target_slot.context_size = ctx_size

            self._spawn_process(target_slot)
            return target_slot.to_dict()

    def unload_model(self, model_alias: str) -> bool:
        with self._lock:
            for slot in self.slots:
                if slot.model_alias == model_alias:
                    return self._unload_slot_under_lock(slot.id)
            return False

    def _unload_slot_under_lock(self, slot_id: int) -> bool:
        slot = next((s for s in self.slots if s.id == slot_id), None)
        if not slot:
            return False

        proc = self.processes.pop(slot.id, None)
        if proc:
            try:
                proc.kill()
                proc.wait(timeout=2)
            except Exception:
                pass

        slot.status = "empty"
        slot.model_alias = None
        slot.model_path = None
        slot.pid = None
        slot.error = None
        slot.draft_model_path = None
        slot.gpu_layers = None
        slot.flash_attn = False
        slot.context_size = self.default_context
        return True

    def _spawn_process(self, slot: LlamaModelSlot) -> None:
        """Helper to spawn the llama-server process in a separate monitoring thread."""
        thread = threading.Thread(
            target=self._run_and_monitor_process,
            args=(slot,),
            daemon=True
        )
        thread.start()

    def _run_and_monitor_process(self, slot: LlamaModelSlot) -> None:
        is_ready = [False]
        ready_event = threading.Event()
        captured_logs = []

        # Build args
        args = [
            self.binary_path,
            "--model", slot.model_path,
            "--alias", slot.model_alias,
            "--port", str(slot.port),
            "--ctx-size", str(slot.context_size),
            "--jinja"
        ]

        # Speculative decoding
        if slot.draft_model_path:
            args.extend([
                "--model-draft", slot.draft_model_path,
                "--draft-max", str(slot.draft_max),
                "--draft-min", str(slot.draft_min),
                "--draft-p-min", str(slot.draft_p_min)
            ])

        # GPU offload
        if slot.gpu_layers is not None:
            args.extend(["--n-gpu-layers", str(slot.gpu_layers)])

        # Flash attention
        if slot.flash_attn:
            args.append("--flash-attn")

        # Check for Multimodal Projector
        if "vl" in slot.model_path.lower():
            model_dir = Path(slot.model_path).parent
            mmproj_path = model_dir / "mmproj-model-f16.gguf"
            if mmproj_path.exists():
                args.extend(["--mmproj", str(mmproj_path)])

        logger.info(f"Spawning slot {slot.id} process: {' '.join(args)}")

        proc = None
        try:
            # Set startupinfo on Windows to avoid console window popping up
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            proc = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                startupinfo=startupinfo,
                encoding="utf-8",
                errors="replace"
            )
            
            with self._lock:
                self.processes[slot.id] = proc
                slot.pid = proc.pid

            # Monitor stdout and stderr in separate readers
            def read_stream(stream, is_stderr):
                for line in iter(stream.readline, ''):
                    if not line:
                        break
                    line_str = line.strip()
                    captured_logs.append(line_str)
                    
                    if not is_ready[0]:
                        # Check ready signals
                        if "HTTP server listening" in line_str:
                            is_ready[0] = True
                            ready_event.set()
                        if "error" in line_str.lower():
                            # Keep track of error lines during startup
                            pass

            stdout_thread = threading.Thread(target=read_stream, args=(proc.stdout, False), daemon=True)
            stderr_thread = threading.Thread(target=read_stream, args=(proc.stderr, True), daemon=True)
            
            stdout_thread.start()
            stderr_thread.start()

            # Timeout wait for 90 seconds
            success = ready_event.wait(timeout=90.0)
            if not success or not is_ready[0]:
                if proc.poll() is None:
                    proc.kill()
                error_msg = "Timeout waiting for llama-server to report ready."
                if captured_logs:
                    error_msg += f" Last logs: {captured_logs[-5:]}"
                raise TimeoutError(error_msg)

            # Process successfully launched
            with self._lock:
                slot.status = "ready"
                slot.error = None
            logger.info(f"Model slot {slot.id} ({slot.model_alias}) is ready on port {slot.port}")

            # Keep monitoring process termination
            proc.wait()
            
            # If we reach here, the process terminated
            with self._lock:
                # If it was not manually emptied, it is an unexpected crash
                if slot.status != "empty":
                    slot.status = "error"
                    exit_code = proc.poll()
                    slot.error = f"Process crashed with exit code {exit_code}."
                    logger.error(f"Model slot {slot.id} process crashed with code {exit_code}")

        except Exception as e:
            with self._lock:
                slot.status = "error"
                slot.error = str(e)
            logger.error(f"Failed to start llama-server on slot {slot.id}: {e}")
            if proc and proc.poll() is None:
                try:
                    proc.kill()
                except Exception:
                    pass

    def shutdown_all(self) -> None:
        with self._lock:
            for slot_id in list(self.processes.keys()):
                proc = self.processes.pop(slot_id, None)
                if proc:
                    try:
                        proc.kill()
                    except Exception:
                        pass
            for slot in self.slots:
                slot.status = "empty"
                slot.model_alias = None
                slot.model_path = None
                slot.pid = None
                slot.error = None
