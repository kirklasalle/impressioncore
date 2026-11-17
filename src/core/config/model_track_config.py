import os
from dataclasses import dataclass


def _normalize(path: str) -> str:
    return path.replace("\\", "/").rstrip("/")


def _is_f_drive_path(path: str) -> bool:
    normalized = _normalize(path).lower()
    return normalized.startswith("f:/")


@dataclass
class ModelTrackConfig:
    """Model-only track configuration for architecture, data, embeddings, and training."""

    model_root: str = "F:/models"
    data_root: str = "F:/data"
    embeddings_root: str = "F:/data/embeddings"
    datasets_root: str = "F:/data/datasets"
    checkpoints_root: str = "F:/models/checkpoints"
    dpo_dataset_path: str = "src/training/data/datasets/dpo_phase3_dataset_with_logprobs.jsonl"

    def validate(self) -> None:
        """Validate mandatory F: path policy for the model-only track."""
        tracked_paths = {
            "model_root": self.model_root,
            "data_root": self.data_root,
            "embeddings_root": self.embeddings_root,
            "datasets_root": self.datasets_root,
            "checkpoints_root": self.checkpoints_root,
        }
        for name, value in tracked_paths.items():
            if not _is_f_drive_path(value):
                raise ValueError(
                    f"{name} must be on F: drive for model-only track. Got: {value}"
                )


def load_model_track_config() -> ModelTrackConfig:
    """Load model-only track configuration with F: mandatory defaults."""
    cfg = ModelTrackConfig(
        model_root=os.getenv("IMPRESSIONCORE_MODEL_ROOT", "F:/models"),
        data_root=os.getenv("IMPRESSIONCORE_DATA_ROOT", "F:/data"),
        embeddings_root=os.getenv("IMPRESSIONCORE_EMBEDDINGS_ROOT", "F:/data/embeddings"),
        datasets_root=os.getenv("IMPRESSIONCORE_DATASETS_ROOT", "F:/data/datasets"),
        checkpoints_root=os.getenv("IMPRESSIONCORE_CHECKPOINTS_ROOT", "F:/models/checkpoints"),
        dpo_dataset_path=os.getenv(
            "IMPRESSIONCORE_DPO_DATASET_PATH",
            "src/training/data/datasets/dpo_phase3_dataset_with_logprobs.jsonl",
        ),
    )
    cfg.validate()
    return cfg
