# NEXUS Language Developer Guide

**Created:** January 19, 2026  
**Updated:** January 20, 2026  
**Author:** Kirk LaSalle; Antigravity Agent  
**Tags:** #nexus #developer #brain_triad #context_management  
**Category:** Developer Documentation  
**Status:** Active - v1.4 (Complete)  
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## Overview

This guide provides comprehensive documentation for developers working with the NEXUS language in ImpressionCore. NEXUS is a Lisp-like prefix notation language used for inter-module communication in the Brain-Triad architecture.

**Version History:**
- v1.2: Context management commands (CONTEXT-*, LLM-QUERY)
- v1.3: Parallel execution (ASYNC, AWAIT, PARALLEL)
- v1.4: Utilities (PIPELINE, arithmetic, CONCAT, LIST, MAP)

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [NEXUS-RLM Commands Reference](#nexus-rlm-commands-reference)
5. [RLM Context Manager API](#rlm-context-manager-api)
6. [Creating RLM Plans](#creating-rlm-plans)
7. [Integration with Brain-Triad](#integration-with-brain-triad)
8. [Memory Management](#memory-management)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## 1. Introduction

### What is NEXUS-RLM?

NEXUS-RLM is an extension to the NEXUS language that enables ImpressionCore to:

- Process documents up to 50MB without GPU memory overhead
- Perform recursive reasoning through Brain-Triad hemispheres
- Search, chunk, and analyze large contexts programmatically
- Track and limit recursion depth for safety

### Key Concepts

| Concept | Description |
|---------|-------------|
| **External Context** | Documents stored in CPU RAM, accessed via NEXUS commands |
| **LLM-QUERY** | Recursive calls to Left/Right/Colossus hemispheres |
| **Context Chunking** | Breaking large documents into processable segments |
| **Recursion Tracking** | Built-in depth limiting (max 20) to prevent infinite loops |

---

## 2. Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    NEXUS-RLM ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐      ┌─────────────────────────────────────┐  │
│  │ User Query   │      │      RLM CONTEXT MANAGER            │  │
│  └──────┬───────┘      │  ┌─────────────────────────────┐    │  │
│         │              │  │ contexts: Dict[str, RLMContext] │  │
│         ▼              │  │ active_context_id: str       │    │  │
│  ┌──────────────┐      │  │ recursion_state: RecursionState│  │  │
│  │    NEXUS     │◄────►│  └─────────────────────────────┘    │  │
│  │ Interpreter  │      │                                     │  │
│  │              │      │  Functions:                         │  │
│  │ - LLM-QUERY  │      │  - load_context_from_file()        │  │
│  │ - CONTEXT-*  │      │  - search_context()                │  │
│  │ - RLM-STATS  │      │  - chunk_context()                 │  │
│  └──────┬───────┘      │  - begin/end_recursive_call()      │  │
│         │              └─────────────────────────────────────┘  │
│         ▼                                                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    BRAIN-TRIAD                            │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐  │   │
│  │  │    LEFT    │  │   RIGHT    │  │      COLOSSUS      │  │   │
│  │  │ (Temp 0.1) │  │ (Temp 0.9) │  │    (Temp 0.5)      │  │   │
│  │  │ Analytical │  │  Creative  │  │    Synthesizer     │  │   │
│  │  └────────────┘  └────────────┘  └────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Component Locations

| Component | Path |
|-----------|------|
| NEXUS Interpreter | `src/orchestrator/nexus_interpreter.py` |
| RLM Context Manager | `src/orchestrator/rlm_context_manager.py` |
| RLM Plan Examples | `plans/rlm_document_analysis.nexus` |
| NEXUS Language Guide | `docs/nexus_language_guide.md` |

---

## 3. Quick Start

### Loading and Analyzing a Document

```python
from src.orchestrator.nexus_interpreter import NexusInterpreter

# Create interpreter
interpreter = NexusInterpreter()

# Load a document
result = interpreter.execute('(CONTEXT-LOAD "docs/README.md" "readme")')
print(result)  # OK-CONTEXT-LOADED: Loaded 15,234 chars as context 'readme'

# Get statistics
stats = interpreter.execute('(CONTEXT-STATS)')
print(stats)

# Search for keywords
results = interpreter.execute('(CONTEXT-SEARCH "installation")')
print(results)

# Query Brain-Triad (returns pending status in async mode)
response = interpreter.execute('(LLM-QUERY "left" "Summarize the installation steps")')
print(response)  # OK-LLM-QUERY-LEFT-PENDING
```

### Executing an RLM Plan

```python
# Execute a pre-defined RLM plan
result = interpreter.execute('(EXECUTE-PLAN "rlm_document_analysis")')
print(result)

# Check output queue for pending operations
print(interpreter.output_queue)
```

---

## 4. NEXUS-RLM Commands Reference

### 4.1 LLM-QUERY

**Syntax:** `(LLM-QUERY target prompt [params])`

**Purpose:** Make a recursive call to a Brain-Triad hemisphere.

**Parameters:**
- `target`: "left" | "right" | "colossus"
- `prompt`: String prompt for the LLM
- `params`: Optional dictionary of parameters

**Example:**
```lisp
(LLM-QUERY "left" "Analyze the logical structure of this argument")
(LLM-QUERY "right" "Generate creative alternatives")
(LLM-QUERY "colossus" "Synthesize the analyses into a conclusion")
```

**Returns:** `OK-LLM-QUERY-{TARGET}-PENDING` or `(ERROR "...")`

---

### 4.2 CONTEXT-LOAD

**Syntax:** `(CONTEXT-LOAD path [context_id])`

**Purpose:** Load a file as external RLM context.

**Parameters:**
- `path`: Relative or absolute file path
- `context_id`: Optional identifier (defaults to filename)

**Example:**
```lisp
(CONTEXT-LOAD "docs/architecture.md")
(CONTEXT-LOAD "F:/data/large_corpus.txt" "corpus_2026")
```

**Limits:**
- Maximum file size: 50MB
- Encoding: UTF-8 (with replacement for errors)

---

### 4.3 CONTEXT-SEARCH

**Syntax:** `(CONTEXT-SEARCH pattern [is_regex] [max_results])`

**Purpose:** Search the active context for a pattern.

**Parameters:**
- `pattern`: Search string or regex pattern
- `is_regex`: Boolean, default `false`
- `max_results`: Integer, default `10`

**Example:**
```lisp
(CONTEXT-SEARCH "neural network")
(CONTEXT-SEARCH "def \\w+\\(" true 20)
```

**Returns:** Formatted string with match positions and surrounding context.

---

### 4.4 CONTEXT-CHUNK

**Syntax:** `(CONTEXT-CHUNK [chunk_size] [by])`

**Purpose:** Split the active context into processable chunks.

**Parameters:**
- `chunk_size`: Chunk size in characters (default: 16384)
- `by`: "chars" | "lines" | "paragraphs"

**Example:**
```lisp
(CONTEXT-CHUNK)
(CONTEXT-CHUNK 8000 "paragraphs")
```

---

### 4.5 CONTEXT-STATS

**Syntax:** `(CONTEXT-STATS [context_id])`

**Purpose:** Get statistics about a loaded context.

**Returns:**
- Character count
- Estimated token count
- Line count
- Paragraph count
- Word count
- Source path

---

### 4.6 CONTEXT-LIST

**Syntax:** `(CONTEXT-LIST)`

**Purpose:** List all loaded contexts with summary information.

---

### 4.7 RECURSION-DEPTH

**Syntax:** `(RECURSION-DEPTH)`

**Purpose:** Get the current recursion depth (0-20).

---

### 4.8 RLM-STATS

**Syntax:** `(RLM-STATS)`

**Purpose:** Get global RLM statistics.

**Returns:**
- Contexts loaded count
- Total searches performed
- Total chunks created
- Total LLM queries made
- Current recursion depth
- Active context ID

---

## 5. RLM Context Manager API

### Python API

```python
from src.orchestrator.rlm_context_manager import get_rlm_context_manager

# Get singleton instance
rlm = get_rlm_context_manager()

# Load context
success, msg = rlm.load_context_from_file("docs/guide.md", "guide")

# Search context
results = rlm.search_context("keyword", is_regex=False, max_results=10)

# Chunk context
chunks = rlm.chunk_context(chunk_size=8000, by="paragraphs")

# Get statistics
stats = rlm.get_context_stats()

# Recursion management
can_recurse, msg = rlm.begin_recursive_call("colossus", "prompt here")
if can_recurse:
    # ... do recursive work ...
    rlm.end_recursive_call()

# Global stats
global_stats = rlm.get_global_stats()
```

### RLMContext Dataclass

```python
@dataclass
class RLMContext:
    content: str                    # The full document text
    source_path: Optional[str]      # Original file path
    loaded_at: str                  # ISO timestamp
    token_count_estimate: int       # Estimated tokens (~4 chars each)
```

### RecursionState Dataclass

```python
@dataclass
class RecursionState:
    current_depth: int = 0          # Current recursion level
    max_depth: int = 20             # Maximum allowed depth
    call_history: List[Dict]        # History of recursive calls
```

---

## 6. Creating RLM Plans

### Plan File Structure

RLM plans are `.nexus` files stored in the `plans/` directory:

```lisp
;; my_rlm_plan.nexus
;; 
;; Description of what this plan does
;;
;; Usage: (EXECUTE-PLAN "my_rlm_plan")

;; Step 1: Load context
(CONTEXT-LOAD "path/to/document.md" "doc")

;; Step 2: Get statistics
(LET ((stats (CONTEXT-STATS)))
    (LOG stats)
    
    ;; Step 3: Conditional processing
    (IF (> (RECURSION-DEPTH) 10)
        (LOG "Warning: High recursion depth")
        
        ;; Step 4: Query hemispheres
        (LET ((analysis (LLM-QUERY "left" "Analyze this")))
            (LOG analysis)
            "Analysis complete")))
```

### Available Plan Templates

| Plan | Description |
|------|-------------|
| `rlm_document_analysis.nexus` | Full document analysis with L/R/Colossus |
| `rlm_recursive_search.nexus` | Recursive search demonstration |

---

## 7. Integration with Brain-Triad

### LLM-QUERY Output Queue

When `LLM-QUERY` is executed, it adds an entry to the interpreter's output queue:

```python
{
    "action": "LLM_QUERY",
    "target": "left",           # or "right", "colossus"
    "prompt": "User prompt here",
    "params": {},
    "recursion_depth": 1
}
```

### Processing LLM Queries

```python
# Process pending LLM queries
for item in interpreter.output_queue:
    if item["action"] == "LLM_QUERY":
        target = item["target"]
        prompt = item["prompt"]
        
        # Route to Brain-Triad
        if target == "left":
            response = brain_triad.query_left(prompt, temperature=0.1)
        elif target == "right":
            response = brain_triad.query_right(prompt, temperature=0.9)
        else:
            response = brain_triad.query_colossus(prompt, temperature=0.5)
```

---

## 8. Memory Management

### GTX 1050 Ti Considerations

| Component | Memory Usage | Notes |
|-----------|--------------|-------|
| B3-Ultra Model | ~3.2 GB | GPU VRAM |
| RLM Context Manager | ~50 MB | CPU RAM |
| Per-Context Storage | Variable | CPU RAM (50MB max) |
| Recursion State | ~1 KB | Negligible |

### Best Practices

1. **Clear Unused Contexts**
   ```python
   rlm.clear_all_contexts()
   ```

2. **Use Chunking for Large Documents**
   ```lisp
   (CONTEXT-CHUNK 8000 "paragraphs")
   ```

3. **Monitor Recursion Depth**
   ```lisp
   (IF (> (RECURSION-DEPTH) 15)
       (LOG "Warning: Approaching max depth"))
   ```

---

## 9. Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `RLM module not available` | Import failure | Check `rlm_context_manager.py` exists |
| `File not found` | Invalid path in CONTEXT-LOAD | Verify file path |
| `File too large` | Exceeds 50MB limit | Split document |
| `Max recursion depth exceeded` | 20+ recursive calls | Restructure plan logic |
| `No context loaded` | CONTEXT-* before CONTEXT-LOAD | Load context first |

### Error Format

All errors are returned in NEXUS format:
```lisp
(ERROR "Descriptive error message")
```

---

## 10. Best Practices

### DO:

- ✅ Load context before performing searches or queries
- ✅ Use chunking for documents > 10K tokens
- ✅ Monitor recursion depth in complex plans
- ✅ Clear contexts when switching documents
- ✅ Log intermediate results for debugging

### DON'T:

- ❌ Attempt to load files > 50MB
- ❌ Create infinite recursion loops
- ❌ Ignore the output queue in production
- ❌ Skip error handling in NEXUS plans

---

## 11. Troubleshooting

### Import Errors

```
ImportError: cannot import name 'get_rlm_context_manager'
```

**Solution:** Ensure `rlm_context_manager.py` is in `src/orchestrator/`.

### Context Not Loading

```
(ERROR "File not found: path/to/file.md")
```

**Solution:** Use absolute paths or paths relative to project root.

### LLM-QUERY Not Returning

**Note:** In v1.2, LLM-QUERY returns `PENDING` status and adds to output queue.
Full synchronous mode is planned for v1.3.

### High Memory Usage

**Solution:** Clear unused contexts and use smaller chunk sizes.

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.4.0 | 2026-01-20 | PIPELINE, arithmetic, LIST, MAP, CONCAT utilities |
| 1.3.0 | 2026-01-20 | ASYNC, AWAIT, PARALLEL parallel execution |
| 1.2.0 | 2026-01-19 | Initial NEXUS context management (LLM-QUERY, CONTEXT-*) |

---

## See Also

- [NEXUS Language Guide](../nexus_language_guide.md)
- [RLM Training Integration Plan](../strategic/b3/RLM_TRAINING_INTEGRATION_PLAN.md) 🆕
- [RLM Research Report](../../reports/rlm_research_report.md)
- [Brain-Triad Architecture](../reference/brain_triad_architecture.md)
- [MHC Ultra Training](../training/MHC_ULTRA_TRAINING_GUIDE.md)

