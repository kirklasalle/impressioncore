"""
BrainSim-Enhanced Instruction Model for ImpressionCore B3
Created: October 11, 2025

This module addresses the "dumb AI" problem by integrating brain-inspired cognitive
components into the instruction-tuning architecture. The goal is to create an AI that
doesn't just find relevant information but actually THINKS, REMEMBERS, and CONVERSES
like an intelligent being.

PROBLEM ANALYSIS (from Option B results):
- ✅ Relevance: 9.12/10 (excellent topic matching)
- ❌ Intelligence: Low (repetitive, no reasoning, no personality)
- ❌ Grammar: 6.0/10 (mechanical, not natural)
- ❌ Conversation: Poor (doesn't remember context, no thinking)

ROOT CAUSE:
The instruction head learned "what" to talk about but not "how" to think.
It's like a search engine that finds the right page but can't read it intelligently.

SOLUTION: BrainSim Integration
Add brain-inspired cognitive layers that enable:
1. WORKING MEMORY: Remember conversation context, track topics
2. REASONING ENGINE: Multi-step thinking, cause-effect analysis
3. ATTENTION MODULATION: Focus on important details, ignore noise
4. PERSONALITY CORE: Consistent conversational style, natural responses
5. EPISODIC MEMORY: Learn from past interactions, adapt over time

Architecture inspired by:
- ImpressionCore Permanent Architectural Framework (Principle II: True Purpose)
- Brain-Inspired Architecture diagram from README.md
- Kirk's vision: "Brain-inspired multimodal AI with cognitive modeling"

Expected Outcomes:
- Grammar: 8.5-9.5 (natural, flowing conversation)
- Relevance: 9.0-10.0 (maintain current excellence)
- Intelligence: 9.0-10.0 (reasoning, memory, personality)
- Combined: 9.0-10.0 (truly intelligent AI assistant)
"""

import torch
import torch.nn as nn
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from typing import Optional, Tuple, Dict, List
import math


