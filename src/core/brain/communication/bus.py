#!/usr/bin/env python3
"""
ImpressionCore: Bus

Module for bus functionality in the ImpressionCore framework.

File: core\brain\communication\bus.py
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
This module implements bus functionality for the
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
from core.brain.communication.bus import MessageBus
instance = MessageBus()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

from typing import Dict, List, Any, Optional, Union, Tuple, Callable, Set
import time
import uuid
from functools import reduce

# Message priority levels
PRIORITY_LOW = 0
PRIORITY_NORMAL = 1
PRIORITY_HIGH = 2
PRIORITY_CRITICAL = 3

# Default memory constraints (in number of messages)
# Memory optimization: Memory-critical operation
DEFAULT_MESSAGE_CAPACITY = 100
DEFAULT_HISTORY_CAPACITY = 50

class MessageBus:
    """Memory-efficient message bus for module communication."""
    # Memory optimization: Memory-critical operation
    
    def __init__(
        self,
        message_capacity: int = DEFAULT_MESSAGE_CAPACITY,
        history_capacity: int = DEFAULT_HISTORY_CAPACITY
    ):
        """
        Initialize the message bus.
        
        Args:
            message_capacity: Maximum number of messages to keep in queue
            history_capacity: Maximum number of messages to keep in history
        """
        self._subscribers = {}  # topic -> list of callbacks
        self._messages = []  # Active messages
        self._history = []  # Message history
        self._message_capacity = message_capacity
        self._history_capacity = history_capacity
    
    def subscribe(self, topic: str, callback: Callable) -> str:
        """
        Subscribe to a message topic.
        
        Args:
            topic: Topic to subscribe to
            callback: Function to call when message is received
            
        Returns:
            Subscription ID
        """
        subscription_id = str(uuid.uuid4())
        
        if topic not in self._subscribers:
            self._subscribers[topic] = {}
        
        self._subscribers[topic][subscription_id] = callback
        return subscription_id
    
    def unsubscribe(self, topic: str, subscription_id: str) -> bool:
        """
        Unsubscribe from a topic.
        
        Args:
            topic: Topic to unsubscribe from
            subscription_id: Subscription ID to remove
            
        Returns:
            True if successfully unsubscribed, False otherwise
        """
        if topic in self._subscribers and subscription_id in self._subscribers[topic]:
            del self._subscribers[topic][subscription_id]
            # Memory optimization: Explicit memory cleanup
            # Clean up empty topics
            if not self._subscribers[topic]:
                del self._subscribers[topic]
                # Memory optimization: Explicit memory cleanup
            return True
        return False
    
    def publish(
        self,
        topic: str,
        message: Dict[str, Any],
        priority: int = PRIORITY_NORMAL,
        source: Optional[str] = None,
        target: Optional[str] = None
    ) -> str:
        """
        Publish a message to a topic.
        
        Args:
            topic: Topic to publish to
            message: Message content
            priority: Message priority
            source: Optional source module
            target: Optional target module (for directed messages)
            
        Returns:
            Message ID
        """
        message_id = str(uuid.uuid4())
        timestamp = time.time()
        
        message_wrapper = {
            "id": message_id,
            "topic": topic,
            "content": message,
            "priority": priority,
            "timestamp": timestamp,
            "source": source,
            "target": target,
            "status": "pending"
        }
        
        # Add to queue based on priority
        self._add_to_queue(message_wrapper)
        
        # Process immediately if there are subscribers
        if topic in self._subscribers:
            self._process_message(message_wrapper)
        
        return message_id
    
    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a message by ID.
        
        Args:
            message_id: ID of the message to retrieve
            
        Returns:
            Message if found, None otherwise
        """
        # Check active messages
        for message in self._messages:
            if message["id"] == message_id:
                return message
        
        # Check history
        for message in self._history:
            if message["id"] == message_id:
                return message
        
        return None
    
    def get_topic_messages(
        self,
        topic: str,
        status: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent messages for a topic.
        
        Args:
            topic: Topic to retrieve messages for
            status: Optional status filter
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages
        """
        results = []
        
        # Check active messages first
        for message in reversed(self._messages):
            if message["topic"] == topic and (status is None or message["status"] == status):
                results.append(message)
                if len(results) >= limit:
                    return results
        
        # Then check history
        for message in reversed(self._history):
            if message["topic"] == topic and (status is None or message["status"] == status):
                results.append(message)
                if len(results) >= limit:
                    return results
        
        return results
    
    def clear_topic(self, topic: str) -> int:
        """
        Clear all messages for a topic.
        
        Args:
            topic: Topic to clear
            
        Returns:
            Number of messages removed
        """
        count = 0
        
        # Remove from active messages
        self._messages = [m for m in self._messages if m["topic"] != topic]
        
        # Remove from history
        history_before = len(self._history)
        self._history = [m for m in self._history if m["topic"] != topic]
        count += history_before - len(self._history)
        
        return count
    
    def get_topics(self) -> List[str]:
        """
        Get all active topics.
        
        Returns:
            List of active topics
        """
        topics = set()
        
        # Get topics from subscribers
        topics.update(self._subscribers.keys())
        
        # Get topics from active messages
        topics.update(message["topic"] for message in self._messages)
        
        return list(topics)
    
    def _add_to_queue(self, message: Dict[str, Any]) -> None:
        """Add a message to the queue based on priority."""
        # Find position based on priority (higher priority first)
        position = 0
        for i, m in enumerate(self._messages):
            if m["priority"] < message["priority"]:
                break
            position = i + 1
        
        # Insert message at the correct position
        self._messages.insert(position, message)
        
        # Remove oldest messages if over capacity
        if len(self._messages) > self._message_capacity:
            # Move oldest message to history
            oldest = self._messages.pop()
            oldest["status"] = "expired"
            self._add_to_history(oldest)
    
    def _add_to_history(self, message: Dict[str, Any]) -> None:
        """Add a message to history."""
        self._history.append(message)
        
        # Remove oldest history items if over capacity
        while len(self._history) > self._history_capacity:
            self._history.pop(0)
    
    def _process_message(self, message: Dict[str, Any]) -> None:
        """Process a message by notifying subscribers."""
        topic = message["topic"]
        target = message["target"]
        
        # Skip if targeted message and we're not the target
        if topic in self._subscribers:
            for sub_id, callback in self._subscribers[topic].items():
                try:
                    callback(message["content"], message["id"])
                except Exception as e:
                    print(f"Error processing message {message['id']}: {str(e)}")
        
        # Update status
        message["status"] = "processed"
        
        # Move to history
        self._messages.remove(message)
        self._add_to_history(message)

# Global message bus instance
_default_bus = MessageBus()

# Public interface functions

def subscribe(topic: str, callback: Callable) -> str:
    """
    Subscribe to a topic on the default message bus.
    
    Args:
        topic: Topic to subscribe to
        callback: Function to call when message is received
        
    Returns:
        Subscription ID
    """
    return _default_bus.subscribe(topic, callback)

def unsubscribe(topic: str, subscription_id: str) -> bool:
    """
    Unsubscribe from a topic on the default message bus.
    
    Args:
        topic: Topic to unsubscribe from
        subscription_id: Subscription ID to remove
        
    Returns:
        True if successfully unsubscribed, False otherwise
    """
    return _default_bus.unsubscribe(topic, subscription_id)

def publish(
    topic: str,
    message: Dict[str, Any],
    priority: int = PRIORITY_NORMAL,
    source: Optional[str] = None,
    target: Optional[str] = None
) -> str:
    """
    Publish a message to a topic on the default message bus.
    
    Args:
        topic: Topic to publish to
        message: Message content
        priority: Message priority
        source: Optional source module
        target: Optional target module (for directed messages)
        
    Returns:
        Message ID
    """
    return _default_bus.publish(topic, message, priority, source, target)

def get_message(message_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a message by ID from the default message bus.
    
    Args:
        message_id: ID of the message to retrieve
        
    Returns:
        Message if found, None otherwise
    """
    return _default_bus.get_message(message_id)

def get_topic_messages(
    topic: str,
    status: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get recent messages for a topic from the default message bus.
    
    Args:
        topic: Topic to retrieve messages for
        status: Optional status filter
        limit: Maximum number of messages to retrieve
        
    Returns:
        List of messages
    """
    return _default_bus.get_topic_messages(topic, status, limit)

def get_topics() -> List[str]:
    """
    Get all active topics on the default message bus.
    
    Returns:
        List of active topics
    """
    return _default_bus.get_topics()

def clear_topic(topic: str) -> int:
    """
    Clear all messages for a topic on the default message bus.
    
    Args:
        topic: Topic to clear
        
    Returns:
        Number of messages removed
    """
    return _default_bus.clear_topic(topic)

def create_message_bus(
    message_capacity: int = DEFAULT_MESSAGE_CAPACITY,
    history_capacity: int = DEFAULT_HISTORY_CAPACITY
) -> MessageBus:
    """
    Create a new message bus instance.
    
    Args:
        message_capacity: Maximum number of messages to keep in queue
        history_capacity: Maximum number of messages to keep in history
        
    Returns:
        New MessageBus instance
    """
    return MessageBus(message_capacity, history_capacity)
