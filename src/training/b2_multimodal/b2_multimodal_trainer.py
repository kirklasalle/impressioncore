#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #memory_management #multimodal #python #source_code #src/training/b2_multimodal/b2_multimodal_trainer.py #testing #tokenization #training
**Category:** Training System
**Status:** Active
"""









# B2 Multimodal Trainer

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #memory_management #multimodal #python #source_code #src\\training\\b2_multimodal\\b2_multimodal_trainer.py #testing #tokenization #training
# Category:** Training System
# Status:** Active

"""
Scaffold for B2 multimodal training pipeline.
Implements modular training loop for conversation, vision, and audio heads.
"""
import sentencepiece as spm
import torch

from src.models.b2_multimodal.core.b2_multimodal_model import B2MultimodalModel
from src.models.b2_multimodal.core.memory_optimization import apply_memory_optimizations


def optimize_model_config_and_device(model_config):
    import torch.nn as nn
    dummy = nn.Identity()
    apply_memory_optimizations(dummy, model_config)
    return model_config




from torch.utils.data import DataLoader, random_split

from src.training.metrics import compute_metrics


def label_smoothing_loss(pred: torch.Tensor, target: torch.Tensor, smoothing: float = 0.1, ignore_index: int = 0) -> torch.Tensor:
    """
    Cross-entropy with label smoothing.
    Args:
        pred: [batch, seq, vocab_size] logits
        target: [batch, seq] target indices
        smoothing: label smoothing factor
        ignore_index: index to ignore in loss
    Returns:
        torch.Tensor: Scalar loss
    """
    confidence = 1.0 - smoothing
    logprobs = torch.nn.functional.log_softmax(pred, dim=-1)
    nll_loss = -logprobs.gather(dim=-1, index=target.unsqueeze(-1)).squeeze(-1)
    smooth_loss = -logprobs.mean(dim=-1)
    mask = (target != ignore_index)
    nll_loss = nll_loss[mask]
    smooth_loss = smooth_loss[mask]
    loss = confidence * nll_loss + smoothing * smooth_loss
    return loss.mean()

def perceptual_loss_stub(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """
    Placeholder for perceptual loss (e.g., VGG-based for images, audio features for audio).
    Args:
        pred: Model output
        target: Ground truth
    Returns:
        torch.Tensor: Scalar loss
    Note: Replace with real perceptual loss for production.
    """
    return torch.nn.functional.mse_loss(pred, target)

class B2MultimodalTrainer:
    """
    Trainer for B2 multimodal model with advanced loss and dataset support.
    Supports label smoothing, perceptual loss, real dataset loading, and validation split.
    """
    def __init__(self, config):
        self.model = B2MultimodalModel(config)
        self.config = config
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=config.get('lr', 1e-4))
        self.label_smoothing = config.get('label_smoothing', 0.0)
        self.use_perceptual_loss = config.get('use_perceptual_loss', False)
        self.train_loader: DataLoader | None = None
        self.val_loader: DataLoader | None = None
        # Initialize tokenizer
        self.sp = spm.SentencePieceProcessor()
        self.sp.load(config['sp_model_path'])

    def load_dataset(self, dataset, val_split: float = 0.1, batch_size: int = 2, seed: int = 42) -> tuple[DataLoader, DataLoader]:
        """
        Split dataset into train/validation and create DataLoaders.
        Args:
            dataset: torch.utils.data.Dataset
            val_split: Fraction for validation set
            batch_size: Batch size
            seed: Random seed for reproducibility
        Returns:
            Tuple[DataLoader, DataLoader]: (train_loader, val_loader)
        """
        n_total = len(dataset)
        n_val = int(n_total * val_split)
        n_train = n_total - n_val
        torch.manual_seed(seed)
        train_set, val_set = random_split(dataset, [n_train, n_val])
        self.train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)
        self.val_loader = DataLoader(val_set, batch_size=batch_size, shuffle=False)
        return self.train_loader, self.val_loader

    def train_step(self, batch, output_modality='conversation'):
        """
        Perform a single training step with advanced loss support.
        Args:
            batch: Input batch dict
            output_modality: Which output head to train
        Returns:
            float: Loss value
        """
        self.model.train()
        self.optimizer.zero_grad()
        output = self.model(batch, output_modality=output_modality)
        if output_modality == 'conversation':
            raw_text = None
            for m in batch['modalities']:
                if m['type'][0] == 'text':
                    # Assuming the list contains one text sample
                    raw_text = m['data']['text'][0]
                    break

            if raw_text is None:
                raise ValueError("Batch is missing text modality for conversation loss.")

            target_ids = self.sp.encode_as_ids(raw_text)

            # Pad or truncate to max_seq_len
            max_len = self.config.get('max_seq_len', 512)
            if len(target_ids) > max_len:
                target_ids = target_ids[:max_len]
            else:
                target_ids = target_ids + [0] * (max_len - len(target_ids)) # 0 is pad token

            target = torch.tensor(target_ids, dtype=torch.long, device=self.model.device)

            if target.dim() == 1:
                target = target.unsqueeze(0)
            # Label smoothing if enabled
            if self.label_smoothing > 0.0:
                loss = label_smoothing_loss(output, target, smoothing=self.label_smoothing, ignore_index=0)
            else:
                loss = torch.nn.functional.cross_entropy(
                    output.view(-1, output.size(-1)),
                    target.view(-1),
                    ignore_index=0
                )
        elif output_modality == 'vision' or output_modality == 'audio':
            # Placeholder: MSE or perceptual loss
            target = torch.randn_like(output)
            if self.use_perceptual_loss:
                loss = perceptual_loss_stub(output, target)
            else:
                loss = torch.nn.functional.mse_loss(output, target)
        else:
            raise ValueError(f"Unknown output_modality: {output_modality}")
        loss.backward()
        self.optimizer.step()
        return loss.item()



    def fit(self, dataloader=None, output_modality='conversation', epochs=1, validate: bool = True):
        """
        Main training loop with optional validation and metric reporting.
        Args:
            dataloader: DataLoader for training (if None, use self.train_loader)
            output_modality: Output head to train
            epochs: Number of epochs
            validate: Whether to run validation after each epoch
        """
        if dataloader is None:
            dataloader = self.train_loader
        for epoch in range(epochs):
            for batch in dataloader:
                loss = self.train_step(batch, output_modality=output_modality)
                print(f"Epoch {epoch} Loss: {loss}")
            if validate and self.val_loader is not None:
                val_loss, val_metrics = self.evaluate(self.val_loader, output_modality, report_metrics=True)
                print(f"Epoch {epoch} Validation Loss: {val_loss} | Metrics: {val_metrics}")

    def evaluate(self, dataloader, output_modality='conversation', report_metrics: bool = False) -> tuple[float, dict | None]:
        """
        Evaluate model on validation set, optionally reporting metrics.
        Args:
            dataloader: DataLoader for validation
            output_modality: Output head to evaluate
            report_metrics: Whether to compute metrics
        Returns:
            float: Average loss
            dict: Aggregated metrics (if requested)
        """
        self.model.eval()
        total_loss = 0.0
        n_batches = 0
        metrics_accum = {}
        with torch.no_grad():
            for batch in dataloader:
                output = self.model(batch, output_modality=output_modality)
                if output_modality == 'conversation':
                    raw_text = None
                    for m in batch['modalities']:
                        if m['type'][0] == 'text':
                            raw_text = m['data']['text'][0]
                            break

                    if raw_text is None:
                        # If no target, we can't calculate loss for this batch
                        loss = torch.tensor(0.0, device=output.device)
                    else:
                        target_ids = self.sp.encode_as_ids(raw_text)

                        # Pad or truncate to max_seq_len
                        max_len = self.config.get('max_seq_len', 512)
                        if len(target_ids) > max_len:
                            target_ids = target_ids[:max_len]
                        else:
                            target_ids = target_ids + [0] * (max_len - len(target_ids)) # 0 is pad token

                        target = torch.tensor(target_ids, dtype=torch.long, device=output.device)

                        if target.dim() == 1:
                            target = target.unsqueeze(0)
                        if self.label_smoothing > 0.0:
                            loss = label_smoothing_loss(output, target, smoothing=self.label_smoothing, ignore_index=0)
                        else:
                            loss = torch.nn.functional.cross_entropy(
                                output.view(-1, output.size(-1)),
                                target.view(-1),
                                ignore_index=0
                            )
                elif output_modality == 'vision' or output_modality == 'audio':
                    target = torch.randn_like(output)
                    if self.use_perceptual_loss:
                        loss = perceptual_loss_stub(output, target)
                    else:
                        loss = torch.nn.functional.mse_loss(output, target)
                else:
                    raise ValueError(f"Unknown output_modality: {output_modality}")
                total_loss += loss.item()
                n_batches += 1
                if report_metrics:
                    # For demo, use same target as above; in real use, use ground truth
                    metrics = compute_metrics(output_modality, output, target)
                    for k, v in metrics.items():
                        metrics_accum[k] = metrics_accum.get(k, 0.0) + v
        avg_loss = total_loss / max(n_batches, 1)
        if report_metrics and n_batches > 0:
            metrics_avg = {k: v / n_batches for k, v in metrics_accum.items()}
            return avg_loss, metrics_avg
        return avg_loss, None



# Example usage: integrating real dataset loader and metrics
if __name__ == '__main__':
    config = {
        'embed_dim': 768,
        'vocab_size': 50257,
        'n_experts': 4,
        'img_dim': 32,
        'audio_dim': 16000,
        'max_seq_len': 32,
        'lr': 1e-4,
        'label_smoothing': 0.1,
        'use_perceptual_loss': True,
        'sp_model_path': 'path/to/sentencepiece/model'  # Add path to your SentencePiece model
    }
    trainer = B2MultimodalTrainer(config)
    # Example: use DummyMultimodalDataset for quick test
    from src.training.b2_multimodal.multimodal_dataset import DummyMultimodalDataset
    dataset = DummyMultimodalDataset(num_samples=20, vocab_size=config['vocab_size'], img_dim=config['img_dim'], audio_dim=config['audio_dim'], seq_len=config['max_seq_len'])
    train_loader, val_loader = trainer.load_dataset(dataset, val_split=0.2, batch_size=2)
    trainer.fit(train_loader, output_modality='conversation', epochs=2, validate=True)

    # Example: integrate real dataset (uncomment and set paths)
    # real_dataset = RealMultimodalDataset(
    #     text_path='F:/datasets/text/',
    #     image_path='F:/datasets/images/',
    #     audio_path='F:/datasets/audio/',
    #     max_samples=100
    # )
    # train_loader, val_loader = trainer.load_dataset(real_dataset, val_split=0.2, batch_size=2)
    # trainer.fit(train_loader, output_modality='conversation', epochs=2, validate=True)
