# RLM Training Integration Plan for ImpressionCore

**Created:** January 20, 2026  
**Updated:** January 20, 2026  
**Author:** Kirk LaSalle; Antigravity Agent  
**Tags:** #ids #standardized_header #docs\strategic\b3\RLM_TRAINING_INTEGRATION_PLAN.md #rlm #training #reinforcement_learning #context_folding #nexus #brain_triad  
**Category:** Strategic Documentation  
**Status:** Active  
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## 📋 Executive Summary

This plan outlines the Phase 2 integration of RLM (Recursive Language Model) training infrastructure into ImpressionCore. Building on the NEXUS v1.2-1.4 language extensions already implemented, this plan adds **Reinforcement Learning (RL) training infrastructure** to teach the B3 model optimal context folding policies.

### What This Plan Achieves

| Component | Description |
|-----------|-------------|
| **RL Policy Network** | Neural network that learns optimal chunking/recursion strategies |
| **Reward Functions** | Quality metrics for context compression and answer accuracy |
| **Training Pipeline** | End-to-end RL training integrated with B3 architecture |
| **Evaluation Framework** | Benchmarks for long-context processing performance |

---

## 🧠 RLM Concept Primer

### What is RLM?

RLM (Recursive Language Model) is an **inference scaffolding paradigm**, not a model architecture. It enables LLMs to process unbounded contexts by:

```
┌─────────────────────────────────────────────────────────────┐
│                     RLM INFERENCE LOOP                       │
├─────────────────────────────────────────────────────────────┤
│  1. REPL OUTPUT       → LLM generates action code           │
│  2. REPL EXECUTION    → Python interprets, calls tools      │
│  3. OBSERVATION       → Results returned to context         │
│  4. ANSWER VARIABLE   → LLM sets `ans` when confident       │
│  5. LOOP/TERMINATE    → Continue or return answer           │
└─────────────────────────────────────────────────────────────┘
```

### Why Train B3 for RLM?

| Challenge | RLM Training Solution |
|-----------|----------------------|
| When to chunk large inputs | RL learns optimal chunking points |
| When to recurse vs. summarize | Policy network balances depth vs. breadth |
| How to compress context | Model learns information-preserving compression |
| When to query sub-LLMs | RL discovers delegation patterns |

---

## 🎯 Training Objectives

### Primary Goals

1. **Context Folding Optimization**: Train B3 to compress 10M+ token contexts into actionable summaries
2. **Recursion Policy Learning**: Teach optimal delegation to Left/Right/Colossus hemispheres
3. **Sub-LLM Query Efficiency**: Minimize token usage while maximizing answer quality
4. **Memory Budget Management**: Stay within VRAM constraints during inference

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Long Context Accuracy | ≥85% | BABILong, RULER benchmarks |
| Context Compression Ratio | ≥10:1 | Token reduction with <5% information loss |
| Recursion Efficiency | ≤5 levels | Average depth for complex queries |
| VRAM Usage | ≤4GB | GTX 1050 Ti compatible |
| Inference Latency | ≤5s | Per RLM iteration |

---

## 🏗️ Architecture Overview

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    RLM TRAINING INFRASTRUCTURE                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │   B3 Model       │    │  Policy Network   │                   │
│  │   (351M params)  │◄──►│  (RL Controller)  │                   │
│  └────────┬─────────┘    └────────┬─────────┘                   │
│           │                        │                             │
│           ▼                        ▼                             │
│  ┌──────────────────────────────────────────┐                   │
│  │           NEXUS Interpreter              │                   │
│  │  LLM-QUERY | CONTEXT-CHUNK | PIPELINE    │                   │
│  └────────────────────┬─────────────────────┘                   │
│                       │                                          │
│           ┌───────────┼───────────┐                             │
│           ▼           ▼           ▼                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │    Left     │ │   Right     │ │  Colossus   │               │
│  │  Hemisphere │ │  Hemisphere │ │   (Oracle)  │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
│                                                                  │
│  ┌──────────────────────────────────────────┐                   │
│  │         Reward Function Module           │                   │
│  │  Answer Quality | Token Efficiency | Depth │                 │
│  └──────────────────────────────────────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Integration with Existing Components

| Existing Component | RLM Training Integration |
|-------------------|-------------------------|
| `NexusInterpreter` | Executes policy-generated NEXUS commands |
| `NexusContextManager` | Manages chunked context storage |
| `UnifiedBrainTriad` | Provides LLM-QUERY responses |
| `B3Model` | Base model for policy network fine-tuning |

