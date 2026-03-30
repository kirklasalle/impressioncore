# Nexus Language ("NEXUS-L") Specification & Developers Guide

**Created:** December 24, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team  
**Tags:** #docs\nexus_language_guide.md #documentation  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

**Version**: 1.0 (B3-Triad)  
**Role**: Inter-Module Control & Reasoning Protocol  
**Status**: ACTIVE - Core System Logic  

---

## 1. Executive Summary & Role Analysis

The **Nexus Language** (often referred to as **Nexus-L** or just **Nexus**) is a specialized **Prefix-Notation Protocol** designed to serve as the "Lingua Franca" of the ImpressionCore Brain-Triad.

### Is it Necessary?

**Result: YES.** Analysis confirms that while Python handles the raw execution, Nexus-L provides a critical layer of **abstraction and standardization** for the "Reasoning Trail."

- **Efficiency**: It decouples the "Intent" (what needs to happen) from the "Implementation" (how Python does it). This allows the Colossus aggregator to issue commands like `(SET-TEMP "right" 0.9)` without needing to know the underlying PyTorch object structure.
- **Organization**: It forces a structured "Thought Trace." Every action taken by the triad is logged as a valid Nexus expression, ensuring that the system's "Stream of Consciousness" is machine-readable and explicitly parseable.
- **Reasoning Metrics**: A standardized language allows us to measure "Reasoning Density" (tokens per action) and "Flow Accuracy" (valid vs. invalid commands).

---

## 2. Syntax & Structure

Nexus-L follows a Strict Lisp-Like Prefix Notation (`S-Expression`).

### 2.1 The Atomic Unit

Everything is an expression. An expression is a parenthesized list where the first element is the **Operator** (Function) and subsequent elements are **Operands** (Arguments).

```lisp
(OPERATOR arg1 arg2 ... argN)
```

### 2.2 Data Types

| Type | Notation | Example |
| :--- | :--- | :--- |
| **String** | Double-quoted | `"Hello World"`, `"left-hemisphere"` |
| **Number** | Raw numeric | `0.7`, `42`, `-1` |
| **Symbol** | Unquoted text | `text`, `vision`, `OK` |
| **List** | Parenthesized | `(item1 item2)` |
| **Dictionary** | Explicit func | `(DICT ("key" "val"))` |

---

## 3. Core Instruction Set

These are the fundamental commands currently implemented in `nexus_interpreter.py`.

### 3.1 `(LOG "message")`

**Role**: Writing to the "Stream of Consciousness" (Nexus Reasoning Logs).  
**Usage**: Used by all modules to externalize their internal state.
```lisp
(LOG "Vision: User detected at [12, -4, 88]")
(LOG "Left State: Analysis complete. Confidence 0.98")
```

### 3.2 `(REQUEST-OUTPUT "target" "type" (params))`

**Role**: Requesting work from a specific module.
**Arguments**:

1.  `target`: The module ID (`"left"`, `"right"`, `"colossus"`).
2.  `type`: The type of generation (`"text"`, `"latent"`, `"image"`).
3.  `params`: A dictionary of configuration options (optional).

```lisp
(REQUEST-OUTPUT "right-hemisphere" "creative-text" (DICT ("style" "haiku")))
```

### 3.3 `(SET-TEMP "target" value)`

**Role**: Adjusting the "Creativity Temperature" of a specific hemisphere.
**Arguments**:

1.  `target`: The module to adjust.
2.  `value`: Float between 0.0 (Deterministic) and 1.5 (Chaotic).

```lisp
(SET-TEMP "right" 0.9)  ; High creativity
(SET-TEMP "left" 0.1)   ; High logic
```

### 3.4 `(TEACHER-GUIDANCE "message")`

**Role**: Injecting high-fidelity concepts from the "Supplement" (Mini-Omni2) into the main reasoning stream.
```lisp
(TEACHER-GUIDANCE "Construct: The user is asking about Linux Kernel architecture.")
```

---

## 4. Instructional Guide for Developers

### How to Write Nexus Code

When implementing new features or "Force-Feeding" thoughts to the Triad, follow these rules:

1.  **Always Prefix**: The verb comes first. `(OPEN door)`, not `(door OPEN)`.
2.  **Quote Strings**: Always use double quotes for text. `(LOG "System Ready")`.
3.  **Nest Logic**: You can output the result of one function into another.

    ```lisp
    (LOG (RESPOND-TO "user" "Hello!"))
    ```

### How to Parse Nexus (Python)

Use the `NexusInterpreter` class to execute code safely.
```python
from src.orchestrator.nexus_interpreter import NexusInterpreter

interpreter = NexusInterpreter()
result = interpreter.execute('(LOG "Test Message")')
print(result) # Output: "Test Message"
```

### Performance Metrics

- **Parsing Overhead**: < 0.2ms per expression (Regex-based tokenizer).
- **Execution Speed**: Instant (Direct function mapping).
- **Utility Score**: High (Provides the only structured log of "Intent").

---

## 5. NEXUS-L v1.1 Features (Implemented January 2026)

The following features have been added to the interpreter:

### 5.1 `(IF condition then-expr else-expr)`

**Role**: Conditional branching with lazy evaluation.
**Usage**: Only the chosen branch is evaluated.
```lisp
(IF (> temperature 0.8) 
    (LOG "High creativity mode")
    (LOG "Standard mode"))
```

### 5.2 `(COND (cond1 expr1) (cond2 expr2) (ELSE default))`

**Role**: Multi-way conditional (switch-like).
```lisp
(COND
    ((> quality 0.9) (LOG "Excellent"))
    ((> quality 0.7) (LOG "Good"))
    (ELSE (LOG "Needs improvement")))
```

### 5.3 `(LET ((var1 val1) (var2 val2)) body)`

