"""Run the loopback sensory API/UI with a shared, memory-only service credential."""

import argparse
import os
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[3]


def main() -> int:
    """Supervise only this launcher's children; never stop an existing service."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-downloads", action="store_true")
    parser.add_argument("--monitor", action="store_true")
    args = parser.parse_args()
    for port in (8000, 5173):
        with socket.socket() as connection:
            if connection.connect_ex(("127.0.0.1", port)) == 0:
                print(f"Port {port} is already in use. Stop that specific runtime before relaunching.", file=sys.stderr)
                return 1
    node = shutil.which("node")
    vite = ROOT / "src" / "interfaces" / "web_client" / "node_modules" / "vite" / "bin" / "vite.js"
    if not node or not vite.is_file():
        print("Node.js or the installed frontend Vite dependency is missing. Restore the frontend dependencies first.", file=sys.stderr)
        return 1
    env = os.environ.copy()
    env["IMPRESSIONCORE_API_KEY"] = env.get("IMPRESSIONCORE_API_KEY") or secrets.token_urlsafe(48)
    if not args.allow_downloads:
        env["HF_HUB_OFFLINE"] = "1"
        env["TRANSFORMERS_OFFLINE"] = "1"
    commands = [
        [sys.executable, str(ROOT / "src" / "interfaces" / "triad_api.py")],
        [node, str(vite), "--host", "127.0.0.1", "--port", "5173"],
    ]
    if args.monitor:
        commands.append([sys.executable, str(ROOT / "src" / "core" / "utils" / "vrgc_autonomous_monitor.py")])
    children: list[subprocess.Popen] = []
    try:
        for index, command in enumerate(commands):
            cwd = ROOT / "src" / "interfaces" / "web_client" if index == 1 else ROOT
            children.append(subprocess.Popen(command, cwd=cwd, env=env))
        print("Local runtime: http://127.0.0.1:5173 (capture is off until explicitly started)", flush=True)
        while all(child.poll() is None for child in children):
            time.sleep(1)
        print("A runtime service exited; stopping this launcher's remaining children.", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 0
    finally:
        for child in children:
            if child.poll() is None:
                child.terminate()
        for child in children:
            try:
                child.wait(timeout=15)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()


if __name__ == "__main__":
    raise SystemExit(main())
