"""Unit Tests for OrreryCognitiveBridge in ImpressionCore."""
import os
import sys
import pytest

# Ensure project root is in sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.memory.orrery_cognitive_bridge import OrreryCognitiveBridge, CognitiveReceipt



@pytest.fixture
def bridge():
    return OrreryCognitiveBridge(agent_id="test_agent_0", charter_goal="Autonomous Knowledge Distillation")


def test_tier1_charter_establishment(bridge):
    """Test Tier 1: Ephemeris meta-strategy alignment."""
    bridge.establish_charter(
        goal="Fine-tune multi-modal reasoning on GTX 1050 Ti",
        constraints=["VRAM < 4GB", "No external API leakage"]
    )

    assert bridge.charter_goal == "Fine-tune multi-modal reasoning on GTX 1050 Ti"
    assert bridge.tier1_meta_strategy["alignment_score"] == 1.0
    assert "VRAM < 4GB" in bridge.tier1_meta_strategy["constraints"]


def test_tier2_milestone_planning(bridge):
    """Test Tier 2: Macro-Orbit milestone decomposition."""
    milestones = bridge.plan_macro_milestones([
        {"id": "m1", "title": "Load Dataset", "description": "Prepare tokenized batches"},
        {"id": "m2", "title": "Run Gradient Checkpointing", "description": "Train memory-efficient layers"},
        {"id": "m3", "title": "Evaluate Benchmark", "description": "Verify perplexity"}
    ])

    assert len(milestones) == 3
    assert milestones[0].status == "active"
    assert milestones[1].status == "pending"

    # Complete first milestone
    bridge.complete_active_milestone(success=True)
    assert milestones[0].status == "completed"
    assert milestones[1].status == "active"


def test_tier3_meso_action_dispatch(bridge):
    """Test Tier 3: Meso-Cycle action queue."""
    action_id = bridge.dispatch_meso_action(
        tool_name="tokenize_text",
        parameters={"text": "Brain-inspired multimodal cognition", "max_len": 128}
    )

    assert action_id.startswith("act_")
    assert len(bridge.tier3_meso_queue) == 1
    assert bridge.tier3_meso_queue[0]["tool_name"] == "tokenize_text"


def test_tier4_micro_execution_and_immutable_ledger(bridge):
    """Test Tier 4: Micro-step execution, cryptographic hashing, and immutable ledgering."""
    bridge.plan_macro_milestones([{"title": "Execute Step"}])

    def sample_executor(payload):
        return f"Processed {payload['count']} tokens"

    receipt = bridge.execute_micro_step(
        tool_name="memory_compression",
        payload={"count": 512},
        execute_fn=sample_executor
    )

    assert isinstance(receipt, CognitiveReceipt)
    assert receipt.success is True
    assert "Processed 512 tokens" in receipt.payload["result"]
    assert len(receipt.signature) == 64  # SHA-256 hash
    assert len(bridge.tier4_ledger) == 1
    assert bridge.tier4_ledger[0].signature == receipt.signature


def test_cognitive_snapshot_export(bridge):
    """Test full planetary cognitive snapshot export."""
    bridge.establish_charter("Test Goal")
    bridge.plan_macro_milestones([{"title": "Step 1"}])
    bridge.execute_micro_step("ping", {}, lambda p: "pong")

    snapshot = bridge.export_cognitive_snapshot()

    assert snapshot["agent_id"] == "test_agent_0"
    assert snapshot["ledger_size"] == 1
    assert len(snapshot["ledger_hashes"]) == 1
    assert snapshot["charter"]["charter"] == "Test Goal"