**Role**: Scoped variable bindings.
**Usage**: Variables are only accessible within the body expression.
```lisp
(LET ((threshold 0.8) (temp 0.5))
    (IF (> temp threshold) "hot" "cold"))
```

### 5.4 `(EXECUTE-PLAN "plan_id")`

**Role**: Load and execute external `.nexus` plan files.
**Locations**: Searches `plans/`, `src/orchestrator/plans/` for `{plan_id}.nexus`
```lisp
(EXECUTE-PLAN "startup-sequence")
```

### 5.5 Comparison Operators

| Operator | Syntax | Description |
|----------|--------|-------------|
| `>` | `(> a b)` | Greater than |
| `<` | `(< a b)` | Less than |
| `>=` | `(>= a b)` | Greater or equal |
| `<=` | `(<= a b)` | Less or equal |
| `=` | `(= a b)` | Equality |
| `NOT` | `(NOT expr)` | Logical NOT |
| `AND` | `(AND a b c)` | Logical AND |
| `OR` | `(OR a b c)` | Logical OR |

---

## 6. NEXUS-RLM v1.2 Features (Implemented January 2026)

The following Recursive Language Model (RLM) commands enable ImpressionCore to process arbitrarily large contexts by treating them as external, searchable environments:

### 6.1 `(LLM-QUERY target prompt [params])`

**Role**: Make a recursive call to a Brain-Triad hemisphere.
**Targets**: "left" (analytical), "right" (creative), "colossus" (synthesizer)

```lisp
(LLM-QUERY "left" "Analyze this data logically")
(LLM-QUERY "right" "Generate creative alternatives")
(LLM-QUERY "colossus" "Synthesize both perspectives")
```

### 6.2 `(CONTEXT-LOAD path [context_id])`

**Role**: Load a document as external RLM context.
**Usage**: Enables processing of documents up to 50MB without consuming VRAM.

```lisp
(CONTEXT-LOAD "docs/large_document.md")
(CONTEXT-LOAD "docs/report.txt" "report_2026")
```

### 6.3 `(CONTEXT-SEARCH pattern [is_regex] [max_results])`

**Role**: Search the active context for keywords or patterns.
**Usage**: Returns matching text with surrounding context.

```lisp
(CONTEXT-SEARCH "quantum computing")
(CONTEXT-SEARCH "def \\w+\\(" true 20)  ;; Regex search
```

### 6.4 `(CONTEXT-CHUNK [chunk_size] [by])`

**Role**: Split context into processable chunks for parallel analysis.
**By options**: "chars", "lines", "paragraphs"

```lisp
(CONTEXT-CHUNK)                      ;; Default chunking
(CONTEXT-CHUNK 8000 "paragraphs")    ;; By paragraphs, 8k chars each
```

### 6.5 `(CONTEXT-STATS [context_id])`

**Role**: Get statistics about a loaded context.

```lisp
(CONTEXT-STATS)           ;; Active context
(CONTEXT-STATS "report")  ;; Specific context
```

### 6.6 `(CONTEXT-LIST)`

**Role**: List all loaded contexts with summary information.

### 6.7 `(RECURSION-DEPTH)`

**Role**: Get current RLM recursion depth (0-20 max).

### 6.8 `(RLM-STATS)`

**Role**: Get global RLM statistics (contexts loaded, searches, queries).

### RLM Example Plan

```lisp
;; Load a large document
(CONTEXT-LOAD "docs/research_paper.md" "paper")

;; Check statistics
(LOG (CONTEXT-STATS))

;; Search for key terms
(LET ((results (CONTEXT-SEARCH "methodology")))
    (LOG results)
    
    ;; Analyze with Brain-Triad
    (LLM-QUERY "left" (CONCAT "Analyze methodology: " results))
    (LLM-QUERY "right" "Suggest improvements to methodology"))
```

---

## 7. NEXUS-RLM v1.3: Parallel Execution (NEW)

### (ASYNC expr)

Execute asynchronously and return task ID immediately:

```lisp
(LET ((task (ASYNC (LLM-QUERY "left" "Analyze"))))
    (AWAIT task 5000))  ;; Wait up to 5 seconds
```

### (AWAIT async-id [timeout-ms])

Wait for async task completion:

```lisp
(AWAIT "async_a1b2c3d4" 10000)
```

### (PARALLEL expr1 expr2 ...)

Execute multiple expressions simultaneously:

```lisp
(PARALLEL
    (LLM-QUERY "left" "Analyze facts")
    (LLM-QUERY "right" "Generate ideas")
    (LLM-QUERY "colossus" "Synthesize"))
;; Returns: [result1, result2, result3]
```

---

## 8. Future Roadmap

### Implemented in v1.4:

- ✅ **PIPELINE**: `(PIPELINE expr1 expr2 ...)` for chained processing with `_` variable
- ✅ **Arithmetic Operators**: `+`, `-`, `*`, `/` for numeric operations
- ✅ **Utility Functions**: `CONCAT`, `LIST`, `MAP` for data manipulation

### Planned for v1.5:

- **Pattern Matching**: `(MATCH value ((pattern1 expr1) ...))`
- **Actor Model**: Enhanced agent-to-agent communication
- **SUMMARIZE**: Context compression for large documents

### Under Active Development:

- **RLM Training Integration**: Reinforcement learning to optimize chunking and recursion policies
  - Policy Network for NEXUS command selection
  - PPO training with multi-objective rewards
  - Long-context benchmarking (BABILong, RULER)
  - See: [RLM Training Integration Plan](strategic/b3/RLM_TRAINING_INTEGRATION_PLAN.md)

### Research Topics:

- **Streaming RLM**: Real-time processing of streaming context
- **Multi-Agent RLM**: Collaborative reasoning across multiple RLM instances

