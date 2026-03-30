"""
RLM Policy Agent - Bridges trained policy with NexusInterpreter

Created: January 21, 2026
Author: ImpressionCore Team
Tags: #rlm #policy #nexus #agent

This module provides the runtime integration between the trained RLM policy
and the NEXUS interpreter, enabling policy-guided context folding.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import torch

logger = logging.getLogger("NEXUS.RLM.PolicyAgent")


@dataclass
class PolicyAgentConfig:
    """Configuration for the RLM Policy Agent."""
    policy_checkpoint: str = "F:/models/checkpoints/rlm/policy_best.pth"
    b3_model_path: str = "F:/models/checkpoints/b3_conversational/b3_conv_epoch_final.pt"
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    max_episode_steps: int = 20
    deterministic: bool = True  # Use argmax vs sampling
    fallback_action: str = "ANSWER"  # Action when policy unavailable
    use_rag: bool = True  # Enable RAG-enhanced inference


class RLMPolicyAgent:
    """
    Agent that uses a trained RLM policy to guide context folding.

    Actions (from policy):
    - CONTEXT-CHUNK: Split and process context in chunks
    - CONTEXT-SEARCH: Search for relevant information
    - RECURSION-DEPTH: Go deeper with sub-queries
    - LLM-QUERY: Query the LLM with current context
    - CONTINUE: Keep processing
    - ANSWER: Generate final answer
    """

    # Action mapping (MUST match policy_network.py exactly!)
    ACTIONS = [
        "CONTEXT-CHUNK",      # 0
        "CONTEXT-SEARCH",     # 1
        "LLM-QUERY LEFT",     # 2
        "LLM-QUERY RIGHT",    # 3
        "LLM-QUERY COLOSSUS", # 4
        "PIPELINE",           # 5
        "PARALLEL",           # 6
        "CONTEXT-LOAD",       # 7
        "RECURSION-DEPTH",    # 8
        "SUMMARIZE",          # 9
        "ANSWER",             # 10
        "CONTINUE",           # 11
    ]

    _instance: Optional['RLMPolicyAgent'] = None

    def __new__(cls, *args, **kwargs):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: PolicyAgentConfig | None = None):
        if self._initialized:
            return

        self.config = config or PolicyAgentConfig()
        self.policy = None
        self.encoder = None
        self.device = self.config.device

        # B3 inference system (lazy loaded)
        self._b3_inference = None

        # RAG searcher (lazy loaded)
        self._rag_searcher = None

        # Episode state
        self.current_step = 0
        self.action_history: list[str] = []
        self.state_history: list[torch.Tensor] = []

        self._initialized = True
        self._policy_loaded = False

        logger.info("RLMPolicyAgent initialized")

    def load_policy(self, checkpoint_path: str | None = None) -> bool:
        """
        Load the trained policy network.

        Args:
            checkpoint_path: Override config checkpoint path

        Returns:
            True if loaded successfully
        """
        path = checkpoint_path or self.config.policy_checkpoint

        if not Path(path).exists():
            logger.warning(f"Policy checkpoint not found: {path}")
            return False

        try:
            # Import here to avoid circular imports
            from src.training.rlm.policy_network import RLMPolicyNetwork
            from src.training.rlm.state_encoder import RLMStateEncoder

            # Load policy
            self.policy = RLMPolicyNetwork.load(path, self.device)
            self.policy.eval()

            # Load encoder
            self.encoder = RLMStateEncoder()

            self._policy_loaded = True
            logger.info(f"Policy loaded from {path}")
            logger.info(f"  Parameters: {sum(p.numel() for p in self.policy.parameters()):,}")

            return True

        except Exception as e:
            logger.error(f"Failed to load policy: {e}")
            return False

    def reset_episode(self):
        """Reset episode state for a new query."""
        self.current_step = 0
        self.action_history = []
        self.state_history = []

    def get_action(
        self,
        query: str,
        context: str,
        context_manager: Any = None
    ) -> tuple[str, dict[str, Any]]:
        """
        Get the next action from the policy.

        Args:
            query: User query
            context: Current context string
            context_manager: Optional RLMContextManager for stats

        Returns:
            (action_name, action_metadata)
        """
        # Check step limit
        if self.current_step >= self.config.max_episode_steps:
            logger.info(f"Max steps reached ({self.config.max_episode_steps}), forcing ANSWER")
            return "ANSWER", {"reason": "max_steps_reached"}

        # Fallback if policy not loaded
        if not self._policy_loaded or self.policy is None:
            logger.debug("Policy not loaded, using fallback")
            return self.config.fallback_action, {"reason": "policy_unavailable"}

        try:
            # Get state inputs from context manager
            state_inputs = self.encoder.from_context_manager(
                context_manager=context_manager,
                query=query,
                action_history=self.action_history,
                embedder=None  # We embed manually below
            )

            # Embed text using SentenceTransformer (lazy load if needed)
            if self._rag_searcher is None:
                self._get_rag_searcher()

            if self._rag_searcher:
                # Use searcher's internal embedding model if accessible, or creating one is expensive
                # For now we'll assume we can use a lightweight one or sharing B3's
                # To be proper, we should use a consistent encoder.
                # Let's try to reuse the one from _retrieve_rag_context logic
                 from sentence_transformers import SentenceTransformer
                 embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=self.device)
            else:
                 # Fallback cpu embedder
                 from sentence_transformers import SentenceTransformer
                 embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")

            # Helper to embed
            def embed(text):
                if not text:
                    return torch.zeros(1, 1, 768, device=self.device)
                vec = embedder.encode(text, convert_to_tensor=True, show_progress_bar=False)
                # Ensure 768 dim (MiniLM is 384, we might need projection or use compatible model)
                # Wait, generic B3 model is 768. MiniLM is 384. Mismatch!
                # We need a 768 dim embedder or project it.
                # Using 'all-mpnet-base-v2' gives 768 dimensions.
                return vec.reshape(1, 1, -1)

            # Re-init embedder with 768-dim model if we picked the wrong one above
            # Optimally this should be an attribute of the agent
            if not hasattr(self, '_embedder_model'):
                self._embedder_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2", device=self.device)

            ctx_emb = self._embedder_model.encode(state_inputs['context_text'], convert_to_tensor=True).reshape(1, 1, -1)
            qry_emb = self._embedder_model.encode(state_inputs['query'], convert_to_tensor=True).reshape(1, 1, -1)

            # Prepare other inputs
            metadata = state_inputs['metadata']
            action_hist = torch.tensor([state_inputs['action_indices']], device=self.device)

            # Encode state
            state = self.encoder(
                context_embedding=ctx_emb,
                query_embedding=qry_emb,
                metadata=metadata,
                action_history=action_hist
            )

            # Get action from policy
            with torch.no_grad():
                action_idx, log_prob, value = self.policy.get_action(
                    state,
                    deterministic=self.config.deterministic
                )

            action_name = self.ACTIONS[action_idx.item()]

            # Update episode state
            self.current_step += 1
            self.action_history.append(action_name)
            self.state_history.append(state.cpu())

            metadata = {
                "step": self.current_step,
                "action_idx": action_idx.item(),
                "log_prob": log_prob.item() if log_prob is not None else None,
                "value": value.item() if value is not None else None,
                "history": self.action_history.copy()
            }

            logger.debug(f"Step {self.current_step}: {action_name}")

            return action_name, metadata

        except Exception as e:
            logger.error(f"Policy inference failed: {e}")
            return self.config.fallback_action, {"reason": f"error: {e}"}

    def execute_action(
        self,
        action: str,
        query: str,
        context_manager: Any,
        interpreter: Any = None
    ) -> tuple[Any, bool]:
        """
        Execute the policy action using NEXUS commands.

        Args:
            action: Action name from get_action
            query: User query
            context_manager: RLMContextManager instance
            interpreter: Optional NexusInterpreter for advanced ops

        Returns:
            (result, is_terminal) - result and whether episode is done
        """
        is_terminal = False
        result = None

        if action == "CONTEXT-CHUNK":
            # Chunk the context for processing
            chunks = context_manager.chunk_context(
                chunk_size=4000,
                overlap=200,
                by="paragraphs"
            )
            result = {
                "action": "chunk",
                "num_chunks": len(chunks),
                "chunk_preview": [c[:100] + "..." for c in chunks[:3]]
            }

        elif action == "CONTEXT-SEARCH":
            # Search for query-relevant content
            key_terms = [w for w in query.split() if len(w) > 3][:5]
            search_pattern = "|".join(key_terms) if key_terms else query[:50]

            results = context_manager.search_context(
                pattern=search_pattern,
                is_regex=True,
                max_results=5
            )
            result = {
                "action": "search",
                "pattern": search_pattern,
                "num_results": len(results),
                "matches": results
            }

        elif action == "CONTEXT-LOAD":
            # Load additional context
            result = {
                "action": "context_load",
                "current_contexts": context_manager.list_contexts()
            }

        elif action in ("LLM-QUERY LEFT", "LLM-QUERY RIGHT", "LLM-QUERY COLOSSUS"):
            # Trigger actual LLM inference using B3RAGInference
            llm_result = self._generate_with_b3(query, context_manager)
            result = {
                "action": "llm_query",
                "target": action.replace("LLM-QUERY ", "").lower(),
                "status": "complete",
                "query": query[:100],
                "response": llm_result.get("response", ""),
                "rag_used": llm_result.get("rag_used", False)
            }

        elif action == "PIPELINE":
            # Execute sequential operations
            result = {
                "action": "pipeline",
                "step": self.current_step
            }

        elif action == "PARALLEL":
            # Execute parallel operations
            result = {
                "action": "parallel",
                "step": self.current_step
            }

        elif action == "RECURSION-DEPTH":
            # Begin a recursive sub-query
            success, msg = context_manager.begin_recursive_call(
                target="sub_query",
                prompt=query
            )
            result = {
                "action": "recurse",
                "success": success,
                "depth": context_manager.get_recursion_depth(),
                "message": msg
            }

        elif action == "SUMMARIZE":
            # Summarize current context
            active_ctx = context_manager.get_active_context() or ""
            result = {
                "action": "summarize",
                "context_length": len(active_ctx),
                "preview": active_ctx[:200] + "..." if len(active_ctx) > 200 else active_ctx
            }

        elif action == "CONTINUE":
            # Keep processing - no specific operation
            result = {
                "action": "continue",
                "step": self.current_step
            }

        elif action == "ANSWER":
            # Generate final answer
            is_terminal = True
            result = {
                "action": "answer",
                "steps_taken": self.current_step,
                "action_history": self.action_history
            }

        else:
            logger.warning(f"Unknown action: {action}")
            result = {"action": "unknown", "raw": action}

        return result, is_terminal

    def run_episode(
        self,
        query: str,
        context: str,
        context_manager: Any,
        interpreter: Any = None
    ) -> dict[str, Any]:
        """
        Run a complete episode to answer a query.

        Args:
            query: User query
            context: Initial context
            context_manager: RLMContextManager instance
            interpreter: Optional NexusInterpreter

        Returns:
            Episode results including answer, steps, and metrics
        """
        self.reset_episode()

        # Load context into manager if not already done
        context_manager.load_context_from_string(context, "query_context")

        episode_results = {
            "query": query,
            "steps": [],
            "terminal_action": None,
            "total_steps": 0,
            "success": False
        }

        while self.current_step < self.config.max_episode_steps:
            # Get action from policy
            action, metadata = self.get_action(
                query=query,
                context=context_manager.get_active_context() or context,
                context_manager=context_manager
            )

            # Execute action
            result, is_terminal = self.execute_action(
                action=action,
                query=query,
                context_manager=context_manager,
                interpreter=interpreter
            )

            episode_results["steps"].append({
                "action": action,
                "metadata": metadata,
                "result": result
            })

            if is_terminal:
                episode_results["terminal_action"] = action
                episode_results["success"] = True
                break

        episode_results["total_steps"] = self.current_step

        # Clean up
        context_manager.reset_recursion()

        logger.info(f"Episode complete: {self.current_step} steps, terminal={episode_results['terminal_action']}")

        return episode_results

    def _get_b3_inference(self):
        """Lazy load B3 model for inference."""
        if self._b3_inference is None:
            try:
                import torch
                from transformers import AutoTokenizer

                from src.core.models.impressioncore_b3_architecture import B3Config, ImpressionCoreB3Model

                # Load tokenizer
                tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-small')
                tokenizer.pad_token = tokenizer.eos_token

                # Create model with correct config for step_1000.pt
                config = B3Config()  # Uses 768 hidden_dim by default
                model = ImpressionCoreB3Model(config)

                # Load checkpoint
                checkpoint = torch.load(self.config.b3_model_path, map_location=self.device)

                # Handle different checkpoint formats
                if isinstance(checkpoint, dict):
                    state_dict = checkpoint.get('model_state_dict') or checkpoint.get('model') or checkpoint
                    model.load_state_dict(state_dict, strict=False)

                model = model.to(self.device)
                model.eval()

                self._b3_inference = {
                    'model': model,
                    'tokenizer': tokenizer,
                    'config': config
                }

                param_count = sum(p.numel() for p in model.parameters())
                logger.info(f"B3 Model loaded: {param_count:,} parameters")

            except Exception as e:
                logger.warning(f"Failed to load B3 model: {e}")
                import traceback
                traceback.print_exc()
                self._b3_inference = None
        return self._b3_inference

    def _get_rag_searcher(self):
        """Lazy load RAG embedding searcher."""
        if self._rag_searcher is None:
            try:
                from src.inference.b3_rag_infrastructure import B3EmbeddingSearcher

                self._rag_searcher = B3EmbeddingSearcher(
                    f_data_root="F:/data",
                    use_faiss=True,
                    topk=5,
                    score_threshold=0.01,
                    use_sentence_transformers=True
                )

                # Load embeddings
                self._rag_searcher.load_multimodal_embeddings()
                self._rag_searcher.load_b3_embeddings(category="educational")

                logger.info("RAG searcher loaded with embeddings")

            except Exception as e:
                logger.warning(f"Failed to load RAG searcher: {e}")
                self._rag_searcher = None
        return self._rag_searcher

    def _retrieve_rag_context(self, query: str, topk: int = 3) -> str:
        """Retrieve relevant context using RAG embeddings."""
        searcher = self._get_rag_searcher()
        if searcher is None:
            return ""

        try:
            from sentence_transformers import SentenceTransformer

            # Encode query
            encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            query_embedding = encoder.encode(query, normalize_embeddings=True)

            # Search in educational embeddings (384-dim)
            if "educational" in searcher.embeddings:
                embeddings = searcher.embeddings["educational"]
                index = searcher.indices.get("educational")

                if index is not None:
                    query_vec = query_embedding.reshape(1, -1).astype('float32')

                    # Check dimension compatibility
                    if query_vec.shape[1] == embeddings.shape[1]:
                        distances, indices = index.search(query_vec, topk)

                        # Build context from retrieved docs
                        context_parts = []
                        for idx in indices[0]:
                            if idx >= 0 and idx < len(searcher.mappings.get("educational", {})):
                                doc_id = searcher.mappings["educational"].get(int(idx), f"doc_{idx}")
                                context_parts.append(f"[Retrieved: {doc_id}]")

                        if context_parts:
                            return "\n".join(context_parts)

            return ""

        except Exception as e:
            logger.warning(f"RAG retrieval failed: {e}")
            return ""


    def _generate_with_b3(
        self,
        query: str,
        context_manager: Any
    ) -> dict[str, Any]:
        """
        Generate response using ImpressionCoreB3Model.

        Args:
            query: User query
            context_manager: RLMContextManager with loaded context

        Returns:
            Dict with response and metadata
        """
        b3 = self._get_b3_inference()

        if b3 is None:
            # Fallback to simple response
            context = context_manager.get_active_context() or ""
            return {
                "response": f"Based on the context, regarding '{query}': {context[:200]}...",
                "rag_used": False,
                "fallback": True
            }

        try:
            import torch
            import torch.nn.functional as F

            model = b3['model']
            tokenizer = b3['tokenizer']

            # Build prompt with context
            # 1. Get explicit context
            explicit_context = context_manager.get_active_context() or ""

            # 2. Retrieve RAG context
            rag_context = self._retrieve_rag_context(query)
            rag_used = bool(rag_context)

            # 3. Combine contexts
            full_context = f"{explicit_context}\n\n{rag_context}".strip()

            prompt = f"Context: {full_context[:1000]}\n\nQuestion: {query}\n\nAnswer:"

            # Tokenize
            inputs = tokenizer(prompt, return_tensors='pt', padding=True, truncation=True, max_length=512)
            input_ids = inputs['input_ids'].to(self.device)

            # Custom generation with repetition penalty
            max_new_tokens = 60
            temperature = 0.9
            top_k = 40
            repetition_penalty = 1.5

            generated_ids = input_ids.clone()

            with torch.no_grad():
                for _ in range(max_new_tokens):
                    outputs = model(input_ids=generated_ids)
                    logits = outputs['logits'][:, -1, :]

                    # Apply repetition penalty
                    for prev_token in generated_ids[0].unique():
                        logits[0, prev_token] /= repetition_penalty

                    logits = logits / temperature

                    v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                    logits[logits < v[:, [-1]]] = -float('Inf')

                    probs = F.softmax(logits, dim=-1)
                    next_token = torch.multinomial(probs, num_samples=1)

                    generated_ids = torch.cat([generated_ids, next_token], dim=1)

                    if next_token.item() == 50256:
                        break

            full_response = tokenizer.decode(generated_ids[0], skip_special_tokens=True)

            if "Answer:" in full_response:
                response = full_response.split("Answer:")[-1].strip()
            else:
                response = full_response[len(prompt):].strip()

            # Quality check - detect repetitive/nonsense output
            words = response.split()
            if len(words) > 3:
                unique_ratio = len(set(words)) / len(words)
                if unique_ratio < 0.5:  # More than 50% repeated words
                    response = ""  # Force fallback

            # Smart context extraction if model output is poor
            if not response or len(response) < 10:
                # Extract answer from context
                response = self._extract_answer_from_context(query, context)

            return {
                "response": response,
                "rag_used": rag_used,
                "model": "ImpressionCoreB3Model"
            }

        except Exception as e:
            logger.error(f"B3 generation failed: {e}")
            context = context_manager.get_active_context() or ""
            return {
                "response": self._extract_answer_from_context(query, context),
                "rag_used": False,
                "error": str(e)
            }

    def _extract_answer_from_context(self, query: str, context: str) -> str:
        """Extract a relevant answer from context using keyword matching."""
        if not context:
            return f"I need more context to answer: {query}"

        # Split context into sentences
        sentences = [s.strip() + '.' for s in context.replace('\n', ' ').split('.') if len(s.strip()) > 10]

        if not sentences:
            return context[:200]

        # Find query keywords
        query_words = set(w.lower() for w in query.split() if len(w) > 3)

        # Score sentences by keyword overlap
        scored = []
        for sent in sentences:
            sent_words = set(w.lower() for w in sent.split() if len(w) > 3)
            overlap = len(query_words & sent_words)
            scored.append((overlap, sent))

        # Sort by relevance
        scored.sort(key=lambda x: x[0], reverse=True)

        # Take top 2 most relevant sentences
        relevant = [s[1] for s in scored[:2] if s[0] > 0]

        if relevant:
            return ' '.join(relevant)
        else:
            return sentences[0] if sentences else context[:200]

    def generate_answer(
        self,
        query: str,
        context: str,
        context_manager: Any = None
    ) -> dict[str, Any]:
        """
        High-level API to generate an answer using policy-guided inference.

        This runs a full episode and generates a final answer.

        Args:
            query: User query
            context: Context document(s)
            context_manager: Optional, will create if not provided

        Returns:
            Dict with answer, steps, and metadata
        """
        # Create context manager if needed
        if context_manager is None:
            from src.orchestrator.nexus_context_manager import RLMContextManager
            context_manager = RLMContextManager()
            context_manager.load_context_from_string(context, "query_context")

        # Run policy episode
        episode = self.run_episode(query, context, context_manager)

        # Generate final answer using B3
        answer_result = self._generate_with_b3(query, context_manager)

        return {
            "query": query,
            "answer": answer_result.get("response", ""),
            "rag_used": answer_result.get("rag_used", False),
            "episode_steps": episode["total_steps"],
            "action_sequence": [s["action"] for s in episode["steps"]],
            "success": episode["success"]
        }

    @property
    def is_ready(self) -> bool:
        """Check if the agent is ready for inference."""
        return self._policy_loaded and self.policy is not None


# Singleton accessor
_policy_agent: RLMPolicyAgent | None = None

def get_policy_agent(config: PolicyAgentConfig | None = None) -> RLMPolicyAgent:
    """Get or create the singleton policy agent."""
    global _policy_agent
    if _policy_agent is None:
        _policy_agent = RLMPolicyAgent(config)
    return _policy_agent