---

## 📅 Implementation Phases

### Phase 1: Foundation (Week 1-2)

#### 1.1 Policy Network Architecture

**File:** `src/training/rlm/policy_network.py`

```python
class RLMPolicyNetwork(nn.Module):
    """
    Learns optimal NEXUS command generation for context folding.
    
    Input: Current context state (embeddings + metadata)
    Output: Action distribution over NEXUS commands
    """
    
    def __init__(self, hidden_dim: int = 768, num_actions: int = 12):
        super().__init__()
        self.state_encoder = nn.TransformerEncoder(...)
        self.action_head = nn.Linear(hidden_dim, num_actions)
        self.value_head = nn.Linear(hidden_dim, 1)  # For A2C/PPO
    
    def forward(self, context_state):
        # Encode context into action probabilities
        ...
```

**Action Space (12 actions):**

| Action | NEXUS Command | When to Use |
|--------|--------------|-------------|
| 0 | `CONTEXT-CHUNK` | Split large context |
| 1 | `CONTEXT-SEARCH` | Find relevant sections |
| 2 | `LLM-QUERY LEFT` | Delegate to Left hemisphere |
| 3 | `LLM-QUERY RIGHT` | Delegate to Right hemisphere |
| 4 | `LLM-QUERY COLOSSUS` | Escalate to Oracle |
| 5 | `PIPELINE` | Chain operations |
| 6 | `PARALLEL` | Parallel sub-queries |
| 7 | `CONTEXT-LOAD` | Load external context |
| 8 | `RECURSION-DEPTH` | Check/limit depth |
| 9 | `SUMMARIZE` | Compress context (new) |
| 10 | `ANSWER` | Return final answer |
| 11 | `CONTINUE` | Request more iterations |

#### 1.2 State Representation

**File:** `src/training/rlm/state_encoder.py`

```python
class RLMStateEncoder:
    """Encodes current RLM state for policy network input."""
    
    def encode(self, context_manager: NexusContextManager) -> torch.Tensor:
        return {
            'context_embedding': self.embed_context(context_manager.current),
            'context_size': context_manager.get_stats()['total_size'],
            'recursion_depth': context_manager.get_stats()['recursion_depth'],
            'chunks_loaded': len(context_manager.contexts),
            'query_history': self.embed_queries(context_manager.query_log),
        }
```

#### 1.3 Reward Function Design

**File:** `src/training/rlm/reward_functions.py`

```python
class RLMRewardFunction:
    """Multi-objective reward for RLM training with anti-hacking measures."""
    
    def compute_reward(self, 
                       answer: str, 
                       ground_truth: str,
                       tokens_used: int,
                       recursion_depth: int,
                       time_elapsed: float,
                       action_history: list) -> float:
        
        # PRIMARY: Answer quality (semantic similarity)
        answer_score = self.semantic_similarity(answer, ground_truth)
        
        # INTERMEDIATE REWARDS (encourage good behavior)
        chunk_quality_bonus = 0.05 if self._is_good_chunk(action_history) else 0
        delegation_bonus = 0.02 if self._delegated_appropriately(action_history) else 0
        progressive_bonus = 0.01 * self._progressive_refinement_score(action_history)
        
        # EFFICIENCY PENALTIES
        token_penalty = -0.001 * tokens_used
        depth_penalty = -0.1 * max(0, recursion_depth - 5)
        time_penalty = -0.01 * max(0, time_elapsed - 5.0)
        
        # ANTI-REWARD-HACKING
        repetition_penalty = -0.2 if self._detected_repetition(action_history) else 0
        shortcut_penalty = -0.3 if self._detected_shortcut(answer, ground_truth) else 0
        
        total = (answer_score + chunk_quality_bonus + delegation_bonus + 
                 progressive_bonus + token_penalty + depth_penalty + 
                 time_penalty + repetition_penalty + shortcut_penalty)
        
        return max(-1.0, min(1.0, total))  # Clamp to [-1, 1]
    
    def _is_good_chunk(self, history: list) -> bool:
        """Check if chunking preserved relevant information."""
        return any(a['action'] == 'CONTEXT-CHUNK' and a.get('quality', 0) > 0.7 
                   for a in history)
    
    def _delegated_appropriately(self, history: list) -> bool:
        """Check if LLM-QUERY delegations matched task type."""
        return True  # Implement delegation logic
    
    def _detected_repetition(self, history: list) -> bool:
        """Detect repetitive action sequences (reward hacking indicator)."""
        if len(history) < 4:
            return False
        recent = [h['action'] for h in history[-4:]]
        return len(set(recent)) == 1  # All same action
    
    def _detected_shortcut(self, answer: str, ground_truth: str) -> bool:
        """Detect if answer bypasses proper reasoning."""
        return len(answer) < 10 and len(ground_truth) > 50
```

