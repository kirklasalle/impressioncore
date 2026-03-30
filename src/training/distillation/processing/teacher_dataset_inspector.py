"""Inspect teacher datasets for prompt coverage and response length statistics."""
from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from pathlib import Path
from statistics import mean

FOCUS_PROMPTS: list[str] = [
    "During the regulator rehearing briefing, one analyst says they are \"lost in the philosophy\" of why the pause is necessary. Draft a coaching response that reconnects them to statutory requirements and lists three concrete next actions.",
    "What signals indicate the team must pause a rehearing to refresh terminology baselines?",
    "Which follow-through assignments ensure privacy requirements remain addressed after rehearing decisions?",
]


def _response_lengths(examples: Iterable[dict[str, object]]) -> dict[str, list[int]]:
    lengths: dict[str, list[int]] = {}
    for example in examples:
        responses = example.get("teacher_responses")
        if not isinstance(responses, dict):
            continue
        for teacher_id, text in responses.items():
            if not isinstance(text, str):
                continue
            lengths.setdefault(teacher_id, []).append(len(text))
    return lengths


def inspect_dataset(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    examples = payload.get("examples", [])
    if not isinstance(examples, list):
        print(f"[warn] {path}: examples array missing")
        return

    print(f"Dataset: {path}")
    print(f"  total_examples: {len(examples)}")

    lengths = _response_lengths(examples)
    for teacher_id, values in sorted(lengths.items()):
        if not values:
            continue
        print(
            f"  teacher {teacher_id}: min={min(values)} max={max(values)} avg={mean(values):.1f}"
        )

    for prompt in FOCUS_PROMPTS:
        for example in examples:
            if example.get("prompt") == prompt:
                print(f"  focus prompt: {prompt}")
                responses = example.get("teacher_responses", {})
                for teacher_id, text in responses.items():
                    if isinstance(text, str):
                        print(f"    {teacher_id}: len={len(text)}")
                break


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect teacher datasets")
    parser.add_argument("datasets", nargs="+", type=Path, help="Paths to teacher dataset JSON files")
    args = parser.parse_args()

    for dataset in args.datasets:
        if dataset.exists():
            inspect_dataset(dataset)
        else:
            print(f"[warn] dataset not found: {dataset}")


if __name__ == "__main__":
    main()
