# Testing

**Created:** May 19, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\developer\testing.md #documentation #inference #memory_management #testing  
**Category:** Developer Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

Last updated: 2025-05-31
Responsible: @GitHubCopilot
---

# ImpressionCore Testing & Validation Guide

This document describes the testing philosophy, test types, and validation strategies for ImpressionCore-b1. It also provides instructions for running and contributing tests, and outlines coverage goals.



## 2. Test Types

- **Unit Tests:**
  - Test individual functions and modules in isolation.
  - Located in `src/tests/` and subdirectories.
- **Integration Tests:**
  - Test interactions between multiple modules (e.g., pipeline, memory manager + model).
- **Performance Tests:**
  - Measure speed, memory usage, and scalability (see `memory_profiler`, `tracemalloc`).
- **End-to-End Tests:**
  - Validate full workflows (e.g., data ingestion → model inference → output).



## 4. Adding New Tests

- Place new tests in the appropriate subdirectory of `src/tests/`.
- Use descriptive function names and docstrings.
- For memory tests, use `memory_profiler` or `tracemalloc` decorators.
- For integration tests, mock external dependencies where possible.



## 6. Reporting & CI Integration

- Test results are reported in CI/CD (see `.github/workflows/`).
- Coverage reports are generated and reviewed for each PR.
- Failures or regressions must be addressed before merging.

---

_Last updated: 2025-05-19_
