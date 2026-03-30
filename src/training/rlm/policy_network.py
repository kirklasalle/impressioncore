# RLM Policy Network with PEFT/LoRA
# src/training/rlm/policy_network.py

"""
RL Policy Network for NEXUS command generation.

Learns optimal action selection for context folding operations,
using PEFT/LoRA for VRAM-efficient training on GTX 1050 Ti.

Prime Directive Compliance: ✅ Verified
"""

import logging
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger("NEXUS.RLM.PolicyNetwork")


@dataclass
class PolicyConfig:
    """Configuration for RLM Policy Network."""
    hidden_dim: int = 768
    num_actions: int = 13
    num_heads: int = 8
    num_layers: int = 2
    dropout: float = 0.1
    # PEFT/LoRA settings
    use_lora: bool = True
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05


class LoRALinear(nn.Module):
    """Low-Rank Adaptation layer for VRAM-efficient fine-tuning."""

    def __init__(
        self,
        in_features: int,
        out_features: int,
        r: int = 16,
        alpha: int = 32,
        dropout: float = 0.05
    ):
        super().__init__()
        self.r = r
        self.alpha = alpha
        self.scaling = alpha / r

        # Original frozen weights (not trained)
        self.weight = nn.Parameter(torch.zeros(out_features, in_features), requires_grad=False)
        self.bias = nn.Parameter(torch.zeros(out_features), requires_grad=False)

        # LoRA trainable adapters
        self.lora_A = nn.Parameter(torch.randn(r, in_features) * 0.01)
        self.lora_B = nn.Parameter(torch.zeros(out_features, r))
        self.lora_dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Original forward
        result = F.linear(x, self.weight, self.bias)
        # LoRA adaptation
        lora_out = self.lora_dropout(x) @ self.lora_A.T @ self.lora_B.T
        return result + lora_out * self.scaling


