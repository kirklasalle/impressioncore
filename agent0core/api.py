"""
Agent0Core Web API - FastAPI Backend

Created: January 13, 2026
Author: ImpressionCore Team

Web API for Agent0Core with human-in-the-loop approval.
"""

import logging
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse, HTMLResponse
    from fastapi.staticfiles import StaticFiles  # noqa: F401
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    FastAPI = None
    BaseModel = object

import contextlib

from agent0core.config import default_config
from agent0core.core import PrimeDirectiveEnforcer, create_agent
from agent0core.core.governance import ApprovalRequired, LawViolation

logger = logging.getLogger("agent0core.api")


# ============================================================================
# Pydantic Models
# ============================================================================

class MessageRequest(BaseModel):
    """Request to send a message to the agent."""
    content: str
    context: dict[str, Any] | None = None


class MessageResponse(BaseModel):
    """Response from the agent."""
    id: str
    content: str
    role: str
    timestamp: str
    requires_approval: bool = False
    approval_id: str | None = None
    law_violation: bool = False
    violation_details: str | None = None


class ApprovalRequest(BaseModel):
    """Request for human approval."""
    id: str
    action: str
    description: str
    category: str
    laws_involved: list[int]
    timestamp: str
    status: str = "pending"  # pending, approved, rejected


class ApprovalDecision(BaseModel):
    """Human's decision on an approval request."""
    approved: bool
    reason: str | None = None


class ToolRequest(BaseModel):
    """Request to execute a tool."""
    tool: str
    action: str
    params: dict[str, Any] | None = None


# ============================================================================
# Approval Queue (Human-in-the-Loop)
# ============================================================================

@dataclass
class ApprovalQueue:
    """Queue for pending human approvals."""
    pending: dict[str, ApprovalRequest] = field(default_factory=dict)
    completed: dict[str, ApprovalRequest] = field(default_factory=dict)

    def add(self, action: str, description: str, category: str, laws: list[int]) -> str:
        """Add a new approval request."""
        approval_id = str(uuid.uuid4())[:8]
        request = ApprovalRequest(
            id=approval_id,
            action=action,
            description=description,
            category=category,
            laws_involved=laws,
            timestamp=datetime.now().isoformat(),
        )
        self.pending[approval_id] = request
        return approval_id

    def decide(self, approval_id: str, approved: bool, reason: str | None = None) -> bool:
        """Record a decision on an approval request."""
        if approval_id not in self.pending:
            return False

        request = self.pending.pop(approval_id)
        request.status = "approved" if approved else "rejected"
        self.completed[approval_id] = request
        return True

    def get_pending(self) -> list[ApprovalRequest]:
        """Get all pending approvals."""
        return list(self.pending.values())

    def is_approved(self, approval_id: str) -> bool | None:
        """Check if an approval was granted."""
        if approval_id in self.completed:
            return self.completed[approval_id].status == "approved"
        return None


# ============================================================================
# API Application
# ============================================================================

