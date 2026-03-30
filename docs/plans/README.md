# NEXUS Plans Repository

Reusable `.nexus` scripts for the Brain-Triad system.

## Usage

Execute any plan from NEXUS-L:
```lisp
(EXECUTE-PLAN "plan-name")
```

Or programmatically from Python:
```python
from src.orchestrator.nexus_interpreter import NexusInterpreter

interpreter = NexusInterpreter()
interpreter.execute('(EXECUTE-PLAN "init-system")')
```

## Available Plans

| Plan | Description |
|------|-------------|
| `init-system` | System startup: sets default temps, loads memory |
| `diagnostics` | Hardware and memory health check |
| `creative-mode` | Shifts triad to creative/divergent thinking (R=0.95, L=0.2) |
| `analytical-mode` | Shifts triad to logical/systematic thinking (L=0.1, R=0.4) |
| `memory-search` | Template for memory search operations |

## Creating New Plans

1. Create a `.nexus` file in this directory
2. Name it `your-plan-name.nexus` (lowercase, hyphens)
3. Use any NEXUS-L v1.1 commands (see `docs/nexus_language_guide.md`)

### Example Plan Structure

```lisp
# NEXUS Plan: [Description]
# Called via: (EXECUTE-PLAN "plan-name")

(LOG "Starting plan...")

# Your commands here
(SET-TEMP "left" 0.3)
(IF (> quality 0.8)
    (LOG "High quality")
    (LOG "Standard quality"))

(LOG "Plan complete")
```

## NEXUS-L v1.1 Quick Reference

| Command | Usage |
|---------|-------|
| `(LOG "msg")` | Write to reasoning log |
| `(SET-TEMP "hemisphere" val)` | Set temperature (0.0-1.0) |
| `(IF cond then else)` | Conditional |
| `(LET ((var val)) body)` | Scoped variables |
| `(> a b)`, `(< a b)`, etc. | Comparison operators |
| `(AND ...)`, `(OR ...)`, `(NOT ...)` | Logic operators |
