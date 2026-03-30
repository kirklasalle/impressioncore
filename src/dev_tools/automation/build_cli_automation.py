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
import asyncio
from pathlib import Path
import json
import datetime
from datetime import timezone

# --- System Oversight Imports ---
# from src.services.system_oversight import SystemOversightService, adaptive_memory_management


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

# Setup rich logging for console
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console)]
)
logger = logging.getLogger("impressioncore-build")

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()  # Go up 4 levels: automation -> scripts -> src -> project_root
SRC_DIR = PROJECT_ROOT / "src"
MEMLOG_CLI_DIR = SRC_DIR / "memlog" / "cli"
REQUIREMENTS = PROJECT_ROOT / "requirements.txt"
GETTING_STARTED = PROJECT_ROOT / "getting_started.py"

# Ensure memlog/cli directory exists
MEMLOG_CLI_DIR.mkdir(parents=True, exist_ok=True)

# --- Structured JSONL Event Logging ---
LOG_ID = f"build_cli_automation_{datetime.datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}"
EVENT_LOG_FILE_BUILD = MEMLOG_CLI_DIR / f"{LOG_ID}.jsonl"
file_event_logger_build = None

def setup_file_event_logger_build():
    global file_event_logger_build
    file_event_logger_build = logging.getLogger(f"FileEventLogger_Build_{LOG_ID}")
    file_event_logger_build.setLevel(logging.INFO)
    file_event_logger_build.propagate = False
    
    for handler in file_event_logger_build.handlers[:]:
        file_event_logger_build.removeHandler(handler)
        handler.close()

    fh = logging.FileHandler(EVENT_LOG_FILE_BUILD)
    fh.setLevel(logging.INFO)
    file_event_logger_build.addHandler(fh)

def log_event_build(event_type, status, details=None, error_message=None, duration_ms=None):
    if file_event_logger_build is None:
        setup_file_event_logger_build()

    log_entry = {
        "timestamp_utc": datetime.datetime.now(timezone.utc).isoformat(),
        "log_id": LOG_ID,
        "source_script": "build_cli_automation.py",
        "event_type": event_type,
        "status": status,
        "details": details or {},
    }
    if error_message:
        log_entry["error_message"] = error_message
    if duration_ms is not None:
        log_entry["duration_ms"] = duration_ms
    
    if file_event_logger_build:
        file_event_logger_build.info(json.dumps(log_entry))
    else:
        with open(EVENT_LOG_FILE_BUILD, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')


def run_command(cmd, desc, cwd=None, check=True):
    """Run a shell command with rich progress and error handling."""
    start_time = time.perf_counter()
    
    python_executable = sys.executable
    if " " in python_executable:
        python_executable = f'"{python_executable}"'

    if cmd.strip().startswith("pip "):
        pip_command_parts = cmd.split(" ", 1)
        if len(pip_command_parts) > 1:
            cmd = f"{python_executable} -m pip {pip_command_parts[1]}"
        else:
            cmd = f"{python_executable} -m pip"
    elif cmd.strip().startswith("python "):
        python_command_parts = cmd.split(" ", 1)
        if len(python_command_parts) > 1:
            cmd = f"{python_executable} {python_command_parts[1]}"
        else:
            cmd = python_executable

    log_event_build("command_execution", "progress", {"command": cmd, "description": desc, "cwd": str(cwd) if cwd else None})
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), TimeElapsedColumn(), console=console) as progress:
        task = progress.add_task(desc, start=True)
        try:
            result = subprocess.run(cmd, shell=True, cwd=cwd, check=check, capture_output=True, text=True, executable=None)
            progress.update(task, advance=100, completed=100)
            duration_ms = (time.perf_counter() - start_time) * 1000
            if result.stdout:
                logger.info(result.stdout.strip())
            if result.stderr:
                logger.warning(result.stderr.strip())
            log_event_build("command_execution", "success", {"command": cmd, "description": desc, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}, duration_ms=duration_ms)
            return result
        except subprocess.CalledProcessError as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            progress.stop_task(task)
            logger.error(f"[FAILED] {desc}\\n{e.stderr}")
            log_event_build("command_execution", "failure", {"command": cmd, "description": desc, "stderr": e.stderr}, error_message=str(e), duration_ms=duration_ms)
            if check:
                sys.exit(1)
            return e


def check_and_create_dirs():
    """Ensure required directories exist."""
    log_event_build("directory_check", "progress", {"action": "Starting directory check and creation"})
    required = ["core", "data", "models", "training", "inference", "brainsim", "tools"]
    all_dirs_ok = True
    for d in required:
        dir_path = SRC_DIR / d
        if not dir_path.exists():
            logger.info(f"Creating missing directory: {dir_path}")
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                log_event_build("directory_check", "success", {"directory": str(dir_path), "status": "created"})
            except Exception as e:
                logger.error(f"Failed to create directory {dir_path}: {e}")
                log_event_build("directory_check", "failure", {"directory": str(dir_path)}, error_message=str(e))
                all_dirs_ok = False
        else:
            logger.info(f"Directory exists: {dir_path}")
            log_event_build("directory_check", "info", {"directory": str(dir_path), "status": "exists"})
    if not all_dirs_ok:
        log_event_build("directory_check", "failure", {"summary": "One or more directories failed to be created."})
        sys.exit(1)
    log_event_build("directory_check", "success", {"summary": "All required directories checked/created."})


