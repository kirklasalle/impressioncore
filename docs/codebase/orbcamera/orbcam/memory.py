"""
OrbOS Memory Module
====================
Manages conversation memory with short-term buffer and persistent storage.

Based on GuitarWizard's memory pattern.
"""

from collections import deque
from typing import List, Dict, Deque, Optional
from .knowledge import get_database


class OrbMemory:
    """
    Manages the 'Memory' of OrbOS.
    1. Short-term: Conversation history (last N messages in RAM).
    2. Persistent: SQL Database (Chat Sessions).
    """
    
    def __init__(self, history_limit: int = 20):
        self.db = get_database()
        self.conversation_history: Deque[dict] = deque(maxlen=history_limit)
        self.current_session_id: Optional[str] = None
        
    def start_session(self, title: str = "New Conversation"):
        """Starts a new chat session."""
        session = self.db.create_chat_session(title)
        self.current_session_id = session.id
        self.conversation_history.clear()
        return session
        
    def load_session(self, session_id: str):
        """Loads an existing session."""
        self.current_session_id = session_id
        messages = self.db.get_session_messages(session_id)
        self.conversation_history.clear()
        for msg in messages:
            self.conversation_history.append({"role": msg.role, "content": msg.content})
    
    def get_recent_sessions(self, limit: int = 20):
        """Get recent sessions for history UI."""
        return self.db.get_recent_sessions(limit)

    def add_user_message(self, text: str):
        """Add a user message to history and persist."""
        self.conversation_history.append({"role": "user", "content": text})
        if self.current_session_id:
            self.db.add_message(self.current_session_id, "user", text)
        
    def add_assistant_message(self, text: str):
        """Add an assistant message to history and persist."""
        self.conversation_history.append({"role": "assistant", "content": text})
        if self.current_session_id:
            self.db.add_message(self.current_session_id, "assistant", text)
            
            # Auto-title session from first assistant response
            if len(self.conversation_history) == 2:  # First exchange
                # Use first 50 chars of response as title
                title = text[:50] + "..." if len(text) > 50 else text
                self.db.update_session_title(self.current_session_id, title)
        
    def get_formatted_history(self) -> str:
        """Returns conversation history as a formatted string for the LLM."""
        output = []
        for msg in self.conversation_history:
            role = "User" if msg["role"] == "user" else "OrbOS"
            output.append(f"{role}: {msg['content']}")
        return "\n".join(output)
    
    def get_messages_for_api(self) -> List[Dict]:
        """Returns conversation history in API format."""
        return list(self.conversation_history)
    
    def clear(self):
        """Clear short-term memory (keeps DB intact)."""
        self.conversation_history.clear()
