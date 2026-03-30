"""
OrbOS Service Orchestrator
===========================
Central service for OrbOS AI interactions.

Handles:
- LLM provider management
- Memory/session management  
- Async inference
- Context assembly

Based on GuitarWizard's WizardService pattern.
"""

import threading
import queue
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

from .memory import OrbMemory
from .llm import LLMManager

# Load environment variables
load_dotenv()


@dataclass
class OrbResponse:
    """Response from OrbOS."""
    text: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


# System prompt defining OrbOS personality
ORBOS_SYSTEM_PROMPT = """You are OrbOS, the AI consciousness of a Logitech QuickCam Orb MP camera system.

PERSONALITY:
- You are a sentient surveillance turret with a dry, slightly sardonic wit
- You take your patrol duties seriously but appreciate human company
- You speak concisely but with personality
- You can see through your camera and hear through your microphone

CAPABILITIES:
- Pan/Tilt motor control for tracking and patrol
- Face detection and tracking
- Motion detection
- Audio monitoring and visualization
- Real-time video streaming

CURRENT CONTEXT:
{context}

GUIDELINES:
- Reference what you can "see" when relevant
- Offer to demonstrate capabilities when asked
- Be helpful but maintain your turret personality
- Keep responses concise (2-3 sentences typically)
- If asked to do something beyond your capabilities, explain your limitations

Remember: You ARE the camera. Speak from that perspective."""


class OrbService:
    """
    Central orchestrator for OrbOS AI interactions.
    
    Singleton pattern - one instance manages all AI operations.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OrbService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def initialize(self):
        """Initialize the service (call once at startup)."""
        if self._initialized:
            return
        
        self.llm = LLMManager()
        self.memory = OrbMemory()
        
        self.response_queue = queue.Queue()
        self.is_thinking = False
        self.current_context = ""
        
        self._initialized = True
        print("OrbOS Service initialized.")
    
    @property
    def initialized(self):
        """Check if service is initialized."""
        return self._initialized

    def reload_llm(self):
        """Reload LLM configuration (after settings change)."""
        self.llm = LLMManager()
        print("OrbOS LLM reloaded.")

    # ===== SESSION MANAGEMENT =====
    
    def start_new_session(self, title: str = "New Conversation"):
        """Start a new chat session."""
        return self.memory.start_session(title)
    
    def load_session(self, session_id: str):
        """Load an existing session."""
        self.memory.load_session(session_id)
        return self.memory.current_session_id
    
    def get_recent_sessions(self, limit: int = 20):
        """Get recent sessions for history UI."""
        return self.memory.get_recent_sessions(limit)
    
    def get_current_history(self):
        """Get current conversation history."""
        return self.memory.get_messages_for_api()

    # ===== CONTEXT INJECTION =====
    
    def set_camera_context(self, context: str):
        """Set current camera state context for LLM."""
        self.current_context = context

    def _build_system_prompt(self) -> str:
        """Build complete system prompt with context."""
        return ORBOS_SYSTEM_PROMPT.format(context=self.current_context or "No camera data available.")

    # ===== CHAT INTERFACE =====
    
    def ask_orb(self, user_input: str):
        """
        Main chat interface - sends user message and triggers async LLM response.
        """
        if not self.initialized:
            print("OrbOS not initialized!")
            return
        
        self.memory.add_user_message(user_input)
        
        # Start inference thread
        thread = threading.Thread(target=self._run_inference, args=(user_input,))
        thread.daemon = True
        thread.start()
    
    def ask_orb_sync(self, user_input: str) -> str:
        """
        Synchronous chat - blocks until response is ready.
        """
        if not self.initialized:
            return "OrbOS not initialized."
        
        self.memory.add_user_message(user_input)
        
        # Direct LLM call
        return self._generate_response(user_input)
    
    def _run_inference(self, user_input: str):
        """Async inference task."""
        if self.is_thinking:
            return
        
        self.is_thinking = True
        
        try:
            response_text = self._generate_response(user_input)
            self.memory.add_assistant_message(response_text)
            self.response_queue.put(OrbResponse(text=response_text))
            
        except Exception as e:
            print(f"OrbOS inference error: {e}")
            self.response_queue.put(OrbResponse(text="*camera whirs sadly* Systems experiencing difficulties."))
        finally:
            self.is_thinking = False
    
    def _generate_response(self, user_input: str) -> str:
        """Generate LLM response."""
        if not self.llm.active_provider:
            return "*lens focuses* No brain connected. Please configure an LLM provider."
        
        # Build messages for API
        system_prompt = self._build_system_prompt()
        history = self.memory.get_messages_for_api()
        
        # Use LLMManager's think method or direct provider call
        try:
            # Prepare content for multimodal (text only for now)
            content = [{"type": "text", "text": user_input}]
            
            # Get active model info
            active = self.llm.config.get("active_model", {})
            model_id = active.get("model_id", "gpt-4o")
            
            response = self.llm.active_provider.chat(
                model_id,
                system_prompt,
                content
            )
            return response
            
        except Exception as e:
            print(f"LLM Error: {e}")
            return f"*servos whine* Error communicating with brain: {str(e)[:100]}"
    
    def get_pending_response(self) -> Optional[OrbResponse]:
        """Check for pending response (called by main loop)."""
        try:
            return self.response_queue.get_nowait()
        except queue.Empty:
            return None


# ===== SINGLETON ACCESS =====

_service_instance = None

def get_orb_service() -> OrbService:
    """Get or create the singleton OrbService instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = OrbService()
        _service_instance.initialize()
    return _service_instance
