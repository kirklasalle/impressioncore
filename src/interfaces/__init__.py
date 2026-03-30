#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #command_line #python #source_code #src/interfaces/__init__.py #web_interface
**Category:** Interface Definitions
**Status:** Active
"""









# Init

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #command_line #python #source_code #src\\\interfaces/__init__.py #web_interface
# Category:** Interface Definitions
# Status:** Active

"""
ImpressionCore Interfaces
========================

User interface components for web, frontend, and CLI interactions.

File: interfaces/__init__.py
Project: ImpressionCore
Created: 2025-01-07

Components:
- web/: Web server and web interface components
- frontend/: React/TypeScript frontend application
- cli/: Command-line interface and tools
"""

from . import cli, frontend, web

__all__ = ['cli', 'frontend', 'web']
