#!/usr/bin/env python3
"""
ImpressionCore - Brain-Inspired Multimodal AI Framework

File: getting_started.py
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
Getting Started with ImpressionCore & ImpressionCore-b1

This script provides a visually enhanced, step-by-step onboarding guide for the entire 
ImpressionCore framework and the ImpressionCore-b1 reference model. It features color, 
ASCII art, progress animations, and rich formatting for a delightful onboarding experience.

Design Philosophy:
User-friendly setup and configuration with visual feedback and clear instructions.

Memory Considerations:
Designed to work within the constraints of the target hardware (4GB VRAM).

Examples:
Run this file directly to see the instructions:
$ python getting_started.py

Notes:
This script helps users get started with ImpressionCore development environment.
"""

import os
import sys
import time
import random
import warnings
from pathlib import Path
from datetime import datetime
import platform

# Suppress NumPy compatibility warnings from PyTorch and other libraries
warnings.filterwarnings("ignore", message=".*numpy.dtype size changed.*")
warnings.filterwarnings("ignore", message=".*numpy.ufunc size changed.*")
warnings.filterwarnings("ignore", message=".*A module that was compiled using NumPy.*")
warnings.filterwarnings("ignore", message=".*NumPy 1.x.*cannot be run in.*NumPy.*")
warnings.filterwarnings("ignore", category=UserWarning, module="torch.*")
warnings.filterwarnings("ignore", category=FutureWarning, module="torch.*")

# Set environment variable to suppress NumPy warnings
os.environ['PYTHONWARNINGS'] = 'ignore::UserWarning'

# ========== COLOR CODES (ANSI) ==========
RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
GREY = "\033[90m"
WHITE = "\033[97m"

# ========== ASCII ART & VISUALS ==========
IC_ASCII = f"""
{CYAN}{BOLD}
 _____                                  _              ______                 
(_____)                                (_)            / _____)                
   _   ____  ____   ____ ____  ___  ___ _  ___  ____ | /      ___   ____ ____ 
  | | |    \|  _ \ / ___) _  )/___)/___) |/ _ \|  _ \| |     / _ \ / ___) _  )
 _| |_| | | | | | | |  ( (/ /|___ |___ | | |_| | | | | \____| |_| | |  ( (/ / 
(_____)_|_|_| ||_/|_|   \____|___/(___/|_|\___/|_| |_|\______)___/|_|   \____)
            |_|                                                               
{RESET}                                                                                 
"""

LOGO_FRAMES = [
    f"{CYAN}{BOLD}◐ ImpressionCore ◑{RESET}",
    f"{CYAN}{BOLD}◓ ImpressionCore ◒{RESET}",
    f"{CYAN}{BOLD}◑ ImpressionCore ◐{RESET}",
    f"{CYAN}{BOLD}◒ ImpressionCore ◓{RESET}"
]

CELEBRATE_BANNER = f"""
{GREEN}{BOLD}
🎉🎉🎉  Congratulations! You are ready to build with ImpressionCore-b1!  🎉🎉🎉
{RESET}"""

QUICK_START_BOX = f"""
{BOLD}{WHITE}{BLUE}
+---------------------------------------------------------------+
|   QUICK START: ImpressionCore-b1 in 3 Steps                   |
+---------------------------------------------------------------+
| 1. Clone & Install:                                           |
|    $ git clone <repo-url>                                     |
|    $ cd impressioncore                                        |
|    $ python -m venv .venv && source .venv/bin/activate        |
|    $ pip install -e .[dev,brainsim,diffusion]                 |
|                                                               |
| 2. Launch Walkthrough UI:                                     |
|    $ python run_server.py                                     |
|    (Open http://localhost:8000 in your browser)               |
|                                                               |
| 3. Build, Train, and Explore:                                 |
|    Use the UI to define, train, and test your model!          |
+---------------------------------------------------------------+
{RESET}"""

DID_YOU_KNOW_TIPS = [
    "You can monitor VRAM usage in real time using the memory logging tools in src/utils/memory.py!",
    "ImpressionCore-b1 is optimized for 4GB VRAM GPUs—no need for expensive hardware.",
    "The walkthrough UI supports both text and image tokenization workflows.",
    "All errors are logged in src/memlog/ for easy troubleshooting.",
    "You can extend the brainsim module to simulate new cognitive functions!",
    "Security is built-in: all user data is protected with quantum-resistant cryptography.",
    "Try the CLI tools in docs/user_guide_tools.md for advanced automation.",
    "You can visualize model architecture and training progress in the web UI.",
    "The project structure is modular—add new features in /src without breaking existing code.",
    "Check out docs/next_steps.md for the latest roadmap and contribution ideas!"
]

