import json
import os
import time
from datetime import datetime
from typing import Any

try:
    import cv2
except ImportError:
    cv2 = None
import torch
import torch.nn as nn
from transformers import AutoTokenizer

from src.core.utils.swarm_presence import swarm as swarm_presence
from src.orchestrator.image_generator import ImageGenerator
from src.orchestrator.message_protocol import pack_message
from src.orchestrator.nexus_interpreter import NexusInterpreter
from src.orchestrator.phoneme_utils import PhonemeProcessor
from src.orchestrator.system_logger import log_event


class UnifiedBrainTriad(nn.Module):
    """
    Unified Wrapper for the Brain-Triad (Left, Right, Colossus).
    Presents a single generation interface to the outside world.
    """

    def __init__(self, config_path: str = "src/core/config/triad_config.json"):
        super().__init__()
        self.config = self._load_config(config_path)

        # New Config Toggle: Simultaneous vs Sequential
        self.simultaneous_load = self.config.get("simultaneous_load", True)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        log_event("TRIAD", f"Initializing Unified Brain Triad on {self.device}")
        self.loading_phase = "INIT_CORE" # Granular Status Tracking
        log_event("TRIAD", f"Loading Mode: {'SIMULTANEOUS (All-in-VRAM)' if self.simultaneous_load else 'SEQUENTIAL (Hot-Swap)'}")

        # Initialize Components with Graceful Degredation
        self.nexus = NexusInterpreter()
        self.nexus.set_triad(self)  # NEXUS: Enable synchronous LLM-QUERY
        self.imager = ImageGenerator()

        try:
            from agent0core.core.pose_interpreter import PoseInterpreter
            from src.orchestrator.orbcloud_vision import OrbCloudVision

            self.vision = OrbCloudVision()
            self.pose_interpreter = PoseInterpreter()
            # We don't call open() here to avoid startup delays,
            # but we ensure the class is instantiated.
            self.vision_active = True
        except Exception as e:
            log_event("TRIAD", f"Vision Layer Unavailable (Graceful Shutoff): {e}", level="WARNING")
            self.vision = None
            self.pose_interpreter = None
            self.vision_active = False

        # Initialize Audio Engine
        try:
            from src.orchestrator.audio_engine import AudioEngine

            self.audio = AudioEngine()
        except Exception as e:
            log_event("TRIAD", f"Audio Engine Unavailable: {e}", level="WARNING")
            self.audio = None

        # Initialize Avatar Engine
        try:
            from src.orchestrator.avatar_engine import AvatarEngine

            self.avatar = AvatarEngine()
        except Exception as e:
            log_event("TRIAD", f"Avatar Engine Unavailable: {e}", level="WARNING")
            self.avatar = None

        # Initialize Models (Qwen Nano-Brain)
        # Using Qwen2.5-0.5B-Instruct as the base "Brain" for all three roles.
        # They will differ by System Prompt and Temperature parameters during execution.
        model_id = (
            self.config.get("model_id")
            or self.config.get("model_path")
            or self.config.get("tokenizer_path")
            or "OpenGVLab/InternVL2-1B"
        )
        tokenizer_source = self.config.get("tokenizer_path", model_id)
        try:
            from transformers import AutoProcessor
            self.processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
            if hasattr(self.processor, 'tokenizer'):
                self.tokenizer = self.processor.tokenizer
            else:
                self.tokenizer = self.processor
            log_event("TRIAD", f"Multimodal Processor Loaded for {model_id}")
        except Exception as e:
            log_event("TRIAD", f"Processor load failed ({e}), falling back to Tokenizer.", level="WARNING")
            self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_source)
            self.processor = None

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = 'left' # Critical for generation

        try:
            # AutoModel is required for InternVL2 (Multimodal)
            from transformers import AutoModel, BitsAndBytesConfig
            self.loading_phase = "LOAD_MODEL"
            log_event("TRIAD", f"Loading {model_id} instances...")

            # Quantization Setup
            quant_type = self.config.get("quantization", None)
            bnb_config = None
            if quant_type == "4bit":
                log_event("TRIAD", "Quantization: 4-bit (BitsAndBytes) Enabled")
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_quant_type="nf4"
                )

            def _load_module():
                # InternVL2 "meta tensor" fix: Monkeypatch torch.linspace to return CPU tensors
                # By using numpy, we bypass torch's meta tensor dispatch completely.
                import numpy as np
                orig_linspace = torch.linspace
                def patched_linspace(start, end, steps, *args, **kwargs):
                    try:
                        # Attempt standard (which might fail on meta device)
                        return orig_linspace(start, end, steps, *args, **kwargs).to("cpu")
                    except Exception:
                        # Fallback: Manual calculation on CPU
                        s = float(start)
                        e = float(end)
                        st = int(steps)
                        if st <= 1:
                            return torch.tensor([s], device="cpu")
                        return torch.from_numpy(np.linspace(s, e, st)).to("cpu")
                torch.linspace = patched_linspace

                # Compatibility Patch: InternVLChatModel missing 'all_tied_weights_keys'
                # This affects some newer transformers versions with InternVL2-1B
                import transformers
                if not hasattr(transformers.PreTrainedModel, "all_tied_weights_keys"):
                    transformers.PreTrainedModel.all_tied_weights_keys = {}

                try:
                    with torch.device("cpu"):
                        model = AutoModel.from_pretrained(
                            model_id,
                            quantization_config=bnb_config,
                            torch_dtype=torch.float16,
                            trust_remote_code=True,
                            device_map=None,
                            low_cpu_mem_usage=False
                        )
                finally:
                    torch.linspace = orig_linspace

                # Now move to the intended device and set to eval
                return model.to(self.device).eval()

            if self.simultaneous_load:
                log_event("TRIAD", "Allocating VRAM for one shared module (InternVL2-1B)...")
                # Loading one shared brain to save VRAM on GTX 1050 Ti
                shared_brain = _load_module()
                self.left = shared_brain
                self.right = shared_brain
                self.colossus = shared_brain

                # InternVL2 Specific Metadata (Required for generation)
                for mod in [self.left, self.right, self.colossus]:
                    if hasattr(mod, "img_context_token_id") and mod.img_context_token_id is None:
                        # InternVL2 typically uses this token for image context
                        mod.img_context_token_id = self.tokenizer.convert_tokens_to_ids('<IMG_CONTEXT>')
                        log_event("TRIAD", f"Set img_context_token_id to {mod.img_context_token_id}")

                log_event("TRIAD", "VRAM Allocation Successful")
            else:
                # Sequential Load Mode
                log_event("TRIAD", "Sequential Load Mode (Performance Impact Warning)")
                shared_brain = _load_module()
                self.left = shared_brain
                self.right = shared_brain
                self.colossus = shared_brain

            self.loading_phase = "READY"

        except Exception as e:
                import traceback
                log_event("TRIAD", f"Model Load Failed: {e}\n{traceback.format_exc()}", level="ERROR")
                raise e from e

        # Avatar Engine
        self.avatar = AvatarEngine()
        self.avatar_id = "USER_01_AVATAR"
        self.is_avatar_active = False # Default to inactive, activated by vision or explicit command

        # Audio Layer (Initialized above)
        # self.audio = ...

        # Phoneme Processor
        self.phoneme_processor = PhonemeProcessor()

        # Load OS Knowledge (Tiny Linux)
        iso_path = "rag_library/tinycore.iso"
        if hasattr(self.colossus, "latent_kernel"):
            self.colossus.latent_kernel.load_knowledge(iso_path)

        # 2025 Swarm Presence Integration
        self.swarm = swarm_presence
        if self.swarm.connect():
            log_event("TRIAD", "Successfully connected to the 2025 MCP Swarm (Goliath).")
        else:
            log_event("TRIAD", "Swarm offline. Running in standalone mode.", level="WARNING")

    def _load_config(self, config_path: str) -> dict[str, Any]:
        """Loads the configuration from a JSON file."""
        import json
        if not os.path.exists(config_path):
            log_event("TRIAD", f"Config file not found at {config_path}. Using default settings.", level="WARNING")
            return {
                "model_id": "src/training/tokenizers/b3_conversation_tokenizer_28k",
                "tokenizer_path": "src/training/tokenizers/b3_conversation_tokenizer_28k",
                "simultaneous_load": True
            }
        with open(config_path) as f:
            return json.load(f)

    def forward(self, input_ids: torch.Tensor, image_features: torch.Tensor | None = None):
        """Standard forward pass for integration testing."""
        # Parallel processing in Left/Right hemispheres
        out_left = self.left(input_ids=input_ids, image_features=image_features)
        out_right = self.right(input_ids=input_ids, image_features=image_features)

        # Packaging into TriMessages with Latent Vectors
        # We use the 'latent_vec' returned by the model forward pass
        msg_left = pack_message(
            provenance="Left",
            modality="text",
            structured={"logic": "analytical_parse"},
            vector=out_left["latent_vec"].mean(dim=1).flatten().tolist(),
            confidence=0.9
        )

        msg_right = pack_message(
            provenance="Right",
            modality="text",
            structured={"creative": "synthesis_associative"},
            vector=out_right["latent_vec"].mean(dim=1).flatten().tolist(),
            confidence=0.7
        )

        # Colossus Integration via Latent OS
        final_integration = self.colossus.integrate_with_os(msg_left, msg_right)

        log_event("TRIAD", "Forward pass complete", payload={"system_status": final_integration["latent_os"]["system_status"]})

        return {
            "integration": final_integration,
            "left_raw": out_left,
            "right_raw": out_right
        }

    def generate(self, prompt: str, sensory_data: dict[str, Any] | None = None, history: list[dict[str, str]] | None = None):
        """
        High-level Triad generation API.
        Broadcasts input to L/R/C simultaneously via ThreadPoolExecutor.
        Aggregates outputs solely via Colossus.
        """
        log_event("TRIAD", f"Broadcasting input: {prompt} (Context: {len(history) if history else 0} msgs)")

        # 0. Swarm Context Injection
        swarm_tags = self.swarm.get_context_tags() if hasattr(self, 'swarm') else []
        if swarm_tags:
            swarm_ctx = f" [Swarm Context: {', '.join(swarm_tags)}]"
            log_event("TRIAD", f"Injecting Swarm Context into Prompt: {swarm_ctx}")
            prompt = swarm_ctx + " " + prompt

        # 1. Sensory Pre-processing
        vision_frames = None

        # Check override (API/Client provided frames)
        if sensory_data and 'vision_frames' in sensory_data:
            vision_frames = sensory_data['vision_frames']
            log_event("VISION", f"Using {len(vision_frames)} API-provided frames.")

        if self.vision_active and self.vision and not vision_frames:
            try:
                vision_frames = self.vision.capture_all_frames()
            except Exception as e:
                log_event("TRIAD", f"Vision Capture Failed: {e}", level="WARNING")

        # 1.1 Snapshot Persistence (Saves vision_frames to disk for UI)
        if vision_frames:
            try:
                snap_dir = r"d:\Projects\impressioncore\src\interfaces\web_client\public\captures"
                if not os.path.exists(snap_dir):
                    os.makedirs(snap_dir, exist_ok=True)

                self.snapshot_urls = []

                # Capture IDs to snap
                if self.vision:
                    ids_to_snap = [getattr(self.vision, 'active_cam_id', None)]
                    if getattr(self.vision, 'active_cam_id2', None) is not None:
                        ids_to_snap.append(self.vision.active_cam_id2)
                else:
                    # If vision not loaded, just snap whatever is in vision_frames (likely indices 0, 1)
                    ids_to_snap = list(vision_frames.keys())

                # Deduplicate and filter None
                ids_to_snap = list(dict.fromkeys([i for i in ids_to_snap if i is not None]))

                # Ensure we have something to snap if ids_to_snap is empty but vision_frames isn't
                if not ids_to_snap and vision_frames:
                    ids_to_snap = [next(iter(vision_frames.keys()))]

                for snap_idx in ids_to_snap:
                    if snap_idx in vision_frames:
                        snap_frame = vision_frames[snap_idx]
                        timestamp = datetime.now().strftime("%H%M%S_%f")
                        snap_filename = f"snap_{snap_idx}_{timestamp}.jpg"
                        snap_path = os.path.join(snap_dir, snap_filename)

                        cv2.imwrite(snap_path, snap_frame)
                        url = f"/captures/{snap_filename}"
                        self.snapshot_urls.append(url)
                        log_event("VISION", f"Snapshot {snap_idx} saved: {url}")

                # Legacy support for single URL (Primary)
                self.snapshot_url = self.snapshot_urls[0] if self.snapshot_urls else None

                # Perform tracking if possible
                if self.vision:
                    user_pos = self.vision.triangulate_position()
                    if self.avatar:
                        self.avatar.update_from_vision(user_pos)

                    # Extract HCEP Oculomotor context for prompt injection
                    hcep_data = user_pos.get("hcep", {})
                    smile = hcep_data.get('smile_score', 0.0)
                    gaze = hcep_data.get('user_gaze', 'UNKNOWN')

                    self.current_hcep_prompt = (
                        f" [Sensory Context: Gaze={gaze}, Focus={hcep_data.get('gaze_target_type', 'FACE')}, "
                        f"Social={ 'Smiling' if smile > 0.4 else 'Neutral' } ({smile:.2f}), "
                        f"Attention={hcep_data.get('user_attention', 0.0):.2f}]"
                    )

                    self.nexus.execute(f"(LOG \"Sensory: User detected at {user_pos['pos']}{self.current_hcep_prompt}\")")
                else:
                    self.current_hcep_prompt = ""
            except Exception as e:
                log_event("TRIAD", f"Snapshot Processing Failed: {e}", level="WARNING")
                self.current_hcep_prompt = ""

        # 1.1 Temporal Visual Context (The "Last 60 Seconds")
        temporal_summary = None
        if self.vision_active and self.vision:
            temporal_summary = self.vision.get_buffer_summary()
            if temporal_summary is not None:
                log_event("VISION", "Temporal summary grid injected into context.")


        # 2. Parallel Dispatch (Triple Response)

        # Helper for thread-safe generation with Multimodal Support
        def _generate_module(module, name, temp, role_prompt, frames, history=None, prompt=prompt, max_tokens=100):
            # InternVL2 Prompt Format
            # Standard: <|im_start|>system\n{role}<|im_end|>\n<|im_start|>user\n<image>\n{prompt}<|im_end|>\n<|im_start|>assistant\n

            # Construct Prompt with History and HCEP Context
            role_prompt_f = role_prompt + getattr(self, "current_hcep_prompt", "")
            full_prompt = f"<|im_start|>system\n{role_prompt_f}<|im_end|>\n"

            if history:
                # Add historical messages (limit to last 10 to save tokens)
                for msg in history[-10:]:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    full_prompt += f"<|im_start|>{role}\n{content}<|im_end|>\n"

            # Current Message
            # Ensure <image> token is present if ANY frames are passed
            has_visuals = False
            if frames:
                if (isinstance(frames, list) and len(frames) > 0) or (isinstance(frames, dict) and len(frames) > 0):
                    has_visuals = True

            if has_visuals and hasattr(self, 'processor'):
                # Augment System Prompt with Visual Awareness
                if "You have visual perception" not in role_prompt:
                    role_prompt += " You have visual perception. The user has provided an image/video frame."

                # Re-construct system header with updated role
                full_prompt = f"<|im_start|>system\n{role_prompt}<|im_end|>\n"

                # Re-add history
                if history:
                    for msg in history[-10:]:
                        role = msg.get("role", "user")
                        content = msg.get("content", "")
                        full_prompt += f"<|im_start|>{role}\n{content}<|im_end|>\n"

                full_prompt += f"<|im_start|>user\n<image>\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
            else:
                full_prompt += f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"

            # log_event("TRIAD", f"{name} Prompt: {full_prompt[:100]}...")

            # Use AutoProcessor if available, fallback to Tokenizer
            try:
                if frames and hasattr(self, 'processor') and self.processor:
                    import cv2
                    from PIL import Image

                    # Normalize frames to single image (Primary Camera Priority)
                    frame_img = None
                    if isinstance(frames, list) and len(frames) > 0:
                        frame_img = frames[0]
                    elif isinstance(frames, dict) and len(frames) > 0:
                        # STRICT: Always use the user-selected active camera for Brain visual input
                        active_id = getattr(self.vision, 'active_cam_id', None)
                        if active_id is not None and active_id in frames:
                            frame_img = frames[active_id]
                        else:
                            # Fallback to the first available if active_id is missing/invalid
                            frame_img = next(iter(frames.values())) if frames else None

                    if frame_img is not None:
                        # Convert BGR to RGB
                        img = Image.fromarray(cv2.cvtColor(frame_img, cv2.COLOR_BGR2RGB))

                        # InternVL2 Processor: text, images, return_tensors
                        inputs = self.processor(text=full_prompt, images=img, return_tensors="pt")
                    else:
                         # Fallback to text-only if frames passed but valid image extraction failed
                         inputs = self.processor(text=full_prompt, images=None, return_tensors="pt")

                else:
                    # Text Only
                    tokenizer_obj = self.tokenizer or (self.processor.tokenizer if self.processor else None)
                    inputs = tokenizer_obj(full_prompt, return_tensors="pt")

                inputs = {k: v.to(self.device if self.simultaneous_load else "cpu") for k, v in inputs.items()}

                # Debug: Check inputs for contamination
                log_event("TRIAD", f"Debug {name} inputs: {list(inputs.keys())}")
                if "use_cache" in inputs:
                    del inputs["use_cache"]

                # Ensure module is on device
                if not self.simultaneous_load:
                    module.to(self.device)

                with torch.no_grad():
                    gen = module.generate(
                        **inputs,
                        max_new_tokens=max_tokens,
                        temperature=temp,
                        do_sample=True,
                        pad_token_id=self.tokenizer.pad_token_id
                    )
                    # Slicing for InternVL is tricky due to token expansion.
                    unexpanded_start_idx = inputs['input_ids'].shape[-1]

                    # Robust Decoding Logic:
                    # If total length is shorter than the input, it's definitely just the new tokens.
                    # If total length is longer, it might have the prompt.
                    if len(gen[0]) <= unexpanded_start_idx:
                        # Output is only the generated tokens
                        txt = self.tokenizer.decode(gen[0], skip_special_tokens=True).strip()
                    else:
                        # Output likely includes prompt
                        decoded_all = self.tokenizer.decode(gen[0], skip_special_tokens=False)

                        if "<|im_start|>assistant" in decoded_all:
                            txt = decoded_all.split("<|im_start|>assistant")[-1]
                        elif "assistant\n" in decoded_all:
                            txt = decoded_all.split("assistant\n")[-1]
                        else:
                            # Fallback to tail index
                            txt = self.tokenizer.decode(gen[0][unexpanded_start_idx:], skip_special_tokens=True).strip()

                    # Clean up trailing tokens
                    for tag in ["<|im_end|>", "<|endoftext|>", "</s>", "\nuser", "\nassistant"]:
                        txt = txt.split(tag)[0]
                    txt = txt.strip()

                    # Log for debugging
                    log_event("TRIAD", f"{name} Sync: InLen={unexpanded_start_idx}, OutLen={len(gen[0])}, TxtLen={len(txt)}")

                    # Fallback for empty responses
                    if not txt or len(txt) < 1:
                        txt = "...(Observing)..."

                    self.nexus.execute(f"(LOG \"{name} Outcome: {txt[:50]}...\")")
                    return txt

            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                log_event("TRIAD", f"{name} Generation Failed: {e}\n{error_trace}", level="ERROR")
                return f"[Error in {name}]"
            finally:
                if not self.simultaneous_load:
                    module.cpu()
                    torch.cuda.empty_cache()

        # Execute Left and Right in parallel threads

        # Structure for trace logging
        trace_id = f"trace_{int(time.time())}"
        trace_data = {
            "id": trace_id,
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "left": None,
            "right": None,
            "colossus_input": None,
            "colossus_output": None
        }

        # 2. Sequential Dispatch (Triple Response)
        # We serialize these on 4GB hardware to prevent VRAM fragmentation and context-switch overhead.
        log_event("TRIAD", "Executing Triple Reasoning Flow (Sequential)...")

        if temporal_summary is not None:
             log_event("TRIAD", "Hemispheres aware of temporal visual history.")

        # Left Brain (Logic)
        resp_left = _generate_module(
            self.left, "Left", 0.7,
            "You are the Logical/Analytic hemisphere. Reasoning step-by-step.",
            vision_frames, history=history, max_tokens=60
        )

        # Right Brain (Creative)
        resp_right = _generate_module(
            self.right, "Right", 0.95,
            "You are the Creative/Associative hemisphere. Thinking outside the box. You have a Mind's Eye: use (GENERATE-IMAGE \"description\") to visualize complex or abstract concepts.",
            vision_frames, history=history, max_tokens=60
        )

        trace_data["left"] = resp_left
        trace_data["right"] = resp_right

        # 3. Colossus Aggregation (Sequential)
        # Verify inputs prevent hallucination
        log_event("TRIAD", "Synthesizing Left/Right outputs via Colossus...")

        # Long-Term Memory Integration: Get summary of recent session history
        memory_summary = self.nexus.execute("(MEMORY-SUMMARY)")
        hcep_ctx = getattr(self, "current_hcep_prompt", "")

        COLOSSUS_ROLE = f"You are Colossus, the executive controller. {memory_summary}{hcep_ctx}\nSynthesize internal thoughts into a single response. You can trigger the Mind's Eye using (GENERATE-IMAGE \"description\") if the creative hemisphere suggests it or if a visual asset is needed."
        COLOSSUS_CONTEXT = f"User Input: {prompt}\n\n[Internal Thought A (Logic)]: {resp_left}\n\n[Internal Thought B (Intuition)]: {resp_right}\n\nSynthesized Response:"

        # Colossus sees the *synthesis* prompt, not just the raw user prompt
        # We pass the synthesis context as the 'prompt' argument to _generate_module
        resp_colossus = _generate_module(self.colossus, "Colossus", 0.5, COLOSSUS_ROLE, vision_frames, prompt=COLOSSUS_CONTEXT)

        # --- Strict Output Cleaning ---
        # 1. Identify "Synthesized Response:" marker
        if "Synthesized Response:" in resp_colossus:
            resp_colossus = resp_colossus.split("Synthesized Response:")[-1].strip()

        # 2. Remove any leaked [Internal Thought ...] blocks
        # Pattern: [Internal Thought ...]: ... (until newline or end)
        import re
        resp_colossus = re.sub(r"\[Internal Thought.*?\]:.*?(?=\n|$)", "", resp_colossus, flags=re.IGNORECASE)
        resp_colossus = re.sub(r"\[Internal Thought.*?\]", "", resp_colossus, flags=re.IGNORECASE) # Catch leftovers

        # 3. Final whitespace cleanup
        resp_colossus = resp_colossus.strip()
        # ------------------------------

        trace_data["colossus_input"] = COLOSSUS_CONTEXT
        trace_data["colossus_output"] = resp_colossus

        # Save Trace
        try:
            with open("logs/triad_traces.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(trace_data) + "\n")
        except Exception as e:
            log_event("TRIAD", f"Failed to save trace: {e}", level="WARNING")

        # 4. Active Nexus-L Execution Loop
        # Extract and execute S-Expressions from all three brain segments.
        all_outputs = [resp_left, resp_right, resp_colossus]
        s_expr_pattern = r"(\([A-Z-]+\s+.*?\))"

        for output in all_outputs:
            matches = re.findall(s_expr_pattern, output)
            for cmd in matches:
                try:
                    result = self.nexus.execute(cmd)
                    log_event("NEXUS-EXEC", f"Executed: {cmd} -> {result}")
                except Exception as e:
                    log_event("NEXUS-EXEC", f"Execution Failed: {cmd} ({e})", level="ERROR")

        # 5. Extract Affective State for Avatar Visualization
        affective_state = self._extract_affective_state(resp_colossus)
        # Update Avatar Engine with new state
        if self.avatar:
            self.avatar.set_emotion(affective_state)

        log_event("TRIAD", f"Affective State determined: {affective_state}")

        # 6. Apply Pending Configuration Changes from the Nexus Queue
        while self.nexus.output_queue:
            action = self.nexus.output_queue.pop(0)
            if action["action"] == "CONFIG" and action["key"] == "temperature":
                target = action["target"].lower()
                new_temp = action["value"]
                log_event("TRIAD-CONF", f"Applying dynamic temperature: {target} -> {new_temp}")
                # Note: Currently temperatures are passed per-call in _generate_module.
                # In a more advanced version, we store these in a state dict.
                # For this MVP, we log that the "intent" was captured.

            elif action["action"] == "REQUEST":
                log_event("TRIAD-REQ", f"Internal work request queued: {action['type']} for {action['target']}")

        # 4. Nexus Output Processing (Commands generated during reasoning)
        # Populate neural thought stream with reasoning trace
        nexus_logs = [
            f"🧠 LEFT [Logical]: {resp_left[:120]}..." if len(resp_left) > 120 else f"🧠 LEFT [Logical]: {resp_left}",
            f"🎨 RIGHT [Creative]: {resp_right[:120]}..." if len(resp_right) > 120 else f"🎨 RIGHT [Creative]: {resp_right}",
            "⚡ COLOSSUS [Synthesis]: Processing hemispheric inputs...",
        ]
        generated_image_url = None

        # Execute any Nexus commands that may have been embedded in Colossus's thought stream
        # Or commands that were queued by the hemispheres.
        # Check specifically for imagery requests.
        while self.nexus.output_queue:
            action = self.nexus.output_queue.pop(0)
            if action["action"] == "GENERATE_IMAGE":
                log_event("TRIAD", f"Executing Nexus Imagery Request: {action['prompt']}")
                generated_image_url = self.imager.generate(action["prompt"], action.get("params"))
            else:
                nexus_logs.append(f"Command Executed: {action['action']}")

        # Final synthesizing of results
        return {
            "response": resp_colossus,
            "internal_monitors": {
                "left_hemisphere": resp_left,
                "right_hemisphere": resp_right
            },
            "nexus_logs": nexus_logs,
            "generated_image_url": generated_image_url,
            "affective_state": affective_state,
            "snapshot_url": getattr(self, 'snapshot_url', None),
            "snapshot_urls": getattr(self, 'snapshot_urls', []),
            "integration_state": {"status": "INTEGRATED", "latent_os": {"system_status": "NOMINAL"}},
            "avatar_update": self.generate_avatar_update(),
            "status": "TRIAD_COMPLETE"
        }

    def speak(self, text: str, play_now: bool = True):
        """Synthesizes speech (TTS) using pyttsx3 (Windows SAPI).
        Returns the path to the generated audio file.
        """
        if not text or not text.strip():
            log_event("AUDIO", "Empty text provided. Skipping synthesis.")
            return None
        log_event("AUDIO", f"Synthesizing speech: {text[:50]}...")

        from datetime import datetime

        import pyttsx3

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        audio_filename = f"tts_{timestamp}.mp3"
        audio_path = os.path.join("logs", audio_filename)
        self.last_audio_url = f"/audio/{audio_filename}"  # Store for API access

        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)

        try:
            engine = pyttsx3.init()
            # Optional: Set voice rate
            engine.setProperty('rate', 175)
            engine.save_to_file(text, audio_path)
            engine.runAndWait()

            # Verify file was created
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                log_event("AUDIO", f"Speech synthesized to {audio_path} ({os.path.getsize(audio_path)} bytes)")

                if play_now and self.audio:
                    self.audio.play_file(audio_path)
            else:
                log_event("AUDIO", "TTS file was not created or is empty", level="ERROR")

        except Exception as e:
            log_event("AUDIO", f"TTS failed: {e}", level="ERROR")

    # ===================================================================
    # === NEXUS v1.2: Direct Hemisphere Query Methods ==============
    # ===================================================================

    def query_left(self, prompt: str, temperature: float = 0.3, max_tokens: int = 150) -> str:
        """
        Direct query to the Left (Logical/Analytical) hemisphere.
        Used by NEXUS for recursive sub-LLM calls.
        """
        return self._query_hemisphere(
            module=self.left, name="Left", prompt=prompt,
            role_prompt="You are the Logical/Analytic hemisphere. Provide factual, structured analysis.",
            temperature=temperature, max_tokens=max_tokens
        )

    def query_right(self, prompt: str, temperature: float = 0.9, max_tokens: int = 150) -> str:
        """
        Direct query to the Right (Creative/Intuitive) hemisphere.
        Used by NEXUS for recursive sub-LLM calls.
        """
        return self._query_hemisphere(
            module=self.right, name="Right", prompt=prompt,
            role_prompt="You are the Creative/Associative hemisphere. Think outside the box, find patterns.",
            temperature=temperature, max_tokens=max_tokens
        )

    def query_colossus(self, prompt: str, temperature: float = 0.5, max_tokens: int = 200) -> str:
        """
        Direct query to Colossus (Central Executive/Synthesizer).
        Used by NEXUS for recursive sub-LLM calls.
        """
        return self._query_hemisphere(
            module=self.colossus, name="Colossus", prompt=prompt,
            role_prompt="You are Colossus, the executive controller. Synthesize and integrate information.",
            temperature=temperature, max_tokens=max_tokens
        )

    def _query_hemisphere(self, module, name: str, prompt: str, role_prompt: str,
                          temperature: float, max_tokens: int) -> str:
        """Internal method for querying a specific hemisphere (RLM interface)."""
        log_event("NEXUS", f"Querying {name} (temp={temperature}): {prompt[:50]}...")

        try:
            # Construct InternVL2-compatible prompt
            full_prompt = f"<|im_start|>system\n{role_prompt}<|im_end|>\n"
            full_prompt += f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"

            tokenizer_obj = self.tokenizer or (self.processor.tokenizer if self.processor else None)
            if not tokenizer_obj:
                return f"[Error: No tokenizer available for {name}]"

            inputs = tokenizer_obj(full_prompt, return_tensors="pt")
            inputs = {k: v.to(self.device if self.simultaneous_load else "cpu") for k, v in inputs.items()}

            if not self.simultaneous_load:
                module.to(self.device)

            with torch.no_grad():
                gen = module.generate(
                    **inputs, max_new_tokens=max_tokens, temperature=temperature,
                    do_sample=True, pad_token_id=tokenizer_obj.pad_token_id
                )

                unexpanded_start_idx = inputs['input_ids'].shape[-1]
                if len(gen[0]) <= unexpanded_start_idx:
                    txt = tokenizer_obj.decode(gen[0], skip_special_tokens=True).strip()
                else:
                    decoded_all = tokenizer_obj.decode(gen[0], skip_special_tokens=False)
                    if "<|im_start|>assistant" in decoded_all:
                        txt = decoded_all.split("<|im_start|>assistant")[-1]
                    else:
                        txt = tokenizer_obj.decode(gen[0][unexpanded_start_idx:], skip_special_tokens=True).strip()

                # Clean up trailing tokens
                txt = txt.split('<|im_end|>')[0].strip()

                log_event('NEXUS', f'{name} Response: {txt[:100]}...')
                return txt

        except Exception as e:
            log_event('NEXUS', f'{name} Query Failed: {e}', level='ERROR')
            return f'[Error in {name}: {e}]'
        finally:
            if not self.simultaneous_load:
                module.cpu()
                torch.cuda.empty_cache()

    def generate_avatar_update(self):
        """Generates instructions for the 3D avatar engine."""
        return self.avatar.get_render_commands()

    def get_model_status(self):
        """Returns metadata about the active model and configuration."""
        import torch
        model_id = self.config.get("model_id") or self.config.get("model_path") or "OpenGVLab/InternVL2-1B"
        quantization = self.config.get("quantization", "None")

        # Calculate VRAM in GB
        vram_alloc = torch.cuda.memory_allocated() / 1e9 if torch.cuda.is_available() else 0
        vram_res = torch.cuda.memory_reserved() / 1e9 if torch.cuda.is_available() else 0

        # Detailed Agent Status
        agents = {
            "left_hemisphere": {
                "role": "Logic/Analysis",
                "model": "Shared (InternVL2)" if self.simultaneous_load else "Swapped",
                "status": "ACTIVE" if self.loading_phase == "READY" else "LOADING"
            },
            "right_hemisphere": {
                "role": "Creative/Visual",
                "model": "Shared (InternVL2)" if self.simultaneous_load else "Swapped",
                "status": "ACTIVE" if self.loading_phase == "READY" else "LOADING"
            },
            "colossus_cortex": {
                "role": "Executive/Synthesis",
                "model": "Shared (InternVL2)" if self.simultaneous_load else "Swapped",
                "status": "ACTIVE" if self.loading_phase == "READY" else "LOADING"
            }
        }

        status = {
            "model_name": model_id,
            "quantization": quantization,
            "device": str(self.device) + (f" ({torch.cuda.get_device_name(0)})" if torch.cuda.is_available() else ""),
            "simultaneous_load": self.simultaneous_load,
            "vram_allocated_gb": vram_alloc,
            "vram_reserved_gb": vram_res,
            "agents": agents,
            "temperatures": {
                "left": 0.7,
                "right": 0.95,
                "colossus": 0.5
            },
            "status": "NOMINAL",
            "llm_loaded": self.loading_phase == "READY",
            "loading_phase": self.loading_phase
        }
        return status

    def get_fused_telemetry(self):
        """
        Merges Vision and Audio telemetry for unified tracking (SpatialSense v2).
        Includes confidence scoring based on source count and quality.
        """
        import math

        # 1. Get Base Data
        vision_data = self.vision.get_telemetry() if self.vision else {"pos": [0,0,0], "detections": {}}
        audio_data = self.audio.get_telemetry() if self.audio else {"stream": {"angle": 0, "vad": False}}

        # Normalization logic
        fused_data = vision_data.copy()
        audio_stream = audio_data.get("stream", {})
        audio_angle = audio_stream.get("angle", 0)
        vad_active = audio_stream.get("vad", False)
        audio_array_active = audio_stream.get("system_active", False)

        fused_data["audio_active"] = vad_active
        fused_data["audio_array_active"] = audio_array_active
        fused_data["audio_angle"] = audio_angle

        # Propagate Kinect/IR status from Vision layer
        fused_data["ir_active"] = vision_data.get("ir_active", False)
        fused_data["depth_active"] = vision_data.get("depth_active", False)

        # 2. Camera Count and Detection Stats
        raw_detections = vision_data.get("detections", {})

        # Use vision caps + virtual streams for count
        cam_count = len(self.vision.caps) if self.vision else 0
        if fused_data.get("ir_active"):
            cam_count += 1
        if fused_data.get("depth_active"):
            cam_count += 1

        fused_data["camera_count"] = cam_count

        # Calculate total unique faces (simplified)
        faces_set = set()
        for cid, faces in raw_detections.items():
            for i, _f in enumerate(faces):
                faces_set.add(f"{cid}_{i}")
        fused_data["total_faces"] = len(faces_set)

        # Semantic Mapping: Convert numeric IDs (0, 1, 98) to names expected by UI
        # UI expects: VisionAlpha, VisionBeta
        # Strategy:
        # - Active Camera (Primary) -> VisionAlpha
        # - Secondary Camera (if exists) -> VisionBeta

        detections = {}
        active_id = self.vision.active_cam_id if self.vision else 99
        active_id2 = getattr(self.vision, 'active_cam_id2', None)

        # Sort keys to ensure deterministic mapping
        cam_ids = sorted(raw_detections.keys())

        for cid in cam_ids:
            faces = raw_detections[cid]
            if not isinstance(faces, list):
                continue

            # 1. Raw Numeric ID Mapping (for dynamic frontend logic)
            detections[str(cid)] = faces

            # 2. Semantic Mapping (Legacy & standard UI)
            cid_str = str(cid)
            if cid_str == str(active_id):
                detections["VisionAlpha"] = faces
            elif cid_str == str(active_id2):
                detections["VisionBeta"] = faces
            elif cid_str == "105":
                detections["VisionDepth"] = faces
            elif cid_str == "106":
                detections["VisionIR"] = faces

            # 3. Automatic "Beta" fallback if not explicitly set
            if active_id2 is None and cid != active_id and "VisionBeta" not in detections:
                detections["VisionBeta"] = faces

        # 4. CROSS-LINKING: Ensure Kinect detections (ID 98) flow to semantic labels if they are active
        # This fixes the issue where the OS sees the Kinect as a generic camera (e.g. ID 0, 1, 5)
        # but OrbCloudVision does specialized processing on ID 98.
        kinect_faces = raw_detections.get("98", raw_detections.get(98, []))
        if kinect_faces:
            # Check if Alpha or Beta is actually a Kinect
            for semantic_label, actual_id in [("VisionAlpha", active_id), ("VisionBeta", active_id2)]:
                if actual_id is None:
                    continue
                meta = self.vision.hardware_metadata.get(actual_id, {})
                model = str(meta.get("model", "")).lower()
                vid_pid = str(meta.get("vid_pid", "")).lower()

                if "kinect" in model or "045e_02ae" in vid_pid:
                    # Found it! Alias the detections so they show up on this stream in the UI
                    processed_kinect = []
                    for i, f in enumerate(kinect_faces):
                        f_copy = f.copy()
                        # Ensure Primary labeling for the aliased stream if it's VisionAlpha
                        if semantic_label == "VisionAlpha" and i == 0:
                            if not str(f_copy.get("label", "")).startswith("Primary:"):
                                f_copy["label"] = f"Primary: {f_copy.get('label', 'Kinect Face')}"
                        processed_kinect.append(f_copy)

                    if not detections.get(semantic_label):
                        detections[semantic_label] = processed_kinect
                    else:
                        # Merge if there are multiple sources (rare but possible)
                        existing_ids = {f.get("id") for f in detections[semantic_label]}
                        for f in processed_kinect:
                            if f.get("id") not in existing_ids:
                                detections[semantic_label].append(f)

        # Filter for cameras that actually have detections
        [label for label, faces in detections.items() if len(faces) > 0]

        # FIX: report total connected cameras, not just those seeing faces
        camera_count = len(self.vision.caps) if self.vision else 0
        total_faces = sum(len(faces) for faces in detections.values())

        fused_data["detections"] = detections # Replaced raw with semantic mapping
        fused_data["camera_count"] = camera_count
        fused_data["total_faces"] = total_faces

        # 5. Pose Analysis (New)
        poses = []
        if self.vision and self.vision.latest_skeleton and hasattr(self, 'pose_interpreter'):
            poses = self.pose_interpreter.analyze(self.vision.latest_skeleton)
        fused_data["poses"] = poses
        fused_data["performance"] = self.vision.performance_stats if self.vision else {}

        # 3. Geometric Correlation (Refined Multi-Target Heuristic)
        alpha_faces = detections.get("VisionAlpha", [])
        best_face_dist = 999.0
        best_face_id = None

        # Lock onto the face closest to the localized audio angle
        for face in alpha_faces:
            bbox = face.get("bbox", [320, 240, 60, 60])
            # Assuming 640px wide FOV for the mapping
            cx_norm = (bbox[0] + bbox[2]/2) / 640.0
            f_angle = (cx_norm - 0.5) * 75.0
            dist = abs(f_angle - audio_angle)
            if dist < best_face_dist:
                best_face_dist = dist
                best_face_id = face.get("id")

        is_correlated = (best_face_dist < 18.0) and vad_active and audio_array_active

        fused_data["target_lock"] = is_correlated
        fused_data["target_face_id"] = best_face_id
        fused_data["angular_distance"] = float(best_face_dist) if best_face_id else 0.0

        # 4. Confidence Calculation (based on actual sensor contribution)
        base_confidence = 0.0
        confidence_sources = []

        # Vision contribution
        if total_faces > 0:
            # Single camera = 40%, dual camera = 70% (stereo depth)
            vision_conf = 0.4 if camera_count == 1 else 0.7
            base_confidence += vision_conf
            confidence_sources.append(f"CAM:{camera_count}")

        # Audio contribution
        if vad_active and audio_array_active:
            audio_conf = 0.2  # Audio adds 20% baseline
            if is_correlated:
                audio_conf = 0.3  # Extra 10% for confirmation
            base_confidence += audio_conf
            confidence_sources.append("AUDIO")

        # Cap at 100%
        fused_data["confidence"] = min(100, int(base_confidence * 100))
        fused_data["confidence_sources"] = confidence_sources

        # 5. Tracking Quality Level
        if fused_data["confidence"] >= 80:
            fused_data["quality"] = "EXCELLENT"
        elif fused_data["confidence"] >= 60:
            fused_data["quality"] = "GOOD"
        elif fused_data["confidence"] >= 40:
            fused_data["quality"] = "FAIR"
        else:
            fused_data["quality"] = "LOW"

        # 6. Decision Matrix (Status Message)
        has_visual_lock = total_faces > 0

        if is_correlated:
            fused_data["status_msg"] = "SPATIAL_LOCK"
        elif not has_visual_lock and vad_active:
            # Blind but hearing. Map Angle to synth X.
            estimated_x = math.sin(math.radians(audio_angle))
            fused_data["pos"] = [estimated_x, 0.0, 1.5]
            fused_data["status_msg"] = f"AUDIO_ONLY ({audio_angle:.0f}°)"
            fused_data["detections"] = {
                "AUDIO_SRC": [{"id": "AUDIO_SRC", "confidence": 0.8, "box": [0,0,0,0]}]
            }
            # TRIGGER PHYSICAL STEERING (Audio-Guided Swivel)
            if self.vision:
                self.vision.steer_to_angle(audio_angle)
        elif has_visual_lock and not vad_active:
            fused_data["status_msg"] = "VISUAL_ONLY"
        elif has_visual_lock and vad_active:
            # Both active but not correlated
            fused_data["status_msg"] = "AMBIGUOUS_SENSORY"
        else:
            fused_data["status_msg"] = "SEARCHING"

        return fused_data

    def _extract_affective_state(self, text: str) -> str:
        """Determines the expression for the Happyface avatar based on the response content."""
        t = text.lower()

        # Mapping based on the happyfaceemojiInfograph set
        if any(w in t for w in ["happy", "great", "excellent", "glad", "joy", "wonderful", "love", "smile", "laugh"]):
            return "HAPPY"
        if any(w in t for w in ["angry", "rage", "frustrated", "stop", "bad", "hate", "no", "failure", "insult"]):
            return "ANGRY"
        if any(w in t for w in ["sad", "sorry", "unfortunate", "regret", "pity", "frown", "cry", "sob", "grief"]):
            return "SAD"
        if any(w in t for w in ["think", "wonder", "ponder", "maybe", "curious", "query", "hmmm", "perhaps", "logic"]):
            return "THINKING"
        if any(w in t for w in ["wow", "amaze", "surprise", "incredible", "shock", "whoa", "unbelievable", "magical"]):
            return "WONDER"

        return "NEUTRAL"

    def shutdown(self):
        """Gracefully terminates all sensory and neural subsystems."""
        log_event("TRIAD", "INITIATING SHUTDOWN SEQUENCE...")

        # 1. Stop Audio
        if self.audio:
            log_event("TRIAD", "Stopping Audio Engine...")
            try:
                self.audio.stop_stream()
                # Close PyAudio instance if accessible, otherwise engine handles it
            except Exception as e:
                log_event("TRIAD", f"Audio Shutdown Warning: {e}", level="WARNING")

        # 2. Release Vision
        if self.vision:
             log_event("TRIAD", "Releasing Vision Hardware...")
             try:
                 # Manually release all capture objects to ensure red lights go off
                 if hasattr(self.vision, 'caps'):
                     for cid, cap in list(self.vision.caps.items()):
                         if cap:
                             try:
                                 if hasattr(cap, 'release') and cap.isOpened():
                                     cap.release()
                                     log_event("TRIAD", f"Released Camera {cid}")
                             except Exception as ce:
                                 log_event("TRIAD", f"Camera {cid} release warning: {ce}", level="WARNING")
                     self.vision.caps.clear()

                 # Force close PS Eye driver if available (turns off red lights)
                 try:
                     from pseyepy import Camera
                     Camera.close_all()
                     log_event("TRIAD", "PS Eye driver closed (all cameras)")
                 except ImportError:
                     pass  # pseyepy not installed
                 except Exception as pe:
                     log_event("TRIAD", f"PS Eye close_all warning: {pe}", level="WARNING")

             except Exception as e:
                 log_event("TRIAD", f"Vision Shutdown Warning: {e}", level="WARNING")

        # 3. Unload Models (VRAM)
        log_event("TRIAD", "Unloading Neural Models...")
        self.left = None
        self.right = None
        self.colossus = None
        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        log_event("TRIAD", "Shutdown Sequence Complete. System Halted.")

    def get_hardware_status(self):
        """Integrates hardware intelligence (OrbCamera/Kinect)"""
        return {
            "vram_allocated": torch.cuda.memory_allocated() / 1e9 if torch.cuda.is_available() else 0,
            "triad_active": True,
            "sensory_ready": self.vision.hardware_metadata is not None if self.vision else False,
            "avatar_active": self.is_avatar_active
        }

def load_unified_triad(config_path: str):
    """Helper to instantiate the unified brain."""
    return UnifiedBrainTriad(config_path)
