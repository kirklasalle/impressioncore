import json
import os
import uuid
from datetime import datetime
from typing import Any


class SessionManager:
    """
    Manages persistent chat sessions stored as JSON files.
    """
    def __init__(self, history_dir: str = "history"):
        self.history_dir = history_dir
        os.makedirs(self.history_dir, exist_ok=True)

    def _get_path(self, session_id: str) -> str:
        return os.path.join(self.history_dir, f"{session_id}.json")

    def list_sessions(self) -> list[dict[str, Any]]:
        """Lists all available sessions with metadata."""
        sessions = []
        for filename in os.listdir(self.history_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.history_dir, filename)
                try:
                    with open(path, encoding="utf-8") as f:
                        data = json.load(f)
                        sessions.append({
                            "id": data.get("id"),
                            "title": data.get("title", "Untitled Session"),
                            "updated_at": data.get("updated_at"),
                            "message_count": len(data.get("messages", []))
                        })
                except Exception:
                    continue
        # Sort by updated_at descending
        return sorted(sessions, key=lambda x: x.get("updated_at", ""), reverse=True)

    def create_session(self, title: str = "New Chat") -> str:
        """Creates a new session and returns the ID."""
        session_id = str(uuid.uuid4())
        data = {
            "id": session_id,
            "title": title,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": []
        }
        self.save_session(session_id, data)
        return session_id

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        """Loads a session from disk."""
        path = self._get_path(session_id)
        if not os.path.exists(path):
            return None
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def save_session(self, session_id: str, data: dict[str, Any]):
        """Persists session data to disk."""
        path = self._get_path(session_id)
        data["updated_at"] = datetime.now().isoformat()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def add_message(self, session_id: str, role: str, content: str, audio_url: str | None = None, snapshot_url: str | None = None, snapshot_urls: list[str] | None = None, generated_image_url: str | None = None):
        """Appends a message to a session with optional media URLs."""
        data = self.get_session(session_id)
        if not data:
            # Auto-create if missing? Or error? Let's auto-create.
            data = {
                "id": session_id,
                "title": content[:30] + "..." if len(content) > 30 else content,
                "created_at": datetime.now().isoformat(),
                "messages": []
            }

        # If it's the first message, maybe update title
        if len(data["messages"]) == 0 and data.get("title") == "New Chat":
            data["title"] = content[:30] + "..." if len(content) > 30 else content

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }

        # Add optional media URLs
        if audio_url:
            message["audio_url"] = audio_url
        if snapshot_url:
            message["snapshot_url"] = snapshot_url
        if snapshot_urls:
            message["snapshot_urls"] = snapshot_urls
        if generated_image_url:
            message["generated_image_url"] = generated_image_url

        data["messages"].append(message)
        self.save_session(session_id, data)

    def delete_session(self, session_id: str) -> bool:
        """Deletes a session file."""
        path = self._get_path(session_id)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def search_memory(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Searches across all sessions for relevant snippets."""
        query = query.lower()
        results = []
        for filename in os.listdir(self.history_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.history_dir, filename)
                try:
                    with open(path, encoding="utf-8") as f:
                        data = json.load(f)
                        for msg in data.get("messages", []):
                            content = msg.get("content", "")
                            if query in content.lower():
                                results.append({
                                    "session_id": data.get("id"),
                                    "session_title": data.get("title"),
                                    "role": msg.get("role"),
                                    "content": content,
                                    "timestamp": msg.get("timestamp")
                                })
                except Exception:
                    continue

        # Sort by timestamp descending
        results = sorted(results, key=lambda x: x.get("timestamp", ""), reverse=True)
        return results[:limit]

    def get_global_context(self) -> str:
        """Returns a brief summary of the last 3 sessions for contextual continuity."""
        sessions = self.list_sessions()[:3]
        if not sessions:
            return "No previous session history found."

        summary = "Recent Session History:\n"
        for s in sessions:
            updated = s.get('updated_at', 'unknown').split('T')[0]
            summary += f"- {s['title']} (Last Active: {updated}, Messages: {s['message_count']})\n"
        return summary

# Global instance
session_manager = SessionManager()
