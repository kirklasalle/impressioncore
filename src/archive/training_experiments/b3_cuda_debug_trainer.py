"""
B3-Hope CUDA Debug Training - Diagnose Token Index Issues
Enable detailed CUDA error reporting to find the exact problem
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer
import logging
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import sys
import os

# Enable CUDA launch blocking for detailed error messages
os.environ['CUDA_LAUNCH_BLOCKING'] = '1'

# Setup logging
log_file = f"b3_cuda_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-small')
tokenizer.pad_token = tokenizer.eos_token

logger.info(f"Tokenizer vocabulary size: {tokenizer.vocab_size}")
logger.info(f"Tokenizer pad_token_id: {tokenizer.pad_token_id}")
logger.info(f"Tokenizer eos_token_id: {tokenizer.eos_token_id}")

class DebugConversationDataset:
    """Generate small test dataset with validation"""

    def __init__(self):
        self.conversations = []
        self._build_dataset()

    def _build_dataset(self):
        """Build small test dataset"""
        logger.info("Building debug test dataset...")

        # Small test set
        test_conversations = [
            ("Hello", "Hello! How can I help you today?"),
            ("Hi there", "Hi! What can I do for you?"),
            ("How are you?", "I'm doing well, thank you for asking!"),
            ("What is AI?", "AI stands for Artificial Intelligence."),
            ("Tell me about yourself", "I'm an AI assistant here to help you."),
        ]

        self.conversations = test_conversations
        logger.info(f"Built dataset with {len(self.conversations)} conversation pairs")

    def get_conversations(self):
        return self.conversations

class ValidatedConversationDataset(Dataset):
    """PyTorch Dataset with token validation"""

    def __init__(self, conversations, tokenizer, max_length=128):
        self.conversations = conversations
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.vocab_size = tokenizer.vocab_size

        logger.info(f"Dataset vocab_size validation: {self.vocab_size}")

    def __len__(self):
        return len(self.conversations)

    def __getitem__(self, idx):
        user_text, ai_text = self.conversations[idx]

        # Format: USER: {text} AI: {response}
        full_text = f"USER: {user_text} AI: {ai_text}"

        encoding = self.tokenizer(
            full_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        input_ids = encoding['input_ids'].squeeze()
        attention_mask = encoding['attention_mask'].squeeze()

        # CRITICAL VALIDATION: Check for out-of-bounds token indices
        max_token_id = input_ids.max().item()
        min_token_id = input_ids.min().item()

        if max_token_id >= self.vocab_size:
            logger.error(f"INVALID TOKEN ID DETECTED!")
            logger.error(f"  Conversation index: {idx}")
            logger.error(f"  User text: {user_text}")
            logger.error(f"  AI text: {ai_text}")
            logger.error(f"  Max token ID: {max_token_id}")
            logger.error(f"  Vocab size: {self.vocab_size}")
            logger.error(f"  Invalid token IDs: {input_ids[input_ids >= self.vocab_size]}")

            # Clamp to valid range
            logger.warning(f"  CLAMPING token IDs to valid range [0, {self.vocab_size-1}]")
            input_ids = torch.clamp(input_ids, 0, self.vocab_size - 1)

        # Validate no negative indices
        if min_token_id < 0:
            logger.error(f"NEGATIVE TOKEN ID DETECTED!")
            logger.error(f"  Conversation index: {idx}")
            logger.error(f"  Min token ID: {min_token_id}")

            # Clamp to valid range
            input_ids = torch.clamp(input_ids, 0, self.vocab_size - 1)

        # Labels are same as input_ids for language modeling
        labels = input_ids.clone()

        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': labels
        }

def load_model(device='cuda'):
    """Load B3-Hope model"""
    logger.info(f"Loading B3-Hope model to {device}...")

    sys.path.insert(0, str(Path(__file__).parent))
    from b3_constitutional_trainer import ImpressionCoreB3Hope, B3HopeConfig

    # Create config
    config = B3HopeConfig()

    # Create model
    model = ImpressionCoreB3Hope(config)

    checkpoint_path = Path('b3_hope_f_drive_production_checkpoint_step_1500.pth')
    if checkpoint_path.exists():
        logger.info(f"Loading checkpoint from {checkpoint_path}")
        checkpoint = torch.load(checkpoint_path, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])
        logger.info("Checkpoint loaded successfully")
    else:
        logger.warning("No checkpoint found, using fresh model")

    model = model.to(device)

    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logger.info(f"Total parameters: {total_params:,}")
    logger.info(f"Trainable parameters: {trainable_params:,}")

    # CRITICAL: Validate embedding layer size
    logger.info("\n" + "="*70)
    logger.info("MODEL ARCHITECTURE VALIDATION")
    logger.info("="*70)

    # Check text encoder embedding
    if hasattr(model, 'text_encoder'):
        if hasattr(model.text_encoder, 'transformer'):
            if hasattr(model.text_encoder.transformer, 'wte'):
                embedding_size = model.text_encoder.transformer.wte.num_embeddings
                logger.info(f"Text encoder embedding size: {embedding_size}")
                logger.info(f"Tokenizer vocab size: {tokenizer.vocab_size}")

                if embedding_size != tokenizer.vocab_size:
                    logger.error(f"MISMATCH DETECTED!")
                    logger.error(f"  Model embedding size: {embedding_size}")
                    logger.error(f"  Tokenizer vocab size: {tokenizer.vocab_size}")
                    logger.error(f"  This WILL cause CUDA errors!")
                else:
                    logger.info(f"✓ Embedding size matches tokenizer vocab size")

    logger.info("="*70 + "\n")

    return model

def validate_batch(batch, vocab_size):
    """Validate batch tensor contents"""
    input_ids = batch['input_ids']

    max_id = input_ids.max().item()
    min_id = input_ids.min().item()

    issues = []

    if max_id >= vocab_size:
        issues.append(f"Max token ID {max_id} >= vocab_size {vocab_size}")

    if min_id < 0:
        issues.append(f"Min token ID {min_id} < 0")

    return issues

def debug_train(num_epochs=3):
    """Debug training with detailed error reporting"""

    logger.info("="*70)
    logger.info("STARTING B3-HOPE CUDA DEBUG TRAINING")
    logger.info("CUDA_LAUNCH_BLOCKING=1 enabled for detailed errors")
    logger.info("="*70)

    # Check CUDA availability
    if not torch.cuda.is_available():
        logger.error("CUDA is not available! Falling back to CPU")
        device = 'cpu'
    else:
        device = 'cuda'
        logger.info(f"CUDA Device: {torch.cuda.get_device_name(0)}")
        logger.info(f"CUDA Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

    # Build debug dataset
    dataset_builder = DebugConversationDataset()
    conversations = dataset_builder.get_conversations()

    # Create validated dataset
    dataset = ValidatedConversationDataset(conversations, tokenizer)
    dataloader = DataLoader(dataset, batch_size=2, shuffle=True)  # Small batch for debugging

    logger.info(f"Training on {len(dataset)} conversation pairs")
    logger.info(f"Batch size: 2 (debug mode)")
    logger.info(f"Epochs: {num_epochs}")

    # Load model
    model = load_model(device)
    model.train()

    # Setup optimizer
    optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5)

    # Training loop with detailed validation
    global_step = 0

    for epoch in range(num_epochs):
        logger.info(f"\n{'='*70}")
        logger.info(f"EPOCH {epoch+1}/{num_epochs}")
        logger.info(f"{'='*70}")

        epoch_loss = 0
        steps_this_epoch = 0

        for batch_idx, batch in enumerate(dataloader):
            logger.info(f"\n--- Batch {batch_idx} ---")

            try:
                # Validate batch BEFORE moving to GPU
                validation_issues = validate_batch(batch, tokenizer.vocab_size)
                if validation_issues:
                    logger.error(f"Batch validation FAILED:")
                    for issue in validation_issues:
                        logger.error(f"  - {issue}")
                    logger.error("Skipping this batch")
                    continue
                else:
                    logger.info(f"✓ Batch validation passed")

                # Move to device
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)

                logger.info(f"  input_ids shape: {input_ids.shape}")
                logger.info(f"  input_ids range: [{input_ids.min().item()}, {input_ids.max().item()}]")
                logger.info(f"  vocab_size: {tokenizer.vocab_size}")

                # Forward pass
                logger.info(f"  Running forward pass...")
                output_dict = model(input_ids)
                logger.info(f"  ✓ Forward pass successful")
                logger.info(f"  output_dict keys: {output_dict.keys()}")

                # Extract logits from output dictionary
                outputs = output_dict['logits']
                logger.info(f"  outputs (logits) shape: {outputs.shape}")

                # Calculate loss
                logger.info(f"  Calculating loss...")
                loss_fct = nn.CrossEntropyLoss(ignore_index=tokenizer.pad_token_id)

                # Reshape for loss calculation
                shift_logits = outputs[:, :-1, :].contiguous()
                shift_labels = labels[:, 1:].contiguous()

                logger.info(f"  shift_logits shape: {shift_logits.shape}")
                logger.info(f"  shift_labels shape: {shift_labels.shape}")
                logger.info(f"  shift_labels range: [{shift_labels.min().item()}, {shift_labels.max().item()}]")

                loss = loss_fct(
                    shift_logits.view(-1, shift_logits.size(-1)),
                    shift_labels.view(-1)
                )

                logger.info(f"  ✓ Loss calculation successful")
                logger.info(f"  loss value: {loss.item():.4f}")

                # Backward pass
                logger.info(f"  Running backward pass...")
                optimizer.zero_grad()
                loss.backward()
                logger.info(f"  ✓ Backward pass successful")

                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

                optimizer.step()
                logger.info(f"  ✓ Optimizer step successful")

                # Track metrics
                epoch_loss += loss.item()
                steps_this_epoch += 1
                global_step += 1

                logger.info(f"✓ Batch {batch_idx} completed successfully!")

            except Exception as e:
                logger.error(f"\n{'!'*70}")
                logger.error(f"ERROR at epoch {epoch}, batch {batch_idx}")
                logger.error(f"{'!'*70}")
                logger.error(f"Error type: {type(e).__name__}")
                logger.error(f"Error message: {str(e)}")
                logger.error(f"{'!'*70}\n")

                # Print full traceback
                import traceback
                logger.error("Full traceback:")
                logger.error(traceback.format_exc())

                # Stop on first error for debugging
                logger.error("\nStopping training to analyze error")
                return None

        # Epoch summary
        avg_epoch_loss = epoch_loss / steps_this_epoch if steps_this_epoch > 0 else float('inf')

        logger.info(f"\nEpoch {epoch+1} Summary:")
        logger.info(f"  Steps completed: {steps_this_epoch}")
        logger.info(f"  Average Loss: {avg_epoch_loss:.4f}")

    logger.info("\n" + "="*70)
    logger.info("DEBUG TRAINING COMPLETE!")
    logger.info(f"Total successful steps: {global_step}")
    logger.info("="*70)

    return True

if __name__ == "__main__":
    logger.info(f"\nStarting debug session: {datetime.now()}")
    logger.info(f"PyTorch version: {torch.__version__}")
    logger.info(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        logger.info(f"CUDA version: {torch.version.cuda}")

    result = debug_train(num_epochs=3)

    if result:
        logger.info("\n✓ Debug training succeeded! Ready for full training.")
    else:
        logger.info("\n✗ Debug training failed. Check logs for details.")
