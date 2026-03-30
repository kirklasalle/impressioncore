"""Generate teacher outputs from local Ollama models (relocated).

Relocated from project root (ollama_generate.py) on August 24, 2025 as part
of structural hygiene initiative (distillation teacher generation grouping).

Writes a JSON file with schema compatible with convert_teacher_outputs.py
(_from_teacher_knowledge), e.g.::

    {
      "generation_timestamp": "...",
      "teacher_models": ["llama3.1:8b", ...],
      "examples": [
         {
           "prompt": "...",
           "teacher_responses": {"llama3.1:8b": "...", "mistral:7b": "..."}
         },
         ...
      ]
    }

Usage example:
    python -m src.training.distillation.teachers.ollama_generate \
        --models "llama3.2:3b,phi3.5:3.8b-mini-instruct-q4_K_M,qwen2:1.5b" \
        --prompts-source F:\\data/distillation/kd_inputs/kd_manifest.jsonl \
        --prompts-limit 100 \
        --out F:\\data/distillation/ollama_gen/ollama_teachers.json
"""
from __future__ import annotations

import argparse
import json
import subprocess  # CLI fallback
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

try:  # optional rich UI
    from rich.console import Console
    from rich.progress import (
        BarColumn,
        Progress,
        TaskProgressColumn,
        TextColumn,
        TimeElapsedColumn,
        TimeRemainingColumn,
    )
    _HAS_RICH = True
    _RICH_CONSOLE = Console()
except Exception:  # pragma: no cover - optional dependency
    _HAS_RICH = False
    _RICH_CONSOLE = None  # type: ignore


def _read_prompts_from_jsonl(path: Path, limit: int) -> list[str]:
    prompts: list[str] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except Exception:  # skip malformed
                continue
            p = obj.get("prompt")
            if isinstance(p, str) and p.strip():
                prompts.append(p)
                if 0 < limit <= len(prompts):
                    break
    return prompts


def _default_prompts() -> list[str]:
    return [
        "Explain the scientific method in simple terms.",
        "What is the difference between inductive and deductive reasoning?",
        "Design a small program that reverses a string in Python.",
        "Describe how photosynthesis works and why it is important.",
        "Given an image of a cat on a table, describe likely scene attributes.",
        "Transcribe the following short audio: 'Hello world, testing one two three'.",
        "Explain the concept of algorithmic complexity with an example.",
        "Summarize the key trade-offs between precision and recall.",
        "Create three follow-up questions for a user asking about healthy diets.",
        "Explain gradient checkpointing and why it helps on low VRAM GPUs."
    ]


def _ollama_generate_with_ctx(session: requests.Session, base_url: str, model: str, prompt: str, num_ctx: int,
                               num_predict: int = 512, temperature: float = 0.7, timeout: int = 60) -> str:
    """Attempt generation via HTTP; fallback to CLI (2 strategies) with given context size."""
    payload = {
        "model": model,
        "prompt": prompt,
        "options": {
            "num_ctx": int(num_ctx),
            "num_predict": int(num_predict),
            "temperature": float(temperature),
            "top_p": 0.9,
        },
        "stream": False,
    }
    try:  # HTTP attempt
        r = session.post(f"{base_url}/api/generate", json=payload, timeout=timeout)
        if r.status_code == 200:
            data = r.json()
            resp = (data.get("response") or "").strip()
            if resp:
                return resp
    except Exception:
        pass
    # CLI basic
    try:
        res = subprocess.run(["ollama", "run", model, prompt], capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=max(timeout, 90))
        if res.returncode == 0 and res.stdout:
            return res.stdout.strip()
    except Exception:
        pass
    # CLI shell secondary (handles special chars)
    try:
        shell_cmd = f'echo {json.dumps(prompt)} | ollama run {model}'
        res = subprocess.run(shell_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=max(timeout, 90), shell=True)
        if res.returncode == 0 and res.stdout:
            return res.stdout.strip()
    except Exception:
        pass
    return ""


def _ollama_generate(session: requests.Session, base_url: str, model: str, prompt: str, num_ctx: int = 128000,
                      num_predict: int = 512, temperature: float = 0.7, timeout: int = 60) -> str:
    for ctx in (num_ctx, 65536, 32768, 8192):  # progressive fallback
        resp = _ollama_generate_with_ctx(session, base_url, model, prompt, ctx, num_predict, temperature, timeout)
        if resp:
            return resp
    return ""


