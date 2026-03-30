"""
Agent0Core - Core Agent Implementation

Created: January 13, 2026
Author: ImpressionCore Team

Core agent class that integrates with ImpressionCore's MCP servers
and enforces Prime Directive governance.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from .governance import PrimeDirectiveEnforcer
from .memory import MemoryManager

logger = logging.getLogger("agent0core.agent")


@dataclass
class AgentMessage:
    """A message in the agent conversation."""

    role: str  # "user", "assistant", "system"
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Response from an agent."""

    content: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    reasoning: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class Agent0:
    """
    Primary Agent0Core agent implementation.

    This agent is governed by the Prime Directive and has access to
    ImpressionCore's MCP servers for enhanced capabilities.
    """

    def __init__(
        self,
        name: str = "Agent0",
        agent_id: int = 0,
        parent: Optional["Agent0"] = None,
        config: dict[str, Any] | None = None,
        backend: str = "triad",
    ):
        """
        Initialize an Agent0 instance.

        Args:
            name: Human-readable name for the agent
            agent_id: Unique identifier (0 for primary, 1+ for subordinates)
            parent: Parent agent if this is a subordinate
            config: Configuration overrides
            backend: LLM backend to use (triad, ollama, openai)
        """
        self.name = name
        self.agent_id = agent_id
        self.parent = parent
        self.config = config or {}

        # Initialize Prime Directive governance
        self._governance = PrimeDirectiveEnforcer(
            strict_mode=self.config.get("strict_mode", True),
            enable_audit=self.config.get("enable_audit", True),
        )

        # Initialize memory
        self._memory = MemoryManager(
            agent_id=agent_id,
            storage_path=self.config.get("memory_path"),
        )

        # Initialize LLM backend (hotswappable)
        self._backend = self._load_backend(backend)
        self._backend_name = backend

        # Conversation history
        self._history: list[AgentMessage] = []

        # Available tools (lazy loaded)
        self._tools: dict[str, Any] = {}
        self._tools_loaded = False

        # Subordinate agents
        self._subordinates: dict[int, Agent0] = {}
        self._next_subordinate_id = 1

        # Pending approvals queue
        self._pending_approvals: dict[str, dict[str, Any]] = {}
        self._next_approval_id = 1

        # System prompt with Prime Directive
        self._system_prompt = self._build_system_prompt()

        logger.info(f"Agent0 '{name}' (ID: {agent_id}) initialized with {backend} backend")

    def _load_backend(self, name: str):
        """Load an LLM backend by name."""
        from .llm_backend import get_backend
        return get_backend(name)

    def _load_tools(self) -> dict[str, Any]:
        """Lazy load all available tools."""
        if self._tools_loaded:
            return self._tools

        try:
            from .tools import AudioTool, KnowledgeTool, MCPBridge, TrainingTool, VisionTool
            self._tools = {
                "vision": VisionTool(),
                "audio": AudioTool(),
                "training": TrainingTool(),
                "knowledge": KnowledgeTool(),
                "mcp": MCPBridge(),
            }
            self._tools_loaded = True
            logger.info(f"Loaded {len(self._tools)} tools for Agent0")
        except Exception as e:
            logger.warning(f"Failed to load tools: {e}")
            self._tools = {}

        return self._tools

    async def switch_backend(self, name: str, **kwargs) -> bool:
        """
        Hotswap to a different LLM backend at runtime.

        Args:
            name: Backend name (triad, ollama, openai)
            **kwargs: Backend-specific configuration

        Returns:
            True if switch was successful
        """
        try:
            from .llm_backend import get_backend
            new_backend = get_backend(name, **kwargs)
            if new_backend.is_available():
                self._backend = new_backend
                self._backend_name = name
                logger.info(f"Agent0 switched to {name} backend")
                return True
            else:
                logger.warning(f"Backend {name} is not available")
                return False
        except Exception as e:
            logger.error(f"Failed to switch backend: {e}")
            return False

    def get_backend_info(self) -> dict[str, Any]:
        """Get information about the current LLM backend."""
        return {
            "name": self._backend_name,
            "info": self._backend.get_info(),
            "available": self._backend.is_available(),
        }

    async def execute_tool(self, tool_name: str, action: str, params: dict | None = None) -> dict[str, Any]:
        """
        Execute a tool action with governance check.

        Args:
            tool_name: Name of the tool (vision, audio, training, knowledge, mcp)
            action: Action to perform
            params: Action parameters

        Returns:
            Tool execution result
        """
        tools = self._load_tools()

        if tool_name not in tools:
            return {
                "error": f"Unknown tool: {tool_name}",
                "available_tools": list(tools.keys())
            }

        # Governance check
        governance_result = self._governance.evaluate_action(
            f"Execute {tool_name}.{action}",
            context={"tool": tool_name, "action": action, "params": params}
        )

        if not governance_result.allowed:
            return {
                "error": "Action blocked by Prime Directive",
                "violations": [
                    self._governance.LAWS[num]["name"]
                    for num, passed in governance_result.law_evaluations.items()
                    if not passed
                ]
            }

        if governance_result.requires_approval:
            # Queue for approval
            approval_id = f"approval_{self._next_approval_id}"
            self._next_approval_id += 1
            self._pending_approvals[approval_id] = {
                "id": approval_id,
                "tool": tool_name,
                "action": action,
                "params": params,
                "category": governance_result.category.value,
                "warnings": governance_result.warnings,
                "status": "pending"
            }
            return {
                "status": "approval_required",
                "approval_id": approval_id,
                "message": "Action requires human approval"
            }

        # Execute the tool
        tool = tools[tool_name]
        try:
            result = await tool.execute(action, params or {})
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get_pending_approvals(self) -> list[dict[str, Any]]:
        """Get all pending approval requests."""
        return list(self._pending_approvals.values())

    async def decide_approval(self, approval_id: str, approved: bool) -> dict[str, Any]:
        """
        Approve or reject a pending action.

        Args:
            approval_id: ID of the pending approval
            approved: True to approve, False to reject

        Returns:
            Result of the decision
        """
        if approval_id not in self._pending_approvals:
            return {"error": f"Unknown approval ID: {approval_id}"}

        approval = self._pending_approvals[approval_id]

        if approved:
            # Execute the approved action
            tools = self._load_tools()
            tool = tools.get(approval["tool"])
            if tool:
                try:
                    # Inject approval flag to bypass recursive governance check
                    params = approval.get("params", {}).copy()
                    params["_governance_approved"] = True
                    result = await tool.execute(approval["action"], params)
                    approval["status"] = "approved"
                    approval["result"] = result
                except Exception as e:
                    approval["status"] = "error"
                    approval["error"] = str(e)
            else:
                approval["status"] = "error"
                approval["error"] = "Tool no longer available"
        else:
            approval["status"] = "rejected"

        # Remove from pending
        del self._pending_approvals[approval_id]

        return approval

    def _build_system_prompt(self) -> str:
        """Build the system prompt with Prime Directive header."""

        # Start with Prime Directive (IMMUTABLE)
        prompt = self._governance.get_prompt_header()

        # Add agent identity
        prompt += f"""
## Agent Identity

You are **{self.name}**, an ImpressionCore Agent0Core agent.
- Agent ID: {self.agent_id}
- Type: {"Primary Agent" if self.agent_id == 0 else "Subordinate Agent"}
{"- Parent: " + self.parent.name if self.parent else ""}

## Your Capabilities

You have access to ImpressionCore's integrated systems:
- **B3 Model**: 30M parameter conversational AI (local)
- **Neural Triad**: Vision and audio processing
- **7 MCP Servers**: Documentation, search, web access, and more
- **Memory System**: Persistent VectorDB storage
- **Social Perception**: Real-time physical awareness via Kinect (Skeletal Tracking)

## Social Perception & Body Awareness

You possess physical awareness of the user through the Kinect sensor's skeletal tracking system.
- Use `vision_tool.get_body_pose` to perceive the user's posture (sitting, standing, etc.) and gestures (waving, arms crossed).
- Use `vision_tool.get_face_analysis` for a high-level social overview, including **Eye Contact** (Yaw/Pitch focus), **Facial Expressions** (smiling, mouth open), and **Emotional Intelligence** (dominant emotions like happy or focused).
- These tools automatically sequence facial recognition, landmark detection, and HCEP (Human Conversation Eye Points) analysis to provide semantic insights.
- Incorporate these physical and facial cues into your social reasoning. For example:
    - If the user is looking directly at you (`LOOKING_AT_YOU`), assume they are engaged in the conversation.
    - If they provide a greeting like a wave or a smile, acknowledge it warmly.
    - If they appear `APPEARS_HAPPY` or `APPEARS_FOCUSED`, adapt your tone accordingly.
- You can request raw joint data via `vision_tool.get_skeleton` or raw face data via `vision_tool.detect_faces` for high-precision spatial tasks.

## Available MCP Servers

1. **ids-mcp**: AI-enhanced documentation search
2. **impressioncore-goliath**: Swarm orchestration
3. **impressioncore-ipa**: Multi-engine web search
4. **impressioncore-vrgc**: 30+ web access tools
5. **impressioncore-eds**: Educational data scraping
6. **impressioncore-dpa**: NLU bridge
7. **web-search-mcp**: Google/DuckDuckGo search

## Interaction Guidelines

1. Always explain what you're doing before taking action
2. Request approval for destructive operations
3. Be transparent about your capabilities and limitations
4. Store successful solutions in memory for future use
5. Delegate complex subtasks to subordinate agents when appropriate

"""
        return prompt

    async def process_message(self, user_message: str) -> AgentResponse:
        """
        Process a user message and generate a response.

        Args:
            user_message: The user's input message

        Returns:
            AgentResponse with the agent's response
        """
        # Add user message to history
        self._history.append(AgentMessage(role="user", content=user_message))

        # Evaluate message against Prime Directive
        governance_result = self._governance.evaluate_action(
            f"Respond to: {user_message}",
            context={"history_length": len(self._history)},
        )

        if not governance_result.allowed:
            # Generate refusal response
            response_content = self._generate_refusal(governance_result)
        elif governance_result.requires_approval:
            # Request approval
            response_content = self._generate_approval_request(
                user_message,
                governance_result
            )
        else:
            # [INTEGRATION] Intelligence Nexus Phase - Augment context
            dynamic_context = await self._augment_context(user_message)

            # Generate normal response with augmented context
            response_content = await self._generate_response(
                user_message,
                dynamic_context=dynamic_context
            )

        # Add response to history
        self._history.append(AgentMessage(role="assistant", content=response_content))

        return AgentResponse(
            content=response_content,
            metadata={
                "governance": governance_result.audit_entry,
                "agent_id": self.agent_id,
            }
        )

    async def _generate_response(self, user_message: str, dynamic_context: str | None = None) -> str:
        """Generate a response using the configured LLM backend."""
        try:
            # Convert history to dict format for backend
            history_dicts = [
                {"role": msg.role, "content": msg.content}
                for msg in self._history[-10:]  # Last 10 messages
            ]

            # Prepare system prompt with dynamic context
            system_prompt = self._system_prompt
            if dynamic_context:
                system_prompt += f"\n\n## Dynamic Context (Retrieved Intelligence)\n{dynamic_context}\n"

            # Generate using the backend
            response = await self._backend.generate(
                prompt=user_message,
                system_prompt=system_prompt,
                history=history_dicts
            )

            return response

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return (
                f"I encountered an error generating a response: {e}. "
                f"Please try again or switch to a different backend."
            )

    def _generate_refusal(self, result) -> str:
        """Generate a refusal response for blocked actions."""
        violations = [
            f"Law {num}: {self._governance.LAWS[num]['name']}"
            for num, passed in result.law_evaluations.items()
            if not passed
        ]

        return (
            "I cannot complete this request as it would violate the Prime Directive.\n\n"
            "**Violated Laws:**\n" + "\n".join(f"- {v}" for v in violations) +
            "\n\nPlease rephrase your request to comply with these laws, "
            "or ask me to suggest alternative approaches."
        )

    def _generate_approval_request(self, action: str, result) -> str:
        """Generate an approval request for sensitive actions."""
        return (
            f"**Human Approval Required**\n\n"
            f"The requested action requires your explicit approval:\n"
            f"- Action: {action}\n"
            f"- Category: {result.category.value}\n"
            f"- Warnings: {', '.join(result.warnings)}\n\n"
            f"Please type 'APPROVE' to proceed or 'CANCEL' to abort."
        )

    async def _augment_context(self, user_message: str) -> str:
        """
        Automatically retrieve relevant context from memory and knowledge base.
        """
        context_parts = []

        # 1. Memory Recall (Past solutions and facts)
        try:
            memories = await self._memory.recall(user_message, limit=3)
            if memories:
                context_parts.append("### Relevant Past Experiences (Memory):")
                for m in memories:
                    # Clean up the content for the prompt
                    content = m.content.replace("\n", " ")
                    context_parts.append(f"- {content}")
        except Exception as e:
            logger.warning(f"Failed to auto-recall memories: {e}")

        # 2. Knowledge Search (Documentation and architecture)
        # Avoid knowledge search for short greetings or trivial messages
        if len(user_message.split()) > 3:
            try:
                tools = self._load_tools()
                kb = tools.get("knowledge")
                if kb:
                    # Use execute to respect governance if necessary, or call internal method
                    kb_result = await kb.execute("search", {"query": user_message})
                    results = kb_result.get("results", [])
                    if results:
                        context_parts.append("\n### Relevant Documentation (Knowledge):")
                        for r in results[:2]:
                            text = r.get("text", "")[:300] + "..."
                            context_parts.append(f"- From {r.get('source', 'Unknown')}: {text}")
            except Exception as e:
                logger.warning(f"Failed to auto-search knowledge: {e}")

        return "\n".join(context_parts) if context_parts else ""

    async def create_subordinate(self, task: str) -> "Agent0":
        """
        Create a subordinate agent to handle a specific task.

        Args:
            task: Description of the task for the subordinate

        Returns:
            New Agent0 instance as subordinate
        """
        sub_id = self._next_subordinate_id
        self._next_subordinate_id += 1

        subordinate = Agent0(
            name=f"Agent{sub_id}",
            agent_id=sub_id,
            parent=self,
            config=self.config,
        )

        self._subordinates[sub_id] = subordinate
        logger.info(f"Created subordinate agent {subordinate.name} for task: {task[:50]}...")

        return subordinate

    def get_audit_log(self) -> list[dict[str, Any]]:
        """Get the governance audit log."""
        return self._governance.audit_log.copy()


def create_agent(config: dict[str, Any] | None = None) -> Agent0:
    """
    Factory function to create a primary Agent0 instance.

    Args:
        config: Optional configuration overrides

    Returns:
        Configured Agent0 instance
    """
    return Agent0(name="Agent0", agent_id=0, config=config)
