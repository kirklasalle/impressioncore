#!/usr/bin/env python3
"""
ImpressionCore: Protocols

Module for protocols functionality in the ImpressionCore framework.

File: core\brain\communication\protocols.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, framework, core, production, 2025]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements protocols functionality for the
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
from src.core.brain.communication.protocols import MainClass
instance = MainClass()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

from typing import Dict, List, Any, Optional, Union, Tuple, Callable, Set
import json
import time
from functools import wraps

# Standard message fields
FIELD_TYPE = "type"
FIELD_CONTENT = "content"
FIELD_METADATA = "metadata"
FIELD_TIMESTAMP = "timestamp"
FIELD_SENDER = "sender"
FIELD_RECIPIENT = "recipient"
FIELD_REQUEST_ID = "request_id"
FIELD_VERSION = "version"

# Message types
TYPE_REQUEST = "request"
TYPE_RESPONSE = "response"
TYPE_ERROR = "error"
TYPE_EVENT = "event"
TYPE_QUERY = "query"
TYPE_COMMAND = "command"
TYPE_STATUS = "status"
TYPE_DATA = "data"

# Error codes
ERROR_VALIDATION = "validation_error"
ERROR_PROCESSING = "processing_error"
ERROR_TIMEOUT = "timeout_error"
ERROR_PERMISSION = "permission_error"
ERROR_NOT_FOUND = "not_found_error"
ERROR_RESOURCE = "resource_error"

# Protocol versions
PROTOCOL_V1 = "1.0"
CURRENT_PROTOCOL = PROTOCOL_V1

def create_message(
    message_type: str,
    content: Any,
    sender: str,
    recipient: Optional[str] = None,
    request_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standard protocol message.
    
    Args:
        message_type: Type of message
        content: Message content
        sender: Sender identifier
        recipient: Optional recipient identifier
        request_id: Optional request ID for response correlation
        metadata: Optional metadata
        
    Returns:
        Protocol-compliant message dictionary
    """
    message = {
        FIELD_TYPE: message_type,
        FIELD_CONTENT: content,
        FIELD_SENDER: sender,
        FIELD_TIMESTAMP: time.time(),
        FIELD_VERSION: CURRENT_PROTOCOL
    }
    
    if recipient:
        message[FIELD_RECIPIENT] = recipient
    if request_id:
        message[FIELD_REQUEST_ID] = request_id
    if metadata:
        message[FIELD_METADATA] = metadata
    
    return message