def print_logo_spinner(duration=1.5, interval=0.18):
    """Animated ImpressionCore logo spinner."""
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        print(f"\r{LOGO_FRAMES[i % len(LOGO_FRAMES)]}", end='', flush=True)
        time.sleep(interval)
        i += 1
    print(f"\r{' '*40}\r", end='')

def print_animated(text, color=CYAN, delay=0.01):
    """Print text with a typewriter animation."""
    for char in text:
        print(f"{color}{char}{RESET}", end='', flush=True)
        time.sleep(delay)
    print()

def print_progress(msg, color=YELLOW, dots=3, delay=0.3):
    """Show animated progress dots."""
    print(f"{color}{msg}{RESET}", end='', flush=True)
    for _ in range(dots):
        print(f"{color}.{RESET}", end='', flush=True)
        time.sleep(delay)
    print()

def print_divider():
    """Print a colored divider."""
    print(f"{MAGENTA}{'='*80}{RESET}")

def print_header(text, icon=None):
    """Print a section header with color, icon, and ASCII divider."""
    print_divider()
    icon_str = f"{icon} " if icon else ""
    print(f"{BOLD}{UNDERLINE}{CYAN}{icon_str}{text.center(76)}{RESET}")
    print_divider()

def print_command(cmd):
    """Print a command with formatting."""
    print(f"  {GREEN}${RESET} {cmd}")

def print_step(num, text, emoji=None):
    """Print a numbered step with color and emoji."""
    emoji_str = f"{emoji} " if emoji else ""
    print(f"\n{BOLD}{YELLOW}{emoji_str}Step {num}:{RESET} {BOLD}{text}{RESET}")

def print_info(msg):
    print(f"{CYAN}[INFO]{RESET} {msg}")

def print_warning(msg):
    print(f"{YELLOW}[WARNING]{RESET} {msg}")

def print_success(msg):
    print(f"{GREEN}[SUCCESS]{RESET} {msg}")

def print_error(msg):
    print(f"{RED}[ERROR]{RESET} {msg}")

# ========== SYSTEM & ENVIRONMENT CHECKS ==========
def check_python_version():
    required = (3, 10)
    actual = sys.version_info[:2]
    if actual >= required:
        print_success(f"Python version OK: {platform.python_version()}")
    else:
        print_error(f"Python >= 3.10 required, found {platform.python_version()}")

def check_gpu():
    try:
        # Temporarily redirect stderr to suppress NumPy compatibility warnings
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            import torch
        
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
            print_success(f"GPU detected: {gpu_name} ({vram_gb:.1f} GB VRAM)")
        else:
            print_warning("No CUDA GPU detected. ImpressionCore-b1 requires at least GTX 1050 Ti (4GB VRAM).")
    except ImportError:
        print_warning("PyTorch not installed. Cannot check GPU. Run 'pip install torch'.")

def check_memory():
    try:
        import psutil
        ram_gb = psutil.virtual_memory().total / 1e9
        if ram_gb >= 16:
            print_success(f"System RAM OK: {ram_gb:.1f} GB")
        else:
            print_warning(f"System RAM low: {ram_gb:.1f} GB (16GB+ recommended)")
    except ImportError:
        print_warning("psutil not installed. Cannot check RAM. Run 'pip install psutil'.")

# ========== VISUAL PROJECT STRUCTURE ==========
def print_project_tree():
    tree = f"""
{BOLD}{BLUE}impressioncore/{RESET}
│
├── {CYAN}src/{RESET}         {GREY}# Core logic, models, data, training, inference, brainsim, tools{RESET}
├── {CYAN}docs/{RESET}        {GREY}# Documentation, architecture, memory optimization, user guide{RESET}
├── {CYAN}main.py{RESET}      {GREY}# Main CLI entry point{RESET}
├── {CYAN}run_server.py{RESET}{GREY}# Web walkthrough UI server{RESET}
├── {CYAN}getting_started.py{RESET}  {GREY}# This onboarding guide{RESET}
├── {CYAN}troubleshoot.bat{RESET}   {GREY}# Windows troubleshooting script{RESET}
"""
    print(tree)

# ========== VISUAL WORKFLOW DIAGRAM ==========
def print_workflow_diagram():
    diagram = f"""
{BOLD}{MAGENTA}ImpressionCore-b1 Workflow:{RESET}

  {CYAN}[User]{RESET}
     │
     ▼
  {BLUE}[Walkthrough UI]{RESET} ──► {GREEN}[Terminal]{RESET} ──► {YELLOW}[Model Config]{RESET} ──► {MAGENTA}[Training]{RESET}
     │                                 │                          │
     ▼                                 ▼                          ▼
  {CYAN}[Docs]{RESET}             {YELLOW}[Data Prep]{RESET}         {GREEN}[Evaluation]{RESET}
     │                                 │                          │
     ▼                                 ▼                          ▼
  {BLUE}[Brainsim]{RESET}         {MAGENTA}[Inference]{RESET}      {CYAN}[Security]{RESET}
"""
    print(diagram)

