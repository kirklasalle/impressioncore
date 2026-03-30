# Web Interface

**Created:** April 19, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\reference\web_interface.md #api #deployment #documentation #inference #memory_management #performance #training #web_interface  
**Category:** Reference Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

# ImpressionCore Web Interface and Walkthrough System

**Last updated: 2025-04-19**

## Overview

The ImpressionCore web interface provides a user-friendly, guided workflow for interacting with the ImpressionCore-b1 LLM. It is designed to make model management, inference, and knowledge operations accessible to both technical and non-technical users.

## Architecture

- **Backend:** Flask-based server with REST and WebSocket endpoints, robust logging, and secure session/file handling.
- **Frontend:** Bootstrap-powered responsive UI, featuring a chat interface and knowledge management panel.
- **Integration:** Directly interfaces with model loading, inference, and training modules in `/src`.

## Key Features

- **Chat Interface:**
  - Real-time interaction with the LLM.
  - Styled user/bot messages for clarity.
- **Knowledge Management:**
  - Add and query subject-predicate-object facts.
  - Knowledge base panel for fact management.
- **Model Management:**
  - Model loading, caching, and metadata endpoints.
  - Secure file uploads and hardware validation.

## Walkthrough/Menu System

- **Current:**
  - Chat and knowledge management are implemented as the first steps in the user workflow.
- **Recommended Expansion:**
  1. Data selection and upload
  2. Model configuration (architecture, memory settings)
  3. Training progress and controls
  4. Evaluation and benchmarking
  5. Model export and deployment

## API & Routing

- REST endpoints for chat, model management, and knowledge operations.
- WebSocket endpoints for real-time updates (e.g., training progress).

## Recommendations

- Expand the walkthrough/menu system to cover the full model build and deployment lifecycle.
- Update this document and the architecture doc as new features are added.
- Ensure all new endpoints and UI features are documented for both users and developers.

## References

- See `docs/impressioncore_b1_architecture.md` for high-level architecture.
- See `src/web/` for implementation details.
