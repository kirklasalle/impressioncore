# Implementation Plan — High Priority Roadmap
**Date:** July 12, 2026 | **Task Slug:** `high-priority-roadmap`

---

## 1. Analysis

### Scope of Work
This plan addresses the following key high-priority roadmap items:
1. **F:\ Drive Path Config Module (Item 10):** Centralized path resolution and environment checking with fail-fast initialization.
2. **Decomposition of Monoliths (Items 4 & 5):**
   - Decomposing FastAPI backend `src/interfaces/triad_api.py` (118KB) into modular routers.
   - Decomposing Flask frontend server `src/interfaces/web/server.py` (143KB) into Blueprints.
3. **Wiring B3 Hope v1 into Runtime Inference (Item 9):**
   - Native PyTorch B3 model initialization from `F:\models\production\b3_hope_v1\`.
   - Integrated VRAM/OOM checks with structured error reporting (Option B with A-fallback suggestions).
4. **Ecosystem & Infrastructure (Items 6, 7 & 8):**
   - Docker Compose file orchestrating services (FastAPI API, Flask server, Vite client).
   - GitHub Actions CI/CD pipeline running checks.
   - Target Unit tests to raise overall test coverage.

### Design Decisions
* **Path Resolution:** A centralized config class `PathConfig` in `src/core/config/paths.py`. It checks `F:\` access and specific file presence during boot.
* **API Routing:** Migrate monolithic routes from `triad_api.py` into `src/interfaces/routes/` folder utilizing FastAPI `APIRouter`.
* **Web Routing:** Migrate Jinja views and routes from `server.py` into `src/interfaces/web/routes/` utilizing Flask `Blueprint`.
* **Native Inference:** Instantiates B3 model architecture (`src/models/architectures/b3_foundation.py` or similar) and loads weights using PyTorch `load_state_dict`. Sets up a dedicated route utilizing GPU semaphores.

---

## 2. Planning & Task Breakdown

### Phase 1: Configuration & Fail-Fast (P0)
- [x] Task 1.1: Create `src/core/config/paths.py` with environment variable overrides and validations.
- [x] Task 1.2: Add unit tests verifying validation raises `RuntimeError` on missing directories.

### Phase 2: Monolith Decomposition (P0)
- [x] Task 2.1: Decompose `src/interfaces/triad_api.py` into separate route files under `src/interfaces/routes/` (e.g., `model.py`, `inference.py`, `dataset.py`).
- [x] Task 2.2: Decompose `src/interfaces/web/server.py` into Flask Blueprints under `src/interfaces/web/routes/` (e.g., `views.py`, `training.py`, `config.py`).
- [x] Task 2.3: Re-route entry points in `pyproject.toml` and launcher scripts to target the newly modular entry points.

### Phase 3: B3 Hope v1 Integration & Inference (P1)
- [x] Task 3.1: Implement PyTorch state-dict loader in `src/inference/pipelines/` to load weights from `F:\models\production\b3_hope_v1\`.
- [x] Task 3.2: Implement VRAM allocation checks and `RuntimeError` (OOM) handling in inference routines, returning HTTP 503 with user instructions to fallback to CPU/Ollama if OOM occurs.
- [x] Task 3.3: Add integration tests for native B3 inference with mock tensors.

### Phase 4: Containerization, CI/CD, and Coverage (P1)
- [ ] Task 4.1: Write a multi-stage `Dockerfile` and `docker-compose.yml` for local deployment.
- [ ] Task 4.2: Create `.github/workflows/ci.yml` for automated linting and test execution.
- [ ] Task 4.3: Raise test coverage by writing unit tests for routes and controllers.

---

## 3. Solutioning & Architecture (Draft)

### Central Config Architecture (`paths.py`)
```python
import os
from pathlib import Path

class PathConfig:
    DEFAULT_F_DRIVE = Path("F:/")
    
    @classmethod
    def get_model_dir(cls) -> Path:
        base = Path(os.getenv("IC_MODEL_DIR", cls.DEFAULT_F_DRIVE / "models/production"))
        if not base.exists():
            raise RuntimeError(f"Critical Path Missing: Model directory {base} is inaccessible.")
        return base
```

### Route Decomposition Layout
```
src/interfaces/
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── inference.py
│   └── monitoring.py
└── triad_api.py (Modular launcher only)
```

---

## 4. Verification & Done Criteria
- `python -m pytest` passes 100% of tests.
- Centralized validation throws an explicit error when `F:\` is unmounted/inaccessible.
- API is running modularly (confirmed by running `/health` and `/inference` tests).
- Docker Compose builds all images cleanly.
