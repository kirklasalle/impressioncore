# RLM State Encoder
# src/training/rlm/state_encoder.py

"""
State Encoder for RLM Policy Network.

Encodes the current RLM context state into a tensor representation
suitable for the policy network to make action decisions.

Prime Directive Compliance: ✅ Verified
"""

import logging
from dataclasses import dataclass
from typing import Any

import torch
import torch.nn as nn

logger = logging.getLogger("NEXUS.RLM.StateEncoder")


@dataclass
class StateEncoderConfig:
    """Configuration for RLM State Encoder."""
    hidden_dim: int = 768
    max_context_tokens: int = 512
    max_history_length: int = 20
    use_positional_encoding: bool = True


class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding."""

    def __init__(self, hidden_dim: int, max_len: int = 512):
        super().__init__()
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, hidden_dim, 2) * (-torch.log(torch.tensor(10000.0)) / hidden_dim))
        pe = torch.zeros(max_len, hidden_dim)
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(0))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:, :x.size(1)]


class RLMStateEncoder(nn.Module):
    """
    Encodes RLM state for policy network input.

    State Components:
        - context_embedding: Semantic representation of loaded context
        - context_metadata: Size, token count, chunk status
        - query_embedding: Current user query
        - action_history: Sequence of previous actions
        - recursion_state: Current depth and limits

    Output:
        Unified state tensor [batch, seq_len, hidden_dim]
    """

    def __init__(self, config: StateEncoderConfig | None = None):
        super().__init__()
        self.config = config or StateEncoderConfig()

        # Context encoder
        self.context_encoder = nn.Linear(self.config.hidden_dim, self.config.hidden_dim)

        # Query encoder
        self.query_encoder = nn.Linear(self.config.hidden_dim, self.config.hidden_dim)

        # Metadata encoder (scalar features -> hidden_dim)
        self.metadata_encoder = nn.Sequential(
            nn.Linear(8, 64),
            nn.ReLU(),
            nn.Linear(64, self.config.hidden_dim)
        )

        # Action history encoder
        self.action_embedding = nn.Embedding(12, self.config.hidden_dim)
        self.history_encoder = nn.GRU(
            self.config.hidden_dim,
            self.config.hidden_dim,
            batch_first=True
        )

        # Positional encoding
        if self.config.use_positional_encoding:
            self.pos_encoder = PositionalEncoding(
                self.config.hidden_dim,
                self.config.max_context_tokens
            )

        # Final projection
        self.output_proj = nn.Linear(self.config.hidden_dim * 4, self.config.hidden_dim)

        logger.info("RLMStateEncoder initialized")

    def encode_context(
        self,
        context_embedding: torch.Tensor
    ) -> torch.Tensor:
        """
        Encode context document embedding.

        Args:
            context_embedding: Pre-computed context embedding [batch, seq_len, hidden_dim]

        Returns:
            Encoded context [batch, hidden_dim]
        """
        # Apply positional encoding
        if self.config.use_positional_encoding:
            context_embedding = self.pos_encoder(context_embedding)

        # Encode and pool
        encoded = self.context_encoder(context_embedding)
        return encoded.mean(dim=1)  # [batch, hidden_dim]

    def encode_query(
        self,
        query_embedding: torch.Tensor
    ) -> torch.Tensor:
        """
        Encode user query embedding.

        Args:
            query_embedding: Query embedding [batch, seq_len, hidden_dim]

        Returns:
            Encoded query [batch, hidden_dim]
        """
        encoded = self.query_encoder(query_embedding)
        return encoded.mean(dim=1)

    def encode_metadata(
        self,
        metadata: dict[str, float]
    ) -> torch.Tensor:
        """
        Encode scalar metadata features.

        Args:
            metadata: Dictionary with keys:
                - context_size: Total context size in chars
                - token_count: Estimated token count
                - chunks_loaded: Number of chunks
                - recursion_depth: Current depth
                - max_recursion: Maximum allowed depth
                - searches_performed: Count of searches
                - queries_made: Count of LLM queries
                - time_elapsed: Time since query start

        Returns:
            Encoded metadata [batch, hidden_dim]
        """
        features = torch.tensor([
            metadata.get('context_size', 0) / 1e6,  # Normalize to millions
            metadata.get('token_count', 0) / 1e5,   # Normalize to 100K
            metadata.get('chunks_loaded', 0) / 10,
            metadata.get('recursion_depth', 0) / 20,
            metadata.get('max_recursion', 20) / 20,
            metadata.get('searches_performed', 0) / 10,
            metadata.get('queries_made', 0) / 10,
            metadata.get('time_elapsed', 0) / 30,   # Normalize to 30s
        ], dtype=torch.float32).unsqueeze(0)

        return self.metadata_encoder(features)

    def encode_action_history(
        self,
        actions: torch.Tensor
    ) -> torch.Tensor:
        """
        Encode sequence of previous actions.

        Args:
            actions: Action indices [batch, history_len]

        Returns:
            Encoded history [batch, hidden_dim]
        """
        if actions.numel() == 0:
            return torch.zeros(1, self.config.hidden_dim)

        action_emb = self.action_embedding(actions)
        _, hidden = self.history_encoder(action_emb)
        return hidden.squeeze(0)

    def forward(
        self,
        context_embedding: torch.Tensor,
        query_embedding: torch.Tensor,
        metadata: dict[str, float],
        action_history: torch.Tensor
    ) -> torch.Tensor:
        """
        Encode full RLM state.

        Args:
            context_embedding: Context document embedding
            query_embedding: User query embedding
            metadata: Scalar metadata features
            action_history: Previous action sequence

        Returns:
            state: Unified state tensor [batch, 1, hidden_dim]
        """
        # Encode each component
        ctx_enc = self.encode_context(context_embedding)
        query_enc = self.encode_query(query_embedding)
        meta_enc = self.encode_metadata(metadata)
        hist_enc = self.encode_action_history(action_history)

        # Concatenate all components
        combined = torch.cat([ctx_enc, query_enc, meta_enc, hist_enc], dim=-1)

        # Project to output dimension
        state = self.output_proj(combined)

        # Add sequence dimension
        return state.unsqueeze(1)  # [batch, 1, hidden_dim]

    @staticmethod
    def from_context_manager(
        context_manager: Any,
        query: str,
        action_history: list,
        embedder: Any
    ) -> dict[str, torch.Tensor]:
        """
        Create state inputs from NEXUS context manager.

        Args:
            context_manager: NexusContextManager instance
            query: Current user query
            action_history: List of previous action dicts
            embedder: Text embedding model

        Returns:
            Dictionary with tensor inputs for forward()
        """
        stats = context_manager.get_global_stats()

        # Get context text and embed
        active_ctx = context_manager.get_active_context()
        if isinstance(active_ctx, str):
            context_text = active_ctx[:4096]
        else:
            context_text = active_ctx.content[:4096] if active_ctx else ""

        # Build metadata
        metadata = {
            'context_size': stats.get('total_chars', 0),
            'token_count': stats.get('total_tokens_estimate', 0),
            'chunks_loaded': stats.get('contexts_loaded', 0),
            'recursion_depth': stats.get('current_recursion_depth', 0),
            'max_recursion': 20,
            'searches_performed': stats.get('total_searches', 0),
            'queries_made': stats.get('total_llm_queries', 0),
            'time_elapsed': 0,  # Caller should provide
        }

        # Extract action indices from history
        action_indices = [h.get('action_id', 11) for h in action_history[-20:]]

        return {
            'context_text': context_text,
            'query': query,
            'metadata': metadata,
            'action_indices': action_indices,
        }


if __name__ == "__main__":
    # Test state encoder
    config = StateEncoderConfig()
    encoder = RLMStateEncoder(config)

    # Dummy inputs
    context_emb = torch.randn(1, 100, 768)
    query_emb = torch.randn(1, 20, 768)
    metadata = {
        'context_size': 50000,
        'token_count': 12500,
        'chunks_loaded': 3,
        'recursion_depth': 2,
    }
    action_history = torch.tensor([[0, 1, 2]])  # 3 previous actions

    # Forward pass
    state = encoder(context_emb, query_emb, metadata, action_history)
    print(f"State shape: {state.shape}")
