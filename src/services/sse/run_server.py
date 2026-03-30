#!/usr/bin/env python3
"""
ImpressionCore - Brain-Inspired Multimodal AI Framework

File: run_server.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-25
Modified: 2025-05-25
Version: 1.0.0

Authors:
- Kirk LaSalle & GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [script]
Dependencies: [] # TODO: Auto-detect or allow manual input
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
# TODO: Add a brief description of this file's purpose.

Design Philosophy:
# TODO: Add design philosophy if applicable.

Memory Considerations:
# TODO: Document any specific memory considerations for this file.

Examples:
# TODO: Provide usage examples if applicable.

Notes:
# TODO: Add any relevant notes.

ImpressionCore Server Entry Point
================================

This script is the main entry point for running the ImpressionCore Flask web server in development mode.

Features:
---------
- Checks for the correct Python virtual environment and prompts the user if not activated.
- Verifies that all required dependencies are installed, and offers to install missing ones.
- Validates the /src directory structure before starting the server.
- Launches the Flask development server, which is implemented in src/web/server.py.

Usage:
------
    python run_server.py

This will perform all environment checks and start the web server on http://localhost:5000/ by default.

Environment:
------------
- Expects a virtual environment (default: .venv310) to be activated.
- Checks for requirements.txt and installs missing dependencies if needed.

Related Files:
--------------
- src/web/server.py: Main Flask app and route definitions.
- src/web/routes.py: Blueprint route definitions.
- src/web/route_config.py: Route mapping and navigation configuration.
- docs/user_guide.md: Full user and developer documentation.

"""
import platform
import subprocess
import venv
import sys
import os
import importlib.util
import logging
from pathlib import Path

logger = logging.getLogger("impressioncore")

# --- Environment and Dependency Checks ---
def check_virtualenv(expected_env_name: str = ".venv310"):
    """
    Checks if the current Python interpreter is running inside the expected virtual environment.
    Args:
        expected_env_name (str): The name of the expected virtual environment directory.
    Returns:
        bool: True if correct environment, False otherwise.
    Raises:
        SystemExit: If not in the correct environment.
    """
    venv_path = Path.cwd() / expected_env_name
    # Accept both with and without leading dot, and ignore case
    expected_env_clean = expected_env_name.lstrip('.').lower()
    current_env = Path(sys.prefix).name.lower().lstrip('.')
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # In a virtualenv
        if current_env != expected_env_clean:
            print(f"[ERROR] Not in the expected virtual environment: {expected_env_name}. Current: {current_env}")
            print(f"Please activate the correct environment before running the server.")
            sys.exit(1)
    elif venv_path.exists():
        print(f"[ERROR] Virtual environment {expected_env_name} exists but is not activated.")
        print(f"Please activate it with: source {expected_env_name}/Scripts/activate (Windows) or source {expected_env_name}/bin/activate (Unix)")
        sys.exit(1)
    else:
        print(f"[WARNING] No virtual environment detected. It is recommended to use {expected_env_name}.")


def check_and_prompt_install_dependencies(requirements_file: str = "requirements.txt"):
    """
    Checks for missing dependencies and prompts the user to install them.
    Args:
        requirements_file (str): Path to requirements.txt.
    Returns:
        bool: True if all dependencies are installed, False if user declined installation.
    """
    import pkg_resources
    import subprocess
    import sys
    from pathlib import Path
    if not Path(requirements_file).exists():
        logger.warning(f"{requirements_file} not found. Skipping dependency check.")
        return True
    with open(requirements_file) as f:
        required = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = [pkg for pkg in required if pkg.lower().split('==')[0] not in installed]
    if missing:
        logger.error(f"Missing dependencies: {missing}")
        print("\nThe following dependencies are missing:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nWould you like to install them now? [y/N]: ", end="", flush=True)
        try:
            response = input().strip().lower()
        except EOFError:
            response = 'n'
        if response == 'y':
            logger.info("User agreed to install missing dependencies.")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
                logger.info("All dependencies installed successfully.")
                return True
            except Exception as e:
                logger.error(f"Failed to install dependencies: {e}", exc_info=True)
                print(f"[ERROR] Failed to install dependencies: {e}")
                return False
        else:
            logger.warning("User declined to install missing dependencies. Continuing without installation.")
            return False
    logger.info("All dependencies are already installed.")
    return True