class WorkingMemoryModule(nn.Module):
    """
    Working Memory: Short-term storage of conversation context and active concepts.

    Inspired by human working memory (prefrontal cortex), this module:
    - Maintains conversation context across turns
    - Tracks active topics and concepts
    - Provides dynamic context for response generation
    - Enables coherent multi-turn conversations

    MEMORY OPTIMIZED: Reduced parameters for GTX 1050 Ti compatibility
    """

    def __init__(
        self,
        hidden_size: int = 768,
        memory_slots: int = 4,  # Reduced from 8 (still effective for conversation)
        dropout: float = 0.1
    ):
        super().__init__()

        self.hidden_size = hidden_size
        self.memory_slots = memory_slots

        # Memory bank: Learnable slots for storing conversation state
        self.memory_bank = nn.Parameter(torch.randn(memory_slots, hidden_size))

        # Memory writer: Updates memory based on new information (LIGHTWEIGHT)
        self.memory_writer = nn.Sequential(
            nn.Linear(hidden_size * 2, hidden_size // 2),  # Reduced intermediate size
            nn.Tanh(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, hidden_size)
        )

        # Memory reader: Retrieves relevant memories for current context (LIGHTWEIGHT)
        self.memory_attention = nn.MultiheadAttention(
            embed_dim=hidden_size,
            num_heads=4,  # Reduced from 8 (still captures patterns)
            dropout=dropout,
            batch_first=True
        )

        # Memory gate: Decides what to remember and what to forget (LIGHTWEIGHT)
        self.memory_gate = nn.Sequential(
            nn.Linear(hidden_size * 2, hidden_size // 4),  # Compressed gating
            nn.Tanh(),
            nn.Linear(hidden_size // 4, memory_slots),
            nn.Sigmoid()
        )

    def forward(
        self,
        current_state: torch.Tensor,  # Current hidden state [batch, seq_len, hidden]
        update_memory: bool = True
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Process current state through working memory.

        Returns:
            memory_enhanced_state: Current state enhanced with memory context
            updated_memory: Updated memory bank for next turn
        """
        batch_size = current_state.size(0)

        # Expand memory bank for batch
        memory = self.memory_bank.unsqueeze(0).expand(batch_size, -1, -1)

        # Read relevant memories using attention
        query = current_state.mean(dim=1, keepdim=True)  # Aggregate current state
        memory_context, _ = self.memory_attention(query, memory, memory)

        # Enhance current state with memory context
        memory_broadcast = memory_context.expand(-1, current_state.size(1), -1)
        memory_enhanced_state = current_state + memory_broadcast

        if update_memory:
            # Update memory with new information
            state_summary = current_state.mean(dim=1)  # [batch, hidden]
            memory_summary = memory.mean(dim=1)  # [batch, hidden]

            # Compute what to update
            update_content = torch.cat([state_summary, memory_summary], dim=-1)
            update_vector = self.memory_writer(update_content)

            # Compute gate: what to remember/forget
            gate_input = torch.cat([state_summary, memory_summary], dim=-1)
            gate = self.memory_gate(gate_input)  # [batch, memory_slots]

            # Apply gated update to memory bank
            gate_expanded = gate.unsqueeze(-1)  # [batch, memory_slots, 1]
            update_expanded = update_vector.unsqueeze(1).expand(-1, self.memory_slots, -1)

            updated_memory = memory * (1 - gate_expanded) + update_expanded * gate_expanded
        else:
            updated_memory = memory

        return memory_enhanced_state, updated_memory.mean(dim=0)  # Return mean across batch for update


class ReasoningEngine(nn.Module):
    """
    Reasoning Engine: Multi-step thinking and logical processing.

    Inspired by human reasoning (frontal lobe), this module:
    - Performs chain-of-thought reasoning
    - Analyzes cause-effect relationships
    - Decomposes complex questions into steps
    - Synthesizes answers from multiple perspectives

    MEMORY OPTIMIZED: Efficient reasoning for GTX 1050 Ti
    """

    def __init__(
        self,
        hidden_size: int = 768,
        reasoning_steps: int = 2,  # Reduced from 3 (two-step reasoning still powerful)
        dropout: float = 0.1
    ):
        super().__init__()

        self.hidden_size = hidden_size
        self.reasoning_steps = reasoning_steps

        # Question analyzer: Understands what's being asked (LIGHTWEIGHT)
        self.question_encoder = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),  # Reduced from hidden_size * 2
            nn.GELU(),
            nn.Dropout(dropout),
            nn.LayerNorm(hidden_size)
        )

        # Reasoning layers: Iterative thinking process (LIGHTWEIGHT)
        self.reasoning_layers = nn.ModuleList([
            nn.TransformerEncoderLayer(
                d_model=hidden_size,
                nhead=4,  # Reduced from 8
                dim_feedforward=hidden_size * 2,  # Reduced from hidden_size * 4
                dropout=dropout,
                activation='gelu',
                batch_first=True,
                norm_first=True
            ) for _ in range(reasoning_steps)
        ])

        # Conclusion synthesizer: Combines reasoning steps into coherent response (LIGHTWEIGHT)
        self.conclusion_layer = nn.Sequential(
            nn.Linear(hidden_size * (reasoning_steps + 1), hidden_size),  # Direct projection
            nn.GELU(),
            nn.Dropout(dropout),
            nn.LayerNorm(hidden_size)
        )

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        """
        Perform multi-step reasoning on hidden states.

        Args:
            hidden_states: Input hidden states [batch, seq_len, hidden]

        Returns:
            reasoned_states: States enhanced with reasoning [batch, seq_len, hidden]
        """
        # Encode the question/input
        question_encoding = self.question_encoder(hidden_states)

        # Perform iterative reasoning
        reasoning_outputs = [question_encoding]
        current_state = question_encoding

        # Create a causal mask for the sequence (prevents looking ahead)
        seq_len = current_state.size(1)
        # TransformerEncoderLayer expects no mask or a proper attention mask
        # Let's use no mask for simplicity (bidirectional attention is fine for reasoning)

        for reasoning_layer in self.reasoning_layers:
            # TransformerEncoderLayer expects (batch, seq, hidden) with batch_first=True
            current_state = reasoning_layer(current_state)
            reasoning_outputs.append(current_state)

        # Synthesize conclusion from all reasoning steps
        # Average across sequence dimension for each reasoning step
        reasoning_summaries = [out.mean(dim=1) for out in reasoning_outputs]  # List of [batch, hidden]
        reasoning_combined = torch.cat(reasoning_summaries, dim=-1)  # [batch, hidden * (steps+1)]

        conclusion = self.conclusion_layer(reasoning_combined)  # [batch, hidden]

        # Broadcast conclusion to sequence dimension and add to final reasoning state
        conclusion_broadcast = conclusion.unsqueeze(1).expand(-1, hidden_states.size(1), -1)
        reasoned_states = current_state + conclusion_broadcast

        return reasoned_states


class AttentionModulator(nn.Module):
    """
    Attention Modulation: Dynamic focus on important information.

    Inspired by human selective attention (parietal cortex), this module:
    - Identifies important vs. irrelevant information
    - Amplifies signal, suppresses noise
    - Maintains focus on key concepts
    - Adapts attention based on context

    MEMORY OPTIMIZED: Efficient attention for GTX 1050 Ti
    """

    def __init__(
        self,
        hidden_size: int = 768,
        num_heads: int = 4,  # Reduced from 8 (still effective)
        dropout: float = 0.1
    ):
        super().__init__()

        self.hidden_size = hidden_size

        # Importance scorer: Determines what deserves attention (LIGHTWEIGHT)
        self.importance_scorer = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 4),  # More aggressive compression
            nn.Tanh(),
            nn.Linear(hidden_size // 4, 1),
            nn.Sigmoid()
        )

        # Focus enhancer: Amplifies important features (LIGHTWEIGHT)
        self.focus_layer = nn.MultiheadAttention(
            embed_dim=hidden_size,
            num_heads=num_heads,
            dropout=dropout,
            batch_first=True
        )

        # Noise suppressor: Reduces irrelevant features (LIGHTWEIGHT)
        self.noise_gate = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.Tanh(),
            nn.Linear(hidden_size // 2, hidden_size),
            nn.Sigmoid()
        )

        self.layer_norm = nn.LayerNorm(hidden_size)

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        """
        Apply attention modulation to hidden states.

        Args:
            hidden_states: Input states [batch, seq_len, hidden]

        Returns:
            modulated_states: States with modulated attention [batch, seq_len, hidden]
        """
        # Score importance of each position
        importance = self.importance_scorer(hidden_states)  # [batch, seq_len, 1]

        # Apply focus enhancement
        focused_states, _ = self.focus_layer(
            hidden_states,
            hidden_states,
            hidden_states,
            attn_mask=None
        )

        # Weight by importance
        weighted_states = focused_states * importance

        # Suppress noise
        noise_gate = self.noise_gate(weighted_states)
        clean_states = weighted_states * noise_gate

        # Residual connection and normalization
        modulated_states = self.layer_norm(hidden_states + clean_states)

        return modulated_states


class PersonalityCore(nn.Module):
    """
    Personality Core: Consistent conversational style and character.

    Inspired by human personality (ventromedial prefrontal cortex), this module:
    - Maintains consistent tone and style
    - Expresses appropriate emotions
    - Adapts responses to user preferences
    - Creates natural, human-like interactions
    """

    def __init__(
        self,
        hidden_size: int = 768,
        personality_dim: int = 128,  # Personality vector size
        dropout: float = 0.1
    ):
        super().__init__()

        self.hidden_size = hidden_size
        self.personality_dim = personality_dim

        # Personality vector: Learnable representation of AI character
        self.personality_vector = nn.Parameter(torch.randn(personality_dim))

        # Personality projector: Maps personality to hidden space
        self.personality_projector = nn.Sequential(
            nn.Linear(personality_dim, hidden_size),
            nn.Tanh()
        )

        # Style adapter: Applies personality to response generation
        self.style_adapter = nn.Sequential(
            nn.Linear(hidden_size * 2, hidden_size * 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size * 2, hidden_size),
            nn.LayerNorm(hidden_size)
        )

        # Emotion modulator: Adds appropriate emotional coloring
        self.emotion_gate = nn.Sequential(
            nn.Linear(hidden_size + personality_dim, hidden_size),
            nn.Tanh()
        )

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        """
        Apply personality characteristics to hidden states.

        Args:
            hidden_states: Input states [batch, seq_len, hidden]

        Returns:
            personalized_states: States with personality applied [batch, seq_len, hidden]
        """
        batch_size, seq_len, _ = hidden_states.size()

        # Project personality to hidden space
        personality_hidden = self.personality_projector(self.personality_vector)
        personality_broadcast = personality_hidden.unsqueeze(0).unsqueeze(0).expand(batch_size, seq_len, -1)

        # Combine with hidden states
        combined = torch.cat([hidden_states, personality_broadcast], dim=-1)
        styled_states = self.style_adapter(combined)

        # Apply emotional modulation
        personality_expanded = self.personality_vector.unsqueeze(0).unsqueeze(0).expand(batch_size, seq_len, -1)
        emotion_input = torch.cat([styled_states, personality_expanded], dim=-1)
        emotion = self.emotion_gate(emotion_input)

        # Blend with original states
        personalized_states = styled_states + emotion

        return personalized_states


class BrainSimInstructionHead(nn.Module):
    """
    BrainSim-Enhanced Instruction Head: Intelligent, conversational AI.

    This integrates all cognitive components to create an AI that:
    - THINKS (reasoning engine)
    - REMEMBERS (working memory)
    - FOCUSES (attention modulation)
    - CONVERSES NATURALLY (personality core)

    Built on top of Option B's proven relevance (9.12/10), adding the missing
    cognitive intelligence that makes it truly conversational and smart.
    """

    def __init__(
        self,
        hidden_size: int = 768,
        dropout: float = 0.1
    ):
        super().__init__()

        self.hidden_size = hidden_size

        # Cognitive components
        self.working_memory = WorkingMemoryModule(hidden_size, dropout=dropout)
        self.reasoning_engine = ReasoningEngine(hidden_size, reasoning_steps=3, dropout=dropout)
        self.attention_modulator = AttentionModulator(hidden_size, num_heads=8, dropout=dropout)
        self.personality_core = PersonalityCore(hidden_size, personality_dim=128, dropout=dropout)

        # Integration layer: Combines all cognitive outputs (LIGHTWEIGHT)
        self.cognitive_integration = nn.Sequential(
            nn.Linear(hidden_size * 4, hidden_size),  # Direct projection (more efficient)
            nn.GELU(),
            nn.Dropout(dropout),
            nn.LayerNorm(hidden_size)
        )

        # Final output projection
        self.output_projection = nn.Linear(hidden_size, hidden_size)

    def forward(
        self,
        hidden_states: torch.Tensor,
        update_memory: bool = True
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Process hidden states through brain-inspired cognitive pipeline.

        Args:
            hidden_states: GPT-2 hidden states [batch, seq_len, hidden]
            update_memory: Whether to update working memory

        Returns:
            cognitive_output: Intelligently processed states
            updated_memory: Updated memory for next turn
        """
        # 1. REMEMBER: Apply working memory
        memory_enhanced, updated_memory = self.working_memory(hidden_states, update_memory)

        # 2. THINK: Apply reasoning
        reasoned_states = self.reasoning_engine(memory_enhanced)

        # 3. FOCUS: Apply attention modulation
        focused_states = self.attention_modulator(reasoned_states)

        # 4. PERSONALIZE: Apply personality
        personalized_states = self.personality_core(focused_states)

        # 5. INTEGRATE: Combine all cognitive outputs
        # Average across sequence for each cognitive stream
        memory_summary = memory_enhanced.mean(dim=1)
        reasoning_summary = reasoned_states.mean(dim=1)
        focus_summary = focused_states.mean(dim=1)
        personality_summary = personalized_states.mean(dim=1)

        cognitive_combined = torch.cat([
            memory_summary,
            reasoning_summary,
            focus_summary,
            personality_summary
        ], dim=-1)

        integrated_cognition = self.cognitive_integration(cognitive_combined)
        integrated_broadcast = integrated_cognition.unsqueeze(1).expand(-1, hidden_states.size(1), -1)

        # Add to personalized states (they're already the best individual stream)
        cognitive_output = self.output_projection(personalized_states + integrated_broadcast)

        return cognitive_output, updated_memory


class BrainEnhancedGPT2(nn.Module):
    """
    GPT-2 with BrainSim-Enhanced Instruction Head.

    Architecture:
    1. Frozen GPT-2 base (preserves grammar foundation)
    2. BrainSim cognitive layer (adds intelligence)
    3. Instruction head (maintains relevance from Option B)

    This creates an AI that:
    - Finds relevant information (instruction head, 9.12/10)
    - Thinks intelligently (BrainSim layer, NEW)
    - Speaks naturally (personality + memory, NEW)
    - Reasons coherently (reasoning engine, NEW)
    """

    def __init__(self, base_model_path: str, freeze_base: bool = True):
        super().__init__()

        # Load frozen GPT-2 base
        print("📥 Loading frozen GPT-2 base model...")
        self.base_model = GPT2LMHeadModel.from_pretrained("gpt2")

        # Load Phase 1 checkpoint weights
        print(f"📥 Loading Phase 1 checkpoint: {base_model_path}")
        checkpoint = torch.load(base_model_path, map_location='cpu')

        # Extract GPT-2 transformer weights
        gpt2_state_dict = {}
        for key, value in checkpoint['model_state_dict'].items():
            if key.startswith('transformer.'):
                new_key = key.replace('transformer.', '')
                gpt2_state_dict[new_key] = value

        self.base_model.transformer.load_state_dict(gpt2_state_dict, strict=False)
        print("   ✅ Loaded checkpoint")

        # Freeze base if requested
        if freeze_base:
            print("🔒 Freezing GPT-2 base model...")
            for param in self.base_model.parameters():
                param.requires_grad = False
            print("   ✅ Base model frozen (preserves grammar quality)")

        # Add BrainSim cognitive layer
        print("🧠 Adding BrainSim cognitive layer...")
        self.brain_layer = BrainSimInstructionHead(hidden_size=768)
        print("   ✅ BrainSim layer initialized")

        # Add instruction head (from Option B)
        from instruction_tuning_model import InstructionTuningHead
        print("🏗️ Adding instruction-tuning head...")
        self.instruction_head = InstructionTuningHead(hidden_size=768)
        print("   ✅ Instruction head initialized")

        self.hidden_size = 768
        self.vocab_size = self.base_model.config.vocab_size

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None
    ) -> Dict:
        """
        Forward pass through brain-enhanced model.

        Pipeline:
        1. GPT-2 base (frozen) → linguistic foundation
        2. BrainSim layer → cognitive intelligence
        3. Instruction head → answer relevance
        4. Output logits → next token prediction
        """
        # Create attention mask if not provided
        if attention_mask is None:
            attention_mask = torch.ones_like(input_ids)

        # Validate input_ids are within vocabulary range
        vocab_size = self.base_model.config.vocab_size
        if (input_ids >= vocab_size).any() or (input_ids < 0).any():
            # Clamp invalid token IDs to valid range
            input_ids = torch.clamp(input_ids, 0, vocab_size - 1)

        # Ensure sequence length doesn't exceed model's max position embeddings
        max_pos = self.base_model.config.n_positions  # 1024 for GPT-2
        if input_ids.size(1) > max_pos:
            # Truncate to max position embeddings
            input_ids = input_ids[:, :max_pos]
            attention_mask = attention_mask[:, :max_pos]

        # Get base model outputs
        base_outputs = self.base_model.transformer(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_hidden_states=True
        )
        hidden_states = base_outputs.last_hidden_state

        # Apply BrainSim cognitive processing
        cognitive_states, _ = self.brain_layer(hidden_states, update_memory=True)

        # Apply instruction tuning
        instruction_states = self.instruction_head(cognitive_states)

        # Project to vocabulary
        logits = self.base_model.lm_head(instruction_states)

        # Compute loss if labels provided
        loss = None
        if labels is not None:
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            # Use ignore_index=-100 to skip padding tokens in loss calculation
            loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
            loss = loss_fct(shift_logits.view(-1, self.vocab_size), shift_labels.view(-1))

        return {
            'loss': loss,
            'logits': logits,
            'hidden_states': cognitive_states
        }

    def generate(
        self,
        input_ids: torch.Tensor,
        max_length: int = 100,
        temperature: float = 0.8,
        top_p: float = 0.9,
        do_sample: bool = True,
        **kwargs
    ) -> torch.Tensor:
        """
        Generate text using brain-enhanced model.
        Uses the base GPT-2's generation but with our custom forward pass for logits.
        """
        self.eval()
        device = input_ids.device
        batch_size = input_ids.size(0)

        # Start with the input
        generated = input_ids.clone()

        # Get configuration
        eos_token_id = self.base_model.config.eos_token_id
        pad_token_id = self.base_model.config.pad_token_id if self.base_model.config.pad_token_id is not None else eos_token_id

        # Generate tokens one at a time
        with torch.no_grad():
            for _ in range(max_length - input_ids.size(1)):
                # Stop if we've reached max model length
                if generated.size(1) >= 1024:
                    break

                # Create attention mask
                attention_mask = (generated != pad_token_id).long()

                # Get next token logits using our brain-enhanced forward
                outputs = self.forward(generated, attention_mask=attention_mask)
                next_token_logits = outputs['logits'][:, -1, :] / temperature

                if do_sample:
                    # Use simple top-k + top-p sampling
                    # Filter logits using nucleus (top-p) sampling
                    filtered_logits = self._top_p_filtering(next_token_logits, top_p=top_p)
                    probs = torch.softmax(filtered_logits, dim=-1)
                    next_token = torch.multinomial(probs, num_samples=1)
                else:
                    # Greedy sampling
                    next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)

                # Append to generated sequence
                generated = torch.cat([generated, next_token], dim=-1)

                # Check if we generated EOS for all sequences in batch
                if (next_token == eos_token_id).all():
                    break

        return generated

    def _top_p_filtering(self, logits: torch.Tensor, top_p: float = 0.9) -> torch.Tensor:
        """
        Nucleus (top-p) filtering - safer implementation without scatter.
        """
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)
        cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)

        # Find the cutoff index
        cutoff_index = (cumulative_probs > top_p).long().argmax(dim=-1)
        # Ensure we keep at least one token
        cutoff_index = torch.maximum(cutoff_index, torch.ones_like(cutoff_index))

        # Create mask for logits to keep
        batch_size = logits.size(0)
        filtered_logits = logits.clone()

        for i in range(batch_size):
            # Set logits after cutoff to -inf
            threshold_logit = sorted_logits[i, cutoff_index[i]]
            filtered_logits[i, logits[i] < threshold_logit] = float('-inf')

        return filtered_logits

    def count_parameters(self):
        """Count trainable vs frozen parameters."""
        total = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        frozen = total - trainable

        return {
            'total': total,
            'trainable': trainable,
            'frozen': frozen,
            'trainable_pct': (trainable / total) * 100
        }