class RLMPolicyNetwork(nn.Module):
    """
    RL Policy Network for NEXUS command selection.

    Learns to generate optimal NEXUS commands for context folding
    based on current state embeddings and query context.

    Architecture:
        - State Encoder: Transformer layers for context understanding
        - Action Head: Discrete action distribution over 12 NEXUS commands
        - Value Head: State value estimation for PPO advantage calculation

    PEFT/LoRA Integration:
        - Uses LoRA adapters for VRAM-efficient training
        - Compatible with GTX 1050 Ti (4GB VRAM)
    """

    # Action space mapping
    ACTIONS = {
        0: "CONTEXT-CHUNK",
        1: "CONTEXT-SEARCH",
        2: "LLM-QUERY LEFT",
        3: "LLM-QUERY RIGHT",
        4: "LLM-QUERY COLOSSUS",
        5: "PIPELINE",
        6: "PARALLEL",
        7: "CONTEXT-LOAD",
        8: "RECURSION-DEPTH",
        9: "SUMMARIZE",
        10: "ANSWER",
        11: "CONTINUE",
        12: "DICT-LOOKUP",
    }

    def __init__(self, config: PolicyConfig | None = None):
        super().__init__()
        self.config = config or PolicyConfig()

        # State encoder with LoRA if enabled
        self.state_projection = self._create_projection(
            self.config.hidden_dim,
            self.config.hidden_dim
        )

        # Transformer encoder for state processing
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=self.config.hidden_dim,
            nhead=self.config.num_heads,
            dim_feedforward=self.config.hidden_dim * 4,
            dropout=self.config.dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(
            encoder_layer,
            num_layers=self.config.num_layers
        )

        # Action head (policy)
        self.action_head = self._create_projection(
            self.config.hidden_dim,
            self.config.num_actions
        )

        # Value head (critic)
        self.value_head = self._create_projection(
            self.config.hidden_dim,
            1
        )

        logger.info(f"RLMPolicyNetwork initialized: {self._count_parameters()} parameters")
        if self.config.use_lora:
            logger.info(f"LoRA enabled: r={self.config.lora_r}, alpha={self.config.lora_alpha}")

    def _create_projection(self, in_dim: int, out_dim: int) -> nn.Module:
        """Create projection layer with optional LoRA."""
        if self.config.use_lora:
            return LoRALinear(
                in_dim, out_dim,
                r=self.config.lora_r,
                alpha=self.config.lora_alpha,
                dropout=self.config.lora_dropout
            )
        else:
            return nn.Linear(in_dim, out_dim)

    def _count_parameters(self) -> int:
        """Count trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

    def forward(
        self,
        state: torch.Tensor,
        action_mask: torch.Tensor | None = None
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass through policy network.

        Args:
            state: Context state embedding [batch, seq_len, hidden_dim]
            action_mask: Optional mask for invalid actions [batch, num_actions]

        Returns:
            action_logits: Log probabilities over actions [batch, num_actions]
            value: State value estimate [batch, 1]
        """
        # Project state
        x = self.state_projection(state)

        # Transformer encoding
        x = self.transformer(x)

        # Global average pooling
        x = x.mean(dim=1)  # [batch, hidden_dim]

        # Action logits
        action_logits = self.action_head(x)

        # Apply action mask if provided
        if action_mask is not None:
            action_logits = action_logits.masked_fill(~action_mask, float('-inf'))

        # Value estimate
        value = self.value_head(x)

        return action_logits, value

    def get_action(
        self,
        state: torch.Tensor,
        action_mask: torch.Tensor | None = None,
        deterministic: bool = False
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Sample action from policy.

        Args:
            state: Context state embedding
            action_mask: Optional mask for invalid actions
            deterministic: If True, select argmax action

        Returns:
            action: Selected action index
            log_prob: Log probability of selected action
            value: State value estimate
        """
        action_logits, value = self.forward(state, action_mask)
        probs = F.softmax(action_logits, dim=-1)

        action = probs.argmax(dim=-1) if deterministic else torch.multinomial(probs, 1).squeeze(-1)

        log_prob = F.log_softmax(action_logits, dim=-1)
        selected_log_prob = log_prob.gather(-1, action.unsqueeze(-1)).squeeze(-1)

        return action, selected_log_prob, value.squeeze(-1)

    def action_to_nexus(self, action: int, query: str) -> str:
        """
        Convert action index to NEXUS command string.

        Args:
            action: Action index (0-11)
            query: Current query for parameterizing commands

        Returns:
            NEXUS command string
        """
        action_name = self.ACTIONS.get(action, "CONTINUE")

        # Generate command based on action type
        if action_name == "CONTEXT-CHUNK":
            return "(CONTEXT-CHUNK 8000 \"paragraphs\")"
        elif action_name == "CONTEXT-SEARCH":
            # Extract key terms from query
            return f"(CONTEXT-SEARCH \"{query[:50]}\")"
        elif action_name == "LLM-QUERY LEFT":
            return f"(LLM-QUERY \"left\" \"{query}\")"
        elif action_name == "LLM-QUERY RIGHT":
            return f"(LLM-QUERY \"right\" \"{query}\")"
        elif action_name == "LLM-QUERY COLOSSUS":
            return f"(LLM-QUERY \"colossus\" \"{query}\")"
        elif action_name == "PIPELINE":
            return "(PIPELINE (CONTEXT-CHUNK) (CONTEXT-SEARCH \"relevant\"))"
        elif action_name == "PARALLEL":
            return "(PARALLEL (LLM-QUERY \"left\" \"analyze\") (LLM-QUERY \"right\" \"create\"))"
        elif action_name == "ANSWER":
            return "(LOG \"Answer ready\")"
        elif action_name == "DICT-LOOKUP":
            # Extract potential terms from query
            terms = [w for w in query.replace("?", "").replace(".", "").split() if len(w) > 3]
            term = terms[-1] if terms else "index"
            return f"(DICT-LOOKUP \"{term}\")"
        elif action_name == "TOOL-CALC":
            # Heuristic: Extract math expression
            # In a real model, this would be a generated argument.
            # Here we just grab the query if it looks like math, or a placeholder.
            return f"(TOOL-CALC \"{query}\")"
        elif action_name == "TOOL-SEARCH":
            # Pass full query to search
            return f"(TOOL-SEARCH \"{query}\")"
        else:
            return f"(LOG \"Action: {action_name}\")"

    def save(self, path: str):
        """Save model checkpoint."""
        torch.save({
            'config': self.config,
            'state_dict': self.state_dict(),
        }, path)
        logger.info(f"Model saved to {path}")

    @classmethod
    def load(cls, path: str, device: str = "cuda") -> "RLMPolicyNetwork":
        """Load model from checkpoint.

        Handles both:
        - Direct model saves (with 'config' and 'state_dict')
        - Trainer checkpoints (with 'policy_state')
        """
        checkpoint = torch.load(path, map_location=device)

        # Determine checkpoint format
        if 'config' in checkpoint:
            # Direct model save format
            config = checkpoint['config']
            state_dict = checkpoint['state_dict']
        elif 'policy_state' in checkpoint:
            # Trainer checkpoint format - use default config
            config = PolicyConfig()
            state_dict = checkpoint['policy_state']
            logger.info("Loading from trainer checkpoint (using default config)")
        else:
            # Unknown format - try loading as raw state dict
            config = PolicyConfig()
            state_dict = checkpoint
            logger.warning("Unknown checkpoint format, loading as raw state dict")

        model = cls(config=config)
        model.load_state_dict(state_dict)
        model.to(device)
        logger.info(f"Model loaded from {path}")
        return model


if __name__ == "__main__":
    # Test policy network
    config = PolicyConfig(use_lora=True)
    policy = RLMPolicyNetwork(config)

    # Dummy input
    state = torch.randn(2, 10, 768)  # [batch, seq_len, hidden_dim]

    # Forward pass
    logits, value = policy(state)
    print(f"Action logits shape: {logits.shape}")
    print(f"Value shape: {value.shape}")

    # Get action
    action, log_prob, val = policy.get_action(state)
    print(f"Action: {action}, Log prob: {log_prob}, Value: {val}")

    # Convert to NEXUS
    nexus_cmd = policy.action_to_nexus(action[0].item(), "What is the capital?")
    print(f"NEXUS command: {nexus_cmd}")
