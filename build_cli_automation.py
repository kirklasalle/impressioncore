#!/usr/bin/env python
"""
ImpressionCore-b1 CLI Build Automation Script

This script automates the CLI-based build, setup, and verification process for ImpressionCore-b1.
It features rich logging, progress animations, and debugging support.
"""
import os
import sys
import subprocess
import time
from pathlib import Path

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
    from rich.logging import RichHandler
    import logging
except ImportError:
    print("[!] 'rich' not found. Installing...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'rich'])
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
    from rich.logging import RichHandler
    import logging

console = Console()

# Setup rich logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console)]
)
logger = logging.getLogger("impressioncore-build")

PROJECT_ROOT = Path(__file__).parent.resolve()
SRC_DIR = PROJECT_ROOT / "src"
REQUIREMENTS = PROJECT_ROOT / "requirements.txt"
GETTING_STARTED = PROJECT_ROOT / "getting_started.py"


def run_command(cmd, desc, cwd=None, check=True):
    """Run a shell command with rich progress and error handling."""
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), TimeElapsedColumn(), console=console) as progress:
        task = progress.add_task(desc, start=True)
        try:
            result = subprocess.run(cmd, shell=True, cwd=cwd, check=check, capture_output=True, text=True)
            progress.update(task, advance=100, completed=100)
            if result.stdout:
                logger.info(result.stdout.strip())
            if result.stderr:
                logger.warning(result.stderr.strip())
            return result
        except subprocess.CalledProcessError as e:
            progress.stop_task(task)
            logger.error(f"[FAILED] {desc}\n{e.stderr}")
            if check:
                sys.exit(1)
            return e


def check_and_create_dirs():
    """Ensure required directories exist."""
    required = ["core", "data", "models", "training", "inference", "brainsim", "tools"]
    for d in required:
        dir_path = SRC_DIR / d
        if not dir_path.exists():
            logger.info(f"Creating missing directory: {dir_path}")
            dir_path.mkdir(parents=True, exist_ok=True)
        else:
            logger.info(f"Directory exists: {dir_path}")


def install_requirements():
    """Install Python requirements."""
    if REQUIREMENTS.exists():
        run_command(f"pip install -r {REQUIREMENTS}", "Installing core requirements")
    else:
        logger.error("requirements.txt not found!")
        sys.exit(1)

    # Optional extras
    run_command("pip install -e .[dev]", "Installing dev dependencies", check=False)
    run_command("pip install -e .[brainsim]", "Installing brainsim dependencies", check=False)
    run_command("pip install -e .[diffusion]", "Installing diffusion dependencies", check=False)


def verify_environment():
    """Run getting_started.py to verify environment."""
    if GETTING_STARTED.exists():
        run_command(f"python {GETTING_STARTED}", "Verifying environment with getting_started.py")
    else:
        logger.warning("getting_started.py not found. Skipping environment verification.")


def main():
    console.rule("[bold green]ImpressionCore-b1 CLI Build Automation")
    logger.info("[1/5] Checking and creating required directories...")
    check_and_create_dirs()

    logger.info("[2/5] Installing requirements and optional dependencies...")
    install_requirements()

    logger.info("[3/5] Verifying environment and framework status...")
    verify_environment()

    logger.info("[4/5] Listing available CLI commands...")
    run_command("python main.py --help", "Listing CLI commands")

    logger.info("[5/5] Build automation complete. Ready for further CLI operations.")
    console.rule("[bold green]Automation Complete")

if __name__ == "__main__":
    main()
