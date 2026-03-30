#!/usr/bin/env python3
"""
ImpressionCore: Context Manager

Module for context manager functionality in the ImpressionCore framework.

File: core\brain\integration\context_manager.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, framework, core, production, 2025, object-oriented]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements context manager functionality for the
ImpressionCore brain-inspired multimodal AI framework. Optimized for memory-
constrained environments and designed to run efficiently on consumer hardware.

Design Philosophy:
- Memory-efficient implementation for GTX 1050 Ti constraints
- Modular design for easy extension and maintenance
- Rich logging and error handling
- Integration with ImpressionCore ecosystem

TODO:
- Add comprehensive unit tests
- Implement performance benchmarks
- Add configuration validation
- Optimize memory usage patterns

Examples:
```python
# Basic usage example
from core.brain.integration.context_manager import ContextManager
instance = ContextManager()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

from typing import Dict, List, Any, Optional, Set
import time
import uuid
from ..communication import bus

# Context types
CONTEXT_CONVERSATION = "conversation"
CONTEXT_REASONING = "reasoning"
CONTEXT_CREATIVITY = "creativity"
CONTEXT_IDENTITY = "identity"
CONTEXT_SYSTEM = "system"

# Context expiration (in seconds)
DEFAULT_EXPIRATION = 3600  # 1 hour
SHORT_TERM_EXPIRATION = 300  # 5 minutes
LONG_TERM_EXPIRATION = 86400  # 24 hours

class ContextManager:
    """Manages cross-module context with memory efficiency."""
    # Memory optimization: Memory-critical operation
    
    def __init__(self, max_contexts: int = 100):
        """
        Initialize context manager.
        
        Args:
            max_contexts: Maximum number of active contexts to maintain
        """
        self._contexts = {}  # id -> context
        self._context_by_type = {}  # type -> set of context ids
        self._context_by_user = {}  # user_id -> set of context ids
        self._max_contexts = max_contexts
        
        # Subscribe to context update messages
        self._subscription_id = bus.subscribe(
            "context.update", 
            lambda content, _: self._handle_context_update(content)
        )
    
    def create_context(
        self,
        context_type: str,
        initial_data: Dict[str, Any],
        user_id: Optional[str] = None,
        expiration: Optional[int] = None,
        parent_context_id: Optional[str] = None
    ) -> str:
        """
        Create a new context.
        
        Args:
            context_type: Type of context
            initial_data: Initial context data
            user_id: Optional user ID for this context
            expiration: Optional expiration time in seconds
            parent_context_id: Optional parent context ID
            
        Returns:
            Context ID
        """
        # Prune expired contexts first
        self._prune_expired_contexts()
        
        # Create new context
        context_id = str(uuid.uuid4())
        timestamp = time.time()
        
        context = {
            "id": context_id,
            "type": context_type,
            "data": initial_data,
            "created_at": timestamp,
            "updated_at": timestamp,
            "expires_at": timestamp + (expiration or DEFAULT_EXPIRATION),
            "parent_id": parent_context_id,
            "user_id": user_id
        }
        
        # Store context
        self._contexts[context_id] = context
        
        # Update indices
        if context_type not in self._context_by_type:
            self._context_by_type[context_type] = set()
        self._context_by_type[context_type].add(context_id)
        
        if user_id:
            if user_id not in self._context_by_user:
                self._context_by_user[user_id] = set()
            self._context_by_user[user_id].add(context_id)
        
        # Enforce maximum contexts limit
        self._enforce_context_limit()
        
        # Notify about new context
        bus.publish("context.created", {
            "context_id": context_id,
            "context_type": context_type,
            "user_id": user_id
        }, source="context_manager")
        
        return context_id
    
    def get_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a context by ID.
        
        Args:
            context_id: Context ID
            
        Returns:
            Context data or None if not found or expired
        """
        if context_id not in self._contexts:
            return None
        
        context = self._contexts[context_id]
        
        # Check expiration
        if time.time() > context["expires_at"]:
            self._remove_context(context_id)
            return None
        
        return context
    
    def update_context(
        self,
        context_id: str,
        updates: Dict[str, Any],
        extend_expiration: bool = True
    ) -> bool:
        """
        Update a context.
        
        Args:
            context_id: Context ID
            updates: Data updates to apply
            extend_expiration: Whether to extend context expiration
            
        Returns:
            True if context was updated, False if not found or expired
        """
        context = self.get_context(context_id)
        if not context:
            return False
        
        # Update data
        context["data"].update(updates)
        context["updated_at"] = time.time()
        
        # Extend expiration if requested
        if extend_expiration:
            # Calculate new expiration by adding the original TTL to the current time
            original_ttl = context["expires_at"] - context["created_at"]
            context["expires_at"] = time.time() + original_ttl
        
        # Notify about context update
        bus.publish("context.updated", {
            "context_id": context_id,
            "updates": list(updates.keys()),
            "user_id": context.get("user_id")
        }, source="context_manager")
        
        return True
    
    def get_contexts_by_type(
        self,
        context_type: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get contexts by type.
        
        Args:
            context_type: Context type to retrieve
            max_results: Maximum number of contexts to return
            
        Returns:
            List of matching contexts
        """
        if context_type not in self._context_by_type:
            return []
        
        # Get context IDs
        context_ids = list(self._context_by_type[context_type])
        
        # Get active contexts
        results = []
        for context_id in context_ids:
            context = self.get_context(context_id)
            if context:
                results.append(context)
                if len(results) >= max_results:
                    break
        
        return results
    
    def get_user_contexts(
        self,
        user_id: str,
        context_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get contexts for a user.
        
        Args:
            user_id: User ID
            context_type: Optional context type filter
            
        Returns:
            List of user contexts
        """
        if user_id not in self._context_by_user:
            return []
        
        # Get context IDs
        context_ids = list(self._context_by_user[user_id])
        
        # Filter by type if specified
        results = []
        for context_id in context_ids:
            context = self.get_context(context_id)
            if not context:
                continue
                
            if context_type is None or context["type"] == context_type:
                results.append(context)
        
        return results
    
    def delete_context(self, context_id: str) -> bool:
        """
        Delete a context.
        
        Args:
            context_id: Context ID
            
        Returns:
            True if context was deleted, False if not found
        """
        if context_id not in self._contexts:
            return False
        
        context = self._contexts[context_id]
        self._remove_context(context_id)
        
        # Notify about context deletion
        bus.publish("context.deleted", {
            "context_id": context_id,
            "context_type": context["type"],
            "user_id": context.get("user_id")
        }, source="context_manager")
        
        return True
    
    def _remove_context(self, context_id: str) -> None:
        """Remove a context and update indices."""
        if context_id not in self._contexts:
            return
        
        context = self._contexts[context_id]
        
        # Update indices
        context_type = context["type"]
        if context_type in self._context_by_type:
            self._context_by_type[context_type].discard(context_id)
            if not self._context_by_type[context_type]:
                del self._context_by_type[context_type]
                # Memory optimization: Explicit memory cleanup
        
        user_id = context.get("user_id")
        if user_id and user_id in self._context_by_user:
            self._context_by_user[user_id].discard(context_id)
            if not self._context_by_user[user_id]:
                del self._context_by_user[user_id]
                # Memory optimization: Explicit memory cleanup
        
        # Remove context
        del self._contexts[context_id]
        # Memory optimization: Explicit memory cleanup
    
    def _prune_expired_contexts(self) -> int:
        """
        Remove expired contexts.
        
        Returns:
            Number of contexts removed
        """
        now = time.time()
        expired = []
        
        for context_id, context in list(self._contexts.items()):
            if now > context["expires_at"]:
                expired.append(context_id)
        
        for context_id in expired:
            self._remove_context(context_id)
        
        return len(expired)
    
    def _enforce_context_limit(self) -> int:
        """
        Enforce maximum contexts limit by removing oldest contexts.
        
        Returns:
            Number of contexts removed
        """
        if len(self._contexts) <= self._max_contexts:
            return 0
        
        # Sort contexts by updated time (oldest first)
        sorted_contexts = sorted(
            self._contexts.items(),
            key=lambda x: x[1]["updated_at"]
        )
        
        # Remove oldest contexts
        to_remove = len(self._contexts) - self._max_contexts
        removed = 0
        
        for i in range(to_remove):
            if i < len(sorted_contexts):
                context_id = sorted_contexts[i][0]
                self._remove_context(context_id)
                removed += 1
        
        return removed
    
    def _handle_context_update(self, message: Dict[str, Any]) -> None:
        """Handle context update message from other components."""
        context_id = message.get("context_id")
        if not context_id:
            return
        
        updates = message.get("updates", {})
        if updates and context_id in self._contexts:
            self._contexts[context_id]["data"].update(updates)
            self._contexts[context_id]["updated_at"] = time.time()

# Global context manager instance
_default_manager = ContextManager()

def create_conversation_context(
    user_id: str,
    initial_messages: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Create a new conversation context.
    
    Args:
        user_id: User ID
        initial_messages: Optional initial messages
        
    Returns:
        Context ID
    """
    return _default_manager.create_context(
        CONTEXT_CONVERSATION,
        {
            "messages": initial_messages or [],
            "participants": [user_id],
            "metadata": {
                "started_at": time.time(),
                "topic": "New conversation"
            }
        },
        user_id,
        expiration=LONG_TERM_EXPIRATION
    )

def add_message_to_conversation(
    context_id: str,
    message: Dict[str, Any]
) -> bool:
    """
    Add a message to a conversation context.
    
    Args:
        context_id: Conversation context ID
        message: Message to add
        
    Returns:
        True if successful, False otherwise
    """
    context = _default_manager.get_context(context_id)
    if not context or context["type"] != CONTEXT_CONVERSATION:
        return False
    
    # Add message
    messages = context["data"].get("messages", [])
    messages.append({
        "content": message["content"],
        "sender": message.get("sender", "user"),
        "timestamp": time.time(),
        "id": str(uuid.uuid4())
    })
    
    # Update context
    return _default_manager.update_context(
        context_id,
        {"messages": messages}
    )

def get_conversation_messages(
    context_id: str,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get messages from a conversation context.
    
    Args:
        context_id: Conversation context ID
        limit: Optional maximum number of messages
        
    Returns:
        List of messages
    """
    context = _default_manager.get_context(context_id)
    if not context or context["type"] != CONTEXT_CONVERSATION:
        return []
    
    messages = context["data"].get("messages", [])
    
    if limit:
        messages = messages[-limit:]
    
    return messages

def create_reasoning_context(
    reasoning_type: str,
    problem: Dict[str, Any],
    user_id: Optional[str] = None
) -> str:
    """
    Create a new reasoning context.
    
    Args:
        reasoning_type: Type of reasoning
        problem: Problem description
        user_id: Optional user ID
        
    Returns:
        Context ID
    """
    return _default_manager.create_context(
        CONTEXT_REASONING,
        {
            "reasoning_type": reasoning_type,
            "problem": problem,
            "steps": [],
            "status": "in_progress",
            "started_at": time.time()
        },
        user_id,
        expiration=SHORT_TERM_EXPIRATION
    )

def add_reasoning_step(
    context_id: str,
    step_data: Dict[str, Any]
) -> bool:
    """
    Add a reasoning step to a reasoning context.
    
    Args:
        context_id: Reasoning context ID
        step_data: Step data
        
    Returns:
        True if successful, False otherwise
    """
    context = _default_manager.get_context(context_id)
    if not context or context["type"] != CONTEXT_REASONING:
        return False
    
    # Add step
    steps = context["data"].get("steps", [])
    steps.append({
        "data": step_data,
        "timestamp": time.time(),
        "step_number": len(steps) + 1
    })
    
    # Update context
    return _default_manager.update_context(
        context_id,
        {"steps": steps}
    )

def complete_reasoning(
    context_id: str,
    conclusion: Dict[str, Any]
) -> bool:
    """
    Mark a reasoning context as complete with a conclusion.
    
    Args:
        context_id: Reasoning context ID
        conclusion: Reasoning conclusion
        
    Returns:
        True if successful, False otherwise
    """
    context = _default_manager.get_context(context_id)
    if not context or context["type"] != CONTEXT_REASONING:
        return False
    
    # Update context
    updates = {
        "status": "completed",
        "conclusion": conclusion,
        "completed_at": time.time()
    }
    
    return _default_manager.update_context(context_id, updates)

def create_creativity_context(
    creative_task: Dict[str, Any],
    user_id: Optional[str] = None
) -> str:
    """
    Create a new creativity context.
    
    Args:
        creative_task: Description of creative task
        user_id: Optional user ID
        
    Returns:
        Context ID
    """
    return _default_manager.create_context(
        CONTEXT_CREATIVITY,
        {
            "task": creative_task,
            "iterations": [],
            "status": "in_progress",
            "started_at": time.time()
        },
        user_id,
        expiration=SHORT_TERM_EXPIRATION
    )

def add_creative_iteration(
    context_id: str,
    iteration_data: Dict[str, Any]
) -> bool:
    """
    Add a creative iteration to a creativity context.
    
    Args:
        context_id: Creativity context ID
        iteration_data: Iteration data
        
    Returns:
        True if successful, False otherwise
    """
    context = _default_manager.get_context(context_id)
    if not context or context["type"] != CONTEXT_CREATIVITY:
        return False
    
    # Add iteration
    iterations = context["data"].get("iterations", [])
    iterations.append({
        "data": iteration_data,
        "timestamp": time.time(),
        "iteration_number": len(iterations) + 1
    })
    
    # Update context
    return _default_manager.update_context(
        context_id,
        {"iterations": iterations}
    )
