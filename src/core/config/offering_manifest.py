"""Offering manifest schema validation for B-series models.

WS1 deliverable: validates offering presets at startup to prevent metadata
drift between declared model stage and discovered artifacts.
"""
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger("impressioncore.offering_manifest")

# Required schema keys for offering validation
_REQUIRED_TOP_KEYS = {"id", "stage", "name", "target_params_m", "model", "training"}
_REQUIRED_MODEL_KEYS = {
    "architecture", "preset", "layers", "hiddenSize", "heads",
    "intermediateSize", "contextWindow", "vocabSize", "precision",
    "activation", "rope",
}
_REQUIRED_TRAINING_KEYS = {
    "epochs", "batchSize", "learningRate", "warmupSteps",
    "scheduler", "precision", "gradCheckpoint", "gradAccumSteps",
    "maxSteps", "checkpointDir",
}
_VALID_STAGES = {"B1", "B2", "B3"}


def validate_offering_preset(preset_id: str, preset: Dict[str, Any]) -> List[str]:
    """Validate a single offering preset against the manifest schema.

    Returns a list of error strings. Empty list means valid.
    """
    errors: List[str] = []

    # Top-level key check
    missing_top = _REQUIRED_TOP_KEYS - set(preset.keys())
    if missing_top:
        errors.append(f"[{preset_id}] Missing top-level keys: {missing_top}")

    # ID consistency
    if preset.get("id") != preset_id:
        errors.append(f"[{preset_id}] Preset id '{preset.get('id')}' does not match key '{preset_id}'")

    # Stage validation
    stage = preset.get("stage")
    if stage not in _VALID_STAGES:
        errors.append(f"[{preset_id}] Invalid stage '{stage}', expected one of {_VALID_STAGES}")

    # Target params positive
    target = preset.get("target_params_m")
    if not isinstance(target, (int, float)) or target <= 0:
        errors.append(f"[{preset_id}] target_params_m must be a positive number, got {target}")

    # Model sub-schema
    model = preset.get("model", {})
    if isinstance(model, dict):
        missing_model = _REQUIRED_MODEL_KEYS - set(model.keys())
        if missing_model:
            errors.append(f"[{preset_id}] Missing model keys: {missing_model}")
    else:
        errors.append(f"[{preset_id}] 'model' must be a dict")

    # Training sub-schema
    training = preset.get("training", {})
    if isinstance(training, dict):
        missing_training = _REQUIRED_TRAINING_KEYS - set(training.keys())
        if missing_training:
            errors.append(f"[{preset_id}] Missing training keys: {missing_training}")
    else:
        errors.append(f"[{preset_id}] 'training' must be a dict")

    return errors


def validate_all_offerings(presets: Dict[str, Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """Validate all offering presets.

    Returns (is_valid, list_of_errors).
    """
    all_errors: List[str] = []

    if not presets:
        all_errors.append("No offering presets found")
        return False, all_errors

    for preset_id, preset in presets.items():
        errors = validate_offering_preset(preset_id, preset)
        all_errors.extend(errors)

    return len(all_errors) == 0, all_errors


def validate_offerings_at_startup() -> bool:
    """Validate offering presets at application startup.

    Called during Builder/Runtime initialization to ensure manifest integrity.
    Logs errors but does not raise — allows startup with warnings.
    """
    from src.core.config.presets import OFFERING_PRESETS

    is_valid, errors = validate_all_offerings(OFFERING_PRESETS)

    if is_valid:
        logger.info(
            "Offering manifest validation passed: %d offerings verified",
            len(OFFERING_PRESETS),
        )
    else:
        logger.error(
            "Offering manifest validation FAILED with %d error(s):",
            len(errors),
        )
        for err in errors:
            logger.error("  - %s", err)

    return is_valid
