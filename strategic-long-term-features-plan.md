# Implementation Plan: Strategic Long-Term Features

## Goal
Implement and verify the three strategic long-term features for ImpressionCore:
1. **One-Click Training CLI**: `impressioncore train --preset conversational_ai` to launch training using GTX 1050 Ti VRAM limitations.
2. **Model Registry Integration**: Hugging Face Hub hosting and downloading checkpoints with urllib fallback.
3. **WebSocket Streaming Inference**: Real-time token-by-token generation for React client.

---

## Tasks

- [ ] **Task 1: Extend Training CLI & Presets**
  - Create `src/core/config/presets.py` containing preset dictionaries (e.g., `conversational_ai`, `smoke_test`, `distillation`).
  - Modify `src/training/core_trainer.py:start_training` to support passing a config dictionary directly in addition to a filepath, and resolve the signature mismatch with `api` in `main.py`.
  - Add `train` parser to `src/main.py` routing to the training execution with `--preset` support.
  - *Verify*: Run `python -m src.main train --preset conversational_ai --device cpu` (dry-run/smoke test).

- [ ] **Task 2: Implement Hugging Face Model Registry Client**
  - Create `src/core/models/registry/hf_integration.py` to handle uploading/downloading checkpoints from Hugging Face Hub using `huggingface_hub` (if available) with a standard HTTP download fallback via `urllib`.
  - Add `registry download` and `registry upload` subcommands to `src/core/models/registry/cli.py` and register the `registry` subparser in `src/main.py`.
  - *Verify*: Run `python -m src.main registry download --repo-id lyog/impressioncore-b1 --filename config.json` (or another test target) and verify local saving.

- [ ] **Task 3: Implement WebSocket Streaming Inference**
  - Add `generate_stream` to `src/orchestrator/unified_triad.py` utilizing `transformers.TextIteratorStreamer` to yield Left Brain thought tokens, Right Brain thought tokens, and Colossus synthesis tokens.
  - Implement a WebSocket route `/v1/chat/stream` in `src/interfaces/routes/chat.py` that processes incoming WebSocket chat requests, invokes the streaming generator, and pushes updates to the client.
  - *Verify*: Create a pytest test or run a python script to simulate WebSocket connection and verify step-by-step token streams.

- [ ] **Task 4: Update React Web Frontend to Support Streaming**
  - Update `src/interfaces/web_client/src/App.jsx` to establish a WebSocket connection to `CHAT_STREAM_WS` inside `handleSend` when streaming is enabled, showing incremental updates for Left/Right thoughts and rendering the Colossus reply token-by-token.
  - *Verify*: Launch dev server and verify token-by-token streaming in the UI.

---

## Done When
- [ ] `impressioncore train --preset conversational_ai` successfully executes a training cycle or a dry-run.
- [ ] Model weights can be downloaded from Hugging Face Hub using the CLI tools.
- [ ] The React chat interface receives and displays thoughts and main responses streamingly.
