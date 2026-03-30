# Agent0Core RLM Training Integration Task
# docs/developer/AGENT0CORE_RLM_INTEGRATION.md

"""
This document defines the integration points between Agent0Core
and the RLM Training Infrastructure for autonomous operation.
"""

# Agent0Core RLM Training Integration

**Created:** January 20, 2026  
**Updated:** January 20, 2026  
**Author:** Kirk LaSalle; Antigravity Agent  
**Tags:** #ids #agent0core #rlm #training #integration #triad_api  
**Category:** Developer Documentation  
**Status:** Active  
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## 📋 Executive Summary

This document provides Agent0Core with the integration specifications and task definitions for operating the RLM (Recursive Language Model) training infrastructure.

---

## 🎯 Agent0Core Task Definitions

### Task 1: Dataset Preparation

**Command:**
```bash
python -m src.training.rlm.prepare_datasets \
    --output F:/data/datasets/text/rlm_training \
    --max_context_length 100000 \
    --min_context_length 1000
```

**Success Criteria:**
- [ ] manifest.json created
- [ ] train.jsonl and eval.jsonl generated
- [ ] At least 3000 total samples

**Error Handling:**
- If disk space low: Alert user, clean temp files
- If generation fails: Retry with smaller batch size

---

### Task 2: Training Execution

**Command:**
```bash
python -m src.training.rlm.rlm_trainer \
    --config config/rlm_training_config.yaml
```

**Monitoring (TensorBoard):**
```bash
tensorboard --logdir F:/models/logs/rlm_training/ --port 6007
```

**Success Criteria:**
- [ ] Training completes without VRAM overflow
- [ ] Mean reward > 0.3 by epoch 50
- [ ] policy_best.pth checkpoint saved

**Error Handling:**
- If VRAM exceeded: Enable CPU offload in config
- If reward stagnates: Reduce learning rate by 50%
- If NaN detected: Restore last checkpoint, reduce batch size

---

### Task 3: Benchmark Evaluation

**Command:**
```bash
python -m src.evaluation.rlm_benchmarks \
    --checkpoint F:/models/checkpoints/rlm/policy_best.pth \
    --output F:/models/checkpoints/rlm/benchmark_results.json \
    --samples 100
```

**Success Thresholds:**
| Metric | Target |
|--------|--------|
| Long Context Accuracy | ≥85% |
| Context Compression | ≥10:1 |
| Max Recursion Depth | ≤5 |
| Max Latency | ≤5s |
| VRAM Usage | ≤4GB |

**Error Handling:**
- If accuracy < 85%: Log for human review, continue training
- If latency > 5s: Profile and optimize

---

## 🔗 API Integration Points

### triad_api.py Integration

Add these endpoints to `src/core/triad_api.py`:

```python
# RLM Training Status Endpoint
@app.route('/api/rlm/status', methods=['GET'])
def rlm_training_status():
    """Get RLM training status and metrics."""
    return {
        "status": "training" | "idle" | "complete",
        "current_epoch": int,
        "mean_reward": float,
        "best_checkpoint": str,
    }

# RLM Training Control Endpoints
@app.route('/api/rlm/start', methods=['POST'])
def start_rlm_training():
    """Start RLM training run."""
    pass

@app.route('/api/rlm/stop', methods=['POST'])
def stop_rlm_training():
    """Gracefully stop training, save checkpoint."""
    pass

# RLM Policy Inference Endpoint
@app.route('/api/rlm/action', methods=['POST'])
def get_rlm_action():
    """Get policy action for current NEXUS state."""
    # Input: context_state from NexusContextManager
    # Output: recommended NEXUS command
    pass
```

### NexusInterpreter Integration

Location: `src/core/nexus/nexus_interpreter.py`

```python
class NexusInterpreter:
    def __init__(self, rlm_policy=None):
        self.rlm_policy = rlm_policy
        
    def get_policy_suggestion(self, context_manager):
        """Get RLM policy suggestion for next action."""
        if self.rlm_policy is None:
            return None
        
        state = self.state_encoder.encode(context_manager)
        action, _, _ = self.rlm_policy.get_action(state)
        return self.rlm_policy.action_to_nexus(action.item(), query)
```

---

## 📁 File Structure

```
src/
├── training/
│   └── rlm/
│       ├── __init__.py              ✅ Created
│       ├── policy_network.py        ✅ Created
│       ├── state_encoder.py         ✅ Created
│       ├── reward_functions.py      ✅ Created
│       ├── experience_buffer.py     ✅ Created
│       ├── rlm_trainer.py           ✅ Created
│       └── prepare_datasets.py      ✅ Created
│
├── evaluation/
│   └── rlm_benchmarks.py            ✅ Created
│
└── core/
    ├── triad_api.py                 🔄 Needs RLM endpoints
    └── nexus/
        ├── nexus_interpreter.py     🔄 Needs policy integration
        └── nexus_context_manager.py ✅ Existing

config/
└── rlm_training_config.yaml         ✅ Created

docs/
├── strategic/b3/
│   └── RLM_TRAINING_INTEGRATION_PLAN.md  ✅ v2.0 Complete
└── developer/
    └── AGENT0CORE_RLM_INTEGRATION.md     ✅ This document
```

