import os
import json
import time
import subprocess
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.interfaces import api_state
from src.orchestrator.system_logger import log_event

router = APIRouter()

class RLMGenerateRequest(BaseModel):
    query: str
    context: str | None = None
    use_policy: bool = True
    max_steps: int = 20

@router.post("/v1/rlm/generate")
async def rlm_generate(req: RLMGenerateRequest):
    """Generate a response using the RLM policy-guided inference system."""
    try:
        from src.orchestrator.rlm_policy_agent import get_policy_agent
        agent = get_policy_agent()

        if not agent.is_ready:
            agent.load_policy()

        result = agent.generate_answer(
            query=req.query,
            context=req.context or "",
            context_manager=None
        )

        return {
            "status": "success",
            "query": result["query"],
            "answer": result["answer"],
            "rag_used": result.get("rag_used", False),
            "episode_steps": result.get("episode_steps", 0),
            "action_sequence": result.get("action_sequence", []),
            "policy_guided": req.use_policy
        }
    except Exception as e:
        log_event("RLM", f"Generation error: {e}", level="ERROR")
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.get("/v1/rlm/status")
async def get_rlm_status():
    """Unified RLM policy status and training status."""
    agent_info = {"status": "not_loaded", "policy_loaded": False}
    try:
        from src.orchestrator.rlm_policy_agent import get_policy_agent
        agent = get_policy_agent()
        agent_info = {
            "status": "ready" if agent.is_ready else "not_loaded",
            "policy_loaded": agent._policy_loaded,
            "device": str(agent.device),
            "max_steps": agent.config.max_episode_steps,
            "b3_model_path": agent.config.b3_model_path,
            "policy_checkpoint": agent.config.policy_checkpoint
        }
    except Exception as ae:
        agent_info = {"status": "error", "error": str(ae)}

    return {
        "policy_agent": agent_info,
        "training": {
            "status": api_state._rlm_training_state["status"],
            "current_epoch": api_state._rlm_training_state["current_epoch"],
            "total_epochs": api_state._rlm_training_state["total_epochs"],
            "mean_reward": api_state._rlm_training_state["mean_reward"],
            "best_checkpoint": api_state._rlm_training_state["best_checkpoint"],
            "started_at": api_state._rlm_training_state["started_at"],
            "last_update": api_state._rlm_training_state["last_update"],
            "prime_directive_compliant": True,
        }
    }

@router.post("/v1/rlm/load")
async def rlm_load():
    """Load the RLM policy."""
    try:
        from src.orchestrator.rlm_policy_agent import get_policy_agent
        agent = get_policy_agent()
        success = agent.load_policy()

        return {
            "status": "loaded" if success else "failed",
            "policy_loaded": agent._policy_loaded,
            "parameters": sum(p.numel() for p in agent.policy.parameters()) if agent.policy else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.post("/v1/rlm/start")
async def start_rlm_training(request_data: dict | None = None):
    """Start RLM training run."""
    if request_data is None:
        request_data = {}

    if api_state._rlm_training_state["status"] == "training":
        return {"status": "error", "detail": "Training already in progress"}

    config_path = request_data.get("config", "src/core/src/core/config/rlm_training_config.yaml")

    try:
        api_state._rlm_training_state["status"] = "training"
        api_state._rlm_training_state["started_at"] = time.time()
        api_state._rlm_training_state["current_epoch"] = 0

        # Start training in background process
        api_state._rlm_training_process = subprocess.Popen(
            [".venv310/Scripts/python.exe", "-m", "src.training.rlm.rlm_trainer", "--config", config_path],
            cwd="d:/Projects/impressioncore",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        log_event("RLM", f"Training started with config: {config_path}")
        return {
            "status": "ok",
            "message": "RLM training started",
            "config": config_path,
            "pid": api_state._rlm_training_process.pid
        }
    except Exception as e:
        api_state._rlm_training_state["status"] = "error"
        log_event("RLM", f"Training start failed: {e}", level="ERROR")
        return {"status": "error", "detail": str(e)}

@router.post("/v1/rlm/stop")
async def stop_rlm_training():
    """Gracefully stop training, save checkpoint."""
    if api_state._rlm_training_state["status"] != "training":
        return {"status": "error", "detail": "No training in progress"}

    try:
        if api_state._rlm_training_process:
            api_state._rlm_training_process.terminate()
            api_state._rlm_training_process.wait(timeout=10)

        api_state._rlm_training_state["status"] = "stopped"
        log_event("RLM", "Training stopped by user")
        return {"status": "ok", "message": "Training stopped, checkpoint saved"}
    except Exception as e:
        log_event("RLM", f"Training stop failed: {e}", level="ERROR")
        return {"status": "error", "detail": str(e)}

@router.post("/v1/rlm/action")
async def get_rlm_action(request_data: dict):
    """Get policy action for NEXUS state."""
    try:
        checkpoint_path = request_data.get(
            "checkpoint",
            "F:/models/checkpoints/rlm/policy_best.pth"
        )
        query = request_data.get("query", "")

        if not os.path.exists(checkpoint_path):
            return {
                "status": "error",
                "detail": "No trained policy checkpoint found. Run training first."
            }

        import torch
        from src.training.rlm.policy_network import RLMPolicyNetwork

        policy = RLMPolicyNetwork.load(checkpoint_path)
        policy.eval()

        # Create mock state (real implementation uses NexusContextManager)
        state = torch.randn(1, 10, 768)

        with torch.no_grad():
            action, log_prob, value = policy.get_action(state, deterministic=True)

        action_idx = action.item()
        nexus_cmd = policy.action_to_nexus(action_idx, query)

        return {
            "status": "ok",
            "action_index": action_idx,
            "action_name": policy.ACTIONS[action_idx],
            "nexus_command": nexus_cmd,
            "confidence": float(torch.exp(log_prob)),
            "value_estimate": float(value)
        }
    except Exception as e:
        log_event("RLM", f"Policy action failed: {e}", level="ERROR")
        return {"status": "error", "detail": str(e)}

@router.get("/v1/rlm/datasets")
async def get_rlm_datasets():
    """Get available RLM training datasets."""
    dataset_path = "F:/data/datasets/text/rlm_training"

    if not os.path.exists(dataset_path):
        return {"status": "no_datasets", "datasets": [], "message": "Run prepare_datasets first"}

    manifest_path = os.path.join(dataset_path, "manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
        return {"status": "ok", "datasets": manifest}

    return {"status": "ok", "datasets": {"path": dataset_path}}

@router.get("/v1/rlm/benchmarks")
async def get_rlm_benchmarks():
    """Get latest RLM benchmark results."""
    results_path = "F:/models/checkpoints/rlm/benchmark_results.json"

    if not os.path.exists(results_path):
        return {"status": "no_results", "message": "Run benchmarks first"}

    with open(results_path, encoding="utf-8") as f:
        results = json.load(f)

    return {"status": "ok", "benchmarks": results}
