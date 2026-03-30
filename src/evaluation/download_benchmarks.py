"""
Benchmark Dataset Downloader for RLM Evaluation

Downloads:
- BABILong from HuggingFace (long-context reasoning benchmark)
- RULER synthetic data (needle-in-haystack extended)

Created: January 21, 2026
"""

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default paths
BENCHMARK_ROOT = Path("F:/data/datasets/text")


def download_babilong(output_dir: Path | None = None, configs: list[str] | None = None):
    """
    Download BABILong benchmark from HuggingFace.

    Available configs: 0k, 1k, 2k, 4k, 8k, 16k, 32k, 64k, 128k
    """
    try:
        from datasets import load_dataset
    except ImportError:
        logger.error("datasets library required. Install with: pip install datasets")
        return False

    output_dir = output_dir or BENCHMARK_ROOT / "babilong_benchmark"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Default to shorter contexts for GTX 1050 Ti
    # BABILong uses separate configs: length configs (0k,1k,etc) and task configs (qa1-qa10)
    # We need to load length configs and extract qa-style samples
    if configs is None:
        configs = ["0k", "1k", "2k", "4k"]  # Reasonable for 4GB VRAM

    logger.info(f"Downloading BABILong benchmark to {output_dir}")
    logger.info(f"Configs: {configs}")

    all_samples = []

    for config in configs:
        try:
            logger.info(f"  Loading config {config}...")
            # BABILong uses qa1-qa10 as splits, not 'test'
            for split in ["qa1", "qa2", "qa3", "qa4", "qa5"]:
                try:
                    dataset = load_dataset(
                        "RMT-team/babilong",
                        name=config,
                        split=split,
                        trust_remote_code=True
                    )

                    for i, sample in enumerate(dataset):
                        input_text = sample.get("input", sample.get("question", ""))
                        target_text = sample.get("target", sample.get("answer", ""))
                        context = sample.get("context", "")

                        all_samples.append({
                            "id": f"{config}_{split}_{i}",
                            "config": config,
                            "task": split,
                            "input": input_text,
                            "target": target_text,
                            "context": context[:8000],
                            "token_count": len(context.split())
                        })

                    logger.info(f"    {split}: {len(dataset)} samples")
                except Exception as e:
                    logger.debug(f"    {split} not available: {e}")

        except Exception as e:
            logger.warning(f"    Failed to load {config}: {e}")

    # Save to JSON
    output_file = output_dir / "babilong_test.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_samples, f, indent=2)

    logger.info(f"✅ BABILong saved: {len(all_samples)} samples to {output_file}")
    return True


