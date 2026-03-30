"""
Lightweight YAML config loader for B3 training pipeline.
Falls back gracefully if PyYAML is not installed.
"""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, TypeVar

T = TypeVar("T")


def _load_yaml(path: str) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except Exception:
        raise RuntimeError(
            "PyYAML not installed. Install with 'pip install pyyaml' or add to requirements.txt"
        ) from None
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def from_section(data: dict[str, Any], section: str, cls: type[T]) -> T:
    """Map a dict section onto a dataclass instance, using defaults for missing fields."""
    values: dict[str, Any] = data.get(section, {}) or {}
    if not is_dataclass(cls):
        return cls(**values)  # type: ignore[arg-type]
    # Build with defaults unless overridden
    inst = cls()  # type: ignore[call-arg]
    current = asdict(inst)
    current.update({k: v for k, v in values.items() if k in current})
    return cls(**current)  # type: ignore[call-arg]


def load_all(path: str) -> dict[str, Any]:
    return _load_yaml(path)
