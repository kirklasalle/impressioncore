"""
ImpressionCore Services Layer
============================

Service layer components for API, backend, and middleware functionality.

File: services/__init__.py
Project: ImpressionCore
Created: 2025-01-07

Components:
- api/: REST API endpoints and handlers
- assistant/: AI assistant service components
- backend/: Backend service implementations
- middleware/: Service middleware and interceptors
"""

from . import api
from . import assistant
from . import backend
from . import middleware

__all__ = ['api', 'assistant', 'backend', 'middleware']
