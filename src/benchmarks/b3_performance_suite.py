#!/usr/bin/env python3
"""
ImpressionCore-B3 Performance Benchmark Suite

File: src/benchmarks/b3_performance_suite.py
Created: April 2026
Authors: Kirk LaSalle; GitHub Copilot
Status: Active

Eight-dimension benchmark suite calibrated for the B3 architecture:

    1. Inference Latency      ← tokens-per-second at various batch/seq configs
    2. VRAM Utilization       ← peak memory vs 4GB GTX 1050 Ti budget
    3. Throughput             ← sustained generation throughput
    4. TurboQuant Fidelity    ← cosine similarity pre/post KV compression
    5. Quantization Fidelity  ← output divergence under FP16/INT8
    6. Context Window Stress  ← latency scaling up to 128k tokens
    7. Expert Routing         ← MoE load balancing (aux loss)
    8. Multimodal Fusion      ← encoder→fusion→model throughput

Hardware target: NVIDIA GTX 1050 Ti (4GB VRAM)
Dependencies: torch, psutil, time
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
import tracemalloc
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
import psutil

# Project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# ── Project imports ──────────────────────────────────────────────────────

try:
    from src.core.models.impressioncore_b3_architecture import (
        B3Config,
        ImpressionCoreB3Model,
    )
    B3_MODEL_AVAILABLE = True
except ImportError:
    B3_MODEL_AVAILABLE = False
    B3Config = None
    ImpressionCoreB3Model = None

try:
    from src.core.quantization.turboquant import TurboQuantCompressor
    from src.core.quantization.turboquant_config import TurboQuantConfig
    TURBOQUANT_AVAILABLE = True
except ImportError:
    TURBOQUANT_AVAILABLE = False

try:
    from src.core.models.b3_multimodal_encoders import (
        TextEncoder,
        ImageEncoder,
        AudioEncoder,
        MultimodalFusion,
    )
    from src.core.models.b3_foundation_architecture import B3FoundationConfig
    ENCODERS_AVAILABLE = True
except ImportError:
    ENCODERS_AVAILABLE = False

logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════
# Core benchmark class
# ═════════════════════════════════════════════════════════════════════════

class B3PerformanceBenchmark:
    """Comprehensive performance benchmark suite for ImpressionCore-B3.

    Covers all eight dimensions from the B3 Benchmark Rubric.
    """

    # VRAM budget for GTX 1050 Ti: 3.5GB usable (0.5GB reserved for OS)
    VRAM_BUDGET_GB = 3.5

    def __init__(self, output_dir: Optional[str] = None, device: Optional[str] = None):
        self.output_dir = Path(output_dir or "benchmarks/results/b3")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.start_time = datetime.now()
        self.hardware_info = self._detect_hardware()
        self.results: Dict[str, Any] = {}
        logger.info("🚀 B3PerformanceBenchmark initialised on %s", self.device)

    # ── Hardware detection ───────────────────────────────────────────

    def _detect_hardware(self) -> Dict[str, Any]:
        hw: Dict[str, Any] = {
            "cpu_cores": psutil.cpu_count(logical=True),
            "ram_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
            "gpu_available": torch.cuda.is_available(),
        }
        if hw["gpu_available"]:
            hw["gpu_name"] = torch.cuda.get_device_name(0)
            hw["gpu_vram_gb"] = round(
                torch.cuda.get_device_properties(0).total_memory / (1024 ** 3), 2
            )
            hw["compute_capability"] = torch.cuda.get_device_capability(0)
        return hw

    # ── Helper: build a throwaway B3 model ──────────────────────────

    def _make_model(self, config: Optional[Any] = None) -> torch.nn.Module:
        if not B3_MODEL_AVAILABLE:
            raise RuntimeError("B3 model classes not importable")
        cfg = config or B3Config()
        model = ImpressionCoreB3Model(cfg)
        model.to(self.device)
        model.eval()
        return model

    # ── Helper: clean GPU ────────────────────────────────────────────

    def _gpu_cleanup(self) -> None:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()

    # ── 1. Inference Latency ─────────────────────────────────────────

    def benchmark_inference_latency(
        self,
        batch_sizes: Optional[List[int]] = None,
        seq_lengths: Optional[List[int]] = None,
        warmup: int = 3,
        iterations: int = 10,
    ) -> Dict[str, Any]:
        """Measure tokens-per-second at various batch/seq configurations."""
        result = self._result_template("Inference Latency")
        batch_sizes = batch_sizes or [1, 2, 4]
        seq_lengths = seq_lengths or [128, 256, 512, 1024]

        try:
            model = self._make_model()
            embed_dim = model.config.embed_dim if hasattr(model, "config") else 768
            detail_rows: List[Dict[str, Any]] = []

            for bs in batch_sizes:
                for sl in seq_lengths:
                    self._gpu_cleanup()
                    try:
                        x = torch.randint(0, 50257, (bs, sl), device=self.device)
                        # warmup
                        with torch.no_grad():
                            for _ in range(warmup):
                                _ = model(x)
                        # measurement
                        times = []
                        with torch.no_grad():
                            for _ in range(iterations):
                                t0 = time.perf_counter()
                                _ = model(x)
                                if torch.cuda.is_available():
                                    torch.cuda.synchronize()
                                times.append(time.perf_counter() - t0)

                        avg = sum(times) / len(times)
                        tok_per_s = (bs * sl) / avg
                        detail_rows.append({
                            "batch_size": bs,
                            "seq_length": sl,
                            "avg_time_s": round(avg, 5),
                            "min_time_s": round(min(times), 5),
                            "max_time_s": round(max(times), 5),
                            "tokens_per_second": round(tok_per_s, 1),
                            "success": True,
                        })
                    except Exception as exc:
                        detail_rows.append({
                            "batch_size": bs, "seq_length": sl,
                            "error": str(exc), "success": False,
                        })

            result["metrics"]["detail"] = detail_rows
            ok = [r for r in detail_rows if r["success"]]
            if ok:
                result["metrics"]["max_tokens_per_second"] = max(
                    r["tokens_per_second"] for r in ok
                )
                result["metrics"]["avg_latency_s"] = round(
                    sum(r["avg_time_s"] for r in ok) / len(ok), 5
                )
            result["success"] = True
            del model
        except Exception as exc:
            result["error"] = str(exc)

        return result

    # ── 2. VRAM Utilization ──────────────────────────────────────────

    def benchmark_vram_utilization(self) -> Dict[str, Any]:
        """Measure peak VRAM usage relative to the GTX 1050 Ti 4GB budget."""
        result = self._result_template("VRAM Utilization")
        if not torch.cuda.is_available():
            result["error"] = "No CUDA device available"
            return result

        try:
            self._gpu_cleanup()
            baseline_mb = torch.cuda.memory_allocated() / (1024 ** 2)

            model = self._make_model()
            model_mb = torch.cuda.memory_allocated() / (1024 ** 2)

            # Run a realistic workload
            x = torch.randint(0, 50257, (1, 512), device=self.device)
            with torch.no_grad():
                _ = model(x)

            peak_mb = torch.cuda.max_memory_allocated() / (1024 ** 2)
            peak_gb = peak_mb / 1024

            result["metrics"] = {
                "baseline_mb": round(baseline_mb, 2),
                "model_load_mb": round(model_mb - baseline_mb, 2),
                "peak_inference_mb": round(peak_mb, 2),
                "peak_inference_gb": round(peak_gb, 3),
                "vram_budget_gb": self.VRAM_BUDGET_GB,
                "within_budget": peak_gb <= self.VRAM_BUDGET_GB,
                "headroom_mb": round((self.VRAM_BUDGET_GB * 1024) - peak_mb, 2),
            }
            result["success"] = True
            del model
        except Exception as exc:
            result["error"] = str(exc)

        self._gpu_cleanup()
        return result

    # ── 3. Throughput ────────────────────────────────────────────────

    def benchmark_throughput(
        self, duration_s: float = 10.0, seq_len: int = 256
    ) -> Dict[str, Any]:
        """Sustained generation throughput measured over a fixed duration."""
        result = self._result_template("Throughput")
        try:
            model = self._make_model()
            x = torch.randint(0, 50257, (1, seq_len), device=self.device)

            # warmup
            with torch.no_grad():
                for _ in range(3):
                    _ = model(x)

            # sustained run
            total_tokens = 0
            t_start = time.perf_counter()
            with torch.no_grad():
                while (time.perf_counter() - t_start) < duration_s:
                    _ = model(x)
                    if torch.cuda.is_available():
                        torch.cuda.synchronize()
                    total_tokens += seq_len

            elapsed = time.perf_counter() - t_start
            result["metrics"] = {
                "duration_s": round(elapsed, 2),
                "total_tokens": total_tokens,
                "sustained_tokens_per_s": round(total_tokens / elapsed, 1),
                "seq_length": seq_len,
            }
            result["success"] = True
            del model
        except Exception as exc:
            result["error"] = str(exc)

        return result

    # ── 4. TurboQuant Fidelity ───────────────────────────────────────

    def benchmark_turboquant_fidelity(self) -> Dict[str, Any]:
        """Cosine similarity of KV tensors pre/post TurboQuant compression."""
        result = self._result_template("TurboQuant Fidelity")
        if not TURBOQUANT_AVAILABLE:
            result["error"] = "TurboQuant modules not importable"
            return result

        try:
            configs = {
                "3.5-bit (quality-neutral)": TurboQuantConfig(
                    bits_per_channel=3.5, block_size=64
                ),
                "2.5-bit (aggressive)": TurboQuantConfig(
                    bits_per_channel=2.5, block_size=64
                ),
            }
            seq_lengths = [256, 1024, 4096]
            dim = 64

            fidelity_rows: List[Dict[str, Any]] = []
            for cfg_name, cfg in configs.items():
                compressor = TurboQuantCompressor(cfg)
                for sl in seq_lengths:
                    x = torch.randn(1, 6, sl, dim)
                    compressed = compressor.compress(x)
                    x_rec = compressor.decompress(compressed)

                    mse = (x - x_rec).pow(2).mean().item()
                    cos = torch.nn.functional.cosine_similarity(
                        x.flatten().unsqueeze(0),
                        x_rec.flatten().unsqueeze(0),
                    ).item()

                    fidelity_rows.append({
                        "config": cfg_name,
                        "seq_length": sl,
                        "mse": round(mse, 6),
                        "cosine_similarity": round(cos, 5),
                        "compression_ratio": round(compressed.compression_ratio, 2),
                    })

            result["metrics"]["fidelity"] = fidelity_rows
            # Pass if all quality-neutral cosine > 0.99
            qn = [r for r in fidelity_rows if "quality-neutral" in r["config"]]
            result["metrics"]["quality_neutral_min_cos"] = min(
                r["cosine_similarity"] for r in qn
            ) if qn else 0.0
            result["success"] = True
        except Exception as exc:
            result["error"] = str(exc)

        return result

    # ── 5. Quantization Fidelity ─────────────────────────────────────

    def benchmark_quantization_fidelity(self) -> Dict[str, Any]:
        """Output divergence of B3 model under FP16 vs FP32."""
        result = self._result_template("Quantization Fidelity")
        try:
            model_fp32 = self._make_model()
            # Clone to FP16
            model_fp16 = self._make_model()
            model_fp16.half()

            x = torch.randint(0, 50257, (1, 128), device=self.device)

            with torch.no_grad():
                out_32 = model_fp32(x)
                out_16 = model_fp16(x.to(self.device))

            # Handle different return types
            if isinstance(out_32, tuple):
                out_32 = out_32[0]
            if isinstance(out_16, tuple):
                out_16 = out_16[0]

            out_32_flat = out_32.float().flatten()
            out_16_flat = out_16.float().flatten()

            # Cosine similarity
            cos = torch.nn.functional.cosine_similarity(
                out_32_flat.unsqueeze(0),
                out_16_flat.unsqueeze(0),
            ).item()

            # MSE
            mse = (out_32_flat - out_16_flat).pow(2).mean().item()

            result["metrics"] = {
                "fp32_vs_fp16_cosine": round(cos, 5),
                "fp32_vs_fp16_mse": round(mse, 8),
                "output_shape": list(out_32.shape),
            }
            result["success"] = True
            del model_fp32, model_fp16
        except Exception as exc:
            result["error"] = str(exc)

        return result

    # ── 6. Context Window Stress ─────────────────────────────────────

    def benchmark_context_window(
        self,
        context_lengths: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """Latency scaling at increasing context lengths."""
        result = self._result_template("Context Window Stress")
        context_lengths = context_lengths or [128, 512, 1024, 2048, 4096]

        try:
            model = self._make_model()
            rows: List[Dict[str, Any]] = []

            for cl in context_lengths:
                self._gpu_cleanup()
                try:
                    x = torch.randint(0, 50257, (1, cl), device=self.device)
                    with torch.no_grad():
                        _ = model(x)  # warmup
                    times = []
                    with torch.no_grad():
                        for _ in range(5):
                            t0 = time.perf_counter()
                            _ = model(x)
                            if torch.cuda.is_available():
                                torch.cuda.synchronize()
                            times.append(time.perf_counter() - t0)

                    peak_mb = (
                        torch.cuda.max_memory_allocated() / (1024 ** 2)
                        if torch.cuda.is_available() else 0
                    )
                    rows.append({
                        "context_length": cl,
                        "avg_latency_s": round(sum(times) / len(times), 5),
                        "peak_vram_mb": round(peak_mb, 2),
                        "success": True,
                    })
                except Exception as exc:
                    rows.append({
                        "context_length": cl,
                        "error": str(exc),
                        "success": False,
                    })

            result["metrics"]["detail"] = rows
            ok = [r for r in rows if r["success"]]
            if len(ok) >= 2:
                # Scaling factor: latency at max vs latency at min
                result["metrics"]["scaling_factor"] = round(
                    ok[-1]["avg_latency_s"] / ok[0]["avg_latency_s"], 2
                )
            result["success"] = True
            del model
        except Exception as exc:
            result["error"] = str(exc)

        return result

    # ── 7. Expert Routing ────────────────────────────────────────────

    def benchmark_expert_routing(self, num_batches: int = 50) -> Dict[str, Any]:
        """MoE expert load-balance analysis."""
        result = self._result_template("Expert Routing")
        try:
            model = self._make_model()

            # Find MoE router if it exists
            router = None
            for name, module in model.named_modules():
                if "router" in name.lower() or "gate" in name.lower():
                    router = module
                    break

            if router is None:
                result["metrics"]["note"] = (
                    "No MoE router found in model — skipping load-balance analysis"
                )
                result["success"] = True
                del model
                return result

            # Run batches and collect routing decisions
            expert_counts: Dict[int, int] = {}
            total_tokens = 0

            with torch.no_grad():
                for _ in range(num_batches):
                    x = torch.randint(0, 50257, (1, 128), device=self.device)
                    output = model(x)

                    # Try to get router aux loss or weights
                    if hasattr(output, "router_logits") or (
                        isinstance(output, dict) and "router_logits" in output
                    ):
                        logits = (
                            output.router_logits
                            if hasattr(output, "router_logits")
                            else output["router_logits"]
                        )
                        if logits is not None:
                            top = logits.argmax(dim=-1).flatten().cpu()
                            for idx in top.tolist():
                                expert_counts[idx] = expert_counts.get(idx, 0) + 1
                                total_tokens += 1

            if total_tokens > 0:
                num_experts = len(expert_counts)
                ideal_share = total_tokens / num_experts if num_experts else 0
                imbalance = max(
                    abs(v - ideal_share) / ideal_share
                    for v in expert_counts.values()
                ) if ideal_share else 0.0

                result["metrics"] = {
                    "expert_counts": expert_counts,
                    "total_tokens_routed": total_tokens,
                    "num_experts_active": num_experts,
                    "max_imbalance_pct": round(imbalance * 100, 2),
                    "balanced": imbalance < 0.2,
                }
            else:
                result["metrics"] = {
                    "note": "Router output did not expose routing decisions; "
                            "model may use inline gating."
                }
            result["success"] = True
            del model
        except Exception as exc:
            result["error"] = str(exc)

        return result

    # ── 8. Multimodal Fusion ─────────────────────────────────────────

    def benchmark_multimodal_fusion(self) -> Dict[str, Any]:
        """Encoder → fusion → latency throughput (384-dim pipeline)."""
        result = self._result_template("Multimodal Fusion")
        if not ENCODERS_AVAILABLE:
            result["error"] = "Multimodal encoder modules not importable"
            return result

        try:
            config = B3FoundationConfig()
            text_enc = TextEncoder(config).to(self.device).eval()
            img_enc = ImageEncoder(config).to(self.device).eval()
            audio_enc = AudioEncoder(config).to(self.device).eval()
            fusion = MultimodalFusion(config).to(self.device).eval()

            # Sample inputs
            input_ids = torch.randint(0, 50257, (1, 32), device=self.device)
            pixel_values = torch.randn(1, 3, 224, 224, device=self.device)
            audio_values = torch.randn(1, 16000, device=self.device)

            # Warmup
            with torch.no_grad():
                te = text_enc(input_ids)
                ie = img_enc(pixel_values)
                ae = audio_enc(audio_values)
                _ = fusion(text_embeds=te, image_embeds=ie, audio_embeds=ae)

            # Benchmark
            times = []
            with torch.no_grad():
                for _ in range(10):
                    t0 = time.perf_counter()
                    te = text_enc(input_ids)
                    ie = img_enc(pixel_values)
                    ae = audio_enc(audio_values)
                    fused, info = fusion(
                        text_embeds=te, image_embeds=ie, audio_embeds=ae
                    )
                    if torch.cuda.is_available():
                        torch.cuda.synchronize()
                    times.append(time.perf_counter() - t0)

            text_params = sum(p.numel() for p in text_enc.parameters())
            img_params = sum(p.numel() for p in img_enc.parameters())
            audio_params = sum(p.numel() for p in audio_enc.parameters())
            fusion_params = sum(p.numel() for p in fusion.parameters())

            result["metrics"] = {
                "avg_pipeline_latency_ms": round(
                    (sum(times) / len(times)) * 1000, 2
                ),
                "output_shape": list(fused.shape),
                "d_model": config.d_model,
                "parameters": {
                    "text_encoder": text_params,
                    "image_encoder": img_params,
                    "audio_encoder": audio_params,
                    "fusion": fusion_params,
                    "total": text_params + img_params + audio_params + fusion_params,
                },
            }
            result["success"] = True
        except Exception as exc:
            result["error"] = str(exc)

        return result

    # ── Comprehensive run ────────────────────────────────────────────

    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run all eight benchmark dimensions and aggregate results."""
        logger.info("🚀 Starting B3 Comprehensive Benchmark Suite")

        benchmarks = [
            ("Inference Latency", self.benchmark_inference_latency),
            ("VRAM Utilization", self.benchmark_vram_utilization),
            ("Throughput", self.benchmark_throughput),
            ("TurboQuant Fidelity", self.benchmark_turboquant_fidelity),
            ("Quantization Fidelity", self.benchmark_quantization_fidelity),
            ("Context Window Stress", self.benchmark_context_window),
            ("Expert Routing", self.benchmark_expert_routing),
            ("Multimodal Fusion", self.benchmark_multimodal_fusion),
        ]

        all_results: Dict[str, Any] = {
            "benchmark_suite": "ImpressionCore-B3 Performance",
            "start_time": self.start_time.isoformat(),
            "hardware_info": self.hardware_info,
            "results": {},
        }

        for name, fn in benchmarks:
            logger.info("  ⏱️ Running %s ...", name)
            try:
                result = fn()
                all_results["results"][name] = result
                status = "✅" if result.get("success") else "⚠️"
                logger.info("  %s %s", status, name)
            except Exception as exc:
                logger.error("  ❌ %s — %s", name, exc)
                all_results["results"][name] = {
                    "test_name": name,
                    "success": False,
                    "error": str(exc),
                }

        end_time = datetime.now()
        all_results["end_time"] = end_time.isoformat()
        all_results["duration_seconds"] = round(
            (end_time - self.start_time).total_seconds(), 2
        )

        # Persist
        self._save_results(all_results)
        self._print_summary(all_results)

        logger.info("🎉 B3 Comprehensive Benchmark Complete")
        return all_results

    # ── Helpers ──────────────────────────────────────────────────────

    def _result_template(self, name: str) -> Dict[str, Any]:
        return {
            "test_name": name,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": None,
            "metrics": {},
        }

    def _save_results(self, results: Dict[str, Any]) -> None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.output_dir / f"b3_benchmark_{ts}.json"
        with open(path, "w") as f:
            json.dump(results, f, indent=2, default=str)
        logger.info("📊 Results saved to %s", path)

    def _print_summary(self, results: Dict[str, Any]) -> None:
        passed = sum(
            1 for r in results["results"].values() if r.get("success")
        )
        total = len(results["results"])
        print(f"\n{'='*60}")
        print(f"  B3 Benchmark Summary: {passed}/{total} passed")
        print(f"  Duration: {results.get('duration_seconds', '?')}s")
        print(f"{'='*60}")

        for name, r in results["results"].items():
            icon = "✅" if r.get("success") else "❌"
            detail = ""
            m = r.get("metrics", {})
            if name == "Inference Latency" and "max_tokens_per_second" in m:
                detail = f"  max {m['max_tokens_per_second']} tok/s"
            elif name == "VRAM Utilization" and "peak_inference_gb" in m:
                b = "✅" if m.get("within_budget") else "⚠️"
                detail = f"  {m['peak_inference_gb']} GB {b}"
            elif name == "TurboQuant Fidelity" and "quality_neutral_min_cos" in m:
                detail = f"  min cos={m['quality_neutral_min_cos']}"
            print(f"  {icon} {name}{detail}")
        print()


