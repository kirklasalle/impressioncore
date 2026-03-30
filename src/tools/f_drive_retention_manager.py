from __future__ import annotations

import argparse
import logging
import shutil
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

LOGGER = logging.getLogger("impressioncore.f_drive_retention")

CHECKPOINT_SUFFIXES = {".pt", ".pth", ".ckpt", ".bin", ".safetensors"}


@dataclass(slots=True)
class RetentionCandidate:
    """Represents a removable file candidate for retention cleanup."""

    path: Path
    size_bytes: int
    modified_at: datetime
    reason: str


@dataclass(slots=True)
class RetentionPolicy:
    """Configurable retention policy for F: drive management."""

    drive_root: Path
    target_free_gb: float
    max_hf_cache_age_days: int
    max_processed_age_days: int
    keep_checkpoints_per_dir: int
    enforce: bool


def bytes_to_gb(value: int) -> float:
    """Convert bytes to gigabytes."""

    return value / (1024**3)


def get_drive_usage(root: Path) -> tuple[int, int, int]:
    """Return total, used, and free bytes for the given drive root."""

    total, used, free = shutil.disk_usage(str(root))
    return total, used, free


def iter_files(root: Path) -> list[Path]:
    """Enumerate regular files under root safely."""

    if not root.exists():
        return []

    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_file():
            files.append(path)
    return files


def candidate_from_path(path: Path, reason: str) -> RetentionCandidate | None:
    """Build a retention candidate from a file path if metadata is accessible."""

    try:
        stat = path.stat()
    except OSError:
        return None

    return RetentionCandidate(
        path=path,
        size_bytes=stat.st_size,
        modified_at=datetime.fromtimestamp(stat.st_mtime),
        reason=reason,
    )


def collect_hf_cache_candidates(policy: RetentionPolicy) -> list[RetentionCandidate]:
    """Collect old HuggingFace cache files under F:/data/huggingface_cache."""

    cache_root = policy.drive_root / "data" / "huggingface_cache"
    cutoff = datetime.now() - timedelta(days=policy.max_hf_cache_age_days)

    candidates: list[RetentionCandidate] = []
    for path in iter_files(cache_root):
        try:
            modified = datetime.fromtimestamp(path.stat().st_mtime)
        except OSError:
            continue
        if modified < cutoff:
            candidate = candidate_from_path(path, "hf_cache_age")
            if candidate is not None:
                candidates.append(candidate)

    return candidates


def collect_processed_candidates(policy: RetentionPolicy) -> list[RetentionCandidate]:
    """Collect old processed data files under F:/data/processed."""

    processed_root = policy.drive_root / "data" / "processed"
    cutoff = datetime.now() - timedelta(days=policy.max_processed_age_days)

    candidates: list[RetentionCandidate] = []
    for path in iter_files(processed_root):
        try:
            modified = datetime.fromtimestamp(path.stat().st_mtime)
        except OSError:
            continue
        if modified < cutoff:
            candidate = candidate_from_path(path, "processed_age")
            if candidate is not None:
                candidates.append(candidate)

    return candidates


def collect_checkpoint_candidates(policy: RetentionPolicy) -> list[RetentionCandidate]:
    """Collect checkpoint files exceeding keep count per checkpoint directory."""

    checkpoints_root = policy.drive_root / "models" / "checkpoints"
    if not checkpoints_root.exists():
        return []

    candidates: list[RetentionCandidate] = []

    for directory in checkpoints_root.rglob("*"):
        if not directory.is_dir():
            continue

        checkpoint_files = [
            p
            for p in directory.iterdir()
            if p.is_file() and p.suffix.lower() in CHECKPOINT_SUFFIXES
        ]
        if len(checkpoint_files) <= policy.keep_checkpoints_per_dir:
            continue

        checkpoint_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        overflow = checkpoint_files[policy.keep_checkpoints_per_dir :]

        for path in overflow:
            candidate = candidate_from_path(path, "checkpoint_overflow")
            if candidate is not None:
                candidates.append(candidate)

    return candidates


def build_plan(policy: RetentionPolicy) -> list[RetentionCandidate]:
    """Build full retention plan sorted by oldest files first."""

    candidates = []
    candidates.extend(collect_hf_cache_candidates(policy))
    candidates.extend(collect_processed_candidates(policy))
    candidates.extend(collect_checkpoint_candidates(policy))
    candidates.sort(key=lambda item: item.modified_at)
    return candidates


