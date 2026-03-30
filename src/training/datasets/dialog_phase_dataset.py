"""Dialog-phase dataset utilities for ImpressionCore warm-start training."""
from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import torch
from torch.utils.data import Dataset

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class DialogSample:
    """Container for a tokenised dialog example."""

    input_ids: torch.Tensor
    attention_mask: torch.Tensor
    labels: torch.Tensor
    modalities: Sequence[str]
    source_path: Path


class DialogPhaseDataset(Dataset[dict[str, torch.Tensor]]):
    """Dataset that materialises dialog samples defined by a manifest."""

    def __init__(
        self,
        manifest_path: str,
        tokenizer,
        max_seq_length: int,
        min_tokens: int = 4,
    ) -> None:
        self.manifest_path = Path(manifest_path)
        self.tokenizer = tokenizer
        self.max_seq_length = max_seq_length
        self.min_tokens = min_tokens
        self.samples: list[DialogSample] = []
        self.modalities_tally: Counter[str] = Counter()
        self._load_manifest()

        if not self.samples:
            raise ValueError(
                "No training samples were produced from manifest: "
                f"{self.manifest_path}. Verify the manifest paths and tokenizer."
            )

    # ------------------------------------------------------------------
    def __len__(self) -> int:
        return len(self.samples)

    # ------------------------------------------------------------------
    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        sample = self.samples[index]
        return {
            "input_ids": sample.input_ids,
            "attention_mask": sample.attention_mask,
            "labels": sample.labels,
        }

    # ------------------------------------------------------------------
    def collate_fn(self, batch: Sequence[dict[str, torch.Tensor]]) -> dict[str, torch.Tensor]:
        input_ids = torch.stack([item["input_ids"] for item in batch])
        attention_mask = torch.stack([item["attention_mask"] for item in batch])
        labels = torch.stack([item["labels"] for item in batch])
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }

    # ------------------------------------------------------------------
    def _load_manifest(self) -> None:
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Dataset manifest not found: {self.manifest_path}")

        with self.manifest_path.open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)

        for entry in manifest.get("splits", {}).get("train", []):
            path = Path(entry.get("path", "")).expanduser()
            if not path.exists():
                logger.warning("Skipping missing dataset shard: %s", path)
                continue

            modalities = entry.get("modalities", [])
            self._materialise_shard(path, modalities)

        logger.info(
            "DialogPhaseDataset loaded %s samples across %s modalities", len(self.samples), dict(self.modalities_tally)
        )

    # ------------------------------------------------------------------
    def _materialise_shard(self, shard_path: Path, modalities: Iterable[str]) -> None:
        with shard_path.open("r", encoding="utf-8") as shard:
            for line_number, line in enumerate(shard, start=1):
                record = line.strip()
                if not record:
                    continue
                text_payload = self._extract_text(record, shard_path, line_number)
                if not text_payload:
                    continue
                encoded = self.tokenizer(
                    text_payload,
                    truncation=True,
                    max_length=self.max_seq_length,
                    padding="max_length",
                    return_tensors="pt",
                )
                input_ids = encoded["input_ids"].squeeze(0)
                attention_mask = encoded["attention_mask"].squeeze(0)
                if attention_mask.sum().item() < self.min_tokens:
                    continue
                labels = input_ids.clone()
                self.samples.append(
                    DialogSample(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        labels=labels,
                        modalities=list(modalities),
                        source_path=shard_path,
                    )
                )
                for modality in modalities:
                    self.modalities_tally[modality] += 1

    # ------------------------------------------------------------------
    def _extract_text(self, record: str, shard_path: Path, line_number: int) -> str | None:
        try:
            payload = json.loads(record)
        except json.JSONDecodeError:
            return record

        if isinstance(payload, str):
            return payload

        if isinstance(payload, dict):
            for candidate in ("text", "utterance", "content", "answer"):
                value = payload.get(candidate)
                if isinstance(value, str) and value.strip():
                    return value

            if "messages" in payload and isinstance(payload["messages"], list):
                return self._stringify_messages(payload["messages"])

            if "dialogue" in payload and isinstance(payload["dialogue"], list):
                return self._stringify_messages(payload["dialogue"])

            prompt = payload.get("prompt")
            response = payload.get("response")
            if isinstance(prompt, str) and isinstance(response, str):
                return f"Human: {prompt.strip()}\nAssistant: {response.strip()}"

        logger.debug(
            "Dropping unhandled record at %s:%s - unable to extract text payload", shard_path, line_number
        )
        return None

    # ------------------------------------------------------------------
    @staticmethod
    def _stringify_messages(messages: Sequence[dict[str, object]]) -> str | None:
        fragments: list[str] = []
        for message in messages:
            if not isinstance(message, dict):
                continue
            role = message.get("role")
            content = message.get("content")
            if isinstance(content, dict):
                content = content.get("text")
            if isinstance(content, list):
                content = " ".join(str(piece) for piece in content if isinstance(piece, str))
            if isinstance(content, str) and content.strip():
                prefix = f"{role}: " if isinstance(role, str) else ""
                fragments.append(prefix + content.strip())
        if fragments:
            return "\n".join(fragments)
        return None


