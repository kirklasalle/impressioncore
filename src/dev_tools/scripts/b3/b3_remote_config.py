#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #python #source_code #src/scripts\b3\b3_remote_config.py
**Category:** Source Code
**Status:** Active
"""



import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class OpenRouterConfig:
    """OpenRouter API configuration"""
    api_key: str = ""
    base_url: str = "https://openrouter.ai/api/v1"
    app_name: str = "ImpressionCore B3 Remote Distillation"
    app_url: str = "https://impressioncore.ai"

@dataclass
class TeacherModelConfig:
    """Teacher model configuration"""
    model_id: str = "moonshotai/kimi-k2:free"
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    timeout: int = 30
    max_retries: int = 3

@dataclass
class RemoteDistillationConfig:
    """Complete remote distillation configuration"""
    openrouter: OpenRouterConfig
    teacher_model: TeacherModelConfig
    curriculum_settings: dict[str, Any]
    performance_thresholds: dict[str, float]

    def save_to_file(self, filepath: str):
        """Save configuration to JSON file"""
        config_dict = asdict(self)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str) -> 'RemoteDistillationConfig':
        """Load configuration from JSON file"""
        with open(filepath, encoding='utf-8') as f:
            config_dict = json.load(f)

        return cls(
            openrouter=OpenRouterConfig(**config_dict['openrouter']),
            teacher_model=TeacherModelConfig(**config_dict['teacher_model']),
            curriculum_settings=config_dict['curriculum_settings'],
            performance_thresholds=config_dict['performance_thresholds']
        )

def create_default_config() -> RemoteDistillationConfig:
    """Create default configuration for remote distillation"""
    return RemoteDistillationConfig(
        openrouter=OpenRouterConfig(),
        teacher_model=TeacherModelConfig(),
        curriculum_settings={
            "progressive_stages": 4,
            "samples_per_stage": [30, 40, 35, 25],
            "complexity_progression": [0.3, 0.6, 0.8, 1.0],
            "rate_limiting_delay": 0.5,
            "fallback_enabled": True
        },
        performance_thresholds={
            "min_performance_score": 0.88,
            "min_improvement": 0.18,
            "min_quality": 9.95,
            "min_retention": 0.87,
            "min_teacher_quality": 0.80,
            "min_api_success": 0.85
        }
    )

def setup_environment() -> str | None:
    """Setup environment and return API key if available"""
    # Check for API key in environment
    api_key = os.getenv('OPENROUTER_API_KEY')

    if api_key:
        return api_key

    # Check for config file
    config_path = Path("remote_distillation_config.json")
    if config_path.exists():
        try:
            config = RemoteDistillationConfig.load_from_file(config_path)
            if config.openrouter.api_key:
                return config.openrouter.api_key
        except Exception:
            pass

    return None

def save_default_config():
    """Save default configuration to file"""
    config = create_default_config()
    config.save_to_file("remote_distillation_config.json")
    print("✅ Default configuration saved to remote_distillation_config.json")
    print("📝 Please edit the file to add your OpenRouter API key")

if __name__ == "__main__":
    save_default_config()