def create_request(
    content: Any,
    sender: str,
    recipient: str,
    request_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a request message.
    
    Args:
        content: Request content
        sender: Sender identifier
        recipient: Recipient identifier
        request_id: Optional request ID
        metadata: Optional metadata
        
    Returns:
        Request message
    """
    return create_message(
        TYPE_REQUEST, content, sender, recipient, request_id, metadata
    )

def create_response(
    content: Any,
    sender: str,
    recipient: str,
    request_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a response message.
    
    Args:
        content: Response content
        sender: Sender identifier
        recipient: Recipient identifier
        request_id: Request ID this response corresponds to
        metadata: Optional metadata
        
    Returns:
        Response message
    """
    return create_message(
        TYPE_RESPONSE, content, sender, recipient, request_id, metadata
    )

def create_error(
    error_code: str,
    error_message: str,
    sender: str,
    recipient: Optional[str] = None,
    request_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create an error message.
    
    Args:
        error_code: Error code
        error_message: Error message
        sender: Sender identifier
        recipient: Optional recipient identifier
        request_id: Optional request ID this error corresponds to
        details: Optional error details
        
    Returns:
        Error message
    """
    content = {
        "code": error_code,
        "message": error_message
    }
    
    if details:
        content["details"] = details
    
    metadata = {"error": True}
    
    return create_message(
        TYPE_ERROR, content, sender, recipient, request_id, metadata
    )

def create_event(
    event_type: str,
    data: Any,
    sender: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create an event message.
    
    Args:
        event_type: Type of event
        data: Event data
        sender: Sender identifier
        metadata: Optional metadata
        
    Returns:
        Event message
    """
    content = {
        "event_type": event_type,
        "data": data
    }
    
    return create_message(
        TYPE_EVENT, content, sender, None, None, metadata
    )

def validate_message(message: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate a message against the protocol.
    
    Args:
        message: Message to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    required_fields = [FIELD_TYPE, FIELD_CONTENT, FIELD_SENDER, FIELD_TIMESTAMP, FIELD_VERSION]
    
    for field in required_fields:
        if field not in message:
            return False, f"Missing required field: {field}"
    
    # Check message type
    valid_types = [
        TYPE_REQUEST, TYPE_RESPONSE, TYPE_ERROR, TYPE_EVENT,
        TYPE_QUERY, TYPE_COMMAND, TYPE_STATUS, TYPE_DATA
    ]
    
    if message[FIELD_TYPE] not in valid_types:
        return False, f"Invalid message type: {message[FIELD_TYPE]}"
    
    # Check protocol version compatibility
    if message[FIELD_VERSION] != CURRENT_PROTOCOL:
        return False, f"Incompatible protocol version: {message[FIELD_VERSION]}, expected: {CURRENT_PROTOCOL}"
    
    # Type-specific validation
    if message[FIELD_TYPE] == TYPE_REQUEST and FIELD_RECIPIENT not in message:
        return False, "Request message missing recipient"
    
    if message[FIELD_TYPE] == TYPE_RESPONSE and FIELD_REQUEST_ID not in message:
        return False, "Response message missing request_id"
    
    return True, None

def protocol_handler(func: Callable) -> Callable:
    """
    Decorator for protocol message handling.
    
    Args:
        func: Function to decorate
        
    Returns:
        Wrapped function with protocol validation
    """
    @wraps(func)
    def wrapper(message: Dict[str, Any], *args, **kwargs):
        """
        
    wrapper function for processing.
    
    Args:
        message: Function parameters
    
    Returns:
        Processed result
    
    Memory Usage:
    # Memory optimization: Memory-critical operation
        - Memory-efficient implementation
        # Memory optimization: Memory-critical operation
        - Optimized for GTX 1050 Ti constraints
    
        """
        # Validate message
        is_valid, error_msg = validate_message(message)
        if not is_valid:
            error = create_error(
                ERROR_VALIDATION,
                error_msg or "Invalid message format",
                kwargs.get("sender", "protocol_handler"),
                message.get(FIELD_SENDER),
                message.get(FIELD_REQUEST_ID)
            )
            return error
        
        # Call the original function
        return func(message, *args, **kwargs)
    
    return wrapper

def serialize_message(message: Dict[str, Any]) -> str:
    """
    Serialize a message to a string.
    
    Args:
        message: Message to serialize
        
    Returns:
        Serialized message string
    """
    return json.dumps(message)

def deserialize_message(serialized: str) -> Dict[str, Any]:
    """
    Deserialize a message string.
    
    Args:
        serialized: Serialized message string
        
    Returns:
        Deserialized message
        
    Raises:
        ValueError: If message cannot be deserialized
    """
    try:
        return json.loads(serialized)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to deserialize message: {e}")

def get_request_id(message: Dict[str, Any]) -> Optional[str]:
    """
    Get request ID from a message.
    
    Args:
        message: Message to extract from
        
    Returns:
        Request ID or None
    """
    return message.get(FIELD_REQUEST_ID)

def is_response_to(response: Dict[str, Any], request: Dict[str, Any]) -> bool:
    """
    Check if a response corresponds to a request.
    
    Args:
        response: Response message
        request: Request message
        
    Returns:
        True if response corresponds to request, False otherwise
    """
    if response.get(FIELD_TYPE) not in [TYPE_RESPONSE, TYPE_ERROR]:
        return False
    
    if request.get(FIELD_TYPE) != TYPE_REQUEST:
        return False
    
    return (
        response.get(FIELD_REQUEST_ID) == request.get(FIELD_REQUEST_ID) and
        response.get(FIELD_RECIPIENT) == request.get(FIELD_SENDER) and
        response.get(FIELD_SENDER) == request.get(FIELD_RECIPIENT)
    )

def is_error(message: Dict[str, Any]) -> bool:
    """
    Check if a message is an error.
    
    Args:
        message: Message to check
        
    Returns:
        True if message is an error, False otherwise
    """
    return message.get(FIELD_TYPE) == TYPE_ERROR
