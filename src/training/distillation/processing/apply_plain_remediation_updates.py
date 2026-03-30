"""Merge freshly generated plain-language remediation teacher responses into the
primary regulator remediation blend dataset.

Usage:
    python -m src.training.distillation.processing.apply_plain_remediation_updates \
        --plain src/training/distillation/kd_inputs/generated/ollama_plain_remediation_teacher_20251027.json \
        --target src/training/distillation/kd_inputs/generated/ollama_combined_teacher_20251026_regulator_remediation_blend.json

The script keeps the dual-teacher structure (llama3.2:3b + phi3.5:3.8b-mini-instruct-q4_K_M)
and ignores any auxiliary models captured during ad-hoc regeneration runs.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

PRIMARY_TEACHERS = (
    "llama3.2:3b",
    "phi3.5:3.8b-mini-instruct-q4_K_M",
)


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:  # pragma: no cover - defensive guard
        raise SystemExit(f"Missing input file: {path}") from exc
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive guard
        raise SystemExit(f"Invalid JSON payload in {path}: {exc}") from exc


def apply_updates(plain_path: Path, target_path: Path) -> int:
    plain_payload = _load_json(plain_path)
    target_payload = _load_json(target_path)

    plain_map = {
        example.get("prompt"): example
        for example in plain_payload.get("examples", [])
        if isinstance(example.get("prompt"), str)
    }

    updated = 0
    for example in target_payload.get("examples", []):
        prompt = example.get("prompt")
        plain_example = plain_map.get(prompt)
        if not plain_example:
            continue

        responses = plain_example.get("teacher_responses", {})
        if not isinstance(responses, dict):
            continue

        teacher_responses = example.setdefault("teacher_responses", {})
        for teacher_id in PRIMARY_TEACHERS:
            if teacher_id in responses:
                teacher_responses[teacher_id] = responses[teacher_id]

        timestamp = plain_example.get("timestamp")
        if isinstance(timestamp, str):
            example["timestamp"] = timestamp

        updated += 1

    if updated:
        target_payload["generation_timestamp"] = datetime.now(timezone.utc).isoformat()
        target_payload["total_examples"] = len(target_payload.get("examples", []))
        target_path.write_text(json.dumps(target_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Update blended remediation dataset with plain-language responses")
    parser.add_argument("--plain", type=Path, required=True, help="Path to freshly generated plain-language teacher JSON")
    parser.add_argument(
        "--target",
        type=Path,
        required=True,
        help="Target blended dataset JSON path to update",
    )
    args = parser.parse_args()

    updated = apply_updates(args.plain, args.target)
    if updated == 0:
        raise SystemExit("No prompts from the plain-language file matched the target dataset.")
    print(f"[ok] Updated {updated} prompts in {args.target}")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