def check_src_structure():
    """
    Checks that the /src directory and key subfolders exist for ImpressionCore.
    Returns:
        None. Prints errors and exits if structure is invalid.
    """
    from pathlib import Path
    import os
    # Use absolute path to src directory
    project_root = Path(__file__).resolve().parent  # FIXED: now points to repo root
    src_path = project_root / "src"
    required_dirs = [
        (src_path / "core" / "brainsim"),
        (src_path / "core"),
        (src_path / "data"),
        (src_path / "models"),
        (src_path / "training"),
        (src_path / "inference"),
        (src_path / "web")
    ]
    missing = [str(d.relative_to(src_path)) for d in required_dirs if not d.is_dir()]
    logger.info(f"[DEBUG] Checking src/ structure at: {src_path}")
    logger.info(f"[DEBUG] Subdirectories found: {[p.relative_to(src_path) for p in src_path.rglob('*') if p.is_dir()]}")
    if missing:
        logger.error(f"Missing required src/ subdirectories: {missing}")
        print(f"[ERROR] Missing required src/ subdirectories: {missing}")
        print("Please ensure the ImpressionCore project structure is correct.")
        sys.exit(1)
    logger.info("[INFO] All required src/ subdirectories are present.")


def check_server_health():
    """
    Checks the health of server.py and associated files by attempting to import and validate key components.
    Returns:
        None. Prints errors and exits if health check fails.
    """
    try:
        # FIX: Look for server.py in src/web/server.py
        server_path = Path(__file__).parent / "src" / "web" / "server.py"
        if not server_path.exists():
            print(f"[ERROR] server.py not found at {server_path}")
            sys.exit(1)
        spec = importlib.util.spec_from_file_location("server", str(server_path))
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)
        # Optionally, check for required attributes/routes        # Just check for the app instance and run_server function
        assert hasattr(server, 'app'), "Flask app instance 'app' not found in server.py"
        assert hasattr(server, 'run_server'), "Function 'run_server' not found in server.py"
        print("[INFO] server.py health check passed.")
    except Exception as e:
        print(f"[ERROR] server.py health check failed: {e}")
        sys.exit(1)

def setup_virtualenv(expected_env_name: str = ".venv310"):
    """
    If the expected virtual environment does not exist, create it and install dependencies.
    Args:
        expected_env_name (str): The name of the expected virtual environment directory.
    Returns:
        None. Prints status and exits if setup fails.
    """
    from pathlib import Path
    import subprocess
    import sys
    venv_path = Path.cwd() / expected_env_name
    if not venv_path.exists():
        print(f"[INFO] Virtual environment {expected_env_name} not found. Creating...")
        try:
            subprocess.check_call([sys.executable, '-m', 'venv', str(venv_path)])
            print(f"[INFO] Created virtual environment at {venv_path}")
        except Exception as e:
            print(f"[ERROR] Failed to create virtual environment: {e}")
            sys.exit(1)
        # Install dependencies
        pip_path = venv_path / 'Scripts' / 'pip.exe' if os.name == 'nt' else venv_path / 'bin' / 'pip'
        if not pip_path.exists():
            print(f"[ERROR] pip not found in the new virtual environment.")
            sys.exit(1)
        try:
            subprocess.check_call([str(pip_path), 'install', '-r', 'requirements.txt'])
            print(f"[INFO] Installed dependencies in {expected_env_name}")
        except Exception as e:
            print(f"[ERROR] Failed to install dependencies: {e}")
            sys.exit(1)
        print(f"[INFO] Setup complete. Please activate the environment and re-run the server.")
        sys.exit(0)

# --- Run setup and checks before importing/starting the server ---
setup_virtualenv()
check_virtualenv()
# check_and_prompt_install_dependencies() # Commented out as requested
check_src_structure()
check_server_health()

import sys, os

# First, add the project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Make sure both project_root and src_path are in sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Print paths for debugging
print(f"Project root path: {project_root}")
print(f"Src path: {src_path}")
print(f"sys.path: {sys.path}")

# Import the Flask app from server_new.py
from src.interfaces.web.server_new import run_server

if __name__ == '__main__':
    run_server()