def _is_big_model(model_id: str) -> bool:
    m = model_id.lower()
    big_tokens = [
        ":7b", ":8b", ":9b", ":11b", ":12b", ":13b", ":20b", ":30b", ":34b", ":70b",
        "-7b", "-8b", "-9b", "-13b", "-70b", "70b", "13b",
        "gemma2:9b", "mistral:7b", "llava:7b", "janus-pro-7b",
    ]
    allow_tokens = ["mini", "q4", "q5", "q6", ":1.5b", ":2b", ":3b", ":0.5b", ":0.3b"]
    if any(tok in m for tok in allow_tokens):
        return False
    return any(tok in m for tok in big_tokens)


def main() -> None:  # pragma: no cover - CLI orchestration
    ap = argparse.ArgumentParser(description="Generate teacher outputs from local Ollama models")
    ap.add_argument("--models", type=str, required=False,
                    default="llama3.2:3b,phi3.5:3.8b-mini-instruct-q4_K_M,qwen2:1.5b",
                    help="Comma-separated list of Ollama model IDs")
    ap.add_argument("--prompts-source", type=str, required=False,
                    help="Path to JSONL with 'prompt' fields (optional)")
    ap.add_argument("--prompts-limit", type=int, default=100, help="Max prompts to use from source")
    ap.add_argument("--out", type=str, required=True, help="Output JSON path")
    ap.add_argument("--base-url", type=str, default="http://localhost:11434", help="Ollama base URL")
    ap.add_argument("--num-ctx", type=int, default=128000, help="Context window (num_ctx)")
    ap.add_argument("--num-predict", type=int, default=512, help="Max tokens to generate (num_predict)")
    ap.add_argument("--allow-big-models", action="store_true",
                    help="Disable small-model enforcement (use with caution on 4GB GPUs)")
    args = ap.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.prompts_source:
        src = Path(args.prompts_source)
        prompts = _read_prompts_from_jsonl(src, args.prompts_limit)
        if not prompts:
            prompts = _default_prompts()
    else:
        prompts = _default_prompts()

    models = [m.strip() for m in str(args.models).split(",") if m.strip()]
    if not args.allow_big_models:
        before = list(models)
        models = [m for m in models if not _is_big_model(m)]
        if not models and before:  # fallback
            models = ["llama3.2:3b", "phi3.5:3.8b-mini-instruct-q4_K_M", "qwen2:1.5b"]

    session = requests.Session()
    try:  # non-fatal reachability check
        session.get(f"{args.base_url}/api/tags", timeout=5)
    except Exception:
        print("[warn] Ollama HTTP not reachable; will attempt CLI fallback.")

    examples: list[dict] = []
    if _HAS_RICH:
        _RICH_CONSOLE.print(f"[bold cyan]Using models:[/bold cyan] {', '.join(models)}")
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=_RICH_CONSOLE,
            transient=False,
        ) as progress:
            task = progress.add_task("Generating prompts", total=len(prompts))
            for prompt in prompts:
                tr: dict[str, str] = {}
                for model in models:
                    resp = _ollama_generate(session, args.base_url, model, prompt, args.num_ctx, args.num_predict, 0.7)
                    if resp:
                        tr[model] = resp
                    time.sleep(0.05)
                if tr:
                    examples.append({
                        "prompt": prompt,
                        "teacher_responses": tr,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                progress.advance(task, 1)
    else:
        print(f"[info] Using models: {', '.join(models)}")
        for idx, prompt in enumerate(prompts):
            tr: dict[str, str] = {}
            for model in models:
                resp = _ollama_generate(session, args.base_url, model, prompt, args.num_ctx, args.num_predict, 0.7)
                if resp:
                    tr[model] = resp
                time.sleep(0.05)
            if tr:
                examples.append({
                    "prompt": prompt,
                    "teacher_responses": tr,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            if (idx + 1) % 5 == 0:
                print(f"[progress] Completed {idx + 1}/{len(prompts)} prompts...")

    payload = {
        "generation_timestamp": datetime.now(timezone.utc).isoformat(),
        "teacher_models": models,
        "total_examples": len(examples),
        "examples": examples,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] Wrote {len(examples)} examples -> {out_path}")


if __name__ == "__main__":  # pragma: no cover
    main()
