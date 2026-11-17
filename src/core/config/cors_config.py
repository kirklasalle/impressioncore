"""
CORS Configuration Utility

Centralizes CORS (Cross-Origin Resource Sharing) policy for all
ImpressionCore API surfaces. Uses environment variables so development
can remain permissive while production is locked down.

Created: February 16, 2026
Author: ImpressionCore Team
Status: Active
"""

import os
from typing import List


def get_allowed_origins() -> list[str]:
    """Return the list of allowed CORS origins from environment.

    Set IMPRESSIONCORE_ALLOWED_ORIGINS as a comma-separated string of
    origins in production.  Defaults to localhost-only for development.

    Examples:
        export IMPRESSIONCORE_ALLOWED_ORIGINS="https://app.example.com,https://admin.example.com"
        export IMPRESSIONCORE_ALLOWED_ORIGINS="*"  # Only for local dev
    """
    env_value = os.getenv("IMPRESSIONCORE_ALLOWED_ORIGINS", "").strip()
    if env_value:
        return [origin.strip() for origin in env_value.split(",") if origin.strip()]
    # Safe default: localhost on common dev ports
    return [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ]
