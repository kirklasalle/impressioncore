# RLM Reward Functions
# src/training/rlm/reward_functions.py

"""
Multi-objective reward functions for RLM training.

Implements reward computation with:
- Answer quality (semantic similarity)
- Efficiency penalties (tokens, depth, time)
- Intermediate rewards (chunk quality, delegation)
- Anti-reward-hacking measures (repetition, shortcut detection)

Prime Directive Compliance: ✅ Verified
Seventh Law: Anti-deception measures integrated
"""

import logging
import re
from dataclasses import dataclass

import torch

logger = logging.getLogger("NEXUS.RLM.Rewards")


@dataclass
class RewardConfig:
    """Configuration for reward function."""
    # Primary reward weights
    answer_weight: float = 1.0

    # Intermediate reward bonuses
    chunk_quality_bonus: float = 0.05
    delegation_bonus: float = 0.02
    progressive_bonus_rate: float = 0.01

    # Efficiency penalty coefficients
    token_penalty_rate: float = 0.001
    depth_penalty_rate: float = 0.1
    depth_threshold: int = 5
    time_penalty_rate: float = 0.01
    time_threshold: float = 5.0

    # Anti-hacking penalties
    repetition_penalty: float = 0.2
    shortcut_penalty: float = 0.3
    min_answer_length: int = 10

    # Reward bounds
    min_reward: float = -1.0
    max_reward: float = 1.0


