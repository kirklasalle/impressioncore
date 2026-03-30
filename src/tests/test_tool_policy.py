import pytest

pytest.importorskip("transformers.training_args", reason="transformers package shadowed or incomplete")

import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer

from src.training.rlm.policy_network import PolicyConfig, RLMPolicyNetwork


def test_policy():
    print("Loading Tool Policy...")

    # Init Models
    embedder = SentenceTransformer('all-MiniLM-L6-v2')

    config = PolicyConfig(hidden_dim=768, num_actions=13, use_lora=True)
    policy = RLMPolicyNetwork(config)
    adapter = nn.Linear(384, 768)

    # Load Checkpoint
    checkpoint = torch.load("checkpoints/rlm/policy_tool_finetuned.pt")
    policy.load_state_dict(checkpoint['policy_state'])
    adapter.load_state_dict(checkpoint['adapter_state'])

    policy.eval()

    # Test Queries
    queries = [
        "What is the definition of abacus?",
        "Define computer.",
        "Meaning of algorithm",
        "Should I eat lunch?" # Control - should ideally NOT be DICT (but we only trained on DICT positive samples so it might hallucinate DICT here since we didn't provide negative samples. This is a known limitation of this rapid prototype phase)
    ]

    print("\nInference Test:")
    print("-" * 50)

    for q in queries:
        with torch.no_grad():
            emb = embedder.encode(q, convert_to_tensor=True).cpu()
            state = adapter(emb).unsqueeze(0).unsqueeze(1) # [1, 1, 768]

            logits, _ = policy(state)
            action = logits.argmax(dim=1).item()

            nexus_cmd = policy.action_to_nexus(action, q)
            print(f"Query: '{q}'")
            print(f"Action: {action} ({nexus_cmd})")
            print("-" * 20)

if __name__ == "__main__":
    test_policy()
