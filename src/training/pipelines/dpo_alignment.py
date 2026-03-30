import json
import os
from pathlib import Path

import bitsandbytes as bnb
import tiktoken
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

# Import B3 Architecture
from src.core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model

# Configuration
CONFIG = {
    "checkpoint_path": r"F:\models\checkpoints\kd_sft_phase2\step_5000.pt",
    "dataset_path": r"src\training\data\datasets\dpo_phase3_dataset_with_logprobs.jsonl",
    "output_dir": r"F:\models\checkpoints\dpo_phase3",
    "batch_size": 1,
    "gradient_accumulation_steps": 8, # Scaled for Phase 3 dataset (2164 samples)
    "learning_rate": 1e-6, # Lower LR for alignment
    "beta": 0.1, # DPO beta parameter
    "num_epochs": 3, # Run for 3 epochs to get reasonable step count
    "save_steps": 20,
    "device": "cuda" if torch.cuda.is_available() else "cpu"
}

class DPODataset(Dataset):
    def __init__(self, file_path, tokenizer):
        self.data = []
        self.tokenizer = tokenizer

        with open(file_path, encoding='utf-8') as f:
            for line in f:
                self.data.append(json.loads(line))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]

        # Format: Human: ... Assistant: ...
        prompt = item['prompt']
        chosen = item['chosen']
        rejected = item['rejected']

        chosen_text = f"Human: {prompt}\nAssistant: {chosen}"
        rejected_text = f"Human: {prompt}\nAssistant: {rejected}"

        chosen_ids = self.tokenizer.encode(chosen_text)
        rejected_ids = self.tokenizer.encode(rejected_text)

        return {
            "chosen_ids": torch.tensor(chosen_ids, dtype=torch.long),
            "rejected_ids": torch.tensor(rejected_ids, dtype=torch.long),
            "ref_logprob_chosen": item['ref_logprob_chosen'],
            "ref_logprob_rejected": item['ref_logprob_rejected'],
            "prompt_len": len(self.tokenizer.encode(f"Human: {prompt}\nAssistant:"))
        }

def collate_fn(batch):
    # Pad sequences to max length in batch
    max_len = max(max(len(x['chosen_ids']), len(x['rejected_ids'])) for x in batch)

    chosen_ids = []
    rejected_ids = []
    ref_logprobs_chosen = []
    ref_logprobs_rejected = []
    prompt_lens = []

    for x in batch:
        # Pad chosen
        c_ids = x['chosen_ids']
        pad_len = max_len - len(c_ids)
        c_ids = F.pad(c_ids, (0, pad_len), value=50256) # GPT-2 pad token
        chosen_ids.append(c_ids)

        # Pad rejected
        r_ids = x['rejected_ids']
        pad_len = max_len - len(r_ids)
        r_ids = F.pad(r_ids, (0, pad_len), value=50256)
        rejected_ids.append(r_ids)

        ref_logprobs_chosen.append(x['ref_logprob_chosen'])
        ref_logprobs_rejected.append(x['ref_logprob_rejected'])
        prompt_lens.append(x['prompt_len'])

    return {
        "chosen_ids": torch.stack(chosen_ids),
        "rejected_ids": torch.stack(rejected_ids),
        "ref_logprob_chosen": torch.tensor(ref_logprobs_chosen),
        "ref_logprob_rejected": torch.tensor(ref_logprobs_rejected),
        "prompt_lens": prompt_lens
    }

def get_batch_logprobs(model, input_ids, prompt_lens):
    """Compute log probabilities for the response part of the sequence."""
    outputs = model(input_ids=input_ids)
    logits = outputs["logits"][:, :-1, :]
    labels = input_ids[:, 1:]

    log_probs = F.log_softmax(logits, dim=-1)
    selected_log_probs = torch.gather(log_probs, -1, labels.unsqueeze(-1)).squeeze(-1)

    # Mask out prompt and padding
    mask = torch.zeros_like(selected_log_probs)
    for i, p_len in enumerate(prompt_lens):
        # p_len is length of prompt. We want to mask 0 to p_len-2 (since shifted)
        # Actually, p_len is index of first response token in original sequence.
        # In shifted sequence (index t corresponds to prediction of t+1),
        # we want to predict token at p_len. So we need logit at p_len-1.
        # So mask should be 1 from p_len-1 onwards.

        # Also mask padding (50256)
        # Simple way: mask where labels != 50256 AND index >= p_len-1
        seq_len = (labels[i] != 50256).sum()
        if p_len - 1 < selected_log_probs.size(1):
            mask[i, p_len-1:seq_len] = 1.0

    return (selected_log_probs * mask).sum(dim=-1)

