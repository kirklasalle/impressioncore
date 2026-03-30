import json
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset
from transformers import get_linear_schedule_with_warmup

from src.training.rlm.policy_network import RLMPolicyNetwork


class ToolDataset(Dataset):
    def __init__(self, data_path, tokenizer):
        with open(data_path) as f:
            self.data = json.load(f)
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        text = f"User: {item['instruction']}\nAction: {item['output']}"
        return text

def train_tool_use():
    print("Initializing Tool Use Fine-tuning...")

    # Load Policy Network (LoRA enabled)
    policy = RLMPolicyNetwork() # Defaults to B3-Base
    tokenizer = policy.tokenizer

    # Dataset
    dataset = ToolDataset("data/datasets/rlm_dictionary_tool.json", tokenizer)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

    optimizer = torch.optim.AdamW(policy.parameters(), lr=1e-4)
    steps = len(dataloader) * 3 # 3 Epochs
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=100, num_training_steps=steps)

    print(f"Training on {len(dataset)} samples for {steps} steps...")

    policy.train()
    for epoch in range(3):
        total_loss = 0
        for batch_idx, text_batch in enumerate(dataloader):
            # Tokenize
            inputs = tokenizer(text_batch, return_tensors="pt", padding=True, truncation=True, max_length=128).to(policy.device)

            # Forward pass (Causal LM)
            outputs = policy.model(**inputs, labels=inputs.input_ids)
            loss = outputs.loss

            # Backward
            loss.backward()
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()

            total_loss += loss.item()

            if batch_idx % 50 == 0:
                print(f"Epoch {epoch+1} | Step {batch_idx} | Loss: {loss.item():.4f}")

        print(f"Epoch {epoch+1} Average Loss: {total_loss / len(dataloader):.4f}")

    # Save
    save_path = "checkpoints/rlm/step_tool_finetuned.pt"
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    policy.save_checkpoint(save_path)
    print(f"Saved tool-finetuned model to {save_path}")

if __name__ == "__main__":
    train_tool_use()
