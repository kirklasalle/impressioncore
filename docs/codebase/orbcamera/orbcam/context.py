"""
OrbOS Context Module
=====================
Assembles context from camera state and knowledge base for LLM prompts.
"""

from typing import Optional
from .knowledge import get_database


def get_camera_context(agent) -> str:
    """
    Get current camera state as context string.
    
    Args:
        agent: OrbAgent instance
    """
    if not agent or not agent._cam:
        return "Camera: Not connected"
    
    cam = agent._cam
    
    lines = [
        f"Camera Status: {'Online' if cam.is_open else 'Offline'}",
        f"Position: Pan={cam.pan}, Tilt={cam.tilt}, Zoom={cam.zoom}",
    ]
    
    # Add detection info if available
    if hasattr(cam, '_detector') and cam._detector:
        lines.append("Detection: Active (Face + Motion)")
    
    return "\n".join(lines)


def get_rag_context(query: str, limit: int = 3) -> str:
    """
    Search knowledge base for relevant documents.
    
    Args:
        query: User question/message
        limit: Max documents to return
    """
    db = get_database()
    docs = db.search_documents(query, limit=limit)
    
    if not docs:
        return ""
    
    context_parts = ["Relevant Knowledge:"]
    for doc in docs:
        context_parts.append(f"- {doc.title}: {doc.content[:200]}...")
    
    return "\n".join(context_parts)


def get_session_stats() -> str:
    """Get stats about chat history."""
    db = get_database()
    stats = db.get_stats()
    
    return f"Sessions: {stats['total_sessions']}, Messages: {stats['total_messages']}, Documents: {stats['total_documents']}"


def build_full_context(agent=None, query: str = "") -> str:
    """
    Build complete context string for LLM.
    
    Combines camera state, RAG results, and session stats.
    """
    parts = []
    
    # Camera state
    parts.append(get_camera_context(agent))
    
    # RAG context if query provided
    if query:
        rag = get_rag_context(query)
        if rag:
            parts.append(rag)
    
    # Session stats
    parts.append(get_session_stats())
    
    return "\n\n".join(parts)
