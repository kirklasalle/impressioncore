"""Structural integrity tests — verify project layout conventions.

These tests act as guardrails to prevent regressions into the messy
root directory state that the cleanup phases eliminated.
"""
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


class TestRootCleanliness:
    """The project root should contain only governance-approved items."""

    ALLOWED_ROOT_FILES = {
        # Governance / documentation
        "README.md",
        "CONTRIBUTING.md",
        "COPILOT_PRIME_DIRECTIVE.md",
        "COPILOT_SACRED_COVENANT.md",
        "HANDOFF_FROM_GUITARGAMES.md",
        "Prime_Directive.txt",
        # Dependency manifests
        "requirements.txt",
        "requirements-phase3.txt",
        "pyproject.toml",
        "pytest.ini",
        # Approved launchers
        "manage_f_models.py",
        # Config
        ".gitignore",
        ".pre-commit-config.yaml",
        ".env.example",
    }

    ALLOWED_ROOT_DIRS = {
        "src",
        "docs",
        "agent0core",
        "bin",
        ".git",
        ".github",
        ".mcp",
        ".vscode",
        ".venv310",
        "backup",
        "backups",
        # Transient (gitignored)
        "cache",
        "temp",
        "test_outputs",
        "logs",
        "checkpoints",
        "models",
        "static",
        "data",
        "production_packages",
        "rag_library",
        "docker",
        "user_data",
        "output",
        ".agent",
        ".cache",
        # Ghost dirs (recreated by VS Code / tooling; harmless when empty)
        "config",
        "history",
        ".goliath_backups",
        ".goliath_logs",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
        "node_modules",
    }

    def test_no_loose_python_scripts(self, project_root: Path):
        """No stray .py files in root, other than approved launcher/shims.

        Each allowed shim delegates to a canonical implementation under
        ``src/`` (see the docstring of each file for its delegation target)
        and exists only because it is a documented user-facing entry point
        (e.g. ``docs/user_guide/*.md`` instructs users to run
        ``python run_server.py`` from the repo root).
        """
        py_files = {f.name for f in project_root.glob("*.py")}
        allowed = {
            "manage_f_models.py",
            "main.py",  # shim -> src/main.py
            "run_server.py",  # shim -> src/services/sse/run_server.py
            "build_cli_automation.py",  # shim -> src/dev_tools/automation/build_cli_automation.py
        }
        stray = py_files - allowed
        assert not stray, f"Stray root .py files found: {stray}"

    def test_no_loose_log_files(self, project_root: Path):
        """No .log or .json artifacts in root."""
        artifacts = {f.name for f in project_root.iterdir()
                     if f.is_file() and f.suffix in (".log", ".json", ".jpg", ".png")}
        assert not artifacts, f"Root artifacts found: {artifacts}"

    def test_no_unexpected_directories(self, project_root: Path):
        """All root directories should be in the allowed set."""
        dirs = {d.name for d in project_root.iterdir() if d.is_dir()}
        unexpected = dirs - self.ALLOWED_ROOT_DIRS
        assert not unexpected, f"Unexpected root directories: {unexpected}"


class TestCanonicalDirectories:
    """Key canonical directories must exist and have __init__.py."""

    REQUIRED_PACKAGES = [
        "src/core",
        "src/core/config",
        "src/core/memory",
        "src/core/protocols",
        "src/training",
        "src/inference",
        "src/tests",
    ]

    @pytest.mark.parametrize("pkg_path", REQUIRED_PACKAGES)
    def test_package_has_init(self, project_root: Path, pkg_path: str):
        init = project_root / pkg_path / "__init__.py"
        assert init.exists(), f"Missing __init__.py in {pkg_path}"

    def test_config_files_in_canonical_location(self, project_root: Path):
        """Config files should live in src/core/config/, not root config/."""
        root_config = project_root / "config"
        if root_config.exists():
            contents = list(root_config.iterdir())
            assert not contents, (
                f"Root config/ contains files — migrate to src/core/config/: "
                f"{[c.name for c in contents]}"
            )
        assert (project_root / "src" / "core" / "config" / "triad_config.json").exists()

    def test_tests_in_canonical_location(self, project_root: Path):
        """Tests should live in src/tests/, not root tests/."""
        assert not (project_root / "tests").exists(), \
            "Root tests/ still exists — should have been consolidated into src/tests/"