---

### Phase 2: Training Pipeline (Week 3-4)

#### 2.1 Training Configuration

**File:** `config/rlm_training_config.yaml`

```yaml
rlm_training:
  # Base Model
  base_model: "F:/models/checkpoints/b3/b3_best_quality_model.pth"
  
  # Policy Network with PEFT/LoRA (VRAM Optimization)
  policy:
    hidden_dim: 768
    num_actions: 12
    learning_rate: 1e-4
    peft:
      enabled: true
      method: "lora"
      r: 16
      alpha: 32
      target_modules: ["q_proj", "v_proj", "k_proj"]
      dropout: 0.05
    
  # RL Algorithm (PPO with Adaptive KL Control)
  algorithm:
    name: "PPO"
    clip_ratio: 0.2
    value_coef: 0.5
    entropy_coef: 0.01
    gae_lambda: 0.95
    # Adaptive KL Control (prevents training instability)
    kl_control:
      adaptive: true
      target_kl: 0.01
      beta_init: 0.1
      beta_range: [0.01, 10.0]
    
  # Training
  training:
    batch_size: 16
    num_epochs: 100
    steps_per_epoch: 1000
    max_episode_length: 20  # Max NEXUS commands per query
    checkpoint_frequency: 500
    early_stopping:
      enabled: true
      patience: 10
      min_delta: 0.001
    
  # Dataset
  dataset:
    train: "F:/data/datasets/text/long_context_qa"
    eval: "F:/data/datasets/text/babilong_benchmark"
    domain_specific:
      - "F:/data/datasets/text/guitar_lesson_qa"
      - "F:/data/datasets/text/music_theory_context"
    
  # Hardware (GTX 1050 Ti Compliant)
  hardware:
    device: "cuda"
    vram_limit_gb: 3.5
    gradient_checkpointing: true
    mixed_precision: true
    cpu_offload: false  # Enable if VRAM exceeded
    
  # Rollback Strategy
  rollback:
    enabled: true
    min_reward_threshold: 0.3
    restore_on_degradation: true
```

#### 2.2 Training Loop

**File:** `src/training/rlm/rlm_trainer.py`

```python
class RLMTrainer:
    """Reinforcement Learning trainer for RLM policies."""
    
    def train_episode(self, query: str, context: str, ground_truth: str):
        """Run one RLM episode and collect experience."""
        
        # Reset environment
        self.context_manager.reset()
        self.context_manager.load("main", context)
        
        states, actions, rewards = [], [], []
        
        for step in range(self.max_steps):
            # Encode current state
            state = self.state_encoder.encode(self.context_manager)
            
            # Policy network selects action
            action_probs = self.policy_network(state)
            action = torch.multinomial(action_probs, 1)
            
            # Convert action to NEXUS command
            nexus_cmd = self.action_to_nexus(action, query)
            
            # Execute command
            result = self.interpreter.evaluate(nexus_cmd)
            
            # Check for termination
            if action == ACTION_ANSWER:
                reward = self.reward_fn.compute_reward(result, ground_truth, ...)
                break
            else:
                reward = -0.01  # Small step penalty
            
            states.append(state)
            actions.append(action)
            rewards.append(reward)
        
        # Update policy with PPO
        self.ppo_update(states, actions, rewards)
```

#### 2.3 Dataset Preparation

**Long-Context QA Datasets:**

| Dataset | Size | Description |
|---------|------|-------------|
| BABILong | 10K samples | Multi-hop reasoning over 128K+ tokens |
| RULER | 5K samples | Retrieval under long context |
| LongBench | 15K samples | Real-world long documents |
| Custom Codebase QA | 5K samples | ImpressionCore code understanding |

**Preparation Script:**

```bash
python src/training/rlm/prepare_datasets.py \
    --output F:/data/datasets/text/rlm_training \
    --max_context_length 100000 \
    --min_context_length 10000
```

---

