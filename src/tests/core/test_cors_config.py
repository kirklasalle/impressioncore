"""Unit tests for src.core.config.cors_config."""

import os
from unittest.mock import patch

from src.core.config.cors_config import get_allowed_origins


class TestGetAllowedOrigins:
    def test_default_returns_localhost_origins(self):
        with patch.dict(os.environ, {}, clear=True):
            # Remove IMPRESSIONCORE_ALLOWED_ORIGINS if set
            os.environ.pop("IMPRESSIONCORE_ALLOWED_ORIGINS", None)
            origins = get_allowed_origins()
            assert "http://localhost:3000" in origins
            assert "http://localhost:5173" in origins
            assert len(origins) == 6

    def test_env_override_single(self):
        with patch.dict(os.environ, {"IMPRESSIONCORE_ALLOWED_ORIGINS": "https://app.example.com"}):
            origins = get_allowed_origins()
            assert origins == ["https://app.example.com"]

    def test_env_override_multiple(self):
        with patch.dict(os.environ, {"IMPRESSIONCORE_ALLOWED_ORIGINS": "https://a.com, https://b.com"}):
            origins = get_allowed_origins()
            assert origins == ["https://a.com", "https://b.com"]

    def test_env_wildcard(self):
        with patch.dict(os.environ, {"IMPRESSIONCORE_ALLOWED_ORIGINS": "*"}):
            origins = get_allowed_origins()
            assert origins == ["*"]

    def test_empty_env_returns_defaults(self):
        with patch.dict(os.environ, {"IMPRESSIONCORE_ALLOWED_ORIGINS": ""}):
            origins = get_allowed_origins()
            assert len(origins) == 6

    def test_whitespace_trimmed(self):
        with patch.dict(os.environ, {"IMPRESSIONCORE_ALLOWED_ORIGINS": "  https://a.com ,  https://b.com  "}):
            origins = get_allowed_origins()
            assert origins == ["https://a.com", "https://b.com"]
