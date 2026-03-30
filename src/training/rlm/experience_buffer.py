# RLM Experience Buffer
# src/training/rlm/experience_buffer.py

"""
Experience buffer for PPO rollout storage.

Stores transitions from RLM episodes for policy updates,
including states, actions, rewards, and log probabilities.

Prime Directive Compliance: ✅ Verified
"""

import logging
from dataclasses import dataclass

import numpy as np
import torch

logger = logging.getLogger("NEXUS.RLM.ExperienceBuffer")


@dataclass
class Transition:
    """Single transition from environment."""
    state: torch.Tensor
    action: int
    reward: float
    log_prob: float
    value: float
    done: bool

    # Optional metadata
    action_name: str = ""
    nexus_command: str = ""


class ExperienceBuffer:
    """
    Rollout buffer for PPO training.

    Stores experiences during policy rollout and provides
    batched data for policy updates with GAE advantage estimation.

    Features:
        - Generalized Advantage Estimation (GAE)
        - VRAM-efficient storage
        - Mini-batch sampling for gradient updates
    """

    def __init__(
        self,
        buffer_size: int = 2048,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
        device: str = "cuda"
    ):
        self.buffer_size = buffer_size
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.device = device

        self.reset()
        logger.info(f"ExperienceBuffer initialized: size={buffer_size}, gamma={gamma}, lambda={gae_lambda}")

    def reset(self):
        """Clear the buffer."""
        self.states: list[torch.Tensor] = []
        self.actions: list[int] = []
        self.rewards: list[float] = []
        self.log_probs: list[float] = []
        self.values: list[float] = []
        self.dones: list[bool] = []

        # Computed during finalize
        self.advantages: torch.Tensor | None = None
        self.returns: torch.Tensor | None = None

        self._finalized = False

    def add(self, transition: Transition):
        """Add a transition to the buffer."""
        if self._finalized:
            raise RuntimeError("Cannot add to finalized buffer. Call reset() first.")

        self.states.append(transition.state)
        self.actions.append(transition.action)
        self.rewards.append(transition.reward)
        self.log_probs.append(transition.log_prob)
        self.values.append(transition.value)
        self.dones.append(transition.done)

    def add_batch(
        self,
        states: torch.Tensor,
        actions: torch.Tensor,
        rewards: torch.Tensor,
        log_probs: torch.Tensor,
        values: torch.Tensor,
        dones: torch.Tensor
    ):
        """Add a batch of transitions."""
        for i in range(len(actions)):
            self.add(Transition(
                state=states[i],
                action=actions[i].item(),
                reward=rewards[i].item(),
                log_prob=log_probs[i].item(),
                value=values[i].item(),
                done=dones[i].item()
            ))

    def __len__(self) -> int:
        return len(self.states)

    def is_full(self) -> bool:
        return len(self) >= self.buffer_size

    def finalize(self, last_value: float = 0.0):
        """
        Compute advantages and returns using GAE.

        Args:
            last_value: Value estimate for the last state (bootstrap)
        """
        if self._finalized:
            return

        rewards = np.array(self.rewards)
        values = np.array([*self.values, last_value])
        dones = np.array([*self.dones, True])

        # GAE computation
        advantages = np.zeros_like(rewards)
        last_gae = 0.0

        for t in reversed(range(len(rewards))):
            if dones[t]:
                next_value = 0.0
                last_gae = 0.0
            else:
                next_value = values[t + 1]

            delta = rewards[t] + self.gamma * next_value - values[t]
            last_gae = delta + self.gamma * self.gae_lambda * last_gae * (1 - dones[t])
            advantages[t] = last_gae

        # Compute returns
        returns = advantages + values[:-1]

        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        self.advantages = torch.tensor(advantages, dtype=torch.float32, device=self.device)
        self.returns = torch.tensor(returns, dtype=torch.float32, device=self.device)

        self._finalized = True
        logger.debug(f"Buffer finalized: {len(self)} transitions, mean advantage={self.advantages.mean():.4f}")

    def get_batches(
        self,
        batch_size: int = 64,
        shuffle: bool = True
    ) -> list[dict[str, torch.Tensor]]:
        """
        Get mini-batches for PPO updates.

        Args:
            batch_size: Size of each mini-batch
            shuffle: Whether to shuffle before batching

        Returns:
            List of batch dictionaries
        """
        if not self._finalized:
            raise RuntimeError("Must call finalize() before getting batches.")

        n = len(self)
        indices = np.arange(n)

        if shuffle:
            np.random.shuffle(indices)

        # Convert to tensors
        states = torch.stack(self.states).to(self.device)
        actions = torch.tensor(self.actions, dtype=torch.long, device=self.device)
        old_log_probs = torch.tensor(self.log_probs, dtype=torch.float32, device=self.device)
        old_values = torch.tensor(self.values, dtype=torch.float32, device=self.device)

        batches = []
        for start in range(0, n, batch_size):
            end = min(start + batch_size, n)
            batch_indices = indices[start:end]

            batches.append({
                'states': states[batch_indices],
                'actions': actions[batch_indices],
                'old_log_probs': old_log_probs[batch_indices],
                'old_values': old_values[batch_indices],
                'advantages': self.advantages[batch_indices],
                'returns': self.returns[batch_indices],
            })

        return batches

    def get_statistics(self) -> dict[str, float]:
        """Get buffer statistics for logging."""
        if not self._finalized:
            return {'size': len(self)}

        return {
            'size': len(self),
            'mean_reward': np.mean(self.rewards),
            'std_reward': np.std(self.rewards),
            'mean_advantage': self.advantages.mean().item(),
            'std_advantage': self.advantages.std().item(),
            'mean_return': self.returns.mean().item(),
            'mean_value': np.mean(self.values),
        }


if __name__ == "__main__":
    # Test experience buffer
    buffer = ExperienceBuffer(buffer_size=100)

    # Add dummy transitions
    for i in range(50):
        state = torch.randn(1, 768)
        transition = Transition(
            state=state,
            action=i % 12,
            reward=np.random.randn() * 0.1,
            log_prob=np.log(0.1),
            value=np.random.randn(),
            done=(i == 49)
        )
        buffer.add(transition)

    # Finalize
    buffer.finalize(last_value=0.0)

    # Get batches
    batches = buffer.get_batches(batch_size=16)
    print(f"Number of batches: {len(batches)}")
    print(f"Batch 0 states shape: {batches[0]['states'].shape}")

    # Statistics
    stats = buffer.get_statistics()
    print(f"Statistics: {stats}")