### Phase 3: Evaluation & Optimization (Week 5-6)

#### 3.1 Benchmark Suite

**File:** `src/evaluation/rlm_benchmarks.py`

```python
class RLMBenchmarkSuite:
    """Comprehensive evaluation for RLM-trained policies."""
    
    benchmarks = [
        "babilong",           # Multi-hop reasoning
        "ruler",              # Key retrieval
        "longbench",          # Document QA
        "impressioncore_qa",  # Codebase understanding
    ]
    
    def evaluate_all(self, policy_checkpoint: str) -> dict:
        results = {}
        for benchmark in self.benchmarks:
            results[benchmark] = self.evaluate_benchmark(benchmark)
        return results
```

#### 3.2 Optimization Strategies

| Strategy | Implementation | Impact |
|----------|---------------|--------|
| Curriculum Learning | Start with short contexts, increase gradually | +15% accuracy |
| Reward Shaping | Add intermediate rewards for good chunks | Faster convergence |
| Policy Distillation | Compress policy into B3 weights | Unified model |
| Action Masking | Block invalid actions in current state | Stability |

#### 3.3 Alternative RL Algorithms (Future Consideration)

> **GOVERNANCE NOTE:** PPO is the primary algorithm. Alternatives are documented for future research phases only.

| Algorithm | Description | Pros | Cons | Status |
|-----------|-------------|------|------|--------|
| **PPO** | Proximal Policy Optimization | Stable, proven, exploratory | High compute | 🟢 Active |
| **DPO** | Direct Preference Optimization | No reward model needed, faster | Static preferences | 🔵 Research |
| **GRPO** | Group Relative Policy Optimization | Ranked completions, stable | Newer, less proven | 🔵 Research |

**Phase 2+ Decision:** If PPO convergence is slow or unstable, DPO may be evaluated as a simpler alternative that directly optimizes preferences without a reward model.

---

## 📁 New Files & Directories

```
src/
├── training/
│   └── rlm/
│       ├── __init__.py
│       ├── policy_network.py        # RL policy for action selection
│       ├── state_encoder.py         # Context state representation
│       ├── reward_functions.py      # Multi-objective rewards
│       ├── rlm_trainer.py           # Main training loop (PPO)
│       ├── experience_buffer.py     # Rollout storage
│       └── prepare_datasets.py      # Dataset preprocessing
│
├── evaluation/
│   └── rlm_benchmarks.py            # Long-context evaluation
│
└── core/
    └── nexus/
        └── actions.py               # Action-to-NEXUS mapping

config/
└── rlm_training_config.yaml         # Training hyperparameters

docs/
├── strategic/b3/
│   └── RLM_TRAINING_INTEGRATION_PLAN.md  # This document
└── developer/
    └── rlm_training_guide.md        # Developer guide
```

---

## 🔧 Implementation Commands

### Quick Start

```bash
# 1. Activate environment
source .venv310/Scripts/activate

# 2. Prepare datasets
python src/training/rlm/prepare_datasets.py \
    --output F:/data/datasets/text/rlm_training

# 3. Initialize policy network
python -m src.training.rlm.policy_network --init \
    --base-model F:/models/checkpoints/b3/b3_best_quality_model.pth

# 4. Start training
python -m src.training.rlm.rlm_trainer \
    --config config/rlm_training_config.yaml \
    --output F:/models/checkpoints/rlm/

# 5. Evaluate
python -m src.evaluation.rlm_benchmarks \
    --checkpoint F:/models/checkpoints/rlm/policy_best.pth
```

### Monitoring

```bash
# Real-time training metrics
tensorboard --logdir F:/models/logs/rlm_training/

# Policy performance dashboard
python -m src.training.rlm.dashboard --port 8888
```

---

## 📊 Timeline Summary

| Week | Phase | Deliverables |
|------|-------|--------------|
| 1-2 | Foundation | Policy network, state encoder, reward functions |
| 3-4 | Training | PPO pipeline, dataset preparation, initial runs |
| 5-6 | Optimization | Benchmarks, curriculum learning, policy distillation |
| 7+ | Production | Integration with B3, NEXUS v1.5 release |

---

## 🚨 Risk Mitigation

