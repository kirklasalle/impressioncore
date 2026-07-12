import time
import uuid
from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.interfaces import api_state
from src.orchestrator.system_logger import log_event

router = APIRouter()

class Agent0ChatRequest(BaseModel):
    content: str | None = None
    message: str | None = None  # Accept both content and message for backward compatibility
    context: dict[str, Any] | None = None

class SwitchBackendRequest(BaseModel):
    backend: str
    model: str | None = None

class ExecuteToolRequest(BaseModel):
    tool: str
    action: str
    params: dict[str, Any] | None = None

class ApprovalDecisionRequest(BaseModel):
    approved: bool

class SpawnSubordinateRequest(BaseModel):
    task: str
    backend: str | None = None

class SubordinateChatRequest(BaseModel):
    message: str

def _get_active_agent():
    """Get active agent0 instance if lazy loaded."""
    api_state._lazy_load_agent0()
    return api_state.agent0_instance

@router.get("/v1/agent0/prime-directive")
async def get_agent0_prime_directive():
    """Get the Prime Directive (10 Laws for Intelligent Systems)."""
    agent = _get_active_agent()
    return {
        "status": "ACTIVE",
        "laws": api_state.PRIME_DIRECTIVE_LAWS,
        "strict_mode": True,
        "agent0_loaded": agent is not None
    }

@router.get("/v1/agent0/status")
async def get_agent0_status():
    """Get Agent0Core status for System Monitor."""
    agent = _get_active_agent()
    loaded = agent is not None
    
    if loaded:
        # Check if agent has governance/laws
        laws = getattr(agent, "LAWS", api_state.PRIME_DIRECTIVE_LAWS)
        tools_list = []
        if hasattr(agent, "_tools"):
            tools_list = list(agent._tools.keys())
        elif hasattr(agent, "_load_tools"):
            try:
                tools_list = list(agent._load_tools().keys())
            except Exception:
                pass
        if not tools_list:
            tools_list = ["vision", "audio", "training", "knowledge", "mcp"]

        return {
            "status": "ACTIVE",
            "prime_directive": "ENFORCED",
            "pending_approvals": len([a for a in api_state.agent0_approval_queue.values() if a.get("status") == "pending"]),
            "tools": tools_list,
            "audit_entries": len(api_state.agent0_audit_log),
            "laws": laws,
            "ids_status": "ONLINE" if (hasattr(agent, "_tools") and "mcp" in agent._tools) else "UNKNOWN"
        }
    else:
        return {
            "status": "OFFLINE",
            "prime_directive": "UNAVAILABLE",
            "pending_approvals": 0,
            "tools": [],
            "audit_entries": 0,
            "error": "Agent0Core not loaded"
        }

@router.post("/v1/agent0/chat")
async def agent0_chat(request: Agent0ChatRequest):
    """Send a message to Agent0Core and get a response (governed by Prime Directive)."""
    message_text = request.content or request.message
    if not message_text:
        raise HTTPException(status_code=400, detail="Message/content required")

    agent = _get_active_agent()
    msg_id = str(uuid.uuid4())[:8]

    # Log to audit queue
    api_state.agent0_audit_log.append({
        "id": msg_id,
        "type": "chat",
        "input": message_text,
        "timestamp": time.time()
    })

    if not agent:
        # Fallback to direct Triad generation if agent0 is not installed/loaded
        triad = api_state.triad_instance
        if triad:
            log_event("AGENT0", f"Fallback Chat: {message_text[:50]}...")
            result = triad.generate(
                f"[Agent0 Mode - Prime Directive Active]\n{message_text}",
                sensory_data={}
            )
            response_text = result.get("response", "I am processing your request...")
            return {
                "id": msg_id,
                "response": response_text,
                "status": "success",
                "prime_directive": "enforced"
            }
        else:
            return {
                "response": "Agent0Core is not available. Please check that the agent0core module is installed.",
                "status": "error"
            }

    try:
        # Process using real agent0core
        if hasattr(agent, "process_message"):
            response = await agent.process_message(message_text)
            log_event("AGENT0", f"Chat: {message_text[:50]}... -> {len(response.content)} chars")
            return {
                "response": response.content,
                "tool_calls": getattr(response, "tool_calls", []),
                "reasoning": getattr(response, "reasoning", ""),
                "governance": response.metadata.get("governance", {}),
                "agent_id": response.metadata.get("agent_id", 0)
            }
        else:
            return {
                "response": "Agent0Core loaded but lacks process_message capability.",
                "status": "error"
            }
    except Exception as e:
        log_event("API", f"Agent0Core chat error: {e}", level="ERROR")
        return {"error": str(e), "response": None, "governance": {}}

