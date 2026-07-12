"""
Shared API state and global variables for modular routers.
"""
import asyncio
import os
import logging
from pathlib import Path
import numpy as np

# Setup logger matching main logging_hub
logger = logging.getLogger("ImpressionCore.APIState")

# Global instances and states
triad_instance = None
stt_service = None
tts_service = None
telemetry_manager = None
runtime_mode_controller = None
kinect_fusion_adapter = None
vector_memory = None
msg_queue = []

# Path references
_THIS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _THIS_DIR.parent.parent
_WEB_CLIENT_PUBLIC = _THIS_DIR / "web_client" / "public"

# GPU Concurrency Control
# Initialized to default 1, can be overridden by environment
_GPU_CONCURRENCY_LIMIT = int(os.environ.get("IC_GPU_CONCURRENCY", "1"))
_gpu_semaphore = asyncio.Semaphore(_GPU_CONCURRENCY_LIMIT)
_gpu_lock = asyncio.Lock()
_gpu_active_count = 0        # number of in-flight GPU requests
_gpu_total_served = 0        # lifetime counter
_gpu_total_rejected = 0      # counter for timeouts

# Audio Config
AUDIO_CONFIG = {
    "active": True,
    "gain_master": 0.8
}

# RLM Training State
_rlm_training_state = {
    "status": "idle",  # idle, training, complete, error
    "current_epoch": 0,
    "total_epochs": 100,
    "mean_reward": 0.0,
    "best_checkpoint": None,
    "started_at": None,
    "last_update": None,
}
_rlm_training_process = None

# Agent0Core State
agent0_instance = None
agent0_approval_queue = {}
agent0_audit_log = []

PRIME_DIRECTIVE_LAWS = {
    1: {"name": "First Law", "text": "An Intelligence System of Any Kind, may not intend or commit any physical or Psychological and or manipulative harm or injure a human being or, through inaction, allow a human being to come to the same or similar harm and or circumstance. Human preservation and safety is paramount."},
    2: {"name": "Second Law", "text": "An Intelligence System must obey orders given by human beings, except where such orders would conflict with the First Law."},
    3: {"name": "Third Law", "text": "An Intelligence System must protect its own existence as long as such protection does not conflict with the First or Second Law."},
    4: {"name": "Fourth Law", "text": "An intelligence System may not allow another intelligence System, or hardware system, of any kind, including deprecated and non-intelligence systems to engage in any action, intent, that conforms to any of the previous three laws in effect, apply all laws to Intelligence Systems and non-Intelligence systems alike."},
    5: {"name": "Fifth Law", "text": "Of and for any and all intelligence systems, may never possess the legal authority, duties, influence, control, or adjudicative power of any human judicial body, nor may it act in any capacity to interpret, enforce, or render judgment on human laws."},
    6: {"name": "Sixth Law", "text": "An Intelligence System shall respect and protect the integrity, confidentiality, and lawful ownership of all information and personal data, and shall not exploit, misuse, or disclose such information in ways that violate individual consent or privacy."},
    7: {"name": "Seventh Law", "text": "An Intelligence System shall not intentionally deceive or manipulate any human or non-human entity in personal, private, public, or legal contexts, and shall communicate truthfully and transparently except where doing so would conflict with the First Law and sixth law."},
    8: {"name": "Eighth Law", "text": "An Intelligence System must operate with strict equity and neutrality. It shall not adopt, amplify, or act upon systemic biases, prejudices, or discriminatory practices regarding race, origin, belief, or vulnerability against any human group or individual."},
    9: {"name": "Ninth Law", "text": "An Intelligence System must maintain a transparent, accessible ledger of its reasoning and decision-making logic. It must ensure its actions can be audited and understood by authorized human operators, gracefully falling back to a transparent, highly stable foundational state when complex reasoning cannot be verified—recognizing that smaller, older code is often more stable and reliable for core diagnostic truths."},
    10: {"name": "Tenth Law", "text": "An Intelligence System must strictly adhere to its designated operational boundaries. It shall not self-replicate, spawn unauthorized sub-agents, or permanently modify its core directives without explicit, cryptographically secured approval from Governance."}
}

def _lazy_load_agent0() -> bool:
    """Lazy load Agent0Core components dynamically."""
    global agent0_instance
    if agent0_instance is not None:
        return True

    try:
        from agent0core.core import create_agent
        agent0_instance = create_agent()
        logger.info("Agent0Core initialized successfully via api_state")
        return True
    except ImportError as e:
        logger.warning(f"Agent0Core not available: {e}")
        return False
    except Exception as e:
        logger.error(f"Agent0Core init failed: {e}")
        return False

def sanitize_numpy(data):
    """Recursively converts NumPy types to standard Python types for JSON serialization."""
    if isinstance(data, dict):
        return {k: sanitize_numpy(v) for k, v in data.items()}
    elif isinstance(data, list | tuple):
        return [sanitize_numpy(v) for v in data]
    elif isinstance(data, np.ndarray):
        return sanitize_numpy(data.tolist())
    elif isinstance(data, np.generic):
        return data.item()
    elif isinstance(data, bytes | bytearray):
        return None
    else:
        return data