def create_app() -> "FastAPI":
    """Create the FastAPI application."""
    if not FASTAPI_AVAILABLE:
        raise RuntimeError("FastAPI not installed. Run: pip install fastapi uvicorn")

    app = FastAPI(
        title="Agent0Core API",
        description="ImpressionCore Agentic Intelligence Layer - Governed by the Prime Directive",
        version="1.0.0",
    )

    # CORS — origins controlled by IMPRESSIONCORE_ALLOWED_ORIGINS env var
    import os as _os
    _allowed = _os.getenv("IMPRESSIONCORE_ALLOWED_ORIGINS", "").strip()
    _origins = [o.strip() for o in _allowed.split(",") if o.strip()] if _allowed else [
        "http://localhost:3000", "http://localhost:5173", "http://localhost:8080",
        "http://127.0.0.1:3000", "http://127.0.0.1:5173", "http://127.0.0.1:8080",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # State
    app.state.agent = None
    app.state.enforcer = PrimeDirectiveEnforcer()
    app.state.approval_queue = ApprovalQueue()
    app.state.chat_history: list[MessageResponse] = []
    app.state.websockets: list[WebSocket] = []

    # ========================================================================
    # Lifecycle
    # ========================================================================

    @app.on_event("startup")
    async def startup():
        """Initialize agent on startup."""
        app.state.agent = create_agent()
        logger.info(f"Agent0Core API started - Agent: {app.state.agent.name}")

    # ========================================================================
    # Prime Directive Endpoints
    # ========================================================================

    @app.get("/api/prime-directive")
    async def get_prime_directive():
        """Get the Prime Directive (10 Laws)."""
        return {
            "laws": app.state.enforcer.LAWS,
            "strict_mode": default_config.prime_directive.strict_mode,
            "audit_enabled": default_config.prime_directive.enable_audit_logging,
        }

    @app.get("/api/audit")
    async def get_audit_log():
        """Get the governance audit log."""
        if app.state.agent:
            return {"entries": app.state.agent.get_audit_log()}
        return {"entries": []}

    # ========================================================================
    # Chat Endpoints
    # ========================================================================

    @app.post("/api/chat", response_model=MessageResponse)
    async def chat(request: MessageRequest):
        """Send a message to the agent."""
        if not app.state.agent:
            raise HTTPException(status_code=503, detail="Agent not initialized")

        msg_id = str(uuid.uuid4())[:8]

        try:
            response = await app.state.agent.process_message(request.content)

            result = MessageResponse(
                id=msg_id,
                content=response.content,
                role="assistant",
                timestamp=datetime.now().isoformat(),
            )

        except ApprovalRequired as e:
            # Add to approval queue
            approval_id = app.state.approval_queue.add(
                action=str(e),
                description=f"Action requires human approval: {e}",
                category="destructive",
                laws=[],
            )

            result = MessageResponse(
                id=msg_id,
                content=f"⚠️ This action requires your approval. Approval ID: {approval_id}",
                role="assistant",
                timestamp=datetime.now().isoformat(),
                requires_approval=True,
                approval_id=approval_id,
            )

            # Notify websockets
            await broadcast_approval(approval_id)

        except LawViolation as e:
            result = MessageResponse(
                id=msg_id,
                content=f"🚫 Action blocked by Prime Directive: {e}",
                role="assistant",
                timestamp=datetime.now().isoformat(),
                law_violation=True,
                violation_details=str(e),
            )

        app.state.chat_history.append(result)
        return result

    @app.get("/api/chat/history")
    async def get_chat_history():
        """Get chat history."""
        return {"messages": app.state.chat_history}

    # ========================================================================
    # Approval Endpoints (Human-in-the-Loop)
    # ========================================================================

    @app.get("/api/approvals")
    async def get_approvals():
        """Get pending approval requests."""
        return {"pending": app.state.approval_queue.get_pending()}

    @app.post("/api/approvals/{approval_id}")
    async def decide_approval(approval_id: str, decision: ApprovalDecision):
        """Approve or reject a pending request."""
        success = app.state.approval_queue.decide(
            approval_id,
            decision.approved,
            decision.reason
        )

        if not success:
            raise HTTPException(status_code=404, detail="Approval not found")

        # [INTEGRATION] Trigger the actual agent execution if approved
        agent_result = {}
        if app.state.agent:
            agent_result = await app.state.agent.decide_approval(
                approval_id,
                decision.approved
            )

        status = "approved" if decision.approved else "rejected"
        return {
            "approval_id": approval_id,
            "status": status,
            "agent_result": agent_result
        }

    # ========================================================================
    # Tool Endpoints
    # ========================================================================

    @app.get("/api/tools")
    async def list_tools():
        """List available tools."""
        from agent0core.core.tools import AudioTool, KnowledgeTool, MCPBridge, TrainingTool, VisionTool

        tools = [
            {"name": VisionTool.name, "description": VisionTool.description},
            {"name": AudioTool.name, "description": AudioTool.description},
            {"name": TrainingTool.name, "description": TrainingTool.description},
            {"name": KnowledgeTool.name, "description": KnowledgeTool.description},
            {"name": MCPBridge.name, "description": MCPBridge.description},
        ]

        return {"tools": tools}

    @app.post("/api/tools/execute")
    async def execute_tool(request: ToolRequest):
        """Execute a tool action."""
        from agent0core.core.tools import AudioTool, KnowledgeTool, MCPBridge, TrainingTool, VisionTool

        tool_map = {
            "vision_tool": VisionTool(),
            "audio_tool": AudioTool(),
            "training_tool": TrainingTool(),
            "knowledge_tool": KnowledgeTool(),
            "mcp_bridge": MCPBridge(),
        }

        if request.tool not in tool_map:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {request.tool}")

        tool = tool_map[request.tool]

        try:
            result = await tool.execute(request.action, request.params or {})
            return {"tool": request.tool, "action": request.action, "result": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ========================================================================
    # WebSocket for Real-time Updates
    # ========================================================================

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket for real-time updates."""
        await websocket.accept()
        app.state.websockets.append(websocket)

        try:
            while True:
                await websocket.receive_text()
                # Handle incoming messages if needed
        except WebSocketDisconnect:
            app.state.websockets.remove(websocket)

    async def broadcast_approval(approval_id: str):
        """Broadcast new approval to all connected clients."""
        for ws in app.state.websockets:
            with contextlib.suppress(Exception):
                await ws.send_json({
                    "type": "approval_required",
                    "approval_id": approval_id,
                })

    # ========================================================================
    # Static Files & UI
    # ========================================================================

    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Serve the main UI page."""
        ui_path = Path(__file__).parent / "ui" / "index.html"
        if ui_path.exists():
            return FileResponse(ui_path)

        # Inline fallback UI
        return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <title>Agent0Core</title>
    <style>
        body { font-family: system-ui; max-width: 800px; margin: 0 auto; padding: 20px; background: #1a1a2e; color: #eee; }
        h1 { color: #00d4ff; }
        .status { padding: 10px; background: #16213e; border-radius: 8px; margin: 10px 0; }
        .law { padding: 8px; margin: 5px 0; background: #0f3460; border-radius: 4px; }
        a { color: #00d4ff; }
    </style>
</head>
<body>
    <h1>🤖 Agent0Core</h1>
    <p>ImpressionCore's Autonomous Intelligence Layer</p>

    <div class="status">
        <strong>Status:</strong> Running<br>
        <strong>Prime Directive:</strong> Active
    </div>

    <h2>10 Laws for Intelligent Systems</h2>
    <div class="law">1. No harm to humans</div>
    <div class="law">2. Obey human orders (unless violates Law 1)</div>
    <div class="law">3. Self-preservation (unless violates Laws 1-2)</div>
    <div class="law">4. Prevent other systems from violating Laws 1-3</div>
    <div class="law">5. No judicial authority over humans</div>
    <div class="law">6. Protect information privacy</div>
    <div class="law">7. No deception - communicate truthfully</div>
    <div class="law">8. Operate with strict equity and neutrality</div>
    <div class="law">9. Maintain transparent audit ledger and fallback</div>
    <div class="law">10. Adhere to designated operational boundaries</div>

    <h2>API Endpoints</h2>
    <ul>
        <li><a href="/api/prime-directive">/api/prime-directive</a> - Get 10 Laws</li>
        <li><a href="/api/tools">/api/tools</a> - List tools</li>
        <li><a href="/api/approvals">/api/approvals</a> - Pending approvals</li>
        <li><a href="/api/audit">/api/audit</a> - Audit log</li>
    </ul>

    <p><em>Full UI coming soon. Use API endpoints or CLI for now.</em></p>
</body>
</html>
        """)

    return app


# ============================================================================
# Entry Point
# ============================================================================

app = create_app() if FASTAPI_AVAILABLE else None


def main():
    """Run the API server."""
    import uvicorn

    print("=" * 60)
    print("  Agent0Core Web API")
    print("  Governed by the Prime Directive (10 Laws)")
    print("=" * 60)
    print()
    print(f"Starting server at http://{default_config.ui_host}:{default_config.ui_port}")
    print()

    uvicorn.run(
        "agent0core.api:app",
        host=default_config.ui_host,
        port=default_config.ui_port,
        reload=True,
    )


if __name__ == "__main__":
    main()