def download_ruler(output_dir: Path | None = None, tasks: list[str] | None = None):
    """
    Download RULER benchmark synthetic data.

    RULER tasks:
    - niah_single: Single needle in haystack
    - niah_multi: Multiple needles
    - vt: Variable tracking
    - cwe: Common words extraction
    - fwe: Frequent words extraction
    - qa: Question answering (uses SQuAD/HotpotQA)
    """

    output_dir = output_dir or BENCHMARK_ROOT / "ruler_benchmark"
    output_dir.mkdir(parents=True, exist_ok=True)

    if tasks is None:
        tasks = ["niah_single", "niah_multi", "vt", "cwe"]

    logger.info(f"Downloading RULER benchmark to {output_dir}")

    # RULER doesn't have a direct download - we'll generate synthetic samples
    # based on the RULER paper methodology
    all_samples = []

    # Generate NIAH (Needle in a Haystack) samples
    logger.info("  Generating NIAH samples...")

    # Paul Graham essays as haystack (using a sample)
    haystack_text = """
    The way to get startup ideas is not to try to think of startup ideas.
    It's to look for problems, preferably problems you have yourself.
    The very best startup ideas tend to have three things in common:
    they're something the founders themselves want,
    that they themselves can build,
    and that few others realize are worth doing.
    """ * 100  # Repeat to create longer context

    needles = [
        ("The secret password is: RULER2024", "What is the secret password?", "RULER2024"),
        ("The magic number is 42", "What is the magic number?", "42"),
        ("The hidden city is Atlantis", "What is the hidden city?", "Atlantis"),
    ]

    for i, (needle, question, answer) in enumerate(needles):
        # Insert needle at different positions
        for pos in [0.1, 0.25, 0.5, 0.75, 0.9]:
            insert_pos = int(len(haystack_text) * pos)
            context = haystack_text[:insert_pos] + f"\n\n{needle}\n\n" + haystack_text[insert_pos:]

            all_samples.append({
                "id": f"niah_{i}_pos{int(pos*100)}",
                "task": "niah_single",
                "input": question,
                "target": answer,
                "context": context[:8000],  # Limit for GTX 1050 Ti
                "needle_position": pos,
                "token_count": len(context[:8000].split())
            })

    # Generate Variable Tracking samples
    logger.info("  Generating VT (Variable Tracking) samples...")

    for i in range(20):
        # Create a chain of variable assignments
        vars_chain = []
        current_val = f"VALUE_{i}"
        for j in range(5):
            var_name = f"VAR_{chr(65 + j)}"
            if j == 0:
                vars_chain.append(f"{var_name} = {current_val}")
            else:
                prev_var = f"VAR_{chr(64 + j)}"
                vars_chain.append(f"{var_name} = {prev_var}")

        # Pad with distractor text
        context = haystack_text[:2000] + "\n\n" + "\n".join(vars_chain) + "\n\n" + haystack_text[:2000]

        all_samples.append({
            "id": f"vt_{i}",
            "task": "vt",
            "input": "What is the value of VAR_E?",
            "target": current_val,
            "context": context,
            "chain_length": 5,
            "token_count": len(context.split())
        })

    # Generate Common Words Extraction samples
    logger.info("  Generating CWE (Common Words) samples...")

    word_lists = [
        ["apple", "banana", "cherry", "apple", "banana", "apple"],
        ["dog", "cat", "bird", "dog", "dog", "fish", "dog"],
        ["red", "blue", "red", "green", "red", "blue", "red"],
    ]

    for i, words in enumerate(word_lists):
        from collections import Counter
        most_common = Counter(words).most_common(1)[0][0]

        context = haystack_text[:1000]
        for w in words:
            context += f"\n\nThe item mentioned is: {w}\n\n" + haystack_text[:200]

        all_samples.append({
            "id": f"cwe_{i}",
            "task": "cwe",
            "input": "What item is mentioned most frequently?",
            "target": most_common,
            "context": context[:4000],
            "token_count": len(context[:4000].split())
        })

    # Save to JSON
    output_file = output_dir / "ruler_test.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_samples, f, indent=2)

    logger.info(f"✅ RULER saved: {len(all_samples)} samples to {output_file}")
    return True


def download_longbench(output_dir: Path | None = None, subset: str = "2wikimqa"):
    """
    Download LongBench subset from HuggingFace.

    Subsets: narrativeqa, qasper, multifieldqa_en, hotpotqa, 2wikimqa, etc.
    """
    try:
        from datasets import load_dataset
    except ImportError:
        logger.error("datasets library required. Install with: pip install datasets")
        return False

    output_dir = output_dir or BENCHMARK_ROOT / "longbench"
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Downloading LongBench/{subset} to {output_dir}")

    try:
        dataset = load_dataset(
            "THUDM/LongBench",
            name=subset,
            split="test",
            trust_remote_code=True
        )

        samples = []
        for i, sample in enumerate(dataset):
            samples.append({
                "id": f"{subset}_{i}",
                "task": subset,
                "input": sample.get("input", ""),
                "target": sample.get("answers", [sample.get("answer", "")])[0] if isinstance(sample.get("answers"), list) else sample.get("answer", ""),
                "context": sample.get("context", ""),
                "token_count": len(sample.get("context", "").split())
            })

        output_file = output_dir / f"longbench_{subset}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(samples, f, indent=2)

        logger.info(f"✅ LongBench saved: {len(samples)} samples to {output_file}")
        return True

    except Exception as e:
        logger.error(f"Failed to download LongBench/{subset}: {e}")
        return False


def main():
    """Download all benchmarks."""
    import argparse

    parser = argparse.ArgumentParser(description="Download RLM evaluation benchmarks")
    parser.add_argument("--babilong", action="store_true", help="Download BABILong")
    parser.add_argument("--ruler", action="store_true", help="Download RULER")
    parser.add_argument("--longbench", action="store_true", help="Download LongBench")
    parser.add_argument("--all", action="store_true", help="Download all benchmarks")
    parser.add_argument("--output", type=str, default=None, help="Output directory")

    args = parser.parse_args()

    if args.output:
        global BENCHMARK_ROOT
        BENCHMARK_ROOT = Path(args.output)

    if args.all or (not args.babilong and not args.ruler and not args.longbench):
        args.babilong = args.ruler = args.longbench = True

    results = {}

    if args.babilong:
        results["babilong"] = download_babilong()

    if args.ruler:
        results["ruler"] = download_ruler()

    if args.longbench:
        results["longbench"] = download_longbench()

    print("\n" + "=" * 60)
    print("DOWNLOAD SUMMARY")
    print("=" * 60)
    for name, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"  {name}: {status}")
    print("=" * 60)


if __name__ == "__main__":
    main()
