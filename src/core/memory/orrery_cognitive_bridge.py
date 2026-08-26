"""
Orrery Cognitive Memory Bridge for ImpressionCore & Agent0Core
Phase 9A: Multi-Tier Hierarchical Planetary Cognitive Cycles

Connects ImpressionCore multi-agent systems and Agent0Core to Orrery's 4-tier architecture:
- Tier 1: Ephemeris (Meta-Strategy, Charter & Mission Alignment)
- Tier 2: Macro-Orbit (Milestone Decomposition & Strategic Sequencing)
- Tier 3: Meso-Cycle (Tactical Tool Dispatching & Dynamic Backtracking)
- Tier 4: Micro-Step (Atomic Action Verification, Invariants & Immutable Ledger)
"""

import time
import uuid
import hashlib
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger("ImpressionCore.OrreryBridge")

@dataclass
class CognitiveReceipt:
    receipt_id: str
    tier: str
    action_name: str
    payload: Dict[str, Any]
    success: bool
    timestamp: float = field(default_factory=time.time)
    signature: str = ""

    def compute_hash(self) -> str:
        data = f"{self.receipt_id}:{self.tier}:{self.action_name}:{self.success}:{self.timestamp}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

@dataclass
class CognitiveMilestone:
    milestone_id: str
    title: str
    description: str
    status: str = "pending"  # pending | active | completed | failed
    receipts: List[CognitiveReceipt] = field(default_factory=list)

class OrreryCognitiveBridge:
    """
    Planetary cognitive cycle memory engine bridging Agent0Core to Orrery governance.
    """
    def __init__(self, agent_id: str = "agent_0", charter_goal: str = "Default Autonomous Objective"):
        self.agent_id = agent_id
        self.charter_goal = charter_goal
        self.tier1_meta_strategy = {
            "charter": charter_goal,
            "alignment_score": 1.0,
            "created_at": time.time()
        }
        self.tier2_milestones: List[CognitiveMilestone] = []
        self.tier3_meso_queue: List[Dict[str, Any]] = []
        self.tier4_ledger: List[CognitiveReceipt] = []
        self.active_milestone_idx = 0

    def establish_charter(self, goal: str, constraints: Optional[List[str]] = None):
        """Tier 1: Ephemeris Meta-Strategy establishment."""
        self.charter_goal = goal
        self.tier1_meta_strategy = {
            "charter": goal,
            "constraints": constraints or [],
            "alignment_score": 1.0,
            "established_at": time.time()
        }
        logger.info(f"[Orrery-T1] Established charter goal: {goal}")

    def plan_macro_milestones(self, milestones: List[Dict[str, str]]) -> List[CognitiveMilestone]:
        """Tier 2: Macro-Orbit milestone decomposition."""
        self.tier2_milestones = [
            CognitiveMilestone(
                milestone_id=m.get("id", str(uuid.uuid4())[:8]),
                title=m["title"],
                description=m.get("description", "")
            )
            for m in milestones
        ]
        if self.tier2_milestones:
            self.tier2_milestones[0].status = "active"
        logger.info(f"[Orrery-T2] Planned {len(self.tier2_milestones)} macro milestones.")
        return self.tier2_milestones

    def dispatch_meso_action(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Tier 3: Meso-Cycle action dispatching and queue management."""
        action_id = f"act_{uuid.uuid4().hex[:10]}"
        action_item = {
            "action_id": action_id,
            "tool_name": tool_name,
            "parameters": parameters,
            "status": "queued",
            "enqueued_at": time.time()
        }
        self.tier3_meso_queue.append(action_item)
        logger.info(f"[Orrery-T3] Enqueued meso action: {tool_name} (ID: {action_id})")
        return action_id

    def execute_micro_step(self, tool_name: str, payload: Dict[str, Any], execute_fn) -> CognitiveReceipt:
        """Tier 4: Micro-Step execution within safety envelope and ledger recording."""
        receipt_id = f"rcpt_{uuid.uuid4().hex[:12]}"
        success = False
        result_payload = {}

        try:
            # Execute underlying action function
            result = execute_fn(payload)
            success = True
            result_payload = {"result": result}
        except Exception as e:
            logger.error(f"[Orrery-T4] Action execution failed: {e}")
            result_payload = {"error": str(e)}
            success = False

        receipt = CognitiveReceipt(
            receipt_id=receipt_id,
            tier="T4_MICRO",
            action_name=tool_name,
            payload=result_payload,
            success=success
        )
        receipt.signature = receipt.compute_hash()

        # Append to immutable ledger
        self.tier4_ledger.append(receipt)

        # Attach receipt to active milestone
        if self.tier2_milestones and self.active_milestone_idx < len(self.tier2_milestones):
            self.tier2_milestones[self.active_milestone_idx].receipts.append(receipt)

        logger.info(f"[Orrery-T4] Ledgered action {tool_name} -> Success: {success} (Receipt: {receipt_id})")
        return receipt

    def complete_active_milestone(self, success: bool = True):
        """Advances Macro-Orbit active milestone."""
        if not self.tier2_milestones or self.active_milestone_idx >= len(self.tier2_milestones):
            return

        active = self.tier2_milestones[self.active_milestone_idx]
        active.status = "completed" if success else "failed"

        self.active_milestone_idx += 1
        if self.active_milestone_idx < len(self.tier2_milestones):
            self.tier2_milestones[self.active_milestone_idx].status = "active"

    def export_cognitive_snapshot(self) -> Dict[str, Any]:
        """Serializes current cognitive cycles, active orbit, and immutable ledger."""
        return {
            "agent_id": self.agent_id,
            "charter": self.tier1_meta_strategy,
            "milestones": [asdict(m) for m in self.tier2_milestones],
            "meso_queue_len": len(self.tier3_meso_queue),
            "ledger_size": len(self.tier4_ledger),
            "ledger_hashes": [r.signature for r in self.tier4_ledger[-10:]],
            "exported_at": time.time()
        }