def export_dialog_phase_shards(
    manifest_path: Path,
    output_root: Path,
    *,
    output_manifest: Path | None = None,
    dry_run: bool = False,
    overwrite: bool = False,
) -> dict[str, object]:
    manifest_path = manifest_path.resolve()
    output_root = output_root.resolve()
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    exported: list[dict[str, object]] = []
    new_manifest = json.loads(json.dumps(manifest))

    for split_name, entries in manifest.get("splits", {}).items():
        updated_entries: list[dict[str, object]] = []
        for entry in entries:
            entry_path = entry.get("path")
            if not entry_path:
                continue

            source_path = _resolve_source_path(entry_path, manifest_path)
            if not source_path.exists():
                raise FileNotFoundError(f"Source shard missing: {source_path}")

            destination_dir = output_root / split_name
            destination_path = destination_dir / source_path.name

            if dry_run:
                logger.info("Dry-run: would export %s -> %s", source_path, destination_path)
            else:
                destination_dir.mkdir(parents=True, exist_ok=True)
                if destination_path.exists() and not overwrite:
                    raise FileExistsError(f"Destination already exists: {destination_path}")
                shutil.copy2(source_path, destination_path)

            record_count = _count_records(source_path)
            updated_entry = dict(entry)
            updated_entry["path"] = destination_path.as_posix()
            updated_entries.append(updated_entry)

            exported.append(
                {
                    "split": split_name,
                    "source": source_path.as_posix(),
                    "destination": destination_path.as_posix(),
                    "records": record_count,
                }
            )

        new_manifest.setdefault("splits", {})[split_name] = updated_entries

    export_manifest_path = output_manifest or output_root / "dialog_phase1_manifest.json"
    metadata = {
        "source_manifest": manifest_path.as_posix(),
        "export_root": output_root.as_posix(),
        "exported_at": datetime.utcnow().isoformat() + "Z",
        "dry_run": dry_run,
        "shard_count": len(exported),
    }
    new_manifest["export_metadata"] = metadata

    if dry_run:
        logger.info("Dry-run: manifest would be written to %s", export_manifest_path)
    else:
        export_manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with export_manifest_path.open("w", encoding="utf-8") as handle:
            json.dump(new_manifest, handle, indent=4)
        logger.info("Export manifest written to %s", export_manifest_path)

    return {"manifest": new_manifest, "exported": exported, "metadata": metadata}


def _count_records(shard_path: Path) -> int:
    with shard_path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def _resolve_source_path(entry_path: str, manifest_path: Path) -> Path:
    candidate = Path(entry_path)
    if candidate.is_absolute():
        return candidate

    repo_candidate = (PROJECT_ROOT / candidate).resolve()
    if repo_candidate.exists():
        return repo_candidate

    local_candidate = (manifest_path.parent / candidate).resolve()
    return local_candidate


def _build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export dialog phase shards to an external root")
    parser.add_argument("--manifest", required=True, help="Source manifest path")
    parser.add_argument("--output-root", required=True, help="Destination directory root")
    parser.add_argument("--output-manifest", help="Optional explicit manifest destination")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without copying files")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing destination shards")
    return parser


def _run_cli() -> None:
    parser = _build_cli_parser()
    args = parser.parse_args()
    summary = export_dialog_phase_shards(
        manifest_path=Path(args.manifest),
        output_root=Path(args.output_root),
        output_manifest=Path(args.output_manifest) if args.output_manifest else None,
        dry_run=args.dry_run,
        overwrite=args.overwrite,
    )
    json.dump(summary, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__" and len(sys.argv) > 1:
    _run_cli()