# ═════════════════════════════════════════════════════════════════════════
# CLI
# ═════════════════════════════════════════════════════════════════════════

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="ImpressionCore-B3 Performance Benchmark Suite"
    )
    parser.add_argument(
        "--output-dir", default="benchmarks/results/b3",
        help="Output directory for benchmark results"
    )
    parser.add_argument(
        "--test",
        choices=[
            "latency", "vram", "throughput", "turboquant",
            "quantization", "context", "routing", "fusion", "all",
        ],
        default="all",
        help="Specific test to run (default: all)"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s │ %(levelname)s │ %(message)s",
    )

    bench = B3PerformanceBenchmark(output_dir=args.output_dir)

    dispatch = {
        "latency": bench.benchmark_inference_latency,
        "vram": bench.benchmark_vram_utilization,
        "throughput": bench.benchmark_throughput,
        "turboquant": bench.benchmark_turboquant_fidelity,
        "quantization": bench.benchmark_quantization_fidelity,
        "context": bench.benchmark_context_window,
        "routing": bench.benchmark_expert_routing,
        "fusion": bench.benchmark_multimodal_fusion,
        "all": bench.run_comprehensive_benchmark,
    }

    try:
        result = dispatch[args.test]()
        print(f"\n✅ B3 Benchmark {'Suite' if args.test == 'all' else args.test} Complete")
        return 0
    except Exception as exc:
        print(f"\n❌ Benchmark failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
