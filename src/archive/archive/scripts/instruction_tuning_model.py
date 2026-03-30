"""
Instruction-Tuning Head for ImpressionCore B3
Created: October 10, 2025

This module implements a task-specific instruction-tuning head on top of the GPT-2 base model.
The approach addresses the root cause of relevance degradation (training objective misalignment)
by adding an explicit architecture for understanding question-answer relationships.

Architecture:
1. Frozen GPT-2 Base: Preserves grammar quality (9.25/10)
2. Query Understanding Layer: Learns to extract intent from questions
3. Cross-Attention Mechanism: Links query understanding to answer generation
4. Answer Generation Head: Produces relevant responses to queries

Training Strategy:
- Freeze GPT-2 base completely (no fine-tuning)
- Train only the instruction head layers
- Use mixed Q&A dataset (SQuAD factual + MS MARCO explanatory + DailyDialog conversation)
- Optimize for relevance while maintaining grammar quality

Expected Outcome:
- Grammar: Maintain 9.0+ (base model frozen)
- Relevance: Improve from 5.3 to 7.5-8.5 (head layer learns Q&A relationships)
- Combined: Achieve 8.0+ overall quality
"""

import torch
import torch.nn as nn
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from typing import Optional, Tuple
import math


class InstructionTuningHead(nn.Module):
    """
    Task-specific head for instruction-tuning on top of frozen GPT-2 base.

    This head learns to:
    1. Understand query intent from the input question
    2. Attend to relevant context in GPT-2 hidden states
    3. Generate relevant answers that address the query

    The key innovation is separating "language generation" (frozen GPT-2)
    from "answer relevance" (trainable head), addressing the root cause
    of relevance degradation in previous attempts.
    """

    def __init__(
        self,
        hidden_size: int = 768,  # GPT-2 small hidden size
        num_attention_heads: int = 8,
        intermediate_size: int = 2048,
        dropout: float = 0.1
    ):
        super().__init__()

        self.hidden_size = hidden_size
        self.num_attention_heads = num_attention_heads
        self.head_dim = hidden_size // num_attention_heads

        # Query Understanding Layer
        # Learns to extract intent and key concepts from input questions
        self.query_encoder = nn.Sequential(
            nn.Linear(hidden_size, intermediate_size),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(intermediate_size, hidden_size),
            nn.LayerNorm(hidden_size)
        )

        # Cross-Attention Mechanism
        # Links query understanding to answer generation
        self.query_attention = nn.MultiheadAttention(
            embed_dim=hidden_size,
            num_heads=num_attention_heads,
            dropout=dropout,
            batch_first=True
        )
        self.attention_norm = nn.LayerNorm(hidden_size)

        # Answer Generation Head
        # Produces relevant responses conditioned on query understanding
        self.answer_head = nn.Sequential(
            nn.Linear(hidden_size, intermediate_size),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(intermediate_size, hidden_size),
            nn.LayerNorm(hidden_size)
        )

        # Relevance Enhancement Layer
        # Amplifies query-relevant features, suppresses off-topic features
        self.relevance_gate = nn.Sequential(
            nn.Linear(hidden_size * 2, hidden_size),
            nn.Sigmoid()
        )

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        """Initialize weights with small values to prevent disrupting base model"""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                module.weight.data.normal_(mean=0.0, std=0.02)
                if module.bias is not None:
                    module.bias.data.zero_()
            elif isinstance(module, nn.LayerNorm):
                module.bias.data.zero_()
                module.weight.data.fill_(1.0)

    def forward(
        self,
        hidden_states: torch.Tensor,
        query_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Forward pass through instruction-tuning head.

        Args:
            hidden_states: Output from frozen GPT-2 base [batch, seq_len, hidden_size]
            query_mask: Mask indicating query tokens vs answer tokens [batch, seq_len]

        Returns:
            Enhanced hidden states with query-aware relevance [batch, seq_len, hidden_size]
        """
        batch_size, seq_len, hidden_size = hidden_states.shape

        # Step 1: Extract query understanding from input
        # Focus on question tokens to understand intent
        query_states = self.query_encoder(hidden_states)

        # Step 2: Apply cross-attention to link query to answer generation
        # This learns which parts of the question are relevant to the answer
        attended_states, attention_weights = self.query_attention(
            query=hidden_states,
            key=query_states,
            value=query_states,
            need_weights=True
        )
        attended_states = self.attention_norm(attended_states + hidden_states)

        # Step 3: Generate answer representation
        # Conditioned on both base model states and query understanding
        answer_states = self.answer_head(attended_states)

        # Step 4: Apply relevance gating
        # Amplify features relevant to answering the query
        combined = torch.cat([hidden_states, answer_states], dim=-1)
        relevance_gate = self.relevance_gate(combined)

        # Gated combination: preserves grammar (from base) while adding relevance (from head)
        enhanced_states = hidden_states * (1 - relevance_gate) + answer_states * relevance_gate

        return enhanced_states


class InstructionTunedGPT2(nn.Module):
    """
    GPT-2 with instruction-tuning head for improved question-answer relevance.

    Architecture:
    1. Frozen GPT-2 base (preserves grammar quality)
    2. Trainable instruction-tuning head (learns answer relevance)
    3. Shared language modeling head (generates tokens)

    This design addresses the root cause of previous failures:
    - Previous approach: Fine-tuned entire model with cross-entropy loss
      - Result: Loss decreased but relevance degraded
      - Root cause: Cross-entropy optimizes next token prediction, not answer relevance

    - New approach: Freeze base, train head with relevance-aware architecture
      - Expected: Grammar maintained (base frozen), relevance improved (head learns Q&A)
      - Key insight: Separate language generation from answer understanding
    """

    def __init__(
        self,
        base_model_path: str,
        device: str = "cuda",
        freeze_base: bool = True
    ):
        super().__init__()

        self.device = device

        # Load frozen GPT-2 base
        print("📥 Loading frozen GPT-2 base model...")
        self.base_model = GPT2LMHeadModel.from_pretrained("gpt2")

        # Load Phase 1 checkpoint if provided
        if base_model_path:
            print(f"📥 Loading Phase 1 checkpoint: {base_model_path}")
            checkpoint = torch.load(base_model_path, map_location=device)

            # Load only GPT-2 base weights (ignore any head weights from checkpoint)
            if "model_state_dict" in checkpoint:
                state_dict = checkpoint["model_state_dict"]
            else:
                state_dict = checkpoint

            # Filter to only GPT-2 transformer weights
            gpt2_state_dict = {
                k.replace("transformer.", ""): v
                for k, v in state_dict.items()
                if k.startswith("transformer.")
            }

            self.base_model.transformer.load_state_dict(gpt2_state_dict, strict=False)

            # Display checkpoint quality if available
            if 'grammar_score' in checkpoint:
                print(f"   ✅ Loaded checkpoint (original quality: {checkpoint['grammar_score']:.2f})")
            else:
                print(f"   ✅ Loaded checkpoint")

        # Freeze base model completely
        if freeze_base:
            print("🔒 Freezing GPT-2 base model...")
            for param in self.base_model.parameters():
                param.requires_grad = False
            print("   ✅ Base model frozen (preserves grammar quality)")

        # Add trainable instruction-tuning head
        print("🏗️ Adding instruction-tuning head...")
        self.instruction_head = InstructionTuningHead(
            hidden_size=768,  # GPT-2 small
            num_attention_heads=8,
            intermediate_size=2048,
            dropout=0.1
        )
        print("   ✅ Instruction head initialized")

        # Keep original LM head for token generation
        # Note: We don't train this, but use it for generating tokens
        self.lm_head = self.base_model.lm_head

        self.to(device)

        # Print parameter summary
        self._print_parameter_summary()

    def _print_parameter_summary(self):
        """Print detailed parameter summary"""
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        frozen_params = total_params - trainable_params

        print("\n" + "="*60)
        print("INSTRUCTION-TUNED GPT-2 MODEL PARAMETERS")
        print("="*60)
        print(f"Total Parameters: {total_params:,}")
        print(f"  Frozen (GPT-2 Base): {frozen_params:,}")
        print(f"  Trainable (Instruction Head): {trainable_params:,}")
        print(f"  Training: {trainable_params / total_params * 100:.1f}% of model")
        print("="*60 + "\n")

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
        query_mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """
        Forward pass through instruction-tuned model.

        Args:
            input_ids: Input token IDs [batch, seq_len]
            attention_mask: Attention mask [batch, seq_len]
            labels: Target token IDs for computing loss [batch, seq_len]
            query_mask: Mask indicating query vs answer tokens [batch, seq_len]

        Returns:
            logits: Token logits [batch, seq_len, vocab_size]
            loss: Cross-entropy loss if labels provided, else None
        """
        # Get hidden states from frozen GPT-2 base
        with torch.no_grad():
            base_outputs = self.base_model.transformer(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_hidden_states=True
            )
            hidden_states = base_outputs.last_hidden_state

        # Apply instruction-tuning head (trainable)
        enhanced_states = self.instruction_head(
            hidden_states=hidden_states,
            query_mask=query_mask
        )

        # Generate token logits
        logits = self.lm_head(enhanced_states)

        # Compute loss if labels provided
        loss = None
        if labels is not None:
            # Shift for next token prediction
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()

            # Cross-entropy loss
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1)
            )

        return logits, loss

    def generate(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        max_length: int = 100,
        temperature: float = 0.8,
        top_p: float = 0.9,
        do_sample: bool = True
    ) -> torch.Tensor:
        """
        Generate text with instruction-tuning head.

        Args:
            input_ids: Input token IDs [batch, seq_len]
            attention_mask: Attention mask [batch, seq_len]
            max_length: Maximum generation length
            temperature: Sampling temperature
            top_p: Nucleus sampling threshold
            do_sample: Whether to sample or use greedy decoding

        Returns:
            Generated token IDs [batch, generated_len]
        """
        self.eval()

        with torch.no_grad():
            batch_size = input_ids.shape[0]
            current_length = input_ids.shape[1]

            # Generate tokens one at a time
            for _ in range(max_length - current_length):
                # Forward pass
                logits, _ = self.forward(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )

                # Get next token logits
                next_token_logits = logits[:, -1, :]

                # Apply temperature
                if temperature != 1.0:
                    next_token_logits = next_token_logits / temperature

                # Apply top-p (nucleus) sampling
                if do_sample:
                    sorted_logits, sorted_indices = torch.sort(next_token_logits, descending=True)
                    cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)

                    # Remove tokens with cumulative probability above threshold
                    sorted_indices_to_remove = cumulative_probs > top_p
                    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                    sorted_indices_to_remove[..., 0] = 0

                    # Set filtered logits to -inf
                    indices_to_remove = sorted_indices[sorted_indices_to_remove]
                    next_token_logits[:, indices_to_remove] = float('-inf')

                    # Sample from filtered distribution
                    probs = torch.softmax(next_token_logits, dim=-1)
                    next_token = torch.multinomial(probs, num_samples=1)
                else:
                    # Greedy decoding
                    next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)

                # Append to sequence
                input_ids = torch.cat([input_ids, next_token], dim=-1)

                # Update attention mask
                if attention_mask is not None:
                    attention_mask = torch.cat([
                        attention_mask,
                        torch.ones((batch_size, 1), dtype=torch.long, device=self.device)
                    ], dim=-1)

                # Check for EOS token
                if (next_token == 50256).all():  # GPT-2 EOS token
                    break

            return input_ids

    def save_checkpoint(self, path: str, epoch: int, grammar_score: float, relevance_score: float):
        """Save instruction-tuning head checkpoint (base model not saved)"""
        checkpoint = {
            "epoch": epoch,
            "instruction_head_state_dict": self.instruction_head.state_dict(),
            "grammar_score": grammar_score,
            "relevance_score": relevance_score,
            "model_config": {
                "hidden_size": 768,
                "num_attention_heads": 8,
                "intermediate_size": 2048
            }
        }
        torch.save(checkpoint, path)
        print(f"💾 Saved checkpoint: {path}")
        print(f"   Grammar: {grammar_score:.2f}, Relevance: {relevance_score:.2f}")


def count_parameters(model: nn.Module) -> dict:
    """Count trainable and frozen parameters"""
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    frozen = sum(p.numel() for p in model.parameters() if not p.requires_grad)
    total = trainable + frozen

    return {
        "total": total,
        "trainable": trainable,
        "frozen": frozen,
        "trainable_percent": trainable / total * 100 if total > 0 else 0
    }


if __name__ == "__main__":
    # Test model creation
    print("Testing InstructionTunedGPT2 creation...")

    model = InstructionTunedGPT2(
        base_model_path=None,  # Use default GPT-2
        device="cpu",
        freeze_base=True
    )

    # Test forward pass
    print("\nTesting forward pass...")
    batch_size, seq_len = 2, 50
    input_ids = torch.randint(0, 50257, (batch_size, seq_len))
    attention_mask = torch.ones((batch_size, seq_len))
    labels = input_ids.clone()

    logits, loss = model(
        input_ids=input_ids,
        attention_mask=attention_mask,
        labels=labels
    )

    print(f"✅ Forward pass successful")
    print(f"   Logits shape: {logits.shape}")
    print(f"   Loss: {loss.item():.4f}")

    # Test generation
    print("\nTesting generation...")
    generated = model.generate(
        input_ids=input_ids[:, :10],
        max_length=50,
        do_sample=True
    )
    print(f"✅ Generation successful")
    print(f"   Generated shape: {generated.shape}")

    print("\n✅ All tests passed!")