def train():
    print("Initializing DPO Training Pipeline...")
    Path(CONFIG["output_dir"]).mkdir(parents=True, exist_ok=True)

    # Load Model
    print(f"Loading model from {CONFIG['checkpoint_path']}...")
    checkpoint = torch.load(CONFIG["checkpoint_path"], map_location="cpu")
    config = B3Config() # Default config
    model = ImpressionCoreB3Model(config)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(CONFIG["device"])
    model.train()

    # Optimizer
    optimizer = bnb.optim.AdamW8bit(model.parameters(), lr=CONFIG["learning_rate"])

    # Dataset
    tokenizer = tiktoken.get_encoding("gpt2")
    dataset = DPODataset(CONFIG["dataset_path"], tokenizer)
    dataloader = DataLoader(dataset, batch_size=CONFIG["batch_size"], shuffle=True, collate_fn=collate_fn)

    print(f"Starting training on {len(dataset)} pairs for {CONFIG['num_epochs']} epochs...")

    step = 0
    optimizer.zero_grad()

    # Calculate total steps
    total_steps = (len(dataloader) // CONFIG["gradient_accumulation_steps"]) * CONFIG["num_epochs"]
    progress_bar = tqdm(total=total_steps)

    for epoch in range(CONFIG["num_epochs"]):
        print(f"\nEpoch {epoch+1}/{CONFIG['num_epochs']}")
        for batch in dataloader:

            chosen_ids = batch["chosen_ids"].to(CONFIG["device"])
            rejected_ids = batch["rejected_ids"].to(CONFIG["device"])
            ref_logprob_chosen = batch["ref_logprob_chosen"].to(CONFIG["device"])
            ref_logprob_rejected = batch["ref_logprob_rejected"].to(CONFIG["device"])
            prompt_lens = batch["prompt_lens"]

            # Forward pass for Policy Model
            policy_logprob_chosen = get_batch_logprobs(model, chosen_ids, prompt_lens)
            policy_logprob_rejected = get_batch_logprobs(model, rejected_ids, prompt_lens)

            # DPO Loss
            # L = -log(sigmoid(beta * (log(pi_theta(yw)/pi_ref(yw)) - log(pi_theta(yl)/pi_ref(yl)))))
            #   = -log(sigmoid(beta * ((log_pi_theta_w - log_pi_ref_w) - (log_pi_theta_l - log_pi_ref_l))))

            logits = CONFIG["beta"] * (
                (policy_logprob_chosen - ref_logprob_chosen) -
                (policy_logprob_rejected - ref_logprob_rejected)
            )

            loss = -F.logsigmoid(logits).mean()

            # Backward
            loss = loss / CONFIG["gradient_accumulation_steps"]
            loss.backward()

            if (step + 1) % CONFIG["gradient_accumulation_steps"] == 0:
                optimizer.step()
                optimizer.zero_grad()
                progress_bar.update(1)
                progress_bar.set_description(f"Loss: {loss.item() * CONFIG['gradient_accumulation_steps']:.4f}")

                # Save Checkpoint
                current_global_step = (step + 1) // CONFIG["gradient_accumulation_steps"]
                if current_global_step % CONFIG["save_steps"] == 0:
                    save_path = os.path.join(CONFIG["output_dir"], f"dpo_step_{current_global_step}.pt")
                    torch.save({
                        'step': current_global_step,
                        'epoch': epoch,
                        'model_state_dict': model.state_dict(),
                        'optimizer_state_dict': optimizer.state_dict(),
                        'loss': loss.item()
                    }, save_path)
                    print(f"\nCheckpoint saved: {save_path}")

            step += 1

    print("Training complete.")
    final_save_path = os.path.join(CONFIG["output_dir"], "dpo_final.pt")
    torch.save({
        'step': step,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss.item()
    }, final_save_path)
    print(f"Final model saved: {final_save_path}")

if __name__ == "__main__":
    train()
