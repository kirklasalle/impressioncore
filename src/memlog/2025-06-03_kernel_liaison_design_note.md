# ImpressionCore Kernel & Liaison Framework Design Note

- The ImpressionCore kernel module (src/core/kernel/) is reserved for the -iu1 and impressioncore-s1 models and later.
- The kernel will serve as the central orchestrator/controller for the brain-inspired architecture, tightly integrated with the Liaison Framework.
- The Liaison Framework was developed first, as the foundational controller layer for ImpressionCore, and inspired the kernel's design.
- This relationship should be referenced in all relevant design, architecture, and memlog documents.
- Do not use or import the kernel in b1 or earlier models.

Timestamp: 2025-06-03
Responsible: GitHub Copilot
