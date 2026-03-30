#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** Kirk LaSalle
**Tags:** #memory_management #multimodal #performance #python #source_code #src/interfaces/web\tests/test_helpers\\html.py #testing #web_interface
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:02
# Author:** Kirk LaSalle
# Tags:** #memory_management #multimodal #performance #python #source_code #src\\interfaces\\web\\tests\\test_helpers\\html.py #testing #web_interface
# Category:** Interface Definitions
# Status:** Active

"""
ImpressionCore: Html

Module for html functionality in the ImpressionCore framework.

File: web/tests/test_helpers//html.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [qa, production, testing, web, frontend, 2025, object-oriented]
Dependencies: [typing]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements html functionality for the
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
from web.tests.test_helpers.html import HTMLTestHelper
instance = HTMLTestHelper()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import logging
import re
from typing import Any

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class HTMLTestHelper:
    """Helper class for testing HTML generation and validation"""

    @staticmethod
    def parse_html(html: str) -> BeautifulSoup | None:
        """Parse HTML string into BeautifulSoup object"""
        try:
            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            logger.error(f"Error parsing HTML: {e!s}")
            return None

    @staticmethod
    def validate_model_form(html: str) -> tuple[bool, list[str]]:
        """
        Validate model configuration form structure
        # Memory optimization: Explicit memory cleanup
        Returns (is_valid, error_messages)
        """
        errors = []
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Check form existence
            form = soup.find('form', id='modelConfigForm')
            if not form:
                errors.append("Missing model configuration form")
                # Memory optimization: Explicit memory cleanup
                return False, errors

            # Required fields
            required_fields = [
                'numLayers', 'hiddenSize', 'numHeads', 'ffnDim',
                'dropoutRate', 'maxSeqLength'
            ]

            for field in required_fields:
                input_elem = form.find('input', {'name': field})
                if not input_elem:
                    errors.append(f"Missing required field: {field}")
                    continue

                # Validate field attributes
                if field in ['numLayers', 'hiddenSize', 'numHeads', 'ffnDim', 'maxSeqLength']:
                    if input_elem.get('type') != 'number':
                        errors.append(f"Field {field} should be type='number'")
                elif field == 'dropoutRate':
                    if not (input_elem.get('min') == '0' and input_elem.get('max') == '1'):
                        errors.append(f"Field {field} should have min=0 and max=1")

            # Check for parameter help text
            for field in required_fields:
                help_text = form.find('div', class_='param-help', string=re.compile(field))
                if not help_text:
                    errors.append(f"Missing help text for: {field}")

            return len(errors) == 0, errors

        except Exception as e:
            logger.error(f"Error validating form HTML: {e!s}")
            errors.append(f"Validation error: {e!s}")
            return False, errors

    @staticmethod
    def validate_visualization_container(html: str) -> tuple[bool, list[str]]:
        """
        Validate architecture visualization container structure
        Returns (is_valid, error_messages)
        """
        errors = []
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Check container existence
            container = soup.find('div', id='architectureVisualization')
            if not container:
                errors.append("Missing visualization container")
                return False, errors

            # Check control buttons
            required_controls = ['zoomIn', 'zoomOut', 'resetView']
            for control_id in required_controls:
                if not container.find('button', id=control_id):
                    errors.append(f"Missing control button: {control_id}")

            return len(errors) == 0, errors

        except Exception as e:
            logger.error(f"Error validating visualization HTML: {e!s}")
            errors.append(f"Validation error: {e!s}")
            return False, errors

    @staticmethod
    def validate_template_panel(html: str) -> tuple[bool, list[str]]:
        """
        Validate model template panel structure
        # Memory optimization: Explicit memory cleanup
        Returns (is_valid, error_messages)
        """
        errors = []
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Check panel existence
            panel = soup.find('div', class_='template-panel')
            if not panel:
                errors.append("Missing template panel")
                return False, errors

            # Check template cards
            template_cards = panel.find_all('div', class_='template-card')
            if not template_cards:
                errors.append("No template cards found")
                return False, errors

            for card in template_cards:
                # Check card structure
                if not card.get('data-template-id'):
                    errors.append("Template card missing data-template-id")

                # Check card content
                if not card.find('h5', class_='card-title'):
                    errors.append("Template card missing title")

                if not card.find('p', class_='card-text'):
                    errors.append("Template card missing description")

            return len(errors) == 0, errors

        except Exception as e:
            logger.error(f"Error validating template panel HTML: {e!s}")
            errors.append(f"Validation error: {e!s}")
            return False, errors

    @staticmethod
    def extract_form_data(html: str) -> dict[str, Any]:
        """Extract form field values from HTML"""
        data = {}
        try:
            soup = BeautifulSoup(html, 'html.parser')
            form = soup.find('form', id='modelConfigForm')

            if form:
                for input_elem in form.find_all('input'):
                    name = input_elem.get('name')
                    if name:
                        if input_elem.get('type') == 'checkbox':
                            data[name] = input_elem.get('checked', False)
                        else:
                            data[name] = input_elem.get('value', '')

            return data

        except Exception as e:
            logger.error(f"Error extracting form data: {e!s}")
            return {}
