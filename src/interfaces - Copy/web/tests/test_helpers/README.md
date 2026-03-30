**Created:** August 04, 2025
**Updated:** August 10, 2025
**Author:** Kirk LaSalle; GitHub Copilot
**Tags:** #ids #standardized_header #src\interfaces\web\tests\test_helpers\README.md
**Category:** Documentation
**Status:** Active

# Test Helpers for Model Definition

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #documentation #src\interfaces\web\tests\test_helpers\readme.md #testing #web_interface  
**Category:** Interface Definitions  
**Status:** Active

This directory contains test utilities that support testing the model definition functionality without modifying existing application code. These helpers follow an additive-only approach to ensure backward compatibility.

## Directory Structure

```
test_helpers/
├── __init__.py           # Common utilities and imports
├── fixtures.py           # Hardware profile test fixtures
├── hardware.py          # Hardware detection test helpers
├── html.py              # HTML validation helpers
├── logging.py           # Test logging utilities
├── mocks.py            # Mock service implementations
├── templates.py        # Model template test data
├── validation.py       # Configuration validation helpers
├── visualization.py    # Architecture visualization helpers
└── README.md          # This file
```

## Usage Examples

### Testing with Mock Hardware

```python
from test_helpers.hardware import HardwareProfile
from test_helpers.fixtures import get_hardware_profile

def test_hardware_compatibility():
    profile = HardwareProfile()
    config = get_test_config('minimal')
    is_supported, reason = profile.can_support_model(config)
    assert is_supported, reason
```

### Testing WebSocket Communication

```python
from test_helpers.mocks import MockWebSocket
import pytest

@pytest.mark.asyncio
async def test_model_updates():
    ws = MockWebSocket()
    await ws.send({'type': 'update', 'config': test_config})
    response = await ws.receive()
    assert response['type'] == 'update_success'
```

### Testing HTML Generation

```python
from test_helpers.html import HTMLTestHelper

def test_model_form():
    html = render_template('model_definition.html')
    helper = HTMLTestHelper()
    is_valid, errors = helper.validate_model_form(html)
    assert is_valid, '\n'.join(errors)
```

### Testing with Logging

```python
from test_helpers.logging import capture_logs

def test_validation_logging():
    with capture_logs('validation', 'tests/logs/validation.json') as logger:
        result = validate_model_config(invalid_config)
        assert logger.contains_error('ValidationError')
```

## Integration Guidelines

1. Use these helpers to write tests that validate new functionality
2. Don't modify existing application code for testing
3. Keep test data separate from production data
4. Use mocks for external services and hardware detection
5. Log test execution for debugging

## Adding New Helpers

When adding new test helpers:

1. Create a new module in this directory
2. Document the module's purpose and usage
3. Include example code
4. Update this README
5. Add new helper to __init__.py if needed

## Requirements

Test helpers require:

- pytest>=7.3.1
- pytest-asyncio>=0.21.0
- beautifulsoup4>=4.9.3
- responses>=0.23.1

Install test dependencies with:

```bash
pip install -r requirements-test.txt