"""Configuration provider protocol for loading and serializing configs."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ConfigProviderProtocol(Protocol):
    """Contract for configuration providers.

    Both ``ConfigManager`` implementations (config_manager.py and config.py)
    satisfy this protocol through duck typing.
    """

    def load_config(self, source: str = "") -> dict[str, Any]:
        """Load configuration from *source* (path, preset name, or default).

        Returns a plain dict representation of the configuration.
        """
        ...

    def get_inference_settings(self) -> dict[str, Any]:
        """Return inference-specific settings (batch size, precision, …)."""
        ...

    def get_training_settings(self) -> dict[str, Any]:
        """Return training-specific settings (lr, epochs, optimizer, …)."""
        ...


@runtime_checkable
class SerializableConfigProtocol(Protocol):
    """Any dataclass-style config that can round-trip through dicts / JSON."""

    def to_dict(self) -> dict[str, Any]:
        ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SerializableConfigProtocol:
        ...

    @classmethod
    def from_json(cls, path: str) -> SerializableConfigProtocol:
        ...

    def save_json(self, path: str) -> None:
        ...