def summarize_candidates(candidates: list[RetentionCandidate]) -> dict[str, tuple[int, int]]:
    """Return count and bytes grouped by retention reason."""

    summary: dict[str, tuple[int, int]] = {}
    counts: dict[str, int] = {}
    bytes_map: dict[str, int] = {}

    for candidate in candidates:
        counts[candidate.reason] = counts.get(candidate.reason, 0) + 1
        bytes_map[candidate.reason] = bytes_map.get(candidate.reason, 0) + candidate.size_bytes

    for reason in sorted(counts.keys()):
        summary[reason] = (counts[reason], bytes_map[reason])

    return summary


def execute_plan(
    candidates: list[RetentionCandidate],
    required_bytes: int,
    enforce: bool,
    preview_limit: int,
) -> tuple[int, int]:
    """Execute or simulate deletions until required_bytes is reached."""

    reclaimed = 0
    processed = 0

    preview_emitted = 0
    preview_suppressed_logged = False

    for candidate in candidates:
        if reclaimed >= required_bytes:
            break

        processed += 1
        if enforce:
            try:
                candidate.path.unlink(missing_ok=False)
                LOGGER.info("deleted %s (%s)", candidate.path, candidate.reason)
            except OSError as exc:
                LOGGER.warning("failed to delete %s: %s", candidate.path, exc)
                continue
        else:
            if preview_emitted < preview_limit:
                LOGGER.info("plan-delete %s (%s)", candidate.path, candidate.reason)
                preview_emitted += 1
            elif not preview_suppressed_logged:
                LOGGER.info("plan-delete output truncated after %d items", preview_limit)
                preview_suppressed_logged = True

        reclaimed += candidate.size_bytes

    return reclaimed, processed


def main() -> None:
    """Run F: drive retention planning and optional enforcement."""

    parser = argparse.ArgumentParser(description="ImpressionCore F: drive retention manager")
    parser.add_argument("--drive-root", type=str, default="F:/", help="Drive root to manage")
    parser.add_argument("--target-free-gb", type=float, default=95.0, help="Desired free-space floor in GB")
    parser.add_argument("--hf-cache-age-days", type=int, default=30, help="Max age for HF cache files")
    parser.add_argument("--processed-age-days", type=int, default=45, help="Max age for processed files")
    parser.add_argument(
        "--keep-checkpoints-per-dir",
        type=int,
        default=4,
        help="How many newest checkpoint files to keep per checkpoint directory",
    )
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="Actually delete files (without this flag, script runs in dry-run mode)",
    )
    parser.add_argument(
        "--preview-limit",
        type=int,
        default=250,
        help="How many planned items to print in dry-run mode",
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

    policy = RetentionPolicy(
        drive_root=Path(args.drive_root),
        target_free_gb=args.target_free_gb,
        max_hf_cache_age_days=args.hf_cache_age_days,
        max_processed_age_days=args.processed_age_days,
        keep_checkpoints_per_dir=max(1, args.keep_checkpoints_per_dir),
        enforce=bool(args.enforce),
    )

    total, used, free = get_drive_usage(policy.drive_root)
    free_gb = bytes_to_gb(free)
    required_gb = max(0.0, policy.target_free_gb - free_gb)
    required_bytes = int(required_gb * (1024**3))

    mode = "ENFORCE" if policy.enforce else "DRY-RUN"
    LOGGER.info("mode=%s", mode)
    LOGGER.info("drive=%s total_gb=%.2f used_gb=%.2f free_gb=%.2f", policy.drive_root, bytes_to_gb(total), bytes_to_gb(used), free_gb)
    LOGGER.info("target_free_gb=%.2f shortfall_gb=%.2f", policy.target_free_gb, required_gb)

    plan = build_plan(policy)
    plan_bytes = sum(item.size_bytes for item in plan)
    LOGGER.info("plan_candidates=%d plan_reclaimable_gb=%.2f", len(plan), bytes_to_gb(plan_bytes))

    summary = summarize_candidates(plan)
    for reason, (count, size_bytes) in summary.items():
        LOGGER.info("plan_reason=%s count=%d reclaimable_gb=%.2f", reason, count, bytes_to_gb(size_bytes))

    if required_bytes <= 0:
        LOGGER.info("no action required; free space already meets target")
        return

    if not plan:
        LOGGER.warning("no cleanup candidates found")
        return

    reclaimed_bytes, processed_count = execute_plan(
        plan,
        required_bytes=required_bytes,
        enforce=policy.enforce,
        preview_limit=max(0, args.preview_limit),
    )
    LOGGER.info(
        "processed_candidates=%d reclaimed_gb=%.2f target_shortfall_gb=%.2f",
        processed_count,
        bytes_to_gb(reclaimed_bytes),
        required_gb,
    )

    if reclaimed_bytes < required_bytes:
        LOGGER.warning("retention policy cannot fully satisfy target free-space floor with current candidates")


if __name__ == "__main__":
    main()
