import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_audit_persistence():
    print("\n--- Testing Audit Persistence ---")
    try:
        from agent0core.core.governance import PrimeDirectiveEnforcer
    except ImportError as e:
        print(f"Import Failed: {e}")
        return False

    # Setup paths
    log_dir = Path("logs/audit")
    if log_dir.exists():
        # Don't delete everything, just ensure we can write
        pass

    enforcer = PrimeDirectiveEnforcer(enable_audit=True)

    # Trigger an action
    action_desc = f"Test Action {time.time()}"
    enforcer.evaluate_action(action_desc)

    # Check if file exists
    files = list(log_dir.glob("*.jsonl"))
    if not files:
        print("FAILED: No audit log file created!")
        return False

    # Get the most recent file
    log_file = sorted(files, key=lambda p: p.stat().st_mtime)[-1]
    print(f"Checking log file: {log_file}")

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
    if test_audit_persistence():
        sys.exit(0)
    else:
        sys.exit(1)