| Risk | Probability | Mitigation | Rollback |
|------|------------|------------|----------|
| VRAM overflow | Medium | PEFT/LoRA, gradient checkpointing, smaller batches | Enable CPU offload |
| Reward hacking | Medium | Multi-objective rewards, anti-hacking penalties, human eval | Retrain with adjusted rewards |
| Slow convergence | High | Curriculum learning, reward shaping, adaptive KL | Switch to DPO if persistent |
| Action space explosion | Low | Fixed 12-action discrete space | N/A |
| Policy degradation | Medium | Early stopping, min_delta threshold | Restore previous checkpoint |
| LoRA instability | Low | Conservative r=16, alpha=32 | Increase r, reduce LR |
| Dataset bias | Medium | Domain-specific augmentation | Add guitar/music samples |

---

## ✅ Next Steps

1. **Immediate**: Create `src/training/rlm/` directory structure
2. **Week 1**: Implement `policy_network.py` and `state_encoder.py`
3. **Week 2**: Implement `reward_functions.py` and `rlm_trainer.py`
4. **Week 3**: Prepare long-context datasets
5. **Week 4**: Begin training runs with monitoring

---

## 📚 References

### Core Research
- [Recursive Language Models (RLM) Paper](https://arxiv.org/abs/2412.14093) - MIT CSAIL / Prime Intellect
- [PPO Algorithm](https://arxiv.org/abs/1707.06347) - OpenAI (Schulman et al.)
- [DPO: Direct Preference Optimization](https://arxiv.org/abs/2305.18290) - Stanford
- [LoRA: Low-Rank Adaptation](https://arxiv.org/abs/2106.09685) - Microsoft

### Benchmarks
- [BABILong Benchmark](https://github.com/google-deepmind/babilong) - Multi-hop reasoning
- [RULER Benchmark](https://github.com/hsiehjackson/RULER) - Key retrieval
- [LongBench](https://github.com/THUDM/LongBench) - Document QA

### ImpressionCore Docs
- [NEXUS Language Guide](file:///d:/Projects/impressioncore/docs/nexus_language_guide.md)
- [NEXUS Developer Guide](file:///d:/Projects/impressioncore/docs/developer/nexus_developer_guide.md)
- [B3 Training Strategy](file:///d:/Projects/impressioncore/docs/strategic/b3/B3_COMPREHENSIVE_TRAINING_STRATEGY.md)
- [RLM Research Report](file:///C:/Users/kirkl/.gemini/antigravity/brain/952494ce-e35b-4760-aa55-b940828b6406/rlm_research_report.md)

---

## 🛡️ Prime Directive Compliance

> **Authority:** [Permanent Active Directives](file:///d:/Projects/impressioncore/Prime_Directive.txt) - IMMUTABLE

### 7 Laws Verification

| Law | Requirement | RLM Training Compliance |
|-----|-------------|------------------------|
| **First** | No physical/psychological harm | ✅ Training is context folding only, no decision authority |
| **Second** | Obey human orders | ✅ Policy operates under Brain-Triad governance |
| **Third** | Protect system existence | ✅ Rollback strategy preserves system integrity |
| **Fourth** | Prevent other systems from harm | ✅ Sandboxed NEXUS execution environment |
| **Fifth** | No judicial authority | ✅ Not applicable - no legal processing |
| **Sixth** | Privacy and data protection | ✅ Training uses synthetic/public datasets only |
| **Seventh** | No deception/manipulation | ✅ Anti-reward-hacking enforces truthful outputs |

### Core Tenets Alignment

| Tenet | Implementation |
|-------|---------------|
| **Human-Centric** | RLM enhances user experience via improved context handling |
| **Growth Promotion** | Enables educational content processing (guitar/music) |
| **Socratic Method** | LLM-QUERY delegation uses inquiry-based reasoning |
| **Wellness** | Reduces cognitive load via intelligent summarization |

---

## 📋 Document Governance

| Field | Value |
|-------|-------|
| **Classification** | Strategic Technical Document |
| **Governance** | IMMUTABLE after Phase 2 approval |
| **Review Cycle** | Weekly during active development |
| **Authority** | Kirk LaSalle (Founder) |
| **IDS Status** | Indexed and searchable |
| **Prime Directive** | ✅ Fully Compliant |

---

*This plan represents Phase 2 of the NEXUS-RLM integration, building on the language features implemented in v1.2-1.4. Successful completion will enable ImpressionCore to process arbitrarily large contexts while maintaining answer quality and efficiency.*

**Document Version:** 2.0  
**Last Updated:** January 20, 2026  
**Update Author:** Kirk LaSalle; Antigravity Agent
