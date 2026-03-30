# Troubleshooting

**Created:** March 03, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\TROUBLESHOOTING.md #api #docs\reference\troubleshooting.md #documentation #testing  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

# ImpressionCore Troubleshooting Guide

This document provides solutions to common issues encountered when working with ImpressionCore components.

## Component Test Failures

### Universal Knowledge Store

- **Symptom**: `ImportError` or `UniversalKnowledgeStore module not found`
- **Solution**: Ensure the `src/knowledge/uks.py` file exists and is properly implemented
- **Verification**: Run `python -c "from src.knowledge.uks import UniversalKnowledgeStore; print('Success')"`

### BrainSimIII Adapter

- **Symptom**: `ImportError` or initialization errors
- **Solution**: Check that `src/integration/brainsim_adapter.py` is properly implemented
- **Verification**: Run `python -c "from src.integration.brainsim_adapter import BrainSimAdapter; print('Success')"`

### Cognitive Service

- **Symptom**: `KeyError: 'intent'` or other format issues
- **Solution**:
  - Check that `src/cognitive/services.py` returns consistent response formats
  - Ensure `analyze_intent()` method returns a dictionary with either:
    - `{'intent': '...', 'confidence': 0.9}` format, or
    - `{'name': '...', 'score': 0.9}` format, or
    - Include a proper error message
- **Verification**:

  ```python
  from src.cognitive.services import CognitiveService
  service = CognitiveService()
  result = service.analyze_intent("What's the weather?")
  print(result)  # Check format
  ```

### Modal Engine

- **Symptom**: Fails to initialize
- **Solution**: Ensure `src/core/modal_engine.py` can handle `None` for cognitive_service parameter
- **Verification**: Run `python -c "from src.core.modal_engine import ModalEngine; engine = ModalEngine(); print('Success')"`

## General Troubleshooting Steps

1. **Check module existence**: Ensure all required modules are in the correct locations
2. **Verify imports**: Test imports in isolation to identify import errors
3. **Check API interfaces**: Verify that component APIs match the expected interfaces
4. **Enable debug logging**: Add `logging.basicConfig(level=logging.DEBUG)` for more verbose output
5. **Use try-except blocks**: Wrap component code in try-except blocks to catch and diagnose errors
