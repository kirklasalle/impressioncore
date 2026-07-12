# Refactoring Monolith API Servers

## Goal
Decompose the monolithic `src/interfaces/triad_api.py` (FastAPI, 118KB) and `src/interfaces/web/server.py` (Flask, 143KB) into modular, domain-specific route controllers. This fixes duplicate route registrations and improves maintainability.

## Tasks
- [x] Task 1: Audit `triad_api.py` to identify duplicates and group routes into domains (System, Agent0, Vision, Audio, RLM, Devices).
- [x] Task 2: Create a modular router structure in `src/interfaces/routes/` and extract the domain routes.
- [x] Task 3: Refactor `triad_api.py` to act as the clean app initializer and mounting point for routes.
- [x] Task 4: Audit `server.py` and extract Flask routes into blueprints under `src/interfaces/web/routes/`.
- [x] Task 5: Refactor `server.py` to use modular blueprints.
- [x] Task 6: Run verification tests to ensure API contracts remain intact.

## Done When
- [x] `triad_api.py` and `server.py` are each under 500 lines of code.
- [x] Duplicate routes in `triad_api.py` are resolved.
- [x] The full stack dev servers (`launch_builder.bat` and `launch_impressioncore.bat`) boot up successfully.
- [x] API validation test suite passes.