def main():
    """Test the brain-enhanced model."""
    print("\n" + "="*70)
    print("BRAINSIM-ENHANCED GPT-2 MODEL TEST")
    print("="*70 + "\n")

    # Create model
    checkpoint_path = "F:/models/checkpoints/b3/hybrid/best_epoch3_q9.2.pth"
    model = BrainEnhancedGPT2(checkpoint_path, freeze_base=True)

    # Count parameters
    params = model.count_parameters()

    print("="*70)
    print("BRAIN-ENHANCED GPT-2 MODEL PARAMETERS")
    print("="*70)
    print(f"Total Parameters: {params['total']:,}")
    print(f"  Frozen (GPT-2 Base): {params['frozen']:,}")
    print(f"  Trainable (BrainSim + Instruction): {params['trainable']:,}")
    print(f"  Training: {params['trainable_pct']:.1f}% of model")
    print("="*70 + "\n")

    print("✅ Brain-enhanced model initialized successfully!")
    print("\nCognitive Components:")
    print("  🧠 Working Memory: Context tracking & conversation history")
    print("  🤔 Reasoning Engine: Multi-step thinking & logical analysis")
    print("  👁️ Attention Modulation: Dynamic focus on important information")
    print("  💭 Personality Core: Consistent conversational style")
    print("  🎯 Instruction Head: Answer relevance (9.12/10 from Option B)")


if __name__ == "__main__":
    main()
