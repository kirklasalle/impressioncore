# Python Environment Fallback Notice (2025-06-12)

**Created:** June 12, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\python310_fallback_notice_2025-06-12.md #docs\python310_fallback_notice_2025_06_12.md #documentation  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## Current Environment: Python 3.10 (.venv310)

Due to an upstream compatibility issue, the `sentencepiece` package is not currently available for Python 3.13. As a result, the ImpressionCore project is using a Python 3.10 virtual environment (`.venv310`) until the issue is resolved.

- All requirements and dependencies are installed and validated in `.venv310`.
- `sentencepiece` is fully functional in this environment.
- The project will continue to use `.venv310` for all development and production tasks until `sentencepiece` supports Python 3.13.
- Once compatibility is restored, migration to Python 3.13 will be re-evaluated.

**Responsible:** GitHub Copilot  
**Timestamp:** 2025-06-12

---

For more details, see the main README and requirements documentation.