def install_requirements():
    """Install Python requirements."""
    log_event_build("dependency_installation", "progress", {"action": "Starting requirements installation"})
    if REQUIREMENTS.exists():
        run_command(f"pip install -r \"{REQUIREMENTS}\"", "Installing core requirements")
    else:
        logger.error(f"requirements.txt not found at: {REQUIREMENTS}")
        log_event_build("dependency_installation", "failure", {"file": str(REQUIREMENTS)}, error_message=f"requirements.txt not found at: {REQUIREMENTS}")
        sys.exit(1)

    run_command(f"pip install -e \"{PROJECT_ROOT}[dev]\"", "Installing dev dependencies", check=False)
    run_command(f"pip install -e \"{PROJECT_ROOT}[brainsim]\"", "Installing brainsim dependencies", check=False)
    run_command(f"pip install -e \"{PROJECT_ROOT}[diffusion]\"", "Installing diffusion dependencies", check=False)
    log_event_build("dependency_installation", "success", {"summary": "Core and optional dependencies processed."})


def verify_environment():
    """Run getting_started.py to verify environment."""
    log_event_build("environment_verification", "progress", {"action": "Starting environment verification"})
    if GETTING_STARTED.exists():
        run_command(f"python \"{GETTING_STARTED}\"", "Verifying environment with getting_started.py")
        log_event_build("environment_verification", "success", {"script": str(GETTING_STARTED)})
    else:
        logger.warning(f"getting_started.py not found at: {GETTING_STARTED}. Skipping environment verification.")
        log_event_build("environment_verification", "info", {"script": str(GETTING_STARTED), "status": "skipped_not_found"})


def main():
    setup_file_event_logger_build()
    log_event_build("script_execution", "progress", {"script_name": "build_cli_automation.py", "status": "started"})
    start_time_main = time.perf_counter()
    
    try:
        # oversight_service = SystemOversightService()
        oversight_service = None
        logger.info("Oversight service disabled for this build")
    except Exception as e:
        logger.warning(f"Could not initialize oversight service: {e}")
        oversight_service = None

    console.rule("[bold green]ImpressionCore-b1 CLI Build Automation")

    logger.info("[1/5] Checking and creating required directories...")
    step_start_time = time.perf_counter()
    check_and_create_dirs()
    log_event_build("main_step", "success", {"step": "1/5_check_and_create_dirs"}, duration_ms=(time.perf_counter() - step_start_time) * 1000)

    if oversight_service:
        try:
            health = asyncio.run(oversight_service.get_system_health())
            log_event_build("system_health_check", "info", {"when": "before_install", **health})
            logger.info(f"[System Health] CPU: {health['cpu_usage']:.2f}%, RAM: {health['memory_usage']:.2f}%, VRAM: {health['gpu_vram_usage']:.2f}%")
        except Exception as e:
            logger.warning(f"System health check failed: {e}")
            log_event_build("system_health_check", "failure", {"when": "before_install"}, error_message=str(e))

        async def mitigation_callback(reason):
            logger.warning(f"[Mitigation Triggered] Reason: {reason}. Attempting to reduce memory usage or offload.")
            log_event_build("memory_mitigation", "triggered", {"reason": reason, "when": "before_install"})
            print(f"[WARNING] Memory mitigation triggered: {reason}. System is attempting to adapt for stability.")

        # Adaptive memory management disabled for this build
        logger.info("Adaptive memory management disabled for this build")

    logger.info("[2/5] Installing requirements and optional dependencies...")
    step_start_time = time.perf_counter()
    install_requirements()
    log_event_build("main_step", "success", {"step": "2/5_install_requirements"}, duration_ms=(time.perf_counter() - step_start_time) * 1000)

    logger.info("[3/5] Verifying environment and framework status...")
    step_start_time = time.perf_counter()
    verify_environment()
    log_event_build("main_step", "success", {"step": "3/5_verify_environment"}, duration_ms=(time.perf_counter() - step_start_time) * 1000)

    logger.info("[4/5] Listing available CLI commands...")
    step_start_time = time.perf_counter()
    run_command("python -m src.cli.main --help", "Displaying available CLI commands", check=False)
    log_event_build("main_step", "success", {"step": "4/5_list_cli_commands"}, duration_ms=(time.perf_counter() - step_start_time) * 1000)

    logger.info("[5/5] Build automation complete!")
    step_start_time = time.perf_counter()
    console.rule("[bold green]Build Complete")
    console.print("[green]✓ All steps completed successfully![/green]")
    console.print("\\n[bold blue]Next Steps:[/bold blue]")
    console.print("1. Run 'python main.py' to start ImpressionCore-b1")
    console.print("2. Check logs in src/memlog/cli/ for detailed event history")
    log_event_build("main_step", "success", {"step": "5/5_build_complete"}, duration_ms=(time.perf_counter() - step_start_time) * 1000)

    total_duration_ms = (time.perf_counter() - start_time_main) * 1000
    log_event_build("script_execution", "success", {"script_name": "build_cli_automation.py", "status": "completed"}, duration_ms=total_duration_ms)


if __name__ == "__main__":
    main()
