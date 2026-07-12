#!/usr/bin/env python3
"""
ImpressionCore B3 — Production Model Exporter

File: src/core/export/export_production_model.py
Created: April 2026
Authors: Kirk LaSalle; GitHub Copilot
Status: Active

Exports a trained B3 checkpoint into the canonical production artifact format:

    <output_dir>/
    ├── model.pt                    # Quantized model weights (state_dict)
    ├── config.json                 # B3Config serialized
    ├── tokenizer/                  # Hybrid tokenizer files
    │   ├── dialogpt_input/         # DialoGPT-small config + vocab
    │   └── gpt2_output/            # GPT-2 config + vocab
    ├── metadata.json               # Training provenance, params, quality scores
    ├── colossus_heads.pt           # Colossus integration weights (if present)
    └── MANIFEST.md                 # Human-readable artifact description

Hardware target: GTX 1050 Ti (4GB VRAM)
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import sys
import time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import torch

logger = logging.getLogger(__name__)

# ── Project imports (with fallbacks for standalone execution) ──────────────

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

try:
    from src.core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model
except ImportError:
    B3Config = None
    ImpressionCoreB3Model = None

try:
    from src.core.models.b3_foundation_architecture import B3FoundationConfig
except ImportError:
    B3FoundationConfig = None


# ── Quantization helpers ──────────────────────────────────────────────────

def _quantize_state_dict(
    state_dict: Dict[str, torch.Tensor],
    mode: str = "fp16",
) -> Dict[str, torch.Tensor]:
    """Apply weight quantization to a state_dict (in-place copy).

    Modes
    -----
    fp16   – Cast all float tensors to float16.
    int8   – Dynamic per-tensor symmetric INT8 quantisation.
    fp32   – No-op (keep full precision for debugging).
    """
    quantized: Dict[str, torch.Tensor] = {}
    for name, tensor in state_dict.items():
        if not tensor.is_floating_point():
            quantized[name] = tensor
            continue

        if mode == "fp16":
            quantized[name] = tensor.half()
        elif mode == "int8":
            scale = tensor.abs().max() / 127.0
            quantized[name] = (tensor / scale).round().to(torch.int8)
            quantized[f"{name}.__scale__"] = scale.float()
        else:  # fp32
            quantized[name] = tensor.float()

    return quantized


def _compute_param_stats(state_dict: Dict[str, torch.Tensor]) -> Dict[str, Any]:
    """Compute basic statistics for a state_dict."""
    total_params = 0
    total_bytes = 0
    for name, tensor in state_dict.items():
        if name.endswith(".__scale__"):
            continue
        total_params += tensor.numel()
        total_bytes += tensor.numel() * tensor.element_size()
    return {
        "total_parameters": total_params,
        "total_bytes": total_bytes,
        "total_mb": round(total_bytes / (1024 ** 2), 2),
    }


# ── Tokenizer export helper ──────────────────────────────────────────────

def _export_tokenizer(output_dir: Path) -> Dict[str, str]:
    """Export the hybrid DialoGPT→GPT-2 tokenizer pair.

    Tries to use HuggingFace transformers to download/save tokenizer files.
    Falls back to writing a reference manifest if transformers is unavailable.
    """
    tokenizer_dir = output_dir / "tokenizer"
    dialogpt_dir = tokenizer_dir / "dialogpt_input"
    gpt2_dir = tokenizer_dir / "gpt2_output"
    dialogpt_dir.mkdir(parents=True, exist_ok=True)
    gpt2_dir.mkdir(parents=True, exist_ok=True)

    tokenizer_info: Dict[str, str] = {}

    try:
        from transformers import AutoTokenizer

        # Input tokenizer: DialoGPT-small
        input_tok = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
        input_tok.save_pretrained(str(dialogpt_dir))
        tokenizer_info["input_tokenizer"] = "microsoft/DialoGPT-small"
        tokenizer_info["input_path"] = str(dialogpt_dir)
        logger.info("✅ DialoGPT-small tokenizer saved to %s", dialogpt_dir)

        # Output tokenizer: GPT-2
        output_tok = AutoTokenizer.from_pretrained("gpt2")
        output_tok.save_pretrained(str(gpt2_dir))
        tokenizer_info["output_tokenizer"] = "gpt2"
        tokenizer_info["output_path"] = str(gpt2_dir)
        logger.info("✅ GPT-2 tokenizer saved to %s", gpt2_dir)

    except ImportError:
        logger.warning(
            "⚠️ transformers not installed — writing tokenizer reference manifest only"
        )
        ref = {
            "input_tokenizer": "microsoft/DialoGPT-small",
            "output_tokenizer": "gpt2",
            "note": "Install `transformers` and re-run export to download tokenizer files.",
        }
        (tokenizer_dir / "tokenizer_reference.json").write_text(
            json.dumps(ref, indent=2)
        )
        tokenizer_info = ref

    return tokenizer_info


# ── Colossus head export ─────────────────────────────────────────────────

def _export_colossus_heads(
    output_dir: Path,
    colossus_checkpoint: Optional[str] = None,
) -> Optional[str]:
    """Copy or re-serialize Colossus integration weights.

    Returns the filename inside ``output_dir`` or ``None`` if no checkpoint
    was found.
    """
    dest = output_dir / "colossus_heads.pt"

    if colossus_checkpoint and Path(colossus_checkpoint).exists():
        src = Path(colossus_checkpoint)
        # If it's a directory, look for the latest .pt inside it
        if src.is_dir():
            pts = sorted(src.glob("*.pt"), key=lambda p: p.stat().st_mtime, reverse=True)
            if not pts:
                pts = sorted(src.glob("**/*.pt"), key=lambda p: p.stat().st_mtime, reverse=True)
            if pts:
                src = pts[0]
            else:
                logger.warning("⚠️ No .pt files found in Colossus checkpoint dir: %s", colossus_checkpoint)
                return None

        shutil.copy2(str(src), str(dest))
        logger.info("✅ Colossus heads copied from %s", src)
        return str(dest)

    # Try standard locations
    standard_paths = [
        Path("F:/models/management/training_sessions/colossus"),
        Path("F:/models/checkpoints/colossus"),
        _PROJECT_ROOT / "models" / "colossus",
    ]
    for sp in standard_paths:
        if sp.exists():
            pts = sorted(sp.glob("**/*.pt"), key=lambda p: p.stat().st_mtime, reverse=True)
            if pts:
                shutil.copy2(str(pts[0]), str(dest))
                logger.info("✅ Colossus heads auto-discovered from %s", pts[0])
                return str(dest)

    logger.info("ℹ️ No Colossus checkpoint found — skipping colossus_heads.pt")
    return None


# ── Manifest generator ───────────────────────────────────────────────────

def _write_manifest(
    output_dir: Path,
    config_dict: Dict[str, Any],
    metadata: Dict[str, Any],
    quantization_mode: str,
) -> None:
    """Write a human-readable MANIFEST.md inside the production artifact."""
    manifest_path = output_dir / "MANIFEST.md"
    lines = [
        "# ImpressionCore B3 — Production Artifact Manifest",
        "",
        f"**Exported:** {metadata.get('export_timestamp', 'unknown')}",
        f"**Model:** {config_dict.get('model_name', 'ImpressionCore-B3')}",
        f"**Version:** {metadata.get('version', '0.0.0')}",
        f"**Quantization:** {quantization_mode}",
        "",
        "## Contents",
        "",
        "| File | Description |",
        "|------|-------------|",
        "| `model.pt` | Quantized model weights (state_dict) |",
        "| `config.json` | B3Config serialized |",
        "| `tokenizer/dialogpt_input/` | DialoGPT-small input tokenizer |",
        "| `tokenizer/gpt2_output/` | GPT-2 output tokenizer |",
        "| `metadata.json` | Training provenance and export metadata |",
        "| `colossus_heads.pt` | Colossus integration weights (if present) |",
        "",
        "## Parameter Summary",
        "",
        f"- **Total parameters:** {metadata.get('total_parameters', 'N/A'):,}",
        f"- **Model size (on-disk):** {metadata.get('model_size_mb', 'N/A')} MB",
        f"- **Embed dim:** {config_dict.get('embed_dim', 'N/A')}",
        f"- **Num layers:** {config_dict.get('num_layers', 'N/A')}",
        f"- **Num heads:** {config_dict.get('num_heads', 'N/A')}",
        f"- **Num experts:** {config_dict.get('num_experts', 'N/A')}",
        "",
        "## Hardware Target",
        "",
        "- **Primary:** NVIDIA GTX 1050 Ti (4GB VRAM)",
        "- **Inference VRAM budget:** <3.5 GB",
        "",
        "## Tokenizer Strategy",
        "",
        "Hybrid: DialoGPT-small (input encoding) → B3 Model → GPT-2 (output generation)",
        "",
        "---",
        "",
        "*Generated by `src/core/export/export_production_model.py`*",
    ]
    manifest_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("✅ MANIFEST.md written to %s", manifest_path)


# ── Validation ───────────────────────────────────────────────────────────

def _validate_artifact(output_dir: Path) -> Dict[str, bool]:
    """Validate that the exported artifact is complete and loadable."""
    checks: Dict[str, bool] = {}

    # Required files
    checks["model.pt"] = (output_dir / "model.pt").exists()
    checks["config.json"] = (output_dir / "config.json").exists()
    checks["metadata.json"] = (output_dir / "metadata.json").exists()
    checks["MANIFEST.md"] = (output_dir / "MANIFEST.md").exists()
    checks["tokenizer_dir"] = (output_dir / "tokenizer").is_dir()

    # Try loading state_dict
    if checks["model.pt"]:
        try:
            sd = torch.load(str(output_dir / "model.pt"), map_location="cpu", weights_only=True)
            checks["model_loadable"] = isinstance(sd, dict) and len(sd) > 0
        except Exception as exc:
            logger.warning("⚠️ model.pt load check failed: %s", exc)
            checks["model_loadable"] = False
    else:
        checks["model_loadable"] = False

    # Try loading config
    if checks["config.json"]:
        try:
            with open(output_dir / "config.json") as f:
                cfg = json.load(f)
            checks["config_loadable"] = isinstance(cfg, dict) and "embed_dim" in cfg
        except Exception:
            checks["config_loadable"] = False
    else:
        checks["config_loadable"] = False

    return checks


# ═════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═════════════════════════════════════════════════════════════════════════

def export_production_model(
    checkpoint_path: str,
    output_dir: str,
    *,
    version: str = "1.0.0",
    quantization: str = "fp16",
    colossus_checkpoint: Optional[str] = None,
    config_overrides: Optional[Dict[str, Any]] = None,
    validate: bool = True,
) -> Dict[str, Any]:
    """Export a trained B3 checkpoint to the canonical production artifact format.

    Parameters
    ----------
    checkpoint_path : str
        Path to a ``.pt`` checkpoint file containing either a full
        ``state_dict`` or a training-state dict with a ``"model_state_dict"``
        key (as produced by ``torch.save({"model_state_dict": ..., ...})``).

    output_dir : str
        Destination directory for the production artifact.  Created if it
        does not exist.

    version : str
        Semantic version string to embed in metadata.

    quantization : str
        Weight quantization mode: ``"fp16"`` | ``"int8"`` | ``"fp32"``.

    colossus_checkpoint : str, optional
        Path to a Colossus integration checkpoint file or directory.  If
        ``None``, the exporter searches standard F-drive locations.

    config_overrides : dict, optional
        Key/value overrides to patch into the exported ``config.json``.

    validate : bool
        Run post-export integrity checks.

    Returns
    -------
    dict
        Export report with keys: ``success``, ``output_dir``, ``validation``,
        ``metadata``, ``errors``.
    """
    report: Dict[str, Any] = {
        "success": False,
        "output_dir": output_dir,
        "validation": {},
        "metadata": {},
        "errors": [],
    }

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    ckpt_path = Path(checkpoint_path)

    # ── 1. Load checkpoint ────────────────────────────────────────────
    logger.info("📦 Loading checkpoint from %s", ckpt_path)
    if not ckpt_path.exists():
        report["errors"].append(f"Checkpoint not found: {ckpt_path}")
        return report

    try:
        raw = torch.load(str(ckpt_path), map_location="cpu", weights_only=False)
    except Exception as exc:
        report["errors"].append(f"Failed to load checkpoint: {exc}")
        return report

    # Support both raw state_dict and training-state wrapper
    if isinstance(raw, dict) and "model_state_dict" in raw:
        state_dict = raw["model_state_dict"]
        training_state = {k: v for k, v in raw.items() if k != "model_state_dict"}
    elif isinstance(raw, dict):
        state_dict = raw
        training_state = {}
    else:
        report["errors"].append(
            f"Unexpected checkpoint format: expected dict, got {type(raw).__name__}"
        )
        return report

    logger.info("  ✅ Loaded %d tensors from checkpoint", len(state_dict))

    # ── 2. Build config ───────────────────────────────────────────────
    config_dict: Dict[str, Any] = {}

    # Try to reconstruct from checkpoint metadata
    if "config" in training_state:
        config_dict = training_state["config"]
        if hasattr(config_dict, "to_dict"):
            config_dict = config_dict.to_dict()
        elif not isinstance(config_dict, dict):
            config_dict = {}

    # Fallback: instantiate default B3Config and serialize
    if not config_dict and B3Config is not None:
        cfg = B3Config()
        config_dict = cfg.to_dict()

    if not config_dict:
        # Absolute fallback — minimal B3 config
        config_dict = {
            "embed_dim": 768,
            "num_heads": 12,
            "num_layers": 8,
            "vocab_size": 50257,
            "num_experts": 8,
            "expert_dim": 2048,
            "experts_per_token": 2,
            "max_seq_length": 4096,
            "model_name": "ImpressionCore-B3",
        }

    if config_overrides:
        config_dict.update(config_overrides)

    (out / "config.json").write_text(json.dumps(config_dict, indent=2, default=str))
    logger.info("  ✅ config.json written")

    # ── 3. Quantize and save weights ─────────────────────────────────
    logger.info("  ⚙️  Quantizing weights (%s)...", quantization)
    t0 = time.time()
    quantized_sd = _quantize_state_dict(state_dict, mode=quantization)
    quant_time = time.time() - t0
    logger.info("    Done in %.2fs", quant_time)

    model_path = out / "model.pt"
    torch.save(quantized_sd, str(model_path))
    model_size_mb = round(model_path.stat().st_size / (1024 ** 2), 2)
    logger.info("  ✅ model.pt written (%s MB)", model_size_mb)

    param_stats = _compute_param_stats(state_dict)

    # ── 4. Export tokenizer ──────────────────────────────────────────
    tokenizer_info = _export_tokenizer(out)

    # ── 5. Export Colossus heads ──────────────────────────────────────
    colossus_path = _export_colossus_heads(out, colossus_checkpoint)

    # ── 6. Write metadata ────────────────────────────────────────────
    metadata = {
        "version": version,
        "model_name": config_dict.get("model_name", "ImpressionCore-B3"),
        "export_timestamp": datetime.now().isoformat(),
        "source_checkpoint": str(ckpt_path),
        "quantization_mode": quantization,
        "quantization_time_s": round(quant_time, 3),
        "total_parameters": param_stats["total_parameters"],
        "model_size_mb": model_size_mb,
        "original_size_mb": param_stats["total_mb"],
        "tokenizer_strategy": "hybrid_dialogpt_gpt2",
        "tokenizer_info": tokenizer_info,
        "colossus_included": colossus_path is not None,
        "hardware_target": "GTX 1050 Ti (4GB VRAM)",
        "training_provenance": {
            "step": training_state.get("step"),
            "epoch": training_state.get("epoch"),
            "loss": training_state.get("loss"),
            "quality_score": training_state.get("quality_score"),
            "optimizer_type": training_state.get("optimizer_type"),
        },
        "export_tool": "src/core/export/export_production_model.py",
    }

    (out / "metadata.json").write_text(json.dumps(metadata, indent=2, default=str))
    logger.info("  ✅ metadata.json written")

    # ── 7. Write manifest ────────────────────────────────────────────
    _write_manifest(out, config_dict, metadata, quantization)

    # ── 8. Validate ──────────────────────────────────────────────────
    validation = {}
    if validate:
        validation = _validate_artifact(out)
        all_ok = all(validation.values())
        if all_ok:
            logger.info("✅ Artifact validation PASSED — all checks OK")
        else:
            failed = [k for k, v in validation.items() if not v]
            logger.warning("⚠️ Artifact validation FAILED checks: %s", failed)

    report["success"] = not report["errors"] and all(validation.values())
    report["validation"] = validation
    report["metadata"] = metadata

    logger.info(
        "🎉 Export complete: %s → %s (%s MB, %s params)",
        ckpt_path.name,
        out,
        model_size_mb,
        f"{param_stats['total_parameters']:,}",
    )
    return report


# ── CLI ──────────────────────────────────────────────────────────────────

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="ImpressionCore B3 — Production Model Exporter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m src.core.export.export_production_model \\\n"
            "      --checkpoint F:/models/checkpoints/kd_sft_phase2/step_5000.pt \\\n"
            "      --output F:/models/production/b3_v1.0.0 \\\n"
            "      --quantization fp16\n"
        ),
    )
    parser.add_argument(
        "--checkpoint", required=True,
        help="Path to .pt checkpoint"
    )
    parser.add_argument(
        "--output", required=True,
        help="Destination directory for production artifact"
    )
    parser.add_argument(
        "--version", default="1.0.0",
        help="Semantic version (default: 1.0.0)"
    )
    parser.add_argument(
        "--quantization", choices=["fp16", "int8", "fp32"], default="fp16",
        help="Weight quantization mode (default: fp16)"
    )
    parser.add_argument(
        "--colossus-checkpoint",
        help="Path to Colossus integration weights"
    )
    parser.add_argument(
        "--no-validate", action="store_true",
        help="Skip post-export validation"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s │ %(levelname)s │ %(message)s",
    )

    report = export_production_model(
        checkpoint_path=args.checkpoint,
        output_dir=args.output,
        version=args.version,
        quantization=args.quantization,
        colossus_checkpoint=args.colossus_checkpoint,
        validate=not args.no_validate,
    )

    if report["success"]:
        print(f"\n✅ Export succeeded → {report['output_dir']}")
        return 0
    else:
        print(f"\n❌ Export failed: {report['errors']}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
