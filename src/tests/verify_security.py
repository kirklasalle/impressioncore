import os
import shutil
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root and src to path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
SRC_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SRC_ROOT not in sys.path:
    sys.path.insert(0, SRC_ROOT)

# 1. Save originals, mock heavy dependencies for import, then restore
_mock_keys = [
    "src.orchestrator.unified_triad",
    "src.orchestrator.system_logger",
    "src.orchestrator.session_manager",
    "src.orchestrator.sensory_intelligence",
    "src.orchestrator.audio_engine",
    "src.orchestrator.vector_connector",
    "src.orchestrator.face_database",
    "src.orchestrator.face_recognition_engine",
    "src.orchestrator.emotion_analyzer",
    "src.orchestrator.liveness_detector",
    "agent0core.core",
]
_saved = {k: sys.modules.get(k) for k in _mock_keys}
for _k in _mock_keys:
    sys.modules[_k] = MagicMock()

# Mock Agent0Core config to ensure known API key
with patch("agent0core.config.default_config") as mock_config:
    mock_config.api_key = "test-secret-key"

    # Import app after mocking
    from fastapi.testclient import TestClient

    from src.interfaces.triad_api import app

# Restore original modules immediately — import is complete
for _k in _mock_keys:
    if _saved[_k] is not None:
        sys.modules[_k] = _saved[_k]
    else:
        sys.modules.pop(_k, None)
del _saved, _mock_keys, _k


def test_api_security():
    print("\n--- Testing API Security ---")
    client = TestClient(app)

    # 1. Public Endpoint (Should pass)
    resp = client.get("/")
    print(f"Public Endpoint '/': {resp.status_code} (Expected 200)")
    if resp.status_code != 200:
        print("FAILED: Public endpoint was blocked!")
        return False

    # 2. Protected Endpoint WITHOUT Key (Should fail 401)
    resp = client.get("/v1/system/status")
    print(f"Protected (No Key): {resp.status_code} (Expected 401)")
    if resp.status_code != 401:
        print(f"FAILED: Protected endpoint allowed without key! (Got {resp.status_code})")
        return False

    # 3. Protected Endpoint WITH Key (Should pass 200)
    # Note: We mocked the backend logic, so it might error 500 or return mocked data,
    # but NOT 401. As long as it's not 401, middleware passed.
    # Actually /v1/system/status tries to access triad_instance.
    # We need to make sure checking triad_instance doesn't crash middleware test.
    # Use headers
    resp = client.get("/v1/system/status", headers={"X-API-Key": "test-secret-key"})
    print(f"Protected (With Key): {resp.status_code} (Expected 200 or 503/500)")

    if resp.status_code == 401:
        print("FAILED: Protected endpoint blocked even with key!")
        return False

    print("SUCCESS: API Security Middleware working as expected.")
    return True


def test_audit_persistence():
    print("\n--- Testing Audit Persistence ---")
    import time

    from agent0core.core.governance import PrimeDirectiveEnforcer

    # Setup paths
    log_dir = Path("logs/audit")
    if log_dir.exists():
        shutil.rmtree(log_dir)  # Clean start

    enforcer = PrimeDirectiveEnforcer(enable_audit=True)

    # Trigger an action
    action_desc = f"Test Action {time.time()}"
    enforcer.evaluate_action(action_desc)

    # Check if file exists
    files = list(log_dir.glob("*.jsonl"))
    if not files:
        print("FAILED: No audit log file created!")
        return False

    log_file = files[0]
    print(f"Log file created: {log_file}")

    # Read content
    content = log_file.read_text(encoding="utf-8")
    if action_desc in content:
        print("SUCCESS: Audit entry persisted to disk.")
        return True
    else:
        print("FAILED: Audit entry not found in file.")
        print(f"File content: {content}")
        return False


if __name__ == "__main__":
    sec_ok = test_api_security()
    audit_ok = test_audit_persistence()

    if sec_ok and audit_ok:
        print("\nOVERALL VERIFICATION: PASSED")
        sys.exit(0)
    else:
        print("\nOVERALL VERIFICATION: FAILED")
        sys.exit(1)