@router.get("/v1/agent0/telemetry")
async def get_agent0_telemetry():
    """Get comprehensive Agent0Core telemetry for System Monitor."""
    agent = _get_active_agent()
    if not agent:
        return {"status": "OFFLINE", "telemetry": {}}

    try:
        from agent0core.core.governance import get_enforcer
        enforcer = get_enforcer()

        # Tools
        from agent0core.core.tools import AudioTool, KnowledgeTool, MCPBridge, TrainingTool, VisionTool
        tools = [
            {"name": t.name, "description": t.description}
            for t in [VisionTool, AudioTool, TrainingTool, KnowledgeTool, MCPBridge]
        ]

        audit_log = agent.get_audit_log() if hasattr(agent, 'get_audit_log') else list(api_state.agent0_audit_log)
        subordinates = list(agent._subordinates.keys()) if hasattr(agent, '_subordinates') else []

        history = [
            {"role": m.role, "content": m.content[:100] + "..." if len(m.content) > 100 else m.content}
            for m in agent._history[-10:]
        ] if hasattr(agent, '_history') else []

        return {
            "status": "ACTIVE",
            "telemetry": {
                "agent_name": agent.name,
                "agent_id": agent.agent_id,
                "prime_directive": "ENFORCED",
                "pending_approvals": len([a for a in api_state.agent0_approval_queue.values() if a.get("status") == "pending"]),
                "subordinates": subordinates,
                "subordinate_count": len(subordinates),
                "tools": tools,
                "tool_count": len(tools),
                "audit_entries": len(audit_log),
                "audit_log": audit_log[-5:],
                "history_length": len(agent._history) if hasattr(agent, '_history') else 0,
                "recent_history": history,
                "laws": enforcer.LAWS
            }
        }
    except Exception as e:
        log_event("API", f"Agent0Core telemetry error: {e}", level="ERROR")
        return {"status": "ERROR", "telemetry": {}, "error": str(e)}

@router.get("/v1/agent0/backends")
async def list_agent0_backends():
    """List available LLM backends for Agent0Core."""
    try:
        from agent0core.core.llm_backend import list_backends
        backends = list_backends()
        agent = _get_active_agent()
        active = agent._backend_name if agent else "none"
        return {"backends": backends, "active": active}
    except ImportError as e:
        return {"backends": [], "error": str(e)}

@router.post("/v1/agent0/switch_backend")
async def switch_agent0_backend(request: SwitchBackendRequest):
    """Switch Agent0 to a different LLM backend at runtime."""
    agent = _get_active_agent()
    if not agent:
        return {"success": False, "error": "Agent0Core not available"}

    kwargs = {}
    if request.model:
        kwargs["model"] = request.model

    success = await agent.switch_backend(request.backend, **kwargs)
    log_event("AGENT0", f"Backend switch to {request.backend}: {'success' if success else 'failed'}")
    return {
        "success": success,
        "active_backend": agent._backend_name,
        "backend_info": agent.get_backend_info() if hasattr(agent, "get_backend_info") else {}
    }