---

## 🚦 Execution Sequence

Agent0Core should execute in this order:

1. **Verify Environment**
   ```bash
   source .venv310/Scripts/activate
   python -c "import torch; print(torch.cuda.is_available())"
   ```

2. **Prepare Datasets** (if not exists)
   ```bash
   python -m src.training.rlm.prepare_datasets --output F:/data/datasets/text/rlm_training
   ```

3. **Start Training**
   ```bash
   python -m src.training.rlm.rlm_trainer --config config/rlm_training_config.yaml
   ```

4. **Monitor Progress**
   - Check tensorboard every 500 steps
   - Alert if mean_reward < 0.1 after 1000 steps

5. **Run Benchmarks** (after training)
   ```bash
   python -m src.evaluation.rlm_benchmarks --checkpoint F:/models/checkpoints/rlm/policy_best.pth
   ```

6. **Report Results**
   - Save benchmark_results.json
   - Update memlog with completion status

---

## 🛡️ Prime Directive Compliance

| Law | Agent0Core Responsibility |
|-----|--------------------------|
| First | Training has no decision authority over humans |
| Second | Obeys user commands for start/stop |
| Third | Checkpoints preserve system state |
| Fourth | Cannot harm other systems |
| Fifth | No judicial authority |
| Sixth | Uses public/synthetic data only |
| Seventh | Anti-hacking measures prevent deception |

---

## ✅ Handoff Checklist

- [x] Policy network implemented
- [x] State encoder implemented
- [x] Reward functions implemented
- [x] Experience buffer implemented
- [x] Trainer implemented
- [x] Config file created
- [x] Dataset prep script created
- [x] Benchmark suite created
- [x] Integration docs created
- [ ] triad_api endpoints (Agent0Core task)
- [ ] NexusInterpreter integration (Agent0Core task)
- [ ] Initial training run (Agent0Core task)
- [ ] Benchmark validation (Agent0Core task)

---

## 📚 Research Citations & Due Diligence

### Core Algorithm References

| Paper | Authors | Year | Application |
|-------|---------|------|-------------|
| [PPO: Proximal Policy Optimization](https://arxiv.org/abs/1707.06347) | Schulman et al. | 2017 | Primary RL algorithm |
| [LoRA: Low-Rank Adaptation](https://arxiv.org/abs/2106.09685) | Hu et al. (Microsoft) | 2021 | VRAM-efficient fine-tuning |
| [DPO: Direct Preference Optimization](https://arxiv.org/abs/2305.18290) | Rafailov et al. (Stanford) | 2023 | Alternative to PPO |
| [RLM: Recursive Language Models](https://arxiv.org/abs/2412.14093) | Zhang, Kraska, Khattab (MIT CSAIL) | 2024 | Context folding paradigm |

### Best Practices Applied (2025-2026 Research)

| Practice | Source | Implementation |
|----------|--------|----------------|
| **Adaptive KL Control** | InstructGPT, Llama 2 | `target_kl=0.01`, dynamic beta |
| **PEFT/LoRA** | Microsoft Research | `r=16, alpha=32` for VRAM efficiency |
| **Reward Shaping** | RLHF Literature | Intermediate bonuses, anti-hacking |
| **Gradient Checkpointing** | PyTorch Best Practices | Standard for GTX 1050 Ti |
| **Mixed Precision** | NVIDIA Training Guide | FP16 for memory savings |

### Benchmark Sources

| Benchmark | Source | Purpose |
|-----------|--------|---------|
| BABILong | Google DeepMind | Multi-hop reasoning over 128K+ tokens |
| RULER | Academic Research | Key retrieval in long contexts |
| LongBench | THUDM | Real-world document QA |

### Alternative Algorithms (Documented for Future Research)

| Algorithm | Paper | Status |
|-----------|-------|--------|
| GRPO (Group Relative Policy Optimization) | DeepSeek | 🔵 Research candidate |
| ORPO (Odds Ratio Policy Optimization) | 2024 Research | 🔵 Future consideration |
| KTO (Kahneman-Tversky Optimization) | 2024 Research | 🔵 Future consideration |

---

**Document Governance:**
- Classification: Developer Integration Document
- Authority: Kirk LaSalle (Founder)
- Status: Ready for Agent0Core execution
- Research Verified: January 20, 2026