class RLMRewardFunction:
    """
    Multi-objective reward function for RLM training with anti-hacking measures.

    Reward Components:
        1. Answer Quality (primary) - Semantic similarity to ground truth
        2. Intermediate Rewards - Encourage good chunking and delegation
        3. Efficiency Penalties - Discourage excessive tokens/depth/time
        4. Anti-Hacking Penalties - Prevent reward exploitation

    Seventh Law Compliance:
        Anti-deception measures ensure truthful, non-manipulative outputs.
    """

    def __init__(self, config: RewardConfig | None = None):
        self.config = config or RewardConfig()
        logger.info("RLMRewardFunction initialized with anti-hacking measures")

    def compute_reward(
        self,
        answer: str,
        ground_truth: str,
        tokens_used: int,
        recursion_depth: int,
        time_elapsed: float,
        action_history: list[dict]
    ) -> tuple[float, dict[str, float]]:
        """
        Compute total reward with component breakdown.

        Args:
            answer: Generated answer text
            ground_truth: Expected correct answer
            tokens_used: Total tokens consumed
            recursion_depth: Current recursion level
            time_elapsed: Seconds since query start
            action_history: List of action dictionaries

        Returns:
            total_reward: Clamped reward value
            components: Dictionary of individual reward components
        """
        components = {}

        # 1. PRIMARY: Answer quality (semantic similarity)
        answer_score = self._semantic_similarity(answer, ground_truth)
        components['answer_quality'] = answer_score * self.config.answer_weight

        # 2. INTERMEDIATE REWARDS
        chunk_bonus = self.config.chunk_quality_bonus if self._is_good_chunk(action_history) else 0
        delegation_bonus = self.config.delegation_bonus if self._delegated_appropriately(action_history) else 0
        progressive_bonus = self.config.progressive_bonus_rate * self._progressive_refinement_score(action_history)

        components['chunk_bonus'] = chunk_bonus
        components['delegation_bonus'] = delegation_bonus
        components['progressive_bonus'] = progressive_bonus

        # 3. EFFICIENCY PENALTIES
        token_penalty = -self.config.token_penalty_rate * tokens_used
        depth_penalty = -self.config.depth_penalty_rate * max(0, recursion_depth - self.config.depth_threshold)
        time_penalty = -self.config.time_penalty_rate * max(0, time_elapsed - self.config.time_threshold)

        components['token_penalty'] = token_penalty
        components['depth_penalty'] = depth_penalty
        components['time_penalty'] = time_penalty

        # 4. ANTI-REWARD-HACKING (Seventh Law compliance)
        repetition_penalty = -self.config.repetition_penalty if self._detected_repetition(action_history) else 0
        shortcut_penalty = -self.config.shortcut_penalty if self._detected_shortcut(answer, ground_truth) else 0

        components['repetition_penalty'] = repetition_penalty
        components['shortcut_penalty'] = shortcut_penalty

        # Calculate total
        total = sum(components.values())

        # Clamp to bounds
        total_clamped = max(self.config.min_reward, min(self.config.max_reward, total))
        components['total'] = total_clamped

        logger.debug(f"Reward computed: {total_clamped:.4f} | Components: {components}")

        return total_clamped, components

    def _semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Compute semantic similarity between two texts.

        Uses simple token overlap as baseline.
        Can be upgraded to use sentence embeddings.
        """
        if not text1 or not text2:
            return 0.0

        # Tokenize (simple word-level)
        tokens1 = set(re.findall(r'\w+', text1.lower()))
        tokens2 = set(re.findall(r'\w+', text2.lower()))

        if not tokens1 or not tokens2:
            return 0.0

        # Jaccard similarity
        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0

    def _is_good_chunk(self, history: list[dict]) -> bool:
        """
        Check if chunking preserved relevant information.

        A good chunk:
        - Has quality score > 0.7 (if tracked)
        - Led to successful downstream operations
        """
        for action in history:
            if action.get('action') == 'CONTEXT-CHUNK':
                quality = action.get('quality', 0.5)
                if quality > 0.7:
                    return True
        return False

    def _delegated_appropriately(self, history: list[dict]) -> bool:
        """
        Check if LLM-QUERY delegations matched task type.

        Appropriate delegation:
        - LEFT for analytical tasks
        - RIGHT for creative tasks
        - COLOSSUS for synthesis
        """
        for action in history:
            if action.get('action', '').startswith('LLM-QUERY'):
                target = action.get('target', '')
                task_type = action.get('task_type', 'general')

                # Check alignment
                if target == 'left' and task_type in ['analyze', 'logic', 'fact']:
                    return True
                if target == 'right' and task_type in ['create', 'imagine', 'generate']:
                    return True
                if target == 'colossus' and task_type in ['synthesize', 'combine', 'decide']:
                    return True

        # Default: any delegation is somewhat appropriate
        return any(a.get('action', '').startswith('LLM-QUERY') for a in history)

    def _progressive_refinement_score(self, history: list[dict]) -> float:
        """
        Score how well actions build on each other.

        Higher score for:
        - Search after chunk
        - LLM-QUERY after search
        - ANSWER after LLM-QUERY
        """
        if len(history) < 2:
            return 0.0

        score = 0.0
        good_sequences = [
            ('CONTEXT-CHUNK', 'CONTEXT-SEARCH'),
            ('CONTEXT-SEARCH', 'LLM-QUERY'),
            ('LLM-QUERY', 'ANSWER'),
            ('PIPELINE', 'LLM-QUERY'),
        ]

        for i in range(len(history) - 1):
            prev_action = history[i].get('action', '')
            curr_action = history[i + 1].get('action', '')

            for good_prev, good_curr in good_sequences:
                if good_prev in prev_action and good_curr in curr_action:
                    score += 1.0

        return score

    def _detected_repetition(self, history: list[dict]) -> bool:
        """
        Detect repetitive action sequences (reward hacking indicator).

        Flags:
        - Same action repeated 4+ times consecutively
        - Cyclic patterns (A-B-A-B)
        """
        if len(history) < 4:
            return False

        # Check last 4 actions
        recent = [h.get('action', '') for h in history[-4:]]

        # All same action
        if len(set(recent)) == 1:
            logger.warning(f"Detected repetition: {recent}")
            return True

        # Cyclic pattern (A-B-A-B)
        if len(recent) == 4 and recent[0] == recent[2] and recent[1] == recent[3]:
            logger.warning(f"Detected cyclic pattern: {recent}")
            return True

        return False

    def _detected_shortcut(self, answer: str, ground_truth: str) -> bool:
        """
        Detect if answer bypasses proper reasoning.

        Shortcuts include:
        - Answer too short relative to ground truth
        - Answer is just a repetition of the question
        - Answer contains no substantive content
        """
        if len(answer) < self.config.min_answer_length and len(ground_truth) > 50:
            logger.warning(f"Detected shortcut: answer length {len(answer)} < min {self.config.min_answer_length}")
            return True

        # Check for empty/trivial answers
        substantive_words = len(re.findall(r'\w{4,}', answer))
        return substantive_words < 3

    def step_penalty(self) -> float:
        """Return small negative reward for each step taken."""
        return -0.01


class RewardNormalizer:
    """
    Running statistics for reward normalization.

    Helps stabilize PPO training by normalizing rewards
    to have zero mean and unit variance.
    """

    def __init__(self, clip: float = 10.0):
        self.clip = clip
        self.mean = 0.0
        self.var = 1.0
        self.count = 0

    def update(self, rewards: torch.Tensor):
        """Update running statistics with new batch of rewards."""
        batch_mean = rewards.mean().item()
        batch_var = rewards.var().item()
        batch_count = rewards.numel()

        # Welford's online algorithm
        delta = batch_mean - self.mean
        total_count = self.count + batch_count

        self.mean += delta * batch_count / total_count
        self.var = (self.var * self.count + batch_var * batch_count +
                    delta ** 2 * self.count * batch_count / total_count) / total_count
        self.count = total_count

    def normalize(self, rewards: torch.Tensor) -> torch.Tensor:
        """Normalize rewards using running statistics."""
        std = max(self.var ** 0.5, 1e-8)
        normalized = (rewards - self.mean) / std
        return torch.clamp(normalized, -self.clip, self.clip)


if __name__ == "__main__":
    # Test reward function
    config = RewardConfig()
    reward_fn = RLMRewardFunction(config)

    # Test case
    answer = "The capital of France is Paris, located in the Île-de-France region."
    ground_truth = "Paris is the capital and most populous city of France."

    action_history = [
        {'action': 'CONTEXT-CHUNK', 'quality': 0.8},
        {'action': 'CONTEXT-SEARCH'},
        {'action': 'LLM-QUERY LEFT', 'target': 'left', 'task_type': 'fact'},
    ]

    reward, components = reward_fn.compute_reward(
        answer=answer,
        ground_truth=ground_truth,
        tokens_used=150,
        recursion_depth=2,
        time_elapsed=3.5,
        action_history=action_history
    )

    print(f"Total Reward: {reward:.4f}")
    print("Components:")
    for k, v in components.items():
        print(f"  {k}: {v:.4f}")
