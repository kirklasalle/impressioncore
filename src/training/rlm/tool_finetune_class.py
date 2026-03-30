import json

import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
from torch.utils.data import DataLoader, Dataset

from src.training.rlm.policy_network import PolicyConfig, RLMPolicyNetwork


class ToolActionDataset(Dataset):
    def __init__(self, data_path, embedder):
        with open(data_path) as f:
            self.data = json.load(f)
        self.embedder = embedder

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        query = item['instruction']
        target_action = 12 # DICT-LOOKUP

        # Embed query
        # Shape: [768] -> [1, 1, 768] (Simulating state sequence)
        emb = self.embedder.encode(query, convert_to_tensor=True)
        # Reshape to [seq_len=1, hidden_dim=384] -> Project to 768 later?
        # MiniLM is 384. Policy expects 768. We'll project or pad.
        # Let's assume we use a 768 model or pad.

        return emb, torch.tensor(target_action)

def train_tool_classifier():
    print("Initializing Tool Policy Training...")

    # Load Embedder
    # Using a small model for speed, will pad to 768
    embedder = SentenceTransformer('all-MiniLM-L6-v2')

    # Policy Network
    config = PolicyConfig(hidden_dim=768, num_actions=13, use_lora=True)
    policy = RLMPolicyNetwork(config)
    policy.train()

    # Adapter to map 384 -> 768
    adapter = nn.Linear(384, 768)

    # Dataset
    dataset = ToolActionDataset("data/datasets/rlm_dictionary_tool.json", embedder)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

    optimizer = torch.optim.Adam(list(policy.parameters()) + list(adapter.parameters()), lr=1e-3)
    criterion = nn.CrossEntropyLoss()

    print(f"Training on {len(dataset)} samples...")

    for epoch in range(3):
        total_acc = 0
        total_loss = 0

        for _batch_idx, (embs, labels) in enumerate(dataloader):
            # embs: [batch, 384]
            # Project to [batch, 1, 768] for Policy input
            states = adapter(embs).unsqueeze(1)

            # Forward
            logits, value = policy(states)
            # logits: [batch, num_actions]

            loss = criterion(logits, labels)

            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

            # Acc
            preds = logits.argmax(dim=1)
            acc = (preds == labels).float().mean()
            total_acc += acc.item()
            total_loss += loss.item()

        print(f"Epoch {epoch+1} | Loss: {total_loss/len(dataloader):.4f} | Acc: {total_acc/len(dataloader):.2%}")

    # Save
    torch.save({
        'policy_state': policy.state_dict(),
        'adapter_state': adapter.state_dict()
    }, "checkpoints/rlm/policy_tool_finetuned.pt")
    print("Saved policy checkpoint.")

if __name__ == "__main__":
    train_tool_classifier()