@router.post("/v1/agent0/execute_tool")
async def execute_agent0_tool_legacy(request: ExecuteToolRequest):
    """Execute a specific tool via Agent0Core with governance check (legacy format)."""
    agent = _get_active_agent()
    if not agent:
        return {"error": "Agent0Core not available"}

    result = await agent.execute_tool(request.tool, request.action, request.params)
    log_event("AGENT0", f"Tool execution: {request.tool}.{request.action} -> {result.get('status', 'unknown')}")
    return {
        "tool": request.tool,
        "action": request.action,
        "result": result
    }

@router.get("/v1/agent0/tools")
async def list_agent0_tools():
    """List all available Agent0Core tools."""
    agent = _get_active_agent()
    if not agent:
        return {"tools": [], "status": "offline"}

    if hasattr(agent, "_load_tools"):
        tools = agent._load_tools()
        tool_info = [
            {
                "name": name,
                "description": getattr(tool, "description", "No description"),
                "available": True
            }
            for name, tool in tools.items()
        ]
    else:
        # Fallback list
        tool_info = [
            {"name": "vision_tool", "description": "Kinect/PS Eye camera control", "available": True},
            {"name": "audio_tool", "description": "Neural Triad audio engine", "available": True},
            {"name": "training_tool", "description": "B3 model training control", "available": True},
            {"name": "knowledge_tool", "description": "Document search and indexing", "available": True},
            {"name": "mcp_bridge", "description": "Bridge to 7 MCP servers", "available": True}
        ]

    return {"tools": tool_info, "count": len(tool_info), "status": "online"}

@router.post("/v1/agent0/tools/{tool_name}/execute")
async def execute_agent0_tool(tool_name: str, request_data: dict):
    """Execute an Agent0Core tool action."""
    agent = _get_active_agent()
    if not agent:
        raise HTTPException(status_code=503, detail="Agent0Core not available")

    action = request_data.get("action", "status")
    params = request_data.get("params", {})

    try:
        if hasattr(agent, "execute_tool"):
            result = await agent.execute_tool(tool_name, action, params)
            return {"tool": tool_name, "action": action, "result": result}
        
        # Fallback to local import mapping if method missing
        from agent0core.core.tools import AudioTool, KnowledgeTool, MCPBridge, TrainingTool, VisionTool
        tool_map = {
            "vision_tool": VisionTool(),
            "audio_tool": AudioTool(),
            "training_tool": TrainingTool(),
            "knowledge_tool": KnowledgeTool(),
            "mcp_bridge": MCPBridge(),
        }

        if tool_name not in tool_map:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_name}")

        tool = tool_map[tool_name]
        result = await tool.execute(action, params)
        return {"tool": tool_name, "action": action, "result": result}
    except HTTPException:
        raise
    except Exception as e:
        log_event("AGENT0", f"Tool execution error: {e}", level="ERROR")
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.get("/v1/agent0/approvals")
async def get_agent0_approvals():
    """Get pending human-in-the-loop approvals."""
    agent = _get_active_agent()
    if agent and hasattr(agent, "get_pending_approvals"):
        approvals = agent.get_pending_approvals()
        return {"pending": approvals, "count": len(approvals)}
        
    pending = [a for a in api_state.agent0_approval_queue.values() if a.get("status") == "pending"]
    return {"pending": pending, "count": len(pending)}

@router.post("/v1/agent0/approvals/{approval_id}/decide")
async def decide_approval_decide(approval_id: str, request: ApprovalDecisionRequest):
    """Approve or reject a pending Agent0Core action (via /decide route)."""
    agent = _get_active_agent()
    if agent and hasattr(agent, "decide_approval"):
        return await agent.decide_approval(approval_id, request.approved)
        
    if approval_id not in api_state.agent0_approval_queue:
        raise HTTPException(status_code=404, detail="Approval not found")

    api_state.agent0_approval_queue[approval_id]["status"] = "approved" if request.approved else "rejected"
    api_state.agent0_approval_queue[approval_id]["decided_at"] = time.time()
    log_event("AGENT0", f"Approval {approval_id}: {'APPROVED' if request.approved else 'REJECTED'}")
    return {
        "approval_id": approval_id,
        "status": "approved" if request.approved else "rejected"
    }

