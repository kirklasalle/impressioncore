#!/usr/bin/env python3
"""
Interactive tester for the trained Colossus Integrator.
Verifies that the model correctly identifies and integrates high-quality responses.
"""

import hashlib
import json
import logging
from pathlib import Path

import torch

from src.integrator.colossus_model import Colossus, ColossusConfig
from src.orchestrator.message_protocol import pack_message

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
logger = logging.getLogger("colossus_tester")

def load_latest_checkpoint() -> Path:
    pointer_file = Path("src/core/config/colossus_checkpoint.pointer")
    if pointer_file.exists():
        with open(pointer_file) as f:
            path_str = f.read().strip()
            return Path(path_str)
    return None

def text_to_vector(text: str, vector_dim: int) -> list[float]:
    """Simple deterministic text-to-vector for testing (must match training)."""
    vector = torch.zeros(vector_dim, dtype=torch.float32)
    content = text.lower().split()
    if not content:
        return vector.tolist()
    for token in content:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:4], "big") % vector_dim
        sign = 1.0 if digest[4] & 1 else -1.0
        vector[idx] += sign
    norm = torch.norm(vector)
    if norm > 0:
        vector = vector / norm
    return vector.tolist()

def confidence_from_text(text: str) -> float:
    """Simple heuristic confidence (must match training)."""
    if not text:
        return 0.1
    tokens = text.split()
    length_bonus = min(0.4, 0.012 * len(tokens))
    diversity = len(set(tokens)) / max(1, len(tokens))
    diversity_bonus = min(0.25, 0.3 * diversity)
    punctuation_bonus = 0.05 if any(ch in text for ch in ".?!") else 0.0
    confidence = 0.3 + length_bonus + diversity_bonus + punctuation_bonus
    return max(0.05, min(0.99, confidence))

def main():
    print("\n🤖 Colossus Integrator - Interactive Test")
    print("=========================================")

    # Load Model
    checkpoint_path = load_latest_checkpoint()
    if not checkpoint_path or not checkpoint_path.exists():
        print("❌ No checkpoint found. Please train the model first.")
        return

    print(f"📂 Loading checkpoint: {checkpoint_path.name}")
    config = ColossusConfig(
        vector_dim=256,
        checkpoint_path=checkpoint_path,
        device="cuda" if torch.cuda.is_available() else "cpu"
    )
    model = Colossus.load(config)
    print("✅ Model loaded successfully.")

    # Load some real data for simulation
    data_path = Path("src/training/distillation/kd_inputs/generated/colossus_100k_identity.json")
    qa_pairs = {}
    if data_path.exists():
        print("📚 Loading QA database for simulation...")
        with open(data_path, encoding="utf-8") as f:
            data = json.load(f)
            for ex in data.get("examples", [])[:1000]: # Load first 1000 for quick lookup
                qa_pairs[ex["prompt"].lower().strip()] = ex["teacher_responses"]["ground_truth_a"]
        print(f"✅ Loaded {len(qa_pairs)} QA pairs.")

    print("\n💬 Enter a prompt (or 'quit' to exit).")
    print("   If the prompt exists in the DB, we'll simulate a perfect expert response.")
    print("   Otherwise, we'll simulate a generic response.")

    while True:
        prompt = input("\nUser: ").strip()
        if prompt.lower() in ["quit", "exit"]:
            break

        if not prompt:
            continue

        # Simulate Expert Response
        response_text = qa_pairs.get(prompt.lower(), "This is a simulated generic response because I don't know the answer.")
        print(f"Expert (Simulated): {response_text}")

        # Prepare Inputs
        vector = text_to_vector(response_text, 256)
        conf = confidence_from_text(response_text)

        msg_a = pack_message("expert_a", "text", {"prompt": prompt, "response": response_text}, vector, conf)
        msg_b = pack_message("expert_b", "text", {"prompt": prompt, "response": response_text}, vector, conf)

        # Run Colossus Integration
        result = model.integrate(msg_a, msg_b)

        # Analyze Result
        out_conf = result.confidence
        out_vector = result.summary_vector

        # Calculate Vector Similarity (Cosine)
        v_in = torch.tensor(vector)
        v_out = torch.tensor(out_vector)
        similarity = torch.dot(v_in, v_out) / (torch.norm(v_in) * torch.norm(v_out))

        print("\n🧠 Colossus Integration Result:")
        print(f"   Confidence: {out_conf:.4f} (Input: {conf:.4f})")
        print(f"   Vector Similarity: {similarity:.4f}")

        if similarity > 0.95 and out_conf > 0.8:
            print("   ✅ PASS: Colossus correctly identified and preserved the high-quality response.")
        else:
            print("   ⚠️ WARNING: Integration degraded the signal.")

if __name__ == "__main__":
    main()