# ========== MAIN ONBOARDING GUIDE ==========
def main():
    print_logo_spinner()
    print(IC_ASCII)
    print(QUICK_START_BOX)
    print_animated("Welcome to ImpressionCore & ImpressionCore-b1!", CYAN, delay=0.03)
    print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Platform: {platform.system()} {platform.release()} | Python: {platform.python_version()}")
    print_progress("Loading onboarding experience", CYAN)

    # 1. Project Overview
    print_header("PROJECT OVERVIEW", icon="🧠")
    print_animated("ImpressionCore is a brain-inspired, modular, memory-optimized multimodal AI framework. ImpressionCore-b1 is the initial reference LLM, designed for consumer hardware (GTX 1050 Ti, 4GB VRAM).", CYAN)
    print("\nKey Features:")
    print(f"{BOLD}- Multimodal:{RESET} Text, image, audio, video support (see docs/user_guide.md)")
    print(f"{BOLD}- Memory-efficient:{RESET} Optimized for low VRAM (see docs/memory_optimization_strategies.md)")
    print(f"{BOLD}- Secure digital identity:{RESET} (see docs/impressioncore_b1_brain_security.md)")
    print(f"{BOLD}- BrainSim:{RESET} Cognitive simulation modules (see docs/BRAINSIM3.md)")
    print(f"{BOLD}- Modular:{RESET} Easily extensible for new models and tasks\n")

    # 2. Directory Structure
    print_header("PROJECT STRUCTURE (Visual)", icon="📁")
    print_project_tree()

    # 3. Visual Workflow
    print_header("VISUAL WORKFLOW DIAGRAM", icon="🔄")
    print_workflow_diagram()

    # 4. Hardware & Environment Checks
    print_header("SYSTEM & HARDWARE CHECKS", icon="🖥️")
    print_progress("Checking Python version", BLUE)
    check_python_version()
    print_progress("Checking GPU", BLUE)
    check_gpu()
    print_progress("Checking system RAM", BLUE)
    check_memory()
    print_info("For full hardware diagnostics, use the walkthrough UI or run: python main.py check-env\n")

    # 5. Documentation & Tools
    print_header("DOCUMENTATION & TOOLS", icon="📚")
    print(f"- {BOLD}User Guide:{RESET} docs/user_guide.md (or docs/user_guide.html for web)")
    print(f"- {BOLD}Architecture:{RESET} docs/ARCHITECTURE.md, docs/impressioncore_b1_architecture.md")
    print(f"- {BOLD}Memory Optimization:{RESET} docs/memory_optimization_strategies.md")
    print(f"- {BOLD}Error Codes:{RESET} docs/error_codes_registry.md")
    print(f"- {BOLD}Next Steps:{RESET} docs/next_steps.md | {BOLD}Roadmap:{RESET} docs/development_roadmap.md\n")
    print(f"- {BOLD}Tools:{RESET} See docs/user_guide_tools.md for CLI and web tools\n")

    # 6. Installation & Environment Setup
    print_header("INSTALLATION & ENVIRONMENT SETUP", icon="⚙️")
    print_animated("Clone the repository and set up a Python 3.10+ environment.", GREEN)
    print_command("git clone <repo-url>")
    print_command("cd impressioncore")
    print_command("python -m venv .venv && source .venv/bin/activate  # or use your preferred method")
    print("- Install core, dev, and optional extras:")
    print_command("pip install -e .")
    print_command("pip install -e .[dev]")
    print_command("pip install -e .[brainsim]")
    print_command("pip install -e .[diffusion]")
    print("- For GPU setup, see docs/GPU_SETUP.md and run the walkthrough's hardware check.\n")
    print_progress("Environment setup complete", GREEN)

    # 7. Walkthrough UI & Terminal
    print_header("WALKTHROUGH UI & TERMINAL INTEGRATION", icon="🖱️")
    print_animated("Start the web-based walkthrough UI:", CYAN)
    print_command("python run_server.py")
    print("- Access the UI in your browser (default: http://localhost:8000)")
    print("- Use the integrated terminal for commands like check-env, train, eval, and more.")
    print("- All changes, logs, and errors are reflected in real-time.\n")
    print_progress("Walkthrough UI ready", CYAN)

    # 8. Model Building & Configuration
    print_header("MODEL DEFINITION & CONFIGURATION", icon="🧩")
    print_animated("Use the walkthrough UI to select the ImpressionCore-b1 template.", YELLOW)
    print("- Adjust model parameters as needed (see docs/impressioncore_b1_architecture.md).")
    print("- Advanced: Try Mixture of Experts (MoE), LoRA, or custom adapters if available.")
    print("- All model configs are stored in src/models/architectures/ and src/core/config/\n")

    # 9. Data Preparation & Tokenization
    print_header("DATA PREPARATION & TOKENIZATION", icon="🗃️")
    print_animated("Prepare your dataset as described in docs/user_guide.md#data-preparation.", GREEN)
    print("- Train or load tokenizers for text/images using the walkthrough or CLI tools.")
    print_command("python main.py train-tokenizer --data <your_data>")
    print_command("python main.py tokenize --input <file> --output <out>")
    print("- For memory-efficient tokenization, see docs/memory_efficient_tokenization.md\n")

    # 10. Training, Memory Logging & Checkpoints
    print_header("TRAINING, MEMORY LOGGING & CHECKPOINTS", icon="🏋️")
    print_animated("Configure training parameters in the walkthrough or config files.", MAGENTA)
    print_command("python main.py train --config <config.yaml>")
    print("- Enable memory logging for all major operations (see src/utils/memory.py):")
    print("    from src.core.utils.memory import log_memory_usage\n    log_memory_usage('Before model init')")
    print("- Monitor VRAM and memory usage during training (see docs/memory_optimization_strategies.md).")
    print("- Checkpoints are saved automatically (see docs/CHECKPOINT_MANAGEMENT.md).\n")
    print_progress("Training setup complete", MAGENTA)

    # 11. Evaluation & Inference
    print_header("EVALUATION & INFERENCE", icon="📊")
    print_animated("Evaluate your model using built-in metrics (Perplexity, BLEU, ROUGE, BERTScore).", BLUE)
    print_command("python main.py eval --model <model.pt> --data <eval_data>")
    print("- Run inference on new data:")
    print_command("python main.py infer --model <model.pt> --input <input.txt>")
    print("- Use the walkthrough's inference environment for interactive testing.")
    print("- For advanced evaluation, see docs/advanced-features.md and docs/BENCHMARKING_TOOLS.md\n")
    print_progress("Evaluation & inference ready", BLUE)

    # 12. Brainsim & Cognitive Modules
    print_header("BRAINSIM & COGNITIVE MODULES", icon="🧬")
    print_animated("Explore src/brainsim/ for memory, multimodal, and cognitive architecture components.", CYAN)
    print("- See docs/BRAINSIM3.md for usage and integration examples.")
    print("- UKS (Unified Knowledge Store) and modal engine are available for advanced workflows.\n")

    # 13. Security & Digital Identity
    print_header("SECURITY & DIGITAL IDENTITY", icon="🔒")
    print_animated("Review docs/impressioncore_b1_brain_security.md for security architecture.", YELLOW)
    print("- All user data is protected with quantum-resistant cryptography.")
    print("- Input validation and access control modules are in src/core/security/\n")

    # 14. Error Handling & Logging
    print_header("ERROR HANDLING & LOGGING", icon="🚨")
    print_animated("All errors are logged in src/memlog/ with timestamps and context.", RED)
    print("- For error codes and solutions, see docs/error_codes_registry.md.")
    print("- Use the terminal for diagnostics and to review logs.\n")

    # 15. Development Workflow & Contribution
    print_header("DEVELOPMENT WORKFLOW & CONTRIBUTION", icon="🛠️")
    print_animated("Review architecture (docs/ARCHITECTURE.md), roadmap (docs/development_roadmap.md), and next steps (docs/next_steps.md).", GREEN)
    print("- Follow ImpressionCore Copilot Instructions for code style, documentation, and memory optimization.")
    print("- Document all changes in src/memlog and keep code modular (see /src structure).\n")

    # 16. Testing & Validation
    print_header("TESTING & VALIDATION", icon="🧪")
    print_animated("Use memory profiling tools (memory_profiler, tracemalloc) for Python.", CYAN)
    print("- Test under low-memory conditions (see docs/GPU_MEMORY_MANAGEMENT.md).")
    print("- Validate all new features with unit and integration tests in src/tests/\n")

    # 17. Support & Troubleshooting
    print_header("SUPPORT & TROUBLESHOOTING", icon="🆘")
    print_animated("If you encounter issues, consult docs/user_guide.md#troubleshooting.", YELLOW)
    print("- Use troubleshoot.bat (Windows) or the terminal for diagnostics.")
    print("- For community support, see project README.md for contact info.\n")

    print_header("END OF IMPRESSIONCORE ONBOARDING GUIDE", icon="🏁")
    print_animated("For a full walkthrough, see docs/walkthrough_plan.md and the User Guide.", CYAN)
    print_animated("Happy building with ImpressionCore-b1!", GREEN)
    print(CELEBRATE_BANNER)
    # Print a random 'Did you know?' tip
    tip = random.choice(DID_YOU_KNOW_TIPS)
    print(f"{BOLD}{MAGENTA}💡 Did you know?{RESET} {tip}\n")

if __name__ == "__main__":
    main()