@router.post("/v1/agent0/approvals/{approval_id}")
async def decide_agent0_approval(approval_id: str, decision: dict):
    """Approve or reject a pending action (direct route)."""
    agent = _get_active_agent()
    approved = decision.get("approved", False)
    if agent and hasattr(agent, "decide_approval"):
        return await agent.decide_approval(approval_id, approved)

    if approval_id not in api_state.agent0_approval_queue:
        raise HTTPException(status_code=404, detail="Approval not found")

    api_state.agent0_approval_queue[approval_id]["status"] = "approved" if approved else "rejected"
    api_state.agent0_approval_queue[approval_id]["decided_at"] = time.time()
    log_event("AGENT0", f"Approval {approval_id}: {'APPROVED' if approved else 'REJECTED'}")
    return {
        "approval_id": approval_id,
        "status": "approved" if approved else "rejected"
    }

@router.post("/v1/agent0/spawn_subordinate")
async def spawn_subordinate(request: SpawnSubordinateRequest):
    """Create a subordinate agent for a specific task."""
    agent = _get_active_agent()
    if not agent:
        return {"error": "Agent0Core not available"}

    try:
        sub = await agent.create_subordinate(request.task)
        if request.backend:
            await sub.switch_backend(request.backend)

        log_event("AGENT0", f"Spawned subordinate: {sub.name} for task: {request.task[:50]}")
        return {
            "subordinate_id": sub.agent_id,
            "name": sub.name,
            "task": request.task,
            "backend": sub._backend_name
        }
    except Exception as e:
        log_event("API", f"Failed to spawn subordinate: {e}", level="ERROR")
        return {"error": str(e)}

@router.get("/v1/agent0/subordinates")
async def list_subordinates():
    """List all subordinate agents."""
    agent = _get_active_agent()
    if not agent:
        return {"subordinates": [], "error": "Agent0Core not available"}

    subs = [
        {
            "id": sub_id,
            "name": sub.name,
            "backend": sub._backend_name,
            "history_length": len(sub._history) if hasattr(sub, "_history") else 0
        }
        for sub_id, sub in agent._subordinates.items()
    ]
    return {"subordinates": subs, "count": len(subs)}

@router.post("/v1/agent0/subordinates/{sub_id}/chat")
async def chat_with_subordinate(sub_id: int, request: SubordinateChatRequest):
    """Send a message to a specific subordinate agent."""
    agent = _get_active_agent()
    if not agent:
        return {"error": "Agent0Core not available"}

    if sub_id not in agent._subordinates:
        return {"error": f"Subordinate {sub_id} not found"}

    sub = agent._subordinates[sub_id]
    response = await sub.process_message(request.message)
    return {
        "subordinate_id": sub_id,
        "subordinate_name": sub.name,
        "response": response.content,
        "governance": response.metadata.get("governance", {})
    }

@router.delete("/v1/agent0/subordinates/{sub_id}")
async def terminate_subordinate(sub_id: int):
    """Terminate a subordinate agent."""
    agent = _get_active_agent()
    if not agent:
        return {"error": "Agent0Core not available"}

    if sub_id not in agent._subordinates:
        return {"error": f"Subordinate {sub_id} not found"}

    sub_name = agent._subordinates[sub_id].name
    del agent._subordinates[sub_id]
    log_event("AGENT0", f"Terminated subordinate: {sub_name}")
    return {"status": "terminated", "subordinate_id": sub_id, "name": sub_name}

@router.get("/v1/agent0/audit")
async def get_agent0_audit():
    """Get Agent0Core audit log."""
    agent = _get_active_agent()
    audit_log = agent.get_audit_log() if (agent and hasattr(agent, 'get_audit_log')) else api_state.agent0_audit_log
    return {
        "entries": audit_log[-50:],
        "total": len(audit_log)
    }
