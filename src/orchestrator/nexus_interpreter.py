import os
import re
from typing import Any

from ..core.utils.hardware_detection import HardwareDetector
from .session_manager import session_manager
from .system_logger import log_event

# NEXUS Context Manager for context folding operations
try:
    from .nexus_context_manager import RLMContextManager, get_rlm_context_manager  # noqa: F401
    from .rlm_policy_agent import RLMPolicyAgent, get_policy_agent  # noqa: F401
    RLM_AVAILABLE = True
except ImportError:
    RLM_AVAILABLE = False
    get_rlm_context_manager = None
    get_policy_agent = None

# Dictionary Knowledge Base
try:
    from ..knowledge.dictionary_index import DictionaryIndex
    DICT_AVAILABLE = True
except ImportError:
    DICT_AVAILABLE = False


class NexusInterpreter:
    """
    A lightweight interpreter for the Nexus Language (prefix-notation).
    Supports basic function calls, nested expressions, and core Triad commands.
    """

    def __init__(self):
        self.functions = {
            "REQUEST-OUTPUT": self._handle_request,
            "RESPOND-TO": self._handle_respond,
            "SET-TEMP": self._handle_set_temp,
            "DICT": self._handle_dict,
            "LIST": self._handle_list,
            "LOG": self._handle_log,
            "TEACHER-GUIDANCE": self._handle_teacher_guidance,
            "MEMORY-SEARCH": self._handle_memory_search,
            "MEMORY-RECALL": self._handle_memory_recall,
            "MEMORY-SUMMARY": self._handle_memory_summary,
            "FILE-READ": self._handle_file_read,
            "FILE-WRITE": self._handle_file_write,
            "SYS-STAT": self._handle_sys_stat,
            "GENERATE-IMAGE": self._handle_generate_image,
            # === NEW: Control Flow & Variables (NEXUS-L v1.1) ===
            "IF": self._handle_if,
            "COND": self._handle_cond,
            "LET": self._handle_let,
            "EXECUTE-PLAN": self._handle_execute_plan,
            # === NEW: Comparison Operators ===
            ">": self._handle_gt,
            "<": self._handle_lt,
            ">=": self._handle_gte,
            "<=": self._handle_lte,
            "=": self._handle_eq,
            "NOT": self._handle_not,
            "AND": self._handle_and,
            "OR": self._handle_or,
            # === NEW: RLM Commands (NEXUS v1.2) ===
            "LLM-QUERY": self._handle_llm_query,
            "CONTEXT-LOAD": self._handle_context_load,
            "CONTEXT-SEARCH": self._handle_context_search,
            "CONTEXT-CHUNK": self._handle_context_chunk,
            "CONTEXT-STATS": self._handle_context_stats,
            "CONTEXT-LIST": self._handle_context_list,
            "RECURSION-DEPTH": self._handle_recursion_depth,
            "RLM-STATS": self._handle_rlm_stats,
            # === NEW: Parallel Execution (NEXUS v1.3) ===
            "ASYNC": self._handle_async,
            "PARALLEL": self._handle_parallel,
            "AWAIT": self._handle_await,
            # === NEW: Pipeline & Utilities (NEXUS v1.4) ===
            "PIPELINE": self._handle_pipeline,
            "+": self._handle_add,
            "-": self._handle_sub,
            "*": self._handle_mul,
            "/": self._handle_div,
            "CONCAT": self._handle_concat,
            "MAP": self._handle_map,
            # === NEW: Knowledge Base (NEXUS v1.5) ===
            "DICT-LOOKUP": self._handle_dict_lookup,
            "DICT-DEF": self._handle_dict_def,
        }
        self.output_queue = []
        # Variable storage for LET bindings (scoped per execution context)
        self.variables: dict[str, Any] = {}

    def parse(self, code: str) -> list[Any]:
        """Tokenize and parse prefix notation into nested lists."""
        log_event("NEXUS", f"Parsing code: {code[:50]}...", level="DEBUG")
        tokens = self._tokenize(code)
        return self._build_ast(tokens)

    def _tokenize(self, code: str) -> list[str]:
        # Simple regex for parentheses, strings, and atoms
        token_pattern = r'\(|\)|"[^"]*"|[^\s()]+'
        return re.findall(token_pattern, code)

    def _build_ast(self, tokens: list[str]) -> list[Any]:
        if not tokens:
            return []

        token = tokens.pop(0)
        if token == "(":
            ast = []
            while tokens[0] != ")":
                ast.append(self._build_ast(tokens))
            tokens.pop(0) # Remove closing ")"
            return ast
        elif token == ")":
            raise ValueError("Unexpected closing parenthesis")
        else:
            # Atomic value
            if token.startswith('"') and token.endswith('"'):
                return token[1:-1]
            try:
                if "." in token:
                    return float(token)
                return int(token)
            except ValueError:
                return token # Symbol

    def execute(self, code: str, context: dict[str, Any] | None = None) -> Any:
        """Parse and evaluate Nexus code."""
        try:
            ast = self.parse(code)
            result = self.evaluate(ast, context or {})
            log_event("NEXUS", "Execution successful", payload={"code": code, "result": result})
            return result
        except Exception as e:
            log_event("NEXUS", f"Execution Error: {e}", level="ERROR")
            return f"(ERROR \"{e!s}\")"

    def evaluate(self, expr: Any, context: dict[str, Any]) -> Any:
        # Handle atoms (non-list expressions)
        if not isinstance(expr, list):
            # Check if it's a variable reference
            if isinstance(expr, str) and expr in self.variables:
                return self.variables[expr]
            # Check context for variable bindings
            if isinstance(expr, str) and expr in context:
                return context[expr]
            return expr  # Return as-is (literal)

        if not expr:
            return None

        func_name = str(expr[0]).upper()
        args = expr[1:]

        # Special forms that need lazy evaluation (don't pre-evaluate args)
        if func_name in ("IF", "COND", "LET", "PIPELINE", "ASYNC"):
            return self.functions[func_name](args, context)

        if func_name in self.functions:
            # Evaluate args first (Eager evaluation)
            eval_args = [self.evaluate(a, context) for a in args]
            return self.functions[func_name](eval_args, context)
        else:
            log_event("NEXUS", f"Unknown function: {func_name}", level="WARNING")
            return expr  # Return as list if unknown

    # --- Built-in Functions ---

    def _handle_dict(self, args, context):
        """(DICT (key1 val1) (key2 val2))"""
        result = {}
        for item in args:
            if isinstance(item, list) and len(item) == 2:
                result[item[0]] = item[1]
        return result

    def _handle_list(self, args, context):
        """(LIST item1 item2)"""
        return list(args)

    def _handle_request(self, args, context):
        """(REQUEST-OUTPUT target type params)"""
        target = args[0]
        req_type = args[1]
        params = args[2] if len(args) > 2 else {}
        self.output_queue.append({
            "action": "REQUEST",
            "target": target,
            "type": req_type,
            "params": params
        })
        return f"OK-REQUEST-{target}"

    def _handle_respond(self, args, context):
        """(RESPOND-TO target data)"""
        target = args[0]
        data = args[1]
        self.output_queue.append({
            "action": "RESPONSE",
            "target": target,
            "data": data
        })
        return f"OK-RESPOND-{target}"

    def _handle_set_temp(self, args, context):
        """(SET-TEMP target value)"""
        target = args[0]
        temp = args[1]
        self.output_queue.append({
            "action": "CONFIG",
            "target": target,
            "key": "temperature",
            "value": temp
        })
        return f"OK-TEMP-{target}"

    def _handle_log(self, args, context):
        msg = " ".join([str(a) for a in args])
        log_event("NEXUS-REASONING", msg)
        return msg

    def _handle_teacher_guidance(self, args, context):
        msg = " ".join([str(a) for a in args])
        log_event("SUPPLEMENT-GUIDE", msg)
        return msg

    def _handle_memory_search(self, args, context):
        """(MEMORY-SEARCH "query")"""
        query = args[0]
        results = session_manager.search_memory(query)
        if not results:
            return "No matching memories found."

        formatted = "Found Memories:\n"
        for r in results:
            formatted += f"[{r['timestamp']}] Session: {r['session_title']} | {r['role']}: {r['content'][:100]}...\n"
        return formatted

    def _handle_memory_recall(self, args, context):
        """(MEMORY-RECALL "session_id")"""
        session_id = args[0]
        data = session_manager.get_session(session_id)
        if not data:
            return f"Session {session_id} not found."

        formatted = f"Full Recall of Session: {data.get('title')}\n"
        for msg in data.get("messages", []):
            formatted += f"{msg['role'].upper()}: {msg['content']}\n"
        return formatted

    def _handle_memory_summary(self, args, context):
        """(MEMORY-SUMMARY)"""
        return session_manager.get_global_context()

    def _get_safe_path(self, relative_path: str) -> str | None:
        # Define project root (relative to this file)
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        target_path = os.path.abspath(os.path.join(base_dir, relative_path))
        if target_path.startswith(base_dir):
            return target_path
        return None

    def _handle_file_read(self, args, context):
        """(FILE-READ "path")"""
        path = self._get_safe_path(args[0])
        if not path or not os.path.exists(path):
            return f"Error: Access denied or file not found: {args[0]}"

        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
                return content[:2000] # Cap output to 2000 chars for safety
        except Exception as e:
            return f"Error reading file: {e}"

    def _handle_file_write(self, args, context):
        """(FILE-WRITE "path" "content")"""
        path = self._get_safe_path(args[0])
        content = args[1]

        if not path:
            return f"Error: Access denied to path: {args[0]}"

        # Security: Prevent writing to critical files like .py files for now?
        # Let's allow it but log it heavily.
        if path.endswith((".py", ".json", ".md", ".jsx", ".css")):
            log_event("NEXUS-FILE", f"CRITICAL: Writing to code file: {path}", level="WARNING")

        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote {len(content)} bytes to {args[0]}"
        except Exception as e:
            return f"Error writing file: {e}"

    def _handle_sys_stat(self, args, context):
        """(SYS-STAT)"""
        detector = HardwareDetector()
        gpu_info = detector.get_gpu_info()
        mem_info = detector.get_memory_info()

        stat = "System Status:\n"
        stat += f"- OS: {os.name} | GPU: {gpu_info.get('gpu_name')}\n"
        stat += f"- VRAM: {mem_info.get('cuda_allocated', 0):.2f}/{mem_info.get('cuda_total', 0):.2f} GB\n"
        stat += f"- RAM: {mem_info.get('system_used', 0):.2f}/{mem_info.get('system_total', 0):.2f} GB ({mem_info.get('system_percent')}%)"
        return stat

    def _handle_generate_image(self, args, context):
        """(GENERATE-IMAGE "prompt" (DICT ("style" "vibrant") ...))"""
        prompt = args[0]
        params = args[1] if len(args) > 1 else {}
        log_event("NEXUS-GEN", f"Image Generation Requested: {prompt}")

        # This hook allows the orchestrator to pick up the request.
        self.output_queue.append({
            "action": "GENERATE_IMAGE",
            "prompt": prompt,
            "params": params
        })
        return "OK-GENERATE-IMAGE-PENDING"

    # =============================================================
    # === NEXUS-L v1.1: Control Flow & Variables ==================
    # =============================================================

    def _handle_if(self, args, context):
        """(IF condition then-expr else-expr)
        Lazy evaluation: only evaluates the branch taken.
        """
        if len(args) < 2:
            return "(ERROR \"IF requires at least condition and then-expr\")"

        condition = self.evaluate(args[0], context)

        # Truthiness check
        if self._is_truthy(condition):
            return self.evaluate(args[1], context)
        elif len(args) > 2:
            return self.evaluate(args[2], context)
        else:
            return None

    def _handle_cond(self, args, context):
        """(COND (cond1 expr1) (cond2 expr2) (ELSE default))
        Multi-way conditional.
        """
        for clause in args:
            if not isinstance(clause, list) or len(clause) < 2:
                continue

            cond_expr = clause[0]
            body_expr = clause[1]

            # Check for ELSE clause
            if isinstance(cond_expr, str) and cond_expr.upper() == "ELSE":
                return self.evaluate(body_expr, context)

            # Evaluate condition
            if self._is_truthy(self.evaluate(cond_expr, context)):
                return self.evaluate(body_expr, context)

        return None

    def _handle_let(self, args, context):
        """(LET ((var1 val1) (var2 val2)) body-expr)
        Creates scoped variable bindings for the body expression.
        """
        if len(args) < 2:
            return "(ERROR \"LET requires bindings and body\")"

        bindings = args[0]
        body = args[1]

        # Create new context with bindings
        new_context = context.copy()

        if isinstance(bindings, list):
            for binding in bindings:
                if isinstance(binding, list) and len(binding) == 2:
                    var_name = str(binding[0])
                    var_value = self.evaluate(binding[1], new_context)
                    new_context[var_name] = var_value
                    self.variables[var_name] = var_value  # Also store in interpreter

        result = self.evaluate(body, new_context)

        # Clean up bindings (scoped)
        if isinstance(bindings, list):
            for binding in bindings:
                if isinstance(binding, list) and len(binding) >= 1:
                    var_name = str(binding[0])
                    self.variables.pop(var_name, None)

        return result

    def _handle_execute_plan(self, args, context):
        """(EXECUTE-PLAN "plan_id")
        Loads and executes a plan file from the plans directory.
        """
        if not args:
            return "(ERROR \"EXECUTE-PLAN requires plan_id\")"

        plan_id = str(args[0])

        # Security: Sanitize plan_id
        if not plan_id.replace("_", "").replace("-", "").isalnum():
            return f"(ERROR \"Invalid plan_id: {plan_id}\")"

        # Look for plan file
        plan_paths = [
            os.path.join("plans", f"{plan_id}.nexus"),
            os.path.join("plans", f"{plan_id}.nxs"),
            os.path.join("src", "orchestrator", "plans", f"{plan_id}.nexus"),
        ]

        plan_code = None
        for path in plan_paths:
            if os.path.exists(path):
                try:
                    with open(path, encoding="utf-8") as f:
                        plan_code = f.read()
                    log_event("NEXUS-PLAN", f"Loaded plan: {path}")
                    break
                except Exception as e:
                    log_event("NEXUS-PLAN", f"Failed to read {path}: {e}", level="ERROR")

        if plan_code is None:
            return f"(ERROR \"Plan not found: {plan_id}\")"

        # Execute the plan
        return self.execute(plan_code, context)

    # =============================================================
    # === NEXUS-L v1.1: Comparison Operators ======================
    # =============================================================

    def _handle_gt(self, args, context):
        """(> a b) - Greater than"""
        if len(args) < 2:
            return False
        return float(args[0]) > float(args[1])

    def _handle_lt(self, args, context):
        """(< a b) - Less than"""
        if len(args) < 2:
            return False
        return float(args[0]) < float(args[1])

    def _handle_gte(self, args, context):
        """(>= a b) - Greater than or equal"""
        if len(args) < 2:
            return False
        return float(args[0]) >= float(args[1])

    def _handle_lte(self, args, context):
        """(<= a b) - Less than or equal"""
        if len(args) < 2:
            return False
        return float(args[0]) <= float(args[1])

    def _handle_eq(self, args, context):
        """(= a b) - Equality"""
        if len(args) < 2:
            return False
        return args[0] == args[1]

    def _handle_not(self, args, context):
        """(NOT expr) - Logical NOT"""
        if not args:
            return True
        return not self._is_truthy(args[0])

    def _handle_and(self, args, context):
        """(AND expr1 expr2 ...) - Logical AND"""
        return all(self._is_truthy(arg) for arg in args)

    def _handle_or(self, args, context):
        """(OR expr1 expr2 ...) - Logical OR"""
        return any(self._is_truthy(arg) for arg in args)

    def _is_truthy(self, value: Any) -> bool:
        """Determines truthiness for NEXUS-L conditionals."""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, int | float):
            return value != 0
        if isinstance(value, str):
            return value.lower() not in ("", "false", "nil", "none", "0")
        if isinstance(value, list | dict):
            return len(value) > 0
        return True

    # =============================================================
    # === NEXUS v1.2: Recursive Language Model Commands =======
    # =============================================================

    def _handle_llm_query(self, args, context):
        """(LLM-QUERY target prompt [params])

        Make a recursive call to a Brain-Triad hemisphere.

        Target can be:
        - "left" - Analytical hemisphere (low temperature)
        - "right" - Creative hemisphere (high temperature)
        - "colossus" - Central synthesizer (balanced)

        Example:
            (LLM-QUERY "left" "Analyze this data logically")
            (LLM-QUERY "right" "Generate creative alternatives")
        """
        if not RLM_AVAILABLE:
            return "(ERROR \"RLM module not available\")"

        if len(args) < 2:
            return "(ERROR \"LLM-QUERY requires target and prompt\")"

        target = str(args[0]).lower()
        prompt = str(args[1])
        params = args[2] if len(args) > 2 else {}

        # Get RLM context manager
        rlm = get_rlm_context_manager()

        # Check recursion depth
        can_recurse, msg = rlm.begin_recursive_call(target, prompt)
        if not can_recurse:
            return f"(ERROR \"{msg}\")"

        try:
            log_event("NEXUS", f"LLM-QUERY to '{target}' (depth: {rlm.get_recursion_depth()})")

            # Check if we have a Brain-Triad instance for synchronous mode
            triad = getattr(self, '_triad_instance', None)

            if triad is not None:
                # SYNCHRONOUS MODE: Direct Brain-Triad query
                try:
                    temperature = params.get('temperature') if isinstance(params, dict) else None
                    max_tokens = params.get('max_tokens', 150) if isinstance(params, dict) else 150

                    if target == "left":
                        response = triad.query_left(prompt, temperature=temperature or 0.3, max_tokens=max_tokens)
                    elif target == "right":
                        response = triad.query_right(prompt, temperature=temperature or 0.9, max_tokens=max_tokens)
                    else:  # colossus
                        response = triad.query_colossus(prompt, temperature=temperature or 0.5, max_tokens=max_tokens)

                    log_event("NEXUS", f"Sync response from {target}: {response[:50]}...")
                    return response

                except Exception as e:
                    log_event("NEXUS", f"Sync query failed, falling back to async: {e}", level="WARNING")

            # ASYNC MODE: Queue the request for later processing
            self.output_queue.append({
                "action": "LLM_QUERY",
                "target": target,
                "prompt": prompt,
                "params": params,
                "recursion_depth": rlm.get_recursion_depth()
            })

            return f"OK-LLM-QUERY-{target.upper()}-PENDING"

        finally:
            rlm.end_recursive_call()

    def set_triad(self, triad_instance):
        """Set the Brain-Triad instance for synchronous LLM-QUERY operations."""
        self._triad_instance = triad_instance
        log_event("NEXUS", "Brain-Triad instance connected for synchronous queries")

    def _handle_context_load(self, args, context):
        """(CONTEXT-LOAD path [context_id])

        Load a document/file as external RLM context.

        Example:
            (CONTEXT-LOAD "docs/large_document.md")
            (CONTEXT-LOAD "docs/report.txt" "report_2026")
        """
        if not RLM_AVAILABLE:
            return "(ERROR \"RLM module not available\")"

        if not args:
            return "(ERROR \"CONTEXT-LOAD requires file path\")"

        file_path = str(args[0])
        context_id = str(args[1]) if len(args) > 1 else None

        rlm = get_rlm_context_manager()
        success, message = rlm.load_context_from_file(file_path, context_id)

        if success:
            log_event("NEXUS", f"Context loaded: {message}")
            return f"OK-CONTEXT-LOADED: {message}"
        else:
            return f"(ERROR \"{message}\")"

    def _handle_context_search(self, args, context):
        """(CONTEXT-SEARCH pattern [is_regex] [max_results])

        Search the active context for a pattern.

        Example:
            (CONTEXT-SEARCH "quantum computing")
            (CONTEXT-SEARCH "def \\w+\\(" true 20)
        """
        if not RLM_AVAILABLE:
            return "(ERROR \"RLM module not available\")"

        if not args:
            return "(ERROR \"CONTEXT-SEARCH requires search pattern\")"

        pattern = str(args[0])
        is_regex = bool(args[1]) if len(args) > 1 else False
        max_results = int(args[2]) if len(args) > 2 else 10

        rlm = get_rlm_context_manager()
        results = rlm.search_context(pattern, is_regex=is_regex, max_results=max_results)

        if not results:
            return "No matches found."

        if "error" in results[0]:
            return f"(ERROR \"{results[0]['error']}\")"

        # Format results
        formatted = f"Found {len(results)} matches:\n"
        for i, r in enumerate(results, 1):
            formatted += f"\n[{i}] Position {r['start']}-{r['end']}:\n"
            formatted += f"   Match: {r['match'][:50]}...\n"
            formatted += f"   Context: ...{r['context'][:100]}...\n"

        return formatted

    def _handle_context_chunk(self, args, context):
        """(CONTEXT-CHUNK [chunk_size] [by])

        Split context into processable chunks.

        By options: "chars", "lines", "paragraphs"

        Example:
            (CONTEXT-CHUNK)
            (CONTEXT-CHUNK 8000 "paragraphs")
        """
        if not RLM_AVAILABLE:
            return "(ERROR \"RLM module not available\")"

        chunk_size = int(args[0]) if args else None
        by = str(args[1]) if len(args) > 1 else "chars"

        rlm = get_rlm_context_manager()
        chunks = rlm.chunk_context(chunk_size=chunk_size, by=by)

        if not chunks:
            return "(ERROR \"No context loaded or empty context\")"

        # Return summary + chunk references
        result = f"Created {len(chunks)} chunks (by {by}):\n"
        for i, chunk in enumerate(chunks[:5]):  # Show first 5
            result += f"  [{i}] {len(chunk)} chars: {chunk[:50]}...\n"

        if len(chunks) > 5:
            result += f"  ... and {len(chunks) - 5} more chunks\n"

        return result

    def _handle_context_stats(self, args, context):
        """(CONTEXT-STATS [context_id])

        Get statistics about a loaded context.

        Example:
            (CONTEXT-STATS)
            (CONTEXT-STATS "report_2026")
        """
        if not RLM_AVAILABLE:
            return "(ERROR \"RLM module not available\")"

        context_id = str(args[0]) if args else None

        rlm = get_rlm_context_manager()
        stats = rlm.get_context_stats(context_id)

        if "error" in stats:
            return f"(ERROR \"{stats['error']}\")"

        result = f"Context Statistics ({stats['context_id']}):\n"
        result += f"  Characters: {stats['char_count']:,}\n"
        result += f"  Tokens (est): {stats['token_estimate']:,}\n"
        result += f"  Lines: {stats['line_count']:,}\n"
        result += f"  Paragraphs: {stats['paragraph_count']:,}\n"
        result += f"  Words: {stats['word_count']:,}\n"
        if stats['source_path']:
            result += f"  Source: {stats['source_path']}\n"

        return result

    def _handle_context_list(self, args, context):
        """(CONTEXT-LIST)

        List all loaded contexts.
        """
        if not RLM_AVAILABLE:
            return "(ERROR \"RLM module not available\")"

        rlm = get_rlm_context_manager()
        contexts = rlm.list_contexts()

        if not contexts:
            return "No contexts loaded."

        result = f"Loaded contexts ({len(contexts)}):\n"
        for ctx in contexts:
            active = " [ACTIVE]" if ctx['active'] else ""
            result += f"  - {ctx['id']}: {ctx['chars']:,} chars (~{ctx['tokens_est']:,} tokens){active}\n"

        return result

    def _handle_recursion_depth(self, args, context):
        """(RECURSION-DEPTH)

        Get current RLM recursion depth.
        """
        if not RLM_AVAILABLE:
            return 0

        rlm = get_rlm_context_manager()
        return rlm.get_recursion_depth()

    def _handle_rlm_stats(self, args, context):
        """(RLM-STATS)

        Get global RLM statistics.
        """
        if not RLM_AVAILABLE:
            return "(ERROR \"RLM module not available\")"

        rlm = get_rlm_context_manager()
        stats = rlm.get_global_stats()

        result = "RLM Global Statistics:\n"
        result += f"  Contexts Loaded: {stats['contexts_loaded']}\n"
        result += f"  Total Searches: {stats['total_searches']}\n"
        result += f"  Total Chunks Created: {stats['total_chunks_created']}\n"
        result += f"  Total LLM Queries: {stats['total_llm_queries']}\n"
        result += f"  Current Recursion Depth: {stats['current_recursion_depth']}\n"
        result += f"  Active Context: {stats['active_context'] or 'None'}\n"

        return result


    # ===================================================================
    # === NEXUS v1.5: Knowledge Base Commands ===========================
    # ===================================================================

    def _get_dictionary(self):
        """Lazy load dictionary index."""
        if not DICT_AVAILABLE:
            return None
        if not hasattr(self, '_dictionary_index'):
            try:
                self._dictionary_index = DictionaryIndex()
            except Exception as e:
                log_event("NEXUS", f"Failed to load dictionary index: {e}", level="ERROR")
                return None
        return self._dictionary_index

    def _handle_dict_lookup(self, args, context):
        """(DICT-LOOKUP "word")

        Quick lookup of a word in the local dictionary knowledge base.
        Returns the first definition found.
        """
        if not DICT_AVAILABLE:
            return "(ERROR \"Knowledge module not available\")"

        word = str(args[0])
        dictionary = self._get_dictionary()

        if not dictionary:
            return "(ERROR \"Dictionary not initialized\")"

        results = dictionary.lookup(word)
        if not results:
            return f"Definition not found for '{word}'."

        # Return first definition
        return results[0]['definition']

    def _handle_dict_def(self, args, context):
        """(DICT-DEF "word")

        Full dictionary entry lookup.
        Returns detailed info including POS.
        """
        if not DICT_AVAILABLE:
            return "(ERROR \"Knowledge module not available\")"

        word = str(args[0])
        dictionary = self._get_dictionary()

        if not dictionary:
            return "(ERROR \"Dictionary not initialized\")"

        results = dictionary.lookup(word)
        if not results:
            return f"Entry not found for '{word}'."

        response = f"Dictionary Entries for '{word}':\\n"
        for i, res in enumerate(results, 1):
            response += f"[{i}] ({res['pos']}) {res['definition']}\\n"

        return response

    # ===================================================================
    # === NEXUS v1.3: Parallel Execution Commands ==================
    # ===================================================================

    def _handle_async(self, args, context):
        """(ASYNC expr)

        Execute an expression asynchronously and return immediately.
        The result is stored with an async ID for later retrieval.

        Example:
            (ASYNC (LLM-QUERY "left" "Analyze this"))

        Returns:
            Async task ID for use with (AWAIT id)
        """
        if len(args) < 1:
            return "(ERROR \"ASYNC requires an expression\")"

        import threading
        import uuid

        async_id = f"async_{uuid.uuid4().hex[:8]}"

        # Initialize async results storage
        if not hasattr(self, '_async_results'):
            self._async_results = {}
            self._async_lock = threading.Lock()

        expr = args[0]

        def run_async():
            try:
                result = self.evaluate(expr, context)
                with self._async_lock:
                    self._async_results[async_id] = {
                        "status": "complete",
                        "result": result,
                        "error": None
                    }
            except Exception as e:
                with self._async_lock:
                    self._async_results[async_id] = {
                        "status": "error",
                        "result": None,
                        "error": str(e)
                    }

        # Mark as pending
        with self._async_lock:
            self._async_results[async_id] = {
                "status": "pending",
                "result": None,
                "error": None
            }

        # Start async execution
        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()

        log_event("NEXUS", f"Started async task: {async_id}")
        return async_id

    def _handle_await(self, args, context):
        """(AWAIT async_id [timeout_ms])

        Wait for an async task to complete and return its result.

        Example:
            (LET ((task (ASYNC (LLM-QUERY "left" "Analyze"))))
                 (AWAIT task 5000))

        Returns:
            The result of the async expression
        """
        if len(args) < 1:
            return "(ERROR \"AWAIT requires an async ID\")"

        async_id = str(args[0])
        timeout_ms = int(args[1]) if len(args) > 1 else 30000  # Default 30s

        if not hasattr(self, '_async_results'):
            return f"(ERROR \"Unknown async ID: {async_id}\")"

        import time
        start = time.time()
        timeout_s = timeout_ms / 1000.0

        while True:
            with self._async_lock:
                if async_id in self._async_results:
                    task = self._async_results[async_id]
                    if task["status"] == "complete":
                        result = task["result"]
                        del self._async_results[async_id]  # Cleanup
                        return result
                    elif task["status"] == "error":
                        error = task["error"]
                        del self._async_results[async_id]
                        return f"(ERROR \"Async task failed: {error}\")"

            if time.time() - start > timeout_s:
                return f"(ERROR \"AWAIT timeout after {timeout_ms}ms\")"

            time.sleep(0.01)  # 10ms poll interval

    def _handle_parallel(self, args, context):
        """(PARALLEL expr1 expr2 ...)

        Execute multiple expressions in parallel and return all results.
        Waits for all to complete before returning.

        Example:
            (PARALLEL
                (LLM-QUERY "left" "Analyze logically")
                (LLM-QUERY "right" "Think creatively")
                (LLM-QUERY "colossus" "Synthesize"))

        Returns:
            List of results in order
        """
        if len(args) < 1:
            return []

        import threading

        results = [None] * len(args)
        errors = [None] * len(args)
        threads = []

        def run_expr(idx, expr):
            try:
                results[idx] = self.evaluate(expr, context)
            except Exception as e:
                errors[idx] = str(e)

        # Start all threads
        for i, expr in enumerate(args):
            t = threading.Thread(target=run_expr, args=(i, expr), daemon=True)
            threads.append(t)
            t.start()

        # Wait for all to complete
        for t in threads:
            t.join(timeout=60.0)  # 60 second max per task

        # Build result
        final_results = []
        for _i, (result, error) in enumerate(zip(results, errors)):
            if error:
                final_results.append(f"(ERROR \"{error}\")")
            else:
                final_results.append(result)

        log_event("NEXUS", f"PARALLEL completed {len(args)} tasks")
        return final_results

    # ===================================================================
    # === NEXUS v1.4: Pipeline & Utility Commands ==================
    # ===================================================================

    def _handle_pipeline(self, args, context):
        """(PIPELINE expr1 expr2 ...)

        Execute expressions in sequence, passing each result to the next.
        The special symbol _ represents the previous result.

        Example:
            (PIPELINE
                (CONTEXT-LOAD "doc.md")
                (CONTEXT-CHUNK 8000)
                (LLM-QUERY "colossus" (CONCAT "Summarize: " _)))

        Returns:
            The result of the final expression
        """
        if len(args) < 1:
            return None

        result = None
        for expr in args:
            # Inject previous result as _ in context
            context = context.copy() if context else {}
            context['_'] = result
            self.variables['_'] = result

            result = self.evaluate(expr, context)

        log_event("NEXUS", f"PIPELINE completed {len(args)} stages")
        return result

    def _handle_add(self, args, context):
        """(+ a b ...) - Add numbers"""
        if len(args) < 2:
            return "(ERROR \"+ requires at least 2 arguments\")"
        nums = [float(a) if isinstance(a, int | float) else 0 for a in args]
        result = sum(nums)
        return int(result) if result == int(result) else result

    def _handle_sub(self, args, context):
        """(- a b) - Subtract numbers"""
        if len(args) < 2:
            return "(ERROR \"- requires at least 2 arguments\")"
        nums = [float(a) if isinstance(a, int | float) else 0 for a in args]
        result = nums[0] - sum(nums[1:])
        return int(result) if result == int(result) else result

    def _handle_mul(self, args, context):
        """(* a b ...) - Multiply numbers"""
        if len(args) < 2:
            return "(ERROR \"* requires at least 2 arguments\")"
        result = 1
        for a in args:
            result *= float(a) if isinstance(a, int | float) else 1
        return int(result) if result == int(result) else result

    def _handle_div(self, args, context):
        """(/ a b) - Divide numbers"""
        if len(args) < 2:
            return "(ERROR \"/ requires at least 2 arguments\")"
        try:
            result = float(args[0])
            for a in args[1:]:
                result /= float(a)
            return int(result) if result == int(result) else result
        except ZeroDivisionError:
            return "(ERROR \"Division by zero\")"

    def _handle_concat(self, args, context):
        """(CONCAT str1 str2 ...) - Concatenate strings"""
        return "".join(str(a) for a in args)

    def _handle_list(self, args, context):
        """(LIST item1 item2 ...) - Create a list"""
        return list(args)

    def _handle_map(self, args, context):
        """(MAP fn list) - Apply function to each element

        Example:
            (MAP (LAMBDA (x) (+ x 1)) (LIST 1 2 3))

        Note: Currently supports built-in functions only
        """
        if len(args) < 2:
            return "(ERROR \"MAP requires function and list\")"

        fn_expr = args[0]
        items = args[1] if isinstance(args[1], list) else [args[1]]

        results = []
        for item in items:
            # Simple function application for built-in functions
            if isinstance(fn_expr, str) and fn_expr in self.functions:
                result = self.functions[fn_expr]([item], context)
            else:
                results.append(item)
                continue
            results.append(result)

        return results



if __name__ == "__main__":
    # Test
    interpreter = NexusInterpreter()
    code = '(REQUEST-OUTPUT "right-hemisphere" "creative-text" (DICT ("style" "haiku") ("topic" "clouds")))'
    result = interpreter.execute(code)
    print(f"Result: {result}")
    print(f"Queue: {interpreter.output_queue}")